#!/usr/bin/env python3
"""Fail-closed patch for the audited Dungeon Quest 3.3.2.0 Pause HUD."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

SECTIONS = ("general_attributes", "elements", "actions", "timers")
MAGIC = {b"NcP", b"NcX", b"NcI"}
OLD_LABEL, NEW_LABEL = "Social/IAP", "Cheats Sandbox"
OLD_ACTION, NEW_ACTION = "onShowSocial", "onShowCheats"
RESUME = "<023><8,3>013<2,10>uai_gp_hud<2,8>onResume"
DEBUG = "<023><8,3>013<2,10>uai_gp_hud<2,7>onDebug<1,5>0.000"
EXPECTED_LAST = "<023><8,3>013<2,14>uai_gp_options<2,9>onShowTab<1,5>3.000"

class PatchError(ValueError):
    pass

def lp(s: str) -> bytes:
    b = s.encode("utf-8")
    return struct.pack("<I", len(b)) + b

def read_lp(data: bytes, pos: int, where: str) -> tuple[str, int]:
    if pos + 4 > len(data):
        raise PatchError(f"truncated length: {where}")
    n = struct.unpack_from("<I", data, pos)[0]
    pos += 4
    if n > len(data) - pos:
        raise PatchError(f"truncated string: {where}")
    try:
        return data[pos:pos+n].decode("utf-8"), pos+n
    except UnicodeDecodeError as e:
        raise PatchError(f"invalid UTF-8: {where}") from e

def sections(data: bytes) -> tuple[dict[str, bytes], int]:
    if len(data) < 8 or struct.unpack_from("<I", data)[0] != 3 or data[4:7] not in MAGIC:
        raise PatchError("unrecognized HUD header")
    version = data[7]
    pos = 8
    result = {}
    for name in SECTIONS:
        if pos+4 > len(data):
            raise PatchError(f"missing {name} header")
        n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if n > len(data)-pos:
            raise PatchError(f"invalid {name} length")
        result[name] = data[pos:pos+n]
        pos += n
    if pos != len(data):
        raise PatchError("trailing bytes after HUD sections")
    return result, version

def parse_actions(payload: bytes, version: int) -> list[dict]:
    if len(payload) < 2:
        raise PatchError("short action table")
    count = struct.unpack_from("<H", payload)[0]
    pos = 2
    out = []
    for i in range(count):
        name, pos = read_lp(payload, pos, f"action[{i}].name")
        if pos+2 > len(payload):
            raise PatchError("truncated action argc")
        argc = struct.unpack_from("<H", payload, pos)[0]
        pos += 2
        params = []
        for j in range(argc):
            value, pos = read_lp(payload, pos, f"{name}.param[{j}]")
            params.append(value)
        extra = ""
        if version > 8:
            extra, pos = read_lp(payload, pos, f"{name}.extra")
        out.append({"name": name, "parameters": params, "extra_script": extra})
    if pos != len(payload):
        raise PatchError("unparsed bytes in action table")
    return out

def write_action(a: dict, version: int) -> bytes:
    params = a["parameters"]
    out = bytearray(lp(a["name"]) + struct.pack("<H", len(params)))
    for p in params:
        out += lp(p)
    if version > 8:
        out += lp(a.get("extra_script", ""))
    return bytes(out)

def replace_once(data: bytes, old: str, new: str, area: str) -> tuple[bytes, int]:
    count = data.count(lp(old))
    if count != 1:
        raise PatchError(f"expected one length-prefixed {old!r} in {area}, got {count}")
    return data.replace(lp(old), lp(new), 1), count

def patch_hud(source: bytes) -> tuple[bytes, dict]:
    before, version = sections(source)
    if version != 12:
        raise PatchError(f"expected HUD v12; got {version}")
    old_actions = parse_actions(before["actions"], version)
    target = [i for i, a in enumerate(old_actions) if a["name"] == OLD_ACTION]
    resume = [a for a in old_actions if a["name"] == "onResume"]
    if len(target) != 1 or len(resume) != 1:
        raise PatchError("expected unique onShowSocial and onResume actions")
    i = target[0]
    a = old_actions[i]
    if len(a["parameters"]) != 7 or a["parameters"][-1] != EXPECTED_LAST:
        raise PatchError("target action schema differs from audited v3.3.2.0; refusing to patch")
    elements, n_label = replace_once(before["elements"], OLD_LABEL, NEW_LABEL, "elements")
    elements, n_callback = replace_once(elements, OLD_ACTION, NEW_ACTION, "elements")
    modified = [dict(a) for a in old_actions]
    modified[i] = {"name": NEW_ACTION, "parameters": [RESUME, DEBUG], "extra_script": ""}
    action_payload = bytearray(struct.pack("<H", len(modified)))
    for item in modified:
        action_payload += write_action(item, version)
    after = dict(before)
    after["elements"], after["actions"] = elements, bytes(action_payload)
    out = bytearray(source[:8])
    for name in SECTIONS:
        out += struct.pack("<I", len(after[name])) + after[name]
    out = bytes(out)
    check, version2 = sections(out)
    actions2 = parse_actions(check["actions"], version2)
    if version2 != version or len(actions2) != len(old_actions):
        raise PatchError("round-trip header/count mismatch")
    if check["general_attributes"] != before["general_attributes"] or check["timers"] != before["timers"]:
        raise PatchError("unexpected section mutation")
    for j, (previous, current) in enumerate(zip(old_actions, actions2)):
        if j == i:
            if current != {"name": NEW_ACTION, "parameters": [RESUME, DEBUG], "extra_script": ""}:
                raise PatchError("patched callback did not round-trip")
        elif previous != current:
            raise PatchError(f"unrelated action changed: {previous['name']}")
    if check["elements"].count(lp(NEW_LABEL)) != 1 or check["elements"].count(lp(NEW_ACTION)) != 1:
        raise PatchError("patched label/callback not uniquely present")
    report = {
        "schema": "dq-pause-cheats-asset-patch-v21",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "output_sha256": hashlib.sha256(out).hexdigest(),
        "source_size_bytes": len(source),
        "output_size_bytes": len(out),
        "hud_version": version,
        "element_count": struct.unpack_from("<I", before["elements"])[0],
        "action_count": len(old_actions),
        "target_action_index": i,
        "changes": {
            "button_label": {"from": OLD_LABEL, "to": NEW_LABEL, "matches": n_label},
            "button_callback": {"from": OLD_ACTION, "to": NEW_ACTION, "matches": n_callback},
            "callback_script": ["uai_gp_hud.onResume", "uai_gp_hud.onDebug(0)"]
        },
        "unchanged_sections": ["general_attributes", "timers"],
        "unrelated_actions_preserved": True,
        "runtime_status": "NOT_RUNTIME_VERIFIED"
    }
    return out, report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    patched, report = patch_hud(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(patched)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, struct.error, PatchError) as e:
        raise SystemExit(f"ERROR: {e}")

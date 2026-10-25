#!/usr/bin/env python3
"""Patch one visible Set Gold control into a version-12 Dungeon Quest debug HUD.

The input v33 HUD is used as the layout-preserving source because its first 71 elements
include deliberate Add-panel transform adjustments that reserve a bottom row. The four
appended v33 mini Gold controls are replaced with one normal-sized Set Gold control.
This operates on caller-supplied decoded HUD files and never mutates the inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

HEADER = struct.Struct("<I")
HUD_VERSION = 12
ORIGINAL_ELEMENT_COUNT = 71
V33_ELEMENT_COUNT = 75
ORIGINAL_ACTION_COUNT = 13
V33_ACTION_COUNT = 17
BUTTON_RECORD_SIZE = 193
ACTION_ID = "onGoldMinus10"
ACTION_SCRIPT = "<023><8,3>013<2,10>uai_gp_hud<2,9>onSetGold"
LABEL_OLD = b"Gold -10"
LABEL_NEW = b"Set Gold"


def parse_hud(data: bytes):
    pos = 0
    marker_len = HEADER.unpack_from(data, pos)[0]
    pos += 4
    marker = data[pos:pos + marker_len]
    pos += marker_len
    version = data[pos]
    pos += 1
    sections = []
    for _ in range(4):
        length = HEADER.unpack_from(data, pos)[0]
        pos += 4
        section = data[pos:pos + length]
        if len(section) != length:
            raise ValueError("truncated HUD section")
        sections.append(section)
        pos += length
    if pos != len(data):
        raise ValueError("unexpected bytes after HUD section table")
    return marker, version, sections


def serialize_hud(marker: bytes, version: int, sections: list[bytes]) -> bytes:
    out = bytearray(struct.pack("<I", len(marker)) + marker + bytes([version]))
    for section in sections:
        out.extend(struct.pack("<I", len(section)))
        out.extend(section)
    return bytes(out)


def parse_actions(section: bytes):
    if len(section) < 2:
        raise ValueError("missing action table")
    count = struct.unpack_from("<H", section)[0]
    pos = 2
    rows = []
    for _ in range(count):
        name_len = HEADER.unpack_from(section, pos)[0]
        pos += 4
        name = section[pos:pos + name_len].decode("utf-8")
        pos += name_len
        param_count = struct.unpack_from("<H", section, pos)[0]
        pos += 2
        params = []
        for _ in range(param_count):
            length = HEADER.unpack_from(section, pos)[0]
            pos += 4
            params.append(section[pos:pos + length].decode("utf-8"))
            pos += length
        script_len = HEADER.unpack_from(section, pos)[0]
        pos += 4
        script = section[pos:pos + script_len].decode("utf-8")
        pos += script_len
        rows.append({"name": name, "params": params, "script": script})
    if pos != len(section):
        raise ValueError(f"action parse consumed {pos}/{len(section)} bytes")
    return rows


def serialize_actions(rows) -> bytes:
    out = bytearray(struct.pack("<H", len(rows)))
    for row in rows:
        encoded_name = row["name"].encode("utf-8")
        out.extend(struct.pack("<I", len(encoded_name)))
        out.extend(encoded_name)
        out.extend(struct.pack("<H", len(row["params"])))
        for param in row["params"]:
            encoded = param.encode("utf-8")
            out.extend(struct.pack("<I", len(encoded)))
            out.extend(encoded)
        script = row["script"].encode("utf-8")
        out.extend(struct.pack("<I", len(script)))
        out.extend(script)
    return bytes(out)


def patch(original: bytes, v33: bytes):
    om, ov, os = parse_hud(original)
    vm, vv, vs = parse_hud(v33)
    if om != vm or ov != HUD_VERSION or vv != HUD_VERSION:
        raise ValueError("HUD marker/version mismatch")
    if struct.unpack_from("<I", os[1])[0] != ORIGINAL_ELEMENT_COUNT:
        raise ValueError("original HUD element count mismatch")
    if struct.unpack_from("<I", vs[1])[0] != V33_ELEMENT_COUNT:
        raise ValueError("v33 HUD element count mismatch")
    orig_actions = parse_actions(os[2])
    v33_actions = parse_actions(vs[2])
    if len(orig_actions) != ORIGINAL_ACTION_COUNT or len(v33_actions) != V33_ACTION_COUNT:
        raise ValueError("HUD action count mismatch")

    # The first v33 appended record is the 193-byte Gold -10 button.
    first_start = len(os[1])
    record = bytearray(vs[1][first_start:first_start + BUTTON_RECORD_SIZE])
    if len(record) != BUTTON_RECORD_SIZE:
        raise ValueError("truncated first v33 appended button")
    if b"gold_minus_10_btn" not in record or LABEL_OLD not in record or ACTION_ID.encode() not in record:
        raise ValueError("first appended element does not match expected v33 button")

    at = record.find(LABEL_OLD)
    if record.find(LABEL_OLD, at + 1) != -1:
        raise ValueError("ambiguous button label occurrence")
    record[at:at + len(LABEL_OLD)] = LABEL_NEW

    # This record's identifier is 17 bytes; the encoded transform begins at byte 34.
    # Offsets 33/37/41/45 corrupt the preceding byte and prevent the element rendering.
    x, y, width, height = 34, 38, 42, 46
    struct.pack_into("<f", record, x, 0.0)
    struct.pack_into("<f", record, y, -0.79)
    struct.pack_into("<f", record, width, 0.82)
    struct.pack_into("<f", record, height, 0.18)

    # Keep v33's modified first-71 element prefix: reverting it removes the reserved row.
    elements = bytearray(vs[1][:len(os[1])])
    elements.extend(record)
    struct.pack_into("<I", elements, 0, ORIGINAL_ELEMENT_COUNT + 1)

    extra_action = {
        "name": ACTION_ID,
        "params": [ACTION_SCRIPT],
        "script": "",
    }
    actions = orig_actions + [extra_action]
    result = serialize_hud(om, ov, [os[0], bytes(elements), serialize_actions(actions), os[3]])

    cm, cv, cs = parse_hud(result)
    if cm != om or cv != ov:
        raise ValueError("output HUD header changed")
    if struct.unpack_from("<I", cs[1])[0] != 72:
        raise ValueError("expected 72 HUD elements after patch")
    parsed_actions = parse_actions(cs[2])
    if len(parsed_actions) != 14:
        raise ValueError("expected 14 HUD actions after patch")
    if parsed_actions[:13] != orig_actions:
        raise ValueError("original action rows changed")
    if parsed_actions[-1] != extra_action:
        raise ValueError("Set Gold callback missing or changed")
    if cs[1][4:len(os[1])] != vs[1][4:len(os[1])]:
        raise ValueError("v33 layout-adjusted first-71 prefix was not preserved")
    appended = cs[1][len(os[1]):]
    if b"Set Gold" not in appended:
        raise ValueError("Set Gold label missing")
    values = struct.unpack_from("<4f", record, x)
    if values != (0.0, -0.7900000214576721, 0.8199999928474426, 0.18000000715255737):
        raise ValueError(f"transform mismatch: {values}")
    report = {
        "input_original_sha256": hashlib.sha256(original).hexdigest(),
        "input_v33_sha256": hashlib.sha256(v33).hexdigest(),
        "output_sha256": hashlib.sha256(result).hexdigest(),
        "output_size": len(result),
        "elements_before_original": ORIGINAL_ELEMENT_COUNT,
        "elements_before_v33": V33_ELEMENT_COUNT,
        "elements_after": 72,
        "actions_before_original": 13,
        "actions_after": 14,
        "preserves_v33_layout_prefix": True,
        "correct_transform_offsets": [34, 38, 42, 46],
        "transform": {"x": values[0], "y": values[1], "width": values[2], "height": values[3]},
        "label": "Set Gold",
        "action": ACTION_ID,
        "target": "uai_gp_hud.onSetGold",
        "runtime": "NOT_VERIFIED",
    }
    return result, report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--original-hud", type=Path, required=True)
    ap.add_argument("--v33-hud", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.output.resolve() in {args.original_hud.resolve(), args.v33_hud.resolve()}:
        raise SystemExit("refusing to overwrite an input HUD")
    result, report = patch(args.original_hud.read_bytes(), args.v33_hud.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

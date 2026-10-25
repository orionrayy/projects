#!/usr/bin/env python3
"""Fail-closed canonical v12 HUD element serializer based on SaveElements field order.

This is an analysis tool, not a package patcher. It preserves the original
non-element sections and refuses unknown types, unsupported versions, and a
nonzero common field that native SaveElements rewrites to 0.0.
"""
from __future__ import annotations
import hashlib
import json
import math
import pathlib
import struct
import sys
from typing import Any

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hud_elements_probe_v41 import HudFormatError, parse_hud  # noqa: E402


def u8(v: int) -> bytes:
    if not 0 <= int(v) <= 255:
        raise HudFormatError(f"u8 out of range: {v}")
    return struct.pack("<B", int(v))


def u32(v: int) -> bytes:
    if not 0 <= int(v) <= 0xffffffff:
        raise HudFormatError(f"u32 out of range: {v}")
    return struct.pack("<I", int(v))


def f32(v: float) -> bytes:
    value = float(v)
    if not math.isfinite(value):
        raise HudFormatError(f"non-finite float is not safe to canonicalize: {value!r}")
    return struct.pack("<f", value)


def string(v: str) -> bytes:
    raw = v.encode("utf-8", errors="surrogateescape")
    return u32(len(raw)) + raw


def vec2(v: list[float]) -> bytes:
    if len(v) != 2:
        raise HudFormatError("vec2 requires 2 floats")
    return f32(v[0]) + f32(v[1])


def color(v: list[int]) -> bytes:
    if len(v) != 4:
        raise HudFormatError("color requires 4 bytes")
    values = [int(x) for x in v]
    if any(x < 0 or x > 255 for x in values):
        raise HudFormatError(f"color component out of range: {values}")
    return bytes(values)


def strings(values: list[str]) -> bytes:
    return b"".join(string(v) for v in values)


def floats(values: list[float]) -> bytes:
    return b"".join(f32(v) for v in values)


def bytes_checked(values: list[int]) -> bytes:
    return b"".join(u8(v) for v in values)


def serialize_element(e: dict[str, Any]) -> bytes:
    typ = int(e["type"])
    flags = e["flags"]
    if len(flags) != 8:
        raise HudFormatError(f"element {e['index']}: wrong common flag count")
    if float(e["aux_float"]) != 0.0:
        raise HudFormatError(
            f"element {e['index']}: common +0x28 field is not zero; "
            "native writer canonicalizes this field"
        )
    out = bytearray()
    out += string(e["name"])
    out += u8(typ)
    out += string(e["label"])
    out += u32(e["field_u32"])
    out += u8(flags[0])
    out += vec2(e["position"])
    out += vec2(e["size"])
    out += f32(e["scale_2c"])
    out += f32(0.0)  # native SaveElements explicitly emits 0.0 for this common field
    out += bytes_checked(flags[1:6])
    out += f32(e["scale_30"])
    for c in e["colors"]:
        out += color(c)
    out += string(e["resource_40"])
    out += vec2(e["vectors_48_50"][0])
    out += vec2(e["vectors_48_50"][1])
    out += bytes_checked(flags[6:8])
    out += strings(e["common_strings"])

    f = e["type_fields"]
    if typ in (1, 5, 9, 10, 13):
        pass
    elif typ == 2:
        out += string(f["string_140"])
        out += floats(f["floats_150_158"])
        out += bytes_checked(f["flags_188_199"])
        out += string(f["resource_160"])
        out += strings(f["strings_168_178"])
    elif typ == 3:
        out += u8(f["flag_1f4"])
        out += floats(f["floats_1d8_1e0"])
        out += bytes_checked(f["flags_1e4_1e6"])
        out += floats(f["floats_1f8_1fc"])
        out += string(f["resource_208"])
        out += string(f["string_210"])
        out += f32(f["float_220"])
        out += strings(f["resources_228_238"])
        for c in f["colors_230_250"]:
            out += color(c)
        out += strings(f["resources_258_290"])
        out += floats(f["floats_298_29c"])
    elif typ == 4:
        out += string(f["string_60"])
        out += floats(f["floats_70_78"])
        out += bytes_checked(f["flags_5b_5f"])
        out += string(f["resource_88"])
    elif typ == 6:
        out += u8(f["flag_c8"])
        out += string(f["string_90"])
        out += floats(f["floats_a0_a8"])
        out += bytes_checked(f["flags_c9_d9"])
        out += string(f["resource_b0"])
        out += string(f["string_b8"])
    elif typ in (7, 12, 14):
        out += string(f["resource"])
    elif typ == 8:
        out += bytes_checked(f["flags_19a_19b"])
    elif typ == 11:
        out += u8(f["flag_19c"])
        out += b"".join(struct.pack("<h", int(v)) for v in f["shorts_1a0_19e"])
        out += string(f["string_1a8"])
        out += string(f["resource_1b8"])
    elif typ == 15:
        out += u8(f["flag_df"])
        out += string(f["string_e0"])
        out += floats(f["floats_f0_f8"])
        out += bytes_checked(f["flags_da_de"])
        out += string(f["resource_108"])
        out += string(f["string_120"])
        out += string(f["string_130"])
        out += strings(f["resources_110_118"])
    else:
        raise HudFormatError(f"element {e['index']}: unsupported type {typ}")
    return bytes(out)


def section(data: bytes) -> bytes:
    return u32(len(data)) + data


def canonical_serialize_hud(
    data: bytes, source: str = "<memory>"
) -> tuple[bytes, dict[str, Any]]:
    parsed = parse_hud(data, source)
    marker = data[4:7]
    if parsed["format_version"] != 12:
        raise HudFormatError("canonical writer supports HUD format v12 only")
    cursor = 8
    sections = []
    for _ in range(4):
        length = struct.unpack_from("<I", data, cursor)[0]
        start = cursor + 4
        sections.append(data[start:start + length])
        cursor = start + length
    general, original_elements, actions, timers = sections
    records = b"".join(serialize_element(e) for e in parsed["records"])
    elements = u32(len(parsed["records"])) + records
    output = (
        u32(3) + marker + bytes([12]) + section(general) + section(elements)
        + section(actions) + section(timers)
    )
    report = {
        "source": source,
        "source_size": len(data),
        "output_size": len(output),
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "output_sha256": hashlib.sha256(output).hexdigest(),
        "byte_identical": output == data,
        "changed_byte_count": sum(a != b for a, b in zip(data, output))
        + abs(len(data) - len(output)),
        "element_count": len(parsed["records"]),
        "element_payload_before": len(original_elements),
        "element_payload_after": len(elements),
        "rewrite_supported": True,
    }
    return output, report


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("hud", nargs="+", type=pathlib.Path)
    p.add_argument("--output-dir", type=pathlib.Path)
    p.add_argument("--summary", action="store_true")
    args = p.parse_args()
    rows = []
    failures = []
    for path in args.hud:
        try:
            source = path.read_bytes()
            output, report = canonical_serialize_hud(source, str(path))
            rows.append(report)
            if args.output_dir:
                args.output_dir.mkdir(parents=True, exist_ok=True)
                (args.output_dir / path.name).write_bytes(output)
            if args.summary:
                print(
                    ("PASS" if report["byte_identical"] else "DIFF")
                    + f" {path.name}: byte_identical={report['byte_identical']}"
                    + f" size={report['source_size']} elements={report['element_count']}"
                    + f" changed={report['changed_byte_count']}"
                )
        except Exception as exc:
            failures.append({"path": str(path), "error": str(exc)})
            print(f"FAIL {path}: {exc}")
    print(json.dumps({
        "tested": len(args.hud),
        "passed": sum(r["byte_identical"] for r in rows),
        "roundtrip_different": sum(not r["byte_identical"] for r in rows),
        "failed": len(failures),
        "failures": failures,
        "results": rows,
    }, indent=2))
    return 0 if not failures and all(r["byte_identical"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())

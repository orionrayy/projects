#!/usr/bin/env python3
"""Read-only probe for v12 serialized HUD element records.

The parser models the field read order observed in libS3DClient.so's
HUDTemplate::LoadElements. It does not serialize or rewrite HUD resources.
Strings are decoded with surrogateescape so legacy non-UTF-8 bytes survive
round-trip through the Python representation rather than breaking the probe.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import struct
from collections import Counter
from typing import Any

SECTION_NAMES = ("general", "elements", "actions", "timers")
KNOWN_MARKERS = {b"NcP", b"NcX", b"NcI"}
EXPECTED_VERSION = 12
MAX_STRING_BYTES = 2_000_000
MAX_ELEMENTS = 100_000


class HudFormatError(ValueError):
    """Malformed or unsupported HUD data."""


class Reader:
    def __init__(self, data: bytes, label: str = "payload") -> None:
        self.data = data
        self.label = label
        self.offset = 0

    def take(self, size: int) -> bytes:
        if size < 0 or self.offset + size > len(self.data):
            raise HudFormatError(
                f"{self.label}: truncated at 0x{self.offset:x}; "
                f"need {size} byte(s), have {len(self.data) - self.offset}"
            )
        start = self.offset
        self.offset += size
        return self.data[start:self.offset]

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.take(2))[0]

    def i16(self) -> int:
        return struct.unpack("<h", self.take(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def f32(self) -> float:
        return struct.unpack("<f", self.take(4))[0]

    def string(self) -> str:
        length_offset = self.offset
        length = self.u32()
        if length > MAX_STRING_BYTES:
            raise HudFormatError(
                f"{self.label}: unreasonable string length {length} "
                f"at 0x{length_offset:x}"
            )
        raw = self.take(length)
        return raw.decode("utf-8", errors="surrogateescape")

    def vec2(self) -> list[float]:
        return [self.f32(), self.f32()]

    def color(self) -> list[int]:
        return list(self.take(4))


def _parse_element(reader: Reader, index: int) -> dict[str, Any]:
    start = reader.offset
    try:
        name = reader.string()
        element_type = reader.u8()
        label = reader.string()
        field_u32 = reader.u32()

        # Common fields serialized by the v12 loader after the label/id.
        flag_11 = reader.u8()
        position = reader.vec2()
        size = reader.vec2()
        scale_2c = reader.f32()
        aux_float = reader.f32()
        common_flags = [reader.u8() for _ in range(5)]
        scale_30 = reader.f32()
        common_colors = [reader.color() for _ in range(3)]
        resource_40 = reader.string()
        vector_48 = reader.vec2()
        vector_50 = reader.vec2()
        common_flags_58 = [reader.u8(), reader.u8()]
        common_strings = [reader.string() for _ in range(4)]

        fields: dict[str, Any] = {}
        if element_type == 1:
            pass
        elif element_type == 2:
            fields["string_140"] = reader.string()
            fields["floats_150_158"] = [reader.f32(), reader.f32(), reader.f32()]
            fields["flags_188_199"] = [reader.u8() for _ in range(5)]
            fields["resource_160"] = reader.string()
            fields["strings_168_178"] = [reader.string(), reader.string()]
        elif element_type == 3:
            fields["flag_1f4"] = reader.u8()
            fields["floats_1d8_1e0"] = [reader.f32(), reader.f32(), reader.f32()]
            fields["flags_1e4_1e6"] = [reader.u8(), reader.u8(), reader.u8()]
            fields["floats_1f8_1fc"] = [reader.f32(), reader.f32()]
            fields["resource_208"] = reader.string()
            fields["string_210"] = reader.string()
            fields["float_220"] = reader.f32()
            fields["resources_228_238"] = [reader.string(), reader.string()]
            # LoadElements reads seven color values in this v12 branch.
            fields["colors_230_250"] = [reader.color() for _ in range(7)]
            fields["resources_258_290"] = [reader.string() for _ in range(8)]
            fields["floats_298_29c"] = [reader.f32(), reader.f32()]
        elif element_type == 4:
            fields["string_60"] = reader.string()
            fields["floats_70_78"] = [reader.f32(), reader.f32(), reader.f32()]
            fields["flags_5b_5f"] = [reader.u8() for _ in range(5)]
            fields["resource_88"] = reader.string()
        elif element_type == 5:
            pass
        elif element_type == 6:
            fields["flag_c8"] = reader.u8()
            fields["string_90"] = reader.string()
            fields["floats_a0_a8"] = [reader.f32(), reader.f32(), reader.f32()]
            fields["flags_c9_d9"] = [reader.u8() for _ in range(5)]
            fields["resource_b0"] = reader.string()
            fields["string_b8"] = reader.string()
        elif element_type == 7:
            fields["resource"] = reader.string()
        elif element_type == 8:
            fields["flags_19a_19b"] = [reader.u8(), reader.u8()]
        elif element_type in (9, 10):
            pass
        elif element_type == 11:
            fields["flag_19c"] = reader.u8()
            fields["shorts_1a0_19e"] = [reader.i16(), reader.i16(), reader.i16()]
            fields["string_1a8"] = reader.string()
            fields["resource_1b8"] = reader.string()
        elif element_type == 12:
            fields["resource"] = reader.string()
        elif element_type == 13:
            pass
        elif element_type == 14:
            fields["resource"] = reader.string()
        elif element_type == 15:
            fields["flag_df"] = reader.u8()
            fields["string_e0"] = reader.string()
            fields["floats_f0_f8"] = [reader.f32(), reader.f32(), reader.f32()]
            fields["flags_da_de"] = [reader.u8() for _ in range(5)]
            fields["resource_108"] = reader.string()
            fields["string_120"] = reader.string()
            fields["string_130"] = reader.string()
            fields["resources_110_118"] = [reader.string(), reader.string()]
        else:
            raise HudFormatError(f"unsupported v12 element type {element_type}")

        return {
            "index": index,
            "offset": start,
            "end_offset": reader.offset,
            "record_size": reader.offset - start,
            "name": name,
            "type": element_type,
            "label": label,
            "field_u32": field_u32,
            "position": position,
            "size": size,
            "scale_2c": scale_2c,
            "aux_float": aux_float,
            "scale_30": scale_30,
            "flags": [flag_11, *common_flags, *common_flags_58],
            "colors": common_colors,
            "resource_40": resource_40,
            "vectors_48_50": [vector_48, vector_50],
            "common_strings": common_strings,
            "type_fields": fields,
        }
    except (HudFormatError, struct.error) as exc:
        raise HudFormatError(
            f"element {index} at 0x{start:x} (cursor 0x{reader.offset:x}): {exc}"
        ) from exc


def parse_hud(data: bytes, source: str = "<memory>") -> dict[str, Any]:
    reader = Reader(data, "HUD header")
    if reader.u32() != 3:
        raise HudFormatError("expected length-prefixed 3-byte HUD marker")
    marker = reader.take(3)
    if marker not in KNOWN_MARKERS:
        raise HudFormatError(f"unknown HUD marker {marker!r}")
    version = reader.u8()
    if version != EXPECTED_VERSION:
        raise HudFormatError(f"this probe supports HUD format v12 only, got v{version}")

    sections: dict[str, bytes] = {}
    for section_name in SECTION_NAMES:
        section_len = reader.u32()
        sections[section_name] = reader.take(section_len)
    if reader.offset != len(data):
        raise HudFormatError(f"{len(data) - reader.offset} trailing byte(s) after HUD sections")

    general_reader = Reader(sections["general"], "general section")
    initial_action = general_reader.string()
    if general_reader.offset != len(sections["general"]):
        raise HudFormatError("unparsed bytes remain in the general section")

    elements_reader = Reader(sections["elements"], "elements section")
    count = elements_reader.u32()
    if count > MAX_ELEMENTS:
        raise HudFormatError(f"unreasonable element count {count}")
    records = [_parse_element(elements_reader, i) for i in range(count)]
    if elements_reader.offset != len(sections["elements"]):
        raise HudFormatError(
            f"{len(sections['elements']) - elements_reader.offset} unparsed byte(s) remain "
            f"in elements section at 0x{elements_reader.offset:x}"
        )

    type_counts = Counter(record["type"] for record in records)
    return {
        "schema": "dq-hud-elements-probe-v41",
        "source": source,
        "file_size": len(data),
        "marker": marker.decode("ascii"),
        "format_version": version,
        "initial_action": initial_action,
        "section_sizes": {name: len(value) for name, value in sections.items()},
        "element_count": count,
        "element_type_counts": {str(k): type_counts[k] for k in sorted(type_counts)},
        "elements_payload_size": len(sections["elements"]),
        "parsed_elements_payload_bytes": elements_reader.offset,
        "records": records,
        "rewrite_supported": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hud", type=pathlib.Path, nargs="+", help="input HUD resource(s), read-only")
    parser.add_argument("--output-dir", type=pathlib.Path, help="optional directory for JSON reports")
    parser.add_argument("--summary", action="store_true", help="print concise per-file results")
    args = parser.parse_args()

    failures = []
    successes = []
    for hud_path in args.hud:
        try:
            report = parse_hud(hud_path.read_bytes(), str(hud_path))
            if args.output_dir:
                args.output_dir.mkdir(parents=True, exist_ok=True)
                output_path = args.output_dir / f"{hud_path.name}.json"
                output_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
            successes.append(report)
            if args.summary:
                counts = ",".join(f"{key}:{value}" for key, value in report["element_type_counts"].items())
                print(f"PASS {hud_path.name}: elements={report['element_count']} types={counts} bytes={report['parsed_elements_payload_bytes']}/{report['elements_payload_size']}")
        except (OSError, HudFormatError, struct.error) as exc:
            failures.append({"path": str(hud_path), "error": str(exc)})
            print(f"FAIL {hud_path}: {exc}")

    print(json.dumps({
        "tested": len(args.hud),
        "passed": len(successes),
        "failed": len(failures),
        "failures": failures,
        "rewrite_supported": False,
        "records": [{"path": report["source"], "element_count": report["element_count"], "element_type_counts": report["element_type_counts"]} for report in successes],
    }, indent=2, ensure_ascii=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Synthetic v12 regression tests; contain no original Dungeon Quest assets."""
from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from hud_elements_probe_v41 import HudFormatError, parse_hud  # noqa: E402


def s(value: bytes | str = b"") -> bytes:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return struct.pack("<I", len(raw)) + raw


def f32(value: float = 0.0) -> bytes:
    return struct.pack("<f", value)


def common(name: str, element_type: int) -> bytes:
    out = bytearray(s(name))
    out += bytes([element_type]) + s("label") + struct.pack("<I", 0x80000001)
    out += b"\x01" + f32(1) + f32(2) + f32(3) + f32(4) + f32(5) + f32(0)
    out += bytes([1, 2, 3, 4, 5]) + f32(7)
    out += bytes([255, 1, 2, 3]) * 3 + s("resource")
    out += f32(8) + f32(9) + f32(10) + f32(11) + bytes([1, 1])
    out += s("a") + s("b") + s("c") + s("d")
    return bytes(out)


def type_specific(element_type: int) -> bytes:
    if element_type == 1 or element_type in (5, 9, 10, 13, 16):
        return b""
    if element_type == 2:
        return s("s140") + f32(1) * 3 + bytes([1, 2, 3, 4, 5]) + s("r160") + s("s168") + s("s178")
    if element_type == 3:
        return bytes([1]) + f32(1) * 3 + bytes([2, 3, 4]) + f32(5) * 2 + s("r208") + s("s210") + f32(6) + s("r228") + s("r238") + (b"\x01\x02\x03\x04" * 7) + b"".join(s(f"r{i}") for i in range(8)) + f32(7) * 2
    if element_type == 4:
        return s("s60") + f32(1) * 3 + bytes([1, 2, 3, 4, 5]) + s("r88")
    if element_type == 6:
        return bytes([1]) + s("s90") + f32(1) * 3 + bytes([1, 2, 3, 4, 5]) + s("rb0") + s("sb8")
    if element_type == 7:
        return s("resource")
    if element_type == 8:
        return bytes([1, 2])
    if element_type == 11:
        return bytes([1]) + struct.pack("<hhh", 2, 3, 4) + s("s1a8") + s("r1b8")
    if element_type in (12, 14):
        return s("resource")
    if element_type == 15:
        return bytes([1]) + s("se0") + f32(1) * 3 + bytes([2, 3, 4, 5, 6]) + s("r108") + s("s120") + s("s130") + s("r110") + s("r118")
    raise AssertionError(f"unhandled fixture type {element_type}")


def make_hud(element_types: list[int], marker: bytes = b"NcP") -> bytes:
    records = b"".join(common(f"element_{i}_type_{t}", t) + type_specific(t) for i, t in enumerate(element_types))
    elements = struct.pack("<I", len(element_types)) + records
    general = s("onOpen")
    actions = struct.pack("<H", 0)
    timers = struct.pack("<H", 0)
    sections = (general, elements, actions, timers)
    return struct.pack("<I", 3) + marker + bytes([12]) + b"".join(struct.pack("<I", len(x)) + x for x in sections)


class HudElementsProbeV41Tests(unittest.TestCase):
    def test_all_v12_element_type_schemas_consume_exact_payload(self) -> None:
        data = make_hud(list(range(1, 16)))
        report = parse_hud(data, "synthetic-all-types.hud")
        self.assertEqual(report["element_count"], 15)
        self.assertEqual(report["parsed_elements_payload_bytes"], report["elements_payload_size"])
        self.assertEqual([row["type"] for row in report["records"]], list(range(1, 16)))
        list_row = report["records"][2]
        self.assertEqual(len(list_row["type_fields"]["colors_230_250"]), 7)
        self.assertEqual(len(list_row["type_fields"]["resources_258_290"]), 8)
        self.assertFalse(report["rewrite_supported"])

    def test_non_utf8_legacy_string_bytes_are_preserved(self) -> None:
        raw = common("legacy-bytes", 1)
        raw = raw.replace(s("label"), s(b"label\x93"), 1)
        elements = struct.pack("<I", 1) + raw
        sections = (s(""), elements, struct.pack("<H", 0), struct.pack("<H", 0))
        data = struct.pack("<I", 3) + b"NcP" + b"\x0c" + b"".join(struct.pack("<I", len(x)) + x for x in sections)
        report = parse_hud(data)
        escaped = report["records"][0]["label"].encode("unicode_escape").decode("ascii")
        self.assertIn("\\udc93", escaped)

    def test_rejects_unknown_type_and_truncated_resource(self) -> None:
        with self.assertRaises(HudFormatError):
            parse_hud(make_hud([16]))
        with self.assertRaises(HudFormatError):
            parse_hud(make_hud([3])[:-1])

    def test_rejects_wrong_version_and_trailing_bytes(self) -> None:
        raw = bytearray(make_hud([1]))
        raw[7] = 11
        with self.assertRaises(HudFormatError):
            parse_hud(bytes(raw))
        with self.assertRaises(HudFormatError):
            parse_hud(make_hud([1]) + b"x")


if __name__ == "__main__":
    unittest.main(verbosity=2)

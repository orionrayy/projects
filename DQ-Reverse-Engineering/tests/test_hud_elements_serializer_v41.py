#!/usr/bin/env python3
"""Synthetic canonical HUD serializer regressions; no game binary fixtures."""
from __future__ import annotations
import math
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from hud_elements_probe_v41 import HudFormatError, parse_hud  # noqa: E402
from hud_elements_serializer_v41 import canonical_serialize_hud  # noqa: E402
from test_hud_elements_probe_v41 import make_hud  # noqa: E402


class HudElementsSerializerV41Tests(unittest.TestCase):
    def test_all_v12_element_types_round_trip_byte_identically(self) -> None:
        source = make_hud(list(range(1, 16)))
        output, report = canonical_serialize_hud(source, "synthetic-all-v12-types.hud")
        self.assertEqual(output, source)
        self.assertTrue(report["byte_identical"])
        self.assertEqual(report["changed_byte_count"], 0)
        self.assertEqual(report["element_count"], 15)

    def test_nonzero_native_canonicalized_common_field_fails_closed(self) -> None:
        source = bytearray(make_hud([1]))
        parsed = parse_hud(bytes(source))
        e = parsed["records"][0]
        general_len = struct.unpack_from("<I", source, 8)[0]
        elements_data_abs = 8 + 4 + general_len + 4
        record_start_abs = elements_data_abs + e["offset"]
        name_len = len(e["name"].encode("utf-8", errors="surrogateescape"))
        label_len = len(e["label"].encode("utf-8", errors="surrogateescape"))
        aux_offset = record_start_abs + 4 + name_len + 1 + 4 + label_len + 4 + 1 + 8 + 8 + 4
        struct.pack_into("<f", source, aux_offset, 1.25)
        with self.assertRaisesRegex(HudFormatError, "field is not zero"):
            canonical_serialize_hud(bytes(source), "synthetic-nonzero-aux.hud")

    def test_nonfinite_numeric_values_are_rejected(self) -> None:
        parsed = parse_hud(make_hud([1]))
        parsed["records"][0]["position"][0] = math.nan
        from hud_elements_serializer_v41 import serialize_element
        with self.assertRaisesRegex(HudFormatError, "non-finite float"):
            serialize_element(parsed["records"][0])

    def test_source_sections_outside_element_payload_are_preserved(self) -> None:
        source = make_hud([1, 3, 8, 15])
        output, _ = canonical_serialize_hud(source)
        parsed = parse_hud(source)
        sections = []
        cur = 8
        for _ in range(4):
            length = struct.unpack_from("<I", source, cur)[0]
            start = cur + 4
            sections.append(source[start:start + length])
            cur = start + length
        out_sections = []
        cur = 8
        for _ in range(4):
            length = struct.unpack_from("<I", output, cur)[0]
            start = cur + 4
            out_sections.append(output[start:start + length])
            cur = start + length
        self.assertEqual(sections[0], out_sections[0])
        self.assertEqual(sections[2], out_sections[2])
        self.assertEqual(sections[3], out_sections[3])
        self.assertEqual(parse_hud(output)["element_count"], parsed["element_count"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

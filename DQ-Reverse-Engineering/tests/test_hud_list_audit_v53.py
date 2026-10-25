#!/usr/bin/env python3
"""Synthetic tests for the read-only HUD List element audit."""
from __future__ import annotations
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
from hud_list_audit_v53 import audit_bytes
from test_hud_elements_codec_v42 import fixture

class HudListAuditV53Tests(unittest.TestCase):
    def test_audit_finds_single_type3_list_and_records_template_boundary(self):
        data = fixture([1, 3, 2])
        report = audit_bytes(data, "synthetic-list.hud")
        self.assertEqual(report["element_count"], 3)
        self.assertEqual(report["type3_list_count"], 1)
        item = report["list_elements"][0]
        self.assertEqual(item["name"], "el1")
        self.assertEqual(item["serialized_record_bytes"] > 0, True)
        self.assertTrue(item["runtime_item_population_serialized"] is False)
        self.assertEqual(len(item["resource_fields"]), 11)

    def test_no_list_returns_zero_type3_records(self):
        report = audit_bytes(fixture([1, 2, 4]), "no-list.hud")
        self.assertEqual(report["type3_list_count"], 0)
        self.assertEqual(report["list_elements"], [])

    def test_corrupt_hud_fails_closed(self):
        with self.assertRaises(Exception):
            audit_bytes(fixture([3])[:-1], "truncated.hud")

if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Synthetic tests for the v57 static native row-precedent evidence gate."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_native_template_row_precedents_v57 import AuditError, validate_audit

REPORT = ROOT / "docs" / "NATIVE_TEMPLATE_ROW_PRECEDENT_AUDIT_V57.json"

class NativeTemplateRowPrecedentV57Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_canonical_report_passes_without_promoting_dispatch(self):
        summary = validate_audit(copy.deepcopy(self.base))
        self.assertEqual(summary["aim_files_parsed"], 162)
        self.assertEqual(summary["catalog_items"], 222)
        self.assertEqual(summary["catalog_routes_assigned"], 0)
        self.assertFalse(summary["generic_dispatch_proven"])

    def test_codex_and_legendex_method_ownership_must_not_be_conflated(self):
        data = copy.deepcopy(self.base)
        codex = next(x for x in data["model_precedents"] if x["model"] == "uai_gp_codex")
        codex["key_function_names_observed"].append("UpdateList")
        with self.assertRaisesRegex(AuditError, "belongs to LegendEx"):
            validate_audit(data)

    def test_catalog_route_count_cannot_be_claimed_without_registry_and_runtime_evidence(self):
        data = copy.deepcopy(self.base)
        data["integration_gate"]["catalog_routes_assigned"] = 1
        with self.assertRaisesRegex(AuditError, "unproven catalog routes"):
            validate_audit(data)

    def test_generic_dispatch_cannot_be_promoted_from_symbol_names(self):
        data = copy.deepcopy(self.base)
        data["integration_gate"]["stable_id_selection_dispatch_proven"] = True
        with self.assertRaisesRegex(AuditError, "stable_id_selection_dispatch_proven"):
            validate_audit(data)

    def test_aim_failure_or_hash_drift_fails_closed(self):
        data = copy.deepcopy(self.base)
        data["source_inventory"]["aim_files_failed"] = 1
        with self.assertRaisesRegex(AuditError, "framing failures"):
            validate_audit(data)
        data = copy.deepcopy(self.base)
        data["target"]["native_library_sha256"] = "bad"
        with self.assertRaisesRegex(AuditError, "invalid native_library_sha256"):
            validate_audit(data)

    def test_legendex_must_keep_both_row_builder_and_updater(self):
        data = copy.deepcopy(self.base)
        legendex = next(x for x in data["model_precedents"] if x["model"] == "uai_gp_legendex")
        legendex["key_function_names_observed"] = ["CreateLegendItem"]
        with self.assertRaisesRegex(AuditError, "LegendEx must retain"):
            validate_audit(data)

if __name__ == "__main__":
    unittest.main(verbosity=2)

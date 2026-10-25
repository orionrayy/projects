#!/usr/bin/env python3
"""Synthetic fail-closed regression tests for v70 exact-target DEX report."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_dex_lifecycle_target_build_v70 import AuditError, validate

REPORT = ROOT / "docs" / "DEX_LIFECYCLE_TARGET_BUILD_V70.json"

class DexLifecycleTargetBuildV70Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_pinned_target_build_manifest_passes_with_runtime_blocked(self):
        result = validate(copy.deepcopy(self.base))
        self.assertEqual(result["status"], "PASS_STATIC_TARGET_DEX_ASSEMBLY_ROUNDTRIP")
        self.assertEqual(result["source_classes"], 10768)
        self.assertEqual(result["patched_classes"], 10769)
        self.assertEqual(result["changed_classes_vs_baseline"], 2)
        self.assertEqual(result["lifecycle_sites_verified"], 2)
        self.assertEqual(result["gold_runtime_checks"], "0/9")
        self.assertEqual(result["catalog_runtime_verified"], "0/222")
        self.assertFalse(result["promotion_allowed"])

    def test_source_dex_hash_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["source_dex"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "source DEX SHA-256 mismatch"):
            validate(doc)

    def test_source_renderer_disassembly_hash_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["source_dex"]["method_source_sha256"] = "f" * 64
        with self.assertRaisesRegex(AuditError, "source renderer disassembly SHA-256 mismatch"):
            validate(doc)

    def test_baseline_assembler_method_bodies_must_remain_unchanged(self):
        doc = copy.deepcopy(self.base)
        doc["baseline_reassemble"]["non_field_differences"] = ["com/shinybox/smash/Smash.smali"]
        with self.assertRaisesRegex(AuditError, "baseline method-body differences"):
            validate(doc)

    def test_baseline_normalization_set_is_exact(self):
        doc = copy.deepcopy(self.base)
        doc["baseline_reassemble"]["changed_files"].append("com/shinybox/smash/Smash.smali")
        with self.assertRaisesRegex(AuditError, "baseline smali normalization file count"):
            validate(doc)

    def test_patched_dex_hash_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["patched_dex"]["sha256"] = "1" * 64
        with self.assertRaisesRegex(AuditError, "patched DEX SHA-256 mismatch"):
            validate(doc)

    def test_missing_classes_are_rejected(self):
        doc = copy.deepcopy(self.base)
        doc["patched_dex"]["missing_classes"] = ["com/shinybox/smash/Smash.smali"]
        with self.assertRaisesRegex(AuditError, "round-trip lost"):
            validate(doc)

    def test_only_renderer_and_probe_classes_may_differ(self):
        doc = copy.deepcopy(self.base)
        doc["patched_dex"]["changed_classes_vs_baseline"].append("com/shinybox/smash/Smash.smali")
        with self.assertRaisesRegex(AuditError, "changed class set"):
            validate(doc)

    def test_probe_must_run_only_after_successful_engine_init(self):
        doc = copy.deepcopy(self.base)
        doc["lifecycle_checks"]["register_only_after_true_init_result"] = False
        with self.assertRaisesRegex(AuditError, "gated by successful engineInitialize"):
            validate(doc)

    def test_unregister_must_precede_both_shutdown_sites(self):
        doc = copy.deepcopy(self.base)
        doc["lifecycle_checks"]["shutdown_hook_order"][0]["unregister_precedes_shutdown"] = False
        with self.assertRaisesRegex(AuditError, "order mismatch"):
            validate(doc)

    def test_cannot_claim_apk_runtime_or_catalog_completion(self):
        doc = copy.deepcopy(self.base)
        doc["apk_or_xapk_built"] = True
        with self.assertRaisesRegex(AuditError, "APK/XAPK was built"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["catalog_runtime_verified_effects"] = 222
        with self.assertRaisesRegex(AuditError, "catalog integration counts"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["promotion_allowed"] = True
        with self.assertRaisesRegex(AuditError, "promotion must remain blocked"):
            validate(doc)

if __name__ == "__main__":
    unittest.main(verbosity=2)

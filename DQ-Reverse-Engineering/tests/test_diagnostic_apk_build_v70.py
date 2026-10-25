#!/usr/bin/env python3
"""Synthetic fail-closed regression tests for the v70 diagnostic APK report."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_diagnostic_apk_build_v70 import AuditError, validate

REPORT = ROOT / "docs" / "DIAGNOSTIC_APK_BUILD_V70.json"

class DiagnosticApkBuildV70Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_pinned_package_report_passes_but_runtime_stays_blocked(self):
        result = validate(copy.deepcopy(self.base))
        self.assertEqual(result["status"], "PASS_STATIC_DIAGNOSTIC_APK_REPORT")
        self.assertEqual(result["apk_sha256"], "07898a4997b1f470728087d6c4bcd22660980be6d0670217d6d64c2b1769d0e8")
        self.assertEqual(result["package_id"], "com.shinybox.dqv70")
        self.assertFalse(result["game_runtime_tested"])
        self.assertEqual(result["gold_runtime_checks"], "0/9")
        self.assertEqual(result["catalog_runtime_verified"], "0/222")
        self.assertFalse(result["promotion_allowed"])

    def test_apk_hash_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["artifact"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "diagnostic APK SHA-256 mismatch"):
            validate(doc)

    def test_test_package_id_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["artifact"]["package_id"] = "com.shinybox.smash"
        with self.assertRaisesRegex(AuditError, "diagnostic package ID mismatch"):
            validate(doc)

    def test_input_dex_and_bridge_hashes_are_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["inputs"]["patched_dex_sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "patched DEX hash mismatch"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["inputs"]["bridge_sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "bridge hash mismatch"):
            validate(doc)

    def test_alignment_and_signature_gates_must_all_pass(self):
        for key in ("zipalign_pre_sign_16k_native", "zipalign_post_sign_16k_native",
                    "apksigner_verify_v1", "apksigner_verify_v2", "apksigner_verify_v3",
                    "aapt_dump_badging"):
            doc = copy.deepcopy(self.base)
            doc["validation"][key] = "FAIL"
            with self.subTest(key=key), self.assertRaisesRegex(AuditError, f"validation.{key}"):
                validate(doc)

    def test_official_signer_must_not_be_claimed(self):
        doc = copy.deepcopy(self.base)
        doc["validation"]["signer"]["matches_official_signer"] = True
        with self.assertRaisesRegex(AuditError, "must not claim official signer match"):
            validate(doc)

    def test_private_test_key_must_not_be_shared(self):
        doc = copy.deepcopy(self.base)
        doc["validation"]["signer"]["private_key_shared"] = True
        with self.assertRaisesRegex(AuditError, "private test key must remain private"):
            validate(doc)

    def test_original_application_artifacts_must_remain_untouched(self):
        doc = copy.deepcopy(self.base)
        doc["package_transform"]["original_apk_modified_in_place"] = True
        with self.assertRaisesRegex(AuditError, "original game artifacts"):
            validate(doc)

    def test_runtime_cannot_be_promoted_without_device_evidence(self):
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["launched_on_device"] = True
        with self.assertRaisesRegex(AuditError, "must not claim device launch"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["promotion_allowed"] = True
        with self.assertRaisesRegex(AuditError, "must not be promoted"):
            validate(doc)

    def test_gold_and_catalog_runtime_claims_cannot_be_fabricated(self):
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["gold_runtime_checks_passed"] = 9
        with self.assertRaisesRegex(AuditError, "Gold candidate gate"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["catalog_runtime_verified_effects"] = 222
        with self.assertRaisesRegex(AuditError, "catalog integration count"):
            validate(doc)

    def test_missing_device_runtime_limitation_fails_closed(self):
        doc = copy.deepcopy(self.base)
        doc["limitations"] = ["static checks only"]
        with self.assertRaisesRegex(AuditError, "device runtime limitation"):
            validate(doc)

if __name__ == "__main__":
    unittest.main(verbosity=2)

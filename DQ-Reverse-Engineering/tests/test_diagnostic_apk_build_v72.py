#!/usr/bin/env python3
"""Regression tests for the v72 diagnostic report validator."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_diagnostic_apk_build_v72 import AuditError, validate

REPORT = ROOT / "docs" / "DIAGNOSTIC_APK_BUILD_V72.json"

class DiagnosticApkBuildV72Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_pinned_static_report_passes_but_runtime_stays_blocked(self):
        result = validate(copy.deepcopy(self.base))
        self.assertEqual(result["status"], "PASS_STATIC_V72_DIAGNOSTIC_REPORT")
        self.assertEqual(result["gold_runtime_checks"], "0/9")
        self.assertEqual(result["catalog_runtime_verified"], "0/222")
        self.assertFalse(result["runtime_logcat_verified"])
        self.assertFalse(result["promotion_allowed"])

    def test_apk_hash_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["artifact"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "APK SHA-256 mismatch"):
            validate(doc)

    def test_package_id_and_launcher_label_are_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["artifact"]["package_id"] = "com.shinybox.smash"
        with self.assertRaisesRegex(AuditError, "package ID mismatch"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["artifact"]["launcher_label"] = "Dungeon Quest"
        with self.assertRaisesRegex(AuditError, "launcher label mismatch"):
            validate(doc)

    def test_static_signature_and_alignment_gates_are_fail_closed(self):
        for key in ("zipalign_pre_sign_16k_native", "zipalign_post_sign_16k_native",
                    "apksigner_verify_v1", "apksigner_verify_v2", "apksigner_verify_v3", "aapt_dump_badging"):
            doc = copy.deepcopy(self.base)
            doc["validation"][key] = "FAIL"
            with self.subTest(key=key), self.assertRaisesRegex(AuditError, f"validation.{key}"):
                validate(doc)

    def test_original_app_and_private_key_must_remain_untouched(self):
        doc = copy.deepcopy(self.base)
        doc["package_transform"]["original_apk_modified_in_place"] = True
        with self.assertRaisesRegex(AuditError, "original game artifacts"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["validation"]["signer"]["private_key_shared"] = True
        with self.assertRaisesRegex(AuditError, "private test key"):
            validate(doc)

    def test_logcat_markers_must_be_complete_and_not_fabricated(self):
        doc = copy.deepcopy(self.base)
        doc["probe_observability"]["expected_markers"].remove("callback_roundtrip=PASS")
        with self.assertRaisesRegex(AuditError, "expected diagnostic markers"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["probe_observability"]["runtime_markers_verified"] = True
        with self.assertRaisesRegex(AuditError, "must not fabricate runtime Logcat"):
            validate(doc)

    def test_runtime_and_promotion_must_remain_blocked(self):
        for key in ("installed_on_device", "launched_on_device", "offline_tested",
                    "native_probe_roundtrip_21_to_42_verified", "shutdown_unregister_verified"):
            doc = copy.deepcopy(self.base)
            doc["runtime_gate"][key] = True
            with self.subTest(key=key), self.assertRaisesRegex(AuditError, f"runtime gate {key}"):
                validate(doc)
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["gold_runtime_checks_passed"] = 9
        with self.assertRaisesRegex(AuditError, "Gold candidate"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["promotion_allowed"] = True
        with self.assertRaisesRegex(AuditError, "must not be promoted"):
            validate(doc)

    def test_physical_device_limitation_must_be_explicit(self):
        doc = copy.deepcopy(self.base)
        doc["limitations"] = ["static checks only"]
        with self.assertRaisesRegex(AuditError, "physical-device/runtime limitation"):
            validate(doc)

if __name__ == "__main__":
    unittest.main(verbosity=2)

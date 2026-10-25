#!/usr/bin/env python3
"""Synthetic fail-closed regressions for v69 native binary cross-check."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_native_client_abi_binary_crosscheck_v69 import AuditError, validate

REPORT = ROOT / "docs" / "NATIVE_CLIENT_ABI_BINARY_CROSSCHECK_V69.json"

class NativeClientAbiBinaryCrosscheckV69Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_pinned_static_crosscheck_passes_but_runtime_remains_blocked(self):
        result = validate(copy.deepcopy(self.base))
        self.assertEqual(result["status"], "PASS_STATIC_ABI_CROSSCHECK")
        self.assertEqual(result["target_symbols_verified"], 3)
        self.assertEqual(result["bridge_jni_exports_verified"], 3)
        self.assertEqual(result["runtime_checks_passed"], 0)
        self.assertEqual(result["catalog_runtime_verified"], "0/222")
        self.assertFalse(result["promotion_allowed"])

    def test_target_library_hash_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["target"]["library"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "target library SHA-256 mismatch"):
            validate(doc)

    def test_target_register_symbol_address_is_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["symbols"]["register"]["address"] = "0x7aec18"
        with self.assertRaisesRegex(AuditError, "symbols.register.address mismatch"):
            validate(doc)

    def test_target_symbol_table_must_remain_dynamic_and_global(self):
        doc = copy.deepcopy(self.base)
        doc["symbols"]["dispatcher"]["symbol_is_in_dynamic_symbol_table"] = False
        with self.assertRaisesRegex(AuditError, "dlsym visibility"):
            validate(doc)

    def test_bridge_hash_and_jni_exports_are_pinned(self):
        doc = copy.deepcopy(self.base)
        doc["bridge_artifact"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(AuditError, "bridge SHA-256 mismatch"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["bridge_artifact"]["jni_exports"].append("Java_fake_extra")
        with self.assertRaisesRegex(AuditError, "JNI export set mismatch"):
            validate(doc)

    def test_cannot_claim_bridge_is_packaged_or_runtime_invoked(self):
        doc = copy.deepcopy(self.base)
        doc["bridge_artifact"]["packaged_into_game"] = True
        with self.assertRaisesRegex(AuditError, "must not claim bridge is packaged"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["bridge_artifact"]["runtime_invoked"] = True
        with self.assertRaisesRegex(AuditError, "must not claim runtime invocation"):
            validate(doc)

    def test_exact_target_header_must_remain_explicitly_missing(self):
        doc = copy.deepcopy(self.base)
        doc["layout_evidence"]["aifunction"]["exact_target_header_available"] = True
        with self.assertRaisesRegex(AuditError, "exact target header"):
            validate(doc)

    def test_runtime_gate_cannot_be_promoted_without_device_evidence(self):
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["promotion_allowed"] = True
        with self.assertRaisesRegex(AuditError, "promotion must remain blocked"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["callback_registration_runtime_verified"] = True
        with self.assertRaisesRegex(AuditError, "callback_registration_runtime_verified"):
            validate(doc)

    def test_catalog_routes_and_gold_runtime_count_cannot_be_fabricated(self):
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["catalog_native_routes_assigned"] = 1
        with self.assertRaisesRegex(AuditError, "catalog counts must remain"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["runtime_gate"]["gold_candidate_checks_passed"] = 1
        with self.assertRaisesRegex(AuditError, "Gold runtime gate must remain"):
            validate(doc)

    def test_wrong_architecture_and_symbol_size_fail_closed(self):
        doc = copy.deepcopy(self.base)
        doc["bridge_artifact"]["elf_machine"] = "x86-64"
        with self.assertRaisesRegex(AuditError, "bridge must be ELF64/AArch64"):
            validate(doc)
        doc = copy.deepcopy(self.base)
        doc["symbols"]["unregister"]["size_bytes"] = 133
        with self.assertRaisesRegex(AuditError, "symbols.unregister.size_bytes mismatch"):
            validate(doc)

    def test_wrong_evidence_scope_cannot_claim_runtime_validation(self):
        doc = copy.deepcopy(self.base)
        doc["evidence"]["evidence_scope"] = "Runtime-tested inside Dungeon Quest"
        with self.assertRaisesRegex(AuditError, "evidence scope must remain static-only"):
            validate(doc)

if __name__ == "__main__":
    unittest.main(verbosity=2)

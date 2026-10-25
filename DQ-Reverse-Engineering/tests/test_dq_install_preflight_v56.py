#!/usr/bin/env python3
"""Synthetic unit tests for install-conflict classification; no device/package mutation."""
from __future__ import annotations
import pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from dq_install_preflight_v56 import classify_update

class InstallPreflightV56Tests(unittest.TestCase):
    def test_same_package_different_signer_predicts_update_conflict(self):
        stock = {"package_id":"com.shinybox.smash", "signer_fingerprints":["AA:11"]}
        candidate = {"package_id":"com.shinybox.smash", "signer_fingerprints":["BB:22"]}
        self.assertEqual(classify_update(stock, candidate), "IN_PLACE_UPDATE_REJECTED_SIGNATURE_MISMATCH_EXPECTED")

    def test_same_package_same_signer_only_passes_identity_gate(self):
        stock = {"package_id":"com.shinybox.smash", "signer_fingerprints":["AA:11"]}
        candidate = {"package_id":"com.shinybox.smash", "signer_fingerprints":["AA:11"]}
        self.assertEqual(classify_update(stock, candidate), "SIGNATURE_IDENTITY_COMPATIBLE_OTHER_INSTALL_GATES_UNCHECKED")

    def test_different_package_can_be_side_by_side_but_runtime_is_unknown(self):
        stock = {"package_id":"com.shinybox.smash", "signer_fingerprints":["AA:11"]}
        candidate = {"package_id":"com.shinybox.dqmod", "signer_fingerprints":["BB:22"]}
        self.assertEqual(classify_update(stock, candidate), "SEPARATE_INSTALL_ID_POSSIBLE_RUNTIME_UNVERIFIED")

    def test_missing_signer_fails_closed(self):
        stock = {"package_id":"com.shinybox.smash", "signer_fingerprints":[]}
        candidate = {"package_id":"com.shinybox.smash", "signer_fingerprints":["BB:22"]}
        self.assertEqual(classify_update(stock, candidate), "UNKNOWN_SIGNER_IDENTITY")

    def test_missing_package_fails_closed(self):
        self.assertEqual(classify_update({}, {"package_id":"com.shinybox.dqmod", "signer_fingerprints":["AA"]}), "UNKNOWN_PACKAGE_ID")

if __name__ == "__main__":
    unittest.main(verbosity=2)

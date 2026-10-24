import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_iap_runtime_evidence_v13 import audit_matrix


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "IAP_SKU_RUNTIME_EVIDENCE_V13.json"


class IAPRuntimeEvidenceV13Tests(unittest.TestCase):
    def test_current_matrix_passes_and_keeps_every_reward_unverified(self):
        result = audit_matrix(MATRIX)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["records"], 109)
        self.assertEqual(result["runtime_reward_verified"], 0)
        self.assertEqual(result["runtime_reward_unverified"], 109)

    def test_verified_requires_runtime_and_persistence_evidence(self):
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        data["records"][0]["runtime_evidence"]["reward_status"] = "VERIFIED"
        # Leave payload, persistence observation, test result and evidence unset.
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "matrix.json"
            target.write_text(json.dumps(data), encoding="utf-8")
            result = audit_matrix(target)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("VERIFIED requires" in error for error in result["errors"]))

    def test_registry_mismatch_fails_closed(self):
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        data["records"][0]["sources"]["dex_static_sku"] = False
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "matrix.json"
            target.write_text(json.dumps(data), encoding="utf-8")
            result = audit_matrix(target)
        self.assertEqual(result["status"], "FAIL")

    def test_tampered_runtime_summary_fails_closed(self):
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        data["evidence_counts"]["runtime_reward_unverified"] = 108
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "matrix.json"
            target.write_text(json.dumps(data), encoding="utf-8")
            result = audit_matrix(target)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("runtime_reward_unverified summary" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()

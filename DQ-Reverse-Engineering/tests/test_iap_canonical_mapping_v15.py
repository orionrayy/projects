import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_iap_canonical_mapping_v15 import audit_mapping

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "IAP_CANONICAL_MAPPING_V15.json"


class CanonicalIAPMappingV15Tests(unittest.TestCase):
    def test_full_registry_and_runtime_boundary(self):
        result = audit_mapping(MATRIX)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["records"], 109)
        self.assertEqual(result["runtime_grants_verified"], 0)
        self.assertEqual(result["vanity_records_unit_verified_for_data_patch"], 46)

    def test_gold_amounts_are_exact_and_distinct_from_gold_boost(self):
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        records = {r["legacy_id"]: r for r in data["records"]}
        self.assertEqual(records["gold"]["family"], "gameplay_boost")
        self.assertEqual(records["gold"]["reward_payload"]["flag"], "iap.boostGold")
        self.assertEqual(records["crystal"]["reward_payload"]["flag"], "iap.boostCS")
        self.assertEqual(records["mythstone"]["reward_payload"]["flag"], "iap.boostMS")
        self.assertEqual(records["gold5"]["reward_payload"]["amount"], 1_000_000_000)

    def test_bundle_component_tampering_fails_closed(self):
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        package20 = next(r for r in data["records"] if r["legacy_id"] == "package20")
        package20["reward_payload"]["items"].pop()
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "matrix.json"
            target.write_text(json.dumps(data), encoding="utf-8")
            result = audit_mapping(target)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("package20" in e for e in result["errors"]))

    def test_mislabelled_vanity_runtime_is_rejected(self):
        data = json.loads(MATRIX.read_text(encoding="utf-8"))
        vanity1 = next(r for r in data["records"] if r["legacy_id"] == "vanity1")
        vanity1["test_status"]["runtime"] = "RUNTIME-VERIFIED"
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "matrix.json"
            target.write_text(json.dumps(data), encoding="utf-8")
            result = audit_mapping(target)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("vanity1" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()

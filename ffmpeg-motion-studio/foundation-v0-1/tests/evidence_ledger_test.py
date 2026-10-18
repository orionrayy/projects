import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / "research" / "evidence-ledger.json").read_text(encoding="utf-8"))
SCENE = json.loads((ROOT / "scenes" / "scene-001.json").read_text(encoding="utf-8"))

class EvidenceLedgerTests(unittest.TestCase):
    def test_claim_ids_are_unique(self):
        ids = [item["id"] for item in LEDGER["records"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_unperformed_training_is_not_claimed_as_learning(self):
        records = {item["id"]: item for item in LEDGER["records"]}
        self.assertEqual(records["data.external-datasets"]["status"], "not_performed")
        self.assertEqual(records["data.model-training"]["status"], "not_performed")
        self.assertEqual(records["data.external-datasets"]["evidence"], [])
        self.assertEqual(records["data.model-training"]["evidence"], [])

    def test_bilateral_render_contract_is_explicit(self):
        expected = {
            "screen-left-arm", "screen-left-hand", "screen-right-arm",
            "pointing-hand", "torso", "head", "legs"
        }
        self.assertEqual(set(SCENE["quality_contract"]["required_render_groups"]), expected)

    def test_source_audit_refs_resolve_inside_project(self):
        records = {item["id"]: item for item in LEDGER["records"]}
        for record_id in ("baseline.single-arm-renderer", "baseline.pose-quality-tautology"):
            for item in records[record_id]["evidence"]:
                self.assertTrue((ROOT / item["path"].replace("ffmpeg-motion-studio/foundation-v0-1/", "")).is_file(),
                                msg=record_id + " missing evidence path " + item["path"])

if __name__ == "__main__":
    unittest.main()

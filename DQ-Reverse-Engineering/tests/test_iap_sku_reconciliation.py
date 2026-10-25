import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "docs" / "IAP_SKU_RECONCILIATION_V7.json"

class IapSkuReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        cls.records = cls.data["records"]

    def test_unique_union_count(self):
        names = [r["legacy_id"] for r in self.records]
        self.assertEqual(len(names), 109)
        self.assertEqual(len(set(names)), 109)

    def test_source_counts(self):
        dex = [r for r in self.records if r["sources"]["dex_static_sku"]]
        xml = [r for r in self.records if r["sources"]["iap_xml_name"]]
        shared = [r for r in self.records if all(r["sources"].values())]
        self.assertEqual(len(dex), 104)
        self.assertEqual(len(xml), 107)
        self.assertEqual(len(shared), 102)
        self.assertEqual(len(xml) - len(shared), 5)
        self.assertEqual(len(dex) - len(shared), 2)

    def test_exact_mismatch_sets(self):
        lookup = {r["legacy_id"]: r for r in self.records}
        xml_only = sorted(k for k, r in lookup.items()
                          if r["sources"]["iap_xml_name"] and not r["sources"]["dex_static_sku"])
        dex_only = sorted(k for k, r in lookup.items()
                          if r["sources"]["dex_static_sku"] and not r["sources"]["iap_xml_name"])
        self.assertEqual(xml_only, ["angelicslime", "demonicslime", "poisonslime", "vanity72", "vanity73"])
        self.assertEqual(dex_only, ["package20", "package21"])

    def test_cosmetic_migration_states(self):
        converted = [r for r in self.records if r["migration_status"] == "draft_converted_to_gold"]
        already_gold = [r for r in self.records if r["migration_status"] == "already_earned_gold"]
        stale_unpriced = [r for r in self.records if r["migration_status"] == "asset_only_unpriced_unreferenced_review"]
        self.assertEqual(len(converted), 16)
        self.assertEqual(len(already_gold), 28)
        self.assertEqual(len(stale_unpriced), 2)
        self.assertTrue(all(r.get("proposed_gold_cost", 0) > 0 for r in converted))

    def test_unknown_bundles_remain_blocked(self):
        blocked = [r for r in self.records if r["family"] == "bundle_contents_unresolved"]
        self.assertEqual(len(blocked), 24)
        self.assertTrue(all(r["migration_status"] == "blocked_contents_unknown" for r in blocked))

if __name__ == "__main__":
    unittest.main()

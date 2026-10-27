import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_first50_flexible_cheats_v81 import validate


class First50FlexibleCheatsV81Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = ROOT / "cheats-sandbox" / "first50_flexible_cheats_v81.json"
        cls.doc = json.loads(cls.catalog.read_text(encoding="utf-8"))
        cls.by_id = {item["id"]: item for item in cls.doc["cheats"]}

    def test_registry_schema_and_uniqueness(self):
        result = validate(self.catalog)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["count"], 50)
        self.assertEqual(result["unique_ids"], 50)
        self.assertEqual(result["unique_labels"], 50)
        self.assertEqual(result["unique_effect_keys"], 50)

    def test_no_cheat_is_promoted_to_runtime_verified(self):
        self.assertEqual(self.doc["runtime_verified"], 0)
        self.assertEqual(self.doc["fully_integrated"], 0)
        self.assertTrue(all(item["runtime_verified"] is False for item in self.doc["cheats"]))

    def test_every_cheat_is_sandbox_scoped(self):
        self.assertTrue(all(item["scope"] == "offline_disposable_profile_only" for item in self.doc["cheats"]))

    def test_configurable_gold_amount_does_not_claim_fixed_gold_route(self):
        item = self.by_id["economy.gold_reward_amount"]
        self.assertEqual(item["adapter_status"], "requires_verified_adapter")
        self.assertIsNone(item["native_route_candidate"])
        self.assertEqual(item["nearby_route_mismatch"], "uai_gp_hud.onDebug(6.0)")
        self.assertIn("fixed at +100,000 Gold", item["notes"])

    def test_boss_variant_is_not_bound_to_fixed_route(self):
        item = self.by_id["enemy.boss_variant"]
        self.assertEqual(item["adapter_status"], "fixed_action_mismatch")
        self.assertIsNone(item["native_route_candidate"])

    def test_duplicate_controls_are_absent_and_dependencies_valid(self):
        self.assertNotIn("player.no_cooldowns", self.by_id)
        self.assertNotIn("progression.level_up_one", self.by_id)
        self.assertEqual(self.by_id["player.auto_heal_threshold"]["requires"], ["player.auto_heal"])
        self.assertEqual(self.by_id["player.auto_heal"]["requires"], [])

    def test_static_candidates_are_not_reported_as_live_handlers(self):
        candidates = [item for item in self.doc["cheats"] if item.get("native_route_candidate")]
        self.assertEqual(len(candidates), 11)
        self.assertTrue(all(item["runtime_verified"] is False for item in candidates))


if __name__ == "__main__":
    unittest.main(verbosity=2)

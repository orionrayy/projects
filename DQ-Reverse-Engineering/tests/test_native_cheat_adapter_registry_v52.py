import copy
import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))
from validate_native_cheat_adapter_registry_v52 import RegistryError, validate_data

class NativeCheatAdapterRegistryV52Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "cheats-sandbox" / "debug_cheats_catalog_v39.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT / "docs" / "NATIVE_CHEAT_ADAPTER_REGISTRY_V52.json").read_text(encoding="utf-8"))

    def test_current_matrix_is_fail_closed_and_truthful(self):
        report = validate_data(self.catalog, self.registry)
        self.assertEqual(report["catalog_items"], 222)
        self.assertEqual(report["catalog_routes"], 0)
        self.assertEqual(report["runtime_verified_catalog_routes"], 0)
        self.assertEqual(report["candidate_actions"], 1)
        self.assertEqual(report["unmapped_catalog_items"], 222)

    def test_duplicate_catalog_id_is_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["cheats"][1]["id"] = catalog["cheats"][0]["id"]
        with self.assertRaisesRegex(RegistryError, "unique"):
            validate_data(catalog, self.registry)

    def test_unknown_catalog_route_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["catalog_routes"] = [{
            "catalog_id": "not.a.real.cheat",
            "status": "candidate_unverified",
            "handler": "uai_gp_hud::onDebug",
            "argument_contract": {"type": "number", "value": 6.0}
        }]
        registry["current_summary"]["catalog_routes"] = 1
        with self.assertRaisesRegex(RegistryError, "unknown catalog ID"):
            validate_data(self.catalog, registry)

    def test_runtime_verified_route_without_evidence_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["catalog_routes"] = [{
            "catalog_id": "player.god_mode",
            "status": "runtime_verified",
            "handler": "native.unproven",
            "argument_contract": {"type": "boolean"},
            "runtime_evidence": None
        }]
        registry["current_summary"].update({
            "catalog_routes": 1,
            "runtime_verified_catalog_routes": 1
        })
        with self.assertRaisesRegex(RegistryError, "runtime_evidence"):
            validate_data(self.catalog, registry)

    def test_fixed_gold_candidate_cannot_masquerade_as_slider_route(self):
        registry = copy.deepcopy(self.registry)
        registry["candidate_actions"][0]["catalog_id"] = "economy.currency_override"
        with self.assertRaisesRegex(RegistryError, "fixed Gold reward"):
            validate_data(self.catalog, registry)

    def test_stale_summary_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["current_summary"]["runtime_verified_catalog_routes"] = 1
        with self.assertRaisesRegex(RegistryError, "stale"):
            validate_data(self.catalog, registry)

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Fail-closed tests for matching legacy debug commands to catalog controls."""
from __future__ import annotations
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"tools"))
from validate_native_debug_catalog_compatibility_v58 import MatrixError,validate
REPORT=ROOT/"docs"/"NATIVE_DEBUG_CATALOG_COMPATIBILITY_V58.json"
CATALOG=ROOT/"cheats-sandbox"/"debug_cheats_catalog_v32.json"
class NativeDebugCatalogCompatibilityV58Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.report=json.loads(REPORT.read_text(encoding="utf-8")); cls.catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
 def test_matrix_passes_without_promoting_any_route(self):
  s=validate(copy.deepcopy(self.report),copy.deepcopy(self.catalog)); self.assertEqual(s["commands_reviewed"],16); self.assertEqual(s["candidate_catalog_ids_reviewed"],12); self.assertEqual(s["exact_catalog_routes_assigned"],0)
 def test_unknown_catalog_id_is_rejected(self):
  d=copy.deepcopy(self.report); d["commands"][1]["candidate_catalog_ids"].append("not.a.real.cheat"); d["summary"]["candidate_catalog_ids_reviewed"]=13
  with self.assertRaisesRegex(MatrixError,"unknown catalog ID"): validate(d,self.catalog)
 def test_fixed_gold_reward_cannot_be_mapped_to_target_slider(self):
  d=copy.deepcopy(self.report); d["commands"][5]["mapping_status"]="no_exact_typed_contract"
  with self.assertRaisesRegex(MatrixError,"command 6 fixed Gold reward"): validate(d,self.catalog)
 def test_spend_gold_context_cannot_be_promoted(self):
  d=copy.deepcopy(self.report); d["commands"][6]["mapping_status"]="no_exact_typed_contract"
  with self.assertRaisesRegex(MatrixError,"command 7 SpendGold"): validate(d,self.catalog)
 def test_route_count_or_runtime_count_cannot_be_fabricated(self):
  d=copy.deepcopy(self.report); d["summary"]["exact_catalog_routes_assigned"]=1
  with self.assertRaisesRegex(MatrixError,"must not create native catalog routes"): validate(d,self.catalog)
  d=copy.deepcopy(self.report); d["summary"]["runtime_verified_catalog_effects"]=1
  with self.assertRaisesRegex(MatrixError,"cannot increase runtime-verified count"): validate(d,self.catalog)
 def test_command_codes_must_be_unique_complete_and_bounded(self):
  d=copy.deepcopy(self.report); d["commands"][1]["command"]=d["commands"][0]["command"]
  with self.assertRaisesRegex(MatrixError,"duplicate debug command code"): validate(d,self.catalog)
if __name__=="__main__": unittest.main(verbosity=2)

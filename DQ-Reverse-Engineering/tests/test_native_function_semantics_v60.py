#!/usr/bin/env python3
"""Fail-closed tests for the v60 native function/handler semantics audit."""
from __future__ import annotations
import copy, json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_native_function_semantics_v60 import AuditError, validate
REPORT=ROOT/"docs"/"NATIVE_FUNCTION_SEMANTICS_V60.json"
class NativeFunctionSemanticsV60Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_canonical_static_audit_passes_without_claiming_runtime(self):
  result=validate(copy.deepcopy(self.base));self.assertEqual(result["catalog_routes"],0);self.assertEqual(result["runtime_verified_effects"],0)
 def test_function_and_handler_names_cannot_be_swapped(self):
  data=copy.deepcopy(self.base);mi=data["model_surface"];mi["confirmed_function_names"].append("onSetGold")
  with self.assertRaisesRegex(AuditError,"function/handler roles"):validate(data)
 def test_onsetgold_cannot_be_promoted_to_authoritative_balance_setter(self):
  data=copy.deepcopy(self.base);row=next(x for x in data["native_function_audit"] if x["name"].startswith("uai_gp_hud::onSetGold("));row["candidate_semantics"]="authoritative_gold_setter"
  with self.assertRaisesRegex(AuditError,"onSetGold must not"):validate(data)
 def test_gold_candidate_cannot_be_mapped_to_currency_slider_by_name(self):
  data=copy.deepcopy(self.base);row=next(x for x in data["native_function_audit"] if x["name"].startswith("uai_gp_hud::RewardGold("));row["catalog_id"]="economy.currency_override"
  with self.assertRaisesRegex(AuditError,"Gold increment cannot be promoted"):validate(data)
 def test_health_mana_level_and_stat_handlers_remain_unmapped(self):
  data=copy.deepcopy(self.base);row=next(x for x in data["native_function_audit"] if x["name"].startswith("uai_gp_hud::onSetHealth("));row["catalog_id"]="player.health_multiplier"
  with self.assertRaisesRegex(AuditError,"unsafe promotion"):validate(data)
 def test_generic_runtime_bridge_cannot_be_claimed_from_symbols(self):
  data=copy.deepcopy(self.base);data["integration_gate"]["generic_hud_action_to_model_function_call_contract_proven"]=True
  with self.assertRaisesRegex(AuditError,"runtime integration gates"):validate(data)
if __name__=="__main__":unittest.main(verbosity=2)

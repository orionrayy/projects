#!/usr/bin/env python3
"""Fail-closed synthetic tests for the v61 native client-function API audit."""
from __future__ import annotations
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_native_client_function_registration_v61 import AuditError,validate
REPORT=ROOT/"docs"/"NATIVE_CLIENT_FUNCTION_REGISTRATION_V61.json"
class NativeClientFunctionRegistrationV61Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_canonical_registration_api_finding_passes_fail_closed(self):
  r=validate(copy.deepcopy(self.base));self.assertTrue(r["client_registration_api_seen"]);self.assertFalse(r["AIFunction_ABI_recovered"]);self.assertEqual(r["catalog_routes"],0)
 def test_callback_abi_cannot_be_marked_recovered_from_pointer_signature(self):
  d=copy.deepcopy(self.base);d["native_entrypoints"][0]["callback_struct_layout_known"]=True
  with self.assertRaisesRegex(AuditError,"AIFunction layout"):validate(d)
 def test_hud_action_call_cannot_be_promoted_to_runtime_test(self):
  d=copy.deepcopy(self.base);e=next(x for x in d["native_entrypoints"] if x["symbol"]=="S3DClient_CallHUDAction");e["runtime_tested"]=True
  with self.assertRaisesRegex(AuditError,"static inspection"):validate(d)
 def test_new_hud_to_client_function_route_remains_unproven(self):
  d=copy.deepcopy(self.base);d["integration_gate"]["new_HUD_action_to_registered_function_call_contract_proven"]=True
  with self.assertRaisesRegex(AuditError,"new_HUD_action_to_registered_function_call_contract_proven"):validate(d)
 def test_gameplay_effect_count_cannot_increase_without_evidence(self):
  d=copy.deepcopy(self.base);d["integration_gate"]["runtime_verified_catalog_effects"]=1
  with self.assertRaisesRegex(AuditError,"catalog routing/effects"):validate(d)
 def test_kernel_symbol_or_size_drift_fails(self):
  d=copy.deepcopy(self.base);d["internal_registration_path"]["register_kernel_method"]["va"]="0xdeadbeef"
  with self.assertRaisesRegex(AuditError,"internal registration symbol drift"):validate(d)
if __name__=="__main__":unittest.main(verbosity=2)

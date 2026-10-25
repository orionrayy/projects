#!/usr/bin/env python3
"""Fail-closed tests for native registration/dispatch evidence in v62."""
from __future__ import annotations
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_native_client_function_call_dispatch_v62 import AuditError,validate
REPORT=ROOT/"docs"/"NATIVE_CLIENT_FUNCTION_CALL_DISPATCH_V62.json"

class NativeClientFunctionCallDispatchV62Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_canonical_static_chain_passes_without_runtime_promotion(self):
  result=validate(copy.deepcopy(self.base))
  self.assertEqual(result["max_callback_inputs"],32)
  self.assertFalse(result["HUD_callsite_proven"])
  self.assertEqual(result["catalog_routes"],0)
 def test_callback_pointer_offset_must_match_disassembly(self):
  data=copy.deepcopy(self.base);data["script_dispatch_entrypoint"]["callback_pointer_offset_in_registered_function"]=16
  with self.assertRaisesRegex(AuditError,"callback pointer offset drift"):validate(data)
 def test_function_name_lookup_and_input_cap_are_required(self):
  data=copy.deepcopy(self.base);data["script_dispatch_entrypoint"]["function_name_is_first_argument"]=False
  with self.assertRaisesRegex(AuditError,"function-name lookup"):validate(data)
  data=copy.deepcopy(self.base);data["script_dispatch_entrypoint"]["max_callback_input_count_in_this_path"]=64
  with self.assertRaisesRegex(AuditError,"callback argument cap drift"):validate(data)
 def test_legacy_gist_cannot_be_claimed_as_exact_target_header(self):
  data=copy.deepcopy(self.base);data["callback_abi_corroboration"]["exact_target_struct_size_and_all_field_offsets_verified"]=True
  with self.assertRaisesRegex(AuditError,"target SDK ABI cannot be presented as recovered"):validate(data)
 def test_hud_action_queue_is_not_same_as_client_function_dispatch(self):
  data=copy.deepcopy(self.base);data["hud_action_separation"]["directly_invokes_registered_client_function"]=True
  with self.assertRaisesRegex(AuditError,"HUD queue"):validate(data)
 def test_app_bootstrap_and_gameplay_effects_remain_blocked(self):
  data=copy.deepcopy(self.base);data["application_bootstrap"]["valid_initialization_hook_for_new_registration_proven"]=True
  with self.assertRaisesRegex(AuditError,"bootstrap gate"):validate(data)
  data=copy.deepcopy(self.base);data["gameplay_bridge"]["runtime_verified_catalog_effects"]=1
  with self.assertRaisesRegex(AuditError,"catalog routes/effects"):validate(data)
 def test_input_count_cap_is_explicitly_derived(self):
  data=copy.deepcopy(self.base);data["script_dispatch_entrypoint"]["max_callback_input_count_in_this_path"]=33
  with self.assertRaisesRegex(AuditError,"callback argument cap drift"):validate(data)

if __name__=="__main__":unittest.main(verbosity=2)

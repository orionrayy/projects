#!/usr/bin/env python3
"""Fail-closed synthetic tests for the v63 ShiVa ABI/bootstrap cross-check."""
from __future__ import annotations
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_shiva_aifunction_abi_bootstrap_v63 import AuditError,validate
REPORT=ROOT/"docs"/"SHIVA_AIFUNCTION_ABI_BOOTSTRAP_V63.json"
class ShivaAIFunctionBootstrapV63Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_canonical_crosscheck_passes_but_target_hook_remains_unproven(self):
  r=validate(copy.deepcopy(self.base));self.assertEqual(r["legacy_callback_offset"],8);self.assertFalse(r["target_hook_proven"]);self.assertEqual(r["catalog_routes"],0)
 def test_callback_field_offset_must_match_binary(self):
  d=copy.deepcopy(self.base);next(x for x in d["legacy_header"]["fields"] if x["name"]=="pCallback")["arm64_offset"]=16
  with self.assertRaisesRegex(AuditError,"field map changed"):validate(d)
 def test_historical_sdk_cannot_be_claimed_as_target_header(self):
  d=copy.deepcopy(self.base);d["legacy_header"]["target_exact_header_and_full_struct_layout_verified"]=True
  with self.assertRaisesRegex(AuditError,"exact target header"):validate(d)
 def test_registration_order_requires_loadpack_before_registration(self):
  d=copy.deepcopy(self.base);d["legacy_registration_lifecycle"]["observed_sequence"].reverse()
  with self.assertRaisesRegex(AuditError,"registration sequence drift"):validate(d)
 def test_target_registration_hook_cannot_be_promoted_from_legacy_project(self):
  d=copy.deepcopy(self.base);d["target_binary_crosscheck"]["registration_hook_in_dungeon_quest_application_source_proven"]=True
  with self.assertRaisesRegex(AuditError,"target source hook"):validate(d)
 def test_catalog_routes_cannot_increase_without_runtime_evidence(self):
  d=copy.deepcopy(self.base);d["integration_gate"]["catalog_routes_assigned"]=1
  with self.assertRaisesRegex(AuditError,"catalog route/effect counts"):validate(d)
 def test_external_reference_commit_must_be_pinned(self):
  d=copy.deepcopy(self.base);d["reference"]["commit"]="master"
  with self.assertRaisesRegex(AuditError,"reference commit must be pinned"):validate(d)
if __name__=="__main__":unittest.main(verbosity=2)

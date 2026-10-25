#!/usr/bin/env python3
"""Fail-closed tests for the v65 DEX lifecycle hook audit."""
from __future__ import annotations
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_dex_engine_lifecycle_hook_audit_v65 import AuditError,validate
REPORT=ROOT/"docs"/"DEX_ENGINE_LIFECYCLE_HOOK_AUDIT_V65.json"
class DexLifecycleHookAuditV65Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_canonical_lifecycle_report_passes_and_stays_unpatched(self):
  result=validate(copy.deepcopy(self.base));self.assertFalse(result["engine_initialize_result_consumed"]);self.assertFalse(result["DEX_patch_applied"])
 def test_engine_initialize_success_must_not_be_claimed(self):
  data=copy.deepcopy(self.base);data["renderer_init"]["critical_observation"]="move-result consumes engineInitialize result"
  with self.assertRaisesRegex(AuditError,"ignored init return"):validate(data)
 def test_shutdown_unregistration_cannot_be_claimed(self):
  data=copy.deepcopy(self.base);data["shutdown_path"]["native_probe_unregistration_present"]=True
  with self.assertRaisesRegex(AuditError,"unregistration cannot"):validate(data)
 def test_catalog_routes_must_remain_zero(self):
  data=copy.deepcopy(self.base);data["status"]["native_routes_assigned"]=1
  with self.assertRaisesRegex(AuditError,"route/effect counts"):validate(data)
 def test_apk_build_is_not_claimed(self):
  data=copy.deepcopy(self.base);data["status"]["game_apk_built"]=True
  with self.assertRaisesRegex(AuditError,"no game APK"):validate(data)
 def test_dex_identity_is_pinned(self):
  data=copy.deepcopy(self.base);data["target"]["classes_dex_sha256"]="bad"
  with self.assertRaisesRegex(AuditError,"invalid classes_dex_sha256"):validate(data)
if __name__=="__main__":unittest.main(verbosity=2)

from __future__ import annotations
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_provider_authority_fix_v74 import AuditError,validate
REPORT=ROOT/"docs"/"PROVIDER_AUTHORITY_FIX_V74.json"
class V74Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_pinned_report_and_runtime_block(self):
  r=validate(copy.deepcopy(self.base)); self.assertEqual(r["status"],"PASS_STATIC_V74_PROVIDER_AUTHORITY_REPORT"); self.assertFalse(r["device_install_verified"]); self.assertFalse(r["promotion_allowed"])
 def test_hash_and_package_id(self):
  d=copy.deepcopy(self.base); d["artifact"]["sha256"]="0"*64
  with self.assertRaisesRegex(AuditError,"APK hash"): validate(d)
  d=copy.deepcopy(self.base); d["artifact"]["package_id"]="com.shinybox.smash"
  with self.assertRaisesRegex(AuditError,"package ID"): validate(d)
 def test_authority_names_must_be_unique(self):
  d=copy.deepcopy(self.base); d["manifest_fix"]["old_official_authorities_remaining"]=True
  with self.assertRaisesRegex(AuditError,"old provider"): validate(d)
  d=copy.deepcopy(self.base); d["manifest_fix"]["renamed_authorities"]["com.shinybox.smash.androidx-startup"]="com.shinybox.smash.androidx-startup"
  with self.assertRaisesRegex(AuditError,"mapping mismatch"): validate(d)
 def test_static_gates_fail_closed(self):
  for k in ("zip_crc","zipalign_16k_pre_sign","zipalign_16k_post_sign","apksigner_v1","apksigner_v2","apksigner_v3","aapt_package_and_label","aapt_provider_authorities","stock_dex_hash","stk_hash","probe_bridge_absent"):
   d=copy.deepcopy(self.base);d["static_validation"][k]="FAIL"
   with self.subTest(k=k),self.assertRaisesRegex(AuditError,"static_validation"):validate(d)
 def test_payload_hashes_pinned(self):
  d=copy.deepcopy(self.base);d["inputs"]["stock_dex_sha256"]="0"*64
  with self.assertRaisesRegex(AuditError,"stock DEX"):validate(d)
  d=copy.deepcopy(self.base);d["inputs"]["stk_sha256"]="0"*64
  with self.assertRaisesRegex(AuditError,"STK hash"):validate(d)
 def test_no_runtime_or_promotion_claim(self):
  for k in ("device_install_tested","device_launch_tested","provider_conflict_on_device_confirmed"):
   d=copy.deepcopy(self.base);d["runtime"][k]=True
   with self.subTest(k=k),self.assertRaisesRegex(AuditError,"fabricate runtime"):validate(d)
  d=copy.deepcopy(self.base);d["promotion_allowed"]=True
  with self.assertRaisesRegex(AuditError,"cannot promote"):validate(d)
 def test_signer_and_key_boundary(self):
  d=copy.deepcopy(self.base);d["signing"]["matches_official_signer"]=True
  with self.assertRaisesRegex(AuditError,"official signer"):validate(d)
  d=copy.deepcopy(self.base);d["signing"]["private_key_shared"]=True
  with self.assertRaisesRegex(AuditError,"private test key"):validate(d)
 def test_unknown_root_cause_remains_explicit(self):
  d=copy.deepcopy(self.base);d["limitations"]=["fix certain"]
  with self.assertRaisesRegex(AuditError,"cause uncertainty"):validate(d)
if __name__=="__main__": unittest.main(verbosity=2)

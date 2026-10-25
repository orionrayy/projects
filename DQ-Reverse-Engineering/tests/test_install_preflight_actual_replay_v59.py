#!/usr/bin/env python3
"""Synthetic guards for the actual-file v50 package identity replay."""
from __future__ import annotations
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from validate_install_preflight_actual_replay_v59 import ReplayError,validate
REPORT=ROOT/"docs"/"INSTALL_PREFLIGHT_ACTUAL_REPLAY_V59.json"
class InstallPreflightActualReplayV59Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
 def test_canonical_replay_proves_signer_mismatch_but_not_runtime(self):
  r=validate(copy.deepcopy(self.base));self.assertEqual(r["candidate_xapk_splits"],20);self.assertFalse(r["signers_match_stock"]);self.assertFalse(r["device_install_verified"])
 def test_stock_hash_drift_fails_closed(self):
  d=copy.deepcopy(self.base);d["stock"]["sha256"]="0"*64
  with self.assertRaisesRegex(ReplayError,"stock XAPK hash drift"):validate(d)
 def test_candidate_signer_equal_to_stock_is_rejected_as_bad_report(self):
  d=copy.deepcopy(self.base);d["candidate_xapk"]["signer_fingerprint_sha256"]=d["stock"]["signer_fingerprint_sha256"]
  with self.assertRaisesRegex(ReplayError,"test XAPK signer fingerprint drift"):validate(d)
 def test_clean_install_uncertainty_must_be_explicit(self):
  d=copy.deepcopy(self.base);d["conclusion"]=d["conclusion"].replace("not proof that a clean install fails","proves all installs fail")
  with self.assertRaisesRegex(ReplayError,"clean-install uncertainty"):validate(d)
 def test_device_and_gameplay_must_not_be_promoted(self):
  d=copy.deepcopy(self.base);d["not_verified"].remove("Android PackageManager installation result on a device")
  with self.assertRaisesRegex(ReplayError,"must not claim device PackageManager"):validate(d)
if __name__=="__main__":unittest.main(verbosity=2)

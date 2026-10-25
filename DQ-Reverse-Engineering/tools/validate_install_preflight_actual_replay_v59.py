#!/usr/bin/env python3
"""Fail-closed validator for the recorded v50 stock/candidate package identity replay."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from typing import Any
SCHEMA="dq-install-preflight-actual-replay-v59"
SHA256=re.compile(r"^[0-9a-f]{64}$")
OFFICIAL="9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D"
TEST="BF:94:D4:AC:89:C5:1D:D6:32:43:8F:E2:C9:A3:0D:41:59:FE:FF:42:14:66:7B:AB:1C:EF:E3:38:1F:3F:22:90"
STOCK_HASH="3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b"
XAPK_HASH="680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430"
APK_HASH="f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa"
EXPECTED="IN_PLACE_UPDATE_REJECTED_SIGNATURE_MISMATCH_EXPECTED"
class ReplayError(ValueError): pass
def validate(data:dict[str,Any])->dict[str,Any]:
 def need(ok:bool,msg:str)->None:
  if not ok: raise ReplayError(msg)
 need(data.get("schema")==SCHEMA,f"schema must be {SCHEMA}")
 stock,xapk,apk=data.get("stock",{}),data.get("candidate_xapk",{}),data.get("candidate_arm64_apk",{})
 need(stock.get("sha256")==STOCK_HASH,"stock XAPK hash drift")
 need(xapk.get("sha256")==XAPK_HASH,"candidate XAPK hash drift")
 need(apk.get("sha256")==APK_HASH,"candidate ARM64 APK hash drift")
 for label,obj in (("stock",stock),("candidate_xapk",xapk),("candidate_arm64_apk",apk)):
  signer=obj.get("signer_fingerprint_sha256")
  need(isinstance(signer,str) and bool(SHA256.fullmatch(signer.replace(":","").lower())),f"{label} signer fingerprint invalid")
  need(obj.get("package_id")=="com.shinybox.smash",f"{label} package ID mismatch")
  need(obj.get("version_name")=="3.3.2.0",f"{label} version mismatch")
  need(obj.get("outer_zip_crc")=="PASS",f"{label} archive CRC not PASS")
  need(obj.get("all_splits_same_package") is True,f"{label} split package identities inconsistent")
  need(obj.get("all_splits_same_signer") is True,f"{label} split signer identities inconsistent")
 need(stock.get("signer_fingerprint_sha256")==OFFICIAL,"official stock signer fingerprint drift")
 need(xapk.get("signer_fingerprint_sha256")==TEST,"test XAPK signer fingerprint drift")
 need(apk.get("signer_fingerprint_sha256")==TEST,"test APK signer fingerprint drift")
 need(stock.get("signer_fingerprint_sha256")!=xapk.get("signer_fingerprint_sha256"),"candidate XAPK signer unexpectedly matches stock")
 need(stock.get("signer_fingerprint_sha256")!=apk.get("signer_fingerprint_sha256"),"candidate APK signer unexpectedly matches stock")
 need(xapk.get("expected_update_assessment")==EXPECTED,"candidate XAPK assessment drift")
 need(apk.get("expected_update_assessment")==EXPECTED,"candidate APK assessment drift")
 need(data.get("assessment")==EXPECTED,"overall update assessment drift")
 need("not proof that a clean install fails" in data.get("conclusion",""),"conclusion must keep clean-install uncertainty explicit")
 nv=data.get("not_verified",[])
 need(isinstance(nv,list) and "Android PackageManager installation result on a device" in nv,"report must not claim device PackageManager verification")
 need("game startup or HUD rendering" in nv and "Gold button touch dispatch or balance mutation" in nv,"report must retain runtime limitations")
 return {"stock_splits":stock.get("split_count"),"candidate_xapk_splits":xapk.get("split_count"),"candidate_apk_splits":apk.get("split_count"),"package_ids_match":True,"signers_match_stock":False,"assessment":EXPECTED,"device_install_verified":False}
def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("report",type=Path);a=p.parse_args()
 try: out=validate(json.loads(a.report.read_text(encoding="utf-8")))
 except (OSError,json.JSONDecodeError,ReplayError) as e:
  print(json.dumps({"status":"FAIL","error":str(e)},indent=2));return 2
 print("PASS: actual package identity replay report is internally consistent");print(json.dumps(out,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())

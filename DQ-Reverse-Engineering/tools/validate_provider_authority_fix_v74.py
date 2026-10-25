#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any
SCHEMA="dq-provider-authority-fix-v74"
APK_SHA256="6185a5f85eaf80ec3cc290cc10e2f0539a5e4ef9eb43ea51b1bae7b4feceda8e"
PACKAGE="com.shinybox.dqv74"
LABEL="DQ v74 Tester"
STOCK_DEX_SHA="bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
STK_SHA="e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e"
EXPECTED_AUTHORITIES={
 "com.shinybox.smash.mobileadsinitprovider":"com.shinybox.dqv74.mobileadsinitprovider",
 "com.shinybox.smash.androidx-startup":"com.shinybox.dqv74.androidx-startup",
}
class AuditError(ValueError): pass
def need(ok:bool,msg:str,errors:list[str])->None:
 if not ok: errors.append(msg)
def validate(doc:dict[str,Any])->dict[str,Any]:
 e=[]
 need(doc.get("schema")==SCHEMA,"schema mismatch",e)
 need(doc.get("status")=="STATIC_VALIDATION_PASS_DEVICE_INSTALL_NOT_TESTED","runtime status must remain unverified",e)
 a,i,m,sv,sig,rt=(doc.get(k) for k in ("artifact","inputs","manifest_fix","static_validation","signing","runtime"))
 for obj,k in zip((a,i,m,sv,sig,rt),("artifact","inputs","manifest_fix","static_validation","signing","runtime")): need(isinstance(obj,dict),f"{k} missing",e)
 if e: raise AuditError("; ".join(e))
 need(a.get("file_name")=="DQ_ModKit_v74_PROVIDER_AUTHORITY_FIX_ARM64.apk","filename mismatch",e)
 need(a.get("size_bytes")==57078652,"APK size mismatch",e)
 need(a.get("sha256")==APK_SHA256,"APK hash mismatch",e)
 need(a.get("package_id")==PACKAGE,"package ID mismatch",e)
 need(a.get("launcher_label")==LABEL,"launcher label mismatch",e)
 need(a.get("version_name")=="3.3.2.0" and a.get("abi")=="arm64-v8a" and a.get("split_count")==1,"version/ABI/package count mismatch",e)
 need(i.get("v73_apk_sha256")=="53799adf3e9d8b3efca062c9a8c97489a050196ad4f9aafcc84acf86d2ad0e49","v73 input hash mismatch",e)
 need(i.get("stock_dex_sha256")==STOCK_DEX_SHA,"stock DEX hash mismatch",e)
 need(i.get("stk_sha256")==STK_SHA,"STK hash mismatch",e)
 need(m.get("renamed_package_id") is True,"package ID rewrite missing",e)
 need(m.get("renamed_authorities")==EXPECTED_AUTHORITIES,"authority rewrite mapping mismatch",e)
 need(m.get("old_official_authorities_remaining") is False,"old provider authorities must be absent",e)
 need(m.get("new_authorities_unique") is True,"new authorities must be unique",e)
 for k in ("zip_crc","zipalign_16k_pre_sign","zipalign_16k_post_sign","apksigner_v1","apksigner_v2","apksigner_v3","aapt_package_and_label","aapt_provider_authorities","stock_dex_hash","stk_hash","probe_bridge_absent"):
  need(sv.get(k)=="PASS",f"static_validation.{k} must PASS",e)
 need(sig.get("kind")=="local diagnostic test certificate","signer kind mismatch",e)
 cert=sig.get("certificate_sha256")
 need(isinstance(cert,str) and bool(re.fullmatch(r"[0-9a-f]{64}",cert)),"certificate digest malformed",e)
 need(sig.get("matches_official_signer") is False,"must not claim official signer",e)
 need(sig.get("private_key_in_repository") is False and sig.get("private_key_shared") is False,"private test key must remain private",e)
 for k in ("device_install_tested","device_launch_tested","provider_conflict_on_device_confirmed"): need(rt.get(k) is False,f"must not fabricate runtime evidence: {k}",e)
 need(rt.get("gold_runtime_checks")=="0/9","Gold runtime gate must remain blocked",e)
 need(rt.get("catalog_runtime_verified")=="0/222","catalogue runtime gate must remain blocked",e)
 need(rt.get("promotion_allowed") is False and doc.get("promotion_allowed") is False,"cannot promote without device evidence",e)
 limits=doc.get("limitations")
 need(isinstance(limits,list) and any("not yet confirmed" in x for x in limits if isinstance(x,str)),"cause uncertainty must be explicit",e)
 if e: raise AuditError("; ".join(e))
 return {"status":"PASS_STATIC_V74_PROVIDER_AUTHORITY_REPORT","apk_sha256":APK_SHA256,"package_id":PACKAGE,"old_authorities_removed":True,"device_install_verified":False,"gold_runtime_checks":"0/9","catalog_runtime_verified":"0/222","promotion_allowed":False}
def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("report",type=Path); args=p.parse_args()
 try:
  doc=json.loads(args.report.read_text(encoding="utf-8"))
  if not isinstance(doc,dict): raise ValueError("report root must be an object")
  result=validate(doc)
 except (OSError,json.JSONDecodeError,ValueError) as ex:
  print(json.dumps({"status":"INVALID","error":str(ex)},indent=2)); return 2
 print(json.dumps(result,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
from typing import Any
SCHEMA="dq-v75-stk-crc-key-fix-apk"
APK_SHA="02f175d07dcacd46f9f9f9d67809a081dd9b1926737247bcbe7ea5b8484f9346"
STK_SHA="24a89cf3f356a2b48474d9681dedd662cec8cd5ec9f01574b26bed02d0ee6182"
class AuditError(ValueError): pass
def need(ok:bool,msg:str,e:list[str])->None:
 if not ok:e.append(msg)
def validate(d:dict[str,Any])->dict[str,Any]:
 e=[]
 need(d.get("schema")==SCHEMA,"schema mismatch",e)
 need(d.get("status")=="STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_TESTED","runtime status must remain unverified",e)
 a=d.get("artifact");s=d.get("stk");m=d.get("manifest");v=d.get("static_validation");sig=d.get("signing");rt=d.get("runtime")
 for o,n in ((a,"artifact"),(s,"stk"),(m,"manifest"),(v,"static_validation"),(sig,"signing"),(rt,"runtime")):need(isinstance(o,dict),n+" missing",e)
 if e:raise AuditError("; ".join(e))
 need(a.get("file_name")=="DQ_ModKit_v75_STK_CRC_KEY_FIX_ARM64.apk","APK filename mismatch",e)
 need(a.get("size_bytes")==57062268 and a.get("sha256")==APK_SHA,"APK size/hash mismatch",e)
 need(a.get("package_id")=="com.shinybox.dqv75" and a.get("launcher_label")=="DQ v75 Tester","package identity mismatch",e)
 need(a.get("abi")=="arm64-v8a" and a.get("split_count")==1 and a.get("version_name")=="3.3.2.0","APK identity detail mismatch",e)
 need(s.get("sha256")==STK_SHA,"STK hash mismatch",e)
 need(s.get("header_key_hex")=="0x45150cdf" and s.get("metadata_crc32_hex")=="0x45150cdf" and s.get("header_key_equals_metadata_crc") is True,"header-key/metadata-CRC invariant not proven",e)
 need(s.get("entry_count")==5630 and s.get("verified_entry_crc_and_decoded_sizes")==5630,"STK verification count mismatch",e)
 need(s.get("only_changed_decoded_entry")=="Resources/HUD/pause.hud" and s.get("unchanged_decoded_entries_identical")==5629,"decoded asset delta mismatch",e)
 need(s.get("non_target_entry_offsets_preserved")==5629 and s.get("exact_alias_groups_preserved")==41 and s.get("all_non_target_exact_alias_topology_preserved") is True,"offset/alias preservation mismatch",e)
 need(s.get("previous_candidate_header_key_hex")=="0x4c4060e8" and s.get("previous_candidate_metadata_crc32_hex")=="0x87bfe0b7" and s.get("previous_candidate_invariant") is False,"previous broken invariant evidence missing",e)
 need(m.get("new_package_id")=="com.shinybox.dqv75" and m.get("old_authorities_absent") is True and m.get("new_authorities_present") is True,"manifest isolation mismatch",e)
 for k in ("zip_crc","zipalign_16k_pre_sign","zipalign_16k_post_sign","apksigner_v1","apksigner_v2","apksigner_v3","aapt_badging","aapt_provider_authorities","stock_dex","native_probe_absent","only_expected_members_differ"):
  need(v.get(k)=="PASS","static_validation."+k+" must PASS",e)
 need(sig.get("kind")=="local diagnostic test certificate" and sig.get("matches_official_signer") is False,"signer boundary mismatch",e)
 need(sig.get("private_key_shared") is False and sig.get("private_key_in_repository") is False,"private key boundary mismatch",e)
 for k in ("device_install_tested","device_launch_tested","force_close_fixed_on_device"):need(rt.get(k) is False,"runtime claim must remain false: "+k,e)
 need(rt.get("gold_runtime_checks")=="0/9" and rt.get("catalog_runtime_verified")=="0/222","runtime evidence count mismatch",e)
 need(rt.get("promotion_allowed") is False and d.get("promotion_allowed") is False,"cannot promote before device validation",e)
 if e:raise AuditError("; ".join(e))
 return {"status":"PASS_STATIC_V75_STK_CRC_KEY_FIX","apk_sha256":APK_SHA,"stk_sha256":STK_SHA,"header_key_matches_table_crc":True,"entries_verified":"5630/5630","only_decoded_asset_changed":"Resources/HUD/pause.hud","device_runtime_tested":False,"promotion_allowed":False}
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("report",type=Path);a=p.parse_args()
 try:
  d=json.loads(a.report.read_text(encoding="utf-8"))
  if not isinstance(d,dict):raise ValueError("report root must be object")
  r=validate(d)
 except (OSError,json.JSONDecodeError,ValueError) as exc:
  print(json.dumps({"status":"INVALID","error":str(exc)},indent=2));return 2
 print(json.dumps(r,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())

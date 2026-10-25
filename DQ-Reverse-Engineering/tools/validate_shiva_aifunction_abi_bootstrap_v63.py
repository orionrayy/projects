#!/usr/bin/env python3
"""Fail-closed consistency validator for the v63 legacy ShiVa ABI cross-check."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from typing import Any

SCHEMA="dq-shiva-aifunction-abi-bootstrap-crosscheck-v63"
SHA_RE=re.compile(r"^[0-9a-f]{40}$")
class AuditError(ValueError): pass

def validate(data:dict[str,Any])->dict[str,Any]:
 def need(ok:bool,msg:str)->None:
  if not ok: raise AuditError(msg)
 need(data.get("schema")==SCHEMA,"wrong schema")
 need(data.get("audit_status")=="LEGACY_HEADER_AND_REGISTRATION_ORDER_CORROBORATED_TARGET_SOURCE_HOOK_STILL_MISSING","audit boundary drift")
 target=data.get("target",{})
 h=target.get("native_library_sha256")
 need(isinstance(h,str) and re.fullmatch(r"[0-9a-f]{64}",h) is not None,"bad target native library hash")
 ref=data.get("reference",{})
 need(ref.get("repository")=="error454/ShiVa-Android-All-In-One","unexpected public reference")
 need(isinstance(ref.get("commit"),str) and SHA_RE.fullmatch(ref["commit"]) is not None,"reference commit must be pinned")
 need(ref.get("reference_is_historical_not_target_source") is True,"historical-source boundary is mandatory")
 legacy=data.get("legacy_header",{})
 need(legacy.get("callback_signature_corroborated_by_target_disassembly") is True,"callback signature cross-check missing")
 need(legacy.get("callback_field_offset_matches_target_disassembly") is True,"callback offset cross-check missing")
 need(legacy.get("target_exact_header_and_full_struct_layout_verified") is False,"exact target header must remain unverified")
 fields=legacy.get("fields",[])
 offsets={x.get("name"):x.get("arm64_offset") for x in fields if isinstance(x,dict)}
 need(offsets.get("pName")==0 and offsets.get("pCallback")==8 and offsets.get("pReturns")==16 and offsets.get("pArguments")==24 and offsets.get("pDescription")==32 and offsets.get("iReserved")==40,"legacy AIFunction field map changed")
 need(legacy.get("expected_arm64_size_bytes_by_legacy_header")==48,"legacy expected ARM64 size drift")
 life=data.get("legacy_registration_lifecycle",{})
 need(life.get("observed_sequence",[])==[
  "S3DClient_Init",
  "configure client/input/render properties and callbacks",
  "S3DClient_LoadPack",
  "iterate static AIFunction table",
  "S3DClient_RegisterFunction(function.pName, &function)"
 ],"reference registration sequence drift")
 need(life.get("registration_loop_after_pack_load_in_reference") is True and life.get("applies_directly_to_dungeon_quest_binary") is False,"reference lifecycle must not be promoted into target source")
 target_binary=data.get("target_binary_crosscheck",{})
 need(target_binary.get("register_symbol",{}).get("va")=="0x7aec14","target register symbol drift")
 need(target_binary.get("dispatch_symbol",{}).get("va")=="0x892bd8","target dispatch symbol drift")
 need(target_binary.get("callback_pointer_offset_used_by_target")==8,"target callback pointer offset drift")
 need(target_binary.get("registration_hook_in_dungeon_quest_application_source_proven") is False,"target source hook must remain unknown")
 gate=data.get("integration_gate",{})
 need(gate.get("catalog_items")==222 and gate.get("catalog_categories")==14,"catalog baseline changed")
 need(gate.get("catalog_routes_assigned")==0 and gate.get("runtime_verified_catalog_effects")==0,"catalog route/effect counts cannot be promoted")
 need(gate.get("target_source_or_authorized_native_client_project_available") is False and gate.get("safe_registration_hook_proven") is False,"missing source/hook cannot be promoted")
 need(gate.get("status")=="BLOCKED","status must remain blocked")
 return {"legacy_callback_offset":offsets["pCallback"],"legacy_expected_aifunction_size":48,"target_callback_offset":target_binary["callback_pointer_offset_used_by_target"],"registration_after_pack_load_in_reference":True,"target_hook_proven":False,"catalog_routes":gate["catalog_routes_assigned"],"runtime_verified_effects":gate["runtime_verified_catalog_effects"],"status":gate["status"]}

def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("report",type=Path);args=p.parse_args()
 try:
  data=json.loads(args.report.read_text(encoding="utf-8"));result=validate(data)
 except (OSError,json.JSONDecodeError,AuditError) as exc:
  print(json.dumps({"status":"FAIL","error":str(exc)},indent=2));return 2
 print("PASS: legacy ABI/bootstrap cross-check consistency");print(json.dumps(result,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())

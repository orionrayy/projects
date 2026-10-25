#!/usr/bin/env python3
"""Fail-closed validator for the v65 DEX engine lifecycle-hook audit."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from typing import Any

SCHEMA="dq-android-engine-lifecycle-hook-audit-v65"
SHA_RE=re.compile(r"^[0-9a-f]{64}$")
class AuditError(ValueError): pass

def validate(data:dict[str,Any])->dict[str,Any]:
 def need(ok:bool,msg:str)->None:
  if not ok: raise AuditError(msg)
 need(data.get("schema")==SCHEMA,"wrong schema")
 need(data.get("audit_status")=="DEX_LIFECYCLE_HOOK_CANDIDATE_FOUND_INIT_RESULT_IGNORED_PATCH_NOT_IMPLEMENTED","audit must preserve the unpatched lifecycle boundary")
 target=data.get("target",{})
 for k in ("base_apk_sha256","classes_dex_sha256","source_xapk_sha256"):
  need(isinstance(target.get(k),str) and SHA_RE.fullmatch(target[k]) is not None,f"invalid {k}")
 init=data.get("renderer_init",{})
 need(init.get("method")=="void com.shinybox.smash.S3DRenderer.onDrawFrame(javax.microedition.khronos.opengles.GL10)","wrong init method")
 need(init.get("code_item_offset_decimal")==4487320 and init.get("code_item_offset_hex")=="0x447898" and init.get("instruction_code_units")==157,"renderer CodeItem identity drift")
 logic=init.get("logic",[])
 need(any(x.get("offset_code_unit")==9 and x.get("target")=="S3DRenderer.engineShutdown()" for x in logic),"initial shutdown call missing")
 need(any(x.get("offset_code_unit")==12 and x.get("target")=="S3DRenderer.engineInitialize()" for x in logic),"initialization call missing")
 need(any(x.get("offset_code_unit")==15 and x.get("field")=="S3DRenderer.bInitialized" for x in logic),"initialized flag write missing")
 need(any(x.get("offset_code_unit")==25 and x.get("target")=="S3DRenderer.engineRunOneFrame()" for x in logic),"frame loop call missing")
 need("not consumed" in init.get("critical_observation",""),"ignored init return warning missing")
 shutdown=data.get("shutdown_path",{})
 need(shutdown.get("shutdown_is_queued_through_glsurfaceview") is True,"GL-thread shutdown path missing")
 need(shutdown.get("native_probe_unregistration_present") is False,"unregistration cannot be claimed implemented")
 hook=data.get("integration_hook_plan",{})
 for k in ("initialization_success_gate_required","retry_after_failed_initialization_required","engine_restart_and_surface_recreation_tests_required"):
  need(hook.get(k) is True,f"hook safety requirement missing: {k}")
 for k in ("DEX_patch_applied","new_probe_class_in_game_dex","native_probe_library_in_game_package"):
  need(hook.get(k) is False,f"unimplemented integration item must remain false: {k}")
 status=data.get("status",{})
 need(status.get("catalog_items")==222 and status.get("catalog_categories")==14,"catalog baseline drift")
 need(status.get("native_routes_assigned")==0 and status.get("runtime_verified_catalog_effects")==0,"catalog route/effect counts cannot be promoted")
 need(status.get("v50_runtime_checks_passed")==0 and status.get("v50_runtime_checks_total")==9 and status.get("status")=="BLOCKED","runtime gate must remain blocked")
 need(status.get("game_apk_built") is False,"no game APK should be built in this increment")
 return {"dex_sha256":target["classes_dex_sha256"],"init_method":init["method"],"engine_initialize_code_unit":12,"engine_initialize_result_consumed":False,"shutdown_on_glsurfaceview_queue":True,"DEX_patch_applied":False,"catalog_routes":0,"runtime_effects":0,"status":"BLOCKED"}

def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("report",type=Path);args=p.parse_args()
 try:
  result=validate(json.loads(args.report.read_text(encoding="utf-8")))
 except (OSError,json.JSONDecodeError,AuditError) as exc:
  print(json.dumps({"status":"FAIL","error":str(exc)},indent=2));return 2
 print("PASS: DEX lifecycle audit consistency");print(json.dumps(result,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())

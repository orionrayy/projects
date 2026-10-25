#!/usr/bin/env python3
"""Fail-closed consistency gate for the v61 native client-function API audit."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from typing import Any

SCHEMA="dq-native-client-function-registration-v61"
SHA_RE=re.compile(r"^[0-9a-f]{64}$")
class AuditError(ValueError): pass

def validate(data:dict[str,Any])->dict[str,Any]:
 def need(ok:bool,msg:str)->None:
  if not ok: raise AuditError(msg)
 need(data.get("schema")==SCHEMA,"wrong schema")
 need(data.get("audit_status")=="CLIENT_FUNCTION_REGISTRATION_API_FOUND_CALLBACK_ABI_AND_GAME_INTEGRATION_UNPROVEN","audit must retain opaque-ABI/runtime boundary")
 target=data.get("target",{})
 for k in ("stock_xapk_sha256","stock_stk_sha256","native_library_sha256"):
  need(isinstance(target.get(k),str) and SHA_RE.fullmatch(target[k]) is not None,f"invalid {k}")
 entries=data.get("native_entrypoints")
 need(isinstance(entries,list) and len(entries)==3,"expected the three client entrypoints")
 by_name={x.get("symbol"):x for x in entries if isinstance(x,dict)}
 need(len(by_name)==len(entries),"duplicate/malformed entrypoint records")
 expected={"S3DClient_RegisterFunction":("0x7aec14",188),"S3DClient_UnregisterFunction":("0x7aecd0",132),"S3DClient_CallHUDAction":("0x7ae594",112)}
 for name,(va,size) in expected.items():
  item=by_name.get(name);need(item is not None,f"missing {name}")
  need(item.get("va")==va and item.get("size_bytes")==size,f"symbol identity drift for {name}")
 reg=by_name["S3DClient_RegisterFunction"]
 need(reg.get("callback_struct_layout_known") is False,"AIFunction layout may not be claimed recovered")
 need(reg.get("callback_calling_convention_verified") is False,"callback ABI may not be claimed verified")
 need(reg.get("lifecycle_thread_contract_known") is False,"lifecycle/thread contract may not be claimed known")
 call=by_name["S3DClient_CallHUDAction"]
 need(call.get("runtime_tested") is False,"static inspection must not be promoted to runtime test")
 internal=data.get("internal_registration_path",{})
 kernel=internal.get("register_kernel_method",{})
 need(kernel.get("symbol","").endswith("RegisterClientFunction(String const&, S3DX::AIFunction const*)"),"internal registration signature drift")
 need(kernel.get("va")=="0x82cccc" and kernel.get("size_bytes")==600,"internal registration symbol drift")
 gm=internal.get("client_call_method",{})
 need(gm.get("va")=="0xa5e5c0" and gm.get("size_bytes")==844,"GameManager call symbol drift")
 need(gm.get("queue_processing_and_model_callback_resolution_fully_recovered") is False,"queue/dispatch proof may not be promoted without evidence")
 boundary=data.get("function_handler_and_catalog_boundary",{})
 for key in ("gold_function_and_handler_proven_equivalent","custom_function_called_from_new_HUD_action_proven","new_HUD_action_can_supply_typed_AIVariable_to_client_function_proven","gameplay_state_readback_and_save_contract_proven"):
  need(boundary.get(key) is False,f"{key} must remain false absent proof")
 gate=data.get("integration_gate",{})
 need(gate.get("catalog_items")==222 and gate.get("catalog_categories")==14,"catalog baseline changed")
 need(gate.get("catalog_routes_assigned")==0 and gate.get("runtime_verified_catalog_effects")==0,"catalog routing/effects must remain zero")
 need(gate.get("separate_native_candidate_actions")==1 and gate.get("runtime_verified_candidate_actions")==0,"Gold candidate must remain unverified")
 for key in ("S3DX_AIFunction_ABI_recovered","function_lifecycle_thread_contract_recovered","new_HUD_action_to_registered_function_call_contract_proven"):
  need(gate.get(key) is False,f"{key} must remain false")
 need(gate.get("client_function_registration_API_seen") is True and gate.get("status")=="BLOCKED","current registration finding/status missing")
 ref=data.get("public_reference",{})
 need(ref.get("url","").startswith("https://") and "shi" in ref.get("summary","").lower(),"context link/summary missing")
 return {"entrypoints_audited":len(entries),"client_registration_api_seen":True,"AIFunction_ABI_recovered":False,"HUD_to_registered_function_route_proven":False,"catalog_routes":gate["catalog_routes_assigned"],"runtime_verified_effects":gate["runtime_verified_catalog_effects"],"status":gate["status"]}

def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("report",type=Path);args=p.parse_args()
 try:
  data=json.loads(args.report.read_text(encoding="utf-8"));out=validate(data)
 except (OSError,json.JSONDecodeError,AuditError) as exc:
  print(json.dumps({"status":"FAIL","error":str(exc)},indent=2));return 2
 print("PASS: native client-function API audit consistency");print(json.dumps(out,indent=2));return 0
if __name__=="__main__":raise SystemExit(main())

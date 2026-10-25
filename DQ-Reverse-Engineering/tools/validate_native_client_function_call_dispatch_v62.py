#!/usr/bin/env python3
"""Fail-closed validator for the v62 native client-function dispatch report."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

SCHEMA="dq-native-client-function-call-dispatch-v62"
SHA_RE=re.compile(r"^[0-9a-f]{64}$")
class AuditError(ValueError): pass

def validate(data:dict[str,Any])->dict[str,Any]:
    def need(ok:bool,msg:str)->None:
        if not ok: raise AuditError(msg)
    need(data.get("schema")==SCHEMA,"wrong schema")
    need(data.get("audit_status")=="REGISTER_LOOKUP_AND_TYPED_CALLBACK_DISPATCH_CONFIRMED_STATIC_BOOTSTRAP_AND_HUD_CALLSITE_UNPROVEN","must preserve the static-only bootstrap/callsite boundary")
    target=data.get("target",{})
    for k in ("stock_xapk_sha256","stock_stk_sha256","native_library_sha256"):
        need(isinstance(target.get(k),str) and SHA_RE.fullmatch(target[k]) is not None,f"invalid {k}")
    entry=data.get("registration_entrypoints",{})
    expected={
      "register":("S3DClient_RegisterFunction","0x7aec14",188),
      "unregister":("S3DClient_UnregisterFunction","0x7aecd0",132),
      "lookup":("Pandora::EngineCore::Kernel::GetClientFunction(Pandora::EngineCore::String const&) const","0x8285dc",76)
    }
    for key,(name,va,size) in expected.items():
        item=entry.get(key,{})
        need(item.get("symbol")==name and item.get("va")==va and item.get("size_bytes")==size,f"entrypoint identity drift: {key}")
        need(item.get("confirmed") is True,f"entrypoint not marked static-confirmed: {key}")
    dispatch=data.get("script_dispatch_entrypoint",{})
    need(dispatch.get("symbol")=="S3DX_AIScriptAPI_system_callClientFunction(int, S3DX::AIVariable const*, S3DX::AIVariable*)","wrong dispatch API")
    need(dispatch.get("va")=="0x892bd8" and dispatch.get("size_bytes")==1556,"dispatch address/size drift")
    need(dispatch.get("function_name_is_first_argument") is True,"function-name lookup contract missing")
    need(dispatch.get("callback_pointer_offset_in_registered_function")==8,"callback pointer offset drift")
    need(dispatch.get("max_callback_input_count_in_this_path")==32,"callback argument cap drift")
    need(dispatch.get("typed_aivariable_marshalling_static_only") is True and dispatch.get("callback_runtime_tested") is False,"runtime marshalling may not be promoted")
    observed=dispatch.get("observed_control_flow",[])
    for phrase in ("Kernel::GetClientFunction","callback field from offset +8","output_array"):
        need(any(phrase in line for line in observed),f"dispatch observation missing: {phrase}")
    corroboration=data.get("callback_abi_corroboration",{})
    need(corroboration.get("corroboration_only") is True,"historical SDK example must be corroboration only")
    need(corroboration.get("exact_target_sdk_header_available") is False and corroboration.get("exact_target_struct_size_and_all_field_offsets_verified") is False,"target SDK ABI cannot be presented as recovered")
    hud=data.get("hud_action_separation",{})
    need(hud.get("directly_invokes_registered_client_function") is False and hud.get("generic_HUD_action_to_new_client_function_route_proven") is False,"HUD queue must not be conflated with callback dispatch")
    boot=data.get("application_bootstrap",{})
    for key in ("valid_initialization_hook_for_new_registration_proven","registration_after_engine_initialization_proven","unregistration_before_unload_proven","thread_affinity_and_reentrancy_contract_proven","benign_no_side_effect_callback_tested"):
        need(boot.get(key) is False,f"bootstrap gate incorrectly promoted: {key}")
    gameplay=data.get("gameplay_bridge",{})
    need(gameplay.get("catalog_items")==222 and gameplay.get("catalog_categories")==14,"catalog baseline drift")
    need(gameplay.get("catalog_routes_assigned")==0 and gameplay.get("runtime_verified_catalog_effects")==0,"catalog routes/effects cannot be promoted")
    need(gameplay.get("runtime_verified_candidate_actions")==0 and gameplay.get("v50_runtime_checks_passed")==0 and gameplay.get("v50_runtime_checks_total")==9,"runtime checks cannot be promoted")
    need(gameplay.get("edited_HUD_or_AIM_callsite_for_new_registered_function_proven") is False and gameplay.get("status")=="BLOCKED","new call site/status boundary drift")
    return {"registration_entrypoints":3,"script_dispatch_va":dispatch["va"],"callback_pointer_offset":8,"max_callback_inputs":32,"exact_sdk_abi_recovered":False,"HUD_callsite_proven":False,"catalog_routes":gameplay["catalog_routes_assigned"],"runtime_effects":gameplay["runtime_verified_catalog_effects"],"status":gameplay["status"]}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("report",type=Path)
    args=p.parse_args()
    try:
        data=json.loads(args.report.read_text(encoding="utf-8"))
        result=validate(data)
    except (OSError,json.JSONDecodeError,AuditError) as exc:
        print(json.dumps({"status":"FAIL","error":str(exc)},indent=2))
        return 2
    print("PASS: native client-function dispatch audit consistency")
    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())

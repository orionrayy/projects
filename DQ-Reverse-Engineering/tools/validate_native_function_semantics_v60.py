#!/usr/bin/env python3
"""Fail-closed consistency validator for the v60 native function-semantics audit."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

SCHEMA = "dq-native-function-semantics-v60"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
class AuditError(ValueError): pass

def validate(data: dict[str, Any]) -> dict[str, Any]:
    def need(ok: bool, msg: str) -> None:
        if not ok: raise AuditError(msg)
    need(data.get("schema") == SCHEMA, "wrong schema")
    need(data.get("audit_status") == "STATIC_FUNCTION_CLASSIFICATION_ONLY_RUNTIME_BRIDGE_UNPROVEN", "runtime bridge boundary must remain unproven")
    target=data.get("target",{})
    for k in ("stock_xapk_sha256","stock_stk_sha256","native_library_sha256"):
        need(isinstance(target.get(k),str) and SHA_RE.fullmatch(target[k]) is not None, f"invalid {k}")
    mi=data.get("model_surface",{})
    need(mi.get("model")=="uai_gp_hud" and mi.get("aim_function_count")==133 and mi.get("aim_handler_count")==240, "unexpected AIM surface inventory")
    f=set(mi.get("confirmed_function_names",[])); h=set(mi.get("confirmed_handler_names",[]))
    need({"RewardGold","RewardDust","SpendGold"}.issubset(f), "effect candidates must remain classified as model functions")
    need({"onDebug","onSetGold","onSetHealth","onSetMana","onSetLevel","onStatIncrease"}.issubset(h), "handler candidates missing")
    need("onSetGold" not in f and "RewardGold" not in h, "function/handler roles must not be conflated")
    items=data.get("native_function_audit")
    need(isinstance(items,list) and len(items)>=7, "native function audit incomplete")
    by_name={x.get("name"):x for x in items if isinstance(x,dict)}
    need(len(by_name)==len(items), "duplicate or malformed native audit entry")
    gold=by_name.get("uai_gp_hud::RewardGold(S3DX::AIVariable)")
    need(gold is not None and gold.get("kind")=="model_function", "RewardGold function evidence missing")
    need(gold.get("catalog_id") is None and gold.get("runtime_verified") is False, "Gold increment cannot be promoted as a catalog or runtime feature without evidence")
    need(gold.get("direct_hud_action_call_contract_proven") is False, "direct HUD-to-function call must stay unproven")
    setgold=by_name.get("uai_gp_hud::onSetGold(int, S3DX::AIVariable const*, S3DX::AIVariable*)")
    need(setgold is not None and setgold.get("kind")=="model_handler", "onSetGold handler evidence missing")
    need(setgold.get("candidate_semantics")=="gold_display_or_label_update_not_proven_balance_setter", "onSetGold must not be classified as an authoritative balance setter")
    for name in (
      "uai_gp_hud::onSetHealth(int, S3DX::AIVariable const*, S3DX::AIVariable*)",
      "uai_gp_hud::onSetMana(int, S3DX::AIVariable const*, S3DX::AIVariable*)",
      "uai_gp_hud::onSetLevel(int, S3DX::AIVariable const*, S3DX::AIVariable*)",
      "uai_gp_hud::onStatIncrease(int, S3DX::AIVariable const*, S3DX::AIVariable*)",
    ):
      it=by_name.get(name)
      need(it is not None and it.get("catalog_id") is None and it.get("runtime_verified") is False, f"unsafe promotion of {name}")
    integ=data.get("integration_gate",{})
    need(integ.get("catalog_items")==222 and integ.get("catalog_categories")==14, "catalog baseline changed")
    need(integ.get("catalog_routes_assigned")==0 and integ.get("runtime_verified_catalog_effects")==0, "native catalog route/effect count must remain zero")
    need(integ.get("separate_native_candidate_actions")==1 and integ.get("runtime_verified_candidate_actions")==0, "single Gold candidate is not runtime verified")
    need(integ.get("generic_hud_action_to_model_function_call_contract_proven") is False and integ.get("gameplay_state_readback_contract_proven") is False, "runtime integration gates cannot be promoted from static symbols")
    need(integ.get("status")=="BLOCKED", "integration status must remain BLOCKED")
    return {"model_functions":mi["aim_function_count"],"model_handlers":mi["aim_handler_count"],"candidate_methods_audited":len(items),"catalog_routes":integ["catalog_routes_assigned"],"runtime_verified_effects":integ["runtime_verified_catalog_effects"],"status":integ["status"]}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("report",type=Path);a=p.parse_args()
    try:
      data=json.loads(a.report.read_text(encoding="utf-8"));result=validate(data)
    except (OSError,json.JSONDecodeError,AuditError) as e:
      print(json.dumps({"status":"FAIL","error":str(e)},indent=2));return 2
    print("PASS: native function-semantics audit consistency")
    print(json.dumps(result,indent=2));return 0
if __name__=="__main__": raise SystemExit(main())

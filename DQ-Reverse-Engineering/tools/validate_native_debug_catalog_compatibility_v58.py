#!/usr/bin/env python3
"""Fail-closed validator for static native-debug/catalog semantic compatibility."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
SCHEMA="dq-native-debug-catalog-compatibility-v58"
ALLOWED={"no_gameplay_catalog_mapping","no_exact_typed_contract","explicit_semantic_mismatch","unsafe_context_unresolved"}
class MatrixError(ValueError): pass
def validate(report:dict[str,Any],catalog:dict[str,Any])->dict[str,Any]:
 def need(ok:bool,msg:str)->None:
  if not ok: raise MatrixError(msg)
 need(report.get("schema")==SCHEMA,f"schema must be {SCHEMA}")
 cheats,categories=catalog.get("cheats"),catalog.get("categories")
 need(isinstance(cheats,list) and len(cheats)==222,"catalog must contain exactly 222 cheat entries")
 need(isinstance(categories,list) and len(categories)==14,"catalog must contain exactly 14 categories")
 ids=[c.get("id") for c in cheats if isinstance(c,dict)]
 need(len(ids)==222 and len(set(ids))==222,"catalog IDs must be complete and unique")
 idset=set(ids); base=report.get("catalog_baseline",{})
 need(base.get("catalog_items")==len(cheats) and base.get("categories")==len(categories),"report/catalog baseline mismatch")
 rows=report.get("commands")
 need(isinstance(rows,list) and len(rows)==16,"expected command-code audit for 1 through 16")
 codes:set[int]=set(); used:set[str]=set()
 for row in rows:
  code=row.get("command")
  need(isinstance(code,int) and not isinstance(code,bool) and 1<=code<=16,f"invalid debug command code: {code!r}")
  need(code not in codes,f"duplicate debug command code: {code}")
  codes.add(code)
  need(isinstance(row.get("hud_action"),str) and row["hud_action"],f"command {code} missing HUD action")
  need(row.get("mapping_status") in ALLOWED,f"command {code} has unsupported mapping status")
  need(row.get("mapping_status")!="exact_match",f"command {code} must not be promoted without a verified typed contract")
  candidates=row.get("candidate_catalog_ids")
  need(isinstance(candidates,list),f"command {code} candidate_catalog_ids must be a list")
  for cid in candidates:
   need(cid in idset,f"command {code} references unknown catalog ID: {cid!r}")
   used.add(cid)
 need(codes==set(range(1,17)),"debug command codes 1..16 must be present exactly once")
 bycode={x["command"]:x for x in rows}; gold=bycode[6]
 need(gold.get("mapping_status")=="explicit_semantic_mismatch","command 6 fixed Gold reward must remain marked as semantic mismatch")
 need("fixed" in gold.get("observed_semantics","").lower() and "100000" in gold.get("observed_semantics",""),"command 6 must preserve exact fixed +100000 Gold semantics")
 need({"economy.currency_override","economy.gold_multiplier","loot.gold_multiplier"}.issubset(set(gold["candidate_catalog_ids"])),"command 6 mismatch guard must mention balance setter and multiplier controls")
 need(bycode[7].get("mapping_status")=="unsafe_context_unresolved","command 7 SpendGold branch must remain blocked pending context recovery")
 summary=report.get("summary",{})
 need(summary.get("commands_reviewed")==16,"summary command count mismatch")
 need(summary.get("candidate_catalog_ids_reviewed")==len(used),"summary candidate ID count stale")
 need(summary.get("exact_catalog_routes_assigned")==0 and summary.get("catalog_routes_total")==0,"static resemblance must not create native catalog routes")
 need(summary.get("runtime_verified_catalog_effects")==0,"static audit cannot increase runtime-verified count")
 need(summary.get("separate_fixed_gold_candidate_runtime_verified") is False,"fixed Gold candidate must remain runtime-unverified")
 need(summary.get("status")=="BLOCKED","catalog native integration must remain BLOCKED")
 return {"catalog_items":len(cheats),"categories":len(categories),"commands_reviewed":len(rows),"candidate_catalog_ids_reviewed":len(used),"exact_catalog_routes_assigned":0,"runtime_verified_catalog_effects":0,"status":"BLOCKED"}
def main()->int:
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("report",type=Path); p.add_argument("--catalog",type=Path,default=Path("cheats-sandbox/debug_cheats_catalog_v32.json")); a=p.parse_args()
 try: summary=validate(json.loads(a.report.read_text(encoding="utf-8")),json.loads(a.catalog.read_text(encoding="utf-8")))
 except (OSError,json.JSONDecodeError,MatrixError) as e:
  print(json.dumps({"status":"FAIL","error":str(e)},indent=2)); return 2
 print("PASS: native debug/catalog compatibility matrix remains fail-closed"); print(json.dumps(summary,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed consistency validator for the read-only v57 native-row audit."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "dq-native-template-row-precedent-v57"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_MODELS = {
    "uai_gp_codex": {"variables": 16, "functions": 25, "states": 0, "handlers": 10},
    "uai_gp_legendex": {"variables": 4, "functions": 10, "states": 2, "handlers": 5},
    "uai_gp_hud": {"variables": 142, "functions": 133, "states": 4, "handlers": 240},
}

class AuditError(ValueError):
    pass

def validate_audit(data: dict[str, Any]) -> dict[str, int | str | bool]:
    def need(condition: bool, message: str) -> None:
        if not condition:
            raise AuditError(message)

    need(data.get("schema") == SCHEMA, f"schema must be {SCHEMA}")
    need(data.get("audit_status") == "STATIC_MODEL_SPECIFIC_PRECEDENTS_CONFIRMED_GENERIC_DISPATCH_UNPROVEN",
         "audit status must retain the model-specific / generic-dispatch-unproven boundary")
    target = data.get("target")
    need(isinstance(target, dict), "target must be an object")
    for key in ("stock_xapk_sha256", "stock_stk_sha256", "native_library_sha256"):
        value = target.get(key)
        need(isinstance(value, str) and bool(SHA256_RE.fullmatch(value)), f"invalid {key}")
    inventory = data.get("source_inventory", {})
    need(inventory.get("aim_files_parsed") == 162, "expected the pinned 162-file AIM framing inventory")
    need(inventory.get("aim_files_failed") == 0, "AIM framing failures must remain zero")
    models = data.get("model_precedents")
    need(isinstance(models, list), "model_precedents must be a list")
    by_name = {x.get("model"): x for x in models if isinstance(x, dict)}
    need(len(by_name) == len(models), "model precedent names must be unique")
    need(set(EXPECTED_MODELS).issubset(by_name), "required model precedents are missing")
    for model_name, expected_counts in EXPECTED_MODELS.items():
        model = by_name[model_name]
        need(model.get("aim_counts") == expected_counts, f"unexpected AIM counts for {model_name}")
        need(model.get("generic_cheat_dispatch_proven") is False,
             f"{model_name} must not be described as a proven generic cheat dispatcher")
        model_hash = inventory.get("model_sha256", {}).get(model_name + ".aim")
        need(isinstance(model_hash, str) and bool(SHA256_RE.fullmatch(model_hash)),
             f"missing pinned hash for {model_name}.aim")

    codex = by_name["uai_gp_codex"]
    legendex = by_name["uai_gp_legendex"]
    codex_functions = set(codex.get("key_function_names_observed", []))
    legendex_functions = set(legendex.get("key_function_names_observed", []))
    need("CreateLegendItem" in codex_functions, "Codex precedent must retain CreateLegendItem")
    need("UpdateList" not in codex_functions, "UpdateList belongs to LegendEx, not the Codex AIM function table")
    need({"CreateLegendItem", "UpdateList"}.issubset(legendex_functions),
         "LegendEx must retain the separate CreateLegendItem/UpdateList precedent")
    for model_name, model in (("uai_gp_codex", codex), ("uai_gp_legendex", legendex)):
        methods = model.get("native_methods")
        need(isinstance(methods, list) and methods, f"{model_name} native AOT evidence is required")
        for method in methods:
            need(isinstance(method.get("va"), str) and method["va"].startswith("0x"),
                 f"{model_name} method missing a native VA")
            need(isinstance(method.get("size_bytes"), int) and method["size_bytes"] > 0,
                 f"{model_name} method missing native size")

    wrappers = data.get("exported_native_list_wrappers")
    need(isinstance(wrappers, list) and len(wrappers) >= 6, "native List wrapper inventory is incomplete")
    wrapper_names = {x.get("symbol") for x in wrappers if isinstance(x, dict)}
    need({"hud_addListItem", "hud_setListOnSelectionChangedAction", "hud_getListSelectedItemAt"}.issubset(wrapper_names),
         "core List population/selection wrapper names are missing")
    gate = data.get("integration_gate", {})
    need(gate.get("catalog_items") == 222 and gate.get("catalog_categories") == 14,
         "catalog baseline must be 222 IDs across 14 categories")
    need(gate.get("catalog_routes_assigned") == 0, "unproven catalog routes may not be promoted")
    need(gate.get("runtime_verified_catalog_effects") == 0, "unverified runtime effects may not be promoted")
    need(gate.get("candidate_native_actions") == 1 and gate.get("runtime_verified_candidate_actions") == 0,
         "the single native candidate remains unverified")
    for key in ("generic_in_engine_row_population_proven", "stable_id_selection_dispatch_proven", "typed_allow_list_handler_contract_proven"):
        need(gate.get(key) is False, f"{key} must remain false absent runtime evidence")
    need(gate.get("status") == "BLOCKED", "integration status must remain BLOCKED")
    decision = gate.get("decision", "")
    need("Do not clone" in decision and "disabled" in decision,
         "decision must preserve fail-closed integration instructions")
    return {
        "aim_files_parsed": inventory["aim_files_parsed"],
        "model_precedents": len(models),
        "native_list_wrappers": len(wrappers),
        "catalog_items": gate["catalog_items"],
        "catalog_routes_assigned": gate["catalog_routes_assigned"],
        "runtime_verified_catalog_effects": gate["runtime_verified_catalog_effects"],
        "generic_dispatch_proven": False,
        "status": gate["status"],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="machine-readable v57 audit JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
        summary = validate_audit(data)
    except (OSError, json.JSONDecodeError, AuditError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 2
    print("PASS: read-only native row precedent audit consistency")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

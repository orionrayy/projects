#!/usr/bin/env python3
"""Fail-closed validator for the native cheat adapter registry and runtime evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

class RegistryError(ValueError):
    pass

RUNTIME_EVIDENCE_FIELDS = {
    "device_or_emulator", "game_build_sha256", "candidate_apk_sha256",
    "handler_route_observed", "before_state", "after_state",
    "exact_effect_confirmed", "save_reload_confirmed", "regression_passed",
    "evidence_artifact"
}

def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RegistryError(message)

def validate_data(catalog: dict[str, Any], registry: dict[str, Any]) -> dict[str, int]:
    cheats = catalog.get("cheats")
    categories = catalog.get("categories")
    _require(isinstance(cheats, list), "catalog.cheats must be a list")
    _require(isinstance(categories, list), "catalog.categories must be a list")
    _require(catalog.get("count") == 222 and len(cheats) == 222, "canonical catalog must contain exactly 222 entries")
    _require(len(categories) == 14, "canonical catalog must contain exactly 14 categories")
    ids = [item.get("id") for item in cheats]
    _require(all(isinstance(item_id, str) and item_id for item_id in ids), "every catalog entry needs a non-empty stable ID")
    _require(len(set(ids)) == len(ids), "catalog stable IDs must be unique")
    id_set = set(ids)

    _require(registry.get("schema_version") == 52, "unsupported registry schema_version")
    cat_meta = registry.get("catalog", {})
    _require(cat_meta.get("count") == len(cheats), "registry/catalog count mismatch")
    _require(cat_meta.get("category_count") == len(categories), "registry/catalog category count mismatch")
    _require(registry.get("policy", {}).get("route_policy") != "open", "open dispatch policies are forbidden")

    routes = registry.get("catalog_routes", [])
    _require(isinstance(routes, list), "catalog_routes must be a list")
    seen_route_ids: set[str] = set()
    for route in routes:
        cid = route.get("catalog_id")
        _require(cid in id_set, f"route references unknown catalog ID: {cid!r}")
        _require(cid not in seen_route_ids, f"duplicate catalog route: {cid}")
        seen_route_ids.add(cid)
        status = route.get("status")
        _require(status in {"candidate_unverified", "runtime_verified"}, f"unsupported route status for {cid}: {status!r}")
        _require(route.get("handler") and route.get("argument_contract"), f"route {cid} needs an explicit handler and typed argument contract")
        if status == "runtime_verified":
            evidence = route.get("runtime_evidence")
            _require(isinstance(evidence, dict), f"runtime-verified route {cid} lacks runtime_evidence")
            missing = sorted(RUNTIME_EVIDENCE_FIELDS - evidence.keys())
            _require(not missing, f"runtime-verified route {cid} missing evidence fields: {missing}")
            for flag in ("exact_effect_confirmed", "save_reload_confirmed", "regression_passed"):
                _require(evidence.get(flag) is True, f"runtime-verified route {cid} requires {flag}=true")
            for field in ("device_or_emulator", "game_build_sha256", "candidate_apk_sha256", "handler_route_observed", "evidence_artifact"):
                _require(isinstance(evidence.get(field), str) and evidence[field].strip(), f"runtime-verified route {cid} has empty {field}")

    candidates = registry.get("candidate_actions", [])
    _require(isinstance(candidates, list), "candidate_actions must be a list")
    candidate_ids: set[str] = set()
    for action in candidates:
        aid = action.get("id")
        _require(isinstance(aid, str) and aid, "every candidate action needs an ID")
        _require(aid not in candidate_ids, f"duplicate candidate action ID: {aid}")
        candidate_ids.add(aid)
        cid = action.get("catalog_id")
        if cid is not None:
            _require(cid in id_set, f"candidate action {aid} references unknown catalog ID: {cid}")
        status = action.get("status")
        _require(status in {"candidate_unverified", "runtime_verified"}, f"unsupported candidate-action status: {status!r}")
        _require(action.get("native_route", {}).get("model") and action.get("native_route", {}).get("handler"),
                 f"candidate action {aid} lacks a named native route")
        _require(isinstance(action.get("evidence"), list) and action["evidence"],
                 f"candidate action {aid} needs static evidence records")
        if status == "runtime_verified":
            evidence = action.get("runtime_evidence")
            _require(isinstance(evidence, dict), f"runtime-verified candidate {aid} lacks runtime_evidence")
            missing = sorted(RUNTIME_EVIDENCE_FIELDS - evidence.keys())
            _require(not missing, f"runtime-verified candidate {aid} missing evidence fields: {missing}")
            for flag in ("exact_effect_confirmed", "save_reload_confirmed", "regression_passed"):
                _require(evidence.get(flag) is True, f"runtime-verified candidate {aid} requires {flag}=true")

    summary = registry.get("current_summary", {})
    runtime_routes = sum(route["status"] == "runtime_verified" for route in routes)
    runtime_candidates = sum(action["status"] == "runtime_verified" for action in candidates)
    _require(summary.get("catalog_item_count") == len(cheats), "summary catalog_item_count is stale")
    _require(summary.get("catalog_routes") == len(routes), "summary catalog_routes is stale")
    _require(summary.get("runtime_verified_catalog_routes") == runtime_routes, "summary runtime_verified_catalog_routes is stale")
    _require(summary.get("candidate_actions") == len(candidates), "summary candidate_actions is stale")
    _require(summary.get("runtime_verified_candidate_actions") == runtime_candidates, "summary runtime_verified_candidate_actions is stale")

    # An unassigned candidate action is explicitly not a catalog route.
    # In particular, fixed RewardGold(100000) must not be masqueraded as a set-to-target slider.
    for action in candidates:
        if action.get("id") == "native.pause.gold_reward_100k":
            _require(action.get("catalog_id") is None, "fixed Gold reward cannot be mapped to the currency-override slider")
            _require(action.get("status") != "runtime_verified" or action.get("runtime_evidence") is not None,
                     "Gold candidate cannot be runtime-verified without device evidence")

    return {
        "catalog_items": len(cheats),
        "catalog_routes": len(routes),
        "runtime_verified_catalog_routes": runtime_routes,
        "candidate_actions": len(candidates),
        "runtime_verified_candidate_actions": runtime_candidates,
        "unmapped_catalog_items": len(cheats) - len(seen_route_ids),
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("cheats-sandbox/debug_cheats_catalog_v39.json"))
    parser.add_argument("--registry", type=Path, default=Path("docs/NATIVE_CHEAT_ADAPTER_REGISTRY_V52.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        result = validate_data(catalog, registry)
    except (OSError, json.JSONDecodeError, RegistryError) as exc:
        parser.error(str(exc))
    print("PASS: fail-closed native adapter registry")
    for key, value in result.items():
        print(f"{key}={value}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

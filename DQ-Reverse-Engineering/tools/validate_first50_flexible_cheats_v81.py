#!/usr/bin/env python3
"""Fail-closed validator for the deduplicated v81.1 first-50 roster."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

EXPECTED = 50
CONTROL_TYPES = {"toggle", "slider", "number", "select", "action"}
INTEGRATED_STATUSES = {"runtime_verified", "implemented"}


def validate(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    cheats = doc.get("cheats")
    if not isinstance(cheats, list) or len(cheats) != EXPECTED:
        raise ValueError(f"expected exactly {EXPECTED} cheats")
    for field, key in (("unique_ids", "id"), ("unique_labels", "label"), ("unique_effect_keys", "effect_key")):
        values = [item.get(key) for item in cheats]
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"missing/invalid {key}")
        if len(set(values)) != EXPECTED or doc.get(field) != EXPECTED:
            raise ValueError(f"duplicate {key} or incorrect summary")

    ids = {item["id"] for item in cheats}
    for i, item in enumerate(cheats):
        prefix = f"cheats[{i}] {item.get('id')!r}"
        control = item.get("control")
        if control not in CONTROL_TYPES:
            raise ValueError(f"{prefix}: unsupported control")
        if item.get("scope") != "offline_disposable_profile_only":
            raise ValueError(f"{prefix}: scope must stay offline/disposable")
        if item.get("runtime_verified") is not False:
            raise ValueError(f"{prefix}: catalog cannot promote runtime evidence")
        if item.get("adapter_status") in INTEGRATED_STATUSES:
            raise ValueError(f"{prefix}: integration needs a separate evidence review")
        if any(dep not in ids for dep in item.get("requires", [])):
            raise ValueError(f"{prefix}: dependency points to missing entry")
        if control in {"slider", "number"}:
            lo, hi, step, default = (item.get(k) for k in ("min", "max", "step", "default"))
            nums = (lo, hi, step, default)
            if not all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in nums):
                raise ValueError(f"{prefix}: numeric control requires numeric bounds/default")
            if lo > hi or step <= 0 or not lo <= default <= hi:
                raise ValueError(f"{prefix}: invalid numeric bounds/default")
        if control == "select" and (not isinstance(item.get("options"), list) or not item["options"] or item.get("default") not in item["options"]):
            raise ValueError(f"{prefix}: invalid select default")
        if control == "toggle" and not isinstance(item.get("default"), bool):
            raise ValueError(f"{prefix}: toggle default must be boolean")
        if control == "action" and item.get("default") is not None:
            raise ValueError(f"{prefix}: action default must be null")

    routes = sum(bool(item.get("native_route_candidate")) for item in cheats)
    verified = sum(item.get("runtime_verified") is True for item in cheats)
    integrated = sum(item.get("adapter_status") in INTEGRATED_STATUSES for item in cheats)
    if doc.get("runtime_verified") != verified or doc.get("fully_integrated") != integrated:
        raise ValueError("summary runtime/integration counts drift")
    if doc.get("existing_native_route_candidates") != routes:
        raise ValueError("summary route count drifts from entries")
    by_id = {item["id"]: item for item in cheats}
    if "player.no_cooldowns" in by_id or "progression.level_up_one" in by_id:
        raise ValueError("duplicate No Cooldowns / Level Up options reintroduced")
    if "player.auto_heal" not in by_id or by_id["player.auto_heal_threshold"].get("requires") != ["player.auto_heal"]:
        raise ValueError("Auto Heal threshold dependency missing")
    gold = by_id["economy.gold_reward_amount"]
    if gold.get("native_route_candidate") is not None or gold.get("nearby_route_mismatch") != "uai_gp_hud.onDebug(6.0)":
        raise ValueError("flexible Gold amount incorrectly mapped to fixed +100K")
    boss = by_id["enemy.boss_variant"]
    if boss.get("native_route_candidate") is not None or boss.get("nearby_route_mismatch") != "uai_gp_hud.onDebug(3.0)":
        raise ValueError("Boss variant selector incorrectly mapped to fixed route")
    return {"result":"PASS","count":50,"unique_ids":50,"unique_labels":50,"unique_effect_keys":50,
            "controls":doc["controls"],"native_route_candidates":routes,"runtime_verified":verified,
            "fully_integrated":integrated,"catalog_only":True}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog",type=Path,nargs="?",default=Path(__file__).parents[1]/"cheats-sandbox"/"first50_flexible_cheats_v81.json")
    args=parser.parse_args()
    try:
        print(json.dumps(validate(args.catalog),indent=2))
        return 0
    except (OSError,json.JSONDecodeError,ValueError,TypeError) as exc:
        parser.exit(2,f"FAIL: {exc}\\n")


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed validator for the curated v81 50-cheat roster.

This validates catalog metadata only. It is not evidence that a game-side
handler is implemented or that any cheat works at runtime.
"""
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
    if not isinstance(cheats, list):
        raise ValueError("cheats must be a list")
    if len(cheats) != EXPECTED:
        raise ValueError(f"expected exactly {EXPECTED} cheats, got {len(cheats)}")

    for field, key in (("unique_ids", "id"), ("unique_labels", "label"), ("unique_effect_keys", "effect_key")):
        values = [x.get(key) for x in cheats]
        if any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f"missing/invalid {key}")
        if len(set(values)) != EXPECTED:
            raise ValueError(f"duplicate {key}")
        if doc.get(field) != EXPECTED:
            raise ValueError(f"summary {field} must be {EXPECTED}")

    for i, item in enumerate(cheats):
        prefix = f"cheats[{i}] {item.get('id')!r}"
        if item.get("control") not in CONTROL_TYPES:
            raise ValueError(f"{prefix}: unsupported control")
        if item.get("scope") != "offline_disposable_profile_only":
            raise ValueError(f"{prefix}: scope must remain offline/disposable")
        if item.get("runtime_verified") is not False:
            raise ValueError(f"{prefix}: do not promote runtime evidence from catalog metadata")
        if item.get("adapter_status") in INTEGRATED_STATUSES:
            raise ValueError(f"{prefix}: promotion requires a separate reviewed runtime evidence record")
        c = item["control"]
        if c in {"slider", "number"}:
            lo, hi, step = item.get("min"), item.get("max"), item.get("step")
            if not all(isinstance(n, (int, float)) and not isinstance(n, bool) for n in (lo, hi, step)):
                raise ValueError(f"{prefix}: numeric control needs numeric min/max/step")
            if lo > hi or step <= 0:
                raise ValueError(f"{prefix}: invalid numeric range or step")
            default = item.get("default")
            if not isinstance(default, (int, float)) or isinstance(default, bool) or not lo <= default <= hi:
                raise ValueError(f"{prefix}: default outside bounds")
        if c == "select":
            opts = item.get("options")
            if not isinstance(opts, list) or not opts or item.get("default") not in opts:
                raise ValueError(f"{prefix}: select default must be in nonempty options")
        if c == "toggle" and not isinstance(item.get("default"), bool):
            raise ValueError(f"{prefix}: toggle default must be boolean")
        if c == "action" and item.get("default") is not None:
            raise ValueError(f"{prefix}: action default must be null")

    routes = sum(bool(x.get("native_route_candidate")) for x in cheats)
    verified = sum(x.get("runtime_verified") is True for x in cheats)
    integrated = sum(x.get("adapter_status") in INTEGRATED_STATUSES for x in cheats)
    if doc.get("runtime_verified") != verified or doc.get("fully_integrated") != integrated:
        raise ValueError("summary runtime/integration counts drift from entries")
    return {
        "result": "PASS",
        "count": len(cheats),
        "unique_ids": len({x["id"] for x in cheats}),
        "unique_labels": len({x["label"] for x in cheats}),
        "unique_effect_keys": len({x["effect_key"] for x in cheats}),
        "numeric_controls_valid": True,
        "select_defaults_valid": True,
        "native_route_candidates": routes,
        "runtime_verified": verified,
        "fully_integrated": integrated,
        "catalog_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path, nargs="?", default=Path(__file__).parents[1] / "cheats-sandbox" / "first50_flexible_cheats_v81.json")
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.catalog), indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        parser.exit(2, f"FAIL: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())

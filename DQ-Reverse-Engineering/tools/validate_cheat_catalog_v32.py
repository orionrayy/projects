#!/usr/bin/env python3
"""Fail-closed validation for the 222-entry Dungeon Quest cheat catalog audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter


def validate(catalog_path: Path, matrix_path: Path) -> list[str]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    cheats = catalog.get("cheats")
    if not isinstance(cheats, list):
        return ["catalog.cheats must be a list"]

    ids = [item.get("id") for item in cheats]
    if len(cheats) != 222 or catalog.get("count") != 222:
        errors.append(f"expected exactly 222 catalog entries, got {len(cheats)} / count={catalog.get('count')}")
    if any(not isinstance(value, str) or not value for value in ids):
        errors.append("each cheat must have a non-empty string id")
    if len(set(ids)) != len(ids):
        errors.append("catalog IDs must be unique")

    categories = catalog.get("categories", [])
    if len(categories) != 14 or set(categories) != {item.get("category") for item in cheats}:
        errors.append("category list must match the 14 categories represented by entries")

    if matrix.get("total_catalog_entries") != len(cheats):
        errors.append("matrix total_catalog_entries does not match catalog")
    matrix_entries = matrix.get("entries")
    if not isinstance(matrix_entries, list) or len(matrix_entries) != len(cheats):
        errors.append("matrix entries must have one row per catalog entry")
        matrix_entries = []

    matrix_ids = [item.get("id") for item in matrix_entries]
    if len(set(matrix_ids)) != len(matrix_ids) or set(matrix_ids) != set(ids):
        errors.append("matrix IDs must be unique and exactly match the catalog IDs")

    runtime_verified = [item.get("id") for item in matrix_entries if item.get("runtime_verified") is True]
    if runtime_verified:
        errors.append(f"runtime-verified claims require explicit device evidence; found {runtime_verified[:5]}")

    counts = Counter(item.get("implementation_status") for item in matrix_entries)
    if counts.get("PARTIAL_NATIVE_CANDIDATE_UNVERIFIED", 0) != 3:
        errors.append("expected exactly three partial native candidates, all unverified")
    if counts.get("REQUIRES_VERIFIED_GAME_ADAPTER", 0) != 219:
        errors.append("expected 219 entries requiring a verified game adapter")
    if counts.get("CONNECTED", 0) or counts.get("FULLY_IMPLEMENTED", 0):
        errors.append("catalog audit must not claim unverified runtime features are connected")
    if matrix.get("implementation_counts", {}).get("fully_integrated") != 0:
        errors.append("fully_integrated must remain 0 until direct game runtime proof exists")
    if matrix.get("implementation_counts", {}).get("runtime_verified") != 0:
        errors.append("runtime_verified must remain 0 until direct game runtime proof exists")

    source_statuses = Counter(item.get("integration_status") for item in cheats)
    if source_statuses.get("requires_game_adapter") != 222:
        errors.append("source design must preserve requires_game_adapter for all 222 items")

    candidate_ids = {item.get("id") for item in matrix_entries if item.get("implementation_status") == "PARTIAL_NATIVE_CANDIDATE_UNVERIFIED"}
    expected_candidates = {
        "progression.player_level",
        "inventory.grant_item",
        "economy.currency_override",
    }
    if candidate_ids != expected_candidates:
        errors.append(f"unexpected candidate mapping IDs: {sorted(candidate_ids)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    args = parser.parse_args()
    errors = validate(args.catalog, args.matrix)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: 222 unique catalog IDs, 14 categories, matched implementation matrix, zero runtime-verified claims, 3 unverified candidates, 219 adapter blockers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

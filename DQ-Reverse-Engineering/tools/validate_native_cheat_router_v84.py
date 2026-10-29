#!/usr/bin/env python3
"""Fail-closed consistency check for the v84 native 50-cheat route gate."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

ROW = re.compile(
    r'^\s*\{"(?P<id>[^"]+)",\s*ValueKind::(?P<kind>\w+),\s*'
    r'(?P<min>-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?),\s*'
    r'(?P<max>-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?),\s*'
    r'(?P<step>-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?),\s*'
    r'(?P<options>\d+),\s*(?P<candidate>true|false),\s*'
    r'(?P<enabled>true|false)\},\s*$'
)

KIND_BY_CONTROL = {
    "toggle": "Boolean",
    "select": "Select",
    "action": "None",
}


def fail(message: str) -> None:
    raise ValueError(message)


def number(value: Any) -> float:
    return 0.0 if value is None else float(value)


def read_native_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "ValueKind::" not in line or not line.lstrip().startswith('{"'):
            continue
        match = ROW.fullmatch(line)
        if not match:
            fail(f"{path}:{line_no}: malformed native registry row")
        row = match.groupdict()
        row["min"] = float(row["min"])
        row["max"] = float(row["max"])
        row["step"] = float(row["step"])
        row["options"] = int(row["options"])
        row["candidate"] = row["candidate"] == "true"
        row["enabled"] = row["enabled"] == "true"
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path, help="canonical first50_flexible_cheats_v81.json")
    parser.add_argument("native_source", type=Path, help="native_cheat_router_v84.cpp")
    args = parser.parse_args()

    try:
        registry = json.loads(args.registry.read_text(encoding="utf-8"))
        cheats = registry["cheats"]
        rows = read_native_rows(args.native_source)

        if len(cheats) != 50 or len(rows) != 50:
            fail(f"expected 50 registry items and 50 native rows; found {len(cheats)} and {len(rows)}")

        registry_ids = [item["id"] for item in cheats]
        native_ids = [row["id"] for row in rows]
        if len(set(registry_ids)) != 50:
            fail("canonical registry does not contain 50 unique IDs")
        if len(set(native_ids)) != 50:
            fail("native registry does not contain 50 unique IDs")
        if set(registry_ids) != set(native_ids):
            fail(f"ID set differs: missing={sorted(set(registry_ids)-set(native_ids))}; "
                 f"unexpected={sorted(set(native_ids)-set(registry_ids))}")

        by_id = {row["id"]: row for row in rows}
        for item in cheats:
            cheat_id = item["id"]
            row = by_id[cheat_id]
            expected_kind = KIND_BY_CONTROL.get(item["control"])
            if expected_kind is None:
                expected_kind = "Integer" if item["value_type"] == "integer" else "Number"
            if row["kind"] != expected_kind:
                fail(f"{cheat_id}: kind {row['kind']} != expected {expected_kind}")

            for field in ("min", "max", "step"):
                if not math.isclose(row[field], number(item.get(field)), rel_tol=0.0, abs_tol=1e-9):
                    fail(f"{cheat_id}: {field} {row[field]} != registry {item.get(field)}")

            expected_options = len(item["options"]) if item.get("options") else 0
            if row["options"] != expected_options:
                fail(f"{cheat_id}: option count {row['options']} != registry {expected_options}")

            expected_candidate = bool(item.get("native_route_candidate"))
            if row["candidate"] != expected_candidate:
                fail(f"{cheat_id}: static route candidate flag diverges from registry")
            if row["enabled"]:
                fail(f"{cheat_id}: runtime_enabled must remain false until runtime proof exists")

        candidate_count = sum(row["candidate"] for row in rows)
        if candidate_count != 11:
            fail(f"expected 11 static-only route candidates, found {candidate_count}")

        source = args.native_source.read_text(encoding="utf-8")
        for required in (
            "kRouteGateFunctionName",
            "if (!spec->runtime_enabled)",
            "return Status::HandlerUnavailable;",
            "return Status::BackendUnavailable;",
            "invoke_route_gate_self_test",
        ):
            if required not in source:
                fail(f"native fail-closed contract missing required marker: {required}")

        print("PASS: native route metadata matches all 50 canonical stable IDs")
        print("PASS: control kinds, ranges, steps and select option counts match canonical registry")
        print("PASS: 11 existing route candidates remain static-only")
        print("PASS: 0/50 runtime handlers are enabled")
        print("PASS: unknown, malformed and unimplemented requests fail closed")
        print("LIMIT: this checks metadata and source contract; it does not prove live-game integration")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

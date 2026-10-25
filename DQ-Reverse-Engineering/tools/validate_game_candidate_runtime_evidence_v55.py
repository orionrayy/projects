#!/usr/bin/env python3
"""Fail-closed validator for Dungeon Quest v50 Gold +100K runtime evidence.

This validates evidence structure and file digests. It does not run the game and
cannot authenticate screenshots/logs by itself; human/device review is required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "dq.game-candidate-runtime-evidence.v55"
EXPECTED_CANDIDATE = {
    "package_id": "com.shinybox.smash",
    "version_name": "3.3.2.0",
    "apk_sha256": "f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa",
    "xapk_sha256": "680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430",
    "stk_sha256": "e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e",
}
CHECKS = (
    "install", "launch", "pause_hud", "button_visible", "button_tap",
    "exact_gold_delta", "save_reload", "no_crash", "regression",
)
CHECK_EVIDENCE = {
    "install": "install_log",
    "launch": "launch_screen",
    "pause_hud": "pause_screen",
    "button_visible": "button_visible",
    "button_tap": "action_log",
    "exact_gold_delta": "gold_delta",
    "save_reload": "save_reload",
    "no_crash": "crash_log",
    "regression": "regression_result",
}
REQUIRED_VERIFIED_EVIDENCE = set(CHECK_EVIDENCE.values()) | {
    "offline_state", "backup_restore"
}
ALLOWED_STATES = {"blocked", "in_progress", "failed", "verified"}
ALLOWED_CHECK_STATES = {"not_run", "pass", "fail"}


def _need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_document(doc: dict[str, Any], evidence_root: Path) -> list[str]:
    errors: list[str] = []
    _need(doc.get("schema") == SCHEMA, f"schema must be {SCHEMA}", errors)
    _need(doc.get("candidate") == EXPECTED_CANDIDATE,
          "candidate identity/hashes do not match the v50 audited candidate", errors)

    state = doc.get("status")
    _need(state in ALLOWED_STATES, f"status must be one of {sorted(ALLOWED_STATES)}", errors)
    device = doc.get("device")
    checks = doc.get("checks")
    observations = doc.get("observations")
    evidence = doc.get("evidence")
    if not isinstance(device, dict):
        errors.append("device must be an object")
        device = {}
    if not isinstance(checks, dict):
        errors.append("checks must be an object")
        checks = {}
    if not isinstance(observations, dict):
        errors.append("observations must be an object")
        observations = {}
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
        evidence = []

    _need(device.get("platform") in {"not_run", "emulator", "physical"},
          "device.platform must be not_run, emulator, or physical", errors)
    _need(device.get("profile") in {"not_run", "disposable_offline"},
          "device.profile must be not_run or disposable_offline", errors)
    _need(isinstance(device.get("offline_confirmed"), bool),
          "device.offline_confirmed must be boolean", errors)
    _need(isinstance(device.get("backup_restore_verified"), bool),
          "device.backup_restore_verified must be boolean", errors)
    api_level = device.get("api_level")
    _need(api_level is None or (isinstance(api_level, int) and not isinstance(api_level, bool) and api_level >= 1),
          "device.api_level must be a positive integer or null", errors)

    for name in CHECKS:
        _need(checks.get(name) in ALLOWED_CHECK_STATES,
              f"checks.{name} must be one of {sorted(ALLOWED_CHECK_STATES)}", errors)

    for name in ("gold_before", "gold_after", "gold_after_reload", "crash_count"):
        value = observations.get(name)
        _need(value is None or (isinstance(value, int) and not isinstance(value, bool) and value >= 0),
              f"observations.{name} must be a non-negative integer or null", errors)

    evidence_by_kind: dict[str, dict[str, Any]] = {}
    root = evidence_root.resolve()
    seen_paths: set[str] = set()
    for i, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{i}] must be an object")
            continue
        kind, relative, digest = item.get("kind"), item.get("path"), item.get("sha256")
        _need(isinstance(kind, str) and bool(kind), f"evidence[{i}].kind is required", errors)
        _need(isinstance(relative, str) and bool(relative), f"evidence[{i}].path is required", errors)
        _need(isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
              f"evidence[{i}].sha256 must be lowercase SHA-256 hex", errors)
        if not isinstance(kind, str) or not isinstance(relative, str) or not isinstance(digest, str):
            continue
        _need(kind not in evidence_by_kind, f"duplicate evidence kind: {kind}", errors)
        evidence_by_kind[kind] = item
        _need(relative not in seen_paths, f"duplicate evidence path: {relative}", errors)
        seen_paths.add(relative)
        relpath = Path(relative)
        _need(not relpath.is_absolute() and ".." not in relpath.parts,
              f"evidence path must be relative and cannot traverse directories: {relative}", errors)
        if relpath.is_absolute() or ".." in relpath.parts:
            continue
        candidate_path = (root / relpath).resolve()
        _need(candidate_path == root or root in candidate_path.parents,
              f"evidence path escapes evidence root: {relative}", errors)
        if candidate_path == root or root not in candidate_path.parents:
            continue
        if not candidate_path.is_file():
            errors.append(f"evidence file missing: {relative}")
            continue
        actual = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
        _need(actual == digest, f"evidence digest mismatch: {relative}", errors)

    for check, evidence_kind in CHECK_EVIDENCE.items():
        if checks.get(check) in {"pass", "fail"}:
            _need(evidence_kind in evidence_by_kind,
                  f"checks.{check}={checks.get(check)} requires evidence kind {evidence_kind}", errors)

    if checks.get("exact_gold_delta") == "pass":
        before, after = observations.get("gold_before"), observations.get("gold_after")
        _need(before is not None and after is not None,
              "gold_before and gold_after are required for an exact-delta pass", errors)
        if isinstance(before, int) and isinstance(after, int):
            _need(after - before == 100_000,
                  f"Gold delta must be exactly +100000; observed {after - before}", errors)
    if checks.get("save_reload") == "pass":
        after, reloaded = observations.get("gold_after"), observations.get("gold_after_reload")
        _need(after is not None and reloaded is not None,
              "gold_after and gold_after_reload are required for save/reload pass", errors)
        _need(after == reloaded, "Gold balance must persist exactly after save/reload", errors)
    if checks.get("no_crash") == "pass":
        _need(observations.get("crash_count") == 0,
              "no_crash=pass requires crash_count=0", errors)

    if state == "blocked":
        _need(device.get("platform") == "not_run" and device.get("profile") == "not_run",
              "blocked status requires platform/profile not_run", errors)
        _need(all(checks.get(k) == "not_run" for k in CHECKS),
              "blocked status cannot contain runtime pass/fail claims", errors)
        _need(not evidence, "blocked status must not list runtime evidence", errors)
    elif state in {"in_progress", "failed", "verified"}:
        _need(device.get("platform") in {"emulator", "physical"} and api_level is not None,
              f"{state} status requires a recorded emulator/physical device and API level", errors)
        _need(device.get("profile") == "disposable_offline" and device.get("offline_confirmed") is True,
              f"{state} status requires an offline disposable test profile", errors)
        _need(device.get("backup_restore_verified") is True,
              f"{state} status requires an independently verified backup/restore path", errors)
        _need("offline_state" in evidence_by_kind,
              f"{state} status requires offline_state evidence", errors)
        _need("backup_restore" in evidence_by_kind,
              f"{state} status requires backup_restore evidence", errors)
        if state == "in_progress":
            _need(not any(checks.get(k) == "fail" for k in CHECKS),
                  "in_progress cannot contain failed checks; use status=failed", errors)
        elif state == "failed":
            _need(any(checks.get(k) == "fail" for k in CHECKS),
                  "failed status requires at least one failed check", errors)

    if state == "verified":
        _need(all(checks.get(k) == "pass" for k in CHECKS),
              "verified status requires every runtime check to pass", errors)
        _need(REQUIRED_VERIFIED_EVIDENCE.issubset(evidence_by_kind),
              "verified status missing evidence kinds: " + ", ".join(sorted(REQUIRED_VERIFIED_EVIDENCE - set(evidence_by_kind))), errors)
        _need(observations.get("crash_count") == 0,
              "verified status requires crash_count=0", errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="runtime evidence JSON manifest")
    parser.add_argument("--evidence-root", type=Path, default=Path("."),
                        help="directory containing the manifest's relative evidence files")
    args = parser.parse_args()
    try:
        doc = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("manifest root must be a JSON object")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "errors": [str(exc)]}, indent=2))
        return 2
    errors = validate_document(doc, args.evidence_root)
    if errors:
        print(json.dumps({"status": "INVALID", "errors": errors}, indent=2))
        return 2
    print(json.dumps({
        "status": doc.get("status"),
        "promotion_allowed": doc.get("status") == "verified",
        "runtime_checks_passed": sum(doc.get("checks", {}).get(k) == "pass" for k in CHECKS),
        "runtime_checks_total": len(CHECKS),
        "note": "Evidence structure/hash validation is not a substitute for human review of captured device evidence."
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

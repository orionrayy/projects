#!/usr/bin/env python3
"""Validate the Cheats Sandbox route contract without claiming game runtime integration."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_JAVA_MARKERS = (
    'PAUSE_OPTIONS_ROUTE_ID = "pause.options"',
    'ENTRY_ID = "pause.options.cheats_sandbox"',
    'registerEntry(String parentRouteId, MenuEntry entry)',
    'mutationRecoveryRequired',
    'runtimeStateHydrated',
    'PageStatus.RECOVERY_REQUIRED',
    'PageStatus.READ_ONLY',
    'ROUTE_HOOK_UNAVAILABLE',
)

def validate(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = root / "docs" / "PAUSE_OPTIONS_CHEATS_ROUTE_V16.json"
    bridge_path = root / "runtime-adapter" / "src" / "main" / "java" / "dev" / "dqdebug" / "runtime" / "PauseOptionsCheatsBridge.java"
    if not manifest_path.is_file():
        return {"status": "FAIL", "errors": [f"missing {manifest_path}"]}
    if not bridge_path.is_file():
        return {"status": "FAIL", "errors": [f"missing {bridge_path}"]}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"invalid route manifest: {exc}"]}
    source = bridge_path.read_text(encoding="utf-8")
    for marker in REQUIRED_JAVA_MARKERS:
        if marker not in source:
            errors.append(f"bridge is missing fail-closed route/gate marker: {marker}")
    if manifest.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    if manifest.get("target", {}).get("integration_goal") != "Pause -> Options -> Cheats (Sandbox)":
        errors.append("unexpected integration goal")
    for expected_path in (
        "Resources/HUD/pause.hud",
        "Resources/AIModels/uai_gp_options.aim",
        "Resources/HUD/debug.hud",
        "Games/Smash.gam",
    ):
        if not any(a.get("path") == expected_path for a in manifest.get("observed_native_ui_assets", [])):
            errors.append(f"missing asset evidence record: {expected_path}")
    bridge_meta = manifest.get("bridge", {})
    if bridge_meta.get("implementation_status") != "IMPLEMENTED":
        errors.append("bridge implementation status must be IMPLEMENTED")
    if bridge_meta.get("unit_test_status") != "UNIT-VERIFIED":
        errors.append("bridge unit-test status must be UNIT-VERIFIED")
    binding = manifest.get("route_binding", {})
    if binding.get("status") != "BLOCKED":
        errors.append("route_binding must remain BLOCKED until an actual native UI hook is verified")
    if binding.get("actual_pause_options_hook_implemented") is not False:
        errors.append("manifest must not claim an actual Pause/Options hook")
    if binding.get("actual_cheats_screen_connected") is not False:
        errors.append("manifest must not claim a connected in-game screen")
    runtime = manifest.get("runtime", {})
    if any(runtime.get(k) is not False for k in (
        "pause_options_to_cheats_reached",
        "gameplay_action_verified",
        "apk_built_signed_installed",
    )):
        errors.append("runtime verification must remain explicitly false")
    if runtime.get("runtime_verified_claims") != 0:
        errors.append("runtime_verified_claims must remain zero")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "bridge_markers_checked": len(REQUIRED_JAVA_MARKERS),
        "asset_evidence_records": len(manifest.get("observed_native_ui_assets", [])),
        "route_binding_status": binding.get("status"),
        "runtime_verified_claims": runtime.get("runtime_verified_claims"),
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="DQ-Reverse-Engineering project root")
    args = parser.parse_args()
    report = validate(args.root)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

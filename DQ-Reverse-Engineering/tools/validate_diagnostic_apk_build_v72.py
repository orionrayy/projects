#!/usr/bin/env python3
"""Fail-closed validation for the v72 Logcat-observable diagnostic APK report."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "dq-diagnostic-arm64-apk-build-v72"
APK_SHA256 = "6261d077092098986094ebcf79522b767143467b7b3bc074341b2da6700098b6"
APK_SIZE = 57717702
CANDIDATE_SHA256 = "f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa"
DEX_SHA256 = "1533a5858e8624f2dc615e5335d14afd6de983c0478271963acb985423eb4d48"
BRIDGE_SHA256 = "82f19bbe8aec8ac95030a5e0f773168f0b3a5bfde76e1fe334f103415f8e0fd5"
STK_SHA256 = "e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e"
EXPECTED_MARKERS = [
    "library_load=PASS", "library_load=FAIL",
    "callback_register=PASS", "callback_register=FAIL",
    "callback_roundtrip=PASS", "callback_roundtrip=FAIL",
    "callback_unregister=PASS", "callback_unregister=FAIL",
    "callback_probe=EXCEPTION", "callback_unregister=EXCEPTION",
    "callback_unregister=SKIP",
]

class AuditError(ValueError):
    pass

def need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)

def validate(doc: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    need(doc.get("schema") == SCHEMA, f"schema must be {SCHEMA}", errors)
    need(doc.get("status") == "BUILT_STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_VERIFIED",
         "status must separate static pass from unverified device runtime", errors)
    artifact, inputs = doc.get("artifact"), doc.get("inputs")
    transform, checks = doc.get("package_transform"), doc.get("validation")
    observability, runtime = doc.get("probe_observability"), doc.get("runtime_gate")
    for value, key in ((artifact, "artifact"), (inputs, "inputs"), (transform, "package_transform"),
                       (checks, "validation"), (observability, "probe_observability"), (runtime, "runtime_gate")):
        need(isinstance(value, dict), f"{key} must be an object", errors)
    if errors:
        raise AuditError("; ".join(errors))

    need(artifact.get("file_name") == "DQ_ModKit_v72_ABI_Probe_LOGCAT_ARM64.apk", "APK filename mismatch", errors)
    need(artifact.get("size_bytes") == APK_SIZE, "APK size mismatch", errors)
    need(artifact.get("sha256") == APK_SHA256, "APK SHA-256 mismatch", errors)
    need(artifact.get("package_id") == "com.shinybox.dqv72", "package ID mismatch", errors)
    need(artifact.get("version_name") == "3.3.2.0", "version name mismatch", errors)
    need(artifact.get("launcher_label") == "DQ v72 Tester", "launcher label mismatch", errors)
    need(artifact.get("abi") == "arm64-v8a" and artifact.get("split_count") == 1,
         "expected one standalone ARM64 package", errors)

    need(inputs.get("source_candidate_apk_sha256") == CANDIDATE_SHA256, "candidate APK hash mismatch", errors)
    need(inputs.get("source_stk_sha256") == STK_SHA256, "source STK hash mismatch", errors)
    need(inputs.get("patched_dex_sha256") == DEX_SHA256, "patched DEX hash mismatch", errors)
    need(inputs.get("bridge_sha256") == BRIDGE_SHA256, "native bridge hash mismatch", errors)
    need(inputs.get("source_candidate_package_id") == "com.shinybox.smash", "source package ID mismatch", errors)
    need(inputs.get("source_stk_changed_entries") == ["Resources/HUD/pause.hud"],
         "source STK delta must remain the audited HUD entry only", errors)

    need(transform.get("target_package_id") == "com.shinybox.dqv72", "transformed package ID mismatch", errors)
    need(transform.get("application_id_length_preserved") is True, "package rename must preserve string length", errors)
    need(transform.get("resources_package_name_updated") is True, "resource package ID update missing", errors)
    need(transform.get("launcher_label_before") == "Dungeon Quest" and
         transform.get("launcher_label_after") == "DQ v72 Tester", "launcher label transformation mismatch", errors)
    need(transform.get("unresolved_icon_attributes_removed") is True, "unresolved icon transform missing", errors)
    need(transform.get("source_app_id_preserved") == "com.shinybox.smash", "source app ID changed", errors)
    need(transform.get("original_apk_modified_in_place") is False and
         transform.get("original_xapk_modified_in_place") is False, "original game artifacts must remain untouched", errors)

    for key in ("outer_zip_crc", "all_apk_zip_entries_crc", "zipalign_pre_sign_16k_native",
                "zipalign_post_sign_16k_native", "apksigner_verify_v1", "apksigner_verify_v2",
                "apksigner_verify_v3", "aapt_dump_badging"):
        need(checks.get(key) == "PASS", f"validation.{key} must be PASS", errors)
    need(checks.get("package_id_verified_by_aapt") is True, "aapt package ID verification missing", errors)
    need(checks.get("launchable_activity_found") == "com.shinybox.smash.Smash", "launcher activity mismatch", errors)
    signer = checks.get("signer")
    need(isinstance(signer, dict), "signer object missing", errors)
    if isinstance(signer, dict):
        cert = signer.get("certificate_sha256")
        need(signer.get("kind") == "local diagnostic test certificate", "signer kind mismatch", errors)
        need(isinstance(cert, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", cert)), "certificate digest format invalid", errors)
        need(signer.get("matches_official_signer") is False, "must not claim official signing identity", errors)
        need(signer.get("private_key_in_repository") is False and signer.get("private_key_shared") is False,
             "private test key must remain private", errors)

    need(observability.get("log_tag") == "DQv72Probe", "Logcat tag mismatch", errors)
    markers = observability.get("expected_markers")
    need(isinstance(markers, list) and all(marker in markers for marker in EXPECTED_MARKERS),
         "one or more expected diagnostic markers are missing", errors)
    need(observability.get("runtime_logcat_captured") is False and
         observability.get("runtime_markers_verified") is False,
         "must not fabricate runtime Logcat evidence", errors)

    for key in ("installed_on_device", "launched_on_device", "offline_tested",
                "native_probe_roundtrip_21_to_42_verified", "shutdown_unregister_verified"):
        need(runtime.get(key) is False, f"must not claim runtime gate {key}", errors)
    need(runtime.get("gold_runtime_checks_passed") == 0 and runtime.get("gold_runtime_checks_total") == 9,
         "Gold candidate must stay 0/9 until tested", errors)
    need(runtime.get("catalog_items") == 222 and runtime.get("catalog_routes_assigned") == 0 and
         runtime.get("catalog_runtime_verified_effects") == 0, "catalogue must stay 0/222", errors)
    need(runtime.get("promotion_allowed") is False and doc.get("promotion_allowed") is False,
         "diagnostic package must not be promoted to stable", errors)
    limitations = doc.get("limitations")
    need(isinstance(limitations, list) and any(
        isinstance(x, str) and ("physical-device" in x or "physical device" in x.lower()) for x in limitations),
        "physical-device/runtime limitation must be explicit", errors)

    if errors:
        raise AuditError("; ".join(errors))
    return {
        "status": "PASS_STATIC_V72_DIAGNOSTIC_REPORT",
        "apk_sha256": APK_SHA256,
        "package_id": "com.shinybox.dqv72",
        "static_package_validation": True,
        "runtime_logcat_verified": False,
        "gold_runtime_checks": "0/9",
        "catalog_runtime_verified": "0/222",
        "promotion_allowed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        doc = json.loads(args.report.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("report root must be an object")
        result = validate(doc)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
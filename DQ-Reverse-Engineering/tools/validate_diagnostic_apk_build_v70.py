#!/usr/bin/env python3
"""Fail-closed validator for the v70 diagnostic APK evidence report.

This checks reported values for consistency; it does not authenticate the APK,
re-run apksigner/aapt, install it, or prove live game behavior.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "dq-diagnostic-arm64-apk-build-v70"
APK_SHA256 = "07898a4997b1f470728087d6c4bcd22660980be6d0670217d6d64c2b1769d0e8"
CANDIDATE_SHA256 = "f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa"
DEX_SHA256 = "2c05a2fb599024659b4784086d295fe0b3090dad073c847bbdec3b0964d1ea90"
BRIDGE_SHA256 = "82f19bbe8aec8ac95030a5e0f773168f0b3a5bfde76e1fe334f103415f8e0fd5"
CERT_SHA256 = "b8f8b624ce1368dca48e3413b4433e81d117fb3cbab904e11ec308ecc79ad60c"

class AuditError(ValueError):
    pass

def need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)

def validate(doc: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    need(doc.get("schema") == SCHEMA, f"schema must be {SCHEMA}", errors)
    need(doc.get("status") == "BUILT_STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_VERIFIED",
         "status must indicate static pass/runtime unverified", errors)
    artifact = doc.get("artifact")
    inputs = doc.get("inputs")
    transform = doc.get("package_transform")
    checks = doc.get("validation")
    runtime = doc.get("runtime_gate")
    need(isinstance(artifact, dict), "artifact must be an object", errors)
    need(isinstance(inputs, dict), "inputs must be an object", errors)
    need(isinstance(transform, dict), "package_transform must be an object", errors)
    need(isinstance(checks, dict), "validation must be an object", errors)
    need(isinstance(runtime, dict), "runtime_gate must be an object", errors)
    if errors:
        raise AuditError("; ".join(errors))

    need(artifact.get("file_name") == "DQ_ModKit_v70_ABI_Probe_DIAGNOSTIC_ARM64.apk",
         "diagnostic APK name mismatch", errors)
    need(artifact.get("size_bytes") == 57717702, "diagnostic APK size mismatch", errors)
    need(artifact.get("sha256") == APK_SHA256, "diagnostic APK SHA-256 mismatch", errors)
    need(artifact.get("package_id") == "com.shinybox.dqv70", "diagnostic package ID mismatch", errors)
    need(artifact.get("version_name") == "3.3.2.0", "version name mismatch", errors)
    need(artifact.get("launcher_label") == "DQ v70 Tester", "diagnostic label mismatch", errors)
    need(artifact.get("abi") == "arm64-v8a" and artifact.get("split_count") == 1,
         "expected one standalone ARM64 package", errors)

    need(inputs.get("source_candidate_apk_sha256") == CANDIDATE_SHA256, "source candidate hash mismatch", errors)
    need(inputs.get("source_stk_sha256") == "e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e",
         "source STK hash mismatch", errors)
    need(inputs.get("patched_dex_sha256") == DEX_SHA256, "patched DEX hash mismatch", errors)
    need(inputs.get("bridge_sha256") == BRIDGE_SHA256, "bridge hash mismatch", errors)
    need(inputs.get("source_candidate_package_id") == "com.shinybox.smash",
         "source app ID mismatch", errors)
    need(inputs.get("source_stk_changed_entries") == ["Resources/HUD/pause.hud"],
         "source STK delta must remain the one audited HUD entry", errors)

    need(transform.get("target_package_id") == "com.shinybox.dqv70", "transformed app ID mismatch", errors)
    need(transform.get("application_id_length_preserved") is True, "package rename must preserve string length", errors)
    need(transform.get("resources_package_name_updated") is True, "resource package name update missing", errors)
    need(transform.get("launcher_label_before") == "Dungeon Quest" and
         transform.get("launcher_label_after") == "DQ v70 Tester", "launcher label transform mismatch", errors)
    need(transform.get("unresolved_icon_attributes_removed") is True,
         "aapt fix for unresolved icon reference missing", errors)
    need(transform.get("source_app_id_preserved") == "com.shinybox.smash",
         "official application ID changed in source report", errors)
    need(transform.get("original_apk_modified_in_place") is False and
         transform.get("original_xapk_modified_in_place") is False,
         "original game artifacts must not be modified in place", errors)

    for key in ("outer_zip_crc", "all_apk_zip_entries_crc", "zipalign_pre_sign_16k_native",
                "zipalign_post_sign_16k_native", "apksigner_verify_v1", "apksigner_verify_v2",
                "apksigner_verify_v3", "aapt_dump_badging"):
        need(checks.get(key) == "PASS", f"validation.{key} must be PASS", errors)
    need(checks.get("package_id_verified_by_aapt") is True, "aapt package-ID confirmation missing", errors)
    need(checks.get("launchable_activity_found") == "com.shinybox.smash.Smash",
         "launchable activity mismatch", errors)
    signer = checks.get("signer")
    need(isinstance(signer, dict), "signer must be an object", errors)
    if isinstance(signer, dict):
        need(signer.get("kind") == "local diagnostic test certificate", "signer kind mismatch", errors)
        need(signer.get("certificate_sha256") == CERT_SHA256, "test certificate SHA-256 mismatch", errors)
        need(signer.get("matches_official_signer") is False, "must not claim official signer match", errors)
        need(signer.get("private_key_in_repository") is False and signer.get("private_key_shared") is False,
             "private test key must remain private", errors)

    need(runtime.get("installed_on_device") is False, "must not claim device install", errors)
    need(runtime.get("launched_on_device") is False, "must not claim device launch", errors)
    need(runtime.get("offline_tested") is False, "must not claim offline game runtime test", errors)
    need(runtime.get("native_probe_roundtrip_21_to_42_verified") is False,
         "must not claim native probe round-trip runtime verification", errors)
    need(runtime.get("shutdown_unregister_verified") is False, "must not claim shutdown lifecycle verified", errors)
    need(runtime.get("gold_runtime_checks_passed") == 0 and runtime.get("gold_runtime_checks_total") == 9,
         "Gold candidate gate must remain 0/9", errors)
    need(runtime.get("catalog_items") == 222 and runtime.get("catalog_routes_assigned") == 0 and
         runtime.get("catalog_runtime_verified_effects") == 0,
         "catalog integration count must remain 0/222", errors)
    need(runtime.get("promotion_allowed") is False and doc.get("promotion_allowed") is False,
         "diagnostic APK must not be promoted to stable", errors)
    limitations = doc.get("limitations")
    need(isinstance(limitations, list) and any("physical-device" in x for x in limitations if isinstance(x, str)),
         "device runtime limitation must be explicit", errors)

    if errors:
        raise AuditError("; ".join(errors))
    return {
        "status": "PASS_STATIC_DIAGNOSTIC_APK_REPORT",
        "apk_sha256": APK_SHA256,
        "package_id": "com.shinybox.dqv70",
        "package_validated_statistically": True,
        "game_runtime_tested": False,
        "gold_runtime_checks": "0/9",
        "catalog_runtime_verified": "0/222",
        "promotion_allowed": False
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

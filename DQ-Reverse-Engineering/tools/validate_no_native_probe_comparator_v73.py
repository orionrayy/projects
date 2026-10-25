#!/usr/bin/env python3
"""Fail-closed static evidence validator for the DQ v73 no-probe comparator."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

SCHEMA = "dq-no-native-probe-comparator-v73"
APK_SHA256 = "53799adf3e9d8b3efca062c9a8c97489a050196ad4f9aafcc84acf86d2ad0e49"
APK_SIZE = 57078652
STOCK_DEX_SHA256 = "bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
STK_SHA256 = "e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e"
CERT_SHA256 = "f797c412ba5b96e7ec85d5deb36a0b2905c9c1c45ba354328ab54e1ee3579616"

class AuditError(ValueError):
    pass

def require(ok: bool, message: str, errors: list[str]) -> None:
    if not ok:
        errors.append(message)

def validate(doc: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    require(doc.get("schema") == SCHEMA, "schema mismatch", errors)
    require(doc.get("status") == "STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_TESTED",
            "status must keep device runtime unverified", errors)
    a, i, iso = doc.get("artifact"), doc.get("inputs"), doc.get("isolation_changes")
    sv, signing, runtime = doc.get("static_validation"), doc.get("signing"), doc.get("runtime")
    require(isinstance(a, dict), "artifact object missing", errors)
    require(isinstance(i, dict), "inputs object missing", errors)
    require(isinstance(iso, dict), "isolation_changes object missing", errors)
    require(isinstance(sv, dict), "static_validation object missing", errors)
    require(isinstance(signing, dict), "signing object missing", errors)
    require(isinstance(runtime, dict), "runtime object missing", errors)
    if errors:
        raise AuditError("; ".join(errors))
    require(a.get("file_name") == "DQ_ModKit_v73_NO_NATIVE_PROBE_ARM64.apk", "artifact filename mismatch", errors)
    require(a.get("size_bytes") == APK_SIZE, "artifact size mismatch", errors)
    require(a.get("sha256") == APK_SHA256, "artifact SHA-256 mismatch", errors)
    require(a.get("package_id") == "com.shinybox.dqv73", "diagnostic package ID mismatch", errors)
    require(a.get("launcher_label") == "DQ v73 Tester", "launcher label mismatch", errors)
    require(a.get("abi") == "arm64-v8a" and a.get("split_count") == 1, "expected single ARM64 APK", errors)
    require(i.get("stock_dex_sha256") == STOCK_DEX_SHA256, "stock DEX hash mismatch", errors)
    require(i.get("stk_sha256") == STK_SHA256, "Gold HUD/STK hash mismatch", errors)
    require(iso.get("stock_classes_dex_restored") is True, "stock DEX restoration not confirmed", errors)
    require(iso.get("libdqbridge_removed") is True, "probe library removal not confirmed", errors)
    require(iso.get("native_probe_jni_invocations_present") is False, "probe JNI must be absent", errors)
    require(iso.get("gold_hud_stk_preserved") is True, "Gold HUD asset must match v50 candidate", errors)
    require(iso.get("application_id_is_separate") is True, "package must remain separate", errors)
    for k in ("zip_crc","zipalign_16k_pre_sign","zipalign_16k_post_sign",
              "apksigner_v1","apksigner_v2","apksigner_v3","aapt_badging",
              "package_id","launcher_label","stock_dex_sha256","bridge_absent","stk_hash_preserved"):
        require(sv.get(k) == "PASS", f"static validation {k} did not pass", errors)
    require(signing.get("kind") == "local diagnostic test certificate", "signer kind mismatch", errors)
    require(signing.get("certificate_sha256") == CERT_SHA256, "test certificate digest mismatch", errors)
    require(signing.get("matches_official_signer") is False, "must not claim official signer", errors)
    require(signing.get("private_key_in_repository") is False and signing.get("private_key_shared") is False,
            "private key must remain private", errors)
    for k in ("device_install_tested","device_start_tested","force_close_reproduced_or_cleared","native_callback_invoked"):
        require(runtime.get(k) is False, f"must not claim runtime evidence: {k}", errors)
    require(runtime.get("gold_plus_100k_runtime_checks") == "0/9", "Gold runtime gate must remain blocked", errors)
    require(runtime.get("catalog_runtime_verified") == "0/222", "catalogue runtime gate must remain blocked", errors)
    require(runtime.get("promotion_allowed") is False and doc.get("promotion_allowed") is False,
            "diagnostic comparator must not be promoted to stable", errors)
    limits = doc.get("limitations")
    require(isinstance(limits, list) and any(isinstance(x, str) and "physical-device" in x for x in limits),
            "physical-device limitation must be explicit", errors)
    if errors:
        raise AuditError("; ".join(errors))
    return {"status":"PASS_STATIC_V73_COMPARATOR_REPORT","apk_sha256":APK_SHA256,
            "native_probe_present":False,"device_runtime_tested":False,
            "gold_runtime_checks":"0/9","catalog_runtime_verified":"0/222","promotion_allowed":False}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    args = p.parse_args()
    try:
        doc = json.loads(args.report.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("report root must be object")
        result = validate(doc)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(json.dumps({"status":"INVALID","error":str(e)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""Fail-closed validator for exact-build v70 DEX assembly/round-trip evidence.

This checks a static evidence report only. It does not authenticate the DEX
bytes, build or sign an APK, install the app, or verify engine runtime behavior.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "dq-target-dex-lifecycle-overlay-v70"
SOURCE_DEX_SHA = "bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
RENDERER_SHA = "6509e64a2f3836bbe59a4ab56fde889192dfff80793ff86ead7699561ea01642"
BASELINE_SHA = "298386037aa3c2c91dd0992ac7a0ee94658d629bced2a7facc369d9ac0092292"
PATCHED_DEX_SHA = "2c05a2fb599024659b4784086d295fe0b3090dad073c847bbdec3b0964d1ea90"
EXPECTED_BASELINE_FILES = {
    "com/google/android/gms/common/GooglePlayServicesUtilLight.smali",
    "com/google/android/gms/common/internal/GmsClientSupervisor.smali",
    "com/google/android/gms/internal/ads/zzamr.smali",
    "com/google/android/gms/internal/ads/zzcfh.smali",
    "com/google/android/gms/internal/ads/zzgka.smali",
    "com/google/android/gms/internal/drive/zzit.smali",
    "com/google/android/gms/internal/drive/zzjx.smali",
    "com/google/android/gms/internal/measurement/zzjo.smali",
    "com/google/android/gms/internal/play_billing/zzcd.smali",
    "com/shinybox/smash/S3DConfigChooserGLES1.smali",
    "com/shinybox/smash/Smash.smali",
    "e0/d0$c.smali", "e0/d0$g.smali", "e0/f.smali", "k/b1.smali", "o0/b.smali", "v/f.smali",
}
EXPECTED_PATCHED_CLASSES = {
    "com/shinybox/smash/DqNativeProbe.smali",
    "com/shinybox/smash/S3DRenderer.smali",
}
EXPECTED_ADDED_CLASS = "com/shinybox/smash/DqNativeProbe.smali"

class AuditError(ValueError):
    pass

def need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)

def validate(doc: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    need(doc.get("schema") == SCHEMA, f"schema must be {SCHEMA}", errors)
    need(doc.get("status") == "TARGET_DEX_ASSEMBLY_AND_ROUNDTRIP_PASS_RUNTIME_NOT_VERIFIED",
         "status must reflect a static-only pass with runtime unverified", errors)

    src, tools, base, patched, life = (
        doc.get("source_dex"), doc.get("tools"), doc.get("baseline_reassemble"),
        doc.get("patched_dex"), doc.get("lifecycle_checks")
    )
    for name, value in (("source_dex", src), ("tools", tools), ("baseline_reassemble", base),
                        ("patched_dex", patched), ("lifecycle_checks", life)):
        need(isinstance(value, dict), f"{name} must be an object", errors)
    if errors:
        raise AuditError("; ".join(errors))

    need(src.get("sha256") == SOURCE_DEX_SHA, "source DEX SHA-256 mismatch", errors)
    need(src.get("size_bytes") == 6996484, "source DEX size mismatch", errors)
    need(src.get("method_source_sha256") == RENDERER_SHA, "source renderer disassembly SHA-256 mismatch", errors)
    need(tools.get("baksmali_smali_version") == "2.5.2", "assembler tool version mismatch", errors)
    need(tools.get("api_level") == 28, "assembler API level mismatch", errors)
    need(tools.get("input_classes") == 10768, "source DEX class count mismatch", errors)

    need(base.get("output_sha256") == BASELINE_SHA, "baseline assembled DEX SHA-256 mismatch", errors)
    need(base.get("output_size_bytes") == 7005996, "baseline assembled DEX size mismatch", errors)
    changed_base = base.get("changed_files")
    need(isinstance(changed_base, list), "baseline changed_files must be a list", errors)
    if isinstance(changed_base, list):
        need(len(changed_base) == 17, "baseline smali normalization file count mismatch", errors)
        need(set(changed_base) == EXPECTED_BASELINE_FILES, "baseline normalization file set mismatch", errors)
    need(base.get("source_disassembly_files_changed") == 17, "baseline source normalization count mismatch", errors)
    need(base.get("changes_only_static_default_field_initializers") is True,
         "baseline round-trip delta must be limited to static default field initializers", errors)
    need(base.get("non_field_differences") == [], "baseline method-body differences found", errors)

    need(patched.get("sha256") == PATCHED_DEX_SHA, "patched DEX SHA-256 mismatch", errors)
    need(patched.get("size_bytes") == 7006620, "patched DEX size mismatch", errors)
    need(patched.get("dex_magic") == "dex\n039\u0000", "patched DEX magic/version mismatch", errors)
    need(patched.get("classes_in_roundtrip") == 10769, "round-trip class count mismatch", errors)
    need(patched.get("added_classes") == [EXPECTED_ADDED_CLASS], "added probe class mismatch", errors)
    need(patched.get("missing_classes") == [], "round-trip lost one or more source classes", errors)
    changed = patched.get("changed_classes_vs_baseline")
    need(isinstance(changed, list), "changed_classes_vs_baseline must be a list", errors)
    if isinstance(changed, list):
        need(set(changed) == EXPECTED_PATCHED_CLASSES, "changed class set must contain only renderer and probe", errors)
        need(len(changed) == len(EXPECTED_PATCHED_CLASSES), "duplicate changed class entry", errors)

    need(life.get("register_only_after_true_init_result") is True,
         "probe must be gated by successful engineInitialize result", errors)
    hooks = life.get("shutdown_hook_order")
    need(isinstance(hooks, list) and len(hooks) == 2, "expected two shutdown hook records", errors)
    if isinstance(hooks, list):
        expected_methods = {
            ".method public onDrawFrame(Ljavax/microedition/khronos/opengles/GL10;)V",
            ".method public onShutdown()V",
        }
        need({item.get("method") for item in hooks if isinstance(item, dict)} == expected_methods,
             "shutdown hook method set mismatch", errors)
        for index, item in enumerate(hooks):
            need(isinstance(item, dict), f"shutdown hook {index} must be an object", errors)
            if not isinstance(item, dict):
                continue
            need(item.get("unregister_count") == 1, f"shutdown hook {index} unregister count mismatch", errors)
            need(item.get("shutdown_count") == 1, f"shutdown hook {index} shutdown count mismatch", errors)
            need(item.get("unregister_precedes_shutdown") is True,
                 f"shutdown hook {index} order mismatch", errors)

    need(doc.get("apk_or_xapk_built") is False, "report cannot claim an APK/XAPK was built", errors)
    need(doc.get("installed_or_run_in_game") is False, "report cannot claim in-game runtime execution", errors)
    need(doc.get("gold_runtime_checks_passed") == 0 and doc.get("gold_runtime_checks_total") == 9,
         "Gold runtime gate must remain 0/9", errors)
    need(doc.get("catalog_routes_assigned") == 0 and doc.get("catalog_runtime_verified_effects") == 0,
         "catalog integration counts must remain zero", errors)
    need(doc.get("catalog_items") == 222, "catalog item count mismatch", errors)
    need(doc.get("promotion_allowed") is False, "promotion must remain blocked", errors)
    note = doc.get("note")
    need(isinstance(note, str) and "not been packaged or executed" in note,
         "runtime limitation note is missing", errors)

    if errors:
        raise AuditError("; ".join(errors))
    return {
        "status": "PASS_STATIC_TARGET_DEX_ASSEMBLY_ROUNDTRIP",
        "source_classes": 10768,
        "patched_classes": 10769,
        "changed_classes_vs_baseline": 2,
        "lifecycle_sites_verified": 2,
        "gold_runtime_checks": "0/9",
        "catalog_runtime_verified": "0/222",
        "promotion_allowed": False,
        "note": "Static manifest validation cannot replace binary reinspection or in-game runtime testing."
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        doc = json.loads(args.report.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("report root must be a JSON object")
        result = validate(doc)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

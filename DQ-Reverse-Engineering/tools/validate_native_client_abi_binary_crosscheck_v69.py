#!/usr/bin/env python3
"""Fail-closed consistency validator for the v69 native ABI binary cross-check.

This validates a pinned evidence manifest. It does not load libS3DClient.so or
invoke the game; runtime status is intentionally required to remain blocked.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "dq-native-client-abi-binary-crosscheck-v69"
TARGET_LIB_SHA = "0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083"
BRIDGE_SHA = "82f19bbe8aec8ac95030a5e0f773168f0b3a5bfde76e1fe334f103415f8e0fd5"
SYMBOLS = {
    "register": ("S3DClient_RegisterFunction", "0x7aec14", 188),
    "unregister": ("S3DClient_UnregisterFunction", "0x7aecd0", 132),
    "dispatcher": (
        "_Z42S3DX_AIScriptAPI_system_callClientFunctioniPKN4S3DX10AIVariableEPS0_",
        "0x892bd8", 1556,
    ),
}
JNI_EXPORTS = {
    "Java_com_shinybox_smash_DqNativeProbe_nativeRegisterProbe",
    "Java_com_shinybox_smash_DqNativeProbe_nativeInvokeProbe",
    "Java_com_shinybox_smash_DqNativeProbe_nativeUnregisterProbe",
}

class AuditError(ValueError):
    pass

def need(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)

def validate(doc: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    need(doc.get("schema") == SCHEMA, f"schema must be {SCHEMA}", errors)
    need(doc.get("status") == "STATIC_ABI_CROSSCHECK_PASS_RUNTIME_NOT_VERIFIED",
         "status must remain STATIC_ABI_CROSSCHECK_PASS_RUNTIME_NOT_VERIFIED", errors)
    target = doc.get("target")
    symbols = doc.get("symbols")
    layout = doc.get("layout_evidence")
    bridge = doc.get("bridge_artifact")
    runtime = doc.get("runtime_gate")
    evidence = doc.get("evidence")
    for name, obj in (("target", target), ("symbols", symbols), ("layout_evidence", layout),
                      ("bridge_artifact", bridge), ("runtime_gate", runtime), ("evidence", evidence)):
        need(isinstance(obj, dict), f"{name} must be an object", errors)
    if errors:
        raise AuditError("; ".join(errors))

    need(target.get("package_id") == "com.shinybox.smash", "target package ID mismatch", errors)
    need(target.get("version_name") == "3.3.2.0", "target game version mismatch", errors)
    need(target.get("abi") == "arm64-v8a", "target ABI must be arm64-v8a", errors)
    lib = target.get("library")
    need(isinstance(lib, dict), "target.library must be an object", errors)
    if isinstance(lib, dict):
        need(lib.get("name") == "libS3DClient.so", "target library name mismatch", errors)
        need(lib.get("sha256") == TARGET_LIB_SHA, "target library SHA-256 mismatch", errors)
        need(lib.get("size_bytes") == 17029072, "target library byte count mismatch", errors)
        need(lib.get("elf_class") == "ELF64" and lib.get("elf_machine") == "AArch64",
             "target library must be ELF64/AArch64", errors)
        need(lib.get("library_was_extracted_from_stock_xapk") is True,
             "target library provenance not confirmed", errors)
        need(lib.get("dlsym_symbols_present") is True, "target dynamic symbol presence not confirmed", errors)

    for key, (expected_name, expected_address, expected_size) in SYMBOLS.items():
        item = symbols.get(key)
        need(isinstance(item, dict), f"symbols.{key} missing", errors)
        if not isinstance(item, dict):
            continue
        need(item.get("name") == expected_name, f"symbols.{key}.name mismatch", errors)
        need(item.get("address") == expected_address, f"symbols.{key}.address mismatch", errors)
        need(item.get("size_bytes") == expected_size, f"symbols.{key}.size_bytes mismatch", errors)
        need(item.get("symbol_type") == "FUNC", f"symbols.{key} must be FUNC", errors)
        need(item.get("binding") == "GLOBAL", f"symbols.{key} must be GLOBAL", errors)
        need(item.get("visibility") == "DEFAULT", f"symbols.{key} must be DEFAULT visibility", errors)
    if isinstance(symbols.get("register"), dict):
        need(symbols["register"].get("return_abi_verified_by_disassembly") is True,
             "register return ABI lacks disassembly evidence", errors)
    if isinstance(symbols.get("unregister"), dict):
        need(symbols["unregister"].get("return_abi_verified_by_disassembly") is True,
             "unregister return ABI lacks disassembly evidence", errors)
    if isinstance(symbols.get("dispatcher"), dict):
        disp = symbols["dispatcher"]
        need(disp.get("callback_pointer_offset_bytes") == 8, "dispatcher callback offset must be +8", errors)
        need(disp.get("maximum_argument_records_including_function_name") == 33,
             "dispatcher argument cap must remain 33", errors)
        need(disp.get("symbol_is_in_dynamic_symbol_table") is True,
             "dispatcher dlsym visibility is not confirmed", errors)

    aif = layout.get("aifunction")
    aiv = layout.get("aivariable")
    need(isinstance(aif, dict), "layout_evidence.aifunction missing", errors)
    need(isinstance(aiv, dict), "layout_evidence.aivariable missing", errors)
    if isinstance(aif, dict):
        need(aif.get("callback_field_offset_bytes") == 8, "AIFunction callback offset must be +8", errors)
        need(aif.get("assumed_arm64_size_bytes") == 48, "AIFunction assumed size mismatch", errors)
        need(aif.get("target_dispatcher_reads_callback_at_offset_8") is True,
             "target callback-field load is not confirmed", errors)
        need(aif.get("exact_target_header_available") is False,
             "validator refuses a claim that the exact target header was recovered", errors)
    if isinstance(aiv, dict):
        need(aiv.get("type_field_offset_bytes") == 0, "AIVariable type offset must be 0", errors)
        need(aiv.get("payload_offset_bytes") == 8, "AIVariable payload offset must be +8", errors)
        need(aiv.get("stride_bytes") == 16, "AIVariable stride must remain 16", errors)
        need(aiv.get("target_disassembly_reads_type_byte_at_offset_0") is True,
             "AIVariable type-byte evidence absent", errors)
        need(aiv.get("target_disassembly_uses_16_byte_record_stride") is True,
             "AIVariable stride evidence absent", errors)

    need(bridge.get("build_workflow_run_id") == 40205015193, "bridge workflow run ID mismatch", errors)
    need(bridge.get("build_workflow_conclusion") == "success", "bridge build must be successful", errors)
    need(bridge.get("artifact_id") == 12603596515, "bridge artifact ID mismatch", errors)
    need(bridge.get("sha256") == BRIDGE_SHA, "bridge SHA-256 mismatch", errors)
    need(bridge.get("size_bytes") == 601112, "bridge byte count mismatch", errors)
    need(bridge.get("elf_class") == "ELF64" and bridge.get("elf_machine") == "AArch64",
         "bridge must be ELF64/AArch64", errors)
    exports = bridge.get("jni_exports")
    need(isinstance(exports, list), "bridge jni_exports must be an array", errors)
    if isinstance(exports, list):
        need(set(exports) == JNI_EXPORTS, "bridge JNI export set mismatch", errors)
        need(len(exports) == len(JNI_EXPORTS), "bridge JNI export list has duplicates or extras", errors)
    need(bridge.get("dynamic_dependencies") == ["libdl.so", "libm.so", "libc.so"],
         "bridge dynamic dependency set mismatch", errors)
    need(bridge.get("game_state_side_effects") is False, "probe must remain side-effect-free", errors)
    need(bridge.get("packaged_into_game") is False, "report must not claim bridge is packaged", errors)
    need(bridge.get("runtime_invoked") is False, "report must not claim runtime invocation", errors)

    need(runtime.get("status") == "BLOCKED", "runtime gate must remain BLOCKED", errors)
    for key in ("physical_or_emulator_game_test", "engine_thread_lifecycle_verified",
                "callback_registration_runtime_verified", "callback_roundtrip_21_to_42_runtime_verified",
                "shutdown_unregister_runtime_verified", "game_relaunch_regression_verified"):
        need(runtime.get(key) is False, f"runtime_gate.{key} must remain false", errors)
    need(runtime.get("gold_candidate_checks_passed") == 0 and runtime.get("gold_candidate_checks_total") == 9,
         "Gold runtime gate must remain 0/9", errors)
    need(runtime.get("catalog_native_routes_assigned") == 0 and
         runtime.get("catalog_runtime_verified_effects") == 0 and runtime.get("catalog_items") == 222,
         "catalog counts must remain 0/222", errors)
    need(runtime.get("promotion_allowed") is False, "promotion must remain blocked", errors)

    evidence_tools = evidence.get("tools")
    need(isinstance(evidence_tools, list), "evidence.tools must be an array", errors)
    if isinstance(evidence_tools, list):
        need("readelf --dyn-syms --wide" in evidence_tools, "binary inspection tool list incomplete", errors)
    need(evidence.get("evidence_scope") ==
         "Static binary/symbol cross-check; no call was made into the live game process",
         "evidence scope must remain static-only", errors)

    if errors:
        raise AuditError("; ".join(errors))
    return {
        "status": "PASS_STATIC_ABI_CROSSCHECK",
        "target_symbols_verified": 3,
        "bridge_jni_exports_verified": 3,
        "runtime_checks_passed": 0,
        "runtime_checks_total": 9,
        "catalog_runtime_verified": "0/222",
        "promotion_allowed": False,
        "note": "Manifest consistency checks are not runtime validation and do not authenticate the source of binary evidence."
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

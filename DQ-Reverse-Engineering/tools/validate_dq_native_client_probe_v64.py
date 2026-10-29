#!/usr/bin/env python3
"""Fail-closed validator for the v64 source-only native-client probe manifest."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "dq-native-client-probe-v64"
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    pass


def validate(data: dict[str, Any]) -> dict[str, Any]:
    def need(ok: bool, message: str) -> None:
        if not ok:
            raise ManifestError(message)

    need(data.get("schema") == SCHEMA, "wrong schema")
    need(data.get("status") == "SOURCE_PROTOTYPE_ONLY_NOT_CONNECTED_TO_GAME",
         "probe must remain source-only")
    target = data.get("target", {})
    need(isinstance(target.get("native_library_sha256"), str)
         and SHA_RE.fullmatch(target["native_library_sha256"]) is not None,
         "bad native library hash")

    symbols = data.get("symbols", {})
    expected = {
        "register": ("S3DClient_RegisterFunction", "0x7aec14", 188),
        "unregister": ("S3DClient_UnregisterFunction", "0x7aecd0", 132),
        "script_dispatch": (
            "_Z42S3DX_AIScriptAPI_system_callClientFunctioniPKN4S3DX10AIVariableEPS0_",
            "0x892bd8", 1556,
        ),
    }
    for key, (name, address, size) in expected.items():
        row = symbols.get(key, {})
        need(row.get("name") == name and row.get("va") == address
             and row.get("size_bytes") == size, f"symbol identity drift: {key}")

    contract = data.get("probe_contract", {})
    need(contract.get("function_name") == "dq_native_probe_roundtrip_v64", "probe name drift")
    need(contract.get("side_effects") == "none; does not read/write game state or files",
         "probe must remain side-effect-free")
    need(contract.get("input_count") == 1 and contract.get("input_type") == "number"
         and contract.get("input_value") == 21, "input contract drift")
    need(contract.get("output_count") == 1 and contract.get("output_type") == "number"
         and contract.get("output_value") == 42, "output contract drift")
    need(contract.get("number_storage") == "float64", "AIVariable numeric storage must match the pinned binary64 disassembly evidence")
    numeric_evidence = contract.get("numeric_storage_evidence", "").lower()
    need("ldr d8" in numeric_evidence and "0x6d5048" in numeric_evidence,
         "binary64 disassembly evidence missing")
    need(contract.get("aifunction_callback_offset") == 8
         and contract.get("aifunction_size_assumed_arm64") == 48
         and contract.get("aivariable_size_assumed_arm64") == 16, "ABI layout assumptions drift")

    implementation = data.get("implementation", {})
    for key in ("real_game_invocation_performed", "actual_HUD_AIM_callsite_added",
                "Java_Dex_loader_or_callsite_patched", "APK_or_XAPK_built"):
        need(implementation.get(key) is False, f"must remain false until separately verified: {key}")

    blockers = data.get("known_blockers", [])
    need(any("post-engineInitialize callsite" in item for item in blockers),
         "unwired Java callsite blocker missing")
    need(any("HUD/AIM serialized action" in item for item in blockers),
         "HUD/AIM limitation missing")

    gameplay = data.get("gameplay_integration", {})
    need(gameplay.get("catalog_items") == 222 and gameplay.get("catalog_categories") == 14,
         "catalog baseline drift")
    need(gameplay.get("catalog_routes_assigned") == 0
         and gameplay.get("runtime_verified_catalog_effects") == 0,
         "probe must not promote gameplay integrations")
    need(gameplay.get("v50_runtime_checks_passed") == 0
         and gameplay.get("v50_runtime_checks_total") == 9
         and gameplay.get("status") == "BLOCKED", "runtime gate must remain blocked")

    return {
        "probe": "side-effect-free",
        "input": 21,
        "output": 42,
        "real_game_invocation": False,
        "apk_built": False,
        "catalog_routes": 0,
        "runtime_effects": 0,
        "status": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = validate(data)
    except (OSError, json.JSONDecodeError, ManifestError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 2
    print("PASS: source-only native probe manifest")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

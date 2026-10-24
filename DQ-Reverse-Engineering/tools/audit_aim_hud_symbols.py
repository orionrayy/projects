#!/usr/bin/env python3
"""Audit printable symbol/label presence in selected extracted Dungeon Quest AIM/HUD assets.

This is a binary string inventory only. It does not disassemble proprietary bytecode,
establish call edges, or prove that a UI screen is reachable at runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

PRINTABLE_ASCII = re.compile(rb"[ -~]{3,}")

TARGETS: dict[str, tuple[str, ...]] = {
    "Resources/AIModels/InAppPurchase.aim": (
        "onPurchaseFailed",
        "onPurchaseSuccess",
        "onPurchaseRefunded",
        "onRegisterHandler",
        "onRequestPurchase",
        "onRestorePurchases",
        "onRestorePurchasesComplete",
    ),
    "Resources/AIModels/uai_gp_options.aim": (
        "GetAvatar",
        "getEnvVar",
        "setEnvVar",
        "MappingDefault",
        "MappingGetCode",
        "MappingClearAll",
        "ToggleComponent",
        "onInit",
        "onShowTab",
        "onMapButton",
        "onLoadOptions",
        "onSaveOptions",
        "onShowOptions",
        "onJoypadButtonDown",
        "onSetControlsOption",
        "onSetGameplayOption",
    ),
    "Resources/AIModels/uai_gp_debug.aim": (
        "CompileShaderList",
        "CompileShaders",
        "onDebugLog",
        "onCompileShaders",
        "onDebugLogResult",
        "onDumpShaderList",
        "onDumpFailedShaders",
        "onCompileShadersCancel",
    ),
    "Resources/AIModels/uai_gp_hud.aim": (
        "bPurchasing",
        "sPurchaseID",
        "onPurchaseSuccess",
        "onPurchaseFailed",
    ),
    "Resources/AIModels/uai_gp_account.aim": (
        "SetIAP",
        "GetIAPString",
        "SetSlotInfo",
        "GetSlotInfoString",
        "SetStashInfo",
        "GetStashInfo",
    ),
    "Resources/HUD/pause.hud": (
        "options",
        "onOptionsClose",
        "onOptionMapPosition",
        "onOptionSort",
        "onResume",
    ),
    "Resources/HUD/debug.hud": (
        "debug",
        "onAddBattle",
        "onCreateCS",
        "onAddLevel",
        "onCreateMS",
        "onAddHeroic",
        "onCreateFeat",
        "gotoLevel",
        "onClose",
        "Add Levels",
        "Add Feat",
        "GOTO Floor",
    ),
}


def printable_ascii_runs(data: bytes, min_length: int = 3) -> list[tuple[int, str]]:
    """Return (byte_offset, printable ASCII run) pairs without decoding arbitrary binary."""
    if min_length < 1:
        raise ValueError("min_length must be positive")
    pattern = PRINTABLE_ASCII if min_length == 3 else re.compile(rb"[ -~]{" + str(min_length).encode("ascii") + rb",}")
    return [(m.start(), m.group().decode("ascii")) for m in pattern.finditer(data)]


def audit_asset(asset_root: Path, relative_path: str, required_symbols: tuple[str, ...]) -> dict[str, Any]:
    path = asset_root / relative_path
    if not path.is_file():
        return {
            "path": relative_path,
            "status": "MISSING_FILE",
            "size_bytes": None,
            "sha256": None,
            "symbols": {symbol: None for symbol in required_symbols},
            "missing_symbols": list(required_symbols),
        }

    data = path.read_bytes()
    runs = printable_ascii_runs(data)
    positions: dict[str, int | None] = {}
    for symbol in required_symbols:
        # Search printable runs so arbitrary binary coincidences are not reported as symbols.
        hits = [
            offset + text.find(symbol)
            for offset, text in runs
            if symbol in text
        ]
        positions[symbol] = min(hits) if hits else None

    missing = [symbol for symbol, offset in positions.items() if offset is None]
    return {
        "path": relative_path,
        "status": "PASS" if not missing else "MISSING_SYMBOLS",
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "printable_run_count": len(runs),
        "symbols": positions,
        "missing_symbols": missing,
    }


def audit_tree(asset_root: Path) -> dict[str, Any]:
    reports = [audit_asset(asset_root, path, symbols) for path, symbols in TARGETS.items()]
    missing_files = [item["path"] for item in reports if item["status"] == "MISSING_FILE"]
    missing_symbols = {
        item["path"]: item["missing_symbols"]
        for item in reports if item["status"] == "MISSING_SYMBOLS"
    }
    return {
        "schema_version": 1,
        "audit_type": "printable_ascii_symbol_inventory",
        "root": str(asset_root),
        "status": "PASS" if not missing_files and not missing_symbols else "FAIL",
        "interpretation_limit": (
            "Offsets identify printable symbol/label bytes in decoded assets only. "
            "They do not establish bytecode call edges, handler binding, UI reachability, "
            "purchase grants, persisted entitlement writes, or runtime behavior."
        ),
        "asset_count": len(reports),
        "missing_files": missing_files,
        "missing_symbols": missing_symbols,
        "assets": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "asset_root",
        type=Path,
        help="root of an extracted STK asset tree (contains Resources/AIModels and Resources/HUD)",
    )
    parser.add_argument("--output-json", type=Path, help="write the complete report to this path")
    args = parser.parse_args()

    report = audit_tree(args.asset_root)
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered, encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

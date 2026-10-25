#!/usr/bin/env python3
"""Static Start/tutorial route contract audit for a base ZIP and cumulative source overlay."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from typing import Any
from reconcile_overlay import ReconcileError, checked_zip, read_overlay, source_index, mask_strings_and_comments, single_quoted_symbol_stream

ROUTE_FILES = {
    "assets/deathforth/boot-end.df": [],
    "assets/deathforth/events.df": ["main-event-do-select"],
    "assets/deathforth/game-info.df": [],
    "assets/deathforth/game-select.df": ["main-event-do-select", "select-start", "select-boot"],
    "assets/deathforth/game-start.df": ["game-start-new"],
    "assets/deathforth/game-load.df": [],
    "assets/deathforth/game-save.df": [],
    "assets/deathforth/game-save-char.df": [],
    "assets/deathforth/game-save-state.df": [],
    "assets/deathforth/game-save-team.df": [],
    "assets/deathforth/minimenu.df": [],
    "assets/deathforth/events/tutorial.df": ["tutorchat-1", "tutorchat-2", "tutorchat-3"],
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def normalize_code(text: str) -> tuple[str, bool]:
    masked, unclosed = mask_strings_and_comments(text)
    return re.sub(r"\s+", " ", masked).strip(), unclosed

def audit_start_route(base_path: Path, overlay_path: Path) -> dict[str, Any]:
    bz, base_names = checked_zip(base_path)
    try:
        root_prefix, indexed = source_index(base_names)
        source = {logical: bz.read(member) for logical, member in indexed.items()}
    finally:
        bz.close()
    overlay = read_overlay(overlay_path)
    effective = dict(source)
    for path, payload in overlay.items():
        if path.endswith(".df") and path.startswith("assets/deathforth/"):
            if path not in source:
                raise ReconcileError(f"route audit overlay path missing from base: {path}")
            effective[path] = payload

    files = []
    all_route_contracts_pass = True
    for path, tokens in ROUTE_FILES.items():
        if path not in source or path not in effective:
            files.append({"path": path, "status": "FAIL_MISSING_SOURCE", "required_tokens": tokens})
            all_route_contracts_pass = False
            continue
        before = source[path].decode("utf-8", "replace")
        after = effective[path].decode("utf-8", "replace")
        was_overlaid = path in overlay
        before_code, before_unclosed = normalize_code(before)
        after_code, after_unclosed = normalize_code(after)
        before_symbols, before_symbol_error = single_quoted_symbol_stream(before)
        after_symbols, after_symbol_error = single_quoted_symbol_stream(after)
        token_results = {token: token.encode("ascii") in effective[path] for token in tokens}
        escaped_quote = b'\\"' in effective[path]
        strings_closed = not after_unclosed
        symbol_stream_preserved = before_symbols == after_symbols and not before_symbol_error and not after_symbol_error
        skeleton_same = before_code == after_code if was_overlaid else True
        passed = strings_closed and not escaped_quote and symbol_stream_preserved and skeleton_same and all(token_results.values())
        all_route_contracts_pass = all_route_contracts_pass and passed
        files.append({
            "path": path,
            "overlaid": was_overlaid,
            "display_code_skeleton_matches_base": skeleton_same,
            "ordered_single_quoted_symbols_match_base": symbol_stream_preserved,
            "display_strings_closed": strings_closed,
            "escaped_backslash_quote_absent": not escaped_quote,
            "required_tokens": token_results,
            "status": "PASS_STATIC" if passed else "FAIL_STATIC_CONTRACT",
        })

    boot_path = "assets/deathforth/boot.df"
    boot = effective.get(boot_path, b"")
    boot_before = source.get(boot_path, b"")
    helper_added = b": id-name-localize ( name -- localized-name )" not in boot_before and b": id-name-localize ( name -- localized-name )" in boot
    ready_localized = b'"SIAP." print' in boot
    marker_ok = b'"GAME-MARKER" $anew' in boot and b'"PENANDA-GAME" $anew' not in boot
    boot_symbols_before = single_quoted_symbol_stream(boot_before.decode("utf-8", "replace"))[0]
    boot_symbols_after = single_quoted_symbol_stream(boot.decode("utf-8", "replace"))[0]
    boot_symbols_ok = boot_symbols_before == boot_symbols_after
    boot_unclosed = normalize_code(boot.decode("utf-8", "replace"))[1]
    boot_escaped_quote = b'\\"' in boot
    boot_pass = helper_added and ready_localized and marker_ok and boot_symbols_ok and not boot_unclosed and not boot_escaped_quote

    return {
        "project": "DR2C VORENYX",
        "audit": "static Start/tutorial route contract; not runtime proof",
        "base": {"file": base_path.name, "bytes": base_path.stat().st_size, "sha256": sha256_file(base_path), "source_prefix": root_prefix},
        "overlay": {"file": overlay_path.name, "bytes": overlay_path.stat().st_size, "sha256": sha256_file(overlay_path)},
        "route_files": files,
        "boot_df_additive_localization_check": {
            "id_name_localize_helper_added": helper_added,
            "READY_label_translated_to_SIAP": ready_localized,
            "canonical_GAME_MARKER_preserved": marker_ok,
            "ordered_single_quoted_symbols_preserved": boot_symbols_ok,
            "display_strings_closed": not boot_unclosed,
            "escaped_backslash_quote_absent": not boot_escaped_quote,
            "status": "PASS_STATIC" if boot_pass else "FAIL_STATIC_CONTRACT",
            "note": "boot.df differs from base because it adds id-name-localize and localizes READY to SIAP; static analysis does not interpret this helper at runtime.",
        },
        "summary": {
            "route_files_checked": len(files),
            "route_files_static_pass": sum(x["status"] == "PASS_STATIC" for x in files),
            "route_files_static_fail": sum(x["status"] != "PASS_STATIC" for x in files),
            "boot_additive_check_pass": boot_pass,
            "overall_static_contracts_pass": all_route_contracts_pass and boot_pass,
        },
        "limitations": [
            "This compares normalized lexical code skeletons and Forth-style single-quoted symbol streams; it is not a full Deathforth parser.",
            "A static pass does not prove that the game engine dispatches events correctly at runtime.",
            "APK build/sign/install, touchscreen input, UI fit, Start-button navigation, gameplay and save/load were not tested.",
        ],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        result = audit_start_route(args.base, args.overlay)
    except ReconcileError as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["summary"]["overall_static_contracts_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())

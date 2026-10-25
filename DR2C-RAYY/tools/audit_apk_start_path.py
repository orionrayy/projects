#!/usr/bin/env python3
"""Static APK-to-APK audit of critical DR2C Start/tutorial routes; not runtime proof."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

ROUTE_FILES: dict[str, list[str]] = {
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
MAX_DIFF_TOKENS = 60


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def mask_strings_and_comments(text: str) -> tuple[str, bool]:
    """Mask double-quoted strings and // comments without changing code positions."""
    out = list(text)
    i, in_string = 0, False
    while i < len(text):
        if in_string:
            if text[i] == '"':
                out[i] = " "
                in_string = False
                i += 1
                continue
            if text[i] not in "\r\n":
                out[i] = " "
            i += 1
            continue
        if text[i:i + 2] == "//":
            while i < len(text) and text[i] not in "\r\n":
                out[i] = " "
                i += 1
            continue
        if text[i] == '"':
            out[i] = " "
            in_string = True
        i += 1
    return "".join(out), in_string


def code_tokens(text: str) -> tuple[list[str], bool]:
    masked, unclosed = mask_strings_and_comments(text)
    return re.findall(r"[A-Za-z_][A-Za-z0-9_-]*|[^\s]", masked), unclosed


def symbol_stream(text: str) -> tuple[list[str], bool]:
    masked, unclosed = mask_strings_and_comments(text)
    return re.findall(r"'\s*([A-Za-z_][A-Za-z0-9_-]*)", masked), unclosed


def code_delta(base: str, candidate: str) -> dict[str, Any]:
    left, left_unclosed = code_tokens(base)
    right, right_unclosed = code_tokens(candidate)
    groups = []
    matcher = difflib.SequenceMatcher(a=left, b=right, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        groups.append({
            "kind": tag,
            "base_tokens": left[i1:i2][:MAX_DIFF_TOKENS],
            "candidate_tokens": right[j1:j2][:MAX_DIFF_TOKENS],
            "base_token_count": i2 - i1,
            "candidate_token_count": j2 - j1,
        })
    return {
        "normalized_code_tokens_match": left == right,
        "base_strings_unclosed": left_unclosed,
        "candidate_strings_unclosed": right_unclosed,
        "change_groups": groups,
    }


def checked_apk(path: Path) -> tuple[zipfile.ZipFile, list[str], str | None]:
    try:
        archive = zipfile.ZipFile(path, "r")
        names = archive.namelist()
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f"cannot open APK ZIP {path}: {exc}") from exc
    if len(names) != len(set(names)):
        archive.close()
        raise ValueError(f"APK contains duplicate ZIP paths: {path.name}")
    return archive, names, archive.testzip()


def audit(base_path: Path, candidate_path: Path) -> dict[str, Any]:
    base, base_names, base_bad = checked_apk(base_path)
    candidate, candidate_names, candidate_bad = checked_apk(candidate_path)
    try:
        base_set, candidate_set = set(base_names), set(candidate_names)
        rows = []
        missing = []
        for path, required in ROUTE_FILES.items():
            if path not in base_set or path not in candidate_set:
                missing.append(path)
                rows.append({
                    "path": path, "status": "FAIL_MISSING_ROUTE",
                    "missing_from_base": path not in base_set,
                    "missing_from_candidate": path not in candidate_set,
                    "required_tokens": {token: False for token in required},
                })
                continue
            before_bytes, after_bytes = base.read(path), candidate.read(path)
            before, after = before_bytes.decode("utf-8", "replace"), after_bytes.decode("utf-8", "replace")
            before_masked, _ = mask_strings_and_comments(before)
            after_masked, after_unclosed = mask_strings_and_comments(after)
            code_same = re.sub(r"\s+", " ", before_masked).strip() == re.sub(r"\s+", " ", after_masked).strip()
            before_symbols, before_sym_error = symbol_stream(before)
            after_symbols, after_sym_error = symbol_stream(after)
            symbols_same = before_symbols == after_symbols and not before_sym_error and not after_sym_error
            token_results = {token: token.encode("ascii") in after_bytes for token in required}
            escaped_quote = b'\\"' in after_bytes
            delta = code_delta(before, after)["change_groups"]
            invariants = not after_unclosed and not escaped_quote and symbols_same and all(token_results.values())
            passed = invariants and code_same
            rows.append({
                "path": path,
                "base_sha256": hashlib.sha256(before_bytes).hexdigest(),
                "candidate_sha256": hashlib.sha256(after_bytes).hexdigest(),
                "byte_identical": before_bytes == after_bytes,
                "normalized_code_skeleton_matches_base": code_same,
                "ordered_single_quoted_symbols_match_base": symbols_same,
                "strings_closed": not after_unclosed,
                "escaped_backslash_quote_absent": not escaped_quote,
                "required_tokens": token_results,
                "code_token_delta": delta,
                "status": "PASS_STATIC" if passed else (
                    "REVIEW_CODE_DRIFT" if invariants and not code_same else "FAIL_STATIC_INVARIANT"
                ),
            })
        boot = candidate.read("assets/deathforth/boot.df") if "assets/deathforth/boot.df" in candidate_set else b""
        marker = b'"GAME-MARKER" $anew' in boot and b'"PENANDA-GAME" $anew' not in boot
        escaped_paths = [
            path for path in candidate_names
            if path.endswith(".df") and path.startswith("assets/deathforth/") and b'\\"' in candidate.read(path)
        ]
        static_pass = base_bad is None and candidate_bad is None and not missing and all(
            row["status"] == "PASS_STATIC" for row in rows
        ) and marker
        return {
            "project": "DR2C VORENYX",
            "audit": "APK-to-APK Start/tutorial static comparison; not runtime proof",
            "base": {"file": base_path.name, "bytes": base_path.stat().st_size,
                     "sha256": sha256_file(base_path), "zip_entries": len(base_names),
                     "zip_crc": "PASS" if base_bad is None else "FAIL"},
            "candidate": {"file": candidate_path.name, "bytes": candidate_path.stat().st_size,
                          "sha256": sha256_file(candidate_path), "zip_entries": len(candidate_names),
                          "zip_crc": "PASS" if candidate_bad is None else "FAIL",
                          "extra_zip_paths": sorted(candidate_set - base_set),
                          "missing_zip_paths": sorted(base_set - candidate_set)},
            "global_checks": {
                "base_duplicate_paths": len(base_names) - len(base_set),
                "candidate_duplicate_paths": len(candidate_names) - len(candidate_set),
                "canonical_GAME_MARKER": marker,
                "escaped_quote_paths": escaped_paths,
                "missing_route_files": missing,
            },
            "route_files": rows,
            "summary": {
                "route_files_checked": len(rows),
                "route_files_static_pass": sum(row["status"] == "PASS_STATIC" for row in rows),
                "route_files_review_code_drift": sum(row["status"] == "REVIEW_CODE_DRIFT" for row in rows),
                "route_files_static_fail": sum(row["status"] not in ("PASS_STATIC", "REVIEW_CODE_DRIFT") for row in rows),
                "overall_static_gate_pass": static_pass,
            },
            "limits": [
                "This is lexical/static analysis, not a full Deathforth parser.",
                "A changed code token may be an intentional display rewrite; it must be reviewed rather than guessed safe.",
                "APK install, Start tap dispatch, embedded VM, gameplay, UI fit, save/load and runtime stability require device-side testing.",
            ],
        }
    finally:
        base.close()
        candidate.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = audit(args.base, args.candidate)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["summary"]["overall_static_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

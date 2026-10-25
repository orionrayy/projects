#!/usr/bin/env python3
"""Compare package payload surfaces and verify native label edits stay in string slots.

Static archive comparison only; does not prove Android runtime behavior.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

EXPECTED_NON_SCRIPT_CHANGES = {
    "AndroidManifest.xml",
    "META-INF/MANIFEST.MF",
    "assets/gfx/ui/dr2c_title_small.png",
    "res/drawable-xxhdpi-v4/splash.png",
    "lib/arm64-v8a/libmain.so",
    "lib/armeabi-v7a/libmain.so",
}
EXPECTED_BASE_ONLY = {"META-INF/CERT.RSA", "META-INF/CERT.SF"}
EXPECTED_CANDIDATE_ONLY = {
    "META-INF/DR2C-VOR.RSA",
    "META-INF/DR2C-VOR.SF",
    "assets/gfx/ui/vorenyx_title_screen.png",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_checked(path: Path) -> tuple[zipfile.ZipFile, list[str], str | None]:
    try:
        archive = zipfile.ZipFile(path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f"cannot open archive {path}: {exc}") from exc
    names = archive.namelist()
    if len(names) != len(set(names)):
        archive.close()
        raise ValueError(f"archive contains duplicate paths: {path.name}")
    return archive, names, archive.testzip()


def contiguous_runs(base: bytes, candidate: bytes) -> list[tuple[int, int]]:
    if len(base) != len(candidate):
        raise ValueError("binary length differs; in-place string-slot analysis is unsafe")
    runs: list[tuple[int, int]] = []
    start = end = None
    for i, (a, b) in enumerate(zip(base, candidate)):
        if a != b:
            if start is None:
                start = i
            end = i
        elif start is not None:
            runs.append((start, end if end is not None else start))
            start = end = None
    if start is not None:
        runs.append((start, end if end is not None else start))
    return runs


def analyze_native_strings(path: str, base: bytes, candidate: bytes) -> dict[str, Any]:
    if len(base) != len(candidate):
        return {"path": path, "same_size": False, "status": "FAIL_SIZE_CHANGED"}
    slots: dict[tuple[int, int], dict[str, Any]] = {}
    changed_bytes = 0
    invalid_offset_changes = []
    for pos, (a, b) in enumerate(zip(base, candidate)):
        if a == b:
            continue
        changed_bytes += 1
        start = base.rfind(b"\0", 0, pos) + 1
        end = base.find(b"\0", pos)
        if end < 0 or start >= end:
            invalid_offset_changes.append(pos)
            continue
        old = base[start:end]
        new = candidate[start:end].rstrip(b"\0")
        slots[(start, end)] = {
            "offset_start": start,
            "offset_end_exclusive": end,
            "base_text": old.decode("ascii", "replace"),
            "candidate_text": new.decode("ascii", "replace"),
            "fixed_slot_bytes": end - start,
            "candidate_text_bytes": len(new),
            "base_printable_ascii": all(32 <= ch < 127 for ch in old),
            "candidate_printable_ascii": all(32 <= ch < 127 for ch in new),
        }
    covered = sum(
        sum(base[i] != candidate[i] for i in range(start, end))
        for start, end in slots
    )
    slot_safe = not invalid_offset_changes and covered == changed_bytes and all(
        item["base_printable_ascii"] and item["candidate_printable_ascii"] for item in slots.values()
    )
    return {
        "path": path,
        "same_size": True,
        "bytes": len(base),
        "changed_byte_count": changed_bytes,
        "contiguous_change_runs": len(contiguous_runs(base, candidate)),
        "changed_string_slot_count": len(slots),
        "all_changed_bytes_inside_ascii_string_slots": slot_safe,
        "invalid_change_offsets": invalid_offset_changes,
        "slots": [slots[key] for key in sorted(slots)],
        "status": "PASS_STRING_SLOTS_ONLY" if slot_safe else "REVIEW_BINARY_DIFF",
    }


def audit(base_path: Path, candidate_path: Path) -> dict[str, Any]:
    base, base_names, base_bad = open_checked(base_path)
    candidate, candidate_names, candidate_bad = open_checked(candidate_path)
    try:
        base_set, candidate_set = set(base_names), set(candidate_names)
        common = sorted(base_set & candidate_set)
        changed, identical = [], []
        base_data: dict[str, bytes] = {}
        candidate_data: dict[str, bytes] = {}
        for name in common:
            a, b = base.read(name), candidate.read(name)
            base_data[name], candidate_data[name] = a, b
            (identical if a == b else changed).append(name)
        added = sorted(candidate_set - base_set)
        removed = sorted(base_set - candidate_set)
        dex = sorted(name for name in common if name.endswith(".dex"))
        dex_changed = [name for name in dex if base_data[name] != candidate_data[name]]
        native = sorted(name for name in common if name.endswith(".so"))
        native_changed = [name for name in native if base_data[name] != candidate_data[name]]
        non_main_native_changed = [name for name in native_changed if not name.endswith("/libmain.so")]
        main_reports = [
            analyze_native_strings(name, base_data[name], candidate_data[name])
            for name in native_changed if name.endswith("/libmain.so")
        ]
        changed_df = sorted(name for name in changed if name.endswith(".df"))
        changed_non_script = sorted(name for name in changed if not name.endswith(".df"))
        unexpected_non_script = sorted(set(changed_non_script) - EXPECTED_NON_SCRIPT_CHANGES)
        all_slot_safe = all(x.get("status") == "PASS_STRING_SLOTS_ONLY" for x in main_reports)
        entry_add_remove_matches_expected = set(removed) == EXPECTED_BASE_ONLY and set(added) == EXPECTED_CANDIDATE_ONLY
        static_pass = (
            base_bad is None and candidate_bad is None and not dex_changed and
            not non_main_native_changed and not unexpected_non_script and all_slot_safe and
            entry_add_remove_matches_expected and
            set(x["path"] for x in main_reports) == {
                "lib/arm64-v8a/libmain.so", "lib/armeabi-v7a/libmain.so"
            }
        )
        return {
            "project": "DR2C VORENYX",
            "audit": "base-vs-candidate APK package change surface; static only",
            "base": {"file": base_path.name, "bytes": base_path.stat().st_size,
                     "sha256": sha256(base_path.read_bytes()), "entries": len(base_names),
                     "zip_crc": "PASS" if base_bad is None else "FAIL", "first_bad_entry": base_bad},
            "candidate": {"file": candidate_path.name, "bytes": candidate_path.stat().st_size,
                          "sha256": sha256(candidate_path.read_bytes()), "entries": len(candidate_names),
                          "zip_crc": "PASS" if candidate_bad is None else "FAIL", "first_bad_entry": candidate_bad},
            "entry_surface": {
                "common_paths": len(common), "byte_identical_common_paths": len(identical),
                "changed_common_paths": changed, "base_only_paths": removed, "candidate_only_paths": added,
                "changed_deathforth_scripts": len(changed_df), "changed_non_script_paths": changed_non_script,
                "unexpected_changed_non_script_paths": unexpected_non_script,
                "entry_add_remove_matches_expected": entry_add_remove_matches_expected,
                "unexpected_base_only_paths": sorted(set(removed) - EXPECTED_BASE_ONLY),
                "unexpected_candidate_only_paths": sorted(set(added) - EXPECTED_CANDIDATE_ONLY),
            },
            "dex": {"entry_count": len(dex), "changed_paths": dex_changed, "all_dex_byte_identical": not dex_changed},
            "native_libraries": {
                "native_so_count": len(native), "changed_native_so_paths": native_changed,
                "changed_non_libmain_so_paths": non_main_native_changed,
                "libmain_string_slot_audits": main_reports,
                "all_non_libmain_native_libraries_byte_identical": not non_main_native_changed,
                "libmain_changes_confined_to_ascii_string_slots": all_slot_safe,
            },
            "summary": {
                "base_zip_crc_pass": base_bad is None,
                "candidate_zip_crc_pass": candidate_bad is None,
                "changed_deathforth_script_count": len(changed_df),
                "dex_byte_identical": not dex_changed,
                "non_libmain_native_libraries_identical": not non_main_native_changed,
                "libmain_string_slot_only_changes": all_slot_safe,
                "no_unexpected_non_script_changes": not unexpected_non_script,
                "entry_add_remove_matches_expected": entry_add_remove_matches_expected,
                "overall_static_package_diff_pass": static_pass,
            },
            "limits": [
                "This audit describes package differences; it does not infer runtime causality.",
                "DEX identity and string-only native diffs do not prove touch dispatch, licensing acceptance, or gameplay stability.",
                "A locally re-signed APK may still be rejected by native integrity/licensing mechanisms.",
            ],
        }
    finally:
        base.close()
        candidate.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-apk", type=Path, required=True)
    parser.add_argument("--candidate-apk", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = audit(args.base_apk, args.candidate_apk)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["summary"]["overall_static_package_diff_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

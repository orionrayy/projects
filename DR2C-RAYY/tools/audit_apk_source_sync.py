#!/usr/bin/env python3
"""Audit byte-for-byte source/overlay synchronization against a base and candidate APK.

Uses only the Python standard library. This is packaging/source-lineage validation,
not a Deathforth interpreter or Android runtime test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

SCRIPT_PREFIX = "assets/deathforth/"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_checked(path: Path) -> tuple[zipfile.ZipFile, list[str], str | None, int]:
    try:
        archive = zipfile.ZipFile(path, "r")
        names = archive.namelist()
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f"cannot open ZIP/APK {path}: {exc}") from exc
    duplicates = len(names) - len(set(names))
    if duplicates:
        archive.close()
        raise ValueError(f"archive {path.name} contains {duplicates} duplicate ZIP path(s)")
    return archive, names, archive.testzip(), duplicates


def logical_script_path(member: str) -> str | None:
    at = member.find(SCRIPT_PREFIX)
    if at < 0 or not member.endswith(".df") or member.endswith("/"):
        return None
    logical = member[at:]
    if any(part in ("", ".", "..") for part in logical.split("/")):
        raise ValueError(f"non-canonical script path in archive: {member}")
    return logical


def read_script_map(archive: zipfile.ZipFile, names: list[str], mode: str) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for member in names:
        if mode == "overlay":
            if not member.endswith(".df") or SCRIPT_PREFIX not in member:
                continue
            idx = member.find("overlay/" + SCRIPT_PREFIX)
            if idx < 0:
                raise ValueError(f"script payload is outside an explicit overlay tree: {member}")
            logical = member[idx + len("overlay/"):]
        elif mode == "apk":
            if not member.startswith(SCRIPT_PREFIX) or not member.endswith(".df"):
                continue
            logical = member
        else:
            logical = logical_script_path(member)
            if logical is None:
                continue
        if logical in result:
            raise ValueError(f"multiple archive entries map to the same script path: {logical}")
        if any(part in ("", ".", "..") for part in logical.split("/")):
            raise ValueError(f"non-canonical logical path: {logical}")
        result[logical] = archive.read(member)
    return result


def pack_info(path: Path, names: list[str], crc_bad: str | None) -> dict[str, Any]:
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "zip_entries": len(names),
        "zip_crc": "PASS" if crc_bad is None else "FAIL",
        "first_bad_zip_entry": crc_bad,
        "duplicate_paths": 0,
    }


def audit(base_source_path: Path, base_apk_path: Path, candidate_apk_path: Path,
          layer_paths: list[Path]) -> dict[str, Any]:
    open_archives: list[zipfile.ZipFile] = []
    try:
        source_zip, source_names, source_bad, _ = open_checked(base_source_path)
        open_archives.append(source_zip)
        base_zip, base_names, base_bad, _ = open_checked(base_apk_path)
        open_archives.append(base_zip)
        candidate_zip, candidate_names, candidate_bad, _ = open_checked(candidate_apk_path)
        open_archives.append(candidate_zip)

        source_scripts = read_script_map(source_zip, source_names, "source")
        base_scripts = read_script_map(base_zip, base_names, "apk")
        candidate_scripts = read_script_map(candidate_zip, candidate_names, "apk")

        source_keys, base_keys, candidate_keys = set(source_scripts), set(base_scripts), set(candidate_scripts)
        base_source_mismatches = sorted(
            key for key in source_keys & base_keys if source_scripts[key] != base_scripts[key]
        )
        base_source_missing = sorted(source_keys - base_keys)
        base_source_extra = sorted(base_keys - source_keys)

        effective = dict(source_scripts)
        provenance = {key: "base_source_archive" for key in source_scripts}
        overlay_counts = []
        override_paths: set[str] = set()
        all_layers_crc_pass = True
        for order, layer_path in enumerate(layer_paths, start=1):
            layer_zip, layer_names, layer_bad, _ = open_checked(layer_path)
            open_archives.append(layer_zip)
            layer_scripts = read_script_map(layer_zip, layer_names, "overlay")
            if layer_bad is not None:
                all_layers_crc_pass = False
            invalid = sorted(set(layer_scripts) - source_keys)
            if invalid:
                raise ValueError(f"overlay {layer_path.name} references unknown source paths: {invalid[:10]}")
            overrides = sorted(set(layer_scripts) & set(effective))
            override_paths.update(overrides)
            effective.update(layer_scripts)
            for key in layer_scripts:
                provenance[key] = f"layer_{order}:{layer_path.name}"
            overlay_counts.append({
                "order": order,
                "file": layer_path.name,
                "sha256": sha256_file(layer_path),
                "script_count": len(layer_scripts),
                "overrides_prior_payload_count": len(overrides),
                "zip_crc": "PASS" if layer_bad is None else "FAIL",
                "paths_missing_from_base_source": invalid,
            })

        effective_keys = set(effective)
        candidate_missing = sorted(effective_keys - candidate_keys)
        candidate_extra = sorted(candidate_keys - effective_keys)
        matched = sorted(key for key in effective_keys & candidate_keys if effective[key] == candidate_scripts[key])
        mismatches = []
        for key in sorted(effective_keys & candidate_keys):
            if effective[key] == candidate_scripts[key]:
                continue
            mismatches.append({
                "path": key,
                "expected_layer": provenance.get(key, "unknown"),
                "expected_bytes": len(effective[key]),
                "candidate_bytes": len(candidate_scripts[key]),
                "expected_sha256": hashlib.sha256(effective[key]).hexdigest(),
                "candidate_sha256": hashlib.sha256(candidate_scripts[key]).hexdigest(),
            })

        base_parity = source_bad is None and base_bad is None and not base_source_mismatches and not base_source_missing and not base_source_extra
        candidate_sync = candidate_bad is None and not candidate_missing and not candidate_extra and not mismatches
        overlay_script_count = sum(
            1 for key, payload in effective.items() if key in source_scripts and source_scripts[key] != payload
        )
        return {
            "project": "DR2C VORENYX",
            "audit": "base source -> ordered source layers -> candidate APK exact script-payload reconciliation",
            "base_source_archive": pack_info(base_source_path, source_names, source_bad),
            "base_apk": pack_info(base_apk_path, base_names, base_bad),
            "candidate_apk": pack_info(candidate_apk_path, candidate_names, candidate_bad),
            "layers": overlay_counts,
            "base_source_to_base_apk": {
                "source_script_count": len(source_scripts),
                "base_apk_script_count": len(base_scripts),
                "exact_payload_matches": len(source_keys & base_keys) - len(base_source_mismatches),
                "mismatch_paths": base_source_mismatches,
                "missing_from_base_apk": base_source_missing,
                "extra_in_base_apk": base_source_extra,
                "exact": base_parity,
            },
            "effective_source_to_candidate_apk": {
                "effective_script_count": len(effective),
                "candidate_script_count": len(candidate_scripts),
                "exact_payload_matches": len(matched),
                "missing_from_candidate": candidate_missing,
                "extra_in_candidate": candidate_extra,
                "mismatches": mismatches,
                "overridden_path_count": len(override_paths),
                "exact": candidate_sync,
            },
            "summary": {
                "base_source_to_base_apk_exact": base_parity,
                "all_layer_zip_crcs_pass": all_layers_crc_pass,
                "candidate_source_sync_exact": candidate_sync,
                "source_script_count": len(source_scripts),
                "overlay_script_count": overlay_script_count,
                "candidate_script_matches": len(matched),
                "candidate_script_mismatches": len(mismatches),
                "overall_payload_sync_pass": base_parity and candidate_sync and all_layers_crc_pass,
            },
            "limits": [
                "Exact payload parity does not prove the embedded Deathforth interpreter executes scripts correctly.",
                "APK install, input dispatch, gameplay, UI fit, save/load, and native integrity/licensing runtime require device-side validation.",
                "This checker reports bytes and does not classify semantic translation quality.",
            ],
        }
    finally:
        for archive in open_archives:
            archive.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-source", type=Path, required=True, help="base source ZIP")
    parser.add_argument("--base-apk", type=Path, required=True, help="base APK matching source ZIP")
    parser.add_argument("--candidate-apk", type=Path, required=True, help="candidate APK being audited")
    parser.add_argument("--layer", type=Path, action="append", default=[], help="overlay ZIP; repeat in application order")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = audit(args.base_source, args.base_apk, args.candidate_apk, args.layer)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["summary"]["overall_payload_sync_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

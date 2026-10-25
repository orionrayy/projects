#!/usr/bin/env python3
"""Verify that a candidate STK differs from its source in exactly one named asset."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
from typing import Any
from stk_packer import StkArchive, safe_path

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verify_delta(source_path: pathlib.Path, candidate_path: pathlib.Path,
                 expected_changed_path: str = "Resources/HUD/debug.hud",
                 expected_source_sha256: str | None = None,
                 expected_candidate_sha256: str | None = None) -> dict[str, Any]:
    src_path, dst_path = source_path.resolve(), candidate_path.resolve()
    if src_path == dst_path:
        raise ValueError("source and candidate must be different paths")
    source_bytes, candidate_bytes = src_path.read_bytes(), dst_path.read_bytes()
    source_hash, candidate_hash = sha256(source_bytes), sha256(candidate_bytes)
    if expected_source_sha256 and source_hash != expected_source_sha256:
        raise ValueError(f"source SHA-256 mismatch: {source_hash}")
    if expected_candidate_sha256 and candidate_hash != expected_candidate_sha256:
        raise ValueError(f"candidate SHA-256 mismatch: {candidate_hash}")
    expected = safe_path(expected_changed_path)
    source, candidate = StkArchive(source_bytes, str(src_path)), StkArchive(candidate_bytes, str(dst_path))
    if source.version != candidate.version:
        raise ValueError(f"STK version differs: {source.version} vs {candidate.version}")
    if source.count != candidate.count:
        raise ValueError(f"entry count differs: {source.count} vs {candidate.count}")
    src_entries = {e.name: e for e in source.entries}
    dst_entries = {e.name: e for e in candidate.entries}
    if src_entries.keys() != dst_entries.keys():
        missing = sorted(src_entries.keys() - dst_entries.keys())
        extra = sorted(dst_entries.keys() - src_entries.keys())
        raise ValueError(f"entry inventory differs; missing={missing[:10]}, extra={extra[:10]}")
    changed = []
    total_decoded = 0
    for name, old_entry in src_entries.items():
        old_data = source.decode(old_entry)
        new_data = candidate.decode(dst_entries[name])
        total_decoded += len(old_data)
        if old_data != new_data:
            changed.append({
                "path": name,
                "source_size": len(old_data),
                "candidate_size": len(new_data),
                "source_sha256": sha256(old_data),
                "candidate_sha256": sha256(new_data),
            })
    if len(changed) != 1 or changed[0]["path"] != expected:
        names = [item["path"] for item in changed]
        raise ValueError(f"expected exactly one changed asset {str(expected)!r}; found {names!r}")
    return {
        "schema": "stk-single-asset-delta-v48",
        "status": "PASS",
        "source": str(src_path),
        "candidate": str(dst_path),
        "source_sha256": source_hash,
        "candidate_sha256": candidate_hash,
        "source_bytes": len(source_bytes),
        "candidate_bytes": len(candidate_bytes),
        "stk_version": source.version,
        "entry_count": source.count,
        "decoded_source_bytes": total_decoded,
        "changed_entry_count": len(changed),
        "changed_entries": changed,
        "all_entry_crc_and_size_checks_passed": True,
        "all_unchanged_decoded_entries_identical": True,
    }

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=pathlib.Path)
    p.add_argument("candidate", type=pathlib.Path)
    p.add_argument("--expected-changed-path", default="Resources/HUD/debug.hud")
    p.add_argument("--expected-source-sha256")
    p.add_argument("--expected-candidate-sha256")
    p.add_argument("--report", type=pathlib.Path)
    p.add_argument("--overwrite-report", action="store_true")
    args = p.parse_args()
    try:
        report = verify_delta(args.source, args.candidate, args.expected_changed_path,
                              args.expected_source_sha256, args.expected_candidate_sha256)
        rendered = json.dumps(report, indent=2, ensure_ascii=True)
        if args.report:
            if args.report.exists() and not args.overwrite_report:
                raise ValueError(f"refusing to overwrite report: {args.report}")
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
        return 0
    except (OSError, ValueError) as exc:
        p.exit(2, f"FAIL: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Byte-level provenance checks for Deathforth source and overlay ZIPs; no APK build."""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

class ProvenanceAuditError(RuntimeError):
    pass

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def checked_zip(path: Path):
    if not path.is_file():
        raise ProvenanceAuditError(f"file not found: {path}")
    try:
        z = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        raise ProvenanceAuditError(f"invalid ZIP {path}: {e}") from e
    names = z.namelist()
    dups = sorted(n for n, count in Counter(names).items() if count > 1)
    if dups:
        z.close()
        raise ProvenanceAuditError(f"duplicate ZIP paths in {path.name}: {dups[:10]}")
    bad = z.testzip()
    if bad:
        z.close()
        raise ProvenanceAuditError(f"ZIP CRC failure in {path.name}: {bad}")
    return z, names

def infer_prefix(names: list[str], overlay: bool) -> str:
    roots = []
    marker = "assets/deathforth/"
    for name in names:
        i = name.find(marker)
        if i < 0:
            continue
        before = name[:i].replace("\\", "/")
        has_overlay = "overlay/" in before
        if has_overlay == overlay:
            roots.append(before + marker)
    if not roots:
        raise ProvenanceAuditError("cannot infer assets/deathforth path prefix")
    return Counter(roots).most_common(1)[0][0]

def safe_relative(raw: str, label: str) -> str:
    if "\\" in raw:
        raise ProvenanceAuditError(f"backslash path in {label}: {raw}")
    p = PurePosixPath(raw)
    if p.is_absolute() or not p.parts or any(x in ("", ".", "..") for x in p.parts) or ":" in p.parts[0]:
        raise ProvenanceAuditError(f"unsafe logical path in {label}: {raw}")
    return p.as_posix()

def index_df(z, names: list[str], prefix: str, label: str) -> dict[str, str]:
    result = {}
    for name in names:
        if name.endswith("/") or not name.startswith(prefix) or not name.endswith(".df"):
            continue
        logical = safe_relative(name[len(prefix):], label)
        if logical in result:
            raise ProvenanceAuditError(f"duplicate normalized path in {label}: {logical}")
        result[logical] = name
    if not result:
        raise ProvenanceAuditError(f"no .df scripts found in {label}")
    return result

def compare_archives(base_path: Path, overlay_path: Path, targets: list[str] | None = None) -> dict[str, Any]:
    bz, bn = checked_zip(base_path)
    oz, on = checked_zip(overlay_path)
    try:
        bp, op = infer_prefix(bn, False), infer_prefix(on, True)
        bi, oi = index_df(bz, bn, bp, base_path.name), index_df(oz, on, op, overlay_path.name)
        common = sorted(set(bi) & set(oi))
        identical, different = [], []
        for rel in common:
            (identical if bz.read(bi[rel]) == oz.read(oi[rel]) else different).append(rel)
        base_only, overlay_only = sorted(set(bi)-set(oi)), sorted(set(oi)-set(bi))
        checks = []
        for raw in targets or []:
            rel = safe_relative(raw, "target list")
            exists_b, exists_o = rel in bi, rel in oi
            same = bz.read(bi[rel]) == oz.read(oi[rel]) if exists_b and exists_o else None
            checks.append({"path": rel, "exists_in_base": exists_b, "exists_in_overlay": exists_o,
                           "byte_identical_to_base": same})
        return {
            "audit_kind": "byte-level source-overlay provenance comparison",
            "base": {"file": base_path.name, "bytes": base_path.stat().st_size,
                     "sha256": sha256_file(base_path), "zip_entries": len(bn),
                     "zip_crc": "PASS", "root_prefix": bp, "df_payloads": len(bi)},
            "overlay": {"file": overlay_path.name, "bytes": overlay_path.stat().st_size,
                        "sha256": sha256_file(overlay_path), "zip_entries": len(on),
                        "zip_crc": "PASS", "root_prefix": op, "df_payloads": len(oi)},
            "comparison": {"matching_paths_compared": len(common),
                           "byte_identical_to_base": len(identical),
                           "byte_different_from_base": len(different),
                           "base_scripts_without_overlay_payload": len(base_only),
                           "overlay_scripts_missing_from_base": len(overlay_only),
                           "byte_different_paths": different,
                           "base_only_paths": base_only, "overlay_only_paths": overlay_only},
            "target_script_checks": checks,
            "scope_limitations": [
                "A byte difference does not prove that all changes are translations.",
                "This does not fully parse Deathforth or test an APK/runtime.",
            ],
        }
    finally:
        bz.close()
        oz.close()

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", required=True, type=Path)
    p.add_argument("--overlay", required=True, type=Path)
    p.add_argument("--target", action="append", default=[])
    p.add_argument("--json-out", type=Path)
    a = p.parse_args()
    try:
        result = compare_archives(a.base, a.overlay, a.target)
    except ProvenanceAuditError as e:
        p.exit(2, f"ERROR: {e}\n")
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if a.json_out:
        a.json_out.parent.mkdir(parents=True, exist_ok=True)
        a.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

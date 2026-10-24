#!/usr/bin/env python3
"""Audit APK ZIP contents against a separately decoded AndroidManifest.xml.

Read-only. Does not extract assets, inspect secret values, or combine splits.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, zipfile
import xml.etree.ElementTree as ET
ANDROID = "http://schemas.android.com/apk/res/android"

def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def audit(apk: pathlib.Path, decoded_manifest: pathlib.Path) -> dict:
    root = ET.parse(decoded_manifest).getroot()
    with zipfile.ZipFile(apk) as zf:
        names = set(zf.namelist())
        native = sorted(n for n in names if n.startswith("lib/") and n.endswith(".so"))
        smf = zf.getinfo("assets/S3DMain.smf") if "assets/S3DMain.smf" in names else None
        secrets = sorted(n for n in names if pathlib.PurePosixPath(n).name.lower() in {"api_key.txt", "apikey.txt", "secrets.json"})
        app = root.find("application")
        return {
            "apk": {"name": apk.name, "size_bytes": apk.stat().st_size, "sha256": sha256_file(apk)},
            "package": root.attrib.get("package"),
            "version_name": root.attrib.get(f"{{{ANDROID}}}versionName"),
            "version_code": root.attrib.get(f"{{{ANDROID}}}versionCode"),
            "split_requirements": {
                "requiredSplitTypes": root.attrib.get("requiredSplitTypes"),
                "isSplitRequired": app.attrib.get(f"{{{ANDROID}}}isSplitRequired") if app is not None else None,
                "extractNativeLibs": app.attrib.get(f"{{{ANDROID}}}extractNativeLibs") if app is not None else None,
            },
            "archive": {
                "entry_count": len(names), "native_library_entry_count": len(native),
                "native_library_paths": native,
                "smf_entry": None if smf is None else {
                    "path": smf.filename, "compressed_size": smf.compress_size,
                    "uncompressed_size": smf.file_size, "zip_method": smf.compress_type,
                    "stored_without_zip_compression": smf.compress_type == zipfile.ZIP_STORED
                },
                "sensitive_asset_names_only": secrets
            },
            "interpretation": "No native entries plus required ABI/density split metadata suggests a base/split APK. Verify matching splits by package/version/signer/ABI. Sensitive asset paths are listed by name only; contents are never read."
        }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=pathlib.Path)
    parser.add_argument("decoded_manifest", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    result = audit(args.apk, args.decoded_manifest)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Static integrity checks for a DR2C VORENYX patch ZIP.

Usage:
  python verify_patch.py /path/to/DR2C_VORENYX_ID_v1.3_localization_patch.zip

This tool does not launch Death Road to Canada and cannot certify runtime compatibility.
"""
from __future__ import annotations
import argparse
import json
import sys
import zipfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("patch", type=Path)
    args = parser.parse_args()
    if not args.patch.is_file():
        print(json.dumps({"status": "FAIL", "error": "patch file not found"}))
        return 2
    try:
        with zipfile.ZipFile(args.patch) as archive:
            bad = archive.testzip()
            names = archive.namelist()
    except (OSError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 2
    report = {
        "status": "PASS" if bad is None else "FAIL",
        "zip_crc": "PASS" if bad is None else "FAIL",
        "bad_entry": bad,
        "entries": len(names),
        "runtime_gameplay_test": "NOT RUN",
        "save_load_test": "NOT RUN",
        "apk_rebuild": "NOT PERFORMED",
    }
    print(json.dumps(report, indent=2))
    return 0 if bad is None else 1


if __name__ == "__main__":
    raise SystemExit(main())

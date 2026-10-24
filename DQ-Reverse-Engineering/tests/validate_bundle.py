#!/usr/bin/env python3
"""Validate metadata and run the static Smali-like consistency checker."""
from pathlib import Path
import json, subprocess, sys, py_compile, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]

def main():
    ET.parse(ROOT / "manifest" / "AndroidManifest.xml")
    index = json.loads((ROOT / "disassembly" / "dex-index.json").read_text(encoding="utf-8"))
    probe = json.loads((ROOT / "docs" / "smf-probe-summary.json").read_text(encoding="utf-8"))
    split = json.loads((ROOT / "docs" / "apk-split-audit-summary.json").read_text(encoding="utf-8"))
    assert index["counts"]["emitted_classes"] == 68, index["counts"]
    assert probe["size_bytes"] == 33_978_539
    assert probe["sha256"] == "340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3"
    assert split["package"] == "com.shinybox.smash"
    assert split["split_requirements"]["requiredSplitTypes"] == "base__abi,base__density"
    assert split["archive"]["native_library_entry_count"] == 0
    prohibited = {"api_key.txt", "DQ.zip", "classes.dex", "S3DMain.smf"}
    unsafe = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and
              (p.name in prohibited or p.suffix.lower() == ".apk")]
    assert not unsafe, unsafe
    for py in ROOT.rglob("*.py"):
        py_compile.compile(str(py), doraise=True)
    result = subprocess.run([sys.executable, str(ROOT / "tests" / "validate_smali.py"),
                             "--root", str(ROOT / "disassembly")],
                            capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stdout + result.stderr)
    metrics = json.loads(result.stdout)
    assert (metrics["files"], metrics["methods"], metrics["instructions"],
            metrics["payloads"], metrics["errors"]) == (68, 405, 5187, 50, 0), metrics
    print("PASS: XML, DEX metadata, SMF fingerprint and APK split audit")
    print("PASS: 68 disassembly files; 405 methods; 5,187 instructions; 50 payloads")
    print("PASS: structural validation has zero errors")
    print("PASS: Python syntax and excluded binary/credential files")

if __name__ == "__main__":
    main()

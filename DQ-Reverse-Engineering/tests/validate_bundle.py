#!/usr/bin/env python3
"""Validate the generated Dungeon Quest reverse-engineering bundle."""
import json
import pathlib
import py_compile
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    ET.parse(ROOT / "manifest" / "AndroidManifest.xml")
    idx = json.loads((ROOT / "disassembly" / "dex-index.json").read_text(encoding="utf-8"))
    smf = json.loads((ROOT / "docs" / "smf-probe.json").read_text(encoding="utf-8"))
    assert idx["counts"]["emitted_classes"] == 68
    assert len(list((ROOT / "disassembly").rglob("*.smali"))) == 68
    assert smf["size_bytes"] == 33_978_539
    assert smf["sha256"] == "340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3"
    bad = [str(p) for p in ROOT.rglob("*") if p.is_file() and (p.name == "api_key.txt" or p.suffix.lower() == ".apk" or p.name == "DQ.zip")]
    assert not bad, bad
    for p in ROOT.rglob("*.py"):
        py_compile.compile(str(p), doraise=True)
    print("PASS: XML, JSON metadata, 68 disassembly files, SMF fingerprint, secret exclusion, Python syntax")

if __name__ == "__main__":
    main()

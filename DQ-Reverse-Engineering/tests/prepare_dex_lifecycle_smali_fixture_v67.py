#!/usr/bin/env python3
"""Build a temporary synthetic smali overlay for assembler validation in CI."""
import hashlib
import pathlib
import sys
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import patch_dex_lifecycle_smali_v67 as patcher


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: prepare_dex_lifecycle_smali_fixture_v67.py OUTPUT_ROOT")
    output = pathlib.Path(sys.argv[1]).resolve()
    source = ROOT / "tests" / "fixtures" / "dex_lifecycle_hook_v67"
    synthetic_dex = output.parent / "synthetic-classes-v67.dex"
    synthetic_dex.write_bytes(b"DQ v67 synthetic identity fixture; not executable DEX\n")
    digest = hashlib.sha256(synthetic_dex.read_bytes()).hexdigest()
    renderer = source / patcher.RENDERER
    renderer_digest = hashlib.sha256(renderer.read_bytes()).hexdigest()
    # The synthetic fixture uses its own pinned identity, never the stock game's hash.
    with mock.patch.object(patcher, "PINNED_DEX_SHA256", digest), mock.patch.object(
        patcher, "PINNED_RENDERER_SMALI_SHA256", renderer_digest
    ):
        report = patcher.create_overlay(source, output, synthetic_dex)
    print("Prepared synthetic smali overlay; no game DEX/APK.")
    print("Patched renderer SHA-256:", report["patched_renderer_sha256"])


if __name__ == "__main__":
    main()

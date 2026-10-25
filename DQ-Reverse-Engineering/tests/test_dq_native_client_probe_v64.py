#!/usr/bin/env python3
"""Manifest boundary tests for the v64 source-only native-client probe."""
from __future__ import annotations
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_dq_native_client_probe_v64 import ManifestError, validate

REPORT = ROOT / "docs" / "DQ_NATIVE_CLIENT_PROBE_V64.json"


class NativeClientProbeManifestV64Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_canonical_manifest_passes_with_no_game_side_effects(self):
        result = validate(copy.deepcopy(self.base))
        self.assertFalse(result["real_game_invocation"])
        self.assertEqual(result["output"], 42)

    def test_probe_cannot_be_given_gameplay_side_effects(self):
        data = copy.deepcopy(self.base)
        data["probe_contract"]["side_effects"] = "RewardGold(100000)"
        with self.assertRaisesRegex(ManifestError, "side-effect-free"):
            validate(data)

    def test_actual_hud_callsite_cannot_be_claimed(self):
        data = copy.deepcopy(self.base)
        data["implementation"]["actual_HUD_AIM_callsite_added"] = True
        with self.assertRaisesRegex(ManifestError, "actual_HUD_AIM_callsite_added"):
            validate(data)

    def test_apk_build_cannot_be_claimed(self):
        data = copy.deepcopy(self.base)
        data["implementation"]["APK_or_XAPK_built"] = True
        with self.assertRaisesRegex(ManifestError, "APK_or_XAPK_built"):
            validate(data)

    def test_catalog_routes_remain_zero(self):
        data = copy.deepcopy(self.base)
        data["gameplay_integration"]["catalog_routes_assigned"] = 1
        with self.assertRaisesRegex(ManifestError, "must not promote"):
            validate(data)

    def test_runtime_gate_remains_blocked(self):
        data = copy.deepcopy(self.base)
        data["gameplay_integration"]["v50_runtime_checks_passed"] = 9
        with self.assertRaisesRegex(ManifestError, "runtime gate"):
            validate(data)


if __name__ == "__main__":
    unittest.main(verbosity=2)

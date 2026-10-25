#!/usr/bin/env python3
"""Fail-closed tests for the v67 source-only smali lifecycle patcher."""
import hashlib
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from patch_dex_lifecycle_smali_v67 import (
    PatchError, PROBE_SMALI, RENDERER, PROBE, create_overlay, patch_renderer,
)

FIXTURE = ROOT / "tests" / "fixtures" / "dex_lifecycle_hook_v67"


class PatchDexLifecycleV67Tests(unittest.TestCase):
    def setUp(self):
        self.source = (FIXTURE / RENDERER).read_text(encoding="utf-8")

    def test_success_gate_preserves_flag_and_unregisters_before_both_shutdowns(self):
        patched, report = patch_renderer(self.source)
        draw = patched.split(".method public onDrawFrame(", 1)[1].split(".end method", 1)[0]
        init = draw.index("->engineInitialize()Z")
        self.assertIn("move-result v1", draw[init:])
        self.assertIn("if-eqz v1, :dq_probe_init_skip_v67", draw[init:])
        self.assertIn("->tryRegisterAndRoundTrip()V", draw[init:])
        self.assertIn("const/4 v1, 0x1", draw[init:])
        self.assertLess(draw.index("->tryUnregister()V"), draw.index("->engineShutdown()V"))
        shut = patched.split(".method public onShutdown()V", 1)[1].split(".end method", 1)[0]
        self.assertLess(shut.index("->tryUnregister()V"), shut.index("->engineShutdown()V"))
        self.assertTrue(report["probe_only_on_true_result"])
        self.assertTrue(report["original_initialized_flag_semantics_preserved"])
        self.assertFalse(report["runtime_verified_catalog_effects"])

    def test_bad_init_shape_fails_closed(self):
        changed = self.source.replace("iput-boolean v1, p0,", "nop")
        with self.assertRaisesRegex(PatchError, "init shape changed"):
            patch_renderer(changed)

    def test_duplicate_init_call_fails_closed(self):
        target = "invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineInitialize()Z"
        changed = self.source.replace(target, target + "\n    " + target)
        with self.assertRaisesRegex(PatchError, "exactly one engineInitialize"):
            patch_renderer(changed)

    def test_double_patch_fails_closed(self):
        with self.assertRaisesRegex(PatchError, "already references"):
            patch_renderer(self.source + "\n# Lcom/shinybox/smash/DqNativeProbe;->alreadyPatched")

    def test_probe_helper_is_lazy_and_side_effect_free(self):
        self.assertNotIn("<clinit>", PROBE_SMALI)
        self.assertIn('System;->loadLibrary', PROBE_SMALI)
        self.assertIn("nativeRegisterProbe()Z", PROBE_SMALI)
        self.assertIn("nativeInvokeProbe()Z", PROBE_SMALI)
        self.assertIn("nativeUnregisterProbe()Z", PROBE_SMALI)
        self.assertIn(".catch Ljava/lang/Throwable;", PROBE_SMALI)

    def test_overlay_does_not_mutate_input_and_writes_separate_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            source_root = root / "source"
            shutil.copytree(FIXTURE, source_root)
            source_bytes = (source_root / RENDERER).read_bytes()
            dex = root / "classes.dex"
            dex.write_bytes(b"synthetic identity fixture")
            out = root / "overlay"
            with mock.patch("patch_dex_lifecycle_smali_v67.PINNED_DEX_SHA256",
                            hashlib.sha256(dex.read_bytes()).hexdigest()):
                report = create_overlay(source_root, out, dex)
            self.assertEqual((source_root / RENDERER).read_bytes(), source_bytes)
            self.assertTrue((out / PROBE).is_file())
            self.assertTrue((out / "dq-lifecycle-smali-patch-v67.json").is_file())
            self.assertTrue(report["apk_or_dex_bytes_written"] is False)

    def test_overlay_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            source_root = root / "source"
            shutil.copytree(FIXTURE, source_root)
            dex = root / "classes.dex"
            dex.write_bytes(b"synthetic identity fixture")
            out = root / "overlay"
            out.mkdir()
            with mock.patch("patch_dex_lifecycle_smali_v67.PINNED_DEX_SHA256",
                            hashlib.sha256(dex.read_bytes()).hexdigest()):
                with self.assertRaisesRegex(PatchError, "refusing overwrite"):
                    create_overlay(source_root, out, dex)

    def test_wrong_dex_hash_fails_before_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            source_root = root / "source"
            shutil.copytree(FIXTURE, source_root)
            dex = root / "classes.dex"
            dex.write_bytes(b"wrong build")
            out = root / "overlay"
            with self.assertRaisesRegex(PatchError, "source DEX hash mismatch"):
                create_overlay(source_root, out, dex)
            self.assertFalse(out.exists())

    def test_source_method_and_probe_routes_are_pinned(self):
        self.assertIn("onDrawFrame(Ljavax/microedition/khronos/opengles/GL10;)V", self.source)
        self.assertIn("onShutdown()V", self.source)
        patched, _ = patch_renderer(self.source)
        self.assertEqual(patched.count("->tryUnregister()V"), 2)
        self.assertEqual(patched.count("->tryRegisterAndRoundTrip()V"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

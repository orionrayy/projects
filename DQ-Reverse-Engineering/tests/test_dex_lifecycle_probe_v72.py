#!/usr/bin/env python3
"""Regression tests for the v72 Logcat-observable smali overlay."""
from __future__ import annotations
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import patch_dex_lifecycle_smali_v72 as patcher

class ProbeV72Tests(unittest.TestCase):
    def test_probe_has_explicit_pass_fail_and_exception_markers(self):
        source = patcher.PROBE_SMALI
        for marker in (
            "library_load=PASS", "library_load=FAIL",
            "callback_register=PASS", "callback_register=FAIL",
            "callback_roundtrip=PASS", "callback_roundtrip=FAIL",
            "callback_unregister=PASS", "callback_unregister=FAIL",
            "callback_probe=EXCEPTION", "callback_unregister=EXCEPTION",
            "callback_unregister=SKIP", "DQv72Probe",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)
        self.assertIn("Landroid/util/Log;->i", source)
        self.assertIn("Landroid/util/Log;->e", source)
        self.assertIn(".catch Ljava/lang/Throwable;", source)

    def test_roundtrip_marker_is_emitted_only_on_success_branch(self):
        source = patcher.PROBE_SMALI
        branch = source.index("if-eqz v0, :probe_invoke_false")
        passed = source.index('const-string v1, "callback_roundtrip=PASS"')
        failed = source.index('const-string v1, "callback_roundtrip=FAIL"')
        self.assertLess(branch, passed)
        self.assertLess(passed, failed)

    def test_lifecycle_hooks_are_gated_and_precede_shutdown(self):
        renderer = """.class public Lcom/shinybox/smash/S3DRenderer;
.super Ljava/lang/Object;
.method public onDrawFrame(Ljavax/microedition/khronos/opengles/GL10;)V
    .locals 1
    invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineShutdown()V
    invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineInitialize()Z
    iput-boolean v0, p0, Lcom/shinybox/smash/S3DRenderer;->bInitialized:Z
    return-void
.end method
.method public onShutdown()V
    .locals 0
    invoke-virtual {p0}, Lcom/shinybox/smash/S3DRenderer;->engineShutdown()V
    return-void
.end method
"""
        patched, report = patcher.patch_renderer(renderer)
        self.assertIn("if-eqz v0, :dq_probe_init_skip_v67", patched)
        self.assertIn("invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->tryRegisterAndRoundTrip()V", patched)
        self.assertTrue(report["unregister_before_shutdown"])
        for method in ("onDrawFrame", "onShutdown"):
            block = patched.split(".method public " + method, 1)[1].split(".end method", 1)[0]
            self.assertLess(block.index("tryUnregister()V"), block.index("engineShutdown()V"))
        self.assertEqual(report["runtime_status"], "NOT_VERIFIED")

    def test_input_with_existing_probe_is_rejected(self):
        source = """.class public Lcom/shinybox/smash/S3DRenderer;
invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->tryUnregister()V
"""
        with self.assertRaisesRegex(patcher.PatchError, "already references"):
            patcher.patch_renderer(source)

if __name__ == "__main__":
    unittest.main(verbosity=2)

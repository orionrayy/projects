#!/usr/bin/env python3
"""Fail-closed tests for the v50 game-candidate runtime evidence gate."""
from __future__ import annotations
import hashlib
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_game_candidate_runtime_evidence_v55 import (
    CHECKS, EXPECTED_CANDIDATE, REQUIRED_VERIFIED_EVIDENCE,
    SCHEMA, validate_document,
)


def blocked_doc():
    return {
        "schema": SCHEMA,
        "status": "blocked",
        "candidate": dict(EXPECTED_CANDIDATE),
        "device": {"platform": "not_run", "model": None, "api_level": None,
                   "profile": "not_run", "offline_confirmed": False,
                   "backup_restore_verified": False},
        "checks": {key: "not_run" for key in CHECKS},
        "observations": {"gold_before": None, "gold_after": None,
                         "gold_after_reload": None, "crash_count": None},
        "evidence": [],
    }


def add_evidence(doc, root, kind, name):
    payload = ("test evidence: " + kind).encode()
    (root / name).write_bytes(payload)
    doc["evidence"].append({"kind": kind, "path": name,
                            "sha256": hashlib.sha256(payload).hexdigest()})


class RuntimeEvidenceV55Tests(unittest.TestCase):
    def test_baseline_is_valid_but_not_promotable(self):
        with tempfile.TemporaryDirectory() as td:
            doc = blocked_doc()
            self.assertEqual(validate_document(doc, pathlib.Path(td)), [])
            self.assertEqual(doc["status"], "blocked")

    def test_wrong_candidate_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            doc = blocked_doc()
            doc["candidate"]["apk_sha256"] = "0" * 64
            self.assertTrue(any("candidate identity/hashes" in e for e in validate_document(doc, pathlib.Path(td))))

    def test_pass_requires_matching_evidence_and_exact_delta(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            doc = blocked_doc()
            doc["status"] = "in_progress"
            doc["checks"]["exact_gold_delta"] = "pass"
            doc["device"].update({"platform": "emulator", "model": "test-emulator",
                                  "api_level": 28, "profile": "disposable_offline",
                                  "offline_confirmed": True, "backup_restore_verified": True})
            doc["observations"].update({"gold_before": 20, "gold_after": 100020})
            self.assertTrue(any("requires evidence kind gold_delta" in e for e in validate_document(doc, root)))
            add_evidence(doc, root, "gold_delta", "delta.txt")
            add_evidence(doc, root, "offline_state", "offline.txt")
            add_evidence(doc, root, "backup_restore", "backup.txt")
            self.assertEqual(validate_document(doc, root), [])
            doc["observations"]["gold_after"] = 100019
            self.assertTrue(any("exactly +100000" in e for e in validate_document(doc, root)))

    def test_verified_requires_every_gate_and_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            doc = blocked_doc()
            doc["status"] = "verified"
            doc["device"].update({"platform": "emulator", "model": "test-emulator",
                                  "api_level": 28, "profile": "disposable_offline",
                                  "offline_confirmed": True, "backup_restore_verified": True})
            doc["checks"] = {key: "pass" for key in CHECKS}
            doc["observations"].update({"gold_before": 5, "gold_after": 100005,
                                         "gold_after_reload": 100005, "crash_count": 0})
            for i, kind in enumerate(sorted(REQUIRED_VERIFIED_EVIDENCE)):
                add_evidence(doc, root, kind, f"evidence-{i}.txt")
            self.assertEqual(validate_document(doc, root), [])
            doc["observations"]["gold_after_reload"] = 100004
            self.assertTrue(any("persist exactly" in e for e in validate_document(doc, root)))

    def test_evidence_path_traversal_and_missing_file_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            doc = blocked_doc()
            doc["status"] = "in_progress"
            doc["checks"]["launch"] = "pass"
            doc["evidence"] = [{"kind": "launch_screen", "path": "../outside.png", "sha256": "0" * 64}]
            errs = validate_document(doc, root)
            self.assertTrue(any("cannot traverse" in e for e in errs))
            doc["evidence"] = [{"kind": "launch_screen", "path": "missing.png", "sha256": "0" * 64}]
            self.assertTrue(any("missing" in e for e in validate_document(doc, root)))

    def test_failed_state_requires_explicit_failure_and_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            doc = blocked_doc()
            doc["status"] = "failed"
            self.assertTrue(any("requires at least one failed check" in e for e in validate_document(doc, pathlib.Path(td))))
            doc["checks"]["launch"] = "fail"
            self.assertTrue(any("requires evidence kind launch_screen" in e for e in validate_document(doc, pathlib.Path(td))))

if __name__ == "__main__":
    unittest.main(verbosity=2)

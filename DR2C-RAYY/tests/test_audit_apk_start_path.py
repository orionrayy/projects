from __future__ import annotations
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_apk_start_path import ROUTE_FILES, audit, code_delta


class ApkStartPathAuditTests(unittest.TestCase):
    def base_entries(self):
        out = {path: b': placeholder "Base text" print ;\n' for path in ROUTE_FILES}
        out["assets/deathforth/boot.df"] = b': boot "GAME-MARKER" $anew "READY." print ;\n'
        out["assets/deathforth/events.df"] = b"defer main-event-do-select ;\n"
        out["assets/deathforth/game-select.df"] = b": select-start ;\n: select-boot 'main-event-do-select ;\n"
        out["assets/deathforth/game-start.df"] = b": game-start-new ;\n"
        out["assets/deathforth/events/tutorial.df"] = (
            b'cyoa-choice: tutorchat-1 ;\ncyoa-choice: tutorchat-2 ;\n'
            b'cyoa-choice: tutorchat-3 ;\n: demo ( pname .. " sees " .. chim ) ;\n'
        )
        return out

    def write_zip(self, path, entries, duplicate=False):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
            if duplicate:
                archive.writestr("assets/deathforth/events/tutorial.df", entries["assets/deathforth/events/tutorial.df"])

    def make_apks(self, base_path, candidate_path, transform=None):
        entries = self.base_entries()
        self.write_zip(base_path, entries)
        candidate = {path: data.replace(b"Base text", b"Teks ID") for path, data in entries.items()}
        if transform:
            transform(candidate)
        self.write_zip(candidate_path, candidate)

    def test_presentation_only_translation_passes(self):
        with tempfile.TemporaryDirectory() as td:
            base, candidate = Path(td) / "base.apk", Path(td) / "candidate.apk"
            self.make_apks(base, candidate)
            report = audit(base, candidate)
            self.assertTrue(report["summary"]["overall_static_gate_pass"])
            self.assertEqual(report["summary"]["route_files_static_pass"], len(ROUTE_FILES))

    def test_tutorial_dynamic_identifier_drift_is_review_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            base, candidate = Path(td) / "base.apk", Path(td) / "candidate.apk"
            def transform(entries):
                path = "assets/deathforth/events/tutorial.df"
                entries[path] = entries[path].replace(b".. chim", b".. cname")
            self.make_apks(base, candidate, transform)
            report = audit(base, candidate)
            self.assertFalse(report["summary"]["overall_static_gate_pass"])
            row = next(item for item in report["route_files"] if item["path"].endswith("events/tutorial.df"))
            self.assertEqual(row["status"], "REVIEW_CODE_DRIFT")
            flattened = [token for group in row["code_token_delta"]
                         for token in group["base_tokens"] + group["candidate_tokens"]]
            self.assertIn("chim", flattened)
            self.assertIn("cname", flattened)

    def test_required_handler_loss_fails(self):
        with tempfile.TemporaryDirectory() as td:
            base, candidate = Path(td) / "base.apk", Path(td) / "candidate.apk"
            def transform(entries):
                path = "assets/deathforth/game-select.df"
                entries[path] = entries[path].replace(b"select-start", b"start-other")
            self.make_apks(base, candidate, transform)
            report = audit(base, candidate)
            self.assertFalse(report["summary"]["overall_static_gate_pass"])
            row = next(item for item in report["route_files"] if item["path"].endswith("game-select.df"))
            self.assertFalse(row["required_tokens"]["select-start"])

    def test_missing_route_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base, candidate = Path(td) / "base.apk", Path(td) / "candidate.apk"
            entries = self.base_entries()
            self.write_zip(base, entries)
            entries.pop("assets/deathforth/game-select.df")
            self.write_zip(candidate, entries)
            report = audit(base, candidate)
            self.assertFalse(report["summary"]["overall_static_gate_pass"])
            row = next(item for item in report["route_files"] if item["path"].endswith("game-select.df"))
            self.assertEqual(row["status"], "FAIL_MISSING_ROUTE")

    def test_duplicate_zip_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            base, candidate = Path(td) / "base.apk", Path(td) / "candidate.apk"
            entries = self.base_entries()
            self.write_zip(base, entries)
            self.write_zip(candidate, entries, duplicate=True)
            with self.assertRaises(ValueError):
                audit(base, candidate)

    def test_token_delta_ignores_text_but_detects_code_identifier(self):
        self.assertTrue(code_delta('pname .. "hello" .. chim', 'pname .. "halo" .. chim')["normalized_code_tokens_match"])
        self.assertFalse(code_delta('pname .. "hello" .. chim', 'pname .. "halo" .. cname')["normalized_code_tokens_match"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

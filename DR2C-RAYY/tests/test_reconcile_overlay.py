from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from reconcile_overlay import ReconcileError, reconcile, safe_path


class ReconcileOverlayTests(unittest.TestCase):
    def write_zip(self, path: Path, entries: dict[str, bytes]) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries.items():
                archive.writestr(name, data)

    def base_entries(self, common4: bytes = b": sample 'original-handler \"hello\" ;\n") -> dict[str, bytes]:
        return {
            "GAME/assets/deathforth/boot.df": b'"GAME-MARKER" $anew\n',
            "GAME/assets/deathforth/events/common/common4.df": common4,
            "GAME/assets/deathforth/events.df": b"main-event-do-select\n",
            "GAME/assets/deathforth/game-select.df": b"main-event-do-select select-start select-boot\n",
            "GAME/assets/deathforth/events/tutorial.df": b"tutorchat-1\n",
            "GAME/assets/deathforth/perkdef.df": b'"Jack of All Trades" $perk\n',
        }

    def test_safe_paths_reject_parent_traversal(self) -> None:
        with self.assertRaises(ReconcileError):
            safe_path("assets/../../oops.df", "bad.zip")
        with self.assertRaises(ReconcileError):
            safe_path("C:/temp/oops.df", "bad.zip")
        with self.assertRaises(ReconcileError):
            safe_path(r"assets\deathforth\boot.df", "bad.zip")

    def test_layered_patch_reconciliation_records_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = root / "base.zip"
            p1 = root / "p1.zip"
            p2 = root / "p2.zip"
            out = root / "out.zip"
            report = root / "report.json"
            self.write_zip(base, self.base_entries())
            self.write_zip(p1, {
                "p1/overlay/assets/deathforth/boot.df": b'"GAME-MARKER" $anew\n',
                "p1/overlay/assets/deathforth/events/common/common4.df": b': sample \'original-handler "hello \\"world\\"" ;\n',
            })
            self.write_zip(p2, {
                "overlay/assets/deathforth/events/common/common4.df": b': sample \'original-handler "hello world" ;\n',
            })
            result = reconcile(base, [p1, p2], out, report)
            self.assertEqual(result["final_overlay"]["unique_paths"], 2)
            self.assertIn("assets/deathforth/events/common/common4.df", result["final_overlay"]["override_history"])
            self.assertEqual(result["checks"]["single_quoted_code_symbol_sequences_preserved"], "PASS")
            with zipfile.ZipFile(out) as archive:
                self.assertEqual(archive.read("overlay/assets/deathforth/events/common/common4.df"), b': sample \'original-handler "hello world" ;\n')
                self.assertIsNone(archive.testzip())
            self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["output"]["zip_crc"], "PASS")

    def test_reconciliation_archive_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = root / "base.zip"
            patch = root / "patch.zip"
            out_a = root / "out-a.zip"
            out_b = root / "out-b.zip"
            report_a = root / "report-a.json"
            report_b = root / "report-b.json"
            self.write_zip(base, self.base_entries())
            self.write_zip(patch, {
                "overlay/assets/deathforth/boot.df": b'"GAME-MARKER" $anew\\n',
                "overlay/assets/deathforth/events/common/common4.df": b': sample \'original-handler "hello" ;\\n',
            })
            result_a = reconcile(base, [patch], out_a, report_a)
            result_b = reconcile(base, [patch], out_b, report_b)
            self.assertEqual(result_a["output"]["sha256"], result_b["output"]["sha256"])
            self.assertEqual(out_a.read_bytes(), out_b.read_bytes())
            with zipfile.ZipFile(out_a) as archive:
                self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist()))

    def test_wrong_expected_base_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = root / "base.zip"
            patch = root / "patch.zip"
            self.write_zip(base, {"G/assets/deathforth/boot.df": b'"GAME-MARKER" $anew'})
            self.write_zip(patch, {"overlay/assets/deathforth/boot.df": b'"GAME-MARKER" $anew'})
            with self.assertRaises(ReconcileError):
                reconcile(base, [patch], root / "out.zip", root / "report.json", "0" * 64)

    def test_missing_deathforth_source_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = root / "base.zip"
            patch = root / "patch.zip"
            self.write_zip(base, {"G/assets/deathforth/boot.df": b'"GAME-MARKER" $anew'})
            self.write_zip(patch, {"overlay/assets/deathforth/not-present.df": b'"x"'})
            with self.assertRaises(ReconcileError):
                reconcile(base, [patch], root / "out.zip", root / "report.json")

    def test_unclosed_display_string_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = root / "base.zip"
            patch = root / "patch.zip"
            self.write_zip(base, self.base_entries())
            self.write_zip(patch, {"overlay/assets/deathforth/events/common/common4.df": b': broken "unclosed\n'})
            with self.assertRaisesRegex(ReconcileError, "unclosed display string"):
                reconcile(base, [patch], root / "out.zip", root / "report.json")

    def test_single_quoted_code_symbol_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = root / "base.zip"
            patch = root / "patch.zip"
            self.write_zip(base, self.base_entries())
            self.write_zip(patch, {"overlay/assets/deathforth/events/common/common4.df": b': sample \'wrong-handler "hello" ;\n'})
            with self.assertRaisesRegex(ReconcileError, "single-quoted code-symbol sequence"):
                reconcile(base, [patch], root / "out.zip", root / "report.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)

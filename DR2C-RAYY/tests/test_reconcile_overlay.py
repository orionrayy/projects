from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from reconcile_overlay import ReconcileError, reconcile, safe_path


class ReconcileOverlayTests(unittest.TestCase):
    def write_zip(self, path: Path, entries: dict[str, bytes]) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries.items():
                archive.writestr(name, data)

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
            self.write_zip(base, {
                "GAME/assets/deathforth/boot.df": b'"GAME-MARKER" $anew\n',
                "GAME/assets/deathforth/events/common/common4.df": b'"hello"\n',
            })
            self.write_zip(p1, {
                "p1/overlay/assets/deathforth/boot.df": b'"GAME-MARKER" $anew\n',
                "p1/overlay/assets/deathforth/events/common/common4.df": b'"hello \\"world\\""\n',
            })
            self.write_zip(p2, {
                "overlay/assets/deathforth/events/common/common4.df": b'"hello world"\n',
            })
            result = reconcile(base, [p1, p2], out, report)
            self.assertEqual(result["final_overlay"]["unique_paths"], 2)
            self.assertIn("assets/deathforth/events/common/common4.df", result["final_overlay"]["override_history"])
            with zipfile.ZipFile(out) as archive:
                self.assertEqual(archive.read("overlay/assets/deathforth/events/common/common4.df"), b'"hello world"\n')
                self.assertIsNone(archive.testzip())
            self.assertEqual(json.loads(report.read_text(encoding="utf-8"))["output"]["zip_crc"], "PASS")

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


if __name__ == "__main__":
    unittest.main(verbosity=2)

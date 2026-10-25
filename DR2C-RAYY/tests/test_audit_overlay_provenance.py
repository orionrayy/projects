from __future__ import annotations
import sys, tempfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_overlay_provenance import ProvenanceAuditError, compare_archives

class ProvenanceAuditTests(unittest.TestCase):
    def write_zip(self, path: Path, items: dict[str, bytes]):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name, data in items.items():
                z.writestr(name, data)

    def test_counts_and_target_script_differences(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base, overlay = root/"base.zip", root/"overlay.zip"
            self.write_zip(base, {
                "GAME/assets/deathforth/boot.df": b"boot\n",
                "GAME/assets/deathforth/events/a.df": b"old\n",
                "GAME/assets/deathforth/events/missing.df": b"x\n",
            })
            self.write_zip(overlay, {
                "PATCH/overlay/assets/deathforth/boot.df": b"boot\n",
                "PATCH/overlay/assets/deathforth/events/a.df": b"new\n",
                "PATCH/overlay/assets/deathforth/events/extra.df": b"extra\n",
            })
            r = compare_archives(base, overlay, ["boot.df", "events/a.df", "events/missing.df", "events/extra.df"])
            self.assertEqual(r["comparison"]["matching_paths_compared"], 2)
            self.assertEqual(r["comparison"]["byte_identical_to_base"], 1)
            self.assertEqual(r["comparison"]["byte_different_from_base"], 1)
            self.assertEqual(r["comparison"]["base_scripts_without_overlay_payload"], 1)
            self.assertEqual(r["comparison"]["overlay_scripts_missing_from_base"], 1)
            checks = {x["path"]: x for x in r["target_script_checks"]}
            self.assertTrue(checks["boot.df"]["byte_identical_to_base"])
            self.assertFalse(checks["events/a.df"]["byte_identical_to_base"])
            self.assertFalse(checks["events/missing.df"]["exists_in_overlay"])
            self.assertTrue(checks["events/extra.df"]["exists_in_overlay"])

    def test_duplicate_zip_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base, overlay = root/"base.zip", root/"overlay.zip"
            self.write_zip(base, {"GAME/assets/deathforth/boot.df": b"x"})
            with zipfile.ZipFile(overlay, "w") as z:
                z.writestr("P/overlay/assets/deathforth/boot.df", b"x")
                z.writestr("P/overlay/assets/deathforth/boot.df", b"y")
            with self.assertRaisesRegex(ProvenanceAuditError, "duplicate ZIP paths"):
                compare_archives(base, overlay)

    def test_unsafe_logical_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base, overlay = root/"base.zip", root/"overlay.zip"
            self.write_zip(base, {"GAME/assets/deathforth/boot.df": b"x"})
            self.write_zip(overlay, {"P/overlay/assets/deathforth/../evil.df": b"x"})
            with self.assertRaisesRegex(ProvenanceAuditError, "unsafe or noncanonical logical path"):
                compare_archives(base, overlay)

    def test_ambiguous_source_roots_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base, overlay = root/"base.zip", root/"overlay.zip"
            self.write_zip(base, {
                "GAME/assets/deathforth/boot.df": b"x",
                "OTHER/assets/deathforth/rogue.df": b"y",
            })
            self.write_zip(overlay, {"P/overlay/assets/deathforth/boot.df": b"x"})
            with self.assertRaisesRegex(ProvenanceAuditError, "ambiguous assets/deathforth path prefixes"):
                compare_archives(base, overlay)

    def test_noncanonical_dot_segment_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base, overlay = root/"base.zip", root/"overlay.zip"
            self.write_zip(base, {"GAME/assets/deathforth/boot.df": b"x"})
            self.write_zip(overlay, {"P/overlay/assets/deathforth/events/./evil.df": b"x"})
            with self.assertRaisesRegex(ProvenanceAuditError, "unsafe or noncanonical logical path"):
                compare_archives(base, overlay)

    def test_missing_archive_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ProvenanceAuditError, "file not found"):
                compare_archives(root/"missing.zip", root/"overlay.zip")

if __name__ == "__main__":
    unittest.main(verbosity=2)

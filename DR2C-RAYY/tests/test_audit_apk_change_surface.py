from __future__ import annotations
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_apk_change_surface import audit


class ApkChangeSurfaceTests(unittest.TestCase):
    def write_zip(self, path: Path, files: dict[str, bytes]):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in files.items():
                z.writestr(name, data)

    def test_expected_script_manifest_and_ascii_label_changes_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.apk"; cand=root/"candidate.apk"
            self.write_zip(base, {
                "classes.dex": b"dex-same",
                "AndroidManifest.xml": b"manifest-a",
                "META-INF/MANIFEST.MF": b"old-signature-meta",
                "lib/arm64-v8a/libmain.so": b"\0strength\0other\0",
                "lib/armeabi-v7a/libmain.so": b"\0strength\0other\0",
                "assets/deathforth/game-select.df": b'"Start" print ;\n',
                "META-INF/CERT.RSA": b"old-rsa",
                "META-INF/CERT.SF": b"old-sf",
            })
            self.write_zip(cand, {
                "classes.dex": b"dex-same",
                "AndroidManifest.xml": b"manifest-b",
                "META-INF/MANIFEST.MF": b"signature meta",
                "META-INF/DR2C-VOR.RSA": b"new-rsa",
                "META-INF/DR2C-VOR.SF": b"new-sf",
                "lib/arm64-v8a/libmain.so": b"\0kekuatan\0other\0",
                "lib/armeabi-v7a/libmain.so": b"\0kekuatan\0other\0",
                "assets/deathforth/game-select.df": b'"Mulai" print ;\n',
                "assets/gfx/ui/vorenyx_title_screen.png": b"art",
            })
            result=audit(base,cand)
            self.assertTrue(result["summary"]["overall_static_package_diff_pass"])
            self.assertTrue(result["summary"]["dex_byte_identical"])
            self.assertEqual(result["summary"]["changed_deathforth_script_count"],1)

    def test_dex_change_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.apk"; cand=root/"candidate.apk"
            self.write_zip(base,{"classes.dex":b"original"})
            self.write_zip(cand,{"classes.dex":b"changed"})
            result=audit(base,cand)
            self.assertFalse(result["summary"]["dex_byte_identical"])
            self.assertFalse(result["summary"]["overall_static_package_diff_pass"])

    def test_non_ascii_native_change_is_reviewed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.apk"; cand=root/"candidate.apk"
            self.write_zip(base,{"lib/arm64-v8a/libmain.so":b"\0strength\0"})
            self.write_zip(cand,{"lib/arm64-v8a/libmain.so":b"\0strengt\x01\0"})
            result=audit(base,cand)
            self.assertFalse(result["summary"]["libmain_string_slot_only_changes"])
            self.assertFalse(result["summary"]["overall_static_package_diff_pass"])

    def test_unexpected_added_path_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.apk"; cand=root/"candidate.apk"
            self.write_zip(base,{"classes.dex":b"same"})
            self.write_zip(cand,{"classes.dex":b"same","unexpected.bin":b"extra"})
            result=audit(base,cand)
            self.assertFalse(result["entry_surface"]["entry_add_remove_matches_expected"])
            self.assertFalse(result["summary"]["overall_static_package_diff_pass"])

    def test_duplicate_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); base=root/"base.apk"; cand=root/"candidate.apk"
            with zipfile.ZipFile(base,"w") as z:
                z.writestr("classes.dex",b"a")
            with zipfile.ZipFile(cand,"w") as z:
                z.writestr("classes.dex",b"a")
                z.writestr("classes.dex",b"a")
            with self.assertRaises(ValueError):
                audit(base,cand)


if __name__ == "__main__":
    unittest.main(verbosity=2)

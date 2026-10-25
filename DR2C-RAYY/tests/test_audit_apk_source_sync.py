from __future__ import annotations
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_apk_source_sync import audit


class ApkSourceSyncTests(unittest.TestCase):
    def create_zip(self, path: Path, entries: dict[str, bytes], duplicate: bool = False):
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
            if duplicate:
                name = next(iter(entries))
                archive.writestr(name, entries[name])

    def fixture(self, root: Path):
        source = root / "source.zip"
        base_apk = root / "base.apk"
        candidate = root / "candidate.apk"
        layer1 = root / "layer1.zip"
        layer2 = root / "layer2.zip"
        base_payloads = {
            "ASSET/DR2C-RAYY/assets/deathforth/boot.df": b'"GAME-MARKER" $anew\n"READY." print\n',
            "ASSET/DR2C-RAYY/assets/deathforth/events/tutorial.df": b': tutorial "Base text" print ;\n',
        }
        apk_payloads = {key.split("DR2C-RAYY/", 1)[1]: value for key, value in base_payloads.items()}
        self.create_zip(source, base_payloads)
        self.create_zip(base_apk, apk_payloads)
        l1 = {"PATCH/overlay/assets/deathforth/events/tutorial.df": b': tutorial "Terjemahan A" print ;\n'}
        l2 = {"overlay/assets/deathforth/events/tutorial.df": b': tutorial "Terjemahan B" print ;\n'}
        self.create_zip(layer1, l1)
        self.create_zip(layer2, l2)
        candidate_payloads = {
            "assets/deathforth/boot.df": apk_payloads["assets/deathforth/boot.df"],
            "assets/deathforth/events/tutorial.df": l2["overlay/assets/deathforth/events/tutorial.df"],
        }
        self.create_zip(candidate, candidate_payloads)
        return source, base_apk, candidate, layer1, layer2

    def test_exact_ordered_overlay_reconciles_all_scripts(self):
        with tempfile.TemporaryDirectory() as td:
            paths = self.fixture(Path(td))
            result = audit(paths[0], paths[1], paths[2], [paths[3], paths[4]])
            self.assertTrue(result["summary"]["base_source_to_base_apk_exact"])
            self.assertTrue(result["summary"]["candidate_source_sync_exact"])
            self.assertEqual(result["effective_source_to_candidate_apk"]["exact_payload_matches"], 2)
            self.assertEqual(result["summary"]["candidate_script_mismatches"], 0)

    def test_candidate_drift_is_reported_exactly(self):
        with tempfile.TemporaryDirectory() as td:
            paths = list(self.fixture(Path(td)))
            self.create_zip(paths[2], {
                "assets/deathforth/boot.df": b'"GAME-MARKER" $anew\n"READY." print\n',
                "assets/deathforth/events/tutorial.df": b': tutorial "Terjemahan A" print ;\n',
            })
            result = audit(paths[0], paths[1], paths[2], [paths[3], paths[4]])
            self.assertFalse(result["summary"]["candidate_source_sync_exact"])
            mismatch = result["effective_source_to_candidate_apk"]["mismatches"]
            self.assertEqual([row["path"] for row in mismatch], ["assets/deathforth/events/tutorial.df"])
            self.assertEqual(mismatch[0]["expected_layer"], f"layer_2:{paths[4].name}")

    def test_base_source_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            paths = list(self.fixture(Path(td)))
            self.create_zip(paths[1], {
                "assets/deathforth/boot.df": b'"WRONG-MARKER" $anew\n',
                "assets/deathforth/events/tutorial.df": b': tutorial "Base text" print ;\n',
            })
            result = audit(paths[0], paths[1], paths[2], [paths[3], paths[4]])
            self.assertFalse(result["summary"]["base_source_to_base_apk_exact"])
            self.assertIn("assets/deathforth/boot.df", result["base_source_to_base_apk"]["mismatch_paths"])

    def test_duplicate_archive_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            paths = list(self.fixture(Path(td)))
            self.create_zip(paths[3], {"overlay/assets/deathforth/events/tutorial.df": b': tutorial ;\n'}, duplicate=True)
            with self.assertRaises(ValueError):
                audit(paths[0], paths[1], paths[2], [paths[3], paths[4]])

    def test_misplaced_overlay_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            paths = list(self.fixture(Path(td)))
            self.create_zip(paths[3], {"assets/deathforth/events/tutorial.df": b': tutorial ;\n'})
            with self.assertRaises(ValueError):
                audit(paths[0], paths[1], paths[2], [paths[3], paths[4]])

    def test_candidate_missing_script_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            paths = list(self.fixture(Path(td)))
            self.create_zip(paths[2], {"assets/deathforth/boot.df": b'"GAME-MARKER" $anew\n"READY." print\n'})
            result = audit(paths[0], paths[1], paths[2], [paths[3], paths[4]])
            self.assertFalse(result["summary"]["candidate_source_sync_exact"])
            self.assertIn("assets/deathforth/events/tutorial.df", result["effective_source_to_candidate_apk"]["missing_from_candidate"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

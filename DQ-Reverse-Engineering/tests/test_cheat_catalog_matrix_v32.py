import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "validate_cheat_catalog_v32.py"
CATALOG = ROOT / "cheats-sandbox" / "debug_cheats_catalog_v32.json"
MATRIX = ROOT / "docs" / "CHEAT_CATALOG_IMPLEMENTATION_MATRIX_V32.json"


class CheatCatalogV32Tests(unittest.TestCase):
    def test_repository_catalog_and_matrix_validate(self):
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), "--catalog", str(CATALOG), "--matrix", str(MATRIX)],
            capture_output=True, text=True, check=False
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS:", proc.stdout)

    def test_catalog_ids_are_unique(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in catalog["cheats"]]
        self.assertEqual(len(ids), 222)
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_catalog_entry_is_runtime_verified(self):
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(matrix["implementation_counts"]["runtime_verified"], 0)
        self.assertFalse(any(entry["runtime_verified"] for entry in matrix["entries"]))

    def test_catalog_entry_missing_from_matrix_fails_closed(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        matrix["entries"].pop()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            cat_path = temp / "catalog.json"
            matrix_path = temp / "matrix.json"
            cat_path.write_text(json.dumps(catalog), encoding="utf-8")
            matrix_path.write_text(json.dumps(matrix), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(VALIDATOR), "--catalog", str(cat_path), "--matrix", str(matrix_path)],
                capture_output=True, text=True, check=False
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("matrix entries must have one row per catalog entry", proc.stdout)


if __name__ == "__main__":
    unittest.main()

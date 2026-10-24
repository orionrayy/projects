import tempfile
import unittest
from pathlib import Path

from tools.audit_aim_hud_symbols import (
    TARGETS,
    audit_asset,
    audit_tree,
    printable_ascii_runs,
)


class AimHudSymbolAuditTests(unittest.TestCase):
    def test_printable_runs_preserve_byte_offsets(self):
        runs = printable_ascii_runs(b"\x00abc\x01onPurchaseSuccess\xff")
        self.assertEqual(runs[0], (1, "abc"))
        self.assertEqual(runs[1], (5, "onPurchaseSuccess"))

    def test_minimum_printable_run_length_is_validated(self):
        with self.assertRaises(ValueError):
            printable_ascii_runs(b"abc", 0)

    def test_all_expected_symbols_are_found_in_fixture_tree(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel_path, symbols in TARGETS.items():
                path = root / rel_path
                path.parent.mkdir(parents=True, exist_ok=True)
                # Sentinel prefixes exercise offsets without pretending these are source binaries.
                path.write_bytes(b"\x00".join(symbol.encode("ascii") for symbol in symbols))
            report = audit_tree(root)
        self.assertEqual(report["status"], "PASS", report["missing_symbols"])
        self.assertEqual(report["asset_count"], len(TARGETS))
        self.assertTrue(all(asset["sha256"] for asset in report["assets"]))
        self.assertTrue(all(not asset["missing_symbols"] for asset in report["assets"]))

    def test_missing_asset_is_reported_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            report = audit_asset(Path(td), next(iter(TARGETS)), TARGETS[next(iter(TARGETS))])
        self.assertEqual(report["status"], "MISSING_FILE")
        self.assertIsNone(report["sha256"])
        self.assertTrue(report["missing_symbols"])

    def test_missing_symbol_is_not_guessed_from_binary_bytes(self):
        rel_path = next(iter(TARGETS))
        expected = TARGETS[rel_path]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"\x00".join(symbol.encode("ascii") for symbol in expected[:-1]))
            report = audit_asset(Path(td), rel_path, expected)
        self.assertEqual(report["status"], "MISSING_SYMBOLS")
        self.assertEqual(report["missing_symbols"], [expected[-1]])
        self.assertIsNone(report["symbols"][expected[-1]])


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Synthetic regression tests for AIM v10 table framing, without game binaries."""
from __future__ import annotations
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from aim_model_probe_v43 import AimFormatError, parse_aim  # noqa: E402


def string(value: bytes | str) -> bytes:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return struct.pack("<I", len(raw)) + raw


def table(records: list[bytes]) -> bytes:
    return struct.pack("<I", len(records)) + b"".join(
        struct.pack("<I", len(record)) + record for record in records
    )


def fixture(
    marker: bytes = b"NcX",
    version: int = 10,
    current_state: str = "Idle",
    handlers: list[bytes] | None = None,
) -> bytes:
    variables = table([string("bDebug") + b"\x03\x00\xaa\xbb", string("nGold") + b"\x01\x00\x00\x00"])
    functions = table([string("SetLoading") + b"\x01\x02", string("Compile") + b"\x00"])
    states = table([string("Idle") + b"\x00\x01", string("CompileShaders") + b"\x01"])
    handler_records = handlers if handlers is not None else [
        string("onInit") + b"\x02\xaa\xbb",
        string("onClose") + b"\x00\xcc",
    ]
    parts = (variables, functions, states, string(current_state), table(handler_records))
    return (
        struct.pack("<I", 3) + marker + bytes([version]) + struct.pack("<I", 0)
        + b"".join(parts)
    )


class AimModelProbeV43Tests(unittest.TestCase):
    def test_parses_all_four_tables_and_current_state(self):
        report = parse_aim(fixture(), "synthetic.aim")
        self.assertEqual(report["marker"], "NcX")
        self.assertEqual(report["format_version"], 10)
        self.assertEqual(report["current_state"], "Idle")
        self.assertTrue(report["current_state_is_listed"])
        self.assertEqual(report["totals"], {
            "variables": 2, "functions": 2, "states": 2, "handlers": 2, "records": 8
        })
        vars_table, funcs_table, states_table, handlers_table = report["tables"]
        self.assertEqual([r["name"] for r in vars_table["records"]], ["bDebug", "nGold"])
        self.assertEqual([r["name"] for r in funcs_table["records"]], ["SetLoading", "Compile"])
        self.assertEqual([r["name"] for r in states_table["records"]], ["Idle", "CompileShaders"])
        self.assertEqual([r["handler_flag"] for r in handlers_table["records"]], [2, 0])
        self.assertEqual([r["opaque_tail_size"] for r in handlers_table["records"]], [2, 1])
        self.assertFalse(report["rewrite_supported"])

    def test_accepts_observed_marker_variants(self):
        for marker in (b"NcX", b"NcP", b"NcI"):
            self.assertEqual(parse_aim(fixture(marker=marker))["marker"], marker.decode("ascii"))

    def test_current_state_can_be_empty_when_no_state_table_entries(self):
        data = fixture(current_state="")
        # Build a consistent model that has no states and no selected state.
        source = parse_aim(data)
        sections = source["tables"]
        variables = table([string("bDebug") + b"\x03\x00"])
        functions = table([string("Compile") + b"\x00"])
        states = table([])
        handlers = table([string("onInit") + b"\x02"])
        data = (
            struct.pack("<I", 3) + b"NcX" + b"\x0a" + struct.pack("<I", 0)
            + variables + functions + states + string("") + handlers
        )
        parsed = parse_aim(data)
        self.assertEqual(parsed["current_state"], "")
        self.assertIsNone(parsed["current_state_is_listed"])
        self.assertEqual(parsed["totals"]["states"], 0)

    def test_rejects_bad_markers_versions_truncation_and_trailing_bytes(self):
        with self.assertRaises(AimFormatError):
            parse_aim(fixture(marker=b"BAD"))
        with self.assertRaises(AimFormatError):
            parse_aim(fixture(version=9))
        with self.assertRaises(AimFormatError):
            parse_aim(fixture()[:-1])
        with self.assertRaises(AimFormatError):
            parse_aim(fixture() + b"x")

    def test_rejects_handler_without_flag(self):
        with self.assertRaises(AimFormatError):
            parse_aim(fixture(handlers=[string("onBroken")]))

    def test_current_state_is_reported_unlisted_without_rejecting_valid_framing(self):
        report = parse_aim(fixture(current_state="NotInTable"))
        self.assertFalse(report["current_state_is_listed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

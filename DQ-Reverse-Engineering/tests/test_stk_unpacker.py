#!/usr/bin/env python3
"""Unit tests for the STK parser using synthetic fixtures, not game binaries."""
from __future__ import annotations
import pathlib
import struct
import sys
import tempfile
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from stk_unpacker import ENTRY_META, HEADER, STK_SIGNATURE, StkArchive, xor_bytes  # noqa: E402


def make_archive(path, entries, key=0x12345678, bad_crc_for=None, raw_flags=0x06):
    records = []
    for name, data, compressed in entries:
        payload = zlib.compress(data) if compressed else data
        records.append((name, data, payload, zlib.crc32(payload) & 0xFFFFFFFF))
    table, payload_blob, offsets = bytearray(), bytearray(), []
    for name, _data, payload, _crc in records:
        offsets.append(len(payload_blob))
        payload_blob.extend(xor_bytes(payload, key))
    for i, (name, raw, payload, crc) in enumerate(records):
        encoded_name = name.encode("utf-8")
        if bad_crc_for == name:
            crc ^= 0x100
        table.extend(struct.pack("<I", len(encoded_name)))
        table.extend(encoded_name)
        table.extend(ENTRY_META.pack(offsets[i], len(payload), len(raw), crc, 4))
    table_end = HEADER.size + len(table)
    header = HEADER.pack(raw_flags, STK_SIGNATURE, b"        ", key, len(records), table_end)
    path.write_bytes(header + xor_bytes(bytes(table), key) + payload_blob)


def main():
    with tempfile.TemporaryDirectory(prefix="stk-test-") as tmp:
        tmp = pathlib.Path(tmp)
        xml = b"<?xml version='1.0'?><root><row id='1'/></root>"
        raw = b"RAW-FIXTURE-123"
        sample = tmp / "valid.smf"
        make_archive(sample, [("Resources/XML/test.xml", xml, True), ("Models/raw.bin", raw, False)])
        archive = StkArchive(sample)
        validator = getattr(archive, "validate_all", None) or archive.validate
        summary = validator(tmp / "inventory.json", tmp / "inventory.csv")
        assert summary["verified_entries"] == 2
        assert summary["verified_uncompressed_bytes"] == len(xml) + len(raw)
        raw_codec = "raw/xor" if "raw/xor" in summary["codec_counts"] else "raw+xor"
        assert summary["codec_counts"] == {"zlib+xor": 1, raw_codec: 1}
        output = tmp / "output"
        archive.extract(output)
        assert (output / "Resources/XML/test.xml").read_bytes() == xml
        assert (output / "Models/raw.bin").read_bytes() == raw

        traversal = tmp / "traversal.smf"
        make_archive(traversal, [("../escape.bin", raw, False)])
        try:
            StkArchive(traversal)
        except ValueError as exc:
            assert "unsafe archive path" in str(exc)
        else:
            raise AssertionError("traversal should be rejected")

        bad_crc_path = tmp / "bad-crc.smf"
        make_archive(bad_crc_path, [("safe.bin", xml, True)], bad_crc_for="safe.bin")
        bad = StkArchive(bad_crc_path)
        bad_output = tmp / "bad-output"
        try:
            bad.extract(bad_output)
        except ValueError as exc:
            assert "CRC mismatch" in str(exc)
        else:
            raise AssertionError("bad CRC should be rejected")
        assert not list(bad_output.iterdir()), "validation failure must not write files"

        nonempty = tmp / "nonempty"
        nonempty.mkdir()
        (nonempty / "keep.txt").write_text("keep", encoding="utf-8")
        try:
            archive.extract(nonempty)
        except ValueError as exc:
            assert "directory" in str(exc) or "new or empty" in str(exc)
        else:
            raise AssertionError("non-empty destination should be rejected")

    print("PASS: STK header/table, zlib+XOR, raw+XOR, extraction, traversal rejection, CRC failure and overwrite safeguards")


if __name__ == "__main__":
    main()

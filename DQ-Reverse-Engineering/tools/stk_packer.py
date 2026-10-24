#!/usr/bin/env python3
"""Rebuild a version-6 ShiVa/STK pack with explicit asset replacements.

This operates on user-supplied pack files. It preserves unchanged decoded entries,
validates CRC/size metadata, and never overwrites the input archive.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import struct
import zlib
from dataclasses import dataclass
from typing import Dict, List, Mapping, Tuple

HEADER = struct.Struct("<BI8sIII")
ENTRY_META = struct.Struct("<IIIIH")
SIGNATURE = 0x00000008
MAX_ENTRIES = 100_000
MAX_NAME_BYTES = 2048
MAX_ENTRY_SIZE = 512 * 1024 * 1024

def xor_bytes(data: bytes, key: int) -> bytes:
    k = struct.pack("<I", key)
    return bytes(b ^ k[i & 3] for i, b in enumerate(data))

def safe_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    p = pathlib.PurePosixPath(normalized)
    if (not normalized or p.is_absolute() or "\x00" in normalized
            or any(part in ("", ".", "..") for part in p.parts)
            or (p.parts and ":" in p.parts[0])):
        raise ValueError("unsafe archive path: %r" % value)
    return p.as_posix()

@dataclass
class Entry:
    name: str
    offset: int
    csize: int
    usize: int
    crc: int
    flags: int

class StkArchive:
    def __init__(self, data: bytes, label: str = "<memory>"):
        self.data, self.label = data, label
        if len(data) < HEADER.size:
            raise ValueError("file too short for STK header")
        raw, self.signature, self.padding, self.key, self.count, self.table_end = HEADER.unpack_from(data)
        self.version, self.header_flags = raw & 0x0F, raw & 0xF0
        if self.signature != SIGNATURE:
            raise ValueError("unexpected STK signature: 0x%08x" % self.signature)
        if self.version != 6:
            raise ValueError("writer supports verified STK version 6 only (got %d)" % self.version)
        if self.header_flags & 0x30:
            raise ValueError("unsupported compression flags 0x%02x" % self.header_flags)
        if not 1 <= self.count <= MAX_ENTRIES:
            raise ValueError("unreasonable entry count: %d" % self.count)
        if not HEADER.size <= self.table_end <= len(data):
            raise ValueError("metadata end offset outside archive")
        self.entries = self._parse_table()
        self._validate_metadata()

    @classmethod
    def from_path(cls, path: pathlib.Path) -> "StkArchive":
        return cls(path.read_bytes(), str(path))

    def _parse_table(self) -> List[Entry]:
        table = xor_bytes(self.data[HEADER.size:self.table_end], self.key)
        pos, entries = 0, []
        for i in range(self.count):
            if pos + 4 > len(table):
                raise ValueError("truncated name length at entry %d" % i)
            size = struct.unpack_from("<I", table, pos)[0]
            pos += 4
            if size < 1 or size > MAX_NAME_BYTES or pos + size + ENTRY_META.size > len(table):
                raise ValueError("invalid name length at entry %d" % i)
            try:
                name = table[pos:pos + size].decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError("invalid UTF-8 name at entry %d" % i) from exc
            pos += size
            entries.append(Entry(name, *ENTRY_META.unpack_from(table, pos)))
            pos += ENTRY_META.size
        if pos != len(table):
            raise ValueError("entry table has %d trailing bytes" % (len(table)-pos))
        return entries

    def _validate_metadata(self) -> None:
        payload_size = len(self.data) - self.table_end
        names = set()
        for e in self.entries:
            name = safe_path(e.name)
            folded = name.casefold()
            if folded in names:
                raise ValueError("duplicate/case-colliding path: %r" % e.name)
            names.add(folded)
            if e.offset > payload_size or e.csize > payload_size - e.offset:
                raise ValueError("payload range exceeds archive: %r" % e.name)
            if not 0 <= e.usize <= MAX_ENTRY_SIZE:
                raise ValueError("unreasonable unpacked size: %r" % e.name)

    def stored_payload(self, e: Entry) -> bytes:
        start = self.table_end + e.offset
        payload = xor_bytes(self.data[start:start + e.csize], self.key)
        if zlib.crc32(payload) & 0xffffffff != e.crc:
            raise ValueError("stored-payload CRC mismatch: %s" % e.name)
        return payload

    def decode(self, e: Entry) -> bytes:
        stored = self.stored_payload(e)
        if e.csize == e.usize:
            decoded = stored
        else:
            dec = zlib.decompressobj()
            decoded = dec.decompress(stored) + dec.flush()
            if not dec.eof or dec.unused_data or dec.unconsumed_tail:
                raise ValueError("invalid/trailing zlib stream: %s" % e.name)
        if len(decoded) != e.usize:
            raise ValueError("decoded-size mismatch: %s (%d != %d)" % (e.name, len(decoded), e.usize))
        return decoded

    def rebuild(self, replacements: Mapping[str, bytes]) -> bytes:
        normalized: Dict[str, bytes] = {}
        for name, content in replacements.items():
            safe = safe_path(name)
            if safe in normalized:
                raise ValueError("duplicate replacement: %s" % safe)
            if not isinstance(content, bytes):
                raise TypeError("replacement content must be bytes: %s" % safe)
            if len(content) > MAX_ENTRY_SIZE:
                raise ValueError("replacement exceeds size cap: %s" % safe)
            normalized[safe] = content
        by_name = {e.name: e for e in self.entries}
        missing = sorted(set(normalized) - set(by_name))
        if missing:
            raise ValueError("replacement target(s) not found: %s" % ", ".join(missing))

        payloads: List[Tuple[Entry, bytes, int]] = []
        for e in self.entries:
            if e.name in normalized:
                plain = normalized[e.name]
                compressed = zlib.compress(plain, level=9)
                stored = plain if len(compressed) >= len(plain) else compressed
                usize = len(plain)
            else:
                stored, usize = self.stored_payload(e), e.usize
            payloads.append((e, stored, usize))

        table = bytearray()
        offset = 0
        for e, stored, usize in payloads:
            name = safe_path(e.name).encode("utf-8")
            table.extend(struct.pack("<I", len(name)))
            table.extend(name)
            table.extend(ENTRY_META.pack(offset, len(stored), usize,
                                        zlib.crc32(stored) & 0xffffffff, e.flags))
            offset += len(stored)
        table_end = HEADER.size + len(table)
        header = HEADER.pack((self.header_flags | self.version), self.signature,
                             self.padding, self.key, len(payloads), table_end)
        output = bytearray(header)
        output.extend(xor_bytes(bytes(table), self.key))
        for _, stored, _ in payloads:
            output.extend(xor_bytes(stored, self.key))

        rebuilt = bytes(output)
        check = StkArchive(rebuilt, "<rebuilt>")
        check_entries = {e.name: e for e in check.entries}
        replacement_names = set(normalized)
        for old in self.entries:
            new = check_entries[old.name]
            want = normalized[old.name] if old.name in replacement_names else self.decode(old)
            if check.decode(new) != want:
                raise ValueError("round-trip content mismatch: %s" % old.name)
        return rebuilt

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=pathlib.Path)
    p.add_argument("output", type=pathlib.Path)
    p.add_argument("--replace", action="append", default=[], metavar="ARCHIVE_PATH=LOCAL_FILE")
    p.add_argument("--report", type=pathlib.Path)
    p.add_argument("--overwrite-output", action="store_true")
    a = p.parse_args()
    try:
        src, dst = a.input.resolve(), a.output.resolve()
        if src == dst:
            raise ValueError("input and output must be different paths")
        if dst.is_symlink():
            raise ValueError("refusing output symlink")
        if dst.exists() and not a.overwrite_output:
            raise ValueError("output exists; pass --overwrite-output to replace it")
        archive = StkArchive.from_path(src)
        replacements = {}
        for spec in a.replace:
            if "=" not in spec:
                raise ValueError("--replace requires ARCHIVE_PATH=LOCAL_FILE")
            name, local = spec.split("=", 1)
            name = safe_path(name)
            if name in replacements:
                raise ValueError("duplicate replacement target: %s" % name)
            replacements[name] = pathlib.Path(local).read_bytes()
        rebuilt = archive.rebuild(replacements)
        dst.parent.mkdir(parents=True, exist_ok=True)
        with dst.open("wb" if a.overwrite_output else "xb") as f:
            f.write(rebuilt)
        verified = StkArchive.from_path(dst)
        counts = {"raw+xor": 0, "zlib+xor": 0}
        decoded_total = 0
        for e in verified.entries:
            verified.decode(e)
            kind = "raw+xor" if e.csize == e.usize else "zlib+xor"
            counts[kind] += 1
            decoded_total += e.usize
        report = {
            "source": src.name, "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "output": dst.name, "output_sha256": hashlib.sha256(rebuilt).hexdigest(),
            "output_size_bytes": len(rebuilt), "version": verified.version,
            "entry_count": len(verified.entries), "decoded_bytes": decoded_total,
            "codec_counts": counts, "replacements": sorted(replacements),
            "all_entries_validated": True, "round_trip_unchanged_entries_verified": True
        }
        if a.report:
            a.report.parent.mkdir(parents=True, exist_ok=True)
            a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, TypeError, struct.error, zlib.error, UnicodeError) as exc:
        p.exit(2, "ERROR: %s\n" % exc)

if __name__ == "__main__":
    raise SystemExit(main())

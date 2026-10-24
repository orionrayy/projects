#!/usr/bin/env python3
"""Safely inspect/extract version-6 Shiva3D STK-style packs with Python stdlib only."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import pathlib
import struct
import sys
import zlib

HEADER = struct.Struct("<BI8sIII")  # packed size 25 bytes
ENTRY_META = struct.Struct("<IIIIH")
STK_SIGNATURE = 0x00000008


def xor_bytes(data: bytes, key: int) -> bytes:
    key_bytes = struct.pack("<I", key)
    return bytes(value ^ key_bytes[i & 3] for i, value in enumerate(data))


def safe_path(name: str) -> pathlib.PurePosixPath:
    name = name.replace("\\", "/")
    path = pathlib.PurePosixPath(name)
    if not name or path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe archive path: {name!r}")
    if path.parts and ":" in path.parts[0]:
        raise ValueError(f"drive-qualified archive path: {name!r}")
    if "\x00" in name:
        raise ValueError("NUL in archive path")
    return path


class StkArchive:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.data = path.read_bytes()
        if len(self.data) < HEADER.size:
            raise ValueError("file too short for STK header")
        raw_flags, self.signature, self.padding, self.key, self.count, self.table_end = HEADER.unpack_from(self.data)
        self.version = raw_flags & 0x0F
        self.flags = raw_flags & 0xF0
        if self.signature != STK_SIGNATURE:
            raise ValueError(f"unexpected signature 0x{self.signature:08x}")
        if self.version < 3:
            raise ValueError(f"legacy version {self.version} requires unsupported UCL decompression")
        if not HEADER.size <= self.table_end <= len(self.data):
            raise ValueError("metadata end offset is outside the input file")
        self.entries = self._parse_table()
        self._validate_entries()

    def _parse_table(self):
        # The version-6 field is an absolute metadata-end offset including the header.
        table = xor_bytes(self.data[HEADER.size:self.table_end], self.key)
        pos, entries = 0, []
        for idx in range(self.count):
            if pos + 4 > len(table):
                raise ValueError(f"truncated filename length at entry {idx}")
            name_len = struct.unpack_from("<I", table, pos)[0]
            pos += 4
            if name_len < 1 or name_len > 2048 or pos + name_len + ENTRY_META.size > len(table):
                raise ValueError(f"invalid filename length {name_len} at entry {idx}")
            name = table[pos:pos + name_len].decode("utf-8")
            pos += name_len
            offset, csize, usize, crc, flags = ENTRY_META.unpack_from(table, pos)
            pos += ENTRY_META.size
            entries.append({"name": name, "offset": offset, "compressed_size": csize,
                            "uncompressed_size": usize, "crc32": crc, "flags": flags})
        if pos != len(table):
            raise ValueError(f"entry table consumed {pos}/{len(table)} bytes")
        return entries

    def _validate_entries(self):
        payload_size = len(self.data) - self.table_end
        seen = set()
        for entry in self.entries:
            key = safe_path(entry["name"]).as_posix().casefold()
            if key in seen:
                raise ValueError(f"duplicate or case-colliding output name: {entry['name']!r}")
            seen.add(key)
            off, size = entry["offset"], entry["compressed_size"]
            if off > payload_size or size > payload_size - off:
                raise ValueError(f"payload range exceeds input: {entry['name']!r}")
            if entry["uncompressed_size"] > 512 * 1024 * 1024:
                raise ValueError(f"unreasonable output size: {entry['name']!r}")

    def decode(self, entry):
        start = self.table_end + entry["offset"]
        raw = self.data[start:start + entry["compressed_size"]]
        payload = xor_bytes(raw, self.key)
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        if crc != entry["crc32"]:
            raise ValueError(f"CRC mismatch for {entry['name']}: expected {entry['crc32']:08x}, got {crc:08x}")
        if entry["compressed_size"] == entry["uncompressed_size"]:
            output, codec = payload, "raw+xor"
        else:
            if self.flags & 0x30:
                raise ValueError(f"unsupported compression flags 0x{self.flags & 0x30:02x}")
            inflater = zlib.decompressobj()
            output = inflater.decompress(payload) + inflater.flush()
            if not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
                raise ValueError(f"invalid or trailing zlib bytes in {entry['name']}")
            codec = "zlib+xor"
        if len(output) != entry["uncompressed_size"]:
            raise ValueError(f"decoded size mismatch for {entry['name']}: {len(output)} != {entry['uncompressed_size']}")
        return output, codec

    def validate(self, json_path=None, csv_path=None):
        rows, codecs, total = [], {}, 0
        for entry in self.entries:
            payload, codec = self.decode(entry)
            codecs[codec] = codecs.get(codec, 0) + 1
            total += len(payload)
            rows.append({
                "name": entry["name"], "offset": entry["offset"],
                "compressed_size": entry["compressed_size"],
                "uncompressed_size": entry["uncompressed_size"],
                "crc32": f'{entry["crc32"]:08x}', "flags": entry["flags"],
                "codec": codec, "sha256": hashlib.sha256(payload).hexdigest()
            })
        result = {
            "input": self.path.name,
            "input_size_bytes": len(self.data),
            "input_sha256": hashlib.sha256(self.data).hexdigest(),
            "signature": f"0x{self.signature:08x}",
            "version": self.version, "flags_raw": f"0x{self.flags:02x}",
            "xor_key": f"0x{self.key:08x}", "entry_count": self.count,
            "entry_table_end_offset": self.table_end,
            "payload_size_bytes": len(self.data) - self.table_end,
            "verified_uncompressed_bytes": total, "verified_entries": len(rows),
            "codec_counts": codecs, "entries": rows
        }
        if json_path:
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if csv_path:
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
                writer.writeheader()
                writer.writerows(rows)
        return {k: v for k, v in result.items() if k != "entries"}

    def extract(self, destination: pathlib.Path):
        destination.mkdir(parents=True, exist_ok=True)
        if destination.is_symlink() or any(destination.iterdir()):
            raise ValueError("destination must be a new or empty, non-symlink directory")
        summary = self.validate()  # fail before writing anything
        root = destination.resolve()
        for entry in self.entries:
            payload, _ = self.decode(entry)
            relative = safe_path(entry["name"])
            target = destination.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            cursor = target.parent
            while cursor != root and cursor != cursor.parent:
                if cursor.is_symlink():
                    raise ValueError(f"symlinked output parent rejected: {cursor}")
                cursor = cursor.parent
            parent = target.parent.resolve()
            if parent != root and root not in parent.parents:
                raise ValueError(f"output escaped destination: {entry['name']!r}")
            if target.exists() or target.is_symlink():
                raise ValueError(f"refusing to overwrite {target}")
            target.write_bytes(payload)
        summary["extracted_to"] = str(destination)
        summary["extracted_files"] = self.count
        return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=pathlib.Path)
    parser.add_argument("--extract", type=pathlib.Path, help="extract to a new/empty directory")
    parser.add_argument("--inventory-json", type=pathlib.Path)
    parser.add_argument("--inventory-csv", type=pathlib.Path)
    args = parser.parse_args()
    try:
        archive = StkArchive(args.archive)
        if args.extract:
            summary = archive.extract(args.extract)
            if args.inventory_json or args.inventory_csv:
                summary = archive.validate(args.inventory_json, args.inventory_csv)
                summary["extracted_to"] = str(args.extract)
                summary["extracted_files"] = archive.count
        else:
            summary = archive.validate(args.inventory_json, args.inventory_csv)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, struct.error, zlib.error, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

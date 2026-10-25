#!/usr/bin/env python3
"""Read-only version-10 AIModel section/record inventory for ShiVa-style .aim files.

The parser only decodes each table's framing and first name string. Remaining
record bytes are opaque and hashed, not interpreted or rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import struct
from collections import Counter
from typing import Any

KNOWN_MARKERS = {b"NcX", b"NcP", b"NcI"}
SUPPORTED_VERSION = 10
MAX_RECORDS = 100_000
MAX_RECORD_BYTES = 64 * 1024 * 1024
MAX_STRING_BYTES = 2_000_000
TABLES = ("variables", "functions", "states", "handlers")


class AimFormatError(ValueError):
    """Malformed, truncated, or unsupported AIM data."""


class Reader:
    def __init__(self, data: bytes, label: str):
        self.data = data
        self.label = label
        self.offset = 0

    def take(self, size: int) -> bytes:
        if size < 0 or self.offset + size > len(self.data):
            raise AimFormatError(
                f"{self.label}: truncated at 0x{self.offset:x}; "
                f"need {size}, have {len(self.data) - self.offset}"
            )
        start = self.offset
        self.offset += size
        return self.data[start:self.offset]

    def u8(self) -> int:
        return self.take(1)[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def string(self) -> tuple[str, bytes]:
        start = self.offset
        size = self.u32()
        if size > MAX_STRING_BYTES:
            raise AimFormatError(
                f"{self.label}: unreasonable string length {size} at 0x{start:x}"
            )
        raw = self.take(size)
        return raw.decode("utf-8", errors="surrogateescape"), self.data[start:self.offset]


def _parse_table(reader: Reader, table_name: str, parse_flag: bool = False) -> dict[str, Any]:
    table_count_offset = reader.offset
    count = reader.u32()
    if count > MAX_RECORDS:
        raise AimFormatError(
            f"{table_name}: unreasonable record count {count} at 0x{table_count_offset:x}"
        )

    records = []
    for index in range(count):
        size_offset = reader.offset
        size = reader.u32()
        if size > MAX_RECORD_BYTES:
            raise AimFormatError(
                f"{table_name}[{index}]: unreasonable record size {size} at 0x{size_offset:x}"
            )
        payload_offset = reader.offset
        payload = reader.take(size)
        record_reader = Reader(payload, f"{table_name}[{index}]")
        name, name_raw = record_reader.string()
        flag = None
        if parse_flag:
            if record_reader.offset >= len(payload):
                raise AimFormatError(
                    f"{table_name}[{index}] {name!r}: handler flag missing from record"
                )
            flag = record_reader.u8()
        records.append({
            "index": index,
            "name": name,
            "record_size": size,
            "record_offset": payload_offset,
            "name_encoded_size": len(name_raw),
            "opaque_tail_size": size - record_reader.offset,
            "record_sha256": hashlib.sha256(payload).hexdigest(),
            "handler_flag": flag,
        })

    return {
        "name": table_name,
        "count": count,
        "count_offset": table_count_offset,
        "records_offset": table_count_offset + 4,
        "end_offset": reader.offset,
        "records": records,
    }


def parse_aim(data: bytes, source: str = "<memory>") -> dict[str, Any]:
    reader = Reader(data, "AIM header")
    marker_len = reader.u32()
    marker = reader.take(3)
    version = reader.u8()
    if marker_len != 3 or marker not in KNOWN_MARKERS:
        raise AimFormatError(f"invalid AIM marker/length: {marker_len}, {marker!r}")
    if version != SUPPORTED_VERSION:
        raise AimFormatError(
            f"unsupported AIM version {version}; this probe is verified for v{SUPPORTED_VERSION}"
        )

    # AIModel::Load reads this v4+ extension/prefix before the four tables.
    extension_prefix = reader.u32()
    variables = _parse_table(reader, "variables")
    functions = _parse_table(reader, "functions")
    states = _parse_table(reader, "states")

    # LoadStates reads the selected/current state name after the state records.
    current_state, current_state_raw = reader.string()
    handler_table = _parse_table(reader, "handlers", parse_flag=True)

    if reader.offset != len(data):
        raise AimFormatError(
            f"{len(data) - reader.offset} trailing byte(s) at 0x{reader.offset:x}"
        )

    state_names = {record["name"] for record in states["records"]}
    return {
        "schema": "aim-model-probe-v43",
        "source": source,
        "file_size": len(data),
        "file_sha256": hashlib.sha256(data).hexdigest(),
        "marker": marker.decode("ascii"),
        "format_version": version,
        "extension_prefix": extension_prefix,
        "current_state": current_state,
        "current_state_encoded_size": len(current_state_raw),
        "current_state_is_listed": (current_state in state_names) if current_state else None,
        "tables": [variables, functions, states, handler_table],
        "totals": {
            "variables": variables["count"],
            "functions": functions["count"],
            "states": states["count"],
            "handlers": handler_table["count"],
            "records": variables["count"] + functions["count"] + states["count"] + handler_table["count"],
        },
        "rewrite_supported": False,
    }


def summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        key: report[key]
        for key in ("source", "file_size", "file_sha256", "marker", "format_version",
                    "extension_prefix", "current_state", "current_state_is_listed", "totals",
                    "rewrite_supported")
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("aim", type=pathlib.Path, nargs="+", help="one or more .aim files; read only")
    parser.add_argument("--output-dir", type=pathlib.Path, help="write one JSON inventory per file")
    parser.add_argument("--summary", action="store_true", help="print compact model summaries")
    args = parser.parse_args()

    failures: list[dict[str, str]] = []
    reports: list[dict[str, Any]] = []
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
    for path in args.aim:
        try:
            report = parse_aim(path.read_bytes(), str(path))
            reports.append(report)
            if args.output_dir:
                out = args.output_dir / f"{path.name}.json"
                if out.exists():
                    raise AimFormatError(f"refusing to overwrite existing report: {out}")
                out.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
            print(json.dumps(summary(report) if args.summary else report, ensure_ascii=True))
        except (OSError, AimFormatError, struct.error) as exc:
            failures.append({"path": str(path), "error": str(exc)})
            print(json.dumps({"path": str(path), "status": "FAIL", "error": str(exc)}, ensure_ascii=True))

    aggregate = Counter()
    for report in reports:
        aggregate.update(report["totals"])
    print(json.dumps({
        "schema": "aim-model-probe-v43-run",
        "tested": len(args.aim),
        "passed": len(reports),
        "failed": len(failures),
        "aggregate_records": dict(aggregate),
        "failures": failures,
        "rewrite_supported": False,
    }, indent=2, ensure_ascii=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

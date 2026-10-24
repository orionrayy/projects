#!/usr/bin/env python3
"""Read-only parser for the known top-level Pandora .hud sections.

This intentionally leaves element and timer records opaque. It must not be used
to rewrite a game HUD: no lossless element serializer is implemented here.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

SECTION_NAMES = ("general_attributes", "elements", "actions", "timers")


class HudFormatError(ValueError):
    """Malformed or truncated HUD resource."""


def _read(data: bytes, offset: int, size: int, what: str) -> bytes:
    if offset < 0 or size < 0 or offset + size > len(data):
        raise HudFormatError(
            f"truncated {what}: offset={offset}, size={size}, file_size={len(data)}"
        )
    return data[offset : offset + size]


def _uint(data: bytes, offset: int, size: int, what: str) -> tuple[int, int]:
    return int.from_bytes(_read(data, offset, size, what), "little"), offset + size


def _string(data: bytes, offset: int, what: str) -> tuple[str, int]:
    length, offset = _uint(data, offset, 4, f"{what} length")
    raw = _read(data, offset, length, what)
    try:
        return raw.decode("utf-8"), offset + length
    except UnicodeDecodeError as exc:
        raise HudFormatError(f"invalid UTF-8 in {what} at byte {offset}") from exc


def inspect_hud(data: bytes, source: str = "<memory>") -> dict:
    """Validate header and all four section bounds, then parse known fields."""
    if len(data) < 8:
        raise HudFormatError("file is shorter than the 8-byte resource header")
    marker_len, _ = _uint(data, 0, 4, "header marker length")
    if marker_len != 3 or data[4:7] != b"NcP":
        raise HudFormatError("expected length-prefixed 'NcP' resource marker")
    version = data[7]
    if version == 0:
        raise HudFormatError("format version 0 is invalid")

    sections = []
    payloads = {}
    cursor = 8
    for name in SECTION_NAMES:
        length, payload_at = _uint(data, cursor, 4, f"{name} section length")
        payload = _read(data, payload_at, length, f"{name} payload")
        sections.append({
            "name": name,
            "header_offset": cursor,
            "payload_offset": payload_at,
            "payload_size": length,
        })
        payloads[name] = payload
        cursor = payload_at + length
    if cursor != len(data):
        raise HudFormatError(f"{len(data) - cursor} trailing byte(s) after four sections")

    general, consumed = _string(payloads["general_attributes"], 0, "initial action")
    if consumed != len(payloads["general_attributes"]):
        raise HudFormatError("unparsed bytes remain in general-attributes section")

    element_payload = payloads["elements"]
    element_count, element_fields_at = _uint(element_payload, 0, 4, "element count")

    action_payload = payloads["actions"]
    action_count, at = _uint(action_payload, 0, 2, "action count")
    actions = []
    for i in range(action_count):
        name, at = _string(action_payload, at, f"action[{i}] name")
        argc, at = _uint(action_payload, at, 2, f"action[{i}] parameter count")
        params = []
        for j in range(argc):
            value, at = _string(action_payload, at, f"action[{i}] parameter[{j}]")
            params.append(value)
        extra = ""
        # The native loader reads one additional string for resource versions > 8.
        if version > 8:
            extra, at = _string(action_payload, at, f"action[{i}] extra script")
        actions.append({"name": name, "parameters": params, "extra_script": extra})
    if at != len(action_payload):
        raise HudFormatError(f"{len(action_payload) - at} unparsed byte(s) in actions section")

    timer_payload = payloads["timers"]
    timer_count, timer_fields_at = _uint(timer_payload, 0, 2, "timer count")
    if timer_count == 0 and timer_fields_at != len(timer_payload):
        raise HudFormatError("empty timer table has unexpected payload bytes")

    return {
        "schema": "pandora-hud-ncp-probe-v1",
        "source": source,
        "file_size": len(data),
        "header": {"marker": "NcP", "format_version": version},
        "sections": sections,
        "general_attributes": {"initial_action": general},
        "elements": {
            "count": element_count,
            "decoded_records": 0,
            "opaque_record_payload_size": len(element_payload) - element_fields_at,
        },
        "actions": {"count": action_count, "records": actions},
        "timers": {
            "count": timer_count,
            "opaque_record_payload_size": len(timer_payload) - timer_fields_at,
        },
        "rewrite_supported": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hud", type=Path, help="input .hud file (read only)")
    parser.add_argument("--output", type=Path, help="write JSON report")
    parser.add_argument("--summary", action="store_true", help="print section/count summary")
    args = parser.parse_args()
    report = inspect_hud(args.hud.read_bytes(), str(args.hud))
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    if args.summary:
        section_text = ", ".join(
            f"{item['name']}={item['payload_size']}B" for item in report["sections"]
        )
        print(
            f"{args.hud}: version={report['header']['format_version']} "
            f"elements={report['elements']['count']} actions={report['actions']['count']} "
            f"timers={report['timers']['count']} | {section_text}"
        )
    elif not args.output:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

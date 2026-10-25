#!/usr/bin/env python3
"""Field-preserving encoder for the v12 HUD action-section framing."""
from __future__ import annotations
import struct
from typing import Any
from hud_action_probe_v45 import parse_action_section, HudActionFormatError

MAX_ACTIONS = 0xFFFF
MAX_STATEMENTS = 0xFFFF
MAX_STRING_BYTES = 2_000_000
MAX_STATEMENT_BYTES = 2_000_000

def _encoded_string(value: str, label: str) -> bytes:
    if not isinstance(value, str):
        raise HudActionFormatError(f"{label} must be a string")
    raw = value.encode("utf-8", errors="surrogateescape")
    if len(raw) > MAX_STRING_BYTES:
        raise HudActionFormatError(f"{label} too large: {len(raw)}")
    return struct.pack("<I", len(raw)) + raw

def encode_action_section(doc: dict[str, Any]) -> bytes:
    actions = doc.get("actions")
    if not isinstance(actions, list) or len(actions) > MAX_ACTIONS:
        raise HudActionFormatError("actions must be a list of at most 65535 records")
    out = bytearray(struct.pack("<H", len(actions)))
    seen = set()
    for i, action in enumerate(actions):
        name = action.get("name")
        if not isinstance(name, str) or not name:
            raise HudActionFormatError(f"action[{i}] name must be a non-empty string")
        if name in seen:
            raise HudActionFormatError(f"duplicate action name: {name!r}")
        seen.add(name)
        statements = action.get("statements")
        if not isinstance(statements, list) or len(statements) > MAX_STATEMENTS:
            raise HudActionFormatError(f"action[{i}] {name!r}: invalid statement list")
        declared = action.get("declared_statement_count", len(statements))
        if declared != len(statements):
            raise HudActionFormatError(f"action[{i}] {name!r}: declared statement count does not match payload")
        out.extend(_encoded_string(name, f"action[{i}] name"))
        out.extend(struct.pack("<H", len(statements)))
        for j, statement in enumerate(statements):
            if not isinstance(statement, str):
                raise HudActionFormatError(f"action[{i}] statement[{j}] must be a string")
            raw = statement.encode("utf-8", errors="surrogateescape")
            if not raw or len(raw) > MAX_STATEMENT_BYTES:
                raise HudActionFormatError(f"action[{i}] statement[{j}] has invalid byte length {len(raw)}")
            out.extend(struct.pack("<I", len(raw)))
            out.extend(raw)
        out.extend(struct.pack("<I", 0))
    rebuilt = bytes(out)
    checked = parse_action_section(rebuilt, "<encoded>")
    if len(checked["actions"]) != len(actions):
        raise HudActionFormatError("action count changed on reparse")
    return rebuilt

def append_action(doc: dict[str, Any], name: str, statements: list[str]) -> None:
    if not isinstance(doc.get("actions"), list):
        raise HudActionFormatError("document has no action list")
    if any(a.get("name") == name for a in doc["actions"]):
        raise HudActionFormatError(f"action already exists: {name!r}")
    if not isinstance(statements, list):
        raise HudActionFormatError("statements must be a list")
    doc["actions"].append({"index": len(doc["actions"]), "name": name,
                           "declared_statement_count": len(statements),
                           "statements": list(statements), "statement_count": len(statements),
                           "offset": None, "end_offset": None})

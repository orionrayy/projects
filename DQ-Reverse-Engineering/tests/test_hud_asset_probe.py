#!/usr/bin/env python3
"""Synthetic regression tests for the read-only Pandora HUD probe."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from hud_asset_probe import HudFormatError, inspect_hud  # noqa: E402


def u16(value: int) -> bytes:
    return struct.pack("<H", value)


def u32(value: int) -> bytes:
    return struct.pack("<I", value)


def string(value: str) -> bytes:
    raw = value.encode("utf-8")
    return u32(len(raw)) + raw


def section(payload: bytes) -> bytes:
    return u32(len(payload)) + payload


def fixture(version: int = 12) -> bytes:
    general = string("onOpen")
    elements = u32(2) + b"opaque-elements"
    actions = u16(2) + string("onOpen") + u16(1) + string("call:model:handler")
    if version > 8:
        actions += string("")
    actions += string("onClose") + u16(0)
    if version > 8:
        actions += string("")
    timers = u16(0)
    return u32(3) + b"NcP" + bytes([version]) + b"".join(
        section(payload) for payload in (general, elements, actions, timers)
    )


def test_valid_version_12() -> None:
    data = fixture(12)
    result = inspect_hud(data, "synthetic.hud")
    assert result["header"] == {"marker": "NcP", "format_version": 12}
    assert result["general_attributes"]["initial_action"] == "onOpen"
    assert [item["payload_size"] for item in result["sections"]] == [
        len(string("onOpen")), len(u32(2) + b"opaque-elements"),
        len(u16(2) + string("onOpen") + u16(1) + string("call:model:handler") + string("")
          + string("onClose") + u16(0) + string("")), 2
    ]
    assert result["elements"]["count"] == 2
    assert result["elements"]["decoded_records"] == 0
    assert result["actions"]["count"] == 2
    assert result["actions"]["records"][0]["name"] == "onOpen"
    assert result["actions"]["records"][0]["parameters"] == ["call:model:handler"]
    assert result["actions"]["records"][1]["name"] == "onClose"
    assert result["timers"]["count"] == 0
    assert result["rewrite_supported"] is False
    assert sum(4 + x["payload_size"] for x in result["sections"]) + 8 == len(data)


def test_legacy_version_8() -> None:
    actions = u16(1) + string("legacy") + u16(1) + string("noop")
    data = u32(3) + b"NcP" + bytes([8]) + b"".join(
        section(payload) for payload in (string(""), u32(0), actions, u16(0))
    )
    result = inspect_hud(data)
    assert result["actions"]["records"][0]["name"] == "legacy"
    assert result["actions"]["records"][0]["parameters"] == ["noop"]


def test_rejects_bad_marker_truncation_and_trailing_data() -> None:
    data = fixture()
    bad = bytearray(data)
    bad[4:7] = b"Bad"
    cases = (bytes(bad), data[:-1], data + b"x")
    for candidate in cases:
        try:
            inspect_hud(candidate)
            raise AssertionError("malformed HUD data was accepted")
        except HudFormatError:
            pass


def test_rejects_malformed_action_table() -> None:
    payloads = (string(""), u32(0), u16(1), u16(0))
    data = u32(3) + b"NcP" + bytes([12]) + b"".join(
        section(payload) for payload in payloads
    )
    try:
        inspect_hud(data)
        raise AssertionError("malformed action table was accepted")
    except HudFormatError:
        pass


if __name__ == "__main__":
    test_valid_version_12()
    test_legacy_version_8()
    test_rejects_bad_marker_truncation_and_trailing_data()
    test_rejects_malformed_action_table()
    print("PASS: HUD header/section/action parser synthetic regression tests")

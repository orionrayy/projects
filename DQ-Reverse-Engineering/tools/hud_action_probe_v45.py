#!/usr/bin/env python3
"""Read-only parser for v12 HUD action records and tagged values.

The probe reads action-section framing only. It does not rewrite HUD files,
interpret action opcodes, or claim that referenced AI symbols execute in-game.
"""
from __future__ import annotations
import argparse, json, pathlib, re, struct
from functools import lru_cache
from typing import Any
from hud_elements_codec_v42 import parse_hud, HudCodecError
from aim_model_probe_v43 import parse_aim, AimFormatError

MAX_ACTIONS = 100_000
MAX_STATEMENT_BYTES = 2_000_000
MAX_STRING_BYTES = 2_000_000
TAG_RE = re.compile(r"<(\d+),(\d+)>")

class HudActionFormatError(ValueError):
    """Malformed, truncated, or unreasonable HUD action stream."""

class Reader:
    def __init__(self, data: bytes, label: str):
        self.data, self.label, self.pos = data, label, 0
    def take(self, n: int) -> bytes:
        if n < 0 or self.pos + n > len(self.data):
            raise HudActionFormatError(f"{self.label}: truncated at 0x{self.pos:x}; need {n}, have {len(self.data)-self.pos}")
        out = self.data[self.pos:self.pos+n]; self.pos += n; return out
    def u16(self) -> int: return struct.unpack("<H", self.take(2))[0]
    def u32(self) -> int: return struct.unpack("<I", self.take(4))[0]
    def string(self) -> str:
        size = self.u32()
        if size > MAX_STRING_BYTES:
            raise HudActionFormatError(f"{self.label}: unreasonable string length {size} at 0x{self.pos-4:x}")
        return self.take(size).decode("utf-8", errors="surrogateescape")

def parse_action_section(data: bytes, source: str = "<memory>") -> dict[str, Any]:
    r = Reader(data, source)
    count = r.u16()
    if count > MAX_ACTIONS:
        raise HudActionFormatError(f"{source}: unreasonable action count {count}")
    actions = []
    for index in range(count):
        start = r.pos
        name = r.string()
        declared_statement_count = r.u16()
        if declared_statement_count > MAX_ACTIONS:
            raise HudActionFormatError(f"{source}: action[{index}] {name!r}: unreasonable statement count {declared_statement_count}")
        statements = []
        for statement_index in range(declared_statement_count):
            length_offset = r.pos
            length = r.u32()
            if length == 0:
                raise HudActionFormatError(f"{source}: action[{index}] {name!r}: early terminator at statement {statement_index}")
            if length > MAX_STATEMENT_BYTES:
                raise HudActionFormatError(f"{source}: action[{index}] {name!r}: unreasonable statement size {length} at 0x{length_offset:x}")
            statements.append(r.take(length).decode("utf-8", errors="surrogateescape"))
        terminator_offset = r.pos
        if r.u32() != 0:
            raise HudActionFormatError(f"{source}: action[{index}] {name!r}: missing zero terminator at 0x{terminator_offset:x}")
        actions.append({"index": index, "name": name, "declared_statement_count": declared_statement_count,
                        "statements": statements, "statement_count": len(statements),
                        "offset": start, "end_offset": r.pos})
    if r.pos != len(data):
        raise HudActionFormatError(f"{source}: {len(data)-r.pos} trailing byte(s) at 0x{r.pos:x}")
    return {"schema": "hud-action-probe-v45", "source": source, "action_count": count,
            "actions": actions, "section_size": len(data), "rewrite_supported": False}

def tagged_values(statement: str) -> list[dict[str, Any]]:
    """Extract safely bounded <type,length> literal values without decoding opcodes."""
    out = []
    for match in TAG_RE.finditer(statement):
        value_start = match.end()
        type_code, length = int(match.group(1)), int(match.group(2))
        value_end = value_start + length
        if length < 0 or value_end > len(statement):
            continue
        out.append({"type_code": type_code, "value": statement[value_start:value_end],
                    "start": match.start(), "end": value_end})
    return out

@lru_cache(maxsize=4)
def _load_ai_symbol_index(root_text: str) -> dict[str, set[str]]:
    root = pathlib.Path(root_text)
    model_to_symbols: dict[str, set[str]] = {}
    for model_path in root.rglob("*.aim"):
        try:
            model = parse_aim(model_path.read_bytes(), str(model_path))
            model_to_symbols[model_path.stem] = {
                record["name"] for table in model["tables"] for record in table["records"]
            }
        except (OSError, AimFormatError):
            continue
    return model_to_symbols

def inspect_hud(path: pathlib.Path, assets_root: pathlib.Path | None = None) -> dict[str, Any]:
    doc = parse_hud(path.read_bytes(), str(path))
    action_doc = parse_action_section(doc["sections"]["actions"], f"{path}:actions")
    model_to_symbols = _load_ai_symbol_index(str(assets_root.resolve())) if assets_root is not None else {}
    for action in action_doc["actions"]:
        values = [v for statement in action["statements"] for v in tagged_values(statement)]
        action["tagged_values"] = values
        action["candidate_ai_refs"] = []
        for i, value in enumerate(values):
            model_name = value["value"]
            if model_name in model_to_symbols:
                target = values[i + 1]["value"] if i + 1 < len(values) else None
                found = target in model_to_symbols[model_name] if target else False
                action["candidate_ai_refs"].append({"model": model_name, "next_tagged_value": target,
                                                    "symbol_name_found_in_model": found})
    types = sorted({e.element_type for e in doc["elements"]})
    return {"source": str(path), "file_size": len(doc["data"]), "element_count": len(doc["elements"]),
            "element_type_counts": {str(k): sum(1 for e in doc["elements"] if e.element_type == k) for k in types},
            **action_doc}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("hud", nargs="+", type=pathlib.Path)
    p.add_argument("--assets-root", type=pathlib.Path, help="optional root containing extracted Resources/AIModels")
    p.add_argument("--summary", action="store_true")
    p.add_argument("--output-dir", type=pathlib.Path)
    args = p.parse_args()
    if args.output_dir: args.output_dir.mkdir(parents=True, exist_ok=True)
    failures = []; passed = 0; total_actions = 0; total_statements = 0
    for path in args.hud:
        try:
            report = inspect_hud(path, args.assets_root)
            passed += 1; total_actions += report["action_count"]
            total_statements += sum(a["statement_count"] for a in report["actions"])
            output = report
            if args.summary:
                output = {k: report[k] for k in ("source", "file_size", "element_count", "element_type_counts", "section_size", "action_count", "rewrite_supported")}
                output["statement_count"] = sum(a["statement_count"] for a in report["actions"])
                output["multi_statement_actions"] = [a["name"] for a in report["actions"] if a["statement_count"] > 1]
            print(json.dumps(output, ensure_ascii=True))
            if args.output_dir:
                dest = args.output_dir / f"{path.name}.json"
                if dest.exists(): raise HudActionFormatError(f"refusing to overwrite existing report: {dest}")
                dest.write_text(json.dumps(report, indent=2, ensure_ascii=True)+"\n", encoding="utf-8")
        except (OSError, HudCodecError, HudActionFormatError, struct.error) as exc:
            failures.append({"path": str(path), "error": str(exc)})
            print(json.dumps({"path": str(path), "status": "FAIL", "error": str(exc)}, ensure_ascii=True))
    print(json.dumps({"schema": "hud-action-probe-v45-run", "tested": len(args.hud), "passed": passed,
                      "failed": len(failures), "actions": total_actions, "statements": total_statements,
                      "failures": failures, "rewrite_supported": False}, indent=2))
    return 0 if not failures else 1
if __name__ == "__main__": raise SystemExit(main())

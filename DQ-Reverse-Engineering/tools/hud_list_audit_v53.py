#!/usr/bin/env python3
"""Read-only inventory of serialized v12 HUD List elements; no files are rewritten."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from hud_elements_codec_v42 import HudCodecError, parse_hud

RESOURCE_FIELDS = (
    "list_resource_208", "list_resource_pair_0", "list_resource_pair_1",
    "list_resource_tail_0", "list_resource_tail_1", "list_resource_tail_2",
    "list_resource_tail_3", "list_resource_tail_4", "list_resource_tail_5",
    "list_resource_tail_6", "list_resource_tail_7",
)

def audit_bytes(data: bytes, source: str = "<memory>") -> dict[str, Any]:
    document = parse_hud(data, source)
    elements = document["elements"]
    lists = []
    for element in elements:
        if element.element_type != 3:
            continue
        fields = {name: element.field(name).value for name in (
            "name", "label", "position_x", "position_y", "size_x", "size_y",
            "visible_flag", "list_flag_1f4", "list_float_a_0", "list_float_a_1",
            "list_float_a_2", "list_flag_0", "list_flag_1", "list_flag_2",
            "list_float_b_0", "list_float_b_1", "list_string_210", "list_float_220",
            "list_float_tail_0", "list_float_tail_1"
        )}
        resources = {name: element.field(name).value for name in RESOURCE_FIELDS}
        nonempty = [name for name, value in resources.items() if value]
        lists.append({
            "index": element.index,
            "offset": element.offset,
            "serialized_record_bytes": len(element.raw),
            **fields,
            "resource_fields": resources,
            "nonempty_resource_fields": nonempty,
            "row_template_resource_present": bool(nonempty),
            "runtime_item_population_serialized": False,
        })
    return {
        "schema": "hud-list-audit-v53",
        "source": source,
        "file_size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "hud_version": 12,
        "element_count": len(elements),
        "type3_list_count": len(lists),
        "list_elements": lists,
        "runtime_boundary": {
            "static_record_is_not_proof_of_runtime_population": True,
            "native_add_item_and_selection_api_must_be_called_by_game_model": True,
            "this_tool_does_not_decode_action_bytecode_or_generate_native_model_code": True,
        },
    }

def audit_path(path: Path) -> dict[str, Any]:
    try:
        return audit_bytes(path.read_bytes(), str(path))
    except (OSError, HudCodecError) as exc:
        raise ValueError(f"{path}: {exc}") from exc

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hud", nargs="+", type=Path, help="one or more decoded v12 .hud files")
    parser.add_argument("--output-dir", type=Path, help="optional directory for JSON reports; existing files are never overwritten")
    args = parser.parse_args()
    failures = []
    for path in args.hud:
        try:
            report = audit_path(path)
            if args.output_dir:
                args.output_dir.mkdir(parents=True, exist_ok=True)
                output = args.output_dir / (path.name + ".list-audit-v53.json")
                if output.exists():
                    raise FileExistsError(f"refusing to overwrite {output}")
                output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(json.dumps({
                "source": report["source"],
                "sha256": report["sha256"],
                "element_count": report["element_count"],
                "type3_list_count": report["type3_list_count"],
                "lists": [{
                    "name": x["name"], "label": x["label"],
                    "record_bytes": x["serialized_record_bytes"],
                    "row_template_resource_present": x["row_template_resource_present"],
                    "nonempty_resource_fields": x["nonempty_resource_fields"],
                } for x in report["list_elements"]],
            }, ensure_ascii=False))
        except (OSError, ValueError, HudCodecError) as exc:
            failures.append(str(exc))
            print(json.dumps({"source": str(path), "status": "FAIL", "error": str(exc)}, ensure_ascii=False))
    if failures:
        print(json.dumps({"status": "FAIL", "errors": failures}, indent=2))
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a separate debug.hud candidate with one static +100K Gold action.

This is only a data-level experiment. It never overwrites the source file and
it does not build or patch an APK or STK archive.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hud_elements_codec_v42 import parse_hud, encode_hud, HudCodecError
from hud_action_probe_v45 import parse_action_section, HudActionFormatError
from hud_action_serializer_v46 import encode_action_section, append_action

STATEMENT = "<023><8,3>013<2,10>uai_gp_hud<2,7>onDebug<1,5>6.000"

def build(source: pathlib.Path, output: pathlib.Path) -> dict:
    if source.resolve() == output.resolve():
        raise ValueError("refusing to overwrite the source HUD")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing candidate: {output}")
    original = source.read_bytes()
    doc = parse_hud(original, str(source))
    original_elements = len(doc["elements"])
    action_doc = parse_action_section(doc["sections"]["actions"], f"{source}:actions")
    if encode_action_section(action_doc) != doc["sections"]["actions"]:
        raise ValueError("source action table did not pass exact no-op roundtrip")
    if any(e.field("name").value == "gold_btn" for e in doc["elements"]):
        raise ValueError("source already contains gold_btn")
    if any(a["name"] == "onAddGold" for a in action_doc["actions"]):
        raise ValueError("source already contains onAddGold action")
    template = next((e for e in doc["elements"] if e.element_type == 2 and e.field("name").value == "hp_btn"), None)
    if template is None:
        raise ValueError("expected debug HUD button hp_btn template is missing")
    button = copy.deepcopy(template)
    button.index = len(doc["elements"])
    button.offset = -1
    button.set("name", "gold_btn")
    button.set("type2_string_140", "Gold +100K")
    button.set("type2_string_178", "onAddGold")
    # Existing Character and Heroic buttons are centered at +0.2 and -0.2.
    button.set("position_y", 0.0)
    doc["elements"].append(button)
    append_action(action_doc, "onAddGold", [STATEMENT])
    doc["sections"]["actions"] = encode_action_section(action_doc)
    candidate = encode_hud(doc)
    # Fail closed: validate output structure, action binding, and encoded route.
    check = parse_hud(candidate, str(output))
    action_check = parse_action_section(check["sections"]["actions"], f"{output}:actions")
    gold_button = next((e for e in check["elements"] if e.field("name").value == "gold_btn"), None)
    gold_action = next((a for a in action_check["actions"] if a["name"] == "onAddGold"), None)
    if len(check["elements"]) != original_elements + 1:
        raise ValueError("candidate element count did not increase by exactly one")
    if gold_button is None or gold_button.field("type2_string_178").value != "onAddGold":
        raise ValueError("candidate button-to-action binding failed verification")
    if gold_action is None or gold_action["statements"] != [STATEMENT]:
        raise ValueError("candidate action payload failed verification")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(candidate)
    return {
        "source": str(source), "output": str(output),
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "source_bytes": len(original), "candidate_bytes": len(candidate),
        "source_elements": original_elements, "candidate_elements": len(check["elements"]),
        "source_actions": action_check["action_count"] - 1,
        "candidate_actions": action_check["action_count"],
        "gold_button_name": gold_button.field("name").value,
        "gold_button_label": gold_button.field("type2_string_140").value,
        "callback": gold_button.field("type2_string_178").value,
        "callback_target": "uai_gp_hud.onDebug(6.0)",
        "runtime_verified": False, "apk_built": False, "stk_repacked": False
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.source, args.output), indent=2))
        return 0
    except (OSError, ValueError, HudCodecError, HudActionFormatError) as exc:
        parser.error(str(exc))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a separate pause.hud candidate with a Gold +100K test button.

This is a data-level feasibility probe only. It does not create an APK, edit
an input archive in place, or mark the action as runtime-verified.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hud_elements_codec_v42 import parse_hud, encode_hud, HudCodecError
from hud_action_probe_v45 import parse_action_section, HudActionFormatError
from hud_action_serializer_v46 import append_action, encode_action_section

BUTTON_NAME = "gold_reward_100k_btn"
ACTION_NAME = "onAddGold100K"
BUTTON_LABEL = "Gold +100K"
STATEMENT = "<023><8,3>013<2,10>uai_gp_hud<2,7>onDebug<1,5>6.000"
SOURCE_SHA256 = "12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395"

def build(source: pathlib.Path, output: pathlib.Path, allow_unpinned_source: bool = False) -> dict:
    if source.resolve() == output.resolve():
        raise ValueError("refusing to overwrite source HUD")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing candidate: {output}")
    original = source.read_bytes()
    source_hash = hashlib.sha256(original).hexdigest()
    if not allow_unpinned_source and source_hash != SOURCE_SHA256:
        raise ValueError(f"source SHA-256 mismatch; expected {SOURCE_SHA256}, got {source_hash}")
    doc = parse_hud(original, str(source))
    source_elements = len(doc["elements"])
    action_doc = parse_action_section(doc["sections"]["actions"], f"{source}:actions")
    source_actions = action_doc["action_count"]
    if encode_action_section(action_doc) != doc["sections"]["actions"]:
        raise ValueError("source action table failed exact no-op round trip")
    if any(e.field("name").value == BUTTON_NAME for e in doc["elements"]):
        raise ValueError(f"source already contains {BUTTON_NAME}")
    if any(a["name"] == ACTION_NAME for a in action_doc["actions"]):
        raise ValueError(f"source already contains {ACTION_NAME}")
    template = next((e for e in doc["elements"]
                     if e.element_type == 2 and e.field("name").value == "pickup_btn"
                     and e.field("label").value == "GameplayMenu"), None)
    if template is None:
        raise ValueError("expected GameplayMenu pickup_btn template is missing")
    button = copy.deepcopy(template)
    button.index = len(doc["elements"])
    button.offset = -1
    button.set("name", BUTTON_NAME)
    button.set("label", "GameplayMenu")
    button.set("type2_string_140", BUTTON_LABEL)
    button.set("type2_string_178", ACTION_NAME)
    button.set("position_x", 0.66)
    button.set("position_y", -0.7)
    # Existing Pickup occupies x=-0.66 on this row; use its empty right-side slot.
    doc["elements"].append(button)
    append_action(action_doc, ACTION_NAME, [STATEMENT])
    doc["sections"]["actions"] = encode_action_section(action_doc)
    candidate = encode_hud(doc)
    check = parse_hud(candidate, str(output))
    check_actions = parse_action_section(check["sections"]["actions"], f"{output}:actions")
    found = [e for e in check["elements"] if e.field("name").value == BUTTON_NAME]
    actions = [a for a in check_actions["actions"] if a["name"] == ACTION_NAME]
    if len(check["elements"]) != source_elements + 1:
        raise ValueError("element count must increase by exactly one")
    if check_actions["action_count"] != source_actions + 1:
        raise ValueError("action count must increase by exactly one")
    if len(found) != 1 or found[0].field("label").value != "GameplayMenu":
        raise ValueError("new button parent/group failed validation")
    if found[0].field("type2_string_140").value != BUTTON_LABEL:
        raise ValueError("new button label failed validation")
    if found[0].field("type2_string_178").value != ACTION_NAME:
        raise ValueError("button callback binding failed validation")
    if len(actions) != 1 or actions[0]["statements"] != [STATEMENT]:
        raise ValueError("new action route failed validation")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(candidate)
    return {
        "schema": "pause-options-gold-row-v50",
        "source": str(source), "output": str(output),
        "source_sha256": source_hash, "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "source_bytes": len(original), "candidate_bytes": len(candidate),
        "source_elements": source_elements, "candidate_elements": len(check["elements"]),
        "source_actions": source_actions, "candidate_actions": check_actions["action_count"],
        "button_name": BUTTON_NAME, "button_label": BUTTON_LABEL, "button_group": "GameplayMenu",
        "button_position": {"x": 0.66, "y": -0.7}, "callback_name": ACTION_NAME,
        "callback_statement": STATEMENT, "native_route_candidate": "uai_gp_hud.onDebug(6.0)",
        "static_effect_candidate": "RewardGold(100000.0)",
        "runtime_verified": False, "apk_built": False, "stk_repacked": False
    }

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=pathlib.Path)
    p.add_argument("output", type=pathlib.Path)
    p.add_argument("--allow-unpinned-source", action="store_true",
                   help="disable source hash pin for synthetic fixtures only")
    args = p.parse_args()
    try:
        print(json.dumps(build(args.source, args.output, args.allow_unpinned_source), indent=2))
        return 0
    except (OSError, ValueError, HudCodecError, HudActionFormatError) as exc:
        p.exit(2, f"ERROR: {exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())

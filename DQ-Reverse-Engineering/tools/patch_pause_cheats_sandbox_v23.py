#!/usr/bin/env python3
"""Fail-closed v23 patch for Dungeon Quest 3.3.2.0 Pause HUD.

Preserves the original onShowSocial action ID and all six menu-state parameters.
Only its final route call is redirected to the existing uai_gp_hud.onDebug(0) call.
No native methods, purchase receipts, entitlements, or cloud state are modified.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

SECTIONS=("general_attributes","elements","actions","timers")
MAGIC={b"NcP",b"NcX",b"NcI"}
OLD_LABEL="Social/IAP"
NEW_LABEL="Cheat Mode"  # Must preserve serialized byte count (10 UTF-8 bytes).
CALLBACK="onShowSocial" # Preserve the element-to-action lookup key.
OLD_ROUTE="<023><8,3>013<2,14>uai_gp_options<2,9>onShowTab<1,5>3.000"
DEBUG_ROUTE="<023><8,3>013<2,10>uai_gp_hud<2,7>onDebug<1,5>0.000"

class PatchError(ValueError): pass

def lp(value:str)->bytes:
    raw=value.encode("utf-8")
    return struct.pack("<I",len(raw))+raw

def read_lp(data:bytes,pos:int,what:str)->tuple[str,int]:
    if pos+4>len(data): raise PatchError(f"truncated string length: {what}")
    size=struct.unpack_from("<I",data,pos)[0]; pos+=4
    if size>len(data)-pos: raise PatchError(f"string exceeds payload: {what}")
    try: return data[pos:pos+size].decode("utf-8"),pos+size
    except UnicodeDecodeError as exc: raise PatchError(f"invalid UTF-8: {what}") from exc

def split_sections(data:bytes)->tuple[dict[str,bytes],int]:
    if len(data)<8 or struct.unpack_from("<I",data)[0]!=3 or data[4:7] not in MAGIC:
        raise PatchError("unrecognized HUD header")
    version=data[7]; pos=8; sections={}
    for name in SECTIONS:
        if pos+4>len(data): raise PatchError(f"missing {name} section header")
        size=struct.unpack_from("<I",data,pos)[0]; pos+=4
        if size>len(data)-pos: raise PatchError(f"{name} section size exceeds file")
        sections[name]=data[pos:pos+size]; pos+=size
    if pos!=len(data): raise PatchError("trailing bytes after HUD sections")
    return sections,version

def parse_actions(payload:bytes,version:int)->tuple[list[dict],list[bytes]]:
    if len(payload)<2: raise PatchError("short action table")
    count=struct.unpack_from("<H",payload)[0]; pos=2; actions=[]; raw_records=[]
    for i in range(count):
        start=pos
        name,pos=read_lp(payload,pos,f"action[{i}].name")
        if pos+2>len(payload): raise PatchError("truncated action parameter count")
        argc=struct.unpack_from("<H",payload,pos)[0]; pos+=2; params=[]
        for j in range(argc):
            value,pos=read_lp(payload,pos,f"{name}.param[{j}]"); params.append(value)
        extra=""
        if version>8: extra,pos=read_lp(payload,pos,f"{name}.extra")
        actions.append({"name":name,"parameters":params,"extra_script":extra})
        raw_records.append(payload[start:pos])
    if pos!=len(payload): raise PatchError("unparsed bytes remain in action section")
    return actions,raw_records

def serialize_action(action:dict,version:int)->bytes:
    params=action["parameters"]
    if len(params)>65535: raise PatchError("action has too many parameters")
    out=bytearray(lp(action["name"])+struct.pack("<H",len(params)))
    for value in params: out+=lp(value)
    if version>8: out+=lp(action.get("extra_script",""))
    return bytes(out)

def rebuild_sections(template:bytes,sections:dict[str,bytes])->bytes:
    out=bytearray(template[:8])
    for name in SECTIONS:
        out+=struct.pack("<I",len(sections[name]))+sections[name]
    return bytes(out)

def patch_hud(source:bytes)->tuple[bytes,dict]:
    if len(NEW_LABEL.encode("utf-8"))!=len(OLD_LABEL.encode("utf-8")):
        raise PatchError("label replacement must preserve UTF-8 byte length")
    sections,version=split_sections(source)
    if version!=12: raise PatchError(f"expected HUD v12, got {version}")
    actions,raw=parse_actions(sections["actions"],version)
    indexes=[i for i,a in enumerate(actions) if a["name"]==CALLBACK]
    if len(indexes)!=1: raise PatchError(f"expected one {CALLBACK} action, got {len(indexes)}")
    index=indexes[0]; target=actions[index]
    if len(target["parameters"])!=7:
        raise PatchError(f"expected the audited seven-parameter {CALLBACK} action, got {len(target['parameters'])}")
    if target["parameters"][-1]!=OLD_ROUTE:
        raise PatchError("original route parameter mismatch; refusing to patch a different HUD")
    label_matches=sections["elements"].count(lp(OLD_LABEL))
    if label_matches!=1: raise PatchError(f"expected one {OLD_LABEL!r} label, got {label_matches}")
    callback_matches=sections["elements"].count(lp(CALLBACK))
    if callback_matches!=1: raise PatchError(f"expected one {CALLBACK!r} element callback, got {callback_matches}")
    new_elements=sections["elements"].replace(lp(OLD_LABEL),lp(NEW_LABEL),1)
    if len(new_elements)!=len(sections["elements"]):
        raise PatchError("element section byte count changed despite equal-length label")
    updated=dict(target); updated["parameters"]=list(target["parameters"])
    updated["parameters"][-1]=DEBUG_ROUTE
    new_raw=list(raw); new_raw[index]=serialize_action(updated,version)
    new_actions=struct.pack("<H",len(new_raw))+b"".join(new_raw)
    rebuilt=dict(sections); rebuilt["elements"]=new_elements; rebuilt["actions"]=new_actions
    output=rebuild_sections(source,rebuilt)
    checked,version2=split_sections(output)
    parsed,checked_raw=parse_actions(checked["actions"],version2)
    if version2!=version or len(parsed)!=len(actions): raise PatchError("round-trip header/action count mismatch")
    if checked["general_attributes"]!=sections["general_attributes"] or checked["timers"]!=sections["timers"]:
        raise PatchError("unexpected section mutation")
    if checked["elements"].count(lp(NEW_LABEL))!=1 or checked["elements"].count(lp(CALLBACK))!=1:
        raise PatchError("patched label or original callback lookup missing")
    for i,(before,after) in enumerate(zip(actions,parsed)):
        if i==index:
            if after["name"]!=CALLBACK or len(after["parameters"])!=7:
                raise PatchError("callback identity or parameter count changed")
            if after["parameters"][:-1]!=before["parameters"][:-1]:
                raise PatchError("one or more of the first six state parameters changed")
            if after["parameters"][-1]!=DEBUG_ROUTE:
                raise PatchError("debug route was not serialized correctly")
        elif raw[i]!=checked_raw[i]:
            raise PatchError(f"unrelated action record changed: {before['name']}")
    report={
        "schema":"dq-pause-cheats-sandbox-v23",
        "source_sha256":hashlib.sha256(source).hexdigest(),
        "output_sha256":hashlib.sha256(output).hexdigest(),
        "source_size_bytes":len(source),"output_size_bytes":len(output),
        "hud_version":version,"action_count":len(actions),"target_action_index":index,
        "label":{"from":OLD_LABEL,"to":NEW_LABEL,"utf8_bytes_preserved":True},
        "callback_name_preserved":True,"element_callback_reference_preserved":True,
        "action_parameter_count_before":7,"action_parameter_count_after":len(parsed[index]["parameters"]),
        "first_six_state_parameters_preserved":True,
        "changed_parameter":{"from":OLD_ROUTE,"to":DEBUG_ROUTE},
        "unrelated_action_records_byte_identical":True,
        "changed_sections":["elements","actions"],
        "runtime_status":"NOT_RUNTIME_VERIFIED"
    }
    return output,report

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("output",type=Path)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    output,report=patch_hud(args.source.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_bytes(output)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except (OSError,struct.error,PatchError) as exc: raise SystemExit(f"ERROR: {exc}")

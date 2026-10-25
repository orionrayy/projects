#!/usr/bin/env python3
"""Fail-closed validator for the v39 scrollable cheat workbench and catalog."""
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path

def validate(html_path: Path, catalog_path: Path, matrix_path: Path | None = None):
    errors=[]
    html=html_path.read_text(encoding="utf-8")
    cat=json.loads(catalog_path.read_text(encoding="utf-8"))
    match=re.search(r"const CATALOG=(\{[\s\S]*?\});\s*\nconst \$=", html)
    if not match:
        return ["Embedded catalog JSON was not found in the HTML"]
    try:
        embedded=json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        return [f"Embedded catalog JSON is invalid: {exc}"]
    cheats=cat.get("cheats",[])
    ids=[x.get("id") for x in cheats]
    if len(cheats)!=222 or cat.get("count")!=222:
        errors.append(f"Expected 222 catalog rows; got {len(cheats)}, declared {cat.get('count')}")
    if len(set(ids))!=222:
        errors.append("Catalog stable IDs must be unique")
    cats=cat.get("categories",[])
    if len(cats)!=14 or set(cats)!={x.get("category") for x in cheats}:
        errors.append("Catalog must represent all 14 category names exactly")
    if embedded != cat:
        errors.append("Embedded HTML catalog differs from standalone JSON catalog")
    if any(not x.get("label") or not x.get("description") or not x.get("tags") for x in cheats):
        errors.append("Each catalog row must include label, description and tags")
    if any(x.get("integration_status")!="requires_game_adapter" for x in cheats):
        errors.append("Unverified game handlers must remain blocked")
    numeric=[x for x in cheats if x.get("control") in ("slider","range")]
    for x in numeric:
        if x.get("min") is None or x.get("max") is None or x.get("step") is None:
            errors.append(f"Numeric entry lacks bounds/step: {x.get('id')}")
            continue
        if x["min"]>x["max"] or x["step"]<=0:
            errors.append(f"Invalid bounds/step: {x.get('id')}")
        if x.get("control")=="range":
            d=x.get("default")
            if not isinstance(d,dict) or d.get("min") is None or d.get("max") is None or d["min"]>d["max"] or d["min"]<x["min"] or d["max"]>x["max"]:
                errors.append(f"Invalid range default: {x.get('id')}")
        else:
            d=x.get("default")
            if d is None or not x["min"]<=d<=x["max"]:
                errors.append(f"Invalid numeric default: {x.get('id')}")
    if "html,body{height:100%;height:100dvh;overflow:hidden;overscroll-behavior:none}" not in html:
        errors.append("Outer document must be fixed to viewport and non-scrollable")
    if not re.search(r"\.cheat-scroll\{[^}]*overflow-y:auto",html):
        errors.append("Cheat list must have its own vertical scroll container")
    if not re.search(r"const items=\[\['−10'",html) or "'−1'" not in html or "'+1'" not in html or "'+10'" not in html:
        errors.append("Numeric controls must expose −10, −1, +1 and +10 steppers")
    if not re.search(r"input\.readOnly=true;input\.inputMode='none'",html):
        errors.append("Gold amount input must not depend on the system keyboard")
    if "gameAdapterConnected:false" not in html and "gameAdapterConnected: false" not in html:
        errors.append("Exports must declare gameAdapterConnected=false")
    if matrix_path:
        matrix=json.loads(matrix_path.read_text(encoding="utf-8"))
        me=matrix.get("entries",[])
        if len(me)!=222 or {e.get("id") for e in me}!=set(ids):
            errors.append("Runtime matrix must contain one entry per catalog ID")
        if matrix.get("counts_by_game_status",{}).get("runtime_verified")!=0:
            errors.append("Runtime verified count must remain zero until device evidence exists")
        if any(e.get("runtime_verified") is True for e in me):
            errors.append("Matrix cannot claim runtime-verified entries without explicit evidence")
    return errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--html",type=Path,required=True)
    p.add_argument("--catalog",type=Path,required=True)
    p.add_argument("--matrix",type=Path)
    a=p.parse_args()
    e=validate(a.html,a.catalog,a.matrix)
    if e:
        for x in e: print("FAIL:",x)
        raise SystemExit(1)
    cat=json.loads(a.catalog.read_text(encoding="utf-8"))
    print(f"PASS: {len(cat['cheats'])} entries, {len(cat['categories'])} categories; independent internal scroll; button-only numeric steppers; custom keypad Gold; no false runtime claims.")
if __name__=="__main__":
    main()

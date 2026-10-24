#!/usr/bin/env python3
"""Convert known cash-only Vanity.xml rows into gameplay-gold unlocks.

This is a data-only draft. It does not remove the billing registry or implement
all IAP categories. Default prices are proposed balance values, not source facts.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import shutil
import xml.etree.ElementTree as ET

PRICE_TO_GOLD = { "0.99": 250000, "1.99": 500000, "2.99": 750000,
                  "3.99": 1000000, "5.99": 1500000 }
XML_PATH = pathlib.Path("Resources/XML/Vanity.xml")

def clean(text):
    return (text or "").strip()

def apply_patch(source_root: pathlib.Path, output_root: pathlib.Path,
                price_to_gold=PRICE_TO_GOLD) -> dict:
    source_root = source_root.resolve()
    output_root = output_root.resolve()
    if not (source_root / XML_PATH).is_file():
        raise ValueError("source does not contain %s" % XML_PATH)
    if source_root == output_root or source_root in output_root.parents or output_root in source_root.parents:
        raise ValueError("source and output directories must be separate and non-overlapping")
    if output_root.exists():
        raise ValueError("output directory already exists; refusing to overwrite")
    parsed = ET.parse(source_root / XML_PATH)
    root = parsed.getroot()
    converted, unresolved, conflicts = [], [], []
    for row in root.iter("Row"):
        name = clean(row.findtext("Name"))
        price = clean(row.findtext("Price"))
        gold = clean(row.findtext("Gold"))
        if not price:
            continue
        try:
            numeric_price = "%.2f" % float(price)
        except ValueError:
            unresolved.append({"name": name, "price": price, "reason": "non-numeric price"})
            continue
        if gold:
            conflicts.append({"name": name, "price": price, "gold": gold, "reason": "both price and gold are populated"})
            continue
        if numeric_price not in price_to_gold:
            unresolved.append({"name": name, "price": price, "reason": "no approved draft tier"})
            continue
        gold_value = int(price_to_gold[numeric_price])
        if gold_value <= 0:
            raise ValueError("gold tier must be positive for %s" % numeric_price)
        gold_node = row.find("Gold")
        if gold_node is None:
            gold_node = ET.SubElement(row, "Gold")
        gold_node.text = str(gold_value)
        price_node = row.find("Price")
        if price_node is not None:
            price_node.text = ""
        converted.append({"name": name, "price_removed": numeric_price, "gold_added": gold_value})
    shutil.copytree(source_root, output_root)
    target = output_root / XML_PATH
    parsed.write(target, encoding="utf-8", xml_declaration=True)
    report = {
        "scope": "cosmetics-only data patch",
        "warning": "does not disable IAP registry or patch Java billing callbacks",
        "source": str(source_root), "output": str(output_root),
        "converted_count": len(converted), "converted": converted,
        "unresolved": unresolved, "conflicts": conflicts,
        "proposed_price_to_gold": {k:int(v) for k,v in price_to_gold.items()}
    }
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=pathlib.Path)
    p.add_argument("output", type=pathlib.Path)
    p.add_argument("--report", type=pathlib.Path)
    a = p.parse_args()
    try:
        result = apply_patch(a.source, a.output)
        raw = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if a.report:
            a.report.parent.mkdir(parents=True, exist_ok=True)
            a.report.write_text(raw, encoding="utf-8")
        print(raw)
    except (OSError, ValueError, ET.ParseError) as exc:
        p.exit(2, "ERROR: %s\n" % exc)

if __name__ == "__main__":
    main()

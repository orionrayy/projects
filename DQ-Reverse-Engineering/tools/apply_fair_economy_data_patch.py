#!/usr/bin/env python3
"""Patch IAP-linked vanity assets to earnable gold; do not alter billing code."""
from __future__ import annotations
import argparse, json, pathlib, shutil, xml.etree.ElementTree as ET

CASH_TO_GOLD = {"0.99": 250_000, "1.99": 500_000, "2.99": 750_000,
                "3.99": 1_000_000, "5.99": 1_500_000}
# Explicit proposals for existing IAP Vanity rows with neither Price nor Gold.
UNPRICED_TO_GOLD = {72: 500_000, 73: 250_000}
VANITY = pathlib.Path("Resources/XML/Vanity.xml")
IAP = pathlib.Path("Resources/XML/IAP.xml")
SHOP = pathlib.Path("Resources/XML/Shop.xml")

def text(row, key):
    return (row.findtext(key) or "").strip()

def number(value, label):
    try: result = int((value or "").strip())
    except (ValueError, AttributeError) as exc: raise ValueError(f"{label} must be an integer: {value!r}") from exc
    if result < 0: raise ValueError(f"{label} must be non-negative")
    return result

def shop_references(root):
    schema = root.find("Schema")
    if schema is None or any(schema.find(c) is None for c in ("Tab1", "Tab2", "Tab3")):
        raise ValueError("Shop.xml must contain Tab1/Tab2/Tab3 schema")
    refs, row_ids = set(), []
    for row in root.findall("Row"):
        if row.get("id") is not None: row_ids.append(number(row.get("id"), "Shop row id"))
        for col in ("Tab1", "Tab2", "Tab3"):
            val = text(row, col)
            if val: refs.add(number(val, f"Shop.{col}"))
    return refs, row_ids

def add_shop_reference(root, vanity_id):
    refs, row_ids = shop_references(root)
    if vanity_id in refs: return False
    row = ET.Element("Row", {"id": str(max(row_ids, default=0) + 1)})
    for col in ("Tab1", "Tab2", "Tab3"):
        cell = ET.SubElement(row, col)
        if col == "Tab3": cell.text = str(vanity_id)
    root.append(row)
    return True

def apply_patch(source, output):
    source, output = pathlib.Path(source).resolve(), pathlib.Path(output).resolve()
    for rel in (VANITY, IAP, SHOP):
        if not (source / rel).is_file(): raise ValueError(f"missing required source table: {rel}")
    if source == output or source in output.parents or output in source.parents:
        raise ValueError("source and output directories must be separate and non-overlapping")
    if output.exists(): raise ValueError("output directory exists; refusing to overwrite")

    vanity_tree = ET.parse(source / VANITY); vanity_root = vanity_tree.getroot()
    iap_root = ET.parse(source / IAP).getroot()
    shop_tree = ET.parse(source / SHOP); shop_root = shop_tree.getroot()
    iap_names = {text(r, "Name") for r in iap_root.findall("Row") if text(r, "Name")}
    shop_refs_before, _ = shop_references(shop_root)
    linked_ids, converted, newly_priced, existing_gold = set(), [], [], []
    review, conflicts = [], []
    seen_ids = set()

    for row in vanity_root.findall("Row"):
        rid = number(row.get("id"), "Vanity row id")
        if rid in seen_ids: raise ValueError(f"duplicate Vanity row id: {rid}")
        seen_ids.add(rid)
        name, sku, price, gold = text(row, "Name"), f"vanity{rid}", text(row, "Price"), text(row, "Gold")
        if sku not in iap_names: continue
        linked_ids.add(rid)
        if price and gold:
            conflicts.append({"row_id": rid, "sku": sku, "name": name, "price": price, "gold": gold})
            continue
        if price:
            try: tier = f"{float(price):.2f}"
            except ValueError:
                review.append({"row_id": rid, "sku": sku, "reason": "non-numeric Price", "value": price}); continue
            if tier not in CASH_TO_GOLD:
                review.append({"row_id": rid, "sku": sku, "reason": "no approved conversion tier", "value": tier}); continue
            target = row.find("Gold")
            if target is None: target = ET.SubElement(row, "Gold")
            target.text = str(CASH_TO_GOLD[tier])
            price_node = row.find("Price")
            if price_node is not None: price_node.text = ""
            converted.append({"row_id": rid, "sku": sku, "name": name, "old_price": tier,
                              "new_gold": CASH_TO_GOLD[tier], "listed_before": rid in shop_refs_before})
        elif gold:
            existing_gold.append({"row_id": rid, "sku": sku, "name": name, "gold": number(gold, "Vanity.Gold")})
        elif rid in UNPRICED_TO_GOLD:
            target = row.find("Gold")
            if target is None: target = ET.SubElement(row, "Gold")
            target.text = str(UNPRICED_TO_GOLD[rid])
            added = add_shop_reference(shop_root, rid)
            newly_priced.append({"row_id": rid, "sku": sku, "name": name,
                                 "new_gold": UNPRICED_TO_GOLD[rid], "added_to_shop": added})
        else:
            review.append({"row_id": rid, "sku": sku, "name": name,
                           "reason": "IAP-linked Vanity row has neither Price nor Gold and no explicit mapping"})

    # Copy only after inputs and decisions have been parsed. IAP.xml is never edited.
    shutil.copytree(source, output)
    vanity_tree.write(output / VANITY, encoding="utf-8", xml_declaration=True)
    shop_tree.write(output / SHOP, encoding="utf-8", xml_declaration=True)
    out_vanity = ET.parse(output / VANITY).getroot()
    by_id = {number(r.get("id"), "output Vanity id"): r for r in out_vanity.findall("Row")}
    remaining = []
    for rid in sorted(linked_ids):
        r = by_id[rid]
        if text(r, "Price") or not text(r, "Gold"):
            remaining.append({"row_id": rid, "sku": f"vanity{rid}", "price": text(r, "Price"), "gold": text(r, "Gold")})
    out_shop = ET.parse(output / SHOP).getroot()
    refs_after, _ = shop_references(out_shop)
    added_ids = set(UNPRICED_TO_GOLD) - shop_refs_before
    missing_shop_refs = sorted(added_ids - refs_after)
    report = {
      "schema_version": 2, "scope": "Vanity data-only earnability patch",
      "source": str(source), "output": str(output), "iap_xml_modified": False,
      "iap_name_count": len(iap_names), "vanity_rows": len(vanity_root.findall("Row")),
      "iap_linked_vanity_rows": len(linked_ids), "converted_cash_count": len(converted), "converted_cash": converted,
      "newly_priced_count": len(newly_priced), "newly_priced": newly_priced,
      "existing_gold_count": len(existing_gold), "existing_gold": existing_gold,
      "manual_review": review, "conflicts": conflicts, "remaining_iap_vanity_without_gold": remaining,
      "shop_rows_before": len(ET.parse(source / SHOP).getroot().findall("Row")),
      "shop_rows_after": len(out_shop.findall("Row")), "missing_new_shop_refs": missing_shop_refs,
      "cash_to_gold_proposal": CASH_TO_GOLD, "unpriced_iap_proposal": UNPRICED_TO_GOLD,
      "warning": "Does not remove IAP.xml SKUs, billing wrappers, ad runtime, receipts, or non-Vanity IAP families."
    }
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=pathlib.Path); p.add_argument("output", type=pathlib.Path); p.add_argument("--report", type=pathlib.Path)
    a = p.parse_args()
    try:
        report = apply_patch(a.source, a.output)
        raw = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if a.report:
            a.report.parent.mkdir(parents=True, exist_ok=True); a.report.write_text(raw, encoding="utf-8")
        print(raw)
        return 1 if report["manual_review"] or report["conflicts"] or report["remaining_iap_vanity_without_gold"] or report["missing_new_shop_refs"] else 0
    except (OSError, ValueError, ET.ParseError) as exc:
        p.exit(2, f"ERROR: {exc}\n")
if __name__ == "__main__": raise SystemExit(main())

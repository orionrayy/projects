#!/usr/bin/env python3
"""Reconcile IAP, Vanity and Shop XML tables against a canonical SKU matrix.

This tool verifies decoded-table identity/references. It does not prove native runtime
behavior, billing removal, reward persistence, UI reachability, or APK installability.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

TABLES = ("IAP.xml", "Vanity.xml", "Shop.xml", "Items.xml", "Dictionary.xml")
ALLOWED_PATCHED_TABLES = {"Shop.xml", "Vanity.xml"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_table(root: Path, name: str) -> tuple[dict[str, dict[str, str | None]], str]:
    path = root / "Resources" / "XML" / name
    if not path.is_file():
        raise FileNotFoundError(f"missing required asset table: {path}")
    root_node = ET.parse(path).getroot()
    if root_node.tag != Path(name).stem:
        raise ValueError(f"unexpected root for {path}: {root_node.tag!r}")
    rows: dict[str, dict[str, str | None]] = {}
    for node in root_node.findall("Row"):
        row_id = node.attrib.get("id")
        if not row_id or row_id in rows:
            raise ValueError(f"missing/duplicate row id in {path}: {row_id!r}")
        rows[row_id] = {child.tag: child.text for child in node}
    return rows, sha256(path)


def shop_tab3_refs(rows: dict[str, dict[str, str | None]]) -> set[int]:
    refs: set[int] = set()
    for row in rows.values():
        value = row.get("Tab3")
        if value is None or value == "":
            continue
        if not value.isdigit():
            raise ValueError(f"non-numeric Shop.xml Tab3 reference: {value!r}")
        refs.add(int(value))
    return refs


def audit(source_root: Path, patched_root: Path | None, matrix_path: Path, patch_report_path: Path | None) -> dict[str, Any]:
    source_tables = {name: read_table(source_root, name) for name in TABLES}
    source_rows = {name: pair[0] for name, pair in source_tables.items()}
    source_hashes = {name: pair[1] for name, pair in source_tables.items()}
    iap_by_name: dict[str, int] = {}
    for row_id, row in source_rows["IAP.xml"].items():
        name = row.get("Name")
        if not name:
            raise ValueError(f"IAP.xml row {row_id} has no Name")
        if name in iap_by_name:
            raise ValueError(f"duplicate IAP Name: {name}")
        iap_by_name[name] = int(row_id)

    vanity_rows = source_rows["Vanity.xml"]
    source_shop_refs = shop_tab3_refs(source_rows["Shop.xml"])
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    records = matrix.get("records")
    discrepancies: list[dict[str, Any]] = []
    if not isinstance(records, list) or len(records) != 109:
        raise ValueError("canonical matrix must contain exactly 109 records")
    ids = [r.get("legacy_id") for r in records]
    if len(set(ids)) != len(ids):
        raise ValueError("canonical matrix has duplicate legacy_id values")

    sku_rows: list[dict[str, Any]] = []
    for record in records:
        sku_id = record.get("legacy_id")
        actual_row_id = iap_by_name.get(sku_id)
        xml = record.get("xml_entry", {})
        if (actual_row_id is not None) != (xml.get("present") is True):
            discrepancies.append({"sku": sku_id, "field": "xml_entry.present", "matrix": xml.get("present"), "actual": actual_row_id is not None})
        if actual_row_id != xml.get("row_id"):
            discrepancies.append({"sku": sku_id, "field": "xml_entry.row_id", "matrix": xml.get("row_id"), "actual": actual_row_id})
        vanity_suffix = None
        vanity_row = None
        if isinstance(sku_id, str) and sku_id.startswith("vanity") and sku_id[6:].isdigit():
            vanity_suffix = int(sku_id[6:])
            vanity_row = vanity_rows.get(str(vanity_suffix))
            if vanity_row is None:
                discrepancies.append({"sku": sku_id, "field": "Vanity.xml row", "matrix": vanity_suffix, "actual": None})
        sku_rows.append({
            "sku": sku_id,
            "iap_xml_row_id": actual_row_id,
            "in_dex_static_registry": bool(record.get("dex_entry", {}).get("present_as_static_literal")),
            "vanity_row_id": vanity_suffix,
            "vanity_name": vanity_row.get("Name") if vanity_row else None,
            "vanity_gold": vanity_row.get("Gold") if vanity_row else None,
            "vanity_cash_price": vanity_row.get("Price") if vanity_row else None,
            "listed_in_shop_tab3_source": vanity_suffix in source_shop_refs if vanity_suffix is not None else None,
            "record_status": record.get("status", "UNKNOWN"),
            "runtime_status": record.get("test_status", {}).get("runtime", "NOT-RUNTIME-VERIFIED"),
        })

    source_names = set(iap_by_name)
    matrix_names = set(ids)
    dex_names = {r.get("legacy_id") for r in records if r.get("dex_entry", {}).get("present_as_static_literal")}
    xml_only = source_names - dex_names
    dex_only = dex_names - source_names
    if source_names - matrix_names:
        discrepancies.append({"field": "sku_union", "source_only": sorted(source_names - matrix_names)})
    unexpected_matrix_only = sorted(name for name in matrix_names - source_names if name not in dex_only)
    if unexpected_matrix_only:
        discrepancies.append({"field": "sku_union", "unexpected_matrix_only": unexpected_matrix_only})
    if source_names - matrix_names or (matrix_names - source_names) != dex_only:
        discrepancies.append({"field": "sku_union_identity", "xml_only": sorted(xml_only), "dex_only": sorted(dex_only), "matrix_only": sorted(matrix_names - source_names)})
    if (len(source_names), len(dex_names), len(source_names & dex_names), len(xml_only), len(dex_only), len(source_names | dex_names)) != (107, 104, 102, 5, 2, 109):
        discrepancies.append({"field": "registry_invariants", "iap_xml": len(source_names), "dex_static": len(dex_names), "shared": len(source_names & dex_names), "xml_only": sorted(xml_only), "dex_only": sorted(dex_only), "union": len(source_names | dex_names)})

    patch_summary: dict[str, Any] | None = None
    table_comparison: dict[str, Any] = {}
    if patched_root:
        patched_tables = {name: read_table(patched_root, name) for name in TABLES}
        patched_rows = {name: pair[0] for name, pair in patched_tables.items()}
        patched_hashes = {name: pair[1] for name, pair in patched_tables.items()}
        changed = sorted(name for name in TABLES if source_hashes[name] != patched_hashes[name])
        unexpected = sorted(set(changed) - ALLOWED_PATCHED_TABLES)
        if unexpected:
            discrepancies.append({"field": "changed_table_allowlist", "unexpected_changes": unexpected})
        if "IAP.xml" in changed:
            discrepancies.append({"field": "IAP.xml_immutability", "sha256_before": source_hashes["IAP.xml"], "sha256_after": patched_hashes["IAP.xml"]})
        after_shop_refs = shop_tab3_refs(patched_rows["Shop.xml"])
        iap_vanity_ids = sorted(int(name[6:]) for name in source_names if name.startswith("vanity") and name[6:].isdigit())
        missing_routes = []
        for row_id in iap_vanity_ids:
            row = patched_rows["Vanity.xml"].get(str(row_id))
            if row is None or not row.get("Gold") or row_id not in after_shop_refs:
                missing_routes.append(row_id)
        before_vanity = source_rows["Vanity.xml"]
        after_vanity = patched_rows["Vanity.xml"]
        changed_vanity_rows = [
            {"row_id": int(row_id), "before": before_vanity.get(row_id), "after": after_vanity.get(row_id)}
            for row_id in sorted(set(before_vanity) | set(after_vanity), key=int)
            if before_vanity.get(row_id) != after_vanity.get(row_id)
        ]
        changed_shop_rows = [
            {"row_id": int(row_id), "before": source_rows["Shop.xml"].get(row_id), "after": patched_rows["Shop.xml"].get(row_id)}
            for row_id in sorted(set(source_rows["Shop.xml"]) | set(patched_rows["Shop.xml"]), key=int)
            if source_rows["Shop.xml"].get(row_id) != patched_rows["Shop.xml"].get(row_id)
        ]
        if missing_routes:
            discrepancies.append({"field": "iap_vanity_earnability_routes", "missing_vanity_ids": missing_routes})
        table_comparison = {
            name: {"source_sha256": source_hashes[name], "patched_sha256": patched_hashes[name], "changed": source_hashes[name] != patched_hashes[name]}
            for name in TABLES
        }
        patch_summary = {
            "changed_tables": changed,
            "allowed_changed_tables": sorted(ALLOWED_PATCHED_TABLES),
            "unexpected_changed_tables": unexpected,
            "iap_xml_unchanged": source_hashes["IAP.xml"] == patched_hashes["IAP.xml"],
            "items_xml_unchanged": source_hashes["Items.xml"] == patched_hashes["Items.xml"],
            "dictionary_xml_unchanged": source_hashes["Dictionary.xml"] == patched_hashes["Dictionary.xml"],
            "source_vanity_rows": len(vanity_rows),
            "source_shop_rows": len(source_rows["Shop.xml"]),
            "patched_shop_rows": len(patched_rows["Shop.xml"]),
            "iap_linked_vanity_skus": len(iap_vanity_ids),
            "patched_iap_vanity_missing_gold_or_shop_route": missing_routes,
            "vanity_row_changes": changed_vanity_rows,
            "shop_row_changes": changed_shop_rows,
            "patch_confidence": "UNIT-VERIFIED:data-table structural invariants only",
            "runtime_ui_purchase_equip_save": "NOT-RUNTIME-VERIFIED",
        }

    if patch_report_path:
        patch_data = json.loads(patch_report_path.read_text(encoding="utf-8"))
        if patch_data.get("iap_linked_vanity_rows") != 46:
            discrepancies.append({"field": "patch_report.iap_linked_vanity_rows", "actual": patch_data.get("iap_linked_vanity_rows"), "expected": 46})
        if patch_data.get("remaining_iap_vanity_without_gold") != []:
            discrepancies.append({"field": "patch_report.remaining_iap_vanity_without_gold", "actual": patch_data.get("remaining_iap_vanity_without_gold")})

    return {
        "schema_version": 1,
        "title": "Dungeon Quest v3.3.2.0 — IAP XML/SKU/Shop Reconciliation v15",
        "status": "PASS" if not discrepancies else "FAIL",
        "evidence_type": "STATIC-DIRECT table parsing; UNIT-VERIFIED when patch invariants pass",
        "inputs": {
            "source_asset_root": str(source_root),
            "patched_asset_root": str(patched_root) if patched_root else None,
            "canonical_matrix": str(matrix_path),
            "source_table_sha256": source_hashes,
        },
        "counts": {
            "iap_xml_rows": len(iap_by_name),
            "canonical_sku_records": len(records),
            "exact_xml_matrix_coverage": len(source_names & matrix_names),
            "dex_static_sku_identifiers": len(dex_names),
            "shared_identifiers": len(source_names & dex_names),
            "xml_only_identifiers": sorted(xml_only),
            "dex_only_identifiers": sorted(dex_only),
            "union_identifiers": len(source_names | dex_names),
            "vanity_rows": len(vanity_rows),
            "iap_linked_vanity_skus": sum(1 for name in source_names if name.startswith("vanity") and name[6:].isdigit()),
            "source_shop_rows": len(source_rows["Shop.xml"]),
            "source_shop_tab3_refs": len(source_shop_refs),
        },
        "tables": table_comparison,
        "patch_summary": patch_summary,
        "sku_rows": sku_rows,
        "discrepancies": discrepancies,
        "interpretation_limit": "Static XML identity and data-table tests do not prove native purchase callbacks, state mutation, save/load, UI reachability or runtime equivalence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="decoded original asset root")
    parser.add_argument("--patched-root", type=Path, help="decoded patched asset root; optional")
    parser.add_argument("--matrix", type=Path, required=True, help="canonical IAP mapping JSON")
    parser.add_argument("--patch-report", type=Path, help="existing patch summary JSON; optional")
    parser.add_argument("--output-json", type=Path, help="write full report to this path")
    args = parser.parse_args()
    try:
        report = audit(args.source_root, args.patched_root, args.matrix, args.patch_report)
    except (OSError, ValueError, ET.ParseError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    print(rendered, end="")
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered, encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

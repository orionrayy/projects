#!/usr/bin/env python3
"""Fail-closed consistency audit for the v13 per-SKU runtime evidence matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_XML_ONLY = {"angelicslime", "demonicslime", "poisonslime", "vanity72", "vanity73"}
EXPECTED_DEX_ONLY = {"package20", "package21"}
EXPECTED_ROUTES = {
    "600": "IAPWrapper.l(String)",
    "601": "IAPWrapper.n()",
    "602": "IAPWrapper.m(String, boolean)",
}


def audit_matrix(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data.get("records")
    errors: list[str] = []
    if not isinstance(records, list):
        return {"status": "FAIL", "errors": ["records must be a list"]}

    ids = [r.get("legacy_id") for r in records]
    if len(ids) != len(set(ids)):
        errors.append("legacy_id values must be unique")
    if len(records) != 109:
        errors.append(f"expected 109 SKU union records; found {len(records)}")

    dex_ids = {r.get("legacy_id") for r in records if r.get("sources", {}).get("dex_static_sku") is True}
    xml_ids = {r.get("legacy_id") for r in records if r.get("sources", {}).get("iap_xml_name") is True}
    shared = dex_ids & xml_ids
    xml_only = xml_ids - dex_ids
    dex_only = dex_ids - xml_ids
    vanity = {r.get("legacy_id") for r in records if isinstance(r.get("legacy_id"), str)
              and r["legacy_id"].startswith("vanity") and r["legacy_id"][6:].isdigit()}

    expected_counts = {
        "iap_xml_unique_identifiers": len(xml_ids),
        "dex_static_sku_identifiers": len(dex_ids),
        "shared_identifiers": len(shared),
        "union_identifiers": len(dex_ids | xml_ids),
        "vanity_sku_asset_correlations": len(vanity),
    }
    if expected_counts != {k: data.get("evidence_counts", {}).get(k) for k in expected_counts}:
        errors.append(f"evidence_counts inconsistent with records: derived={expected_counts}")
    if len(xml_ids) != 107 or len(dex_ids) != 104 or len(shared) != 102:
        errors.append(f"unexpected registry totals: XML={len(xml_ids)}, DEX={len(dex_ids)}, shared={len(shared)}")
    if xml_only != EXPECTED_XML_ONLY:
        errors.append(f"XML-only identifiers mismatch: {sorted(xml_only)}")
    if dex_only != EXPECTED_DEX_ONLY:
        errors.append(f"DEX-only identifiers mismatch: {sorted(dex_only)}")
    if len(vanity) != 46:
        errors.append(f"expected 46 vanity asset correlations; found {len(vanity)}")
    reported_counts = data.get("evidence_counts", {})
    if set(reported_counts.get("xml_only_identifiers", [])) != xml_only:
        errors.append("reported XML-only list does not match the record-level source flags")
    if set(reported_counts.get("dex_only_identifiers", [])) != dex_only:
        errors.append("reported DEX-only list does not match the record-level source flags")

    verified = 0
    for record in records:
        sku = record.get("legacy_id", "<missing>")
        evidence = record.get("runtime_evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{sku}: runtime_evidence must be an object")
            continue
        status = evidence.get("reward_status")
        if status not in {"UNVERIFIED", "VERIFIED", "BLOCKED"}:
            errors.append(f"{sku}: invalid reward_status {status!r}")
        if status == "VERIFIED":
            verified += 1
            required = evidence.get("verification_evidence")
            if not isinstance(required, list) or not required:
                errors.append(f"{sku}: VERIFIED requires non-empty verification_evidence")
            if evidence.get("persisted_entitlement_write") != "OBSERVED":
                errors.append(f"{sku}: VERIFIED requires observed persisted entitlement write")
            if evidence.get("runtime_test_status") != "PASS":
                errors.append(f"{sku}: VERIFIED requires runtime_test_status PASS")
            if evidence.get("reward_payload") is None:
                errors.append(f"{sku}: VERIFIED requires a concrete reward_payload")
        elif status == "UNVERIFIED":
            if evidence.get("runtime_test_status") == "PASS":
                errors.append(f"{sku}: PASS runtime test cannot coexist with UNVERIFIED status")
    unverified = sum(
        r.get("runtime_evidence", {}).get("reward_status") == "UNVERIFIED"
        for r in records if isinstance(r.get("runtime_evidence"), dict)
    )
    if data.get("evidence_counts", {}).get("runtime_reward_verified") != verified:
        errors.append("runtime_reward_verified summary does not match per-record statuses")
    if data.get("evidence_counts", {}).get("runtime_reward_unverified") != unverified:
        errors.append("runtime_reward_unverified summary does not match per-record statuses")

    flow = data.get("observed_purchase_flow", {})
    if flow.get("handler_routes") != EXPECTED_ROUTES:
        errors.append("handler_routes differ from statically verified route map")
    callback = flow.get("purchase_result_boundary", {})
    if callback.get("implementation") != "native declaration; no body in supplied DEX":
        errors.append("native callback boundary must remain explicit")
    if callback.get("per_sku_grant_mapping") != "not verified":
        errors.append("per-SKU grant mapping must not be overstated")

    return {
        "status": "PASS" if not errors else "FAIL",
        "matrix": str(path),
        "records": len(records),
        "registry_counts": expected_counts,
        "runtime_reward_verified": verified,
        "runtime_reward_unverified": unverified,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_matrix = Path(__file__).resolve().parents[1] / "docs" / "IAP_SKU_RUNTIME_EVIDENCE_V13.json"
    parser.add_argument("--matrix", type=Path, default=default_matrix)
    args = parser.parse_args()
    result = audit_matrix(args.matrix)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

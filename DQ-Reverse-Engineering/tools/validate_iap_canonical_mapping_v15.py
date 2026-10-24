#!/usr/bin/env python3
"""Fail-closed validation for the v15 canonical native IAP mapping."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_XML_ONLY = {"angelicslime", "demonicslime", "poisonslime", "vanity72", "vanity73"}
EXPECTED_DEX_ONLY = {"package20", "package21"}
EXPECTED_GOLD = {
    "gold1": (20_000_000, "0x737070", "0x7370d0"),
    "gold2": (50_000_000, "0x7371b8", "0x737218"),
    "gold3": (150_000_000, "0x737300", "0x737360"),
    "gold4": (350_000_000, "0x737448", "0x7374ac"),
    "gold5": (1_000_000_000, "0x737594", "0x7375f4"),
}
EXPECTED_BOOST_KEYS = {
    "gold": ("iap.boostGold", "nGoldBoost"),
    "crystal": ("iap.boostCS", "nCSBoost"),
    "mythstone": ("iap.boostMS", "nMSBoost"),
    "exp": ("iap.boostExp", "nExpBoost"),
    "luck": ("iap.boostMf", "nLuckBoost"),
    "pickup": ("iap.boostPU", "nPUBoost"),
    "petboost": ("iap.boostPet", "nPetBoost"),
    "hunter": ("iap.boostHunter", "nHunterBoost"),
}
EXPECTED_BUNDLES = {
    "package20": [64, 65, 66, 67],
    "package21": [68, 69, 70, 71],
    "special2": [56, 57, 58],
}


def audit_mapping(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data.get("records")
    errors: list[str] = []
    if not isinstance(records, list):
        return {"status": "FAIL", "errors": ["records must be a list"]}

    ids = [r.get("legacy_id") for r in records]
    if len(records) != 109:
        errors.append(f"expected 109 records; found {len(records)}")
    if len(set(ids)) != len(ids):
        errors.append("legacy_id values are not unique")
    by_id = {r.get("legacy_id"): r for r in records}
    xml_ids = {r["legacy_id"] for r in records if r.get("xml_entry", {}).get("present") is True}
    dex_ids = {r["legacy_id"] for r in records if r.get("dex_entry", {}).get("present_as_static_literal") is True}
    shared, xml_only, dex_only = xml_ids & dex_ids, xml_ids - dex_ids, dex_ids - xml_ids
    if (len(xml_ids), len(dex_ids), len(shared), len(xml_ids | dex_ids)) != (107, 104, 102, 109):
        errors.append(f"unexpected registry counts XML/DEX/shared/union={(len(xml_ids), len(dex_ids), len(shared), len(xml_ids | dex_ids))}")
    if xml_only != EXPECTED_XML_ONLY:
        errors.append(f"XML-only mismatch: {sorted(xml_only)}")
    if dex_only != EXPECTED_DEX_ONLY:
        errors.append(f"DEX-only mismatch: {sorted(dex_only)}")

    row_ids = [r["xml_entry"].get("row_id") for r in records if r.get("xml_entry", {}).get("present")]
    if len(row_ids) != 107 or set(row_ids) != set(range(1, 108)):
        errors.append("IAP.xml row IDs must cover 1..107 exactly once")
    if len(set(row_ids)) != len(row_ids):
        errors.append("IAP.xml row IDs are duplicated")

    for sku, (amount, branch, callsite) in EXPECTED_GOLD.items():
        r = by_id.get(sku)
        payload = r.get("reward_payload", {}) if r else {}
        if not r or payload.get("type") != "gold_currency" or payload.get("amount") != amount:
            errors.append(f"{sku}: expected exact native gold payload {amount}")
            continue
        if r.get("native_entry", {}).get("product_branch_pc") != branch:
            errors.append(f"{sku}: product branch PC mismatch")
        evidence_text = " ".join(str(e.get("location", "")) for e in r.get("evidence", []))
        if callsite not in evidence_text:
            errors.append(f"{sku}: RewardGold callsite {callsite} not cited in evidence")
        if r.get("runtime_status") == "RUNTIME-VERIFIED" or r.get("test_status", {}).get("runtime") != "NOT-RUNTIME-VERIFIED":
            errors.append(f"{sku}: static constant must not be described as runtime-verified")

    for sku, (flag, runtime_value) in EXPECTED_BOOST_KEYS.items():
        r = by_id.get(sku)
        payload = r.get("reward_payload", {}) if r else {}
        if not r or r.get("family") != "gameplay_boost":
            errors.append(f"{sku}: must be classified as gameplay_boost")
        if payload.get("flag") != flag or payload.get("runtime_value") != runtime_value:
            errors.append(f"{sku}: boost key mapping is incorrect")
    if by_id.get("gold", {}).get("family") == "gold_currency_pack":
        errors.append("gold is incorrectly classified as a Gold currency pack; native evidence maps it to boostGold")
    if by_id.get("crystal", {}).get("family") == "crafting_resource_product_candidate":
        errors.append("crystal is incorrectly classified as a direct currency product; native evidence maps it to boostCS")
    if by_id.get("mythstone", {}).get("family") == "crafting_resource_product_candidate":
        errors.append("mythstone is incorrectly classified as a direct currency product; native evidence maps it to boostMS")

    for sku, vanity_ids in EXPECTED_BUNDLES.items():
        r = by_id.get(sku)
        payload = r.get("reward_payload", {})
        observed = [x.get("vanity_id") for x in payload.get("items", [])]
        if not r or payload.get("type") != "vanity_unlocks" or observed != vanity_ids:
            errors.append(f"{sku}: expected vanity key sequence {vanity_ids}; got {observed}")

    vanity_records = [r for r in records if r.get("family") == "vanity_cosmetic"]
    if len(vanity_records) != 46:
        errors.append(f"expected 46 IAP vanity records; found {len(vanity_records)}")
    for r in vanity_records:
        vid = int(r["legacy_id"][6:]) if r["legacy_id"].startswith("vanity") and r["legacy_id"][6:].isdigit() else None
        payload = r.get("reward_payload", {})
        if payload.get("type") != "vanity_unlock" or payload.get("vanity_id") != vid:
            errors.append(f"{r.get('legacy_id')}: vanity suffix mapping missing or incorrect")
        if r.get("replacement_route", {}).get("status") != "UNIT-VERIFIED":
            errors.append(f"{r.get('legacy_id')}: data-only Gold route must be marked UNIT-VERIFIED")
        if r.get("test_status", {}).get("runtime") != "NOT-RUNTIME-VERIFIED":
            errors.append(f"{r.get('legacy_id')}: runtime must remain explicitly unverified")

    runtime_verified = [r.get("legacy_id") for r in records if r.get("test_status", {}).get("runtime") == "RUNTIME-VERIFIED"]
    if runtime_verified:
        errors.append(f"runtime-verified SKUs lack runtime test evidence policy approval: {runtime_verified}")
    counts = data.get("counts", {})
    expected_summary = {
        "xml_ids": len(xml_ids), "dex_literals": len(dex_ids), "shared": len(shared),
        "xml_only": sorted(xml_only), "dex_only": sorted(dex_only), "union": len(xml_ids | dex_ids),
        "rows": len(records), "runtime_grants_verified": 0, "runtime_grants_unverified": 109,
        "vanity_data_routes_unit_verified": 46,
    }
    for key, value in expected_summary.items():
        actual = counts.get(key)
        if isinstance(value, list):
            if sorted(actual or []) != value:
                errors.append(f"summary {key} mismatches records")
        elif actual != value:
            errors.append(f"summary {key}: expected {value}, got {actual}")

    flow = data.get("flow", {})
    if "IAPWrapper_onPurchaseSuccess" not in flow.get("native_success", "") and "onPurchaseSuccess" not in flow.get("native_success", ""):
        errors.append("native success chain is missing")
    if "sAIHandler" not in flow.get("model_event", {}).get("dynamic_forward_variable", ""):
        errors.append("dynamic sAIHandler boundary must be documented")
    if "runtime value" not in flow.get("model_event", {}).get("dynamic_target_runtime_value", "").lower() and "unknown" not in flow.get("model_event", {}).get("dynamic_target_runtime_value", "").lower():
        errors.append("dynamic model target must not be overstated")

    return {
        "status": "PASS" if not errors else "FAIL",
        "records": len(records),
        "xml_ids": len(xml_ids),
        "dex_literals": len(dex_ids),
        "shared": len(shared),
        "vanity_records_unit_verified_for_data_patch": len(vanity_records),
        "gold_payloads_static_direct": len(EXPECTED_GOLD),
        "boost_keys_static_direct": len(EXPECTED_BOOST_KEYS),
        "runtime_grants_verified": len(runtime_verified),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_matrix = Path(__file__).resolve().parents[1] / "docs" / "IAP_CANONICAL_MAPPING_V15.json"
    parser.add_argument("--matrix", type=Path, default=default_matrix)
    args = parser.parse_args()
    result = audit_mapping(args.matrix)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

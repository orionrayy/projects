#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "research" / "evidence-ledger.json"
SCHEMA_PATH = ROOT / "schemas" / "evidence-ledger.schema.json"

def main():
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(ledger),
        key=lambda e: list(map(str, e.absolute_path)),
    )
    if errors:
        for error in errors:
            location = "/" + "/".join(map(str, error.absolute_path))
            print(f"{location}: {error.message}")
        raise SystemExit(1)

    ids = [item["id"] for item in ledger["records"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("EVIDENCE_LEDGER_DUPLICATE_ID")
    for item in ledger["records"]:
        if item["status"] == "not_performed" and item["evidence"]:
            raise SystemExit("NOT_PERFORMED_RECORD_MUST_NOT_CLAIM_EVIDENCE: " + item["id"])
        if item["status"] in ("passed_ci", "failed_ci") and not item["evidence"]:
            raise SystemExit("CI_STATUS_REQUIRES_EVIDENCE: " + item["id"])
        for ref in item["evidence"]:
            if "revision" not in ref and not ref.get("url"):
                # Source-relative paths are valid for the current worktree evidence.
                if not ref.get("path", "").strip():
                    raise SystemExit("EVIDENCE_REFERENCE_MISSING_LOCATION: " + item["id"])

    not_performed = [r["id"] for r in ledger["records"] if r["status"] == "not_performed"]
    print("EVIDENCE_LEDGER_SCHEMA_PASS records=" + str(len(ids)))
    print("TRAINING_OR_INGESTION_NOT_CLAIMED records=" + ",".join(not_performed))

if __name__ == "__main__":
    main()

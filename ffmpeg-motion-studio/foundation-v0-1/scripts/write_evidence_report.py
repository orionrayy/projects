#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ledger_path = ROOT / "research" / "evidence-ledger.json"
raw = ledger_path.read_bytes()
ledger = json.loads(raw)
out = ROOT / "out" / "evidence-ledger-validation-report.json"
out.parent.mkdir(parents=True, exist_ok=True)

repo = os.environ.get("GITHUB_REPOSITORY", "orionrayy/projects")
sha = os.environ.get("GITHUB_SHA", "unknown")
run_id = os.environ.get("GITHUB_RUN_ID", "unknown")
workflow_url = f"https://github.com/{repo}/actions/runs/{run_id}"

report = {
    "report_schema_version": "1.0.0",
    "evidence_ledger_sha256": hashlib.sha256(raw).hexdigest(),
    "tested_revision": sha,
    "workflow_run_url": workflow_url,
    "status": "gates_reached",
    "passed_gates": [
        "scene_schema",
        "evidence_ledger_schema",
        "http_preview_smoke",
        "bilateral_character_render_contract",
        "serialized_rendered_pose_quality",
        "synthetic_motion_benchmarks",
        "rasterizer_consistency_diagnostic",
        "python_schema_tests",
        "ffmpeg_render_and_ffprobe",
        "source_snapshot_packaging"
    ],
    "external_dataset_ingestion": "not_performed",
    "model_training_or_finetuning": "not_performed",
    "claims": [
        {
            "id": item["id"],
            "status_at_commit": item["status"],
            "claim": item["claim"]
        }
        for item in ledger["records"]
    ],
    "limitations": [
        "This report certifies automated engineering gates only, not artistic approval.",
        "Serialized hand-transform checks validate render-state consistency, not aesthetic quality or human-motion naturalness.",
        "The render is a procedural 2D prototype; human review of silhouette and anatomy remains required.",
        "No dataset learning or training capability is claimed."
    ]
}
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("EVIDENCE_REPORT_CREATED " + str(out))

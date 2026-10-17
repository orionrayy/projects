#!/usr/bin/env python3
"""Deterministic open-world space-time benchmark. Synthetic software checks only."""
from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np

from motionlab.analysis import analyze_video
from motionlab.media import sha256_file
from motionlab.synthetic import generate_synthetic_clip


def _analyze(path: Path, fps: int, width: int, height: int) -> dict[str, Any]:
    return analyze_video(
        path, max_fps=float(fps), width=width, height=height,
        max_frames=10000, window_frames=16, window_stride=8,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reports/openworld-synthetic-benchmark")
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--duration", type=float, default=3.0)
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--height", type=int, default=72)
    args = parser.parse_args()
    if args.fps < 2 or args.fps > 60 or args.duration < 0.5:
        raise SystemExit("fps must be 2..60 and duration must be >=0.5s")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    scenarios = ("move_reverse", "freeze", "flash", "global_pan_reverse", "pan_plus_object", "abstract_nirmana", "fractal_zoom")
    results: dict[str, Any] = {}
    reports: dict[str, Any] = {}
    for scenario in scenarios:
        clip = generate_synthetic_clip(
            output_dir / f"{scenario}.mkv", scenario=scenario,
            duration_s=args.duration, fps=args.fps,
        )
        report = _analyze(clip, args.fps, args.width, args.height)
        reports[scenario] = report
        signature_vectors = [np.asarray(window["signature_vector"], dtype=np.float64) for window in report["timeline"]]
        results[scenario] = {
            "sha256": sha256_file(clip),
            "frames_decoded": report["sampling"]["frames_decoded"],
            "timeline_coverage_ratio": report["sampling"]["timeline_coverage_ratio"],
            "window_count": len(report["timeline"]),
            "feature_dimensions": report["measurements"]["feature_dimensions"],
            "signature_distance_p50": report["measurements"]["signature_distance_p50"],
            "signature_distance_p95": report["measurements"]["signature_distance_p95"],
            "exact_duplicate_transition_ratio": report["measurements"]["exact_duplicate_transition_ratio"],
            "cross_window_relation_count": report["measurements"]["cross_window_relations"],
            "event_types": sorted({event["event_type"] for event in report["events"]}),
            "regional_nodes_per_window": [len(window["regional_nodes"]) for window in report["timeline"]],
            "regional_edges_per_window": [len(window["regional_edges"]) for window in report["timeline"]],
            "scale_levels_per_window": [len(window["scale_signatures"]) for window in report["timeline"]],
            "all_features_finite": all(np.isfinite(vector).all() for vector in signature_vectors),
        }

    moving = reports["move_reverse"]
    frozen = reports["freeze"]
    flash = reports["flash"]
    mixed = reports["pan_plus_object"]
    nirmana = reports["abstract_nirmana"]
    fractal = reports["fractal_zoom"]
    deterministic_again = _analyze(
        output_dir / "move_reverse.mkv", args.fps, args.width, args.height
    )
    original_vectors = [window["signature_vector"] for window in moving["timeline"]]
    repeat_vectors = [window["signature_vector"] for window in deterministic_again["timeline"]]
    checks = {
        "space_time_signature_available": all(
            item["feature_dimensions"] >= 120 and item["window_count"] >= 1
            for item in results.values()
        ),
        "timeline_coverage_reported": all(
            item["timeline_coverage_ratio"] is None or item["timeline_coverage_ratio"] >= 0.95
            for item in results.values()
        ),
        "multiscale_analysis_present": all(
            len(set(item["scale_levels_per_window"])) == 1 and item["scale_levels_per_window"][0] == 3
            for item in results.values()
        ),
        "relational_spatial_field_present": all(
            all(count == 24 for count in item["regional_nodes_per_window"])
            and all(count >= 38 for count in item["regional_edges_per_window"])
            for item in results.values()
        ),
        "space_time_signatures_finite": all(item["all_features_finite"] for item in results.values()),
        "frozen_input_integrity_signal": frozen["measurements"]["exact_duplicate_transition_ratio"] > 0.30,
        "temporal_structure_not_constant_for_dynamic_cases": (
            moving["measurements"]["signature_distance_p95"] > 0.0
            and flash["measurements"]["signature_distance_p95"] > 0.0
            and mixed["measurements"]["signature_distance_p95"] > 0.0
            and nirmana["measurements"]["signature_distance_p95"] > 0.0
            and fractal["measurements"]["signature_distance_p95"] > 0.0
        ),
        "deterministic_repeatability": original_vectors == repeat_vectors,
        "frame_pair_analysis_not_primary": all(
            report["sampling"]["pairwise_frame_analysis_is_primary"] is False
            and report["provenance"]["legacy_pairwise_optical_flow_used_by_core"] is False
            for report in reports.values()
        ),
    }
    result = {
        "schema_version": "fma.openworld.synthetic-benchmark.v0.2",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "synthetic_only": True,
        "real_world_evidence": False,
        "state_of_the_art_claim_supported": False,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "fps": args.fps,
            "duration_s": args.duration,
            "width": args.width,
            "height": args.height,
        },
        "checks": checks,
        "scenarios": results,
        "limitations": [
            "Generated, lossless/simple synthetic videos only; no claim about arbitrary natural or abstract video generalization.",
            "This benchmark tests observability, multiscale signature stability and software contracts, not semantic action understanding.",
            "A passing test suite is not a real-world accuracy score and does not establish novelty or state of the art.",
        ],
    }
    report_path = output_dir / "synthetic-benchmark.json"
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "report_path": str(report_path), "checks": checks}, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

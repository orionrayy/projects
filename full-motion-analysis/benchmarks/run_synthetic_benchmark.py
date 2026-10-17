#!/usr/bin/env python3
"""Run a small deterministic motion / freeze / flash benchmark. Synthetic evidence only."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from typing import Any

from motionlab.analysis import analyze_video
from motionlab.media import sha256_file
from motionlab.synthetic import generate_synthetic_clip


def _median(values):
    if not values:
        return None
    import statistics
    return float(statistics.median(values))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reports/synthetic-benchmark")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--duration", type=float, default=3.0)
    args = parser.parse_args()

    out = Path(args.output_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    for scenario in ("move_reverse", "freeze", "flash", "global_pan_reverse", "pan_plus_object"):
        clip = generate_synthetic_clip(
            out / f"{scenario}.mkv", scenario=scenario,
            duration_s=args.duration, fps=args.fps,
        )
        result = analyze_video(clip, max_fps=float(args.fps), optical_flow=True)
        (out / f"{scenario}.analysis.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        results[scenario] = {
            "sha256": sha256_file(clip),
            "frames_decoded": result["sampling"]["frames_decoded"],
            "timeline_coverage_ratio": result["sampling"]["timeline_coverage_ratio"],
            "measurements": result["measurements"],
            "event_counts": result["event_counts"],
            "event_types": sorted({event["event_type"] for event in result["events"]}),
            "timeline_monotonic": all(
                a["timestamp_s"] < b["timestamp_s"]
                for a, b in zip(result["timeline"], result["timeline"][1:])
            ),
            "optical_flow_status": result["provenance"]["optical_flow"],
            "flow_grid_cells_observed": max(
                (len(point["flow_grid"]) for point in result["timeline"] if point.get("flow_grid")),
                default=0,
            ),
            "global_affine_fit_points": sum(
                point.get("global_affine_fit_status") == "fit" for point in result["timeline"]
            ),
            "global_affine_dx_by_half": {
                "first_half_median": _median([
                    point["global_affine_translation_dx_px_frame"] for point in result["timeline"]
                    if point.get("global_affine_fit_status") == "fit"
                    and point.get("global_affine_translation_dx_px_frame") is not None
                    and point["timestamp_s"] < args.duration * 0.4
                ]),
                "second_half_median": _median([
                    point["global_affine_translation_dx_px_frame"] for point in result["timeline"]
                    if point.get("global_affine_fit_status") == "fit"
                    and point.get("global_affine_translation_dx_px_frame") is not None
                    and point["timestamp_s"] > args.duration * 0.6
                ]),
            },
        }

    move = results["move_reverse"]
    freeze = results["freeze"]
    flash = results["flash"]
    pan = results["global_pan_reverse"]
    mixed = results["pan_plus_object"]
    flow_available = pan["optical_flow_status"].startswith("available:")
    mixed_flow_available = mixed["optical_flow_status"].startswith("available:")
    first_half_dx = pan["global_affine_dx_by_half"]["first_half_median"]
    second_half_dx = pan["global_affine_dx_by_half"]["second_half_median"]
    checks = {
        "motion_changes_measured": move["measurements"]["mean_abs_diff_p95"] > 0.0005,
        "timeline_order_valid": all(item["timeline_monotonic"] for item in results.values()),
        "freeze_has_repeated_frames": freeze["measurements"]["exact_duplicate_transition_ratio"] > 0.30,
        "flash_interval_flagged": (
            "possible_flash_candidate" in flash["event_types"]
            or "scene_transition_candidate" in flash["event_types"]
        ),
        "spatial_flow_grid_available": not flow_available or (
            pan["flow_grid_cells_observed"] == 24
        ),
        "affine_transform_fit_available": not flow_available or pan["global_affine_fit_points"] > 0,
        "known_global_pan_direction_reversal_detected": not flow_available or (
            first_half_dx is not None and second_half_dx is not None
            and first_half_dx > 0.2 and second_half_dx < -0.2
        ),
        "independent_object_motion_region_detected_during_camera_pan": not mixed_flow_available or (
            "local_motion_region_candidate" in mixed["event_types"]
            and mixed["flow_grid_cells_observed"] == 24
        ),
    }
    output = {
        "schema_version": "fma.synthetic-benchmark.v0.1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "synthetic_only": True,
        "real_world_evidence": False,
        "state_of_the_art_claim_supported": False,
        "environment": {"python": platform.python_version(), "fps": args.fps, "duration_s": args.duration},
        "checks": checks,
        "scenarios": results,
        "limitations": [
            "Synthetic lossless grayscale fixtures only; no claim about natural-video generalization.",
            "This suite validates observability and software behavior, not semantic action understanding.",
        ],
    }
    report_path = out / "synthetic-benchmark.json"
    report_path.write_text(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "report_path": str(report_path), "checks": checks}, indent=2))
    return 0 if output["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

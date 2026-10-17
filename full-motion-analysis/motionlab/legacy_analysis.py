"""Temporal measurements and evidence-linked event candidates."""
from __future__ import annotations

import hashlib
import importlib.metadata
import math
import platform
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np

from . import __version__
from .media import iter_gray_frames, probe_media, sha256_file, tool_version
from .metrics import measure_frame_pair, robust_high_threshold


def _optional_cv2(enabled: bool) -> tuple[Any | None, str]:
    if not enabled:
        return None, "disabled_by_request"
    try:
        import cv2  # type: ignore
        return cv2, f"available:{cv2.__version__}"
    except ImportError:
        return None, "unavailable:install_opencv_python_headless_for_dense_optical_flow"


def _round_value(value: Any, digits: int = 6) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.floating, float)):
        f = float(value)
        return round(f, digits) if math.isfinite(f) else None
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, bool):
        return value
    return value


def _event(
    event_type: str,
    frame_index: int,
    timestamp_s: float,
    severity: str,
    rule_id: str,
    measurement: dict[str, Any],
    limitation: str,
    end_s: float | None = None,
) -> dict:
    return {
        "event_type": event_type,
        "timestamp_s": round(float(timestamp_s), 6),
        "end_timestamp_s": round(float(end_s), 6) if end_s is not None else None,
        "frame_index": int(frame_index),
        "severity": severity,
        "rule_id": rule_id,
        "measurement": {k: _round_value(v) for k, v in measurement.items()},
        "interpretation_limit": limitation,
    }


def _local_motion_regions(grid: Any) -> list[dict[str, Any]]:
    """Find adjacent high-residual grid regions without assigning object identity."""
    if not isinstance(grid, list):
        return []
    active: dict[tuple[int, int], dict[str, Any]] = {}
    for cell in grid:
        if not isinstance(cell, dict):
            continue
        occupancy = cell.get("affine_residual_moving_pixel_ratio")
        p90 = cell.get("affine_residual_p90_magnitude_px_frame")
        if not isinstance(occupancy, (int, float)) or not isinstance(p90, (int, float)):
            continue
        if math.isfinite(float(occupancy)) and math.isfinite(float(p90)) and occupancy >= 0.08 and p90 >= 0.75:
            active[(int(cell["row"]), int(cell["column"]))] = cell
    regions: list[dict[str, Any]] = []
    unseen = set(active)
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        component = [seed]
        frontier = [seed]
        while frontier:
            y, x = frontier.pop()
            for neighbor in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    frontier.append(neighbor)
                    component.append(neighbor)
        cells = [active[p] for p in component]
        x0 = min(float(cell["x0_norm"]) for cell in cells)
        y0 = min(float(cell["y0_norm"]) for cell in cells)
        x1 = max(float(cell["x1_norm"]) for cell in cells)
        y1 = max(float(cell["y1_norm"]) for cell in cells)
        regions.append({
            "grid_cells": [{"row": y, "column": x} for y, x in sorted(component)],
            "cell_count": len(cells),
            "bbox_norm_xyxy": [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)],
            "centroid_norm_xy": [round((x0 + x1) / 2.0, 4), round((y0 + y1) / 2.0, 4)],
            "mean_residual_magnitude_px_frame": float(np.mean([
                float(cell["affine_residual_mean_magnitude_px_frame"]) for cell in cells
            ])),
            "p90_residual_magnitude_px_frame": float(np.max([
                float(cell["affine_residual_p90_magnitude_px_frame"]) for cell in cells
            ])),
            "mean_residual_moving_pixel_ratio": float(np.mean([
                float(cell["affine_residual_moving_pixel_ratio"]) for cell in cells
            ])),
        })
    return regions


def detect_event_candidates(rows: list[dict], fps: float) -> list[dict]:
    """Transparent heuristics. Event names are candidates, not semantic or causal claims."""
    if not rows:
        return []
    diffs = [float(r["mean_abs_diff"]) for r in rows[1:]]
    diff_threshold = robust_high_threshold(diffs, floor=0.035, mad_multiplier=4.0)
    flow_values = [
        float(r["flow_mean_magnitude_px_frame"])
        for r in rows[1:] if r.get("flow_mean_magnitude_px_frame") is not None
    ]
    flow_threshold = robust_high_threshold(flow_values, floor=0.35, mad_multiplier=4.0)
    events: list[dict] = []

    # Per-observation scene transition candidates.
    for r in rows[1:]:
        strong_change = float(r["mean_abs_diff"]) >= 0.15
        hist_change = float(r["histogram_delta"]) >= 0.50
        distributed_change = float(r["changed_pixel_ratio"]) >= 0.55
        if (hist_change and strong_change) or (distributed_change and float(r["mean_abs_diff"]) >= 0.20):
            events.append(_event(
                "scene_transition_candidate", r["frame_index"], r["timestamp_s"], "high",
                "FMA-CUT-001",
                {
                    "mean_abs_diff": r["mean_abs_diff"],
                    "changed_pixel_ratio": r["changed_pixel_ratio"],
                    "histogram_delta": r["histogram_delta"],
                },
                "A large frame change may be an edit, flash, exposure shift, occlusion, or rapid camera move; this is not a semantic scene classifier.",
            ))

    # New motion after a low-motion observation.
    signal_key = "flow_mean_magnitude_px_frame" if flow_values else "mean_abs_diff"
    motion_threshold = flow_threshold if flow_values else max(0.012, diff_threshold * 0.75)
    active = [False] * len(rows)
    for i, r in enumerate(rows):
        signal = r.get(signal_key)
        active[i] = signal is not None and float(signal) >= motion_threshold
    for i in range(1, len(rows)):
        before_active = active[i - 1]
        if active[i] and not before_active:
            events.append(_event(
                "motion_onset_candidate", rows[i]["frame_index"], rows[i]["timestamp_s"], "medium",
                "FMA-ONSET-001",
                {signal_key: rows[i].get(signal_key), "threshold": motion_threshold},
                "Indicates measured image change / flow above a heuristic threshold; it does not identify the moving object or its intent.",
            ))

    # Outlier changes/bursts.
    for r in rows[1:]:
        if float(r["mean_abs_diff"]) >= diff_threshold:
            events.append(_event(
                "motion_burst_candidate", r["frame_index"], r["timestamp_s"], "medium",
                "FMA-BURST-001",
                {"mean_abs_diff": r["mean_abs_diff"], "threshold": diff_threshold,
                 "flow_mean_magnitude_px_frame": r.get("flow_mean_magnitude_px_frame")},
                "An unusually large adjacent-frame change can be movement, a cut, a lighting event, compression artefact, or a camera shake.",
            ))

    # Direction reversal candidate from average dense-flow vectors.
    for i in range(2, len(rows)):
        a, b = rows[i - 1], rows[i]
        if a.get("flow_mean_dx_px_frame") is None or b.get("flow_mean_dx_px_frame") is None:
            continue
        av = (float(a["flow_mean_dx_px_frame"]), float(a["flow_mean_dy_px_frame"]))
        bv = (float(b["flow_mean_dx_px_frame"]), float(b["flow_mean_dy_px_frame"]))
        amag, bmag = math.hypot(*av), math.hypot(*bv)
        denom = max(amag * bmag, 1e-9)
        cos_angle = max(-1.0, min(1.0, (av[0] * bv[0] + av[1] * bv[1]) / denom))
        angle = math.degrees(math.acos(cos_angle))
        if amag >= 0.35 and bmag >= 0.35 and angle >= 140:
            events.append(_event(
                "direction_reversal_candidate", b["frame_index"], b["timestamp_s"], "medium",
                "FMA-REVERSAL-001",
                {"angle_change_deg": angle, "previous_vector_px_frame": av,
                 "current_vector_px_frame": bv, "previous_magnitude": amag, "current_magnitude": bmag},
                "A reversal in the scene-wide mean flow vector is not proof that a specific object reversed; multiple motions or camera motion can produce this signal.",
            ))

    # Local motion-region candidates are derived from flow unexplained by the fitted global affine transform.
    # Components are image-grid regions, not persistent objects or semantic actions.
    for r in rows[1:]:
        grid = r.get("flow_grid")
        for region_index, region in enumerate(_local_motion_regions(grid)):
            events.append(_event(
                "local_motion_region_candidate", r["frame_index"], r["timestamp_s"], "medium",
                "FMA-LOCAL-RESIDUAL-001",
                {"region_index": region_index, **region},
                "A spatially coherent residual-flow region is not an object identity. It can arise from independently moving content, non-rigid motion, parallax, occlusion, rolling shutter, or a failed global-motion fit.",
            ))

    # Exact repeated decoded-frame runs. A static scene can be legitimate; keep that caveat explicit.
    run_start: int | None = None
    for i in range(1, len(rows) + 1):
        duplicate = i < len(rows) and bool(rows[i].get("exact_duplicate_of_previous"))
        if duplicate and run_start is None:
            run_start = i - 1
        if not duplicate and run_start is not None:
            run_end = i - 1
            run_len = run_end - run_start + 1
            duration = run_len / fps
            if duration >= 0.5:
                start_row = rows[run_start]
                end_row = rows[run_end]
                events.append(_event(
                    "repeated_frame_run_candidate", start_row["frame_index"], start_row["timestamp_s"], "medium",
                    "FMA-FREEZE-001",
                    {"repeated_decoded_frames": run_len, "duration_s": duration,
                     "end_frame_index": end_row["frame_index"]},
                    "Repeated frames may indicate a frozen render, intentional hold, or a genuinely static camera/scene; review the evidence frames before treating it as a defect.",
                    end_s=end_row["timestamp_s"],
                ))
            run_start = None

    # A flash-like single-frame excursion is suggested by two large adjacent changes.
    for i in range(1, len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        if (
            float(a["mean_abs_diff"]) >= max(0.16, diff_threshold)
            and float(b["mean_abs_diff"]) >= max(0.16, diff_threshold)
            and float(b["histogram_delta"]) >= 0.35
        ):
            events.append(_event(
                "possible_flash_candidate", a["frame_index"], a["timestamp_s"], "medium",
                "FMA-FLASH-001",
                {"first_change": a["mean_abs_diff"], "return_change": b["mean_abs_diff"],
                 "first_histogram_delta": a["histogram_delta"], "return_histogram_delta": b["histogram_delta"]},
                "A brief global change is consistent with a flash but can also be a fast cut, exposure correction, or occlusion.",
                end_s=b["timestamp_s"],
            ))

    # Merge duplicate candidate rows of the same type within two sampled frames.
    events.sort(key=lambda e: (e["timestamp_s"], e["event_type"], e["rule_id"]))
    compact: list[dict] = []
    for event in events:
        if compact:
            last = compact[-1]
            if (
                last["event_type"] == event["event_type"]
                and last["rule_id"] == event["rule_id"]
                and event["timestamp_s"] - last["timestamp_s"] <= max(0.05, 2.0 / fps)
                and event["event_type"] in {"motion_burst_candidate", "scene_transition_candidate", "possible_flash_candidate"}
            ):
                continue
        compact.append(event)
    return compact


def analyze_video(
    path: str | Path,
    *,
    max_fps: float = 30.0,
    width: int = 320,
    height: int = 180,
    max_frames: int = 100_000,
    optical_flow: bool = True,
) -> dict:
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError("input_path_must_be_a_file")
    if not 1.0 <= float(max_fps) <= 120.0:
        raise ValueError("max_fps_must_be_between_1_and_120")
    if width < 64 or height < 64 or width % 2 or height % 2:
        raise ValueError("analysis_width_height_must_be_even_and_at_least_64")
    if not 1 <= int(max_frames) <= 1_000_000:
        raise ValueError("max_frames_must_be_between_1_and_1000000")

    metadata = probe_media(source)
    source_fps = metadata.get("source_fps") or 30.0
    analysis_fps = min(float(source_fps), float(max_fps))
    cv2_module, flow_status = _optional_cv2(optical_flow)
    rows: list[dict] = []
    previous: np.ndarray | None = None
    truncated = False

    for frame_index, frame in iter_gray_frames(
        source, fps=analysis_fps, width=width, height=height, max_frames=int(max_frames)
    ):
        luma = float(frame.mean()) / 255.0
        if previous is None:
            measured = {
                "mean_abs_diff": 0.0, "changed_pixel_ratio": 0.0, "histogram_delta": 0.0,
                "difference_centroid_x_norm": None, "difference_centroid_y_norm": None,
                "flow_mean_dx_px_frame": None, "flow_mean_dy_px_frame": None,
                "flow_mean_magnitude_px_frame": None, "flow_magnitude_p90_px_frame": None,
                "flow_moving_pixel_ratio": None, "flow_global_median_dx_px_frame": None,
                "flow_global_median_dy_px_frame": None, "flow_residual_mean_px_frame": None,
                "flow_coherence": None, "direction_deg_image_coordinates": None,
                "global_affine_translation_dx_px_frame": None, "global_affine_translation_dy_px_frame": None,
                "global_affine_rotation_deg_frame": None, "global_affine_scale_factor": None,
                "global_affine_residual_median_px_frame": None, "global_affine_residual_p90_px_frame": None,
                "global_affine_inlier_ratio": None, "global_affine_fit_status": "first_frame_no_pair",
                "affine_residual_magnitude_mean_px_frame": None,
                "affine_residual_magnitude_p90_px_frame": None,
                "affine_residual_moving_pixel_ratio": None,
                "flow_grid": None, "exact_duplicate_of_previous": False,
            }
        else:
            measured = measure_frame_pair(previous, frame, cv2_module=cv2_module)
            measured["exact_duplicate_of_previous"] = bool(np.array_equal(previous, frame))
        rows.append({
            "frame_index": frame_index,
            "timestamp_s": frame_index / analysis_fps,
            "mean_luma": luma,
            **measured,
        })
        previous = frame
        if frame_index + 1 >= int(max_frames):
            estimated_frames = (
                math.ceil(float(metadata["duration_s"]) * analysis_fps)
                if metadata.get("duration_s") else None
            )
            truncated = estimated_frames is not None and estimated_frames > int(max_frames)

    if not rows:
        raise RuntimeError("no_decodable_video_frames")
    events = detect_event_candidates(rows, analysis_fps)
    count = len(rows)
    duration = metadata.get("duration_s")
    covered_s = min(float(duration), count / analysis_fps) if duration else count / analysis_fps
    coverage_ratio = min(1.0, covered_s / float(duration)) if duration else None
    sample_rate_ratio = min(1.0, analysis_fps / float(source_fps)) if source_fps else None
    observed_diffs = [float(r["mean_abs_diff"]) for r in rows[1:]]
    flow_mags = [float(r["flow_mean_magnitude_px_frame"]) for r in rows[1:]
                 if r["flow_mean_magnitude_px_frame"] is not None]
    exact_duplicates = sum(bool(r["exact_duplicate_of_previous"]) for r in rows[1:])
    dark_frames = sum(float(r["mean_luma"]) <= 0.01 for r in rows)

    max_series_points = 4000
    stride = max(1, math.ceil(count / max_series_points))
    timeline = []
    event_frame_ids = {int(e["frame_index"]) for e in events}
    for row in rows:
        if row["frame_index"] % stride == 0 or row["frame_index"] in event_frame_ids:
            timeline.append({
                "frame_index": row["frame_index"],
                "timestamp_s": round(row["timestamp_s"], 6),
                "mean_abs_diff": round(float(row["mean_abs_diff"]), 6),
                "changed_pixel_ratio": round(float(row["changed_pixel_ratio"]), 6),
                "mean_luma": round(float(row["mean_luma"]), 6),
                "histogram_delta": round(float(row["histogram_delta"]), 6),
                "flow_mean_dx_px_frame": _round_value(row["flow_mean_dx_px_frame"]),
                "flow_mean_dy_px_frame": _round_value(row["flow_mean_dy_px_frame"]),
                "flow_mean_magnitude_px_frame": _round_value(row["flow_mean_magnitude_px_frame"]),
                "flow_magnitude_p90_px_frame": _round_value(row["flow_magnitude_p90_px_frame"]),
                "flow_moving_pixel_ratio": _round_value(row["flow_moving_pixel_ratio"]),
                "flow_grid": row.get("flow_grid"),
                "flow_global_median_dx_px_frame": _round_value(row["flow_global_median_dx_px_frame"]),
                "flow_global_median_dy_px_frame": _round_value(row["flow_global_median_dy_px_frame"]),
                "flow_residual_mean_px_frame": _round_value(row["flow_residual_mean_px_frame"]),
                "flow_coherence": _round_value(row["flow_coherence"]),
                "global_affine_translation_dx_px_frame": _round_value(row["global_affine_translation_dx_px_frame"]),
                "global_affine_translation_dy_px_frame": _round_value(row["global_affine_translation_dy_px_frame"]),
                "global_affine_rotation_deg_frame": _round_value(row["global_affine_rotation_deg_frame"]),
                "global_affine_scale_factor": _round_value(row["global_affine_scale_factor"]),
                "global_affine_residual_median_px_frame": _round_value(row["global_affine_residual_median_px_frame"]),
                "global_affine_residual_p90_px_frame": _round_value(row["global_affine_residual_p90_px_frame"]),
                "global_affine_inlier_ratio": _round_value(row["global_affine_inlier_ratio"]),
                "global_affine_fit_status": row["global_affine_fit_status"],
                "affine_residual_magnitude_mean_px_frame": _round_value(row["affine_residual_magnitude_mean_px_frame"]),
                "affine_residual_magnitude_p90_px_frame": _round_value(row["affine_residual_magnitude_p90_px_frame"]),
                "affine_residual_moving_pixel_ratio": _round_value(row["affine_residual_moving_pixel_ratio"]),
                "exact_duplicate_of_previous": bool(row["exact_duplicate_of_previous"]),
            })

    event_counts: dict[str, int] = {}
    for event in events:
        event_counts[event["event_type"]] = event_counts.get(event["event_type"], 0) + 1

    try:
        numpy_version = importlib.metadata.version("numpy")
    except importlib.metadata.PackageNotFoundError:
        numpy_version = np.__version__
    return {
        "schema_version": "fma.analysis.v0.1",
        "project_version": __version__,
        "input": {"filename": source.name, "sha256": sha256_file(source)},
        "media": metadata,
        "sampling": {
            "requested_max_fps": float(max_fps),
            "analysis_fps": analysis_fps,
            "analysis_width": int(width),
            "analysis_height": int(height),
            "frames_decoded": count,
            "estimated_source_frames_at_analysis_rate": (
                math.ceil(float(duration) * analysis_fps) if duration else None
            ),
            "truncated_by_frame_limit": truncated,
            "timeline_coverage_ratio": round(coverage_ratio, 6) if coverage_ratio is not None else None,
            "sample_rate_ratio_to_source": round(sample_rate_ratio, 6) if sample_rate_ratio is not None else None,
            "sampling_warning": bool(sample_rate_ratio is not None and sample_rate_ratio < 0.8),
            "output_series_stride": stride,
            "output_series_points": len(timeline),
        },
        "measurements": {
            "measurement_space": "downscaled_grayscale_image_plane",
            "absolute_pixel_velocity_available": False,
            "mean_abs_diff_median": _round_value(float(np.median(observed_diffs)) if observed_diffs else 0.0),
            "mean_abs_diff_p95": _round_value(float(np.percentile(observed_diffs, 95)) if observed_diffs else 0.0),
            "mean_abs_diff_p99": _round_value(float(np.percentile(observed_diffs, 99)) if observed_diffs else 0.0),
            "flow_mean_magnitude_median_px_frame": _round_value(float(np.median(flow_mags)) if flow_mags else None),
            "flow_mean_magnitude_p95_px_frame": _round_value(float(np.percentile(flow_mags, 95)) if flow_mags else None),
            "exact_duplicate_transition_count": int(exact_duplicates),
            "exact_duplicate_transition_ratio": round(exact_duplicates / max(1, count - 1), 6),
            "near_black_frame_ratio": round(dark_frames / count, 6),
        },
        "events": events,
        "event_counts": event_counts,
        "timeline": timeline,
        "provenance": {
            "python": platform.python_version(),
            "numpy": numpy_version,
            "ffmpeg": tool_version("ffmpeg"),
            "ffprobe": tool_version("ffprobe"),
            "optical_flow": flow_status,
            "optical_flow_method": "Farneback dense optical flow" if cv2_module is not None else None,
            "camera_motion_proxy": "median dense-flow vector; assumes static background dominates" if cv2_module is not None else None,
            "analysis_config_sha256": hashlib.sha256(
                f"{max_fps}|{width}|{height}|{max_frames}|{bool(optical_flow)}".encode("utf-8")
            ).hexdigest(),
        },
        "interpretation_limits": [
            "Motion quantities refer to the analyzed image plane and are not calibrated physical-world velocities.",
            "No object identity or object-level attribution is inferred by the v0.1 baseline.",
            "Median flow is only a camera-translation proxy when static/background pixels dominate.",
            "A threshold event is a candidate supported by adjacent-frame measurements, not proof of intent or physical cause.",
            "Downsampling, blur, occlusion, low texture, lighting changes, rolling shutter, and compression can distort motion estimates.",
        ],
    }

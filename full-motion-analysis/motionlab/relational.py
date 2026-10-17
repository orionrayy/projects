"""Open-world relational analysis over bounded spatiotemporal volumes.

The primary unit is a space-time block, not a frame pair. Features are intentionally
domain-neutral measurements; they do not imply semantic understanding or physical causality.
"""
from __future__ import annotations

import math
import platform
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from . import __version__
from .media import iter_rgb_frames, probe_media, sha256_file, tool_version

FEATURE_SCHEMA = "fma.openworld.relational-signature.v1"
ANALYSIS_SCHEMA = "fma.openworld.analysis.v0.2"
WINDOW_FRAMES = 16
WINDOW_STRIDE = 8
SPATIAL_SCALES = (1, 2, 4)
TILE_ROWS = 4
TILE_COLS = 6
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".mpeg", ".mpg"}


def _finite(value: float) -> float:
    return float(value) if math.isfinite(float(value)) else 0.0


def _box_reduce(volume: np.ndarray, factor: int) -> np.ndarray:
    if factor <= 1:
        return volume.astype(np.float32, copy=False)
    t, h, w, c = volume.shape
    h2, w2 = h // factor, w // factor
    if h2 < 4 or w2 < 4:
        return volume.astype(np.float32, copy=False)
    cropped = volume[:, :h2 * factor, :w2 * factor, :].astype(np.float32, copy=False)
    return cropped.reshape(t, h2, factor, w2, factor, c).mean(axis=(2, 4))


def _luma(rgb: np.ndarray) -> np.ndarray:
    return (
        rgb[..., 0] * 0.2126
        + rgb[..., 1] * 0.7152
        + rgb[..., 2] * 0.0722
    ).astype(np.float32, copy=False)


def _histogram(values: np.ndarray, bins: int = 8) -> list[float]:
    hist, _ = np.histogram(values, bins=bins, range=(0.0, 1.0))
    total = float(hist.sum())
    if total <= 0:
        return [0.0] * bins
    return [float(item / total) for item in hist]


def _gradient_signature(y: np.ndarray) -> list[float]:
    gx = np.zeros_like(y, dtype=np.float32)
    gy = np.zeros_like(y, dtype=np.float32)
    if y.shape[2] > 2:
        gx[:, :, 1:-1] = (y[:, :, 2:] - y[:, :, :-2]) * 0.5
    if y.shape[1] > 2:
        gy[:, 1:-1, :] = (y[:, 2:, :] - y[:, :-2, :]) * 0.5
    mag = np.sqrt(gx * gx + gy * gy)
    angle = np.arctan2(gy, gx)
    weights = mag.ravel()
    orient, _ = np.histogram(
        angle.ravel(), bins=8, range=(-math.pi, math.pi), weights=weights
    )
    orient = orient.astype(np.float64)
    orient_total = float(orient.sum())
    if orient_total:
        orient /= orient_total
    return [
        _finite(np.mean(np.abs(gx))),
        _finite(np.mean(np.abs(gy))),
        _finite(np.mean(mag)),
        _finite(np.std(mag)),
        _finite(np.percentile(mag, 90)),
        _finite(np.mean(mag >= 0.04)),
        *[_finite(v) for v in orient.tolist()],
    ]


def _spacetime_spectrum(y: np.ndarray) -> list[float]:
    """Summarise energy over temporal-frequency × spatial-frequency bands."""
    centered = y.astype(np.float32, copy=False) - float(np.mean(y))
    if centered.size == 0 or min(centered.shape) < 2:
        return [0.0] * 16
    spectrum = np.fft.fftn(centered, axes=(0, 1, 2))
    energy = np.abs(np.fft.fftshift(spectrum, axes=(0, 1, 2))) ** 2
    ft = np.abs(np.fft.fftshift(np.fft.fftfreq(y.shape[0])))[:, None, None]
    fy = np.fft.fftshift(np.fft.fftfreq(y.shape[1]))[None, :, None]
    fx = np.fft.fftshift(np.fft.fftfreq(y.shape[2]))[None, None, :]
    spatial = np.sqrt(fy * fy + fx * fx) / math.sqrt(0.5)
    temporal_edges = (0.0, 0.04, 0.12, 0.28, 0.51)
    spatial_edges = (0.0, 0.10, 0.25, 0.50, 1.01)
    cells: list[float] = []
    total = float(energy.sum()) + 1e-12
    for ti in range(4):
        temporal_mask = (ft >= temporal_edges[ti]) & (ft < temporal_edges[ti + 1])
        for si in range(4):
            mask = temporal_mask & (spatial >= spatial_edges[si]) & (spatial < spatial_edges[si + 1])
            cells.append(float(energy[mask].sum() / total) if np.any(mask) else 0.0)
    cell_total = sum(cells)
    if cell_total:
        cells = [v / cell_total for v in cells]
    return [_finite(v) for v in cells]


def _spatial_correlations(y: np.ndarray) -> list[float]:
    results: list[float] = []
    for dy, dx in ((0, 1), (1, 0), (0, 2), (2, 0), (0, 4), (4, 0)):
        h, w = y.shape[1:]
        if h <= dy + 2 or w <= dx + 2:
            results.append(0.0)
            continue
        a = y[:, :h-dy or None, :w-dx or None].ravel()
        b = y[:, dy:, dx:].ravel()
        n = min(a.size, b.size)
        a, b = a[:n].astype(np.float64), b[:n].astype(np.float64)
        a -= a.mean()
        b -= b.mean()
        denom = math.sqrt(float(a @ a) * float(b @ b))
        results.append(float((a @ b) / denom) if denom > 1e-12 else 0.0)
    return [_finite(v) for v in results]


def _temporal_signature(y: np.ndarray) -> list[float]:
    """Describe a whole block's temporal envelope without adjacent-frame motion labels."""
    signal = y.mean(axis=(1, 2)).astype(np.float64)
    spatial_activity = y.std(axis=(1, 2)).astype(np.float64)
    n = len(signal)
    if n == 0:
        return [0.0] * 12
    x = np.linspace(-1.0, 1.0, n) if n > 1 else np.zeros(1)
    centered = signal - signal.mean()
    slope = float((x @ centered) / max(float(x @ x), 1e-12))
    quarter = max(1, n // 4)
    early_late = float(signal[-quarter:].mean() - signal[:quarter].mean())
    activity_spectrum = np.abs(np.fft.rfft(spatial_activity - spatial_activity.mean()))
    activity_total = float(activity_spectrum.sum()) + 1e-12
    activity_bins = []
    for left, right in ((0.0, 0.15), (0.15, 0.35), (0.35, 0.65), (0.65, 1.01)):
        freqs = np.fft.rfftfreq(n)
        mask = (freqs >= left) & (freqs < right)
        activity_bins.append(float(activity_spectrum[mask].sum() / activity_total))
    return [
        _finite(signal.mean()), _finite(signal.std()), _finite(np.ptp(signal)),
        _finite(slope), _finite(early_late),
        _finite(spatial_activity.mean()), _finite(spatial_activity.std()),
        _finite(np.percentile(spatial_activity, 90)),
        *[_finite(v) for v in activity_bins],
    ]


def _scale_features(volume: np.ndarray, factor: int) -> tuple[list[str], list[float], np.ndarray]:
    scaled_rgb = _box_reduce(volume, factor) / 255.0
    y = _luma(scaled_rgb)
    prefix = f"scale_{factor}"
    names: list[str] = [
        f"{prefix}_luma_mean", f"{prefix}_luma_std",
    ]
    values: list[float] = [_finite(y.mean()), _finite(y.std())]
    gradient_names = [
        "grad_abs_x", "grad_abs_y", "grad_mean", "grad_std", "grad_p90",
        "grad_occupancy", *[f"grad_orientation_{i}" for i in range(8)],
    ]
    names.extend(f"{prefix}_{name}" for name in gradient_names)
    values.extend(_gradient_signature(y))
    names.extend(f"{prefix}_spatial_corr_{i}" for i in range(6))
    values.extend(_spatial_correlations(y))
    names.extend(f"{prefix}_st_spectrum_t{i}_s{j}" for i in range(4) for j in range(4))
    values.extend(_spacetime_spectrum(y))
    temporal = _temporal_signature(y)
    names.extend(f"{prefix}_temporal_{i}" for i in range(len(temporal)))
    values.extend(temporal)
    return names, values, y


def _tile_signatures(volume: np.ndarray) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[float]]:
    y = _luma(volume / 255.0)
    height, width = y.shape[1:]
    nodes: list[dict[str, Any]] = []
    descriptor_matrix: list[list[float]] = []
    temporal_signals: list[np.ndarray] = []
    for row in range(TILE_ROWS):
        for col in range(TILE_COLS):
            y0, y1 = round(row * height / TILE_ROWS), round((row + 1) * height / TILE_ROWS)
            x0, x1 = round(col * width / TILE_COLS), round((col + 1) * width / TILE_COLS)
            patch_rgb = volume[:, y0:y1, x0:x1, :].astype(np.float32) / 255.0
            patch = y[:, y0:y1, x0:x1]
            temporal = patch.mean(axis=(1, 2)).astype(np.float64)
            temporal_signals.append(temporal)
            bands = np.abs(np.fft.rfft(temporal - temporal.mean()))
            bands = bands / (float(bands.sum()) + 1e-12)
            bins = []
            f = np.fft.rfftfreq(len(temporal))
            for low, high in ((0.0, 0.12), (0.12, 0.28), (0.28, 0.48), (0.48, 1.01)):
                mask = (f >= low) & (f < high)
                bins.append(float(bands[mask].sum()))
            gx = np.diff(patch, axis=2) if patch.shape[2] > 1 else np.zeros_like(patch)
            gy = np.diff(patch, axis=1) if patch.shape[1] > 1 else np.zeros_like(patch)
            descriptor = [
                *[float(patch_rgb[..., channel].mean()) for channel in range(3)],
                *[float(patch_rgb[..., channel].std()) for channel in range(3)],
                float(np.mean(np.abs(gx))), float(np.mean(np.abs(gy))),
                float(np.std(patch)), float(np.mean(np.std(patch, axis=0))),
                *bins, float(temporal[-max(1, len(temporal)//4):].mean() - temporal[:max(1, len(temporal)//4)].mean()),
            ]
            descriptor_matrix.append(descriptor)
            nodes.append({
                "node_id": f"r{row}c{col}",
                "region_norm_xyxy": [
                    round(x0 / width, 4), round(y0 / height, 4),
                    round(x1 / width, 4), round(y1 / height, 4),
                ],
                "descriptor": [_finite(v) for v in descriptor],
                "temporal_energy": _finite(np.std(temporal)),
            })

    matrix = np.asarray(descriptor_matrix, dtype=np.float64)
    center = np.median(matrix, axis=0)
    spread = np.median(np.abs(matrix - center), axis=0) * 1.4826
    spread[spread < 1e-5] = 1.0
    scaled = (matrix - center) / spread
    norm = np.linalg.norm(scaled, axis=1, keepdims=True)
    normalized = scaled / np.maximum(norm, 1e-12)
    edges: list[dict[str, Any]] = []
    neighbor_scores: list[float] = []
    for i in range(TILE_ROWS * TILE_COLS):
        r, c = divmod(i, TILE_COLS)
        for nr, nc in ((r + 1, c), (r, c + 1)):
            if nr < TILE_ROWS and nc < TILE_COLS:
                j = nr * TILE_COLS + nc
                score = float(np.clip(normalized[i] @ normalized[j], -1.0, 1.0))
                neighbor_scores.append(score)
                edges.append({"source": nodes[i]["node_id"], "target": nodes[j]["node_id"], "relation": "spatial_neighbor", "signature_similarity": round(score, 6)})
    remote: list[tuple[float, int, int]] = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if abs(i // TILE_COLS - j // TILE_COLS) + abs(i % TILE_COLS - j % TILE_COLS) <= 1:
                continue
            score = float(np.clip(normalized[i] @ normalized[j], -1.0, 1.0))
            if score >= 0.80:
                remote.append((score, i, j))
    remote.sort(reverse=True)
    for score, i, j in remote[:24]:
        edges.append({"source": nodes[i]["node_id"], "target": nodes[j]["node_id"], "relation": "nonlocal_signature_similarity", "signature_similarity": round(score, 6)})
    remote_scores = [entry[0] for entry in remote]
    relational_summary = [
        _finite(np.mean(neighbor_scores)) if neighbor_scores else 0.0,
        _finite(np.std(neighbor_scores)) if neighbor_scores else 0.0,
        _finite(np.mean(remote_scores)) if remote_scores else 0.0,
        _finite(len(remote_scores) / max(1, len(nodes))),
        _finite(np.std([np.std(v) for v in temporal_signals])),
    ]
    return nodes, edges, relational_summary


def extract_block_signature(volume_rgb: np.ndarray) -> dict[str, Any]:
    """Build a domain-neutral signature and region-relation graph for one space-time block."""
    if volume_rgb.ndim != 4 or volume_rgb.shape[-1] != 3 or volume_rgb.dtype != np.uint8:
        raise ValueError("volume_must_be_uint8_T_H_W_RGB")
    if volume_rgb.shape[0] < 2 or min(volume_rgb.shape[1:3]) < 16:
        raise ValueError("space_time_block_too_small")
    normalized = volume_rgb.astype(np.float32) / 255.0
    names: list[str] = []
    values: list[float] = []
    for channel, channel_name in enumerate(("r", "g", "b")):
        ch = normalized[..., channel]
        names.extend((f"channel_{channel_name}_mean", f"channel_{channel_name}_std"))
        values.extend((_finite(ch.mean()), _finite(ch.std())))
        histogram = _histogram(ch, 8)
        names.extend(f"channel_{channel_name}_hist_{i}" for i in range(8))
        values.extend(histogram)
    scale_records: list[dict[str, Any]] = []
    for factor in SPATIAL_SCALES:
        scale_names, scale_values, y = _scale_features(volume_rgb, factor)
        names.extend(scale_names)
        values.extend(scale_values)
        scale_records.append({
            "spatial_scale": factor,
            "luma_mean": _finite(y.mean()),
            "luma_std": _finite(y.std()),
            "gradient_mean": _finite(np.mean(np.sqrt(np.diff(y, axis=2, append=y[:, :, -1:]) ** 2 + np.diff(y, axis=1, append=y[:, -1:, :]) ** 2))),
        })
    nodes, edges, relation_summary = _tile_signatures(volume_rgb)
    relation_names = [
        "region_neighbor_similarity_mean",
        "region_neighbor_similarity_spread",
        "region_nonlocal_similarity_mean",
        "region_nonlocal_edge_density",
        "region_temporal_energy_spread",
    ]
    names.extend(relation_names)
    values.extend(relation_summary)
    return {
        "feature_schema": FEATURE_SCHEMA,
        "feature_names": names,
        "signature_vector": [_finite(v) for v in values],
        "scale_signatures": scale_records,
        "regional_nodes": nodes,
        "regional_edges": edges,
        "feature_count": len(values),
    }


def _robust_scale(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    median = np.median(matrix, axis=0)
    mad = np.median(np.abs(matrix - median), axis=0) * 1.4826
    std = np.std(matrix, axis=0)
    scale = np.where(mad > 1e-5, mad, np.where(std > 1e-5, std, 1.0))
    return median, scale


def _window_events(windows: list[dict[str, Any]], duplicate_flags: list[bool], fps: float) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if len(windows) > 1:
        matrix = np.asarray([window["signature_vector"] for window in windows], dtype=np.float64)
        _, scale = _robust_scale(matrix)
        distances = [
            float(np.sqrt(np.mean(((matrix[i] - matrix[i - 1]) / scale) ** 2)))
            for i in range(1, len(windows))
        ]
        center = float(np.median(distances)) if distances else 0.0
        mad = float(np.median(np.abs(np.asarray(distances) - center))) if distances else 0.0
        threshold = max(1.0, center + 4.0 * 1.4826 * mad)
        for i, score in enumerate(distances, start=1):
            if score >= threshold:
                window = windows[i]
                events.append({
                    "event_type": "temporal_structure_shift_candidate",
                    "timestamp_s": window["start_timestamp_s"],
                    "end_timestamp_s": window["end_timestamp_s"],
                    "frame_index": window["start_frame_index"],
                    "severity": "high" if score >= threshold * 1.5 else "medium",
                    "rule_id": "FMA-REL-SHIFT-001",
                    "measurement": {"multiscale_signature_distance": round(score, 6), "robust_threshold": round(threshold, 6), "compared_window_indices": [i-1, i]},
                    "interpretation_limit": "A shift in whole-block spatial-temporal structure can reflect motion, appearance, a cut, zoom, exposure, or domain-specific change; it is not a semantic or causal label.",
                })
    run_start: int | None = None
    for i in range(len(duplicate_flags) + 1):
        duplicate = i < len(duplicate_flags) and duplicate_flags[i]
        if duplicate and run_start is None:
            run_start = max(0, i - 1)
        if not duplicate and run_start is not None:
            end_idx = i - 1
            duration = max(0, end_idx - run_start + 1) / max(fps, 1e-9)
            if duration >= 0.5:
                events.append({
                    "event_type": "repeated_frame_run_candidate",
                    "timestamp_s": run_start / fps,
                    "end_timestamp_s": end_idx / fps,
                    "frame_index": run_start,
                    "severity": "medium",
                    "rule_id": "FMA-QC-REPEAT-001",
                    "measurement": {"duration_s": round(duration, 6), "repeated_transitions": i - run_start},
                    "interpretation_limit": "This is a low-level integrity indicator only; a freeze, intentional hold, or genuinely static source require different interpretations.",
                })
            run_start = None
    events.sort(key=lambda item: (item["timestamp_s"], item["event_type"]))
    return events


def _cross_window_relations(windows: list[dict[str, Any]], cap: int = 256) -> list[dict[str, Any]]:
    if len(windows) < 2:
        return []
    if len(windows) > cap:
        ids = np.linspace(0, len(windows) - 1, cap).round().astype(int).tolist()
    else:
        ids = list(range(len(windows)))
    vectors = np.asarray([windows[i]["signature_vector"] for i in ids], dtype=np.float64)
    pairs: list[dict[str, Any]] = []
    _, scale = _robust_scale(vectors)
    normalized = (vectors - np.median(vectors, axis=0)) / scale
    norms = np.linalg.norm(normalized, axis=1)
    for a in range(len(ids)):
        for b in range(a + 2, len(ids)):
            delta = float(np.mean(np.abs(normalized[a] - normalized[b])))
            similarity = math.exp(-delta)
            gap = windows[ids[b]]["center_timestamp_s"] - windows[ids[a]]["center_timestamp_s"]
            if similarity >= 0.90:
                pairs.append({
                    "source_window": ids[a], "target_window": ids[b],
                    "relation": "recurrent_multiscale_signature",
                    "similarity": round(similarity, 6),
                    "temporal_gap_s": round(gap, 6),
                })
    pairs.sort(key=lambda item: item["similarity"], reverse=True)
    return pairs[:512]


def analyze_video(
    path: str | Path,
    *,
    max_fps: float = 30.0,
    width: int = 160,
    height: int = 90,
    max_frames: int = 100_000,
    optical_flow: bool = False,
    window_frames: int = WINDOW_FRAMES,
    window_stride: int = WINDOW_STRIDE,
    model_path: str | Path | None = None,
) -> dict[str, Any]:
    """Analyze a video through multiscale space-time blocks and relational signatures.

    optical_flow remains accepted for caller compatibility but is not used by the v0.2 core.
    """
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError("input_path_must_be_a_file")
    if not 1.0 <= float(max_fps) <= 120.0:
        raise ValueError("max_fps_must_be_between_1_and_120")
    if width < 64 or height < 64 or width % 2 or height % 2:
        raise ValueError("analysis_width_height_must_be_even_and_at_least_64")
    if not 1 <= int(max_frames) <= 1_000_000:
        raise ValueError("max_frames_must_be_between_1_and_1000000")
    if not 2 <= int(window_frames) <= 256:
        raise ValueError("window_frames_must_be_between_2_and_256")
    if not 1 <= int(window_stride) <= int(window_frames):
        raise ValueError("window_stride_must_be_between_1_and_window_frames")

    metadata = probe_media(source)
    source_fps = float(metadata.get("source_fps") or 30.0)
    analysis_fps = min(float(max_fps), source_fps)
    windows: list[dict[str, Any]] = []
    buffer: list[tuple[int, np.ndarray]] = []
    decoded_count = 0
    duplicate_flags: list[bool] = []
    last_frame: np.ndarray | None = None
    near_black_count = 0
    luma_samples: list[float] = []
    last_window_end = -1
    frame_cap_hit = False

    def process_block(items: list[tuple[int, np.ndarray]]) -> None:
        if len(items) < 2:
            return
        index_start, index_end = items[0][0], items[-1][0]
        volume = np.stack([item[1] for item in items], axis=0)
        signature = extract_block_signature(volume)
        start_s = index_start / analysis_fps
        end_s = index_end / analysis_fps
        windows.append({
            "window_index": len(windows),
            "start_frame_index": index_start,
            "end_frame_index": index_end,
            "start_timestamp_s": round(start_s, 6),
            "end_timestamp_s": round(end_s, 6),
            "center_timestamp_s": round((start_s + end_s) / 2.0, 6),
            "feature_schema": signature["feature_schema"],
            "feature_count": signature["feature_count"],
            "signature_vector": signature["signature_vector"],
            "scale_signatures": signature["scale_signatures"],
            "regional_nodes": signature["regional_nodes"],
            "regional_edges": signature["regional_edges"],
        })

    for index, rgb in iter_rgb_frames(
        source, fps=analysis_fps, width=width, height=height, max_frames=int(max_frames)
    ):
        decoded_count += 1
        luma_samples.append(float(_luma(rgb.astype(np.float32) / 255.0).mean()))
        if float(luma_samples[-1]) <= 0.01:
            near_black_count += 1
        if last_frame is not None:
            duplicate_flags.append(bool(np.array_equal(last_frame, rgb)))
        last_frame = rgb
        buffer.append((index, rgb))
        if len(buffer) >= int(window_frames):
            items = buffer[:int(window_frames)]
            process_block(items)
            last_window_end = items[-1][0]
            buffer = buffer[int(window_stride):]

    estimated_frames = (
        int(math.ceil(float(metadata["duration_s"]) * analysis_fps))
        if metadata.get("duration_s") else None
    )
    frame_cap_hit = decoded_count >= int(max_frames) and estimated_frames is not None and estimated_frames > int(max_frames)
    if buffer and buffer[-1][0] > last_window_end and len(buffer) >= 2:
        process_block(buffer)
    if not windows:
        raise RuntimeError("not_enough_decodable_frames_for_space_time_analysis")

    duration = metadata.get("duration_s")
    covered_s = min(float(duration), decoded_count / analysis_fps) if duration else decoded_count / analysis_fps
    coverage = min(1.0, covered_s / float(duration)) if duration else None
    duplicate_ratio = (sum(duplicate_flags) / len(duplicate_flags)) if duplicate_flags else 0.0
    black_ratio = near_black_count / max(1, len(luma_samples))
    event_list = _window_events(windows, duplicate_flags, analysis_fps)
    relation_pairs = _cross_window_relations(windows)
    vectors = np.asarray([window["signature_vector"] for window in windows], dtype=np.float64)
    adjacent_distances = [
        float(np.sqrt(np.mean((vectors[i] - vectors[i-1]) ** 2)))
        for i in range(1, len(vectors))
    ]
    measurements = {
        "space_time_windows": len(windows),
        "feature_dimensions": int(vectors.shape[1]),
        "cross_window_relations": len(relation_pairs),
        "signature_distance_p50": round(float(np.percentile(adjacent_distances, 50)), 6) if adjacent_distances else 0.0,
        "signature_distance_p95": round(float(np.percentile(adjacent_distances, 95)), 6) if adjacent_distances else 0.0,
        "exact_duplicate_transition_ratio": round(duplicate_ratio, 6),
        "near_black_frame_ratio": round(black_ratio, 6),
        "region_node_count_per_window": TILE_ROWS * TILE_COLS,
    }
    report: dict[str, Any] = {
        "schema_version": ANALYSIS_SCHEMA,
        "project_version": "0.2.0",
        "input": {"filename": source.name, "sha256": sha256_file(source)},
        "media": metadata,
        "sampling": {
            "requested_max_fps": float(max_fps),
            "analysis_fps": analysis_fps,
            "analysis_width": int(width),
            "analysis_height": int(height),
            "frames_decoded": decoded_count,
            "estimated_source_frames_at_analysis_rate": estimated_frames,
            "timeline_coverage_ratio": round(coverage, 6) if coverage is not None else None,
            "sampling_rate_ratio": min(1.0, analysis_fps / source_fps) if source_fps else None,
            "truncated_by_frame_limit": frame_cap_hit,
            "window_frames": int(window_frames),
            "window_stride": int(window_stride),
            "analysis_unit": "overlapping_spatiotemporal_volume",
            "pairwise_frame_analysis_is_primary": False,
        },
        "measurements": measurements,
        "timeline": windows,
        "events": event_list,
        "event_counts": _count_events(event_list),
        "relational_field": {
            "schema_version": "fma.relational-field.v1",
            "unit": "space_time_window",
            "node_semantics": "fixed spatial regions summarized over a temporal block; not object identities",
            "cross_window_relations": relation_pairs,
            "window_relation_cap": 256,
        },
        "provenance": {
            "architecture": "open_world_spatiotemporal_relations",
            "feature_schema": FEATURE_SCHEMA,
            "decode_backend": tool_version("ffmpeg"),
            "probe_backend": tool_version("ffprobe"),
            "numpy_version": np.__version__,
            "python_version": platform.python_version(),
            "requested_legacy_optical_flow": bool(optical_flow),
            "legacy_pairwise_optical_flow_used_by_core": False,
            "source_sha256": sha256_file(source),
        },
        "interpretation_limits": [
            "The feature substrate is domain-neutral but not semantically universal; no bounded system can guarantee a correct interpretation of every possible visual phenomenon.",
            "Temporal signatures summarize sampled space-time volumes and can miss events shorter than the sampling interval or features below the selected spatial scale.",
            "Region nodes describe fixed image regions over a block, not persistent object identities, segmentations, 3D motion, intent, or causality.",
            "Fourier energy and multiscale statistics describe structural regularities but can be ambiguous across different visual processes.",
            "Repeated exact frames are reported as an integrity signal; intentional holds and genuine static scenes are not automatically classified as defects.",
            "The unsupervised model learns corpus-specific relation patterns and novelty profiles; it does not automatically learn human semantics or prove cross-domain generalization.",
        ],
    }
    if model_path is not None:
        from .learning import load_model, score_windows
        report["learned_analysis"] = score_windows(report, load_model(model_path))
    return report


def _count_events(events: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        key = str(event["event_type"])
        counts[key] = counts.get(key, 0) + 1
    return counts

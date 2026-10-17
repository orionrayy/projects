"""Frame-pair measurements. These are image-plane observables, not physical-world truth."""
from __future__ import annotations

import math
from typing import Any

import numpy as np


def normalized_histogram(frame: np.ndarray, bins: int = 32) -> np.ndarray:
    hist, _ = np.histogram(frame, bins=bins, range=(0, 256))
    hist = hist.astype(np.float64)
    total = float(hist.sum())
    return hist / total if total else hist


def histogram_distance(a: np.ndarray, b: np.ndarray, bins: int = 32) -> float:
    """Total-variation distance between grayscale histograms in [0, 1]."""
    ha = normalized_histogram(a, bins)
    hb = normalized_histogram(b, bins)
    return float(0.5 * np.abs(ha - hb).sum())


def measure_frame_pair(
    previous: np.ndarray,
    current: np.ndarray,
    *,
    cv2_module: Any | None = None,
) -> dict[str, float | None]:
    """Measure change and optional dense optical flow for two equal-sized gray frames."""
    if previous.ndim != 2 or current.ndim != 2:
        raise ValueError("frames_must_be_2d_grayscale")
    if previous.shape != current.shape:
        raise ValueError("frame_shapes_must_match")
    if previous.dtype != np.uint8 or current.dtype != np.uint8:
        raise ValueError("frames_must_be_uint8")

    delta = np.abs(current.astype(np.int16) - previous.astype(np.int16)).astype(np.uint8)
    mean_diff = float(delta.mean()) / 255.0
    changed_ratio = float(np.count_nonzero(delta >= 12)) / float(delta.size)
    hist_delta = histogram_distance(previous, current)

    weights = delta.astype(np.float64)
    total_weight = float(weights.sum())
    if total_weight > 0:
        x_weights = np.arange(current.shape[1], dtype=np.float64)[None, :]
        y_weights = np.arange(current.shape[0], dtype=np.float64)[:, None]
        cx = float((weights * x_weights).sum() / total_weight)
        cy = float((weights * y_weights).sum() / total_weight)
        cx_norm = cx / max(1, current.shape[1] - 1)
        cy_norm = cy / max(1, current.shape[0] - 1)
    else:
        cx_norm = None
        cy_norm = None

    result: dict[str, float | None] = {
        "mean_abs_diff": mean_diff,
        "changed_pixel_ratio": changed_ratio,
        "histogram_delta": hist_delta,
        "difference_centroid_x_norm": cx_norm,
        "difference_centroid_y_norm": cy_norm,
        "flow_mean_dx_px_frame": None,
        "flow_mean_dy_px_frame": None,
        "flow_mean_magnitude_px_frame": None,
        "flow_global_median_dx_px_frame": None,
        "flow_global_median_dy_px_frame": None,
        "flow_residual_mean_px_frame": None,
        "flow_coherence": None,
        "direction_deg_image_coordinates": None,
    }

    if cv2_module is None:
        return result

    flow = cv2_module.calcOpticalFlowFarneback(
        previous, current, None, 0.5, 3, 15, 3, 5, 1.2, 0
    )
    fx = flow[..., 0].astype(np.float32)
    fy = flow[..., 1].astype(np.float32)
    magnitude = np.sqrt(fx * fx + fy * fy)
    mean_dx = float(fx.mean())
    mean_dy = float(fy.mean())
    mean_mag = float(magnitude.mean())
    median_dx = float(np.median(fx))
    median_dy = float(np.median(fy))
    residual = np.sqrt((fx - median_dx) ** 2 + (fy - median_dy) ** 2)
    mean_vector_mag = math.hypot(mean_dx, mean_dy)

    result.update({
        "flow_mean_dx_px_frame": mean_dx,
        "flow_mean_dy_px_frame": mean_dy,
        "flow_mean_magnitude_px_frame": mean_mag,
        "flow_global_median_dx_px_frame": median_dx,
        "flow_global_median_dy_px_frame": median_dy,
        "flow_residual_mean_px_frame": float(residual.mean()),
        "flow_coherence": min(1.0, mean_vector_mag / max(mean_mag, 1e-8)),
        "direction_deg_image_coordinates": (
            math.degrees(math.atan2(mean_dy, mean_dx))
            if mean_vector_mag > 1e-5 else None
        ),
    })
    return result


def robust_high_threshold(values: list[float], *, floor: float, mad_multiplier: float = 3.5) -> float:
    """Median/MAD high threshold; deterministic and less outlier-sensitive than mean/std."""
    if not values:
        return floor
    array = np.asarray(values, dtype=np.float64)
    med = float(np.median(array))
    mad = float(np.median(np.abs(array - med)))
    sigma_robust = 1.4826 * mad
    return max(float(floor), med + mad_multiplier * max(sigma_robust, 1e-6))

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
) -> dict[str, Any]:
    """Measure adjacent-frame change and optional dense flow with a spatial grid."""
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

    result: dict[str, Any] = {
        "mean_abs_diff": mean_diff,
        "changed_pixel_ratio": changed_ratio,
        "histogram_delta": hist_delta,
        "difference_centroid_x_norm": cx_norm,
        "difference_centroid_y_norm": cy_norm,
        "flow_mean_dx_px_frame": None,
        "flow_mean_dy_px_frame": None,
        "flow_mean_magnitude_px_frame": None,
        "flow_magnitude_p90_px_frame": None,
        "flow_moving_pixel_ratio": None,
        "flow_global_median_dx_px_frame": None,
        "flow_global_median_dy_px_frame": None,
        "flow_residual_mean_px_frame": None,
        "flow_coherence": None,
        "direction_deg_image_coordinates": None,
        "global_affine_translation_dx_px_frame": None,
        "global_affine_translation_dy_px_frame": None,
        "global_affine_rotation_deg_frame": None,
        "global_affine_scale_factor": None,
        "global_affine_residual_median_px_frame": None,
        "global_affine_residual_p90_px_frame": None,
        "global_affine_inlier_ratio": None,
        "global_affine_fit_status": "unavailable",
        "flow_grid": None,
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
    moving_mask = magnitude >= 0.5

    result.update({
        "flow_mean_dx_px_frame": mean_dx,
        "flow_mean_dy_px_frame": mean_dy,
        "flow_mean_magnitude_px_frame": mean_mag,
        "flow_magnitude_p90_px_frame": float(np.percentile(magnitude, 90)),
        "flow_moving_pixel_ratio": float(np.mean(moving_mask)),
        "flow_global_median_dx_px_frame": median_dx,
        "flow_global_median_dy_px_frame": median_dy,
        "flow_residual_mean_px_frame": float(residual.mean()),
        "flow_coherence": min(1.0, mean_vector_mag / max(mean_mag, 1e-8)),
        "direction_deg_image_coordinates": (
            math.degrees(math.atan2(mean_dy, mean_dx))
            if mean_vector_mag > 1e-5 else None
        ),
    })

    # Robust global affine fit estimates dominant image-plane camera/scene motion.
    # Local residual is a proxy only; it is not physical causality or object segmentation.
    if hasattr(cv2_module, "estimateAffinePartial2D"):
        step = max(4, min(height, width) // 20)
        ys, xs = np.mgrid[step // 2:height:step, step // 2:width:step]
        source_points = np.stack([xs.ravel(), ys.ravel()], axis=1).astype(np.float32)
        sampled_dx = fx[ys, xs].ravel().astype(np.float32)
        sampled_dy = fy[ys, xs].ravel().astype(np.float32)
        valid = np.isfinite(sampled_dx) & np.isfinite(sampled_dy)
        source_points = source_points[valid]
        sampled_flow = np.stack([sampled_dx[valid], sampled_dy[valid]], axis=1)
        if len(source_points) >= 6:
            destination_points = source_points + sampled_flow
            matrix, inliers = cv2_module.estimateAffinePartial2D(
                source_points, destination_points, method=getattr(cv2_module, "RANSAC", 8),
                ransacReprojThreshold=2.0, maxIters=200, confidence=0.99, refineIters=10,
            )
            if matrix is not None and np.asarray(matrix).shape == (2, 3) and np.isfinite(matrix).all():
                affine = np.asarray(matrix, dtype=np.float64)
                predicted = source_points.astype(np.float64) @ affine[:, :2].T + affine[:, 2]
                residuals = np.sqrt(np.sum((destination_points.astype(np.float64) - predicted) ** 2, axis=1))
                a, c = float(affine[0, 0]), float(affine[1, 0])
                inlier_ratio = (
                    float(np.mean(np.asarray(inliers).reshape(-1) > 0))
                    if inliers is not None else None
                )
                result.update({
                    "global_affine_translation_dx_px_frame": float(affine[0, 2]),
                    "global_affine_translation_dy_px_frame": float(affine[1, 2]),
                    "global_affine_rotation_deg_frame": math.degrees(math.atan2(c, a)),
                    "global_affine_scale_factor": math.hypot(a, c),
                    "global_affine_residual_median_px_frame": float(np.median(residuals)),
                    "global_affine_residual_p90_px_frame": float(np.percentile(residuals, 90)),
                    "global_affine_inlier_ratio": inlier_ratio,
                    "global_affine_fit_status": "fit",
                })
            else:
                result["global_affine_fit_status"] = "fit_failed"
        else:
            result["global_affine_fit_status"] = "insufficient_valid_points"

    # A compact spatial field summary preserves multi-region variation lost by one global mean.
    # Grid cells are regions, not object identities or segmented object tracks.
    grid_rows, grid_cols = 4, 6
    height, width = magnitude.shape
    grid: list[dict[str, Any]] = []
    for grid_y in range(grid_rows):
        y0, y1 = round(grid_y * height / grid_rows), round((grid_y + 1) * height / grid_rows)
        for grid_x in range(grid_cols):
            x0, x1 = round(grid_x * width / grid_cols), round((grid_x + 1) * width / grid_cols)
            cell_fx = fx[y0:y1, x0:x1]
            cell_fy = fy[y0:y1, x0:x1]
            cell_mag = magnitude[y0:y1, x0:x1]
            cell_mean_dx = float(cell_fx.mean())
            cell_mean_dy = float(cell_fy.mean())
            cell_mean_mag = float(cell_mag.mean())
            grid.append({
                "row": grid_y,
                "column": grid_x,
                "x0_norm": round(x0 / width, 4),
                "y0_norm": round(y0 / height, 4),
                "x1_norm": round(x1 / width, 4),
                "y1_norm": round(y1 / height, 4),
                "mean_dx_px_frame": cell_mean_dx,
                "mean_dy_px_frame": cell_mean_dy,
                "mean_magnitude_px_frame": cell_mean_mag,
                "p90_magnitude_px_frame": float(np.percentile(cell_mag, 90)),
                "moving_pixel_ratio": float(np.mean(cell_mag >= 0.5)),
                "coherence": min(
                    1.0,
                    math.hypot(cell_mean_dx, cell_mean_dy) / max(cell_mean_mag, 1e-8),
                ),
            })
    result["flow_grid"] = grid
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

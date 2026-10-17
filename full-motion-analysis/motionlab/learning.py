"""CPU-first self-supervised relational-model fitting and novelty scoring.

This learns corpus-specific structure prototypes from unlabeled space-time signatures.
It does not learn human semantics, physical laws, or guaranteed cross-domain invariance.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

MODEL_SCHEMA = "fma.openworld.relational-model.v1"


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _matrix(examples: Iterable[dict[str, Any]]) -> np.ndarray:
    rows = [item.get("vector") for item in examples]
    if not rows:
        raise ValueError("training_examples_empty")
    matrix = np.asarray(rows, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[1] < 8 or matrix.shape[0] < 2:
        raise ValueError("training_requires_at_least_two_vectors_with_eight_features")
    if not np.isfinite(matrix).all():
        raise ValueError("training_features_contain_non_finite_values")
    return matrix


def _canonicalize_component_signs(components: np.ndarray) -> np.ndarray:
    result = components.copy()
    for i in range(result.shape[0]):
        pivot = int(np.argmax(np.abs(result[i])))
        if result[i, pivot] < 0:
            result[i] *= -1.0
    return result


def _kmeans(data: np.ndarray, max_clusters: int, iterations: int = 30) -> tuple[np.ndarray, np.ndarray]:
    unique = np.unique(np.round(data, decimals=8), axis=0)
    k = max(1, min(int(max_clusters), len(unique), len(data)))
    if k == 1:
        centers = np.mean(data, axis=0, keepdims=True)
    else:
        # Deterministic farthest-first initialization; no RNG or external ML dependency.
        first = int(np.argmax(np.sum((data - data.mean(axis=0)) ** 2, axis=1)))
        chosen = [first]
        min_distance = np.sum((data - data[first]) ** 2, axis=1)
        while len(chosen) < k:
            next_index = int(np.argmax(min_distance))
            if next_index in chosen:
                remaining = [i for i in range(len(data)) if i not in chosen]
                if not remaining:
                    break
                next_index = max(remaining, key=lambda i: (float(min_distance[i]), -i))
            chosen.append(next_index)
            min_distance = np.minimum(min_distance, np.sum((data - data[next_index]) ** 2, axis=1))
        centers = data[chosen].copy()
    for _ in range(iterations):
        squared = np.sum((data[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        labels = np.argmin(squared, axis=1)
        updated = centers.copy()
        nearest_error = np.min(squared, axis=1)
        for cluster in range(len(centers)):
            members = data[labels == cluster]
            if len(members):
                updated[cluster] = members.mean(axis=0)
            else:
                updated[cluster] = data[int(np.argmax(nearest_error))]
        if np.allclose(updated, centers, rtol=1e-5, atol=1e-7):
            centers = updated
            break
        centers = updated
    distances = np.sqrt(np.sum((data - centers[labels]) ** 2, axis=1))
    return centers, distances


def fit_relational_model(
    train_examples: list[dict[str, Any]],
    *,
    max_components: int = 24,
    max_prototypes: int = 12,
) -> dict[str, Any]:
    matrix = _matrix(train_examples)
    median = np.median(matrix, axis=0)
    mad = np.median(np.abs(matrix - median), axis=0) * 1.4826
    std = np.std(matrix, axis=0)
    scale = np.where(mad > 1e-6, mad, np.where(std > 1e-6, std, 1.0))
    standardized = np.clip((matrix - median) / scale, -12.0, 12.0)
    covariance = (standardized.T @ standardized) / max(1, len(standardized) - 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    component_count = max(1, min(int(max_components), matrix.shape[1], len(matrix) - 1))
    eigenvalues = np.maximum(eigenvalues[order[:component_count]], 1e-8)
    components = _canonicalize_component_signs(eigenvectors[:, order[:component_count]].T)
    projected = standardized @ components.T
    projection_scale = np.sqrt(eigenvalues)
    latent = np.clip(projected / projection_scale, -15.0, 15.0)
    centers, distances = _kmeans(latent, max_prototypes)
    squared = np.sum((latent[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    labels = np.argmin(squared, axis=1)
    radii: list[float] = []
    for cluster in range(len(centers)):
        cluster_distances = np.sqrt(squared[labels == cluster, cluster])
        radius = float(np.percentile(cluster_distances, 95)) if len(cluster_distances) else 0.0
        radii.append(max(radius, 1e-3))
    counts = np.bincount(labels, minlength=len(centers)).tolist()
    model = {
        "schema_version": MODEL_SCHEMA,
        "feature_schema": "fma.openworld.relational-signature.v1",
        "training_mode": "unlabeled_robust_whitening_pca_and_farthest_first_prototypes",
        "input_dimensions": int(matrix.shape[1]),
        "sample_count": int(matrix.shape[0]),
        "max_components_requested": int(max_components),
        "max_prototypes_requested": int(max_prototypes),
        "normalizer_median": median.tolist(),
        "normalizer_scale": scale.tolist(),
        "components": components.tolist(),
        "component_scale": projection_scale.tolist(),
        "prototypes": centers.tolist(),
        "prototype_radii_p95": radii,
        "training_cluster_counts": counts,
        "limitations": [
            "Prototype IDs are anonymous structure clusters, not semantic classes.",
            "Novelty indicates distance from this training corpus and is not a calibrated probability.",
            "Unsupervised fit quality does not establish domain generalization or motion-understanding accuracy.",
        ],
    }
    model["model_sha256"] = canonical_sha256(model)
    return model


def _transform(model: dict[str, Any], vectors: np.ndarray) -> np.ndarray:
    dimensions = int(model["input_dimensions"])
    if vectors.ndim != 2 or vectors.shape[1] != dimensions:
        raise ValueError("model_feature_dimension_mismatch")
    median = np.asarray(model["normalizer_median"], dtype=np.float64)
    scale = np.asarray(model["normalizer_scale"], dtype=np.float64)
    components = np.asarray(model["components"], dtype=np.float64)
    component_scale = np.asarray(model["component_scale"], dtype=np.float64)
    standardized = np.clip((vectors - median) / np.maximum(scale, 1e-8), -12.0, 12.0)
    return np.clip((standardized @ components.T) / np.maximum(component_scale, 1e-8), -15.0, 15.0)


def score_vectors(model: dict[str, Any], vectors: np.ndarray) -> list[dict[str, Any]]:
    latent = _transform(model, vectors)
    centers = np.asarray(model["prototypes"], dtype=np.float64)
    radii = np.asarray(model["prototype_radii_p95"], dtype=np.float64)
    dists = np.sqrt(np.sum((latent[:, None, :] - centers[None, :, :]) ** 2, axis=2))
    labels = np.argmin(dists, axis=1)
    results: list[dict[str, Any]] = []
    for i, label in enumerate(labels.tolist()):
        distance = float(dists[i, label])
        radius = float(radii[label])
        results.append({
            "prototype_id": int(label),
            "prototype_distance": round(distance, 6),
            "novelty_ratio": round(distance / max(radius, 1e-8), 6),
            "outside_training_radius": bool(distance > radius),
        })
    return results


def score_windows(report: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    windows = report.get("timeline", [])
    if not windows:
        return {"status": "NO_WINDOWS", "model_sha256": model.get("model_sha256"), "windows": []}
    vectors = np.asarray([window["signature_vector"] for window in windows], dtype=np.float64)
    scores = score_vectors(model, vectors)
    return {
        "status": "SCORED",
        "model_sha256": model.get("model_sha256"),
        "interpretation": "Corpus-relative anonymous prototype assignment and novelty ratio; not semantic recognition or calibrated probability.",
        "windows": [
            {"window_index": int(window["window_index"]), **score}
            for window, score in zip(windows, scores)
        ],
    }


def load_model(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).expanduser().resolve(strict=True).read_text(encoding="utf-8"))
    if data.get("schema_version") != MODEL_SCHEMA:
        raise ValueError("unsupported_relational_model_schema")
    claimed = data.get("model_sha256")
    payload = dict(data)
    payload.pop("model_sha256", None)
    if claimed != canonical_sha256(payload):
        raise ValueError("model_integrity_check_failed")
    if len(data.get("normalizer_median", [])) != int(data.get("input_dimensions", -1)):
        raise ValueError("model_normalizer_dimension_mismatch")
    return data


def write_json_atomic(path: str | Path, data: dict[str, Any]) -> Path:
    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    rendered = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(destination)
    return destination


def validation_summary(model: dict[str, Any], validation_examples: list[dict[str, Any]]) -> dict[str, Any]:
    if not validation_examples:
        return {
            "status": "NOT_AVAILABLE",
            "validation_video_count": 0,
            "mean_quantization_distance": None,
            "mean_single_prototype_baseline_distance": None,
            "relative_quantization_improvement": None,
            "occupied_prototype_count": 0,
            "largest_cluster_fraction": None,
        }
    matrix = _matrix(validation_examples)
    latent = _transform(model, matrix)
    centers = np.asarray(model["prototypes"], dtype=np.float64)
    dists = np.sqrt(np.sum((latent[:, None, :] - centers[None, :, :]) ** 2, axis=2))
    quant = np.min(dists, axis=1)
    baseline_center = latent.mean(axis=0, keepdims=True)
    baseline = np.sqrt(np.sum((latent - baseline_center) ** 2, axis=1))
    baseline_mean = float(np.mean(baseline))
    quant_mean = float(np.mean(quant))
    improvement = (baseline_mean - quant_mean) / max(baseline_mean, 1e-8)
    labels = np.argmin(dists, axis=1)
    counts = np.bincount(labels, minlength=len(centers))
    nonzero = counts[counts > 0]
    return {
        "status": "COMPUTED",
        "validation_example_count": int(len(matrix)),
        "mean_quantization_distance": round(quant_mean, 6),
        "p95_quantization_distance": round(float(np.percentile(quant, 95)), 6),
        "mean_single_prototype_baseline_distance": round(baseline_mean, 6),
        "relative_quantization_improvement": round(float(improvement), 6),
        "occupied_prototype_count": int(len(nonzero)),
        "largest_cluster_fraction": round(float(nonzero.max() / len(matrix)), 6) if len(nonzero) else 1.0,
    }

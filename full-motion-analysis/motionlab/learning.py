"""CPU-first self-supervised relational encoder and corpus-relative novelty model.

A small NumPy denoising autoencoder is trained without semantic labels; deterministic
prototypes summarize its latent space. No LLM, GPU, Torch, scikit-learn or paid API is required.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

MODEL_SCHEMA = "fma.openworld.relational-model.v2"


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


def _init_weights(input_dim: int, hidden_dim: int, latent_dim: int, rng: np.random.Generator) -> dict[str, np.ndarray]:
    def glorot(fan_in: int, fan_out: int) -> np.ndarray:
        limit = math.sqrt(6.0 / max(1, fan_in + fan_out))
        return rng.uniform(-limit, limit, size=(fan_in, fan_out)).astype(np.float64)
    return {
        "w1": glorot(input_dim, hidden_dim),
        "b1": np.zeros(hidden_dim, dtype=np.float64),
        "w2": glorot(hidden_dim, latent_dim),
        "b2": np.zeros(latent_dim, dtype=np.float64),
        "w3": glorot(latent_dim, hidden_dim),
        "b3": np.zeros(hidden_dim, dtype=np.float64),
        "w4": glorot(hidden_dim, input_dim),
        "b4": np.zeros(input_dim, dtype=np.float64),
    }


def _forward(x: np.ndarray, weights: dict[str, np.ndarray]) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    h1 = np.tanh(x @ weights["w1"] + weights["b1"])
    z = np.tanh(h1 @ weights["w2"] + weights["b2"])
    h3 = np.tanh(z @ weights["w3"] + weights["b3"])
    reconstruction = h3 @ weights["w4"] + weights["b4"]
    return reconstruction, (h1, z, h3)


def _encode(x: np.ndarray, weights: dict[str, np.ndarray]) -> np.ndarray:
    h1 = np.tanh(x @ weights["w1"] + weights["b1"])
    return np.tanh(h1 @ weights["w2"] + weights["b2"])


def _clean_mse(x: np.ndarray, weights: dict[str, np.ndarray]) -> float:
    reconstruction, _ = _forward(x, weights)
    return float(np.mean((reconstruction - x) ** 2))


def _train_encoder(
    x: np.ndarray,
    *,
    hidden_dim: int,
    latent_dim: int,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    mask_probability: float,
    seed: int,
) -> tuple[dict[str, np.ndarray], list[float]]:
    if epochs < 1 or epochs > 200:
        raise ValueError("encoder_epochs_must_be_between_1_and_200")
    if batch_size < 2 or batch_size > 4096:
        raise ValueError("encoder_batch_size_must_be_between_2_and_4096")
    if hidden_dim < 4 or hidden_dim > 256 or latent_dim < 2 or latent_dim > hidden_dim:
        raise ValueError("invalid_encoder_dimensions")
    if not 0.0 < learning_rate <= 0.05:
        raise ValueError("learning_rate_must_be_in_0_to_0_05")
    if not 0.0 <= mask_probability <= 0.5:
        raise ValueError("mask_probability_must_be_between_0_and_0_5")

    rng = np.random.default_rng(seed)
    weights = _init_weights(x.shape[1], hidden_dim, latent_dim, rng)
    m = {key: np.zeros_like(value) for key, value in weights.items()}
    v = {key: np.zeros_like(value) for key, value in weights.items()}
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    step = 0
    trace = [_clean_mse(x, weights)]
    sample_count, feature_count = x.shape

    for _epoch in range(epochs):
        order = rng.permutation(sample_count)
        for start in range(0, sample_count, batch_size):
            target = x[order[start:start + batch_size]]
            corrupted = target.copy()
            corrupted *= (rng.random(corrupted.shape) >= mask_probability)
            corrupted += rng.normal(0.0, 0.015, size=corrupted.shape)
            reconstruction, (h1, z, h3) = _forward(corrupted, weights)

            # Denoising reconstruction: damaged signature -> intact signature.
            delta = (2.0 / max(1, target.shape[0] * feature_count)) * (reconstruction - target)
            grads: dict[str, np.ndarray] = {
                "w4": h3.T @ delta,
                "b4": delta.sum(axis=0),
            }
            dh3 = (delta @ weights["w4"].T) * (1.0 - h3 * h3)
            grads["w3"] = z.T @ dh3
            grads["b3"] = dh3.sum(axis=0)
            dz = (dh3 @ weights["w3"].T) * (1.0 - z * z)
            grads["w2"] = h1.T @ dz
            grads["b2"] = dz.sum(axis=0)
            dh1 = (dz @ weights["w2"].T) * (1.0 - h1 * h1)
            grads["w1"] = corrupted.T @ dh1
            grads["b1"] = dh1.sum(axis=0)

            # Gradient norm clipping bounds damage from corrupted/outlier examples.
            norm = math.sqrt(sum(float(np.sum(grad * grad)) for grad in grads.values()))
            if not math.isfinite(norm):
                raise ValueError("non_finite_encoder_gradient")
            if norm > 5.0:
                grads = {key: grad * (5.0 / norm) for key, grad in grads.items()}

            step += 1
            for key, grad in grads.items():
                m[key] = beta1 * m[key] + (1.0 - beta1) * grad
                v[key] = beta2 * v[key] + (1.0 - beta2) * grad * grad
                m_hat = m[key] / (1.0 - beta1 ** step)
                v_hat = v[key] / (1.0 - beta2 ** step)
                weights[key] -= learning_rate * m_hat / (np.sqrt(v_hat) + eps)
                if not np.isfinite(weights[key]).all():
                    raise ValueError("non_finite_encoder_parameter")
        trace.append(_clean_mse(x, weights))
    return weights, trace


def _kmeans(data: np.ndarray, max_clusters: int, iterations: int = 30) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    unique = np.unique(np.round(data, decimals=8), axis=0)
    k = max(1, min(int(max_clusters), len(unique), len(data)))
    if k == 1:
        centers = data.mean(axis=0, keepdims=True)
    else:
        # Deterministic farthest-first initialization, without external ML libraries.
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
            updated[cluster] = members.mean(axis=0) if len(members) else data[int(np.argmax(nearest_error))]
        if np.allclose(updated, centers, rtol=1e-5, atol=1e-7):
            centers = updated
            break
        centers = updated
    squared = np.sum((data[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    labels = np.argmin(squared, axis=1)
    distances = np.sqrt(squared[np.arange(len(data)), labels])
    return centers, labels, distances


def fit_relational_model(
    train_examples: list[dict[str, Any]],
    *,
    max_components: int = 24,
    max_prototypes: int = 12,
    encoder_hidden_dim: int = 48,
    encoder_epochs: int = 8,
    encoder_batch_size: int = 64,
    learning_rate: float = 0.002,
    mask_probability: float = 0.12,
    seed: int = 20261018,
) -> dict[str, Any]:
    matrix = _matrix(train_examples)
    median = np.median(matrix, axis=0)
    mad = np.median(np.abs(matrix - median), axis=0) * 1.4826
    std = np.std(matrix, axis=0)
    scale = np.where(mad > 1e-6, mad, np.where(std > 1e-6, std, 1.0))
    standardized = np.clip((matrix - median) / scale, -8.0, 8.0)
    latent_dim = max(2, min(int(max_components), int(encoder_hidden_dim)))
    weights, loss_trace = _train_encoder(
        standardized,
        hidden_dim=int(encoder_hidden_dim),
        latent_dim=latent_dim,
        epochs=int(encoder_epochs),
        batch_size=int(encoder_batch_size),
        learning_rate=float(learning_rate),
        mask_probability=float(mask_probability),
        seed=int(seed),
    )
    latent = _encode(standardized, weights)
    centers, labels, distances = _kmeans(latent, max_prototypes)
    radii = []
    for cluster in range(len(centers)):
        values = distances[labels == cluster]
        radii.append(max(float(np.percentile(values, 95)) if len(values) else 0.0, 1e-3))
    model = {
        "schema_version": MODEL_SCHEMA,
        "feature_schema": "fma.openworld.relational-signature.v1",
        "training_mode": "unlabeled_denoising_autoencoder_plus_deterministic_prototypes",
        "embedding_method": "numpy_denoising_autoencoder",
        "input_dimensions": int(matrix.shape[1]),
        "embedding_dimensions": int(latent_dim),
        "sample_count": int(matrix.shape[0]),
        "encoder_hidden_dim": int(encoder_hidden_dim),
        "encoder_epochs": int(encoder_epochs),
        "encoder_batch_size": int(encoder_batch_size),
        "encoder_learning_rate": float(learning_rate),
        "encoder_mask_probability": float(mask_probability),
        "encoder_seed": int(seed),
        "normalizer_median": median.tolist(),
        "normalizer_scale": scale.tolist(),
        "encoder_weights": {key: value.tolist() for key, value in weights.items()},
        "prototypes": centers.tolist(),
        "prototype_radii_p95": radii,
        "training_cluster_counts": np.bincount(labels, minlength=len(centers)).tolist(),
        "single_prototype_baseline_center": latent.mean(axis=0).tolist(),
        "training_diagnostics": {
            "initial_clean_reconstruction_mse": round(float(loss_trace[0]), 8),
            "final_clean_reconstruction_mse": round(float(loss_trace[-1]), 8),
            "clean_reconstruction_mse_by_epoch": [round(float(value), 8) for value in loss_trace],
            "training_loss_decreased": bool(loss_trace[-1] < loss_trace[0]),
        },
        "limitations": [
            "The encoder learns from hand-designed space-time signatures; it is not an end-to-end pixel foundation model.",
            "Prototype IDs are anonymous corpus-relative structure clusters, not semantic classes.",
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
    standardized = np.clip((vectors - median) / np.maximum(scale, 1e-8), -8.0, 8.0)
    if "encoder_weights" in model:
        weights = {key: np.asarray(value, dtype=np.float64) for key, value in model["encoder_weights"].items()}
        return _encode(standardized, weights)
    # Read-only compatibility path for earlier PCA/prototype snapshots.
    components = np.asarray(model["components"], dtype=np.float64)
    component_scale = np.asarray(model["component_scale"], dtype=np.float64)
    return np.clip((standardized @ components.T) / np.maximum(component_scale, 1e-8), -15.0, 15.0)


def score_vectors(model: dict[str, Any], vectors: np.ndarray) -> list[dict[str, Any]]:
    latent = _transform(model, vectors)
    centers = np.asarray(model["prototypes"], dtype=np.float64)
    radii = np.asarray(model["prototype_radii_p95"], dtype=np.float64)
    dists = np.sqrt(np.sum((latent[:, None, :] - centers[None, :, :]) ** 2, axis=2))
    labels = np.argmin(dists, axis=1)
    results = []
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
        "embedding_method": model.get("embedding_method", "legacy_pca"),
        "interpretation": "Corpus-relative anonymous prototype assignment and novelty ratio; not semantic recognition or calibrated probability.",
        "windows": [
            {"window_index": int(window["window_index"]), **score}
            for window, score in zip(windows, scores)
        ],
    }


def load_model(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).expanduser().resolve(strict=True).read_text(encoding="utf-8"))
    if data.get("schema_version") not in {MODEL_SCHEMA, "fma.openworld.relational-model.v1"}:
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
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
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
    baseline_center = np.asarray(model.get("single_prototype_baseline_center", []), dtype=np.float64)
    if baseline_center.shape != (latent.shape[1],):
        raise ValueError("model_baseline_center_dimension_mismatch")
    baseline = np.sqrt(np.sum((latent - baseline_center[None, :]) ** 2, axis=1))
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

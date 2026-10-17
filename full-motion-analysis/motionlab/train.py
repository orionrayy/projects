"""Automatic local-corpus training for the open-world relational model.

The default workflow discovers local videos, deduplicates by SHA-256, analyzes each video
with the same domain-neutral signature engine, splits by source video (never by window),
fits an unlabeled model, validates on held-out videos, and conditionally promotes it.
No video is downloaded, uploaded, or added to Git by this command.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from typing import Any

from .learning import canonical_sha256, fit_relational_model, validation_summary, write_json_atomic
from .media import sha256_file
from .relational import VIDEO_EXTENSIONS, analyze_video


def discover_videos(root: str | Path, *, max_videos: int = 500) -> list[Path]:
    source = Path(root).expanduser().resolve(strict=True)
    if source.is_file():
        candidates = [source] if source.suffix.lower() in VIDEO_EXTENSIONS else []
    elif source.is_dir():
        candidates = sorted(path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS)
    else:
        candidates = []
    if not candidates:
        raise ValueError("no_supported_video_files_found")
    return candidates[:max(1, int(max_videos))]


def _split_hashes(hashes: list[str]) -> tuple[set[str], set[str]]:
    ordered = sorted(set(hashes))
    if len(ordered) < 2:
        return set(ordered), set()
    validation_count = max(1, int(math.ceil(len(ordered) * 0.2)))
    validation = set(ordered[-validation_count:])
    training = set(ordered[:-validation_count])
    return training, validation


def train_corpus(
    input_root: str | Path,
    output_dir: str | Path,
    *,
    max_videos: int = 100,
    max_fps: float = 8.0,
    width: int = 160,
    height: int = 90,
    max_frames: int = 20_000,
    window_frames: int = 16,
    window_stride: int = 8,
    auto_promote: bool = False,
    rights_attested: bool = False,
    max_components: int = 24,
    max_prototypes: int = 12,
    max_windows_per_video: int = 64,
) -> dict[str, Any]:
    started = time.perf_counter()
    videos = discover_videos(input_root, max_videos=max_videos)
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicate_count = 0
    failures: list[dict[str, str]] = []
    for path in videos:
        try:
            digest = sha256_file(path)
            if digest in seen:
                duplicate_count += 1
                continue
            seen.add(digest)
            report = analyze_video(
                path,
                max_fps=max_fps,
                width=width,
                height=height,
                max_frames=max_frames,
                window_frames=window_frames,
                window_stride=window_stride,
                optical_flow=False,
            )
            all_windows = report.get("timeline", [])
            if len(all_windows) > max_windows_per_video:
                selected_indices = np.linspace(
                    0, len(all_windows) - 1, max_windows_per_video
                ).round().astype(int).tolist()
                selected_windows = [all_windows[index] for index in selected_indices]
            else:
                selected_windows = all_windows
            # Retain only feature vectors for training; discard regional graphs from memory.
            sampled_windows = [
                {
                    "window_index": int(window["window_index"]),
                    "signature_vector": window["signature_vector"],
                }
                for window in selected_windows
                if isinstance(window.get("signature_vector"), list)
            ]
            rows.append({
                "filename": path.name,
                "sha256": digest,
                "windows": sampled_windows,
                "total_windows": len(all_windows),
                "coverage_ratio": report["sampling"].get("timeline_coverage_ratio"),
                "frames_decoded": report["sampling"].get("frames_decoded"),
                "analysis_schema": report.get("schema_version"),
            })
        except KeyboardInterrupt:
        print(json.dumps({"status": "WATCH_STOPPED", "reason": "keyboard_interrupt"}), flush=True)
        return 0
    except (OSError, RuntimeError, ValueError, PermissionError) as exc:
            failures.append({"filename": path.name, "error": str(exc)[:500]})

    if not rows:
        raise RuntimeError("no_training_videos_analyzed_successfully")
    train_hashes, validation_hashes = _split_hashes([row["sha256"] for row in rows])
    train_examples: list[dict[str, Any]] = []
    validation_examples: list[dict[str, Any]] = []
    for row in rows:
        target = train_examples if row["sha256"] in train_hashes else validation_examples
        for window in row["windows"]:
            vector = window.get("signature_vector")
            if isinstance(vector, list):
                target.append({
                    "video_sha256": row["sha256"],
                    "window_index": int(window["window_index"]),
                    "vector": vector,
                })
    if len(train_examples) < 2:
        raise RuntimeError("training_corpus_produced_fewer_than_two_space_time_examples")

    model = fit_relational_model(
        train_examples,
        max_components=max_components,
        max_prototypes=max_prototypes,
    )
    model.pop("model_sha256", None)
    model["training_corpus_sha256"] = canonical_sha256(sorted(train_hashes))
    model["training_video_count"] = len(train_hashes)
    model["validation_video_count"] = len(validation_hashes)
    model["model_sha256"] = canonical_sha256(model)
    summary = validation_summary(model, validation_examples) if len(validation_examples) >= 2 else {
        "status": "NOT_AVAILABLE",
        "validation_example_count": len(validation_examples),
        "relative_quantization_improvement": None,
        "occupied_prototype_count": 0,
        "largest_cluster_fraction": None,
    }
    summary["validation_video_count"] = len(validation_hashes)
    train_coverage_ok = all(
        row["coverage_ratio"] is None or float(row["coverage_ratio"]) >= 0.95
        for row in rows if row["sha256"] in train_hashes
    )
    validation_coverage_ok = all(
        row["coverage_ratio"] is None or float(row["coverage_ratio"]) >= 0.95
        for row in rows if row["sha256"] in validation_hashes
    )
    model_diversity_ok = (
        int(summary.get("occupied_prototype_count") or 0) >= min(2, len(model["prototypes"]))
        and float(summary.get("largest_cluster_fraction") or 1.0) < 0.98
    )
    validation_gain = summary.get("relative_quantization_improvement")
    validation_gain_ok = validation_gain is not None and float(validation_gain) >= 0.05
    gates = {
        "minimum_distinct_videos": len(rows) >= 5,
        "minimum_training_videos": len(train_hashes) >= 4,
        "video_level_holdout_exists": len(validation_hashes) >= 1 and len(validation_examples) >= 2,
        "operator_attested_data_use_rights": bool(rights_attested),
        "training_timeline_coverage": bool(train_coverage_ok),
        "validation_timeline_coverage": bool(validation_coverage_ok),
        "heldout_prototype_improvement_at_least_5_percent": bool(validation_gain_ok),
        "heldout_cluster_diversity": bool(model_diversity_ok),
        "finite_model_parameters": all(
            math.isfinite(float(value))
            for key in ("normalizer_median", "normalizer_scale", "components", "component_scale", "prototypes", "prototype_radii_p95")
            for group in (model[key] if isinstance(model[key], list) else [model[key]])
            for value in (group if isinstance(group, list) else [group])
        ),
    }
    promotion_eligible = all(gates.values())
    candidate_path = write_json_atomic(output / "candidate_model.json", model)
    manifest = {
        "schema_version": "fma.training-manifest.v1",
        "rights_attestation": "operator_attests_rights_to_process_local_corpus" if rights_attested else "not_attested",
        "network_downloads_performed": False,
        "media_uploaded": False,
        "raw_media_committed_to_git": False,
        "sources": [
            {
                "filename": row["filename"],
                "sha256": row["sha256"],
                "analysis_schema": row["analysis_schema"],
                "frames_decoded": row["frames_decoded"],
                "window_count": row["total_windows"],
                "sampled_window_count": len(row["windows"]),
                "timeline_coverage_ratio": row["coverage_ratio"],
                "split": "train" if row["sha256"] in train_hashes else "validation",
            }
            for row in rows
        ],
        "failures": failures,
    }
    write_json_atomic(output / "dataset_manifest.json", manifest)
    promoted = False
    promotion_reason = "promotion_not_requested"
    if auto_promote:
        if promotion_eligible:
            write_json_atomic(output / "active_model.json", model)
            promoted = True
            promotion_reason = "all_video_level_holdout_and_rights_gates_passed"
        else:
            promotion_reason = "one_or_more_promotion_gates_failed"
    report = {
        "schema_version": "fma.training-report.v1",
        "status": "PROMOTED" if promoted else ("CANDIDATE_READY" if promotion_eligible else "CANDIDATE_NEEDS_EVIDENCE"),
        "model_schema": model["schema_version"],
        "model_sha256": model["model_sha256"],
        "candidate_model_path": str(candidate_path),
        "active_model_path": str((output / "active_model.json").resolve()) if promoted else None,
        "video_count_discovered": len(videos),
        "video_count_analyzed": len(rows),
        "duplicate_video_count_skipped": duplicate_count,
        "failed_videos": failures,
        "train_video_count": len(train_hashes),
        "validation_video_count": len(validation_hashes),
        "train_window_count": len(train_examples),
        "validation_window_count": len(validation_examples),
        "model_dimensions": model["input_dimensions"],
        "prototype_count": len(model["prototypes"]),
        "validation": summary,
        "promotion_gates": gates,
        "promotion_eligible": promotion_eligible,
        "promotion_attempted": bool(auto_promote),
        "promotion_result": "PROMOTED" if promoted else promotion_reason,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "honesty_contract": {
            "human_labels_used": False,
            "llm_required": False,
            "semantic_accuracy_established": False,
            "cross_domain_generalization_established": False,
            "promotion_is_not_semantic_validation": True,
        },
    }
    write_json_atomic(output / "training_report.json", report)
    return report



def corpus_inventory_fingerprint(input_root: str | Path, *, max_videos: int = 100) -> tuple[str, int]:
    """Fast local inventory checkpoint. SHA-256 of file contents is still verified during training."""
    source = Path(input_root).expanduser().resolve(strict=True)
    videos = discover_videos(source, max_videos=max_videos)
    items: list[dict[str, Any]] = []
    for path in videos:
        stat = path.stat()
        relative = path.name if source.is_file() else path.relative_to(source).as_posix()
        items.append({
            "relative_path": relative,
            "size_bytes": int(stat.st_size),
            "mtime_ns": int(stat.st_mtime_ns),
        })
    items.sort(key=lambda item: item["relative_path"])
    return canonical_sha256(items), len(items)


def watch_corpus(
    input_root: str | Path,
    output_dir: str | Path,
    *,
    poll_interval_s: int = 900,
    retry_interval_s: int = 21600,
    max_cycles: int | None = None,
    **training_options: Any,
) -> dict[str, Any]:
    """Watch a local corpus and retrain on inventory changes with durable idempotent checkpoints.

    This foreground loop only processes local files. It never downloads data or starts
    background work detached from the caller. Failed/gated attempts are retried no more
    often than retry_interval_s for an unchanged corpus.
    """
    import time as _time

    poll_interval_s = max(30, min(86400, int(poll_interval_s)))
    retry_interval_s = max(poll_interval_s, min(7 * 86400, int(retry_interval_s)))
    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "watch_state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("schema_version") != "fma.training-watch-state.v1":
            state = {}
    except (OSError, ValueError, json.JSONDecodeError):
        state = {}
    state.setdefault("history", [])
    cycle = 0
    last_result: dict[str, Any] = {"status": "WATCHING", "state_path": str(state_path)}

    while True:
        cycle += 1
        now = _time.time()
        try:
            inventory_sha, inventory_count = corpus_inventory_fingerprint(
                input_root, max_videos=int(training_options.get("max_videos", 100))
            )
        except (OSError, RuntimeError, ValueError, PermissionError) as exc:
            last_result = {"status": "INVENTORY_ERROR", "error": str(exc)[:500]}
            state.update({
                "schema_version": "fma.training-watch-state.v1",
                "last_check_unix_s": int(now),
                "last_error": str(exc)[:500],
            })
            write_json_atomic(state_path, state)
            print(json.dumps(last_result, ensure_ascii=False), flush=True)
            if max_cycles is not None and cycle >= max_cycles:
                return last_result
            _time.sleep(poll_interval_s)
            continue

        previous_inventory = state.get("last_attempt_inventory_sha256")
        last_attempt = float(state.get("last_attempt_unix_s") or 0)
        previous_status = str(state.get("last_result_status") or "")
        should_run = (
            previous_inventory != inventory_sha
            or not previous_inventory
            or (
                previous_status not in {"PROMOTED", "CANDIDATE_READY"}
                and now - last_attempt >= retry_interval_s
            )
        )
        state.update({
            "schema_version": "fma.training-watch-state.v1",
            "last_check_unix_s": int(now),
            "current_inventory_sha256": inventory_sha,
            "current_inventory_count": inventory_count,
            "poll_interval_s": poll_interval_s,
            "retry_interval_s": retry_interval_s,
        })

        if should_run:
            try:
                report = train_corpus(input_root, output, **training_options)
                last_result = {
                    "status": report["status"],
                    "inventory_sha256": inventory_sha,
                    "model_sha256": report.get("model_sha256"),
                    "promotion_eligible": report.get("promotion_eligible"),
                    "training_report_path": str((output / "training_report.json").resolve()),
                }
                last_error = None
            except (OSError, RuntimeError, ValueError, PermissionError) as exc:
                last_result = {
                    "status": "ERROR",
                    "inventory_sha256": inventory_sha,
                    "error": str(exc)[:500],
                }
                last_error = str(exc)[:500]
            state["last_attempt_inventory_sha256"] = inventory_sha
            state["last_attempt_unix_s"] = int(_time.time())
            state["last_result_status"] = str(last_result.get("status"))
            state["last_result_model_sha256"] = last_result.get("model_sha256")
            state["last_error"] = last_error
            history = list(state.get("history", []))
            history.append({
                "attempt_unix_s": state["last_attempt_unix_s"],
                "inventory_sha256": inventory_sha,
                "status": last_result.get("status"),
                "model_sha256": last_result.get("model_sha256"),
                "error": last_error,
            })
            state["history"] = history[-30:]
        else:
            last_result = {
                "status": "UNCHANGED_SKIPPED",
                "inventory_sha256": inventory_sha,
                "video_count": inventory_count,
                "next_retry_after_s": max(0, retry_interval_s - int(now - last_attempt))
                if previous_status not in {"PROMOTED", "CANDIDATE_READY"} else None,
            }
        write_json_atomic(state_path, state)
        print(json.dumps(last_result, ensure_ascii=False), flush=True)
        if max_cycles is not None and cycle >= max_cycles:
            return last_result
        _time.sleep(poll_interval_s)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="motionlab-train", description="Train an unlabeled open-world relational model from local videos.")
    parser.add_argument("input", help="A video file or local directory of videos")
    parser.add_argument("--output-dir", default="reports/openworld-training")
    parser.add_argument("--max-videos", type=int, default=100)
    parser.add_argument("--max-fps", type=float, default=8.0)
    parser.add_argument("--width", type=int, default=160)
    parser.add_argument("--height", type=int, default=90)
    parser.add_argument("--max-frames", type=int, default=20_000)
    parser.add_argument("--window-frames", type=int, default=16)
    parser.add_argument("--window-stride", type=int, default=8)
    parser.add_argument("--max-components", type=int, default=24)
    parser.add_argument("--max-prototypes", type=int, default=12)
    parser.add_argument("--max-windows-per-video", type=int, default=64, help="Deterministically sample at most this many temporal windows from each source video.")
    parser.add_argument("--auto-promote", action="store_true", help="Promote candidate only if all held-out and rights gates pass")
    parser.add_argument("--attest-rights", action="store_true", help="Attest that you have permission to process every video in this local corpus")
    parser.add_argument("--watch", action="store_true", help="Stay in the foreground and retrain after the local corpus changes.")
    parser.add_argument("--poll-seconds", type=int, default=900)
    parser.add_argument("--retry-seconds", type=int, default=21600)
    args = parser.parse_args(argv)
    try:
        options = dict(
            args.input, args.output_dir,
            max_videos=args.max_videos,
            max_fps=args.max_fps,
            width=args.width,
            height=args.height,
            max_frames=args.max_frames,
            window_frames=args.window_frames,
            window_stride=args.window_stride,
            auto_promote=args.auto_promote,
            rights_attested=args.attest_rights,
            max_components=args.max_components,
            max_prototypes=args.max_prototypes,
            max_windows_per_video=args.max_windows_per_video,
        )
        if args.watch:
            watch_corpus(
                args.input, args.output_dir,
                poll_interval_s=args.poll_seconds,
                retry_interval_s=args.retry_seconds,
                **options,
            )
            return 0
        report = train_corpus(args.input, args.output_dir, **options)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["status"] != "CANDIDATE_NEEDS_EVIDENCE" else 3
    except (OSError, RuntimeError, ValueError, PermissionError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

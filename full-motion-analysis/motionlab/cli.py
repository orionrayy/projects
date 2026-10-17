"""Command-line entry point for motion analysis and render QC."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .analysis import analyze_video
from .audit import audit_video
from .media import probe_media


def _write_or_print(data: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    if output:
        destination = Path(output).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(rendered + "\n", encoding="utf-8")
        temporary.replace(destination)
        print(json.dumps({"report_path": str(destination), "schema_version": data.get("schema_version"), "status": data.get("status", "COMPLETED")}))
    else:
        print(rendered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="motionlab", description="Open-world multiscale spatiotemporal analysis, corpus training, and FFmpeg video audit.")
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="Read FFprobe metadata.")
    probe.add_argument("video")

    analyze = sub.add_parser("analyze", help="Analyze overlapping spatiotemporal blocks, multiscale signatures, and relational structure.")
    analyze.add_argument("video")
    analyze.add_argument("--output")
    analyze.add_argument("--max-fps", type=float, default=30.0)
    analyze.add_argument("--width", type=int, default=160)
    analyze.add_argument("--height", type=int, default=90)
    analyze.add_argument("--max-frames", type=int, default=100_000)
    analyze.add_argument("--no-optical-flow", action="store_true", help="Compatibility flag; v0.2 core does not use pairwise optical flow.")
    analyze.add_argument("--window-frames", type=int, default=16)
    analyze.add_argument("--window-stride", type=int, default=8)
    analyze.add_argument("--model", help="Optional local relational model JSON for anonymous prototype/novelty scoring.")

    audit = sub.add_parser("audit", help="Run FFmpeg render quality checks.")
    audit.add_argument("video")
    audit.add_argument("--output")
    audit.add_argument("--expected-width", type=int)
    audit.add_argument("--expected-height", type=int)
    audit.add_argument("--expected-fps", type=float)
    audit.add_argument("--expected-duration", type=float)
    audit.add_argument("--require-audio", action="store_true")
    audit.add_argument("--max-fps", type=float, default=30.0)
    audit.add_argument("--max-frames", type=int, default=100_000)
    train = sub.add_parser("train", help="Train an unlabeled relational model from a local video corpus.")
    train.add_argument("input", help="Video file or directory; media stays local.")
    train.add_argument("--output-dir", default="reports/openworld-training")
    train.add_argument("--max-videos", type=int, default=500)
    train.add_argument("--max-fps", type=float, default=8.0)
    train.add_argument("--width", type=int, default=160)
    train.add_argument("--height", type=int, default=90)
    train.add_argument("--max-frames", type=int, default=20000)
    train.add_argument("--window-frames", type=int, default=16)
    train.add_argument("--window-stride", type=int, default=8)
    train.add_argument("--auto-promote", action="store_true")
    train.add_argument("--attest-rights", action="store_true", help="Attest you can lawfully process all local corpus videos.")
    train.add_argument("--watch", action="store_true", help="Keep this process running; retrain when the local corpus inventory changes.")
    train.add_argument("--poll-seconds", type=int, default=900)
    train.add_argument("--retry-seconds", type=int, default=21600)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "train":
            from .train import train_corpus, watch_corpus
            options = dict(
                max_videos=args.max_videos,
                max_fps=args.max_fps, width=args.width, height=args.height,
                max_frames=args.max_frames, window_frames=args.window_frames,
                window_stride=args.window_stride, auto_promote=args.auto_promote,
                rights_attested=args.attest_rights,
            )
            _write_or_print(result, None)
            return 0 if result["status"] != "CANDIDATE_NEEDS_EVIDENCE" else 3
        if args.command == "probe":
            result = probe_media(args.video)
        elif args.command == "analyze":
            result = analyze_video(
                args.video, max_fps=args.max_fps, width=args.width, height=args.height,
                max_frames=args.max_frames, optical_flow=not args.no_optical_flow,
                window_frames=args.window_frames, window_stride=args.window_stride,
                model_path=args.model,
            )
            _write_or_print(result, args.output)
            return 0
        else:
            result = audit_video(
                args.video, expected_width=args.expected_width, expected_height=args.expected_height,
                expected_fps=args.expected_fps, expected_duration_s=args.expected_duration,
                require_audio=args.require_audio, max_fps=args.max_fps, max_frames=args.max_frames,
            )
            _write_or_print(result, args.output)
            return 0 if result["status"] != "FAIL" else 2
        _write_or_print(result, None)
        return 0
    except KeyboardInterrupt:
        print(json.dumps({"status": "WATCH_STOPPED", "reason": "keyboard_interrupt"}), flush=True)
        return 0
    except (OSError, RuntimeError, ValueError, PermissionError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

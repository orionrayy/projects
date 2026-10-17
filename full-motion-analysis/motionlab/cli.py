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
    parser = argparse.ArgumentParser(prog="motionlab", description="Evidence-grounded motion analysis and FFmpeg video audit.")
    sub = parser.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="Read FFprobe metadata.")
    probe.add_argument("video")

    analyze = sub.add_parser("analyze", help="Measure frame-to-frame motion and temporal event candidates.")
    analyze.add_argument("video")
    analyze.add_argument("--output")
    analyze.add_argument("--max-fps", type=float, default=30.0)
    analyze.add_argument("--width", type=int, default=320)
    analyze.add_argument("--height", type=int, default=180)
    analyze.add_argument("--max-frames", type=int, default=100_000)
    analyze.add_argument("--no-optical-flow", action="store_true")

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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "probe":
            result = probe_media(args.video)
        elif args.command == "analyze":
            result = analyze_video(
                args.video, max_fps=args.max_fps, width=args.width, height=args.height,
                max_frames=args.max_frames, optical_flow=not args.no_optical_flow,
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
    except (OSError, RuntimeError, ValueError, PermissionError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Local MCP server. Runs over stdio by default; never expose publicly without a secure gateway."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP as MCPServerClass
except ImportError:
    try:
        # MCP SDK v2 renamed FastMCP to MCPServer; retain v1 compatibility.
        from mcp.server.mcpserver import MCPServer as MCPServerClass
    except ImportError as exc:
        print('Install MCP support with: python -m pip install -e ".[mcp]"', file=sys.stderr)
        raise SystemExit(2) from exc

from motionlab.analysis import analyze_video
from motionlab.audit import audit_video
from motionlab.media import probe_media
from motionlab.security import resolve_allowed_video_path

mcp = MCPServerClass(
    "motion-evidence-lab",
    instructions=(
        "Analyze local video using timestamped frame-change and optional dense optical-flow evidence. "
        "Report candidate events and limitations. Do not assert physical-world speed or causality. "
        "Only read video files inside MOTION_ALLOWED_ROOTS."
    ),
)


def _save_report(data: dict[str, Any], prefix: str) -> str:
    report_dir = Path(os.environ.get(
        "MOTION_REPORT_DIR", str(Path.home() / ".motion-evidence-lab" / "reports")
    )).expanduser().resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    file_hash = data.get("input", {}).get("sha256", "no-input-hash")
    target = report_dir / f"{prefix}-{file_hash[:16]}.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(target)
    return str(target)


@mcp.tool()
def inspect_video_metadata(video_path: str) -> dict[str, Any]:
    """Read codec, dimensions, duration, source FPS, and audio stream presence for an allowed local video path."""
    target = resolve_allowed_video_path(video_path)
    return probe_media(target)


@mcp.tool()
def analyze_local_video(
    video_path: str,
    max_fps: float = 30.0,
    optical_flow: bool = True,
    max_frames: int = 100000,
) -> dict[str, Any]:
    """Measure temporal image motion, dense flow when available, and timestamped event candidates. Saves a complete JSON report."""
    target = resolve_allowed_video_path(video_path)
    report = analyze_video(
        target, max_fps=max_fps, optical_flow=optical_flow, max_frames=max_frames
    )
    report_path = _save_report(report, "analysis")
    return {
        "status": "COMPLETED",
        "report_path": report_path,
        "input": report["input"],
        "media": report["media"],
        "sampling": report["sampling"],
        "measurements": report["measurements"],
        "events": report["events"],
        "event_counts": report["event_counts"],
        "provenance": report["provenance"],
        "interpretation_limits": report["interpretation_limits"],
    }


@mcp.tool()
def audit_ffmpeg_render(
    video_path: str,
    expected_width: int = 1920,
    expected_height: int = 1080,
    expected_fps: float = 24.0,
    expected_duration_s: float | None = None,
    require_audio: bool = False,
    max_fps: float = 30.0,
) -> dict[str, Any]:
    """Audit a local FFmpeg render against media, sampling, duplicate/freeze, black-frame, and optional audio expectations."""
    target = resolve_allowed_video_path(video_path)
    report = audit_video(
        target, expected_width=expected_width, expected_height=expected_height,
        expected_fps=expected_fps, expected_duration_s=expected_duration_s,
        require_audio=require_audio, max_fps=max_fps,
    )
    report_path = _save_report(report, "audit")
    return {
        "status": report["status"],
        "release_gate_passed": report["release_gate_passed"],
        "report_path": report_path,
        "input": report["input"],
        "media": report["media"],
        "qc": report["qc"],
        "event_counts": report["analysis"]["event_counts"],
        "events": report["analysis"]["events"],
        "limits": report["limits"],
    }


if __name__ == "__main__":
    transport = os.environ.get("MOTION_MCP_TRANSPORT", "stdio")
    if transport not in {"stdio", "streamable-http"}:
        raise SystemExit("MOTION_MCP_TRANSPORT must be stdio or streamable-http")
    mcp.run(transport=transport)

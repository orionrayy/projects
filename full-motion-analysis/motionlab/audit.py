"""Release-oriented QC checks for rendered videos; semantic quality is out of scope."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .analysis import analyze_video
from .media import probe_media


def audit_video(
    path: str | Path,
    *,
    expected_width: int | None = None,
    expected_height: int | None = None,
    expected_fps: float | None = None,
    expected_duration_s: float | None = None,
    require_audio: bool = False,
    max_fps: float = 30.0,
    max_frames: int = 100_000,
) -> dict[str, Any]:
    media = probe_media(path)
    analysis = analyze_video(
        path,
        max_fps=max_fps,
        width=320,
        height=180,
        max_frames=max_frames,
        optical_flow=False,
    )
    findings: list[dict[str, Any]] = []

    def finding(severity: str, code: str, message: str, observed: Any = None, expected: Any = None) -> None:
        findings.append({
            "severity": severity,
            "code": code,
            "message": message,
            "observed": observed,
            "expected": expected,
        })

    if expected_width is not None and media["width"] != expected_width:
        finding("error", "FMA-QC-RESOLUTION", "Video width does not match expected output.", media["width"], expected_width)
    if expected_height is not None and media["height"] != expected_height:
        finding("error", "FMA-QC-RESOLUTION", "Video height does not match expected output.", media["height"], expected_height)
    if expected_fps is not None:
        actual_fps = media.get("source_fps")
        if actual_fps is None or abs(float(actual_fps) - float(expected_fps)) > 0.15:
            finding("error", "FMA-QC-FPS", "Reported frame rate does not match expected output.", actual_fps, expected_fps)
    if expected_duration_s is not None:
        actual_duration = media.get("duration_s")
        tolerance = max(0.15, float(expected_duration_s) * 0.01)
        if actual_duration is None or abs(float(actual_duration) - float(expected_duration_s)) > tolerance:
            finding("error", "FMA-QC-DURATION", "Container/video duration is outside tolerance.", actual_duration, expected_duration_s)

    if analysis["sampling"]["truncated_by_frame_limit"]:
        finding(
            "error", "FMA-QC-INCOMPLETE-DECODE",
            "Analysis stopped at its frame limit before covering the estimated timeline.",
            analysis["sampling"]["frames_decoded"],
            analysis["sampling"]["estimated_source_frames_at_analysis_rate"],
        )
    coverage = analysis["sampling"]["timeline_coverage_ratio"]
    if coverage is not None and coverage < 0.98:
        finding("warning", "FMA-QC-COVERAGE", "Decoded frame coverage is below 98% of the reported duration.", coverage, 0.98)

    duplicate_ratio = analysis["measurements"]["exact_duplicate_transition_ratio"]
    if duplicate_ratio >= 0.25:
        finding(
            "warning", "FMA-QC-REPEATED-FRAMES",
            "At least 25% of analyzed transitions decode to exactly repeated frames; check for freezes or intentional holds.",
            duplicate_ratio, "< 0.25 advisory threshold",
        )

    black_ratio = analysis["measurements"]["near_black_frame_ratio"]
    if black_ratio >= 0.20:
        finding(
            "warning", "FMA-QC-NEAR-BLACK",
            "At least 20% of analyzed frames are near-black; this can be intentional and requires context review.",
            black_ratio, "< 0.20 advisory threshold",
        )

    if require_audio and not media["audio_present"]:
        finding("error", "FMA-QC-AUDIO-MISSING", "Audio is required but no audio stream exists.", False, True)
    elif not media["audio_present"]:
        finding("warning", "FMA-QC-SILENT-OUTPUT", "No audio stream is present; this is only an error when the delivery contract requires audio.", False, "configurable")

    for event in analysis["events"]:
        if event["event_type"] == "repeated_frame_run_candidate":
            finding(
                "warning", "FMA-QC-FREEZE-CANDIDATE",
                "A run of identical decoded frames was detected. Inspect the timestamped evidence before deciding whether it is a defect.",
                {"start_s": event["timestamp_s"], "end_s": event["end_timestamp_s"],
                 "duration_s": event["measurement"]["duration_s"]},
                "scene-dependent",
            )
        elif event["event_type"] == "possible_flash_candidate":
            finding(
                "warning", "FMA-QC-FLASH-CANDIDATE",
                "A short high-change excursion resembles a flash; review the cited interval.",
                {"start_s": event["timestamp_s"], "end_s": event["end_timestamp_s"]},
                "scene-dependent",
            )

    errors = sum(f["severity"] == "error" for f in findings)
    warnings = sum(f["severity"] == "warning" for f in findings)
    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {
        "schema_version": "fma.audit.v0.1",
        "status": status,
        "release_gate_passed": status == "PASS",
        "summary": {"error_count": errors, "warning_count": warnings, "finding_count": len(findings)},
        "input": analysis["input"],
        "media": media,
        "qc": {
            "expected": {
                "width": expected_width, "height": expected_height,
                "fps": expected_fps, "duration_s": expected_duration_s,
                "require_audio": bool(require_audio),
            },
            "actual": {
                "width": media["width"], "height": media["height"],
                "fps": media["source_fps"], "duration_s": media["duration_s"],
                "audio_present": media["audio_present"],
            },
            "duplicate_transition_ratio": duplicate_ratio,
            "near_black_frame_ratio": black_ratio,
            "findings": findings,
        },
        "analysis": analysis,
        "limits": [
            "A QC pass covers only the configured technical checks; it does not certify aesthetics, story clarity, educational correctness, animation quality, natural speech, or causal motion interpretation.",
            "Exact repeated frames and dark frames can be intentional. Review finding timestamps in their scene context.",
            "The default analysis runs at a capped frame rate. Inspect the sampling contract before auditing fast motion.",
        ],
    }

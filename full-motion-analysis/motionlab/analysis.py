"""Public FMA entry point. The open-world relational engine is the default in v0.2."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .legacy_analysis import detect_event_candidates
from .relational import analyze_video as _analyze_relational


def analyze_video(
    path: str | Path,
    *,
    max_fps: float = 30.0,
    width: int = 320,
    height: int = 180,
    max_frames: int = 100_000,
    optical_flow: bool = False,
    window_frames: int = 16,
    window_stride: int = 8,
    model_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run v0.2 open-world space-time analysis.

    optical_flow remains accepted to avoid breaking callers but is not used by the
    primary engine. The v0.1 frame-pair implementation remains isolated in legacy_analysis.
    """
    return _analyze_relational(
        path,
        max_fps=max_fps,
        width=width,
        height=height,
        max_frames=max_frames,
        optical_flow=optical_flow,
        window_frames=window_frames,
        window_stride=window_stride,
        model_path=model_path,
    )

"""Deterministic synthetic grayscale video fixtures with known motion intervals."""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

from .media import require_tool


def _gray_frame(index: int, frames: int, width: int, height: int, fps: int, scenario: str) -> np.ndarray:
    frame = np.full((height, width), 16, dtype=np.uint8)
    box = 32
    max_x = width - box - 8
    if scenario == "move_reverse":
        midpoint = max(1, frames // 2)
        if index <= midpoint:
            x = 8 + int((max_x - 8) * index / midpoint)
        else:
            x = 8 + int((max_x - 8) * (frames - index) / max(1, frames - midpoint))
        frame[height // 2 - box // 2:height // 2 + box // 2, x:x + box] = 220
    elif scenario == "freeze":
        moving_frames = max(2, int(fps * 0.5))
        x = 8 + int((max_x - 8) * min(index, moving_frames) / moving_frames)
        frame[height // 2 - box // 2:height // 2 + box // 2, x:x + box] = 220
    elif scenario == "flash":
        frame[height // 2 - box // 2:height // 2 + box // 2, width // 3:width // 3 + box] = 220
        if index == max(1, fps // 2):
            frame[:, :] = 245
    elif scenario == "static":
        frame[height // 2 - box // 2:height // 2 + box // 2, width // 3:width // 3 + box] = 220
    else:
        raise ValueError(f"unknown_synthetic_scenario:{scenario}")
    return frame


def generate_synthetic_clip(
    output_path: str | Path,
    *,
    scenario: str,
    duration_s: float = 3.0,
    fps: int = 30,
    width: int = 320,
    height: int = 180,
) -> Path:
    if duration_s <= 0 or fps < 1 or width < 64 or height < 64 or width % 2 or height % 2:
        raise ValueError("invalid_synthetic_video_dimensions_or_rate")
    frame_count = int(round(duration_s * fps))
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        require_tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-f", "rawvideo", "-pixel_format", "gray", "-video_size", f"{width}x{height}",
        "-framerate", str(fps), "-i", "pipe:0", "-frames:v", str(frame_count),
        "-c:v", "ffv1", "-pix_fmt", "gray", str(output),
    ]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(frame_count):
            proc.stdin.write(_gray_frame(i, frame_count, width, height, fps, scenario).tobytes())
        proc.stdin.close()
        _, stderr = proc.communicate(timeout=60)
    except BaseException:
        proc.kill()
        proc.communicate()
        raise
    if proc.returncode != 0:
        message = (stderr or b"").decode("utf-8", errors="replace").strip()[:1000]
        raise RuntimeError(f"synthetic_ffmpeg_encode_failed:{message}")
    return output

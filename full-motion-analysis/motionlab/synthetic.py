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
    elif scenario == "global_pan_reverse":
        # Deterministic, textured entire-scene translation with an exact direction reversal.
        rng = np.random.default_rng(7411)
        yy, xx = np.mgrid[0:height, 0:width]
        noise = rng.normal(0.0, 8.0, size=(height, width))
        base = np.clip(
            128 + 38 * np.sin(xx / 7.0) + 32 * np.cos(yy / 9.0) + noise,
            0, 255,
        ).astype(np.uint8)
        midpoint = max(1, frames // 2)
        shift = round(index * 1.5) if index <= midpoint else round(midpoint * 1.5 - (index - midpoint) * 1.5)
        frame = np.roll(base, shift, axis=1)
    elif scenario == "pan_plus_object":
        # Textured background pans right; a high-contrast object independently moves right faster.
        rng = np.random.default_rng(7411)
        yy, xx = np.mgrid[0:height, 0:width]
        noise = rng.normal(0.0, 8.0, size=(height, width))
        base = np.clip(128 + 38 * np.sin(xx / 7.0) + 32 * np.cos(yy / 9.0) + noise, 0, 255).astype(np.uint8)
        camera_shift = round(index * 1.0)
        frame = np.roll(base, camera_shift, axis=1)
        object_box = 30
        object_x = 24 + int((width - object_box - 48) * index / max(1, frames - 1))
        object_x = min(width - object_box - 4, max(4, object_x))
        object_y = height // 2 - object_box // 2
        patch_y, patch_x = np.mgrid[0:object_box, 0:object_box]
        patch = np.where(((patch_x // 3 + patch_y // 3) % 2) == 0, 245, 185).astype(np.uint8)
        frame[object_y:object_y + object_box, object_x:object_x + object_box] = patch
    elif scenario == "abstract_nirmana":
        # Domain-free geometric composition: rotation, bands, rings and interference patterns.
        yy, xx = np.mgrid[0:height, 0:width]
        x = (xx.astype(np.float64) - width / 2.0) / max(1.0, width / 2.0)
        y = (yy.astype(np.float64) - height / 2.0) / max(1.0, height / 2.0)
        phase = 2.0 * np.pi * index / max(1, frames - 1)
        angle = 0.7 * np.sin(phase * 0.5)
        u = np.cos(angle) * x - np.sin(angle) * y
        v = np.sin(angle) * x + np.cos(angle) * y
        radius = np.sqrt(u * u + v * v)
        rings = np.sin(24.0 * radius - phase * 1.4)
        interference = np.sin(11.0 * u + 2.0 * np.sin(7.0 * v + phase))
        cross_bands = np.sin(8.0 * (u + v) - phase) * np.cos(6.0 * (u - v) + phase * 0.7)
        composition = 128.0 + 44.0 * rings + 43.0 * interference + 28.0 * cross_bands
        frame = np.clip(composition, 0, 255).astype(np.uint8)
    elif scenario == "fractal_zoom":
        # Procedural Mandelbrot zoom; no object semantics or labels are used by FMA.
        yy, xx = np.mgrid[0:height, 0:width]
        progress = index / max(1, frames - 1)
        zoom = 1.0 + 99.0 * (progress ** 1.2)
        scale = 3.6 / (width * zoom)
        cx, cy = -0.743643887037151, 0.131825904205330
        real = cx + (xx.astype(np.float64) - width / 2.0) * scale
        imag = cy + (yy.astype(np.float64) - height / 2.0) * scale
        cvalue = real + 1j * imag
        z = np.zeros_like(cvalue)
        escaped_at = np.full((height, width), 40, dtype=np.float32)
        active = np.ones((height, width), dtype=bool)
        for iteration in range(40):
            z[active] = z[active] * z[active] + cvalue[active]
            escaped = active & ((z.real * z.real + z.imag * z.imag) > 4.0)
            escaped_at[escaped] = iteration + 1
            active[escaped] = False
            if not np.any(active):
                break
        smooth = np.sqrt(np.clip(escaped_at / 40.0, 0.0, 1.0))
        fine = np.sin(escaped_at * 0.75 + np.log1p(zoom) * 5.0) * 12.0
        frame = np.clip(20.0 + 220.0 * smooth + fine, 0, 255).astype(np.uint8)
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
        require_tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "gray", "-video_size", f"{width}x{height}",
        "-framerate", str(fps), "-i", "pipe:0", "-frames:v", str(frame_count),
        "-c:v", "ffv1", "-pix_fmt", "gray", str(output),
    ]
    proc = subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )
    assert proc.stdin is not None
    try:
        for i in range(frame_count):
            proc.stdin.write(_gray_frame(i, frame_count, width, height, fps, scenario).tobytes())
        proc.stdin.close()
        proc.wait(timeout=60)
        stderr = proc.stderr.read() if proc.stderr is not None else b""
        if proc.stderr is not None:
            proc.stderr.close()
    except BaseException:
        proc.kill()
        proc.wait()
        if proc.stderr is not None:
            proc.stderr.read()
            proc.stderr.close()
        raise
    if proc.returncode != 0:
        message = (stderr or b"").decode("utf-8", errors="replace").strip()[:1000]
        raise RuntimeError(f"synthetic_ffmpeg_encode_failed:{message}")
    return output

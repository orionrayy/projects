"""Bounded FFmpeg/FFprobe media intake."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Iterator

import numpy as np


def require_tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"required_tool_not_found_on_PATH:{name}")
    return found


def tool_version(name: str) -> str | None:
    try:
        proc = subprocess.run([require_tool(name), "-version"], capture_output=True, text=True, timeout=10, check=False)
        first = (proc.stdout or proc.stderr).splitlines()
        return first[0].strip() if first else None
    except (OSError, RuntimeError, subprocess.TimeoutExpired):
        return None


def _parse_rate(value: object) -> float | None:
    if not isinstance(value, str) or not value or value == "0/0":
        return None
    try:
        rate = float(Fraction(value)) if "/" in value else float(value)
        return rate if rate > 0 else None
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def probe_media(path: str | Path) -> dict:
    source = Path(path).expanduser().resolve(strict=True)
    if not source.is_file():
        raise ValueError("input_path_must_be_a_file")
    proc = subprocess.run(
        [require_tool("ffprobe"), "-v", "error", "-show_streams", "-show_format", "-of", "json", str(source)],
        capture_output=True, text=True, timeout=60, check=False,
    )
    if proc.returncode != 0:
        message = (proc.stderr or "ffprobe_failed").strip()[:1500]
        raise RuntimeError(f"ffprobe_failed:{message}")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("ffprobe_returned_invalid_json") from exc
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not video:
        raise ValueError("no_video_stream_found")
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    fmt = data.get("format", {})
    duration = video.get("duration", fmt.get("duration"))
    try:
        duration_f = float(duration) if duration is not None else None
        if duration_f is not None and (duration_f <= 0 or not np.isfinite(duration_f)):
            duration_f = None
    except (TypeError, ValueError, OverflowError):
        duration_f = None
    fps = _parse_rate(video.get("avg_frame_rate")) or _parse_rate(video.get("r_frame_rate"))
    try:
        source_frames = int(video.get("nb_frames")) if video.get("nb_frames") not in (None, "N/A") else None
    except (TypeError, ValueError):
        source_frames = None
    return {
        "filename": source.name, "format_name": fmt.get("format_name"),
        "container_duration_s": duration_f, "duration_s": duration_f,
        "video_codec": video.get("codec_name"), "pixel_format": video.get("pix_fmt"),
        "width": int(video.get("width") or 0), "height": int(video.get("height") or 0),
        "source_fps": fps, "source_frame_count": source_frames,
        "audio_stream_count": len(audio_streams), "audio_present": bool(audio_streams),
        "audio_codecs": [s.get("codec_name") for s in audio_streams],
    }


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def iter_gray_frames(path: str | Path, *, fps: float, width: int, height: int, max_frames: int) -> Iterator[tuple[int, np.ndarray]]:
    """Yield timestamp-ordered fixed-size grayscale frames with bounded buffering."""
    if fps <= 0 or width <= 0 or height <= 0 or max_frames <= 0:
        raise ValueError("fps_dimensions_and_max_frames_must_be_positive")
    if width % 2 or height % 2:
        raise ValueError("analysis_dimensions_must_be_even")
    source = Path(path).expanduser().resolve(strict=True)
    vf = f"fps={fps:.8f},scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=gray"
    command = [
        require_tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-nostdin",
        "-i", str(source), "-map", "0:v:0", "-vf", vf, "-an", "-sn", "-dn",
        "-threads", "1", "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    frame_bytes = width * height
    index = 0
    cap_reached = False
    failure: Exception | None = None
    stderr = b""
    try:
        assert process.stdout is not None
        while index < max_frames:
            chunk = process.stdout.read(frame_bytes)
            if not chunk:
                break
            if len(chunk) != frame_bytes:
                failure = RuntimeError(f"truncated_raw_frame:index={index}:bytes={len(chunk)}:expected={frame_bytes}")
                break
            yield index, np.frombuffer(chunk, dtype=np.uint8).reshape(height, width).copy()
            index += 1
        if index >= max_frames:
            cap_reached = True
    finally:
        if (cap_reached or failure is not None) and process.poll() is None:
            process.terminate()
        try:
            _, stderr = process.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            _, stderr = process.communicate(timeout=5)
            failure = failure or RuntimeError("ffmpeg_decode_timeout_after_termination")
        finally:
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
        if not cap_reached and process.returncode not in (0, None):
            message = (stderr or b"").decode("utf-8", errors="replace").strip()[:1500]
            failure = failure or RuntimeError(f"ffmpeg_decode_failed:{message}")
        if failure:
            raise failure

#!/usr/bin/env bash
# Deterministic codec/filter smoke tests for FFmpeg Motion Studio's render profile.
set -Eeuo pipefail

BIN_DIR="${1:-}"
OUT_DIR="${2:-}"
if [[ -z "$BIN_DIR" || -z "$OUT_DIR" ]]; then
  echo "Usage: $0 <ffmpeg-bin-dir> <output-dir>" >&2
  exit 2
fi
FFMPEG="$BIN_DIR/ffmpeg"
FFPROBE="$BIN_DIR/ffprobe"
mkdir -p "$OUT_DIR"
WORK="$OUT_DIR/work"
mkdir -p "$WORK"

"$FFMPEG" -version | tee "$OUT_DIR/ffmpeg-version.txt"
"$FFPROBE" -version | tee "$OUT_DIR/ffprobe-version.txt"
grep -Fq "ffmpeg version 9.0.2" "$OUT_DIR/ffmpeg-version.txt"
grep -Fq "ffprobe version 9.0.2" "$OUT_DIR/ffprobe-version.txt"

"$FFMPEG" -hide_banner -encoders > "$OUT_DIR/encoders.txt"
"$FFMPEG" -hide_banner -filters > "$OUT_DIR/filters.txt"
for encoder in libx264 libx265 libmp3lame libopus libvpx-vp9 libaom-av1; do
  if ! grep -Eq "[[:space:]]${encoder}[[:space:]]" "$OUT_DIR/encoders.txt"; then
    echo "Required encoder missing: $encoder" >&2
    exit 1
  fi
done
for filter in drawtext subtitles loudnorm xfade acrossfade zscale; do
  if ! grep -Eq "[[:space:]]${filter}[[:space:]]" "$OUT_DIR/filters.txt"; then
    echo "Required filter missing: $filter" >&2
    exit 1
  fi
done

FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
test -s "$FONT"
"$FFMPEG" -hide_banner -y -benchmark \
  -f lavfi -i "testsrc2=size=320x180:rate=24:duration=2" \
  -f lavfi -i "sine=frequency=997:sample_rate=48000:duration=2" \
  -vf "drawtext=fontfile=$FONT:text='FFmpeg 9.0.2':fontcolor=white:fontsize=18:x=10:y=10,format=yuv420p" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v libx264 -preset ultrafast -crf 28 -c:a aac -b:a 128k -shortest \
  -movflags +faststart "$WORK/av-smoke.mp4" 2>&1 | tee "$OUT_DIR/av-benchmark.log"

printf '1\n00:00:00,000 --> 00:00:01,500\nSubtitle render regression\n' > "$WORK/captions.srt"
"$FFMPEG" -hide_banner -y \
  -f lavfi -i "color=c=0x203040:size=320x180:rate=24:duration=2" \
  -vf "subtitles=$WORK/captions.srt,format=yuv420p" \
  -an -c:v libx264 -preset ultrafast -crf 30 "$WORK/subtitles-smoke.mp4"

"$FFMPEG" -hide_banner -y \
  -f lavfi -i "testsrc2=size=320x180:rate=24:duration=2" \
  -f lavfi -i "testsrc2=size=320x180:rate=24:duration=2" \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=1.5,format=yuv420p[v]" \
  -map "[v]" -an -c:v libx264 -preset ultrafast -crf 30 "$WORK/xfade-smoke.mp4"

"$FFMPEG" -hide_banner -y \
  -f lavfi -i "sine=frequency=440:sample_rate=48000:duration=2" \
  -f lavfi -i "sine=frequency=880:sample_rate=48000:duration=2" \
  -filter_complex "[0:a][1:a]acrossfade=d=0.5:c1=tri:c2=tri[a]" \
  -map "[a]" -c:a pcm_s16le "$WORK/acrossfade-smoke.wav"

export FFPROBE WORK
python3 - <<'PY'
import json
import os
import subprocess
from pathlib import Path

probe = os.environ["FFPROBE"]
work = Path(os.environ["WORK"])

def inspect(path: Path) -> dict:
    raw = subprocess.check_output([
        probe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ], text=True)
    return json.loads(raw)

av = inspect(work / "av-smoke.mp4")
streams = av["streams"]
video = next((s for s in streams if s.get("codec_type") == "video"), None)
audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
assert video, "AV smoke output has no video stream"
assert audio, "AV smoke output has no audio stream"
assert video.get("codec_name") == "h264", video
assert (video.get("width"), video.get("height")) == (320, 180), video
assert video.get("r_frame_rate") == "24/1", video
assert audio.get("codec_name") == "aac", audio
duration = float(av["format"]["duration"])
assert 1.90 <= duration <= 2.20, duration

subtitle = inspect(work / "subtitles-smoke.mp4")
assert any(s.get("codec_type") == "video" for s in subtitle["streams"]), subtitle

xfade = inspect(work / "xfade-smoke.mp4")
xfade_duration = float(xfade["format"]["duration"])
assert 3.35 <= xfade_duration <= 3.65, xfade_duration

acrossfade = inspect(work / "acrossfade-smoke.wav")
audio_only = [s for s in acrossfade["streams"] if s.get("codec_type") == "audio"]
assert audio_only, acrossfade
audio_duration = float(acrossfade["format"]["duration"])
assert 3.35 <= audio_duration <= 3.65, audio_duration

summary = {
    "target_version": "9.0.2",
    "platform": "Ubuntu 24.04 x86_64",
    "checks": {
        "version_pinned": True,
        "h264_aac_mux": True,
        "resolution_320x180": True,
        "frame_rate_24fps": True,
        "drawtext": True,
        "subtitle_burn_in": True,
        "loudnorm": True,
        "video_xfade": True,
        "audio_acrossfade": True,
        "required_encoder_and_filter_inventory": True,
    },
    "av_smoke_duration_seconds": duration,
    "xfade_duration_seconds": xfade_duration,
    "acrossfade_duration_seconds": audio_duration,
}
(work.parent / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
PY

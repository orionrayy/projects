# FFmpeg Motion Studio — Custom FFmpeg Runtime

This folder defines a reproducible **Ubuntu 24.04 x86_64** custom FFmpeg build for the Motion Studio rendering pipeline. It deliberately does not overwrite the host system's `ffmpeg` binary.

## Target and provenance

- Target: **FFmpeg 9.0.2** from the official FFmpeg 9.0 stable branch.
- Source: `https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz`
- Source SHA-256 pinned in `scripts/build_custom_ffmpeg.sh`.
- The source archive is verified against FFmpeg's official OpenPGP release-signing key, whose fingerprint is pinned in the build script.
- The custom feature profile includes H.264/HEVC encoding, VP9/AV1 codec support, ASS subtitles, drawtext, loudnorm, zscale, video xfade, and audio acrossfade. CI asserts the required encoders/filters and exercises the critical media paths.

The official FFmpeg release page identifies 9.0.2 as the latest patch on the 9.0 branch. FFmpeg 8.1.3 is a separate maintained branch; the project intentionally selects the newer 9.0 major line and pins it until tests authorize a change.

## Run in GitHub Actions

Workflow: `.github/workflows/ffmpeg-motion-studio-upgrade.yml`

A push to `feature/ffmpeg-motion-studio-9.0.2-upgrade`, a relevant pull request, or a manual workflow dispatch runs the build. On success, it publishes:

- `ffmpeg-9.0.2-ubuntu-24.04-x86_64.tar.gz` — the custom `ffmpeg` and `ffprobe` binaries with build provenance.
- `ffmpeg-9.0.2-regression-summary.json` — machine-readable regression results.
- `*.sha256` — an archive checksum.

Artifacts are retained for 14 days to keep the workflow free-first and avoid committing large binaries into Git. Download the artifact ZIP from the successful Actions run, then extract the inner `.tar.gz` package.

## Local build on Ubuntu 24.04

Install the prerequisites used by CI:

```bash
sudo apt-get update
sudo apt-get install -y build-essential pkg-config nasm yasm curl gnupg \
  fonts-dejavu-core libass-dev libfreetype6-dev libfontconfig1-dev libfribidi-dev \
  libmp3lame-dev libopus-dev libvorbis-dev libvpx-dev libx264-dev libx265-dev \
  libdav1d-dev libaom-dev libzimg-dev zlib1g-dev
```

Then run:

```bash
bash ffmpeg-motion-studio/scripts/build_custom_ffmpeg.sh
```

The package is written to `ffmpeg-motion-studio/dist/`. The test suite can also be run separately against an installed custom binary:

```bash
bash ffmpeg-motion-studio/scripts/smoke_test_ffmpeg.sh /path/to/bin /tmp/ffmpeg-motion-studio-qc
```

## What this does not claim

- It does not silently replace the FFmpeg binary on the user's Windows machine, Android/Termux device, or any production host.
- It does not claim a faster render without a like-for-like benchmark against a pinned baseline. CI records a smoke-encode benchmark, validates stream properties, and checks media-processing paths.
- A successful codec/filter test does not certify animation quality, character anatomy, numeric correctness in every frame, narration naturalness, or synchronization. Those remain separate Motion Studio acceptance gates.
- The binary is a **GPL-enabled custom build** because it enables GPL codec libraries. Anyone redistributing it must satisfy the applicable FFmpeg and linked-library license requirements.

## Upgrade rule

Do not bump `FFMPEG_VERSION`, source hash, or signing-key pin independently. Update the source provenance and profile together, pass all regression checks, inspect output metadata, and compare render speed against the same baseline/settings before promoting a new runtime.

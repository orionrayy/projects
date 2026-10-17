# FFmpeg Motion Studio — Custom FFmpeg Runtime

This folder defines reproducible runtime profiles for the Motion Studio rendering pipeline. It deliberately does not overwrite an existing system-wide FFmpeg installation.

## Linux custom build and provenance

- Target: FFmpeg 9.0.2 from the official FFmpeg 9.0 stable branch.
- Source: https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz
- Source SHA-256 is pinned in scripts/build_custom_ffmpeg.sh.
- The source archive is verified against FFmpeg's official OpenPGP release-signing key, whose fingerprint is pinned in the build script.
- The custom feature profile includes H.264/HEVC encoding, VP9/AV1 codec support, ASS subtitles, drawtext with HarfBuzz shaping, loudnorm, zscale, video xfade, and audio acrossfade. CI asserts required encoders/filters and exercises the critical media paths.

FFmpeg 9.0.2 is the selected custom Linux target; FFmpeg 8.1.3 is a separately maintained branch.

## Build and validate the Linux custom runtime

Workflow: .github/workflows/ffmpeg-motion-studio-upgrade.yml

On success, the workflow publishes a custom Ubuntu 24.04 x86_64 archive, a machine-readable regression summary, and archive checksum. Artifacts are retained for 14 days to keep the workflow free-first.

Local build prerequisites are Ubuntu 24.04 build-essential, pkg-config, nasm/yasm, GnuPG, and the external codec/filter development libraries listed in scripts/build_custom_ffmpeg.sh. Run:

~~~bash
bash ffmpeg-motion-studio/scripts/build_custom_ffmpeg.sh
~~~

## Windows 11 side-by-side install

The Windows script downloads a version-pinned FFmpeg 9.0.2 essentials build from Gyan's Windows builds, verifies the pinned SHA-256 before extraction, checks the version, required encoders and filters, performs a short H.264/AAC encode, and validates the result with FFprobe.

Run from the repository root in PowerShell:

~~~powershell
.\ffmpeg-motion-studio\scripts\install_ffmpeg_9_0_2_windows.ps1
~~~

Default install path: %LOCALAPPDATA%\FFmpeg-MotionStudio\9.0.2. Existing system installations remain untouched. To replace an existing versioned target, pass -Force; the previous target is preserved in a timestamped backup. To add this version to the current user's PATH, pass -AddToUserPath, then verify the selected executable with Get-Command ffmpeg -All because a machine-level PATH entry can still take precedence.

Workflow .github/workflows/ffmpeg-motion-studio-windows-validate.yml performs the same hash, version, codec, filter and media smoke checks on a native Windows runner and publishes a JSON report, not redistributed binaries.

## Benchmarks and acceptance boundary

This package does not claim a faster render without a like-for-like benchmark against a pinned baseline. Metadata, codec/filter tests and smoke encoding prove runtime functionality, not animation quality, character anatomy, numeric correctness in every frame, narration naturalness or synchronization. Those remain separate Motion Studio acceptance gates.

## Licensing

The Linux custom build enables GPL libraries. The Windows installer preserves upstream package license/readme files. Review applicable FFmpeg and linked-library licenses before redistributing either build.

## Upgrade rule

Do not bump FFMPEG_VERSION, source hash, signing-key pin or Windows package hash independently. Update provenance and the feature profile together, pass regression checks, inspect output metadata, and compare render speed against identical baseline settings before promoting a runtime.

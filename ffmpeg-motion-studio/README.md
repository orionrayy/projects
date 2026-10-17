# FFmpeg Motion Studio — Free-first cloud runtime

The upgrade workflow is designed to run in GitHub Actions on Ubuntu 24.04 x86_64. No Windows or local installation is required to build the Linux custom FFmpeg runtime.

## Target and source provenance

- Target: FFmpeg 9.0.2, the latest stable release on the FFmpeg 9.0 branch according to the official release page.
- Source: https://ffmpeg.org/releases/ffmpeg-9.0.2.tar.xz
- Source SHA-256 is pinned in scripts/build_custom_ffmpeg.sh.
- The source archive is verified against its signature using the pinned FFmpeg release-signing key.
- Build profile enables H.264/HEVC, VP9/AV1, ASS subtitles, shaped drawtext, loudnorm, zscale, video xfade, and audio acrossfade.

## Build on GitHub — no local runtime required

Workflow: .github/workflows/ffmpeg-motion-studio-upgrade.yml

Push changes to the upgrade branch or open the workflow in GitHub Actions and select **Run workflow**. The workflow builds from official source on Ubuntu 24.04, verifies provenance, executes codec/filter and audio/video regression checks, and uploads these artifacts on success:

- `ffmpeg-9.0.2-ubuntu-24.04-x86_64.tar.gz` — custom `ffmpeg` and `ffprobe` binaries, build manifest, runtime dependency report, and checksums.
- `ffmpeg-9.0.2-regression-summary.json` — machine-readable test results.
- Archive SHA-256 file.

To retrieve the package, open the successful run and download its Artifacts section. Artifacts are retained for 14 days to minimize long-lived storage and keep the process free-first. If the build fails, do not treat an artifact or upgrade as complete.

## Re-run locally only if desired

A local build is optional and requires Ubuntu 24.04 plus the development packages listed in scripts/build_custom_ffmpeg.sh:

```bash
bash ffmpeg-motion-studio/scripts/build_custom_ffmpeg.sh
```

## Acceptance boundary

Passing codec/filter tests and smoke encoding verifies runtime functions, not professional animation quality, character anatomy, numerical correctness across every frame, narration naturalness, or synchronization. Those remain separate Motion Studio acceptance gates. No claim of faster rendering is valid without a like-for-like benchmark against a pinned baseline.

## Licensing

The Linux custom build enables GPL libraries. Review FFmpeg and linked-library licenses before redistributing the package.

## Upgrade rule

Do not change the version, source hash, or signing-key pin independently. Update source provenance and the feature profile together, pass regression checks, inspect stream metadata, and compare render speed against identical baseline settings before promoting the runtime.

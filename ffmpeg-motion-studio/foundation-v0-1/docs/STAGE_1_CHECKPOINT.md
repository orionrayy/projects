# Foundation Stage 0/1 — Execution Checkpoint

Date: 2026-10-18
Repository: https://github.com/orionrayy/projects
Branch: `feature/motion-studio-foundation-v0-1`
Previous renderer: preserved; no migration performed.
Status: `VERTICAL_SLICE_CI_PASS` once the run for the current source revision completes.

## Scope delivered
- Strict Draft 2020-12 scene schema and one canonical 96-frame scene manifest.
- Frame-index deterministic motion core with two-bone IK; unreachable target clamping and explicit diagnostics.
- Shared SVG renderer used by interactive browser preview and deterministic headless export.
- Preview playback, pause, scrub/frame stepping, phase shortcuts, and rig diagnostic overlay.
- Layout reservation guard and fault-injection tests for target-marker collisions.
- FFmpeg H.264 render path plus ffprobe metadata validation and explicit visual-only report.
- GitHub Actions cloud workflow for schema validation, preview syntax/HTTP smoke tests, motion and layout tests, schema tests, export, and artifact upload.

## Acceptance evidence required
- Preview server routes `/preview/`, `/src/motion-core.mjs`, and `/scenes/scene-001.json` successfully.
- Determinism holds for repeated and shuffled frame requests.
- IK segment lengths remain within contract tolerance and unreachable targets are flagged rather than stretched.
- Layout fault injection reports marker/divider and marker/copy overlaps.
- Output metadata is H.264, 1280×720, 24fps, 96 frames / 4 seconds; no audio stream is expected for this prototype.
- Artifact `motion-studio-foundation-v0-1-visual-only` exists for the successful CI run.

## Test history / corrections
- First CI attempt exposed that FFmpeg is not guaranteed to be preinstalled on GitHub-hosted runners. Workflow now installs FFmpeg explicitly.
- A second attempt passed environment setup, manifest validation, Node tests, and Python schema tests; it was cancelled when a newer revision was pushed while rendering.
- Preview server path handling was simplified to avoid regex-escaping ambiguity; explicit JS syntax and HTTP smoke checks were added.
- The accepted CI status must be read from the latest run associated with this checkpoint, not inferred from local tests.

## Important limits
- The pilot is a simple stylized pointing gesture, intentionally silent.
- This does not prove natural acting, universal body proportions, artistic approval, commercial-video-generator parity, full-film migration, or production-ready audio.
- The original renderer remains untouched. No files were committed to `main`; the feature branch is the integration boundary.

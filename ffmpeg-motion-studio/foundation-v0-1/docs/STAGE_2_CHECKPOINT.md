# Stage 2 Checkpoint — Parameterized Preview and Motion Benchmark

Version: 0.2.0. Previous renderer preserved; no changes to main.

## Implemented
- In-memory controls for target X/Y, upper-arm and forearm length, anticipation, settle amplitude and elbow bend.
- Store A / compare candidate B at the same timeline frame; reset restores the canonical scene.
- Layout and IK warnings remain visible; controls do not silently persist changes into the source manifest.
- Adaptive settling amplitude reduces secondary motion when there is insufficient IK reach headroom.
- Seven synthetic motion scenarios evaluated across all 96 frames each.
- Per-case reporting includes reachability, segment-length error, wrist step size, acceleration, endpoint error and layout status.
- Cloud CI verifies preview HTTP routes, tests, schema contracts, synthetic benchmark and an actual FFmpeg export.

## Defect discovered and corrected
The expanded suite initially found five temporary unreachable frames for a low target near maximum reach and three for a near-max-reach target. The endpoint itself was reachable, but a decorative 4 px settle moved the requested wrist outside the IK envelope. The core now computes remaining reach headroom and scales the settle amplitude; all expected-reachable cases must stay reachable through every frame.

## Local validation
- 15 Node tests passed.
- 5 Python schema tests passed.
- Scene schema validation passed.
- Synthetic suite: 7/7 scenarios across 96 frames each (672 frame evaluations).
- Preview HTTP smoke checks passed for live controls and motion scenario catalog.
- FFmpeg/FFprobe: H.264, 1280x720, 24fps, 96 frames, 4 seconds, no audio.

## Limitations
- Browser-vs-librsvg pixel parity has not been measured. SVG generation and logical motion are deterministic, but font rendering and anti-aliasing can vary by rasterizer.
- Synthetic scenarios are engineering regression cases, not captured human motion or a universal naturalness score.
- One scene only; full-film migration, voiceover and artistic approval remain open.

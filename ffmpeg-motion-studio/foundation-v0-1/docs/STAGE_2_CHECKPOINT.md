# Stage 2 Checkpoint — Live Preview and Motion Benchmark

Version: 0.2.1
Branch: \`feature/motion-studio-foundation-v0-1\`
Base feature architecture: Foundation v0.1; old renderer untouched.

## Implemented
- Live in-memory parameter controls for target X/Y, upper-arm and forearm lengths, anticipation amplitude, settle amplitude and elbow-bend direction.
- Store A / compare candidate B side by side at the same frame; reset restores the canonical scene.
- Continuous warning state for unreachable IK targets and authored layout-reservation conflicts.
- Adaptive settling amplitude: secondary motion is scaled to available reach headroom.
- Seven synthetic scenarios evaluated over all 96 frames each, with reachability, segment error, endpoint error, step-size, acceleration and layout metrics.
- GitHub Actions runs preview HTTP smoke tests, Node tests (including interaction behavior), Python schema tests, benchmark and real FFmpeg export.

## Defect discovered and corrected
The expanded benchmark initially found five temporary unreachable frames for a lower target and three for a near-maximum-reach target. Their endpoint was reachable, but the decorative settling wobble exceeded the IK envelope. The motion core now reduces the settling amplitude according to geometric headroom. Regression tests require all frames in every expected-reachable scenario to remain reachable.

## Evidence
- 7/7 synthetic benchmark cases PASS across 96 frames each (672 frame evaluations).
- 16 Node tests pass locally, including a mocked-UI integration test that checks parameter changes, A/B reference preservation, layout warnings, IK warnings and reset behavior.
- 5 Python schema tests pass.
- Preview endpoints, scene manifest and benchmark catalog pass HTTP smoke checks.
- FFmpeg/FFprobe render contract: H.264, 1280×720, 24 fps, 96 frames, four seconds, intentionally silent.
- Cloud CI run for commit \`4fd1fa228a230171088b75284b1cb686e2db2fa0\`: PASS before the final UI interaction test was added. The next run must validate this checkpoint's exact commit.

## Remaining limitations
- Browser-versus-librsvg pixel parity remains UNVERIFIED. Logical motion and shared SVG serialization are deterministic; browser fonts/antialiasing may render differently.
- Synthetic motion profiles are engineering regression cases, not captured human motion or an aesthetic gold standard.
- No film migration, full narrative, voiceover, universal naturalness or commercial video-generator parity is claimed.

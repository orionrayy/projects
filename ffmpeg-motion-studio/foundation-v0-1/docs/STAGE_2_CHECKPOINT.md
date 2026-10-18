# Stage 2 Checkpoint — Live Preview, Motion Benchmark and Raster Diagnostics

Version: 0.2.2
Branch: `feature/motion-studio-foundation-v0-1`
Previous renderer: preserved and untouched.

## Implemented
- In-memory live controls for target X/Y, upper-arm and forearm lengths, anticipation, settle amplitude and elbow-bend direction.
- Store A / compare candidate B side-by-side at the same frame; reset restores the canonical scene.
- Live warning state for unreachable IK targets and authored layout-reservation conflicts.
- Adaptive settling amplitude that respects the remaining IK reach envelope.
- Seven synthetic scenarios evaluated across all 96 frames (672 frame evaluations), with reachability, segment error, endpoint error, step size, acceleration and layout metrics.
- Chromium-versus-FFmpeg/librsvg raster measurement for six frames, paired PNG evidence and two contact sheets.
- GitHub Actions validates preview HTTP paths, Node tests, UI interaction tests, Python schema contracts, motion benchmark, raster diagnostic and FFmpeg export.
- The exact source subtree can be packaged from the same CI checkout as the rendered evidence.

## Defect discovered and corrected
The expanded benchmark initially found five temporary unreachable frames for a lower target and three for a near-maximum-reach target. Their endpoint was reachable, but decorative settling exceeded the IK envelope. The motion core now reduces the settle amplitude according to geometric headroom. Regression tests require all frames in every expected-reachable scenario to remain reachable.

## Verified evidence
- 7/7 synthetic benchmark cases passed across all 96 frames.
- 16 Node tests passed, including a mocked UI integration test for editing, A/B reference preservation, layout warnings, IK warnings and reset.
- 5 Python JSON Schema tests passed.
- Preview HTTP smoke checks for the UI, motion core, scene manifest and benchmark catalog passed.
- FFmpeg/FFprobe: H.264, 1280x720, 24fps, 96 frames, four seconds, intentionally silent.
- Raster comparison used Google Chrome 155.0.8059.39, FFmpeg 6.1.1-3ubuntu5 and ImageMagick MAE. Six frames had identical 1280x720 dimensions; normalized MAE mean was 0.00179965, max 0.00182074 and min 0.00178600.
- Visual inspection of the six paired frames shows no obvious whole-object/layout displacement. Most visible differences are along shape/text edges and anti-aliasing. This is an initial inspection, not proof of perfect parity.
- Latest successful Cloud CI at v0.2.1 source commit `9958a344827f51ad9a48b2ad1ec6b05ebdd128ed`: https://github.com/orionrayy/projects/actions/runs/39123503277

## Raster calibration status
The raster report deliberately remains `MEASURED_UNCALIBRATED`. MAE is a global mean and can conceal local errors; the saved difference PNGs and contact sheets should be reviewed before choosing a tolerance. The sample covers six of 96 frames, so all-frame pixel parity is not yet established.

## Remaining limitations
- Synthetic motion profiles are engineering cases, not captured human movement or an aesthetic gold standard.
- The pilot is one stylized pointing scene. Full film migration, voiceover, audio mastering and artistic approval remain open.
- Passing tests does not prove naturalness or equivalence to commercial generative video.

# Stage 17 — Motion Studio v0.9.4 contact-aligned long-stride gait

Date: 2026-10-20 (Asia/Jakarta)

## Baseline and defect
This checkpoint is based on current v0.9.3 head 24e216af8b4fde254c4fb3a896aa80841e8dbbbd, which includes the integrated portrait gait/scene and recent portrait IK calibration. That work is preserved in this isolated candidate.

The landscape profile still uses an 85.2 px effective stride; the integrated portrait profile uses 96 px but different start/stop timing. The gait clock previously used the nominal clip duration rather than the timestamp of the last rendered sample. Its old phase warp could also hold a nonzero offset at integer cycle boundaries, preventing reliable double-support contact at the end.

## Candidate changes
- Landscape effective stride: 85.2 → 93 px (+9.2%), with the nominal 1.33 s cycle retained (about 90.2 steps/min).
- Retain the 96 px portrait stride and portrait-specific IK reach easing; align its ramp with the last rendered sample.
- Calibrate leg proportions to 80/82 px and pelvis root y=414 to provide more IK flex margin at contact.
- Evaluate start/stop ramps against (frame_count - 1) / fps, the timestamp of the last actually rendered frame.
- Replace accumulated phase offsets with bounded C2 phase warping proportional to sin(pi*u)^3; phase offset and its first derivative are zero at cycle boundaries.
- Select equal ramp durations so five cycles land on the last rendered frame for both the 192-frame/24fps landscape preview and 240-frame/30fps portrait preview.
- Raise the stride acceptance floor to 92 px without relaxing existing knee-step, ankle-reach, planted-foot, cadence, acceleration or FFprobe gates.

## Validation gates
1. All existing regression suites plus new boundary tests pass for carry, free-arm and integrated portrait gait.
2. First and final rendered frames have both feet in stance at ground level; phase offset and terminal gait rate are effectively zero.
3. Landscape stride is at least 92 px; portrait stride is at least 95 px; maximum knee step stays below 13 px/frame; ankle clamp stays below 1.5 px; stance drift stays below 0.05 px/frame.
4. Hosted render produces 192 frames at 1280×720/24fps for carry/free and 240 frames at 720×1280/30fps for portrait; FFprobe, checksum and artifact-upload gates pass.
5. Full-speed human review remains required. CI success alone does not establish naturalness, production readiness, browser/FFmpeg parity or audio QC.

## Rollback
v0.9.3 remains unmodified. If any gate fails, keep v0.9.4 draft and fix the earliest failing layer without relaxing thresholds.

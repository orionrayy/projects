# Motion Studio Foundation v0.8.7 — Stance Extension and Gait Biomechanics

This candidate preserves the v0.8.6 organic-contour renderer and improves stance/swing biomechanics.

## Changes
- Raise the pelvis 8px so the fixed leg chain can extend toward the ground during stance.
- Use phase-aware knee pole targets: relatively extended during stance, flexed during swing, with a smooth squared-sine/smoothstep transition at contact boundaries.
- Reduce swing-foot clearance from 30px to 24px to avoid an exaggerated crouching pose.
- Add gait-specific regression checks for stance-knee extension, stance/swing angle separation, knee bend, ankle reachability and deterministic cycle sampling.

## Validation
Node.js 20+; hosted workflow uses FFmpeg/librsvg and renders carry/free at 1280x720, 24fps, 192 frames with metrics, contact sheets, and SHA-256 sums.

Numerical tests are necessary but cannot prove naturalness. Full-speed human visual acceptance, renderer parity and full-film integration remain separate gates.

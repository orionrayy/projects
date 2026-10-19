# Stage 3 — Whole-body locomotion checkpoint (v0.7.0)

State: engineering checks pass; prototype only.

## Implementation
This stage adds deterministic biped gait, half-cycle separation, planted stance-foot mapping, smooth swing lift, two-bone IK, stable signed bend branches, pelvis bob, torso sway, partial head compensation, and low-amplitude basket suspension.

## Local validation evidence
- Full JavaScript test suite: 52/52 passed.
- Python unit tests: 13/13 passed.
- Synthetic motion benchmark: 7/7 passed.
- Rendered-pose validation: 96/96 frames passed.
- Locomotion render: 192/192 frames passed geometric gates.
- Output: H.264, 1280x720, 24fps, 8 seconds, silent.
- Maximum near/far elbow step: 5.05 / 4.67 px (gate 8px).
- Maximum near/far knee step: 15.87 / 15.47 px (gate 18px).
- Sampled stance foot world drift: approximately 2.27e-13 px.

The full source archive was extracted into a clean directory and re-run: 52/52 JavaScript tests, 13/13 Python tests and a fresh FFmpeg render passed.

## Open issues
- Contact sheet review only; full-speed human visual acceptance is not completed.
- Both hands are fixed to basket handles, so free-arm swing is not implemented.
- Stylized body is thin-limbed, and some leg silhouettes cross.
- Browser-vs-FFmpeg raster parity timed out in headless Chromium and remains unverified.
- No hosted CI result is claimed.
- No model training or dataset acquisition is claimed.
- This locomotion lab is not tied to the generator source for the separate Character Stability Rig V5 video and is not a full-film render.

## Reproduction
Run the full source package for the FFmpeg renderer and complete suite. This branch includes the locomotion evaluator, config and focused review tests; it does not contain the separate render script.

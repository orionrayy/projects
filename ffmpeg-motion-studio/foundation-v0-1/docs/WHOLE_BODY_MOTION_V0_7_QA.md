# Whole-body motion V0.7 QA record

- Branch increment: `feature/motion-studio-whole-body-v0-7`
- Python proof render: 8.000 s, 1280x720, 24 fps, 192 frames.
- MP4 independently decoded to 192 frames for visual evidence.
- Dense contact sheets: 8; context sheets: 4; detailed crops: 21.
- Maximum arm segment-length error: < 2.1e-13 px.
- Maximum leg segment-length error: < 1.3e-13 px.
- Foot and arm target-clamp error: 0 px.
- Hand-to-basket anchor error: 0 px.
- Head-relative-to-root horizontal range: 11.12 px; vertical range: 2.58 px.
- Left/right elbow-relative-to-root horizontal range: 12.14 / 12.08 px.
- Basket translation range: 9.60 px horizontal, 4.64 px vertical.
- Torso pitch interval: -0.0300 to +0.0537 radians.
- Steps/minute at test settings: 118.06.
- Motion Studio JS tests: 47 passed, 0 failed.
- Scene schema, evidence ledger, seven synthetic motion cases, rendered-pose gate (96/96), reference clip validation and 13 Python unit tests passed.
- `measure:raster-parity` did not finish within the 120 s execution window; this specific check is not counted as passed.
- Artistic/perceptual review is still required: passing geometry gates does not prove a perfect walk.

# Whole-body motion V0.7.1 — QA record

## Scope
A targeted update to improve synchronization among pelvis, torso, shoulders, arms, head and held props; walking cadence itself is not the sole motion source.

## Architecture
- One deterministic gait phase with intentional channel phase offsets.
- Separate angle-valued head nod (radians) and displacement-valued head bob.
- Bounded torso pitch and counter-shifted shoulder line.
- Wrist anchors locked to prop grips; elbow response shares the gait phase.
- Basket, handle, shell, and contents share one carry transform.
- The Python proof renderer draws the head on a crop-local isolated layer and rotates the face/hair group together.

## Local test evidence
- Motion Studio Node tests: 48 passed / 0 failed.
- Existing Python stability tests: 8 passed / 0 failed.
- New whole-body rig tests: 3 passed / 0 failed.
- Synthetic motion benchmark: 7/7 PASS.
- Rendered-pose gate: 96/96 PASS.
- Scene schema, evidence ledger and reference-clip checks: PASS.
- Independent MP4 metadata: H.264, 1280×720, 24 fps, 8.000 seconds, 192 decoded frames.
- Dense visual review: 8 contact sheets covering all frames; 4 context sheets; 21 detailed frames.
- Maximum arm and leg segment-length error from the rig solver: < 2.3e-13 px.
- Hand-to-basket anchor error: 0 px.
- Compared with V6 metrics, root-relative head movement increased about 27%; left/right elbow horizontal range increased about 22%; basket translation range increased about 23%.

## Limitations
This is a stylized procedural 2D demonstration, not motion capture. Some side-view leg silhouettes can still cross; numerical consistency does not prove natural-looking motion. Raster parity is not counted among passing gates. The four-minute CFG film is not automatically rebuilt by this foundational change; the update must be integrated and reviewed scene-by-scene before that release.

# Stage 6 — Natural Motion Refinement v0.8.2

State: engineering candidate; review artifacts must be inspected before visual acceptance.

## Defects motivating this stage

The v0.8.1 carry/free-arm contact sheets showed overly narrow leg projection, an excessively flexed free-arm silhouette, and torso/head movement that was difficult to read at overview scale.

## Candidate changes

- Increase pelvis bounce, phase-coupled torso sway and head counter-rotation with a secondary motion term.
- Introduce configurable head follow and torso horizontal response.
- Increase free-arm swing and pendulum response, while increasing wrist drop to avoid a persistently acute elbow angle.
- Increase projected left/right leg separation and reduce knee-forward bias.
- Refine rendered limb widths, torso silhouette and carry prop dimensions.
- Add metric acceptance checks for foot separation, torso/head angular range and free-arm relative wrist travel.

## Acceptance gates

- Node tests and hosted render pipeline must pass.
- Both profiles must encode complete 192-frame H.264 previews at 1280x720 / 24fps.
- Human visual review must compare v0.8.1 and v0.8.2 full-speed previews and contact sheets.
- Do not merge on geometry metrics alone. Keep naturalness, browser/FFmpeg parity and 240-second integration unresolved until evidenced.

# Stage 5 — Rendered Motion Evidence v0.8.1

State: implementation candidate; hosted render CI and human visual acceptance are separate gates.

## Scope delivered in this slice

- Reuses the v0.8.0 deterministic locomotion solver and scene definitions.
- Renders carry and free-arm profiles to complete 192-frame SVG sequences.
- Applies the pose evaluator's head counter-rotation around the neck pivot in visible SVG geometry.
- Records JSON reports per mode and a combined manifest. Reports keep human naturalness review and raster parity explicitly unresolved.
- Hosted CI rasterizes SVG with librsvg, encodes H.264 MP4 with FFmpeg, emits 4x4 contact sheets, probes dimensions/frame rate/frame count, and stores outputs as a 14-day artifact.

## Acceptance gates

- Node syntax and regression suite must pass.
- Both modes must generate 192 frames, H.264 1280x720, 24fps.
- Frame count must be 192 and the expected metric/report artifacts must exist.
- Geometry gates are not a substitute for visual review.
- Human review must assess foot sliding/crossing, body-part synchronization, hand/object contact, gait weight, head/torso coupling, and start/end motion continuity.
- Browser-vs-FFmpeg raster parity and full 240-second film integration remain open.

## Evidence limits

A green workflow confirms tests, SVG rasterization, video encoding, and metadata probes ran. It does not certify commercial-quality animation, artistic acceptance, or the full product feature set.

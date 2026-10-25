# Motion Studio Foundation — Rendered Validation v0.8.1

Status: review candidate, not a production editor release.

This stage adds a deterministic SVG renderer for carry and free-arm gait profiles, full-length frame preflight, machine-readable geometry reports, and a hosted FFmpeg preview artifact. It applies the pose evaluator's existing head counter-rotation around the neck pivot in visible head geometry instead of leaving the angle as an unused diagnostic output.

## Reproduce

Requirements: Node.js 20+ for tests; FFmpeg and librsvg are required only to rasterize and encode the preview.

- Run regression tests: npm test
- Generate all SVG frames and JSON evidence: npm run render:preview -- .working
- Hosted workflow output: carry/free MP4 previews, 4x4 contact sheets, and geometry reports.

The hosted workflow validates 192 frames per profile at 1280x720 and 24fps. Artifact retention is 14 days.

## Evidence boundaries

The geometry report verifies finite pose values, solver error bounds, contacts, and configured projection metrics. It does not establish artistic naturalness, correct weight, perfect anatomy, or production readiness. Human review of contact sheets and full-speed playback remains a required acceptance gate. Browser-vs-FFmpeg raster parity remains unverified.

## Out of scope for this review slice

This is a procedural 2D review harness. It is not a trained motion-understanding model and does not yet provide weight painting, mesh deformation, a general hierarchical rig editor, a full IK/FK authoring UI, mirrored rig authoring, a multi-track NLE, audio mixer UI, a generic effect stack, a caption editor, or an asset-rights catalog.

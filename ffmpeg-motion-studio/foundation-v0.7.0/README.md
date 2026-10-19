# Motion Studio Foundation — Locomotion v0.7.0

This review branch isolates deterministic procedural biped locomotion with basket carry. It is an engineering prototype, not a trained motion model or a production animation release.

## Included in this branch
- Deterministic whole-body pose evaluator with half-cycle-separated legs.
- Planted-foot mapping, smooth swing lift, two-bone inverse kinematics and deterministic signed-bend branches.
- Pelvis bob, torso sway, partial head compensation and constrained basket contacts.
- Scene configuration and smoke tests over all 192 frames.

## Hosted review-branch CI
GitHub Actions smoke workflow completed successfully: 6/6 Node tests passed on the review branch.
Run: https://github.com/orionrayy/projects/actions/runs/39303476254

This CI tests the review slice's solver, scene configuration and geometry constraints. It does not run the complete local FFmpeg source archive or validate artistic naturalness.

## Complete local evidence package
The full locally verified source package includes the FFmpeg SVG renderer, 192 frame outputs, MP4, contact sheet, execution report and validation logs. The downloadable source bundle is the complete reproduction package; this branch is a review slice and does not contain the separate renderer.

Local clean-extraction checks: JavaScript 52/52, Python 13/13, synthetic motion benchmark 7/7, rendered-pose gate 96/96, and a fresh 192-frame FFmpeg render passed.

## Known quality limits
The current profile carries a basket, so both hands remain attached to the handles and do not exhibit a natural free-arm swing. The character is schematic, leg silhouettes sometimes cross, full-speed human review remains open, and browser-vs-FFmpeg raster parity is unverified.

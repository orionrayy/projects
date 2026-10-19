# Motion Studio Foundation — Locomotion v0.7.0

This review branch isolates deterministic procedural biped locomotion with basket carry. It is an engineering prototype, not a trained motion model or a production animation release.

## Included in this branch
- Deterministic whole-body pose evaluator with half-cycle-separated legs.
- Planted-foot mapping, smooth swing lift, two-bone inverse kinematics and deterministic signed-bend branches.
- Pelvis bob, torso sway, partial head compensation and constrained basket contacts.
- Scene configuration and smoke tests over all 192 frames.

## Run
Use Node.js 20 or newer:
- npm test

The complete locally verified source package includes the FFmpeg SVG renderer, 192 frame outputs, MP4, contact sheet, execution report and validation logs. The branch itself is a review slice of that package; hosted CI is not claimed until a workflow is run against the committed source.

## Known quality limits
The current profile carries a basket, so both hands remain attached to the handles and do not exhibit a natural free-arm swing. The character is schematic, leg silhouettes sometimes cross, full-speed human review remains open, and browser-vs-FFmpeg raster parity is unverified.

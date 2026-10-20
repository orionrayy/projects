# Motion Studio Foundation — Temporal Quality v0.8.3

Status: engineering candidate. Human visual acceptance remains pending.

This stage adds per-frame step/acceleration diagnostics for the pelvis, chest, head, elbows, wrists, knees and feet; measures stance-foot drift only between consecutive stance frames; and counts contact-state transitions. It preserves the existing v0.8.2 motion parameters and rendered carry/free-arm review profiles.

## Reproduce

Requirements: Node.js 20+ for tests; FFmpeg and librsvg are used for previews.

- Run all tests: npm test
- Create SVG frame sequences and JSON reports: npm run render:preview -- .working
- Hosted workflow emits H.264 preview videos, 4-fps contact sheets and metric manifests for both profiles.

## Evidence boundaries

Temporal metrics can expose spikes and stance sliding, but cannot score weight, anatomy, acting or naturalness on their own. This remains procedural 2D motion, not a production editor or trained motion model. Full-speed review, browser-versus-FFmpeg parity and integration into the narrated 240-second film remain open.

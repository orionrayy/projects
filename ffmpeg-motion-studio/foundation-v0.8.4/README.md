# Motion Studio Foundation — Prop Interaction v0.8.4

Status: engineering candidate; human visual acceptance remains pending.

This stage removes the carried object from the free-arm demonstration, where it had appeared unattached, and adds a restrained cycle-phased tilt to the carry prop. The handle contact points are rotated with the basket so both wrists remain constrained to the same visible geometry.

## Reproduce
- Tests: npm test (Node.js 20+)
- Generate SVG frame sequences and JSON diagnostics: npm run render:preview -- .working
- Hosted Linux CI encodes carry/free H.264 previews and 4-fps contact sheets, and publishes a 14-day artifact.

## Evidence boundaries
A passing contact constraint proves only alignment of the computed wrist and handle points. It does not certify load bearing, natural grip, hand shape, acting, or production quality. The character remains a procedural 2D prototype.

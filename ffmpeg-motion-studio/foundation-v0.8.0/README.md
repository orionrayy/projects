# Motion Studio Foundation — Character Quality v0.8.0

This is a focused review slice for the local v0.8.0 candidate. It is not a production editor release.

## What changed
- Hermite foot swing with stance-matched boundary velocities.
- Explicit 2D pole-target IK to stabilize elbow/knee bend choice.
- Screen-space bilateral leg separation to reduce crossed projections.
- Heel/toe roll, stance lock, waist-level basket carry, larger handle separation and a separate free-arm counter-swing profile.
- New per-frame elbow flexion acceptance test; geometry/visual acceptance are kept separate.

## Local evidence
The complete local source bundle includes the SVG/FFmpeg renderer, carry/free MP4 previews, contact sheets, GIF previews, reports, and all tests. This branch contains the solver, scenes, and focused tests so the core logic can be reviewed and exercised in hosted CI.

## Reproduce
Requirements: Node.js 20+
Command: npm test

## Current status
Prototype; visual acceptance pending. Render reports and metrics only establish deterministic geometry and frame continuity. They do not prove natural character movement. The arms are schematic; full-speed visual art-direction review and browser-vs-FFmpeg raster parity remain open. General weight painting, mesh editing, FK/IK authoring UI, multitrack NLE, audio mixer UI, generic effect stack, smart caption editor, and asset-rights catalog are not part of this review slice.

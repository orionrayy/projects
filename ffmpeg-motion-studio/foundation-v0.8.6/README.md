# Motion Studio Foundation v0.8.6 — Organic Contours and Joint Integration

This candidate builds on v0.8.5's human-scale proportions by replacing straight taper polygons with curved limb silhouettes, integrating knee/elbow marks into the limb surface, adding sleeve-cuff seams, and refining palm, thumb and finger contours.

## Validation
- Node.js 20+; FFmpeg and librsvg tools for hosted video export.
- Run `npm test` and `npm run render:preview -- .working`.
- Hosted workflow renders carry/free profiles at 1280x720, 24fps, 192 frames, with contact sheets, per-frame metrics and SHA-256 sums.

This remains a procedural stylized 2D character, not realistic 3D anatomy. Geometry/temporal tests do not prove naturalness. Full-speed human acceptance, renderer parity and full-film integration remain pending.

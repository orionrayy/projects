# Motion Studio Foundation — Anatomy Refinement v0.8.1

**Status: anatomy prototype; visual acceptance pending.** This is an isolated review branch and does not replace v0.8.0 or change `main`.

## Scope of this increment

- Reusable tapered capsule geometry for limbs with rounded end caps and proximal/distal radii.
- A torso silhouette defined by shoulder, ribcage, waist and hip stations, smoothed into a closed path.
- Distinct shoulder landmarks and two-bone IK re-solving so arm lengths remain fixed as the shoulder profile changes.
- Head, hair cap, eye-only facial style, neck, clothing seams, hands, shoes and a detailed basket illustration.
- Deterministic sampling for both carry and free-arm locomotion profiles.
- A 192-frame SVG pipeline, PNG rasterization, H.264/FFprobe QC and contact-sheet artifacts in hosted CI.

## Run locally

Requirements: Node.js 20+, Python 3, FFmpeg/FFprobe; Python packages `cairosvg` and `pillow`.

```sh
npm test
npm run preview -- ./dist
python -m pip install cairosvg pillow
python scripts/rasterize-preview.py dist
python scripts/validate-preview.py
```

The preview command writes all per-frame SVGs and a JSON anatomy measurement manifest. The rasterizer builds two silent 1280x720, 24 FPS, 192-frame MP4s plus bulk contact sheets. Validation checks the codec, raster dimensions, nominal frame rate, frame count, duration and SHA-256.

## Explicit limits

This is a procedural 2D illustration and locomotion-study renderer, not a full rig/mesh authoring product. Rounded vector anatomy is a visual approximation, not deformable skinning. No general weight painting, mesh deformation, editor UI, IK/FK timeline authoring, motion capture/retargeting, physics, or multitrack audio is claimed here. Numeric tests do not establish anatomical correctness, natural motion, or artistic acceptance; inspect full-speed playback as well as the bulk contact sheets before promotion.

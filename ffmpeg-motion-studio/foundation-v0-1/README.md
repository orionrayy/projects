# Motion Studio Foundation v0.2.4

Isolated implementation pilot; the previous renderer is preserved and untouched.

## Goal
Prove a deterministic scene -> shared motion core -> interactive SVG preview -> FFmpeg H.264 export path before migrating the existing film.

## Requirements
Node.js 20+, FFmpeg with SVG/librsvg decoding, libx264 and ffprobe, Python 3 with jsonschema. The parity diagnostic also uses Chromium and ImageMagick (installed on the GitHub Actions runner).

## Interactive preview
Run `npm run preview` and open http://127.0.0.1:4173/preview/. The browser UI supports timeline play/pause, scrubbing, frame stepping, phase shortcuts, rig diagnostics, editable target X/Y, arm segment lengths, anticipation, settle amplitude, and elbow bend. Store an A reference and compare B side by side at the same frame. Edits are in-memory and do not alter the canonical scene manifest.

## Validation commands
```sh
python -m pip install -r requirements-test.txt
npm run validate:scene
npm test
python -m unittest discover -s tests -p '*test.py' -v
npm run benchmark:motion
npm run measure:raster-parity
npm run render
```

The synthetic motion suite evaluates seven authored engineering scenarios across 96 frames each. It tests reachability, IK segment lengths, endpoint error, frame-to-frame movement and layout reservations. These thresholds are regression guards, not universal standards of natural movement or aesthetics.

The raster parity diagnostic compares six selected SVG frames rendered by headless Chromium and FFmpeg/librsvg. It records normalized MAE plus the paired PNGs and difference/contact sheets. Current status is `MEASURED_UNCALIBRATED`: MAE is not an aesthetic score, and no pass/fail threshold has been chosen.

## Invariants and limits
- Motion is evaluated from an integer frame index, never accumulated playback deltas.
- Preview and export share the same JS motion core and SVG renderer.
- Unreachable IK targets are clamped and flagged; limbs are not stretched to force a target.
- Invalid scene fields, rig lengths, frame indices and reserved-zone collisions are rejected.
- The export is a four-second 1280x720/24fps silent visual pilot, not a production master or artistic-quality certification.
- Pixel parity has been sampled, not tested on all frames. The pilot does not prove natural acting, audio quality, arbitrary-character anatomy, or commercial video-generator parity.


## v0.2.3 visual/pose correction
The hand now follows the forearm during anticipation and eases into a straight pointing pose during reach. The SVG composition draws the upper arm over the torso edge to preserve a visible shoulder connection, adds a neck bridge, and reports TARGET AHEAD until measured contact tolerance is reached. A full-timeline visual contract test checks pose finiteness, arm/hand geometry and phase-accurate contact labeling.

These are structural/rendering fixes, not a claim that the character is anatomically or artistically production-ready. Human-motion evaluation and broader character-shape validation remain outstanding.


## v0.2.4 rest-pose correction
The initial wrist pose is now scene-configured through `character.rest_pose` rather than hard-coded near the torso. This moves the idle wrist forward and higher, preventing the elbow from folding behind the shoulder during anticipation. Schema validation makes these offsets explicit and rejects invalid ranges. A new test checks the elbow/wrist side relationship across all anticipation frames.

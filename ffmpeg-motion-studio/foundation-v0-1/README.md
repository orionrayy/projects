# Motion Studio Foundation v0.2

Isolated implementation pilot; existing renderers remain untouched.

## Goal
Prove a deterministic scene -> shared motion core -> interactive SVG preview -> FFmpeg H.264 export path before migrating the existing film.

## Requirements
Node.js 20+, FFmpeg with SVG/librsvg decoding, libx264 and ffprobe, Python 3 with jsonschema.

## Preview / validation
Run \`npm run preview\`; open http://127.0.0.1:4173/preview/. Use the timeline scrubber, play/pause, frame stepping, gesture shortcuts and rig diagnostics. Serve over HTTP, not file://.

Run \`python -m pip install -r requirements-test.txt\`, \`npm test\`, \`python -m unittest discover -s tests -p '*test.py' -v\`, \`npm run validate:scene\`, and \`npm run render\`.

The export is a four-second 1280x720/24fps silent visual pilot, not a production master or artistic-quality certification.

## Invariants
- Frame state is evaluated from an integer index, never accumulated playback deltas.
- Preview and export share the same JS motion core and SVG renderer.
- Unreachable IK targets are clamped and flagged; limbs are not stretched to force a target.
- Invalid schema fields, rig lengths, frame indices and reserved-zone collisions are rejected.
- Passing technical tests does not prove naturalness, aesthetic quality or commercial-generator parity.
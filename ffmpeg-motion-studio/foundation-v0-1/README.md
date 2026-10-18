# Motion Studio Foundation v0.3.0

Isolated character-rig/action-model upgrade. The older production renderer remains untouched.

## Architecture
- `character-rig.mjs`: local-to-world landmarks, torso pivot transforms, neck/head anchors, elbow pole construction.
- `action-model.mjs`: anticipation, curved reach, contact, settle and hold timing. The index axis aims toward the target throughout the action.
- `motion-core.mjs`: deterministic frame-index evaluation and two-bone IK with an elbow pole target.
- `pose-quality.mjs`: measurable checks for segment lengths, hand-target angle, and contact during hold.
- `svg-renderer.mjs`: presentation layer reused by browser preview and FFmpeg export.

## Validation
```sh
python -m pip install -r requirements-test.txt
npm run validate:scene
npm test
python -m unittest discover -s tests -p '*test.py' -v
npm run benchmark:motion
npm run measure:raster-parity
npm run render
```

The seven-case synthetic suite is an engineering regression set, not an aesthetic dataset or human-motion ground truth. Raster comparisons measure browser/FFmpeg consistency only. Silhouette, anatomy, gesture and timing still require human visual review.

## Scope
This is a compact 2D character-action rig, not a general-purpose human animation system. Its purpose is to explicitly separate character structure, action intent, IK geometry, pose quality contracts and rendering.

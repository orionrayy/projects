# Motion Studio Foundation v0.6.0

## Scope of this increment
This is the first bilateral-character and evidence-ledger integration step. It does **not** claim that the renderer is production-grade or that motion data has been learned. The existing production renderer and `main` remain untouched; changes are isolated to `feature/motion-studio-foundation-v0-1`.

## Architecture in this increment
- `scene-001.json`: an explicit bilateral master with screen-left and screen-right arms, a target-action arm, a relaxed far arm, and required render groups.
- `character-rig.mjs`: world-space landmarks and deterministic pole targets for both arm chains.
- `action-model.mjs`: phase-aware anticipation, curved reach, contact, settle and hold targets.
- `motion-core.mjs`: frame-index pose solving for both arms, with per-bone geometry diagnostics.
- `pose-quality.mjs`: machine-checkable segment, target-contact, and hand-aim contracts. These checks are engineering guards, not an aesthetic quality score.
- `svg-renderer.mjs`: explicit rendered groups for both arms, both hands, torso, head and legs. The far-side arm is layered behind the torso.
- `research/evidence-ledger.json`: provenance register distinguishing verified source findings, CI-pending implementation claims, and data/training work that has not been performed.

## Validation
```sh
python -m pip install -r requirements-test.txt
npm run validate:scene
npm run validate:evidence
npm test
python -m unittest discover -s tests -p '*test.py' -v
npm run benchmark:motion
npm run validate:rendered-pose
npm run measure:raster-parity
npm run render
```

CI must confirm required render groups and both arm chains on every frame, not merely check that SVG strings compile. Benchmark and raster reports are attached to the exact tested source revision.

## Rendered-pose gate in v0.5.0
The prior hand-aim metric compared `handAngle` to the same wrist-to-target angle used to construct it, so it could not detect a renderer transform defect. v0.5.0 evaluates the serialized `pointing-hand` transform across every declared frame and checks origin, rendered tip, scale, and angle. A mutation test changes the SVG rotation and must fail. This is a geometry/render contract only, not a human-motion or aesthetic score.


## User-supplied manual keyframe reference (v0.6.0)

A separate keyframe path preserves five authored poses in `reference-data/stickman-step/clip.json` as 11 named landmarks and 10 parent-child segments. It adds a versioned clip schema, deterministic linear interpolation, SVG rig rendering, a scrubbable browser preview at `/preview/stickman-step.html`, sample-specific geometry gates, and FFmpeg/FFprobe export.

Run from this project directory:

```sh
npm run validate:reference-clip
npm run render:reference-clip
```

The fixture records the SHA-256 of the user-provided archive. The inspected source does not specify a reliable playback frame rate; 24 FPS and eight output subdivisions per source interval are Motion Studio choices, not asserted source-app semantics. This demonstrates structured geometry ingestion and procedural interpolation only; it is not model training, a generalized walking model, or artistic approval. The left-toe landmark is labelled a planted candidate only because its measured start/end displacement is small.

## Evidence policy
- Dataset research is not dataset ingestion.
- Dataset ingestion is not model training.
- Passing deterministic geometry tests is not artistic acceptance.
- Rasterizer consistency is not visual-quality proof.
- Any training claim must cite the dataset version, license review, data manifest, configuration, resulting model digest, and a separate evaluation report.

No external dataset is downloaded and no model is trained or fine-tuned in this increment.

## Clean-room research and topology stress tests

Aggregate-only static findings from the submitted Drawing Cartoons 2 sample are documented in `research/drawing-cartoons-2-clean-room-findings.md`, with eight controlled open questions in `research/format-semantics-experiment-plan.json`. The source archives, APK, DEX bytecode, character images and audio are not redistributed. Keyframe clip validation also checks that the ordered landmark list and numeric point-ID map match the clip's landmarks, that IDs are unique, and that the root has no parent. Synthetic stress tests cover 6, 27 (parent depth 26), 30, 64 and 128 landmarks. These tests are robustness checks, not claims about original-app limits or human-motion aesthetics.


## Whole-body locomotion layer (v0.7.0 increment)
`src/whole-body-motion.mjs` adds a deterministic phase-coupled motion evaluator for pelvis bounce/sway, torso pitch and shoulder shift, head counter-sway/nod, free-arm counter-swing, and carried-prop lag/rotation. `motion-core.mjs` exposes these channels as `state.wholeBodyMotion` only when a scene opts in through `motion.whole_body_motion`; the existing reach scene remains visually unchanged by default.

The carry-walk proof of concept was rendered by the companion Python procedural rig. QA evaluated 192 frames extracted independently from an 8 s, 1280×720, 24 FPS MP4 across 8 dense contact sheets, 4 context sheets, and 21 high-resolution detail frames. Segment lengths and hand-to-prop contact were checked numerically. This is deterministic stylized 2D animation, not motion-capture data or a guarantee of artistic perfection.

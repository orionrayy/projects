# Motion Studio Foundation v0.4.0

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
npm run measure:raster-parity
npm run render
```

CI must confirm required render groups and both arm chains on every frame, not merely check that SVG strings compile. Benchmark and raster reports are attached to the exact tested source revision.

## Evidence policy
- Dataset research is not dataset ingestion.
- Dataset ingestion is not model training.
- Passing deterministic geometry tests is not artistic acceptance.
- Rasterizer consistency is not visual-quality proof.
- Any training claim must cite the dataset version, license review, data manifest, configuration, resulting model digest, and a separate evaluation report.

No external dataset is downloaded and no model is trained or fine-tuned in this increment.

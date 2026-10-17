# Project Status and Checkpoint

Updated: 2026-10-18  
Repository: orionrayy/projects  
Project root: full-motion-analysis/  
Working branch: feat/fma-open-world-relational-v0-2  
Pull request: https://github.com/orionrayy/projects/pull/3 (draft; not merged)

## Current release state

**Target version:** v0.2.0 open-world relational foundation  
**CI at validated code checkpoint:** PASS — run [39061424908](https://github.com/orionrayy/projects/actions/runs/39061424908) on source commit \`af5f7981c82615ef5cdb0b2179faec3c438af95b\`  
**Unit/integration tests:** 30 passed  
**Synthetic benchmark:** 9/9 contract checks passed  
**Production readiness:** NO  
**Real-world benchmark evidence:** NOT ESTABLISHED  
**Universal domain generalization:** NOT ESTABLISHED  
**Semantic action / persistent identity / 3D motion / physical speed / causal inference:** NOT CLAIMED AS SOLVED  
**LLM or paid inference required by baseline:** NO  
**Local stdio MCP:** source updated; MCP contract tests passed in CI  
**Remote MCP:** source and Render Blueprint exist; deployment and live end-to-end smoke test are not confirmed

## Foundation changed

- Public \`motionlab.analyze_video\` now delegates to the open-world relational core. The primary unit is an overlapping RGB space-time volume, not an adjacent frame pair.
- Features combine per-channel appearance, multiscale spatial gradients/orientation/correlation, temporal envelopes, signed first-half/second-half spatial contrast, joint spatiotemporal spectral energy, 24 fixed-region descriptors and regional relations.
- Cross-window structure-shift candidates and recurrence relations are computed from complete block signatures.
- \`fma.openworld.relational-signature.v1\` and \`fma.openworld.analysis.v0.2\` define the current feature/report contracts.
- The v0.1 pairwise analyzer is preserved in \`motionlab/legacy_analysis.py\` for controlled baseline comparisons.
- Abstract/nirmana interference and procedural Mandelbrot zoom fixtures are added beside motion, freeze, flash, camera-pan reversal and mixed global/local movement.
- CLI, FFmpeg QC and local/remote MCP sources now call the v0.2 analysis core. A test passing does not mean a remote service is live.

## Training and autonomy

- Added a CPU-first unlabeled trainer with robust normalization, PCA projection and deterministic anonymous prototypes using NumPy.
- Training sources are deduplicated by SHA-256 and split by source-video hash, not by overlapping windows.
- Model, manifest and training report are written separately. Model JSON has a SHA-256 integrity digest.
- Candidate promotion is gated on source count, held-out source separation, coverage, a held-out quantization comparison against a frozen training-only baseline, prototype diversity, finite values and explicit rights attestation.
- Added a foreground watch mode. It inventories a local corpus, retrains when metadata inventory changes, persists \`watch_state.json\`, avoids repeating a successful unchanged run and rate-limits same-inventory retries after a failure/gated outcome.
- Training does not download or upload video. Watch mode is a foreground process, not a detached service.

The learned model currently groups hand-designed relational signatures into corpus-relative anonymous prototypes. It is trainable, but it is not a neural foundation encoder and does not learn human semantics automatically.

## Verified CI evidence

Run [39061424908](https://github.com/orionrayy/projects/actions/runs/39061424908):
- Python source compilation passed.
- 30 unit/integration tests passed.
- The synthetic benchmark generated and analyzed movement/reversal, freeze, flash, camera-pan reversal, independent local motion during a pan, abstract/nirmana interference and a procedural fractal zoom.
- All nine benchmark contract checks passed: feature availability, coverage reporting, three scales, relational spatial field, finite features, duplicate-frame integrity signal, nonconstant signatures on dynamic cases, deterministic repeatability, and the v0.2 non-frame-pair primary representation contract.
- The benchmark report explicitly records \`synthetic_only=true\`, \`real_world_evidence=false\`, and \`state_of_the_art_claim_supported=false\`.

This evidence establishes deterministic code behavior on controlled synthetic sources only. It is not a real-world accuracy result.

## Remaining validation gates

1. Acquire or generate a reproducible, rights-cleared evaluation corpus spanning abstract art, fractals, stylized animation, natural video, POV/third-person and mixed unfamiliar scenes.
2. Measure retrieval/recurrence quality, temporal intervention sensitivity, structural shift localization, robustness and abstention on held-out source videos.
3. Compare against the preserved v0.1 baseline and simple static/multiscale baselines using the same CPU/RAM/sampling budget.
4. Profile long videos and low-resource devices, including worst-case memory, runtime, and output-size behaviour.
5. Deploy remote MCP only after explicit workspace/owner approval; verify authenticated upload, analysis, pagination, retention and cleanup end-to-end on a supported client.
6. Keep the PR draft until real-world evaluation begins and a reviewer verifies implementation contracts.

## Known limitations

- Open-world means no mandatory input-domain ontology; it does not mean semantic understanding of all possible videos.
- The feature extractor is still hand-designed. The trained layer learns normalization, projection and anonymous prototypes; it is not a learned neural spatiotemporal encoder.
- Fixed region nodes are not object segmentation or persistent identity.
- Spectral energy is partly order-insensitive; signed temporal contrast provides one additional order-sensitive statistic, not full motion semantics.
- A one-view video cannot uniquely determine all 3D motion or physical causes. Unsampled intervals cannot be recovered as fact.
- Metadata-based watch detection can miss content altered while preserving both file size and modification time; run training manually after such a change.
- Auto-promotion gates evaluate unsupervised codebook utility, not semantic accuracy or universal domain transfer.

## Checkpoint policy

Record exact source SHA, feature-schema version, CI run, dataset/source hashes, model digest, training options and promotion-gate results. Never merge or claim production readiness solely on synthetic CI.

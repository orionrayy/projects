# Project Status and Checkpoint

Updated: 2026-10-18  
Repository: orionrayy/projects  
Project root: full-motion-analysis/  
Validated code checkpoint: \`37074b4e0dca605f3e87219a381e3144deb49bc4\`  
Active draft PR: https://github.com/orionrayy/projects/pull/7

## Current release state

**Target version:** v0.2.0 open-world relational foundation + self-supervised signature encoder  
**CI:** PASS — [run #39062384750](https://github.com/orionrayy/projects/actions/runs/39062384750) at the code checkpoint above  
**Unit/integration tests:** 32 passed  
**Synthetic benchmark:** 9/9 contract checks passed  
**Production readiness:** NO  
**Real-world benchmark evidence:** NOT ESTABLISHED  
**Universal domain generalization:** NOT ESTABLISHED  
**Semantic action / persistent identity / 3D motion / physical speed / causal inference:** NOT CLAIMED AS SOLVED  
**LLM, GPU or paid inference required by baseline:** NO  
**Local MCP:** code updated; MCP security contract tests pass, but no separately deployed local MCP host is claimed  
**Remote MCP:** source and Render Blueprint exist; live deployment and end-to-end remote smoke test are not confirmed

## Foundation rewrite

- Public \`motionlab.analyze_video\` now uses overlapping RGB space-time volumes as the primary analysis unit. Frame-pair optical flow is not the core representation.
- Each block yields color distributions, multi-scale spatial gradients/orientation/autocorrelation, temporal envelopes, signed half-block spatial contrast, joint spatiotemporal spectral energy, 24 fixed-region descriptors and regional-relation edges.
- Cross-window structure-shift candidates and recurrence relations use whole-block signatures.
- Current contracts: \`fma.openworld.relational-signature.v1\` and \`fma.openworld.analysis.v0.2\`.
- The previous frame-pair analyzer is preserved as \`motionlab/legacy_analysis.py\` for explicit baseline comparison.
- Synthetic fixtures cover movement/reversal, freeze, flash, camera-pan reversal, mixed camera/local movement, abstract/nirmana interference and procedural Mandelbrot zoom.
- Isolated global-luminance pulses are a separate low-level QC candidate, so flash warnings can still reach FFmpeg render audit. This is not a semantic flash classifier.

## Training and autonomous operation

- Added an unlabeled NumPy denoising autoencoder trained to reconstruct intact signatures from masked/noisy signatures.
- The learned embedding is followed by deterministic, farthest-first initialized prototypes; outputs are anonymous corpus-relative clusters and novelty ratios, not semantic classes.
- The block feature extractor remains hand-designed. The autoencoder learns a nonlinear representation over signatures; it is not an end-to-end raw-pixel video foundation model.
- Corpus intake hashes and deduplicates source videos. Train/validation are split by source-video hash to prevent overlapping-window leakage.
- Candidate model, dataset manifest and training report are stored separately. The model has an integrity SHA-256.
- Promotion gates include distinct train/holdout sources, coverage, held-out prototype quantization improvement versus a frozen training-only centroid, cluster diversity, decreasing clean reconstruction loss, finite model parameters and operator rights attestation.
- \`motionlab train --watch\` monitors local corpus inventory, retrains on inventory changes, writes durable \`watch_state.json\`, rate-limits repeated retries and skips unchanged inputs after a successful or previously gated attempt. It stays in the foreground; it is not a detached production service.

Training stays local by default. It does not fetch online datasets, upload personal videos, or commit video media to GitHub.

## Verified CI evidence

[Run #39062384750](https://github.com/orionrayy/projects/actions/runs/39062384750) executed on code checkpoint \`37074b4e0dca605f3e87219a381e3144deb49bc4\`:
- Source compilation passed.
- 32 unit/integration tests passed.
- Encoder fit/score, deterministic model hash, model load/integrity and dimension-mismatch tests passed.
- The watcher integration test verified that an insufficient corpus cannot promote an active model, records a checkpoint and skips retraining on an unchanged follow-up pass.
- The flash-QC regression test verified that a synthetic global-luminance pulse produces a \`possible_flash_candidate\` and the FFmpeg render audit surfaces \`FMA-QC-FLASH-CANDIDATE\`.
- The synthetic benchmark analyzed movement/reversal, freeze, flash, camera-pan reversal, independent local movement under global pan, abstract/nirmana interference and Mandelbrot zoom.
- All nine benchmark checks passed: space-time signature availability, coverage reporting, multiscale signatures, relational field, finite features, duplicate-frame integrity signal, dynamic signature variation, repeatability and the non-frame-pair-primary contract.
- Benchmark assertions explicitly state \`synthetic_only=true\`, \`real_world_evidence=false\`, and \`state_of_the_art_claim_supported=false\`.

This verifies code contracts on synthetic clips. It is not a measurement of real-world accuracy or domain generalization. The watcher has an integration test, but has not been validated as a long-running production process on a real authorized corpus.

## Remaining gates

1. Evaluate a rights-cleared corpus spanning abstract art, fractals, stylized animation, natural video, POV/third-person and unfamiliar mixed scenes.
2. Publish cross-domain metrics, failure cases, recurrence retrieval quality, temporal intervention sensitivity, robustness and abstention behaviour on held-out source videos.
3. Compare against the preserved v0.1 baseline and simple static/multiscale baselines under identical CPU/RAM/sampling budgets.
4. Profile long videos and low-resource devices, including peak RAM, runtime and report-size behaviour.
5. Run a real local-corpus training job on authorized data, inspect its manifest and gates, and verify model promotion/rollback.
6. Deploy remote MCP only with explicit owner approval and verify authentication, upload, analysis, report pagination, retention and cleanup end-to-end.
7. Keep the PR draft until independent real-video validation begins and implementation contracts receive review.

## Known limitations

- “Open-world” means no mandatory input-domain ontology at intake; it does not guarantee accurate semantic understanding of every possible video.
- Signature extraction remains hand-designed. The encoder learns from those signatures, not directly from raw pixels.
- Fixed image regions are not persistent object identities or object segmentation.
- Fourier energy loses some temporal order/direction information; signed temporal contrast recovers only a limited portion of temporal asymmetry.
- A single-view video cannot always determine 3D motion, physical causes or intent. Unsampled intervals remain unobserved.
- Novelty ratios are not calibrated probabilities or anomaly truth.
- The watcher uses file size and modification time for inexpensive change detection; manually rerun training if content changes while preserving both metadata values.
- Auto-promotion evaluates unsupervised representation and reconstruction criteria, not semantic accuracy or universal transfer.

## Checkpoint policy

Track source SHA, model SHA, feature schema, training options, dataset hashes, CI run and each promotion gate. Do not merge or claim production readiness based only on synthetic CI.

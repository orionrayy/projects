# Project Status and Checkpoint

Updated: 2026-10-18  
Repository: orionrayy/projects  
Project root: full-motion-analysis/  
Branch: feat/full-motion-analysis-v0-1  
Pull request: https://github.com/orionrayy/projects/pull/1 (draft; not merged)

## Current release state

**Version target:** v0.2.0 open-world relational foundation  
**Implementation status:** foundation modules and training workflow committed to the draft branch  
**Latest source validation:** pending fresh CI for the v0.2 rewrite  
**Production readiness:** NO  
**Real-world benchmark evidence:** NOT ESTABLISHED  
**Universal domain generalization:** NOT ESTABLISHED  
**Semantic action / object identity / 3D motion / physical speed / causal inference:** NOT CLAIMED AS SOLVED  
**LLM or paid inference required by baseline:** NO  
**Local stdio MCP:** source updated to expose relational evidence and optional model scoring; latest CI pending  
**Remote MCP:** source and Render Blueprint exist; deployment and end-to-end smoke test have not been confirmed

## Foundation changed

- The public analysis entry point now delegates to a new open-world relational engine that operates on overlapping RGB space-time blocks rather than using frame-pair optical flow as the core representation.
- New signatures combine color distributions, multi-scale gradients and correlations, temporal envelopes, 3D spatiotemporal frequency bands, a 4×6 regional relation graph and cross-window recurrence candidates.
- The block feature schema is versioned as fma.openworld.relational-signature.v1.
- The original v0.1 pairwise analyzer is preserved in motionlab/legacy_analysis.py for baseline comparison.
- CLI and MCP expose the new analysis path. Optional OpenCV remains non-essential for the v0.2 core.

## Trainable / autonomous local workflow

- Added an unlabeled CPU-first trainer using robust normalization, PCA projection, and deterministic structure prototypes.
- Added video-hash source-level train/validation separation, exact-file deduplication, corpus/model manifests, validation summaries and promotion gates.
- Local gated promotion requires a distinct multi-video corpus, a held-out video split, minimum coverage, measurable unsupervised prototype utility, diversity and an explicit rights attestation.
- The learned model represents corpus-relative anonymous structure clusters. It does not learn human semantics or guarantee cross-domain generalization.
- Training does not download, upload, or commit the supplied media.

## Validation still required

The earlier v0.1 CI checks do not validate the rewritten v0.2 core. A fresh workflow run must confirm:
1. Python compilation and dependency installation.
2. Existing remote-MCP security tests.
3. New relational signature tests, including temporal reversal, color structure, finite degenerate cases and region relations.
4. New model fitting, integrity, scoring and dimensionality tests.
5. Updated synthetic integration benchmark over movement, freeze, flash, global pan and mixed local content.
6. Deterministic repeatability and explicit synthetic-only evidence contract.

After CI, the next stage is a rights-reviewed, domain-stratified real-video benchmark. Candidate datasets remain only a registry until the exact terms and media are reviewed. Synthetic passes are not real-world evidence.

## Known limitations

- The signature substrate is still hand-designed. It broadens domain-neutral inspection but cannot represent every possible phenomenon.
- The learnable layer is a CPU-first statistical representation/codebook, not a learned neural spatiotemporal foundation encoder.
- Fixed 4×6 regions are not object segmentation or persistent object identity.
- The spectral signature can be ambiguous; Fourier energy alone does not preserve every directional or semantic relationship.
- Sampling resolution/window stride can miss small or fast structure. Unobserved intervals cannot be reconstructed as fact.
- Auto-promotion gates only evaluate unsupervised codebook utility; independent labelled evaluation remains necessary before production claims.

## Checkpoint policy

Do not merge or label production-ready until the new branch's CI is green and the real-video validation plan has begun. Record the exact branch head, CI run IDs, model hash, feature schema, corpus hashes and promotion-gate results in the next checkpoint.

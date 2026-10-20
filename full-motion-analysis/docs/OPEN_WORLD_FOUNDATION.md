# Open-World Foundation Contract

## Objective

FMA should inspect visual-temporal evidence from arbitrary unknown inputs without requiring a predefined object ontology or domain label. “Open-world” is an intake and representation goal, not a guarantee of perfect semantic understanding for every possible video.

The supported target ranges from abstract/nirmana compositions and fractal zooms to cartoons, anime, movies, POV footage, third-person recordings and everyday scenes. These domains remain separate evaluation strata, not mandatory routing branches.

## Architectural shift

The v0.1 implementation estimated frame-pair differences and optional optical flow before thresholding event candidates. That implementation remains in motionlab/legacy_analysis.py as a comparison baseline.

The v0.2 public analysis core instead treats an overlapping RGB space-time block as its primary signature unit. It preserves:
- appearance/color distributions;
- multiscale spatial texture and autocorrelation;
- temporal envelopes and frequency structure;
- joint spatiotemporal spectral energy;
- fixed-region relations and cross-window recurrences;
- source-linked provenance, sampling coverage and model limits.

Frame samples remain the digital input substrate. This design does not claim to infer an unobserved continuous world between samples; it explicitly records its sampling interval and resolution.

## What the current core does not claim

- It is not a universal semantic reasoner.
- Fixed region nodes do not represent persistent objects.
- Similarity does not imply identity or causal relation.
- Fourier signatures do not uniquely identify the process that generated a video.
- An anonymous prototype is not a class such as “person walking” or “Mandelbrot zoom.”
- An automatic promotion gate does not prove semantic accuracy or cross-domain generalization.
- No state-of-the-art or world-first claim is justified by synthetic CI.

## Change-control rule

If an addition reintroduces a mandatory stage that classifies a video domain before analysis, requires object detection for all inputs, or makes per-frame/per-pair inference the central representation, the change must be treated as an explicit architecture proposal and evaluated against the open-world contract.

Any proposed “universal” operator must be evaluated for counterexamples on at least:
1. abstract spatial patterns;
2. scale-recursive/fractal imagery;
3. non-rigid stylized animation;
4. natural camera footage;
5. POV and third-person movement;
6. mixed-domain or unfamiliar footage.

All claims must distinguish observed measurement, model-supported interpretation, and speculation.

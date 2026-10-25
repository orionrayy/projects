# Benchmark and Evidence Protocol — Open-World FMA

## Scope contract

The benchmark must evaluate whether the shared representation preserves useful structure across unfamiliar video kinds. Domain names are evaluation strata, not mandatory routing classes. Success on one category does not establish universal generalization.

Primary strata should include:
- abstract/nirmana compositions and kinetic art;
- fractal and mathematical zoom sequences;
- 2D animation, cartoons and anime, including non-rigid stylization;
- film and natural camera recordings;
- POV and third-person scenes;
- everyday recordings with occlusion, lighting changes, compression and camera motion;
- mixed or unfamiliar visual sources that were not used to design feature rules.

Only use media with clear rights and provenance. Locally generated synthetic fixtures are appropriate for controlled invariants but cannot substitute for natural video.

## P0: deterministic software-contract checks

The current CI benchmark generates controlled motion/reversal, freeze, flash, global-pan and pan-plus-independent-content clips. It checks:
- complete, finite multiscale space-time signatures;
- stable feature dimensionality and feature-schema identity;
- regional-node / relational-edge generation;
- reported temporal coverage;
- deterministic repeatability on the same input and environment;
- a duplicate-frame integrity signal;
- explicit non-use of pairwise optical flow as the primary v0.2 representation.

A passing synthetic run verifies software behaviour only. It does not establish generalization, novelty, semantic understanding or state of the art.

## P1: open-world invariance and sensitivity matrix

Every operator should declare transformations that should preserve its output, transformations that should change it, and circumstances where the expected relation is not knowable. Evaluate paired/counterfactual clips such as:

| Controlled transformation | Expected analysis property |
|---|---|
| Moderate exposure/gamma change | Structural descriptors should remain usable; appearance descriptors may change and must remain distinguishable from geometry evidence. |
| Palette swap with same shapes | Geometry/temporal relationships should not be erased by the color change; appearance channels should explicitly register it. |
| Spatial resizing / crop / translation | Cross-scale or regional relationships should preserve only the invariances declared by the operator. |
| Fractal zoom | Scale-sensitive signatures should change measurably and preserve useful recurrence information where it exists; they need not infer the mathematical formula. |
| Reverse or shuffle temporal order | Order-sensitive descriptors should change; order-invariant spectral-energy descriptors must not be presented as sufficient evidence of direction. |
| Repeat or drop intervals | Reported coverage and temporal statistics must expose the alteration rather than pretending the clip was fully observed. |
| Camera pan with independent local content | Global and regional evidence should remain separately available without assuming a semantic object identity. |
| Non-rigid stylized deformation | Avoid rigid-body assumptions; measure structural change and disclose ambiguous correspondence. |
| Compression, blur, occlusion and low texture | Measure degradation and abstention, not just the cases that remain easy. |

Do not assert invariance simply because a particular signature happens to stay similar on one synthetic example. Each property requires multiple seeds, resolutions, motion amplitudes and background patterns.

## P2: independent real-video evaluation

Use rights-reviewed, documented datasets or personally collected/authorized clips. The existing DATASET_REGISTRY is a candidate list, not evidence that any media was acquired or approved.

Required protocol:
- archive dataset version, official URL, terms, licence, attribution, SHA-256 and allowed use;
- keep train / calibration / validation / final test split at the original-video or scene level;
- keep final test videos unseen during feature-rule design and model training;
- include a human-labelled subset with clear annotation rules and adjudication;
- publish per-stratum results, failures, abstentions and confidence intervals;
- compare against the v0.1 frame-pair baseline, static appearance-only signatures, and simple multiscale baselines under the same sampling/resource budget.

## Evaluation measures

- Signature repeatability under declared invariances.
- Sensitivity to declared temporal interventions and temporal-order reversal.
- Recurrence retrieval precision/recall against human-curated or constructed ground truth.
- Change-interval temporal IoU and timestamp error where event boundaries are annotated.
- Region-relation robustness; do not call it object segmentation accuracy.
- Training-model quantization error, cluster occupancy and novelty calibration against independently labelled known/novel structure examples.
- Cross-domain transfer and domain-specific error; never collapse the entire matrix to a single score.
- Runtime, peak RSS memory, frames/seconds decoded, analysis coverage, feature count and output size.
- Ablation of scales, Fourier bands, region relations, and learned projection/prototypes.

## Training validation and promotion

The local trainer splits by source video hash to avoid overlap leakage. Its current promotion gates measure unsupervised codebook utility only. They are operational safeguards, not accuracy certification. For a production acceptance gate, require independent annotations or a trusted external benchmark and compare the candidate to a frozen baseline before promotion.

## Report contract

Every benchmark report must state:
- source revision and feature-schema version;
- configuration, dimensions, sample rate and window policy;
- source hashes, source rights manifest and exclusions;
- exact split logic and number of independent source videos;
- per-stratum and aggregate measurements, baselines, uncertainty and failure cases;
- whether the data is synthetic or natural;
- explicit booleans for real-world evidence and state-of-the-art claim support.

Do not claim state of the art unless comparison data, split, implementation, command, environment and independent baseline are reproducible.

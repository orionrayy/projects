# Architecture — FMA Open-World Relational Core

## Invariants

1. **No required domain ontology.** A video is not required to be classified as live action, animation, fractal, art, POV, or any other category before analysis.
2. **No object detector prerequisite.** Geometric entities, semantic categories, and persistent identities are optional interpretations, not intake requirements.
3. **Space-time blocks are the primary analysis unit.** The public v0.2 analyzer computes signatures from overlapping RGB volumes; pairwise flow is not the main representation.
4. **Relations are first-class.** Every window produces fixed spatial-region nodes and relations. Similarity across temporally separated windows is reported separately from semantic identity.
5. **Learned outputs remain corpus-relative.** Anonymous prototypes and novelty ratios cannot be presented as ground-truth semantics or calibrated probabilities.
6. **Bounded, reproducible work.** Decode rate, dimensions, window length/stride, frame cap, source hash and feature schema are recorded.
7. **Claims follow evidence.** Synthetic regression passes do not prove generalization or state of the art.

## Data path

1. FFprobe establishes stream metadata and source-duration expectations. SHA-256 binds the report to the input bytes.
2. FFmpeg decodes bounded RGB24 samples at a declared rate and resolution. The decoder streams samples into a fixed-size overlapping buffer.
3. Each temporal block is analyzed at spatial scales 1×, 2× and 4×. Per-channel statistics preserve color, while gradients, orientation energy and spatial autocorrelation characterize structure without semantic labels.
4. A block-level 3D Fourier transform summarizes joint temporal/spatial frequency energy. Temporal envelopes and regional temporal spectra retain order-related evidence that a single static histogram would discard.
5. A 4×6 fixed-region field generates 24 regional descriptors. Spatial-neighbor and non-local similarity edges describe relationships between regions over the same window; they do not imply object identity.
6. Whole-window signatures are compared across intervals. Robust signature-distance candidates, recurrence relations and duplicate-frame integrity checks populate the report. Exact duplicate checks are a technical QC signal, not the primary motion model.
7. The JSON report retains signatures, scales, nodes, edges, source provenance, window coverage and explicit interpretive limits.
8. Optional local learned scoring applies the trained standardizer, denoising encoder and anonymous prototypes. The analysis itself continues to work without any trained model.

## Why this is not universal understanding yet

Hand-designed signatures create an open intake path but have finite descriptive power. Different phenomena can share similar statistics, and semantic relationships may not be recoverable from low-resolution grayscale/color samples alone. The core does not claim physical 3D motion, intent, causal explanation, persistent object identity, or accurate interpretation of every possible visual domain.

The design target is not a single “universal feature” that works perfectly. It is a substrate that can observe structure without a required ontology, expose uncertainty and allow future operators/encoders to contribute evidence without rewriting the entire control path.

## Automatic training path

The trainer uses local unlabeled videos, source hashes, video-level train/validation separation, robust median/MAD normalization, a small NumPy denoising autoencoder, and deterministic farthest-first prototypes. It outputs a candidate model and validation report. It promotes the model locally only when explicit coverage, corpus-size, holdout-quality, diversity and rights-attestation gates all pass.

No online scraping occurs. This is both a privacy boundary and a licensing boundary. Any future online dataset connector must carry per-dataset terms, checksums, permitted-use status and reproducible source manifests.

## Data contracts

Analysis report schema: fma.openworld.analysis.v0.2  
Block feature schema: fma.openworld.relational-signature.v1  
Trained model schema: fma.openworld.relational-model.v1

A signature-vector dimensionality mismatch is an error; silently scoring a vector with a different schema is forbidden. Model JSON carries an integrity digest. Per-report model annotations state that prototypes are corpus-relative and non-semantic.

## Extension rules

New feature operators must declare:
- the input domain and scale at which they operate;
- the evidence they emit, feature-schema/version identity and computational cost;
- invariances they are expected to preserve and transformations expected to change the output;
- known ambiguities and failure conditions;
- tests that can falsify their claimed utility.

Domain-specific adapters may be added, but they must not become mandatory gates for the shared open-world core.

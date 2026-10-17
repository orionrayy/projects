# Benchmark and Evidence Protocol

## P0: deterministic synthetic tests

Use generated, lossless clips with known timing and movement: moving-object reversal, full-scene pan reversal, a moving object over a globally panning textured background, static hold/repeated frames, and a one-frame global flash. Keep expected global and local motion separate in the ground-truth contract. Record generator version, exact parameters, source hash, expected interval, actual output, and test result.

Minimum checks:
- time-series timestamps are strictly increasing and within source duration;
- a moving object yields non-zero adjacent-frame change;
- a known held segment produces a measurable exact-duplicate transition ratio;
- a one-frame flash generates a localized high-change candidate;
- reversing full-scene camera motion flips the fitted affine translation direction;
- an independently moving textured object generates a localized affine-residual region while the background undergoes global pan;
- running the same fixture with the same dependencies yields the same non-model measurements;
- missing optional OpenCV is reported explicitly;
- max-frame limits cannot silently produce a complete-status report.

Synthetic scores establish software-contract correctness only. They do not establish performance on natural videos.

## P1: temporal reasoning and order sensitivity

Build an adversarial suite with, at minimum:
- original versus reversed frame order;
- original versus deterministically shuffled frame order;
- repeated/subsampled frames at several FPS values;
- controlled frame drops, jitter, scene cuts, flashes and frozen intervals;
- blur, resizing, compression, exposure shifts, camera pans and occlusion;
- multiple independently moving regions and one dominant camera move.

Report a temporal-order sensitivity gap separately from image-semantic accuracy. When the claim depends on action order, reversing/shuffling frames should materially change the relevant result. Report false positives and abstentions; do not reward confident guesses on unobservable motion.

## P2: independently licensed real datasets

Candidate categories: optical-flow ground-truth sets, video-object segmentation sets, action-localization sets, and animation/render-specific clips. Before ingesting any dataset, record a manifest with source URL, maintainer, dataset/version, file hashes, license, permitted research/commercial use, attribution rules, personal-data considerations, download date, and whether redistribution is allowed. Do not commit raw datasets or weights to this repository until their rights are verified.

Use source-defined train/validation/test partitions when available. Where custom splits are needed, split by original video/scene/source, not adjacent frames, to avoid temporal leakage. Keep benchmark configuration and threshold calibration separate from an untouched final test set.

## Metrics

| Capability | Metric |
|---|---|
| Optical flow | Endpoint error (EPE), angular error where applicable, valid-pixel coverage |
| Motion event localization | Event precision/recall/F1, start/end timestamp MAE, tolerance-banded AP |
| Temporal order | Contrast between original/reversed/shuffled outputs, direction-order accuracy on labeled cases |
| Motion segmentation | Region IoU, boundary accuracy, identity switches where applicable |
| Camera-motion estimate | Translation/rotation/affine error on synthetic or calibrated ground truth |
| Render QC | Known-defect recall, false-alarm rate, exact duplicate/freeze span localization |
| Calibration / uncertainty | Reliability diagrams, Brier/log loss where probabilities are defined, selective risk under abstention |
| Operations | Runtime, peak RAM, effective FPS, frame coverage, deterministic repeatability |

Publish per-domain results and confidence intervals, plus the simple frame-difference and Farnebäck baselines. Report mean and tail performance; never use a single aggregate score to conceal catastrophic motion failures.

## Baselines and controls

- Frame-difference-only baseline.
- OpenCV Farnebäck dense-flow baseline (if installed).
- Optional independently licensed/reproducible methods selected in a later research phase.
- Sampling-rate and resolution ablations.
- Temporal reversal/shuffle controls.
- Human-labeled audit subset with adjudication procedure and annotator agreement.

Do not compare only against screenshots, and do not claim state of the art unless the model/version, dataset version, split, commands, runtime environment, metric implementation, and independent baseline are all published.

## Benchmark result contract

Each run should emit machine-readable JSON containing:
- schema version, source revision and config hash;
- dataset manifest hash and dataset license reference;
- model/dependency versions and hardware profile;
- number of examples, exclusions and exclusion reasons;
- metrics, uncertainty intervals and per-domain stratification;
- baseline results and paired comparisons;
- errors, failure cases and known limitations;
- explicit booleans for **real_world_evidence**, **independent_test_set**, and **state_of_the_art_claim_supported**.

These flags default to false. A successful CI run does not flip them.

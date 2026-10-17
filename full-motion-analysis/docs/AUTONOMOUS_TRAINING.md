# Autonomous Local Training

## What is trainable in v0.2

The CPU-first model learns corpus-relative structure representations from unlabeled FMA signatures. It fits robust normalization, a compact PCA projection and deterministic prototypes. Each new analyzed window may then receive:
- an anonymous prototype assignment;
- a distance to the selected prototype;
- a novelty ratio relative to that prototype's training radius.

These values can help explore recurring and unfamiliar structural patterns. They are not semantic labels, calibrated probabilities, or proof that a video contains an error.

This model is a first trainable layer, not a neural foundation model. The fixed feature extractor is still hand-designed. A future self-supervised neural encoder can implement the same feature-schema / transform / evaluation contracts as an optional backend without making the baseline dependent on a large model or paid API.

## One-command workflow

~~~bash
motionlab train ./authorized-videos --output-dir ./models/fma
~~~

The trainer discovers videos recursively, calculates SHA-256, skips exact duplicates, analyzes each source, separates train and validation by whole-video hash, fits the model, computes held-out quantization and cluster-diversity summaries, and writes:
- candidate_model.json — candidate weights/centers plus integrity SHA-256;
- dataset_manifest.json — source hashes, counts, sampling coverage, source-level split and failed items;
- training_report.json — evaluation metrics and every promotion gate.

The media remains local. The command does not scrape websites, automatically download datasets, upload videos, or commit media to GitHub. Dataset fetchers must be separate, license-aware adapters with provenance and rights checks.

## Conditional autonomous promotion

~~~bash
motionlab train ./authorized-videos --output-dir ./models/fma --attest-rights --auto-promote
~~~

The rights flag is an explicit operator attestation that the local corpus may be processed. Promotion is attempted only if all gates pass:
- at least five distinct, successfully analyzed video sources;
- at least four training sources and a distinct held-out source;
- at least 95% reported analysis-time coverage where source duration is available;
- at least 5% improvement in held-out prototype quantization versus a single-centroid latent baseline;
- multiple occupied prototypes without extreme assignment collapse;
- finite model parameters and the operator rights attestation.

If a gate fails, the candidate and report are kept, but active_model.json is not overwritten. There is no “promote because the run finished” fallback.

The validation is unsupervised and measures representation/codebook utility only. For production or claims of domain independence, a labelled or independently adjudicated benchmark is still required; these gates cannot establish semantic motion accuracy.

## Data discipline

Use source-level splits to prevent overlapping windows from the same video leaking into both train and validation. Record hashes instead of absolute local paths in the manifest. Do not treat online availability as a licence grant. Keep all experiment parameters, source hashes, feature schema version and model hash with each run.

## Continued/automatic updates

Run the built-in foreground watcher when a local folder is the authorized source of new examples:

~~~bash
motionlab train ./authorized-videos --output-dir ./models/fma --watch --poll-seconds 900 --retry-seconds 21600 --attest-rights --auto-promote
~~~

The watcher fingerprints a fast inventory of relative paths, byte sizes and modification times. Content SHA-256 is still calculated during the actual training job. On a changed inventory it trains a candidate; on an unchanged successfully processed inventory it skips work. If training fails or a gate blocks promotion, retrying the same inventory is delayed by the configured retry interval. `watch_state.json` stores inventory/model hashes, last status and the last 30 attempts. The process remains in the foreground and stops with Ctrl+C; it is not a detached background service.

Do not delete the previous active model or retry promotion blindly after a failure. Keep the active model hash, candidate hash and training report as a durable checkpoint. If a process crashes during atomic file replacement, inspect the existing model hash and report before retrying. The watcher uses metadata for cheap change detection; explicitly rerun training if external tooling changes content while preserving both the size and the modification time.

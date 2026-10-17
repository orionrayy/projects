# Full Motion Analysis (FMA) — Open-World Relational Core

**Version:** 0.2.0  
**State:** foundation rewrite implemented on a draft PR; independent real-world validation is still pending.  
**Policy:** free-first, CPU-first, no LLM or paid inference API required by the baseline.

FMA is designed to inspect temporal visual structure across nirmana and abstract graphics, fractal zooms, animation, cartoons, anime, film, POV, third-person footage and everyday recordings without requiring a domain label or object detector at intake.

This is an engineering target, not a claim that the current implementation semantically understands every possible domain. The v0.2 core supplies domain-neutral measurements and a local unsupervised learning path; cross-domain accuracy must be established by evaluation.

## Foundation shift

The public analyzer now analyzes overlapping RGB space-time volumes. It does **not** use frame-pair optical flow as the primary representation. A decoded frame is still a source sample, but the principal signature summarizes a temporal block across multiple spatial scales.

The CPU-first signature combines:
- per-channel color distribution and appearance statistics;
- multi-scale spatial gradients, orientation distributions, and autocorrelation;
- temporal envelopes and temporal-frequency bands over the entire block;
- 3D spatiotemporal Fourier energy summarized into temporal × spatial-frequency bands;
- a 4×6 fixed-region relational field whose nodes describe whole-window regional statistics, not object identities;
- non-local regional similarity relations and recurrence candidates across different windows;
- robustly detected changes between whole-window signatures, with measurements and explicit interpretation limits.

Feature extraction does not require object identity, pose, a fixed class ontology, a neural network, OpenCV, or a model-provider API. Color is preserved during decode. Sampling remains bounded and declared. Sparse sampling, low resolution, aliasing, occlusion, and ambiguity can still hide important information.

## Install

Requirements: Python 3.11+, FFmpeg, FFprobe, NumPy.

~~~bash
python -m pip install -e .
~~~

Optional local MCP support:

~~~bash
python -m pip install -e ".[mcp]"
~~~

## Analyze a video

~~~bash
motionlab analyze input.mp4 --output reports/input-analysis.json
~~~

A CPU-light corpus default is 160×90 at up to 30 sampled frames per second, with 16-frame windows and stride 8. Increase resolution when small structures matter:

~~~bash
motionlab analyze input.mp4 --width 320 --height 180 --max-fps 15 --window-frames 24 --window-stride 8 --output reports/detail.json
~~~

The report includes the source SHA-256, actual frame coverage, feature schema, space-time windows, region nodes/edges, cross-window recurrence candidates, events and interpretation limits.

## Train automatically from an unlabeled local corpus

No hand-labelled event data or LLM is required for the initial relational model. Provide local videos you are allowed to process:

~~~bash
motionlab train ./my-video-corpus --output-dir ./models/fma --max-fps 8 --encoder-epochs 8 --encoder-hidden-dim 48
~~~

The trainer:
1. discovers supported local videos and deduplicates exact files by SHA-256;
2. analyzes each source with the same space-time signature engine;
3. splits by **source video hash**, never by overlapping windows from the same video;
4. fits robust normalization, a small denoising autoencoder trained with NumPy and deterministic anonymous structure prototypes;
5. evaluates held-out quantization and prototype occupancy;
6. writes candidate_model.json, dataset_manifest.json, and training_report.json.

Request gated local promotion only when you can attest that all inputs may be processed:

~~~bash
motionlab train ./my-video-corpus --output-dir ./models/fma --attest-rights --auto-promote
~~~

For autonomous local retraining when the corpus changes, keep a foreground watcher running:

~~~bash
motionlab train ./my-video-corpus --output-dir ./models/fma --watch --poll-seconds 900 --retry-seconds 21600 --attest-rights --auto-promote
~~~

The watcher writes a durable watch checkpoint, skips an unchanged corpus after a successful candidate/promote run, and retries a failed or gated run no more often than the configured retry interval unless the inventory changes. Stop it with Ctrl+C. It does not detach itself as a background service or fetch new media.

Promotion is conditional, not guaranteed. The default gates require at least five distinct videos, at least four training videos, a held-out video split, sufficient data coverage, a measurable held-out improvement, prototype diversity, decreasing clean reconstruction loss, and the rights attestation. Otherwise the candidate remains unpromoted and the report records the failed gate.

Apply an accepted model:

~~~bash
motionlab analyze input.mp4 --model ./models/fma/active_model.json --output reports/scored.json
~~~

The learned prototype IDs are anonymous patterns relative to a local corpus. Novelty scores are distance ratios, **not** semantic labels, calibrated probabilities, anomaly truth, or proof of generalization.

## MCP

The local stdio MCP server exposes metadata inspection, relational analysis, and FFmpeg render audit. Configure narrow MOTION_ALLOWED_ROOTS; a supplied model path must also be within an allowed root. The tool response limits embedded timeline windows and writes the complete report locally.

~~~bash
export MOTION_ALLOWED_ROOTS="$HOME/Videos:$HOME/Downloads:$HOME/render-outputs"
export MOTION_REPORT_DIR="$HOME/.motion-evidence-lab/reports"
python mcp_server.py
~~~

Remote Streamable HTTP source and Render packaging remain separate from deployment. A source file or passing CI does not mean a remote service is live or connected to ChatGPT.

## Current limitations

- The observation descriptors remain hand-designed; the trainable layer optimizes a small denoising encoder over those descriptors. It is not an end-to-end raw-video foundation encoder and it does not automatically learn human semantics.
- No accuracy on arbitrary domains, novel phenomena, physical motion, semantic action, 3D reconstruction, or causal explanation is established.
- A region node is a fixed image region summarized over a time block, not a persistent object or segmentation.
- The training gate is a cautious unsupervised representation-quality gate. It does not substitute for labelled ground-truth benchmarks or human acceptance.
- The local-corpus trainer does not download media automatically. Dataset acquisition requires provenance and licence review first.
- The legacy pairwise implementation is preserved in motionlab/legacy_analysis.py for comparison; motionlab/metrics.py remains a baseline module but is not used by the v0.2 analysis core.

See docs/OPEN_WORLD_FOUNDATION.md, docs/AUTONOMOUS_TRAINING.md, docs/ARCHITECTURE.md, docs/BENCHMARK_PROTOCOL.md, docs/MCP_INTEGRATION.md, and PROJECT_STATUS.md.

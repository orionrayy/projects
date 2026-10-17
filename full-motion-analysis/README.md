# Full Motion Analysis (FMA)

**Project code:** FMA / Motion Evidence Lab  
**Status:** v0.1 bootstrap — research prototype, not yet a validated motion-understanding system  
**Design target:** reproducible, evidence-grounded temporal analysis of video, including audits of FFmpeg-rendered animation  
**Operating policy:** free-first, CPU-first baseline, optional acceleration, no paid API required

## Why this project exists

Many video interfaces answer from sparse visual samples. FMA is designed to make temporal evidence explicit: what changed between observations, how dense image motion behaves, which time-localized events are candidates, how much of the source timeline was processed, and which conclusions remain unobservable.

FMA is **not** just an object tracker. Its planned evidence stack combines frame-difference measurements, dense optical flow, camera-motion indicators, temporal event candidates, integrity checks, uncertainty/limitation reporting, and adversarial tests that check whether a system actually depends on temporal order. Object identity, segmentation, causal interpretation, physical-world measurements, and learned action recognition are separate capabilities and are not claimed as solved by this bootstrap.

## Current v0.1 scope

- Probe source media with FFprobe and decode a timestamped grayscale stream using FFmpeg.
- Measure per-interval pixel change and, when OpenCV is installed, dense Farnebäck optical flow, a 4×6 spatial motion grid, moving-pixel ratio, magnitude quantiles, median global translation, residual local flow, direction, and flow coherence.
- Emit evidence-backed candidates for scene transitions, motion onset/bursts, direction reversals, repeated-frame runs, and possible flashes.
- Audit FFmpeg exports for decode coverage, dimensions/FPS/duration, exact duplicate frames, black frames, missing audio, and temporal discontinuities.
- Generate deterministic synthetic clips with known motion / freeze / flash conditions and exercise them in tests and CI.
- Expose local file analysis via an MCP server using the official Python SDK, plus a local CLI.
- Persist a versioned JSON report with SHA-256, tool versions, sampling settings, time series, event evidence, limitations, and QC findings.

The core intentionally has no Torch, cloud inference, or paid provider requirement. NumPy is the only baseline Python runtime dependency. The grid retains spatial variation that a single global flow vector would erase; grid cells are spatial regions, not persistent object identities or object segmentation. OpenCV is optional and provides dense optical flow; without it, the report marks the flow lane unavailable instead of pretending frame differencing is full motion estimation.

## Quick start

Requirements: Python 3.11+, FFmpeg and FFprobe on PATH.

~~~bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install -e ".[vision,mcp]"
python -m motionlab.cli analyze path/to/video.mp4 --output reports/analysis.json
python -m motionlab.cli audit path/to/render.mp4 --require-audio --output reports/render-audit.json
python -m unittest discover -s tests -v
python benchmarks/run_synthetic_benchmark.py --output-dir reports/synthetic-benchmark
~~~

MCP local server (stdio):

~~~bash
python mcp_server.py
~~~

Read docs/MCP_INTEGRATION.md before registering the server in an MCP host. Local MCP tools can read only paths under configured allowed roots. Do not expose a local-path server to the public internet.

## Example output categories

Every result separates:
- **Measurement:** sampled frames, pixel-difference signal, image-plane flow vectors, exact duplicate-frame spans, media metadata.
- **Candidate event:** a thresholded temporal event with timestamp, source frame index, observed measurements, and rule identifier.
- **Interpretation limit:** what the measurements cannot establish (for example, real-world velocity, intent, object identity, or physical causation).
- **QC finding:** a configurable render acceptance warning/failure, not a semantic truth judgement.

Pixel motion is measured in the analyzed image plane. Without camera calibration, geometry, scale, and scene assumptions, it is not a physical-world speed measurement. Median flow is only a camera-translation proxy under a static-background / majority-background assumption.

## Roadmap

1. **P0 — evidence contract:** deterministic decode, explicit sampling, optical-flow lane, JSON evidence schema, synthetic regression tests, FFmpeg render audit, MCP stdio entry point.
2. **P1 — benchmark discipline:** timestamp localization error, motion-event precision/recall, flow error against known synthetic ground truth, temporal-order permutation tests, repeatability and resource profiling.
3. **P2 — richer scene motion:** optional segmentation-conditioned flow, camera-motion compensation diagnostics, articulated pose / deformation adapters, occlusion and uncertainty handling.
4. **P3 — motion semantics:** optional video action models behind a model adapter contract; evaluated against temporal adversarial tests, not only image-caption accuracy.
5. **P4 — FFmpeg feedback loop:** compare intended scene/keyframe manifest with rendered output, detect pacing/freeze/flash/duplicate frames, compare expected audio coverage and actual stream metadata, attach frame/time evidence.
6. **P5 — MCP deployment:** secure upload/job API and remotely hosted Streamable HTTP MCP deployment after storage, authentication, isolation, and budget boundaries are specified.

Each phase is gated on tests and evidence from the previous one. No phase is considered complete just because code exists.

## Claims policy

The project aims to be highly competitive and distinct, but does not claim to be “the world's first,” “#1,” causally omniscient, or state of the art without an independently reproducible comparison. Synthetic tests validate instrumentation and code contracts; they do not establish real-world generalization. Benchmark dataset licenses and provenance must be checked before download or redistribution.

See docs/ARCHITECTURE.md, docs/BENCHMARK_PROTOCOL.md, docs/MCP_INTEGRATION.md, docs/THREAT_MODEL.md, and PROJECT_STATUS.md.

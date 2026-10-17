# Architecture

## Data path

1. **Intake / provenance:** resolve a local file, inspect streams with FFprobe, compute SHA-256, and record FFmpeg/FFprobe/Python/NumPy/OpenCV versions.
2. **Bounded decode:** FFmpeg decodes a grayscale stream at a declared analysis rate and dimensions. Frames are streamed one at a time; a frame cap prevents unbounded memory/time.
3. **Observable measurements:** each adjacent pair produces normalized mean absolute difference, changed-pixel ratio, histogram distance, difference centroid, and (when available) dense optical flow.
4. **Camera/scene-motion decomposition:** report the median-flow translation proxy, fit a robust global partial-affine transform with RANSAC when supported, and quantify residual dense flow. This separates a dominant image-plane transform from unexplained local motion without asserting object identity or physical causation.
5. **Spatial flow field:** summarize dense flow in a fixed 4×6 image grid with direction, magnitude quantiles, moving-pixel occupancy and coherence. These regions preserve multi-zone motion evidence that a single global vector erases; they are not stable object instances.
6. **Temporal event proposals:** transparent heuristics emit timestamped candidates with rule IDs and measurements. They do not emit causal ground truth.
7. **Render QC:** dimensions, rate, duration, decode coverage, exact duplicate frames, near-black ratio, and optional audio presence are compared with a configurable delivery contract.
8. **Report:** a versioned JSON result stores a downsampled time series while preserving source hash, sampling parameters, events, and interpretive limitations.
9. **Interfaces:** CLI and local MCP tools call the same Python functions, avoiding divergent analysis logic.

## Design principles

- **Evidence before narrative:** every candidate event must cite frame index, timestamp, rule identifier, and measurements.
- **Temporal coverage is a first-class output:** a result with capped or sparse sampling must say so.
- **Fail visibly:** missing OpenCV means optical flow is unavailable, not that frame difference has become optical flow.
- **Bounded resources:** FFmpeg uses streaming pipes, modest analysis dimensions, one decode thread, and a configurable frame ceiling.
- **Objective proxies are not omniscience:** image-plane motion does not reveal physical distance, intent, object identity, or causality without additional evidence and assumptions.
- **Adapters, not dependency sprawl:** heavy learned models stay optional and later must implement a narrow, testable adapter interface.

## Planned adapter contracts

Later phases should add independent adapters rather than coupling the base pipeline to a single vendor/model:

- **Segmentation-conditioned motion:** mask/instance identity, per-mask flow, occlusion state, confidence and track continuity.
- **Camera motion:** global affine/homography estimation with fit residuals and explicit failure states; compare against median-flow proxy.
- **Pose/deformation:** articulated keypoints and local motion for humans/animals/rigs, with visibility and keypoint confidence.
- **Action semantics:** temporal model produces labels over intervals, model/version provenance, calibration, supporting frames, alternative hypotheses, and abstention.
- **Expected-versus-rendered FFmpeg audit:** consume an intended scene/keyframe manifest and compare object regions, timing windows, motion envelopes, caption bounds, and audio cue windows with decoded output.

## Why one VLM is not the architecture

An image/video-language model may provide useful semantics, but it can hallucinate transitions that were not observed. FMA's measurement and QC layers are model-independent and should be run even if an optional semantic model is later added. A semantic layer must not overwrite measured timestamps or evidence.

# Project Status and Checkpoint

Updated: 2026-10-18  
Repository: orionrayy/projects  
Project root: full-motion-analysis/  
Branch: feat/full-motion-analysis-v0-1  
Pull request: https://github.com/orionrayy/projects/pull/1 (draft; not merged)

## Current release state

**Phase:** P0 motion-evidence core validated on synthetic ground truth; P1 real-world evaluation not started  
**Production readiness:** NO  
**State-of-the-art / world's-first claim supported:** NO  
**Real-world benchmark evidence:** NOT ESTABLISHED  
**Semantic action understanding, persistent object identity, 3D motion, physical-world velocity and causal inference:** NOT CLAIMED AS SOLVED  
**Local MCP:** implemented (stdio)  
**Remote MCP:** source, Dockerfile and Render Blueprint implemented; deployment not created  
**ChatGPT connector attached:** NO  
**Paid inference API required by baseline:** NO

## Implemented capabilities

- FFprobe stream metadata, SHA-256 provenance, bounded FFmpeg streaming decode and explicit sampling-rate/coverage reporting.
- Adjacent-frame pixel-change measurements plus optional dense Farnebäck optical flow.
- Spatial 4×6 flow evidence field and robust RANSAC partial-affine transform estimates: image-plane translation, rotation, scale, inlier ratio, residual median/p90.
- Affine-compensated local residual motion and connected local-motion-region candidates. These indicate localized motion not explained by the dominant fitted image-plane transform, not persistent object identities or semantic actions.
- Timestamped heuristic candidates for scene transitions, motion onset/bursts, direction reversal, repeated-frame runs and possible flashes. Candidates retain measurements and limitations.
- FFmpeg render QC for dimensions, FPS, duration, decode coverage, repeated frames, near-black frames, possible freeze/flash and a configurable required-audio stream.
- Local CLI, local stdio MCP tools with allowed-root path policy, and a remote Streamable HTTP MCP server with bearer auth, one-use upload tickets, streamed upload size cap, media validation, concurrency limit and paginated reports.
- Docker packaging, free-plan Render Blueprint, dataset licence registry, synthetic benchmark runner and GitHub Actions CI.

## Validation checkpoint

GitHub Actions run [39056780459](https://github.com/orionrayy/projects/actions/runs/39056780459) passed after adding the mixed camera/object motion scenario and remote bearer-auth contract tests.

Measured result from the hosted logs:
- 20 unit/integration tests passed.
- 8 synthetic benchmark checks passed: observed movement, monotonic timestamps, repeated-frame freeze, flash candidate, spatial flow grid, affine-fit availability, known global-pan direction reversal, and detection of an independent object-motion region during a global camera pan.
- No \`ResourceWarning\` entries were present in the retrieved run log.

This validates software contracts on synthetic inputs. It does **not** measure performance on natural videos or prove novelty, production readiness, or state of the art.

Earlier passing runs:
- [39055664706](https://github.com/orionrayy/projects/actions/runs/39055664706): affine/global-pan revision.
- [39055754870](https://github.com/orionrayy/projects/actions/runs/39055754870): benchmark registry and manifest.
- [39056485897](https://github.com/orionrayy/projects/actions/runs/39056485897): MCP SDK v1/v2 compatibility.

## Acceptance gates

| Gate | Evidence required | State |
|---|---|---|
| Media intake/decode | FFprobe metadata, decoded frame counts, frame cap and sampling coverage | Implemented; synthetic/integration tested |
| Motion field | Dense flow, spatial grid, global transform and affine-compensated residual evidence | Implemented; synthetic tested |
| Local motion regions | Known object motion localized after global camera-pan compensation | Synthetic scenario passes; natural-video validity untested |
| Event localization | Timestamped candidates with rule IDs, measurement links and error/false-positive estimates | Heuristic candidates implemented; real-world calibration pending |
| Temporal-order sensitivity | Original/reversed/shuffled comparisons on labeled temporal tasks | Planned for P1 |
| FFmpeg release gate | Technical output expectations plus defect precision/recall on an annotated render set | Basic technical checks implemented; real-world calibration pending |
| Real-world benchmark | Licensed dataset manifests, untouched splits, baselines, confidence intervals and failure cases | Not started; dataset candidates registered only |
| Remote security | Deployment smoke tests, auth verification, upload TTL/quota/cleanup, isolated decoder behaviour | Unit contract tests pass; not deployed or end-to-end tested |
| ChatGPT integration | Supported workspace, deployed HTTPS endpoint, credential configuration, real video handoff | Not connected; requires user approval for Render workspace/deployment |

## Real-world dataset policy

Candidate sources are listed in \`benchmarks/DATASET_REGISTRY.md\` (MPI Sintel, KITTI Flow, DAVIS and a temporal-order benchmark). No dataset media has been downloaded, rights-reviewed, or benchmarked yet. Public accessibility is not treated as permission for commercial use or redistribution. Every ingest is gated by \`benchmarks/dataset_manifest.template.json\`.

## Known limitations

- The baseline is classical image-plane motion estimation plus transparent heuristics; it does not yet perform persistent object segmentation, articulated pose/deformation reconstruction, learned temporal action recognition, 3D scene recovery, or causal reasoning.
- Optical flow can fail under blur, low texture, occlusion, exposure changes, large displacement, rolling shutter and compression.
- The global affine model can fail with parallax, strong non-rigid scenes, large independent objects or dominant foreground motion. Residual regions can be false positives and can fragment as objects cross grid cells.
- Downsampling to 320×180 and capped frame sampling can miss small/fast motion. Reported pixel/frame units are not physical-world velocity.
- A technical render pass does not certify aesthetics, anatomy, narrative continuity, text readability, educational correctness, audio intelligibility or lip sync.
- Synthetic CI is a regression gate, not a substitute for independent natural-video benchmarks, labeled test sets, and human review.

## Remote MCP deployment and privacy

Remote source exposes an authenticated MCP endpoint and separate upload-ticket page. The endpoint is **not live**. A free-plan Render Blueprint is prepared but has not been deployed. Free instances can sleep and use ephemeral storage; temporary videos may disappear before their nominal retention window after a restart or redeploy.

The upload flow is intentional: the MCP tool returns a one-use, expiring URL; the user selects the video in the browser and then passes the resulting opaque upload ID to the analysis tool. MCP does not automatically forward arbitrary video attachment bytes to a different server.

Current ChatGPT documentation does not list Go for full custom MCP server connections. A deployed endpoint therefore cannot be presumed usable from this ChatGPT Go session; check current plan/workspace support before relying on it. The endpoint can be used by a compatible MCP client with Streamable HTTP and bearer auth.

## Next gates

1. Confirm the latest source revision's CI, then keep this draft PR open until remote deployment settings are approved.
2. Build temporal-order reversal/shuffle metrics, sampled-frame ablations, and motion-timestamp localization tests.
3. Acquire only rights-cleared data, starting with a small reproducible subset, and report Farnebäck/frame-difference baselines.
4. Test remote MCP through an actual deployed endpoint only after workspace approval; verify auth, upload limits, expiry, cleanup and end-to-end video handoff.
5. Advance claims only when independently reproducible evidence supports them.

# Project Status and Checkpoint

Updated: 2026-10-18  
Repository: orionrayy/projects  
Project root: full-motion-analysis/  
Branch: feat/full-motion-analysis-v0-1

## Current release state

**Phase:** P0 bootstrap in implementation  
**Production readiness:** NO  
**Real-world benchmark claim:** NOT ESTABLISHED  
**Semantic / causal action understanding:** NOT IMPLEMENTED  
**Remote MCP upload endpoint:** NOT IMPLEMENTED  
**ChatGPT connector attached:** NO — a repository commit alone cannot register a custom MCP server in a ChatGPT workspace  
**Paid services:** none required by the current architecture

## Acceptance gates

| Gate | Required evidence | State at bootstrap |
|---|---|---|
| Decode correctness | FFprobe metadata, complete/incomplete decode status, frame timestamp accounting | In implementation |
| Motion measurement | Frame-difference series plus optional dense optical flow with explicit coordinate units | In implementation |
| Camera-motion assumptions | Median-flow estimate and documented static-background limitation | In implementation |
| Event localization | Timestamped event candidates linked to raw measurements and rule IDs | In implementation |
| Temporal-order sensitivity | Forward/reverse/shuffled synthetic challenge; report metric changes | Planned for P1 |
| FFmpeg render QC | Dimensions/FPS/duration/audio/duplicate/freeze/black/flash checks | In implementation |
| Reproducibility | Input SHA-256, tool/dependency versions, deterministic synthetic fixtures | In implementation |
| MCP contract | Safe local-root validation, probe/analyze/audit tools, stdio transport | In implementation |
| Real-world benchmark | Licensed datasets, baselines, split protocol, error intervals, independent run | Not started |
| Remote MCP | Authenticated upload or object storage, quotas, retention, SSRF isolation, remote endpoint | Not started |

## Success criteria for P0

1. Tests can run locally and in GitHub Actions using free hosted CI minutes within normal repository limits.
2. Synthetic ground-truth clips establish that motion, frozen spans, and abrupt global changes are measurable and timestamped.
3. Reports never present image-plane pixel velocity as real-world speed or a threshold event as confirmed causality.
4. Optional OpenCV failure is visible in report provenance and does not silently mislabel a fallback result as optical flow.
5. MCP file access is constrained to allowed roots; no unauthenticated remote server or arbitrary URL fetch is exposed.
6. FFmpeg audit has explicit warning/failure policy and can treat missing audio as a release blocker when requested.
7. Every quality claim is tied to a command, test report, artifact hash, and exact source revision.

## Known limitations

- Sparse or reduced-resolution sampling can miss events shorter than the effective frame interval.
- Dense optical flow can fail under blur, low texture, occlusion, lighting changes, rolling shutter, and large displacements.
- Median-flow camera-motion estimates assume that background/static pixels dominate.
- A static scene and a frozen render can look alike; exact duplicate spans are evidence, not proof of a bug.
- Frame-level motion is not equivalent to identifying an object, inferring intent, recovering 3D motion, or explaining physical cause.
- Thresholds are starting heuristics. They must be calibrated and stress-tested before being used as acceptance gates.
- CI synthetic clips are instrumentation tests, not a substitute for real-world datasets, human review, or independent benchmark results.

## Next checkpoint

After source files land: run unit/integration tests, inspect the CI run on the PR branch, fix failures without weakening contracts, write measured results here, and only then advance to P1. Do not record test success before seeing the actual output.

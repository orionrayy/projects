# Real-Video Dataset Registry

This registry identifies candidates for objective motion evaluation. A public download page is **not** by itself a licence grant. No dataset or extracted media may be mirrored in this repository until the exact archive terms, permitted use, attribution, privacy restrictions, and redistribution rules have been reviewed and recorded.

## Candidate registry

| Dataset | Evidence it can provide | Official source | Constraints before ingestion |
|---|---|---|---|
| MPI Sintel Flow | Long sequences, large displacement, motion blur, defocus, atmospheric effects, ground-truth optical flow. Official page lists 23 training sequences and 12 test sequences; complete archive is 5.3 GB. | https://sintel.is.tue.mpg.de/ and https://sintel.is.tue.mpg.de/downloads | Inspect the README and terms in the exact archive; record licence/version and whether evaluation-only test data can be used. It is rendered animation, not natural-camera footage. |
| KITTI Flow 2012 | Real driving scenes with a moving camera and predominantly static environment; 194 training and 195 test scenes per the official benchmark page. | https://www.cvlibs.net/datasets/kitti/eval_flow.php | Review official data terms for the exact download/version, non-commercial limitations if applicable, citation, and whether test ground truth is available. |
| KITTI Flow 2015 | Real driving scenes with moving camera and moving objects; 200 training and 200 test scenes per the official benchmark page. | https://www.cvlibs.net/datasets/kitti/eval_flow.php | Same restrictions as above. Keep 2012 and 2015 protocols distinct; don't leak scenes across calibration/test. |
| DAVIS 2017 | Video object masks / multi-object spatiotemporal segmentation and identity consistency. | https://davischallenge.org/davis2017/code.html and https://davischallenge.org/ | Review exact image/video/annotation terms and each component's licence. Its object segmentation labels are not optical-flow ground truth. |
| VBenchComp | Research protocol for separating temporal questions from image-only/knowledge-based questions and testing sensitivity to shuffled frame order. | https://arxiv.org/abs/2505.14321 | Read the paper and implementation/data terms before reusing any benchmark prompts, code or derived annotations. Use the temporal-order idea as a diagnostic even if no assets are redistributed. |

## Required licence/provenance record

For each ingested dataset or subset, create a manifest containing:
- maintainer and official canonical URL;
- exact dataset/archive version and download date;
- archive SHA-256 and file inventory hash;
- explicit licence identifier or archived terms reference;
- commercial/research-use status and redistribution permission;
- required citation and attribution;
- personal-data/consent notes and any usage restrictions;
- approved subset IDs, exclusions, and reason;
- source-defined split or scene-level custom split rationale.

Unknown licence fields are blockers, not implicit permission. Do not upload large raw datasets or checkpoints to GitHub. Use ephemeral/cache storage in CI where licence and resource policy allow it, and publish hashes + benchmark reports instead of media.

## Evaluation design

Do not collapse every capability into one aggregate score. Keep the following tracks separate:

1. **Dense-flow accuracy:** EPE / angular error on ground-truth-valid pixels, stratified by motion magnitude and occlusion.
2. **Camera-vs-local motion decomposition:** global transform error and residual-motion detection on known camera movement, independently moving regions, and camera shake.
3. **Temporal event localization:** event precision/recall/F1, timestamp error and duration overlap at several FPS/resolution settings.
4. **Video instance continuity:** mask IoU and temporal identity consistency where segmentation labels exist; tracking scores do not replace motion-field scores.
5. **Temporal-order stress tests:** original/reversed/shuffled sequences with expected directional change; score abstention and calibration as well as accuracy.
6. **FFmpeg animation audit:** defect recall / false alarm and timestamp localization for known render failures, plus separate human review of story, geometry, readable text and audio.
7. **Robustness:** blur, illumination, compression, rolling shutter, occlusion, cuts, repeated frames and out-of-domain scene type.

Use a distinct validation set for threshold calibration and untouched held-out source videos for final evaluation. Report per-domain results, confidence intervals and failure cases. P0 synthetic checks are not real-world evidence.

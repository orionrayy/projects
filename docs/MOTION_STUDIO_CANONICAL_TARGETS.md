# Motion Studio — Canonical Product Targets

Last reconciled: 2026-10-20 (Asia/Jakarta). Canonical repo: https://github.com/orionrayy/projects.
Current engineering candidate: Motion Studio v0.9.1 damped-human-gait checkpoint on branch motion-studio-v0.9.1-damped-human-gait. v0.9.0 side-profile render and tests passed; v0.9.1 amplitude damping, C2 gait continuity and stricter temporal gates are pending.
Status rule: prototype presence, passing geometry tests, rendered evidence and human visual acceptance are different states.

## Mission
Build a usable 2D character-animation studio and video pipeline whose motion is weight-bearing, coherent, synchronized, repeatable and reviewable at full speed. Prefer free-first hosted Linux/GitHub Actions. Do not assume Windows, a local GPU, paid APIs or local rendering. Never bypass host/tool safety or report success without independent evidence.

## Character setup, rigging and deformation — required
- Character setup and bone-rigging interface; editable hierarchical skeleton with root, pelvis, spine/torso/chest, neck/head, clavicles/shoulders, upper/lower arms, wrists/hands/fingers, hips, upper/lower legs, knees, ankles, feet and toes.
- Bone constraints and limits: rotation/range limits, stable bend direction/pole targets, reachability clamps, contact-aware limits and visible diagnostics.
- Pivot-point/joint placement tools, bone mirroring/symmetry, rig validation and proportion/silhouette controls.
- Weight painting, per-bone influence inspection and stable mesh deformation without tearing, collapsing or detached joints.
- IK (inverse kinematics) vs FK (forward kinematics), switching/blending, pole controls and a general authoring UI.
Current status: v0.8.x contains a procedural 2D two-bone IK/pole-target solver. A complete interactive rig editor, general FK/IK authoring, weight painting, mesh deformation and mirror UI are not verified as delivered.

## Motion authoring and quality — required
- Walk cycles and run cycles, cadence/stride/stance-swing tuning, phase offsets, root motion, speed changes, turns, start/stop and transitions.
- Planted-foot locking, heel-toe roll, ground contact, foot-slip/penetration detection and continuous ankle/knee motion.
- Phase-coupled full-body action: pelvis, torso/spine, shoulders, arms, neck and head must coordinate rather than animate independently.
- Arm counter-swing; independent arm/hand/finger movement when not constrained; prop grasp, carry, push, pull, release and entry/exit continuity.
- Overlapping action, anticipation, follow-through, secondary motion, inertia, gravity, balance and visible weight transfer.
- Keyframes/interpolation, timing curves, action clips, pose continuity, smooth gait transitions and repeatable deterministic evaluation.
- Head counter-rotation, gaze and facial orientation must visibly affect rendered geometry, not remain unused diagnostic values.
- Stylized anatomy is acceptable; incoherent proportions, silhouette crossings, sliding feet, snapping joints and hand/prop separation are not.
Current status: deterministic procedural gait and carry/free-arm profiles exist. v0.8.1 adds rendering evidence and applies the existing head-angle channel to the visible SVG head. Foot silhouettes/crossing, gait weight, synchronization and artistic naturalness remain unaccepted until the actual artifacts are reviewed at full speed.

## Editing, timeline and production workflow — required
- Character/scene editor, project save/load, asset import/export, deterministic project manifest and undo/redo.
- Timeline scrub/playback, time/frame display, keyframes, curves, layered tracks, action clips and editable scene duration.
- Camera/framing/composition, visual depth, background/foreground separation, shading/shadows, scene transitions and render-quality controls.
- Preview vs final render, resumable scene-by-scene pipeline, progress/reporting and reproducible generation.
- Multi-track NLE-style sequencing integrated with the same validated project state.
Current status: v0.8.1 is a procedural review harness, not an interactive editor or full NLE.

## Audio, captions and deliverables — required
- Audio mixer/timeline for narration, dialogue, ambience, music and SFX; clear voice/source provenance and per-scene fallback status.
- Loudness normalization, ducking, timing checks, audio-stream validation and no silent output mislabeled as narrated final.
- Smart caption editor, subtitle safe-area/timing checks, SRT and transcript exports.
- FFmpeg output validation for codec, resolution, frame rate, frame count, duration, audio channels/sample rate and signal levels.
- MP4, contact sheets, machine-readable manifest, logs, checksums and evidence reports.
Current status: separate CFG Explainer V4 workflow has reported a successful 240-second artifact with audio. Integration with v0.8.1's character solver is not verified; v0.8.1 previews are 8-second silent proof samples.

## Full Motion Analysis / motion QA — required research subsystem
- Analyze motion as a continuous space-time signal, not only isolated screenshots or unrelated frame pairs; track temporal consistency, regional/object relations, camera movement, occlusion, scale and uncertainty.
- Benchmark daily life, POV, third-person footage, film, anime/cartoon, abstract/nirmana motion and Mandelbrot/fractal zoom; retain deterministic baselines and reproducible video-level splits.
- Self-supervised training must have model/source provenance, held-out evaluation, integrity checks, guarded promotion and an insufficient-data no-promotion gate.
- Synthetic metrics do not prove universal understanding or state-of-the-art status. Real-world cross-domain evidence is required.
Current status: FMA v0.2 is a research proposal/prototype with hand-designed signatures and no established universal performance.

## Asset provenance and operating policy
- Asset rights/license catalog, attribution, source provenance, content hashes and restrictions.
- Record code/solver version, scene configuration, fonts/tools/FFmpeg version, render parameters, output hashes and validation outcomes.
- Free-first, bounded resource use, reusable deterministic outputs, explicit fallbacks and expiry-aware artifact links.
- External side effects must be authorized, idempotent and verified. Safety layers must not be bypassed.

## Quality gates
1. Regression tests for IK/FK, limits, finite values, gait phase boundaries, contact constraints, invalid input and trajectory continuity.
2. Per-frame metrics for bone length, foot drift, ground penetration, bilateral separation, joint velocity/acceleration spikes, prop contact, head/torso motion and pose continuity.
3. Hosted render of every profile under review, MP4 metadata probes and contact sheets; verify complete frame count, not just successful process exit.
4. Human full-speed review for leg crossing/sliding, weight, body synchronization, hand/prop contact, anticipation/overlap, start/end continuity and visual style.
5. Geometry tests are necessary but cannot declare naturalness. Keep human acceptance pending until reviewed.
6. Browser-versus-FFmpeg parity and full-film integration are separate validation gates.
7. A short rig preview is not the full 240-second film.

## Next stages
- Stage 5 / v0.8.1: rendered carry/free-arm previews, contact sheets and JSON geometry reports; hosted render CI passed and both contact sheets were inspected. Human acceptance remains pending. The review found an overly acute free-arm pose, weak torso/head readability and narrow projected foot separation.
- Stage 6 / v0.8.2: tuned torso/head coupling, free-arm trajectory, basket response, projected leg separation and silhouette; added quantitative regression gates. Hosted CI passed on commit `e36fd96e8a30c1699216a02e585d57b0332afd5b`, and the 8-second carry/free artifacts were verified as H.264 1280x720/24fps/192 frames with geometry reports. Contact sheets show clearer leg separation and more readable torso/head response, but the animation remains schematic; naturalness, full-speed acceptance, browser/FFmpeg parity and 240-second film integration remain unaccepted.
- Stage 7 / v0.8.3: add per-frame displacement/acceleration diagnostics for pelvis, chest, head, elbows, wrists, knees and feet; stance-foot drift measurement; and contact-state transition counts. Hosted test/render/upload workflow passed on head 7a6eaa28659a148593bf6d46198cf95407de737e. Both carry/free output MP4s and 4-fps contact sheets were generated; temporal metrics include stance drift at approximately 1.14e-13 px/frame and maximum joint acceleration at 7.58 px/frame². Human naturalness remains pending.
- Stage 8 / v0.8.4: fix scene semantics by hiding the unheld basket in free-arm mode and add a small phase-lagged basket tilt for carry mode. Hosted interaction workflow passed on head f5a95311e442356490555ab200bbe28c8f49f4b6; carry tilt range is 5.16 degrees and wrist-to-handle contact error remains 0. This is a procedural response, not full rigid-body physics.
- Stage 9 / v0.8.5: improve head/torso/neck ratios, distinguish visual pelvis width from projected leg depth, and replace line-only limbs with tapered silhouettes. Hosted workflow passed at commit a335a6c6ae53aa3434fed26e2e946a90667cd2ef; full-speed visual review remains pending.
- Stage 9b / v0.8.6 candidate: introduce curved limb contours with subtle mid-segment bulges, less prominent integrated knee/elbow marks, sleeve cuffs, and clearer palm/thumb/finger contours without changing the stable locomotion solver. CI and full-speed visual acceptance remain pending.
- Stage 9: compare v0.8.3/v0.8.4 MP4s and contact sheets, and review v0.8.5 anatomy at full speed. Fix foot-crossing/sliding, body proportions, weight transfer, upper-body synchronization and prop-contact defects with regression tests.
- Stage 10: editable skeleton hierarchy, joint constraints, pivots, mirroring and IK/FK authoring.
- Stage 11: weight painting/deformation, complete walk/run profiles, transitions, overlapping and secondary action.
- Stage 12: timeline, layered clips, camera/compositing, audio mixer, subtitles and rights-aware assets.
- Stage 13: integrate reviewed character animation into the 240-second FFmpeg pipeline and the separate motion-analysis QA loop.
- Stage 14: production hardening, renderer parity, performance/accessibility, import/export and cross-domain test corpus.

Version numbers are checkpoints, not evidence of quality. When a gate fails, fix the earliest failing layer before adding a new version.


## Stage 9 anatomy/proportion review checkpoint — 2026-10-20

The v0.8.5 candidate targets defects demonstrated in v0.8.4 screenshots: short/narrow torso, long visible neck, oversized circular head relative to body, line-like limbs, large joint dots and hands that do not read as hands. It adds configurable torso/head offsets, separate hip placement from foot depth projection, tapered limb surfaces, shaped head/neck/torso, hand contours and machine-readable proportion diagnostics. This remains a candidate until hosted logs, MP4 metadata, evidence artifact and full-speed human inspection pass; it does not claim realistic anatomy, mesh deformation, complete rig editing or production readiness.


## Stage 9b organic-contour review checkpoint — 2026-10-20

Full-size inspection of v0.8.5 found that head/torso proportions were clearer but limbs remained tube-like, joint disks too prominent, sleeves visually merged with limbs, and hands lacked readable grip contours. The v0.8.6 candidate addresses these surface/rendering defects while deliberately preserving the v0.8.5 gait solver, hip/foot projection, cycle timing, contact constraints and temporal thresholds. It remains a procedural stylized 2D character; no claim of physically realistic anatomy or production acceptance is made.


## Stage 10 gait-biomechanics checkpoint — 2026-10-20

Full-size review of v0.8.6 found stance and swing phases both reading as a squat because the pelvis-to-floor span was short relative to fixed leg-chain length and knee pole bias stayed equally strong throughout the cycle. The v0.8.7 candidate raises pelvis position by 8px, reduces swing-foot clearance to 24px, and uses a smooth phase-aware knee bias (more extended stance, more flexed swing). Bone lengths, root stride speed, foot contact model, organic contours, hand/prop rendering and temporal limits are retained. Hosted checks and full-speed human acceptance remain separate gates.


## Stage 11 sagittal gait and near/far leg overlap — 2026-10-20

References consulted: Monmouth Animation Instruction Pages, “Movement: Walk Cycle” (https://animation.monmouth.edu/instruct/animation/walk-cycle/); Arnold et al., “Biomechanics of Multi-ligament Knee Injuries and Effects on Gait,” sagittal-plane gait summary (https://pmc.ncbi.nlm.nih.gov/articles/PMC2953341/); van der Zee et al., “A biomechanics dataset of healthy human walking at various speeds, step lengths and step widths,” Scientific Data (https://www.nature.com/articles/s41597-022-01817-1). The references support building from contact/loading, mid-stance extension, toe-off, and swing rather than holding one crouched knee pose throughout the cycle. Code inspection identified that the prior side-view profile added 28 px to one leg and -28 px to the other in the screen-horizontal axis, exaggerating apparent leg spread by 56 px. v0.8.8 reduces that projection to 6 px per side while retaining the sagittal stride trajectory; reduces pelvis bounce to avoid the two-bone IK repeatedly approaching its maximum-extension singularity; and adds explicit tests for near/far attachment spacing, stance/swing distinction, ankle reachability, and acceleration. No acceptance is claimed until CI and full-speed video review pass.


## Stage 12 — Heel-strike contact extension v0.8.9 — 2026-10-20

Visual review of v0.8.8 full-size frames confirmed that near/far leg separation was corrected, but the contact pose remained visibly crouched. The two-bone chain length was 160px against a 155px hip-to-ankle span at contact, giving an internal knee angle of roughly 151 degrees (about 29 degrees of flexion), too bent for a neutral heel-strike pose. v0.8.9 uses a 158px leg chain (78px upper / 80px lower), places the pelvis at y=410, keeps bob at 0.5px, and lengthens the full gait cycle to 1.20s to retain a temporal margin. The expected heel-strike angle is tested explicitly (>155 degrees), as are phase-separated stance/swing flexion, ankle reachability, foot drift, bone length, side-view leg projection and the unchanged <8 px/frame² acceleration limit. Visual acceptance remains independent.


## Stage 13 — True side-profile projection v0.9.0 — 2026-10-20

Review of the v0.8.9 full-size frame showed that the renderer still presented a frontal face (bilateral eyes), front-view torso/shoulder width, and equally wide near/far legs. This made the otherwise narrow hip-centre spacing read as splayed limbs. v0.9.0 adds a right-facing single-eye profile face, narrows the torso and hips, brings near/far shoulders to ±5px, reduces leg projection to ±2px, and renders a narrower/darker far leg behind the near leg. It also reduces carry basket handle depth spacing to 14px so hands overlap in side projection. The v0.8.9 locomotion solver, foot trajectories, bone lengths, heel-strike extension, cycle cadence and <8px/frame² temporal gate remain unchanged. Hosted CI and full-speed human visual acceptance remain separate gates.


## Stage 13 validation update — 2026-10-20

The push run 39366594252 and pull-request run 39366610236 both completed successfully at commit 30b5db07cca260831e5d857852fe10e6f23c83d8. The hosted artifact `motion-studio-v0.9.0-true-side-profile-review` was uploaded and reviewed at full frame size. It reports 192 frames at 24fps for both profiles, max bone-length error below 1e-12px, basket handle-contact error 0px, planted stance-foot drift below 1e-12px, and maximum tracked-point acceleration 7.6813px/frame² (<8). Visual review shows a right-facing single-eye profile and clear near/far leg overlap; however, full-speed artistic-naturalness acceptance is still pending. A follow-up adds explicit projection metrics (`nearFarLegCenterGapPx`, shoulder gap, profile torso/hip widths and far/near segment-width ratios) so the diagnostics describe side-view geometry rather than frontal widths.


## Stage 14 — Damped human gait v0.9.1 — 2026-10-20

The v0.9.0 artifact had exact stance-foot planting but excessive secondary motion: knee peak step 11.02px/frame, maximum acceleration 7.68px/frame², free-arm wrist step 14.31px/frame, torso orientation range 11.47°, head 5.97°, basket tilt range 5.16° and 24px swing lift. v0.9.1 damps these amplitudes and replaces cubic swing interpolation with quintic Hermite interpolation that matches acceleration at phase boundaries, a C2 foot-clearance pulse, and smoother heel/toe roll. References: van der Zee et al. (2022) https://www.nature.com/articles/s41597-022-01817-1; Meyns et al. (2013) https://pubmed.ncbi.nlm.nih.gov/23489950/; Spallone et al. (2026) https://pmc.ncbi.nlm.nih.gov/articles/PMC13418446/; healthy Thai gait cohort (2023) https://pmc.ncbi.nlm.nih.gov/articles/PMC10696785/. Validation pending.

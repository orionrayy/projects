# Motion Studio — Canonical Product Targets

Last reconciled: 2026-10-20 (Asia/Jakarta). Canonical repo: https://github.com/orionrayy/projects.
Current engineering candidate: Motion Studio v0.9.3 longer-stride phase-adaptive gait in `ffmpeg-motion-studio/foundation-v0.9.3/` on branch motion-studio-v0.9.1-damped-human-gait. v0.9.1 and v0.9.2 are retained as comparison baselines. Earlier CI success on commit 44c08d0ef8ada24b91d5bc43cadcdf1370774678 is superseded by the latest-head checkpoint in section 14; full-size carry/free previews and metrics are available in artifact motion-studio-v0.9.1-damped-human-gait-review. Human visual acceptance at continuous full-speed playback remains pending.
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


## Stage 14 validation results — 2026-10-20

The v0.9.1 push and pull-request workflows both completed successfully and generated two 1280×720, 24fps, 192-frame MP4 previews plus 4fps contact sheets, metrics and SHA-256 checksums. Compared with v0.9.0 metrics: maximum tracked-point acceleration fell from 7.6813 to 3.0994px/frame² (−59.7%); maximum knee step fell from 11.0177 to 7.3980px/frame (−32.8%); chest step fell from 5.4096 to 2.8082px/frame (−48.1%); head step fell from 4.3670 to 2.4259px/frame (−44.4%); torso-angle range fell from 11.4712° to 4.5055° (−60.7%); head-angle range fell from 5.9741° to 2.6302° (−56.0%); basket tilt range fell from 5.1559° to 1.3677° (−73.5%). Stance-foot drift remained below 1e-12px/frame and basket-hand contact error remained 0px. Peak foot displacement per frame rose from 4.0345 to 6.8856px because the C2 trajectory trades some peak velocity for smoother acceleration; maximum total acceleration declined substantially. Continuous full-speed human-naturalness review remains pending, so this stays a draft.


## Stage 15 — Adaptive, contact-reactive gait v0.9.2 — 2026-10-20

The user's review correctly identified that v0.9.1 was smoother by per-frame acceleration metrics but still stiff, repetitive and robotic. The key defect was a fixed-speed phase loop with pure sinusoidal upper-body targets and too little weight-transfer response, not merely excessive amplitude.

Research inputs:
- van der Zee et al. (2022), open motion-capture/ground-reaction-force data across 33 combinations of speed, step length and width: https://www.nature.com/articles/s41597-022-01817-1
- Van Criekinge et al. (2023), full-body motion-capture gait data from 138 able-bodied adults across ages 21–86 and 50 stroke survivors: https://www.nature.com/articles/s41597-023-02767-y
- Ferber et al. (2002), reactive balance corrections after unexpected walking perturbations, with coordinated hip/trunk and lower-limb contributions: https://www.sciencedirect.com/science/article/pii/S0966636202000103
- Meyns et al. (2013), gait-coordinated arm swing and its stabilization: https://pubmed.ncbi.nlm.nih.gov/23489950/

The v0.9.2 candidate adds an integrated smooth start/stop gait clock whose phase coordinate drives both root travel and foot trajectory, preserving stance-foot locking during the speed ramps. It adds contact-localized pelvis compression and lateral transfer, torso/head reaction, balanced free-arm counter-swing using a multi-harmonic waveform, subtle basket response, and deterministic smoothed cycle variation with small left/right asymmetry. Amplitudes are restored modestly after over-damping; the goal is coordinated response, not random jitter.

Validation status: CI/render is pending after this commit. Full-speed naturalness acceptance remains pending until both previews are watched continuously at actual speed. Do not infer human likeness from tests or frame-step metrics alone.


## Stage 16 — Longer-stride phase-adaptive gait v0.9.3 — 2026-10-20

Full-size inspection of v0.9.2 remained stiff, short-strided and robotic despite successful tests/render. The effective stride was 44.64px for a character roughly 300px tall, torso response was subtle, and arm swing was not clearly legible. v0.9.3 increases effective stride to 93px/cycle and foot lift to 16.5px, adds a subtle forward torso lean and asymmetric pelvis rhythm, and varies stride timing through bounded deterministic phase warping of ±0.018 cycles. A shared phase coordinate drives root translation, foot stance/swing, contact response and arm timing so planted stance is preserved. Contact compression remains low because larger body displacement degraded heel-strike extension in early trials.

Research inputs:
- van der Zee et al. (2022), healthy walking capture across speed/step length/step width with motion capture and GRFs: https://www.nature.com/articles/s41597-022-01817-1
- Van Criekinge et al. (2023), full-body gait capture for 138 able-bodied adults: https://www.nature.com/articles/s41597-023-02767-y
- Ferber et al. (2002), perturbation-based reactive balance adjustments: https://www.sciencedirect.com/science/article/pii/S0966636202000103
- Collins et al. (2009), dynamic arm swinging in human walking: https://pmc.ncbi.nlm.nih.gov/articles/PMC2817299/

Validation: CI and full render must pass; continuous full-speed naturalness review remains independent. Do not call this human-like until visual acceptance clears.


## 14. Reference-led visual review and gait-branch correction — 2026-10-20

This checkpoint supersedes earlier claims about the latest v0.9.3 head. The uploaded reference set contains eight vertical H.264 videos (720×1280, 30 fps, approximately 157–331 seconds each). An initial evenly spaced contact-sheet inspection identified a consistent visual grammar; the video set has not been accepted as exhaustive full-speed human motion review.

- Audit: MOTION_STUDIO_REFERENCE_VIDEO_AUDIT_2026-10-20.md.
- The reference visual proof is a separate, dependency-free Node/SVG preview, rendered by CI to a 720×1280, 30 fps, 240-frame MP4 plus a contact sheet. It demonstrates four reusable shot families: room-wide staging, object detail, numbered rule card, and evidence/connection diagram.
- Visual-system requirements now explicitly include composition-safe zones, fixed hierarchy, restrained alert accents, prop-driven action, camera/cut rhythm, typography legibility, and cross-shot continuity. This is a proof slice, not a finished NLE/editor or a full-length export.
- The most recent v0.9.3 workflow before this change was run 39374481048 and failed two temporal assertions. The maximum knee step was 20.0466 px/frame and maximum joint acceleration was 17.7348 px/frame². The fixed-X knee-branch choice could swap geometric solutions as candidate ordering crossed.
- The candidate solver now chooses the knee branch relative to the oriented hip-to-ankle normal, rather than sorting candidates by world-space X. The first hosted rerun retained the exact 20.0466 px knee-step and 17.7348 px/frame² acceleration maxima, so that branch-only change was insufficient. The follow-up adds a knee-only C2 upper-reach transition with a 1 px flex margin to avoid the near-straight two-bone singularity while preserving exact carry-arm IK targets. It must still pass all-frame continuity and hosted rendering gates before being called verified.
- Required evidence: all source tests pass without relaxing thresholds; CI renders carry/free videos and the vertical visual proof; FFprobe confirms resolution, frame rate, frame count and duration; checksums are recorded; the resulting contact sheet and clips still need full-speed visual acceptance.
- Still open: full-speed naturalness and action readability; broader speed/step-width/starting/stopping coverage; browser-vs-FFmpeg raster parity; audio and full editor/timeline subsystems. Successful CI is not production approval.


## 15. Follow-up: near-extension singularity mitigation — 2026-10-20

- The first geometric knee-branch selection change did not alter the CI maxima; the subsequent run still reported a 20.0466 px knee step and 17.7348 px/frame² maximum joint acceleration.
- The next candidate adds a knee-only C2 reach transition over the last 8 px of the chain's nominal reach, ending 1 px short of the sum of upper/lower leg lengths. This avoids the worst near-straight singularity while leaving arm IK endpoint contracts unchanged.
- A synthetic near-extension test and a detailed all-frame continuity test now cover reach margin, knee angle, endpoint error, branch side, step spikes, and acceleration. The tests must pass with the existing geometric/temporal assertions unchanged.
- The new visual proof remains in the same candidate, but no new artifact or naturalness acceptance is claimed until the updated hosted run succeeds.


## Follow-up 2: monotone C2 knee reach + pelvis/floor calibration — 2026-10-20

The first soft-reach candidate was not accepted: CI recorded a remaining knee jump of 17.70 px/frame, endpoint clamp error of 1.86 px, and elevated knee acceleration. The original polynomial could exceed the requested radius partway through its transition, so it was replaced rather than relaxing any acceptance gate.

- New upper-reach curve uses the monotone expression u - u^3 + 0.5u^4, a C2 profile with unit entry slope and zero exit slope/curvature. The transition spans up to the last 6 px of leg reach and leaves a 3 px knee-flex margin for equal/near-equal segment lengths.
- Both v0.9.3 scene profiles shift the pelvis 2 px lower on the canvas (root_y 409 → 411), reducing the near-extended hip-to-ankle distance for the current stride/contact geometry.
- The synthetic near-extension test checks that solved reach never overshoots the requested target or reverses as target reach increases. Knee step, acceleration, ground contact, stance drift and endpoint reach checks remain independent and must all pass.
- This is an unverified candidate: only hosted CI and reviewed full-speed renders can establish whether the calibration improves the actual motion.


## Follow-up 3: stride/cadence envelope calibration — 2026-10-20

The monotone C2 reach curve stopped its radius overshoot, but the latest hosted run still failed at a 13.9645 px/frame knee displacement and 1.9303 px maximum ankle clamp. These remain real quality-gate failures.

- Both v0.9.3 profiles now use a 1.29 s gait cycle and screen stride scale 0.57, giving an effective stride of 85.5 px/cycle and a predicted cadence around 93 steps/min. That remains above the previous 44.64 px/cycle short-shuffle baseline while moderating peak swing geometry.
- Existing hard limits remain unchanged: maximum knee step <13 px/frame, ankle reach error <1.5 px, and the temporal acceleration threshold derived from stride length.
- Added a frame-local ankle reach diagnostic test that reports the exact frame, side, hip, requested foot and solved ankle if the reach gate fails.
- Await the latest hosted run. This candidate is not considered fixed until every source test, render/FFprobe gate and artifact upload passes. Full-speed human art-direction review remains an independent acceptance gate.


## Follow-up 4: endpoint tolerance without gate relaxation — 2026-10-20

Latest hosted run 39381538157 shows the stride/cadence tune brought the knee-step and temporal-acceleration tests inside their existing limits. The remaining failures were the side-view reachability gate and its new per-frame diagnostic: carry mode, frame 101, right leg entering swing, requested reach 158.452 px and solved reach 156.910 px, giving 1.5419 px endpoint error (limit <1.5 px).

- The knee C2 transition width is narrowed from 6.0 to 5.75 px. This makes the solved radius approximately 0.12 px closer to the target at the observed worst frame; it does not change the endpoint-error threshold.
- Re-run the complete source tests and render pipeline. Do not interpret a narrowly passing geometric metric as full-speed naturalness acceptance.


## Follow-up 5: heel-strike extension vs endpoint reach — 2026-10-20

The latest source run passed the per-frame ankle-reach diagnostic, stance-foot, knee-step and temporal-acceleration limits, but the biomechanical heel-strike angle was 153.39° (target >155°). The updated candidate balances these competing constraints explicitly:
- Slightly shorten and re-balance each leg chain to 78.5/80.5 px (total 159 px), making the same contact pose less crouched.
- Use a 4.5 px C2 transition and a small monotone smoothstep bias (0.055) that preserves no-overshoot and makes the upper reach settle about 2 px below chain maximum. The transition remains C2 at each boundary; tests still prohibit target overshoot and preserve the endpoint error gate.
- This may increase sensitivity near near-straight poses; therefore the same-frame knee step/acceleration, branch-side, reach, and >155° heel-strike gates must all pass together. No gate is relaxed.


## Follow-up 6: final temporal cadence calibration — 2026-10-20

The latest hosted run passed heel-strike extension, stance-foot contact, ankle reach, no-overshoot and visual-proof tests. Two temporal tests still found a 13.3348 px/frame knee displacement against the unchanged <13 px/frame limit after the leg-length/curve calibration.

- Both scene profiles now use cycle_seconds 1.33 and screen_stride_scale 0.568. This gives an effective stride of 85.2 px/cycle and a modeled cadence of about 90.2 steps/minute.
- Expected effect is a small reduction in swing-phase knee displacement while retaining a longer stride than the 44.64 px/cycle baseline; CI must confirm the actual frame-level maxima.
- All geometry and temporal assertions remain unchanged. The PR stays draft and unmerged until the new head passes hosted render checks and full-speed human visual acceptance.

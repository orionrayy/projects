# Motion Studio — Canonical Product Targets

Last reconciled: 2026-10-20 (Asia/Jakarta). Canonical repo: https://github.com/orionrayy/projects.
Current engineering candidate: motion-studio-v0.8.1-rendered-validation.
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
- Stage 5 / v0.8.1: render carry/free-arm sequences, apply head counter-rotation visibly, publish MP4/contact-sheet/JSON evidence; wait for hosted CI and human review.
- Stage 6: inspect actual artifacts; fix demonstrated defects (foot crossings/sliding, weight transfer, torso/shoulder/arm/head coupling and object contacts) with regressions.
- Stage 7: editable skeleton hierarchy, joint constraints, pivots, mirroring and IK/FK authoring.
- Stage 8: weight painting/deformation, walk/run profiles, transitions, overlapping and secondary action.
- Stage 9: timeline, layered clips, camera/compositing, audio mixer, subtitles and rights-aware assets.
- Stage 10: integrate reviewed character animation into the 240-second FFmpeg pipeline and the separate motion-analysis QA loop.
- Stage 11: production hardening, renderer parity, performance/accessibility, import/export and cross-domain test corpus.

Version numbers are checkpoints, not evidence of quality. When a gate fails, fix the earliest failing layer before adding a new version.

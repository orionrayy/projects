# Motion Studio Foundation v0.9.5 — Face Refinement and Activity Suite

This candidate continues from the hosted-verified v0.9.4 gait checkpoint. It preserves the existing stride, C2 swing-lift trajectory and all current geometry/temporal acceptance gates.

## Visual refinement
- Replace the rigid profile-head ellipse with a softer, slightly broader side-profile silhouette and a restrained face: one visible eye, a small brow, an integrated nose contour, and a short neutral mouth line.
- Reduce the head-to-chest gap by moving the head center offset from 145 px to 137 px, shortening the exposed neck without changing the core torso or leg chain.
- Slightly increase swing clearance, pelvic bob, torso sway and free-arm amplitude within the existing motion envelope limits.

## Activity coverage
Six deterministic, rendered 3-second 24 FPS proof clips:
1. Stand with subtle breathing.
2. Look-around with controlled head motion.
3. Reach forward with IK-constrained arm extension.
4. Crouch/pick-up with staged lowering, a table-fixed grasp target, contact-aware parcel attachment, lift and recovery.
5. Sit-to-stand with forward-momentum anticipation, seat-off/extension and a final stabilization hold.
6. Weight-shift/foot-pivot cue. It is not represented as a completed turn.

The last item is not true 3D yaw or a multi-view turn. The code explicitly declares that limitation rather than representing a 2D torso counter-rotation as a full turn.

## Verification
The hosted workflow runs all historical regression tests, new face-design and activity tests, then renders five additional action families plus the breathing stand preview at 1280×720/24 FPS, 72 frames per clip. FFprobe checks and SHA-256 checksums are recorded in the artifact.

CI passing verifies kinematic consistency and reproducible renders, not human-like naturalness. Full-speed review and 3D/multi-view turning remain separate acceptance gates. Browser/FFmpeg parity and audio QC are still not verified.

## Forensic action review — repair iteration
The previous encoded clips were extracted and inspected frame-by-frame (72 frames per clip, six clips). That audit found weak/incorrect phase timing: reach held the target for most of the clip; the pickup object was checked mainly at the final held pose instead of the grasp interval; sit-to-stand began with a forward lean already applied and did not explicitly test the momentum-transfer pose; breathing moved the whole root instead of isolating motion in the upper torso; the 2D turn label overstated what the rig can render.

Action channels now use shape-preserving cubic keyframe curves with explicit anticipation, approach, contact, release and settle phases. Breathing is isolated from root/foot motion. Pick-up aims at a table-fixed wrist/grasp anchor and records contact through the gripping interval. Sit-to-stand reaches its forward lean before extension and uses a counterbalance target for the arms. The weight-shift clip now includes opposite foot-pivot cues and is labeled honestly as a 2D weight-shift rather than a real 3D turn.

The hosted workflow emits all 72 frames of every clip in two 6×6 full-frame sheets plus two 6×6 zoomed action-detail sheets. These are audit evidence, not automatic artistic acceptance. Manifest schema 1.5.0 reports contact and return-to-rest gates; human visual acceptance remains pending until the clips pass deliberate full-speed review.

## Evaluation references
- Microsoft Learn, [Animation Principles](https://learn.microsoft.com/en-us/windows/win32/lwef/animation-principles): anticipation, arcs, and secondary action.
- Animation Reference, [Timing and Spacing](https://animationreference.org/resources/animation-timing-and-spacing-reference): compare key-pose intervals, spacing changes, holds, and acceleration.
- Hellmers et al., [Measurement of the Chair Rise Performance of Older People Based on Force Plates and IMUs](https://doi.org/10.3390/s19061370), *Sensors* (2019): phases from seated posture through flexion momentum, momentum transfer, extension and stabilization.
- [Systematic review of sit-to-stand biomechanics in younger and older adults](https://pubmed.ncbi.nlm.nih.gov/37639862/) (2023): highlights forward trunk momentum, foot position and post-rise balance stabilization.

## Action semantics refinement (review-driven)
The activity proof now renders a chair for the sit-to-stand clip and a table-top parcel for the pick-up clip. The parcel stays on the table before the grasp, then follows a deterministic reach/grasp/lift trajectory and remains in hand at the clip end. New regression tests check those semantic cues, object-to-hand attachment, prop step continuity and chair presence. These remain procedural 2D proofs: they do not establish full-body naturalness or true 3D turning.

## Visual-review follow-up
The sit-to-stand seat/backrest and pick-up table are now rendered as filled silhouettes instead of thin lines; the parcel has been enlarged while preserving the grasp anchor. The activity manifest now records whether the chair/object actually appears, whether the parcel remains held at the final frame, maximum per-frame parcel displacement, and held-object contact error. Visual acceptance remains pending.

## Reach action context (review-driven)
The reach clip now contains a visible wall-mounted button aligned to the reach target. Its contact window is explicit in the pose state, and regression tests verify the wrist reaches the target at peak extension without weakening the existing IK/contact gates. Manifest schema 1.3.0 records target presence, peak contact and maximum contact error; artistic acceptance remains pending.
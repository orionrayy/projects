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

Action channels now use monotone quintic Hermite keyframe curves with a shared zero-acceleration contract at every key; this prevents acceleration jumps between authored phases while keeping values within each segment's range. Endpoint velocities are zero because the character holds its initial/final pose outside the timeline. The activity manifest reports peak per-joint jerk and its frame index as an additional temporal cross-check alongside step and acceleration metrics. These numerical gates are still diagnostic evidence, not artistic acceptance. Breathing is isolated from root/foot motion. Pick-up aims at a table-fixed wrist/grasp anchor and records contact through the gripping interval. Sit-to-stand reaches its forward lean before extension and uses separate seated-lap, counterbalance, and standing arm poses. The weight-shift clip now includes opposite foot-pivot cues and is labeled honestly as a 2D weight-shift rather than a real 3D turn.

The audit also found two misleading mechanisms: action-camera X tracking cancelled the animated pelvis translation, and the reach target followed the shoulder, making the previous contact test self-fulfilling. The activity camera is now anchored to the starting root, and the reach target is fixed in world coordinates; both are regression-gated. Profile gaze now includes a rendered pupil offset driven by the glance timeline. Parcel contact is a continuous interval gate: all sampled frames after grip onset must remain within the contact tolerance.

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

## Visual-forensics rework: hand orientation, crossed arms, torso and profile depth

The first 432-frame contact sheet failed visual acceptance despite passing the numerical joint-step and bone-length tests. Cross-checking the renderer, pose solver and activity timelines exposed defects those metrics did not test: near/far elbow branches could converge across the torso; relaxed hands inherited forearm-dependent rotations; the trunk silhouette was drawn with mostly screen-vertical offsets instead of following the spine axis; and zero-stride activity poses projected both feet almost on top of each other.

This revision makes hand pose semantic (relaxed, point, press, grip), constrains relaxed-hand orientation toward screen-down, adds explicit near/far hand metadata to SVG for audit, builds the side-profile torso contour in the chest-to-pelvis local frame, separates the static projected feet, and chooses elbow branches that preserve the far arm behind the torso in idle profile poses. Look-around and turn-in-place cues are more legible but remain 2D profile approximations; this does not claim true 3D yaw or production-level human realism.

The sit-to-stand action should not be judged only by a smooth pelvis trajectory. A 2023 systematic review reports that trunk flexion/momentum, vertical momentum, and postural stabilization are important to sit-to-stand performance and balance regulation ([Sadeh et al., Clinical Biomechanics, 2023](https://pubmed.ncbi.nlm.nih.gov/37639862/)). Animation review also needs clear anticipation, staging, timing, arcs and follow-through rather than mechanically smooth interpolation ([Microsoft Learn: Animation Principles](https://learn.microsoft.com/en-us/windows/win32/lwef/animation-principles); [Disney Animation: Animation Process](https://www.disneyanimation.com/process/animation/)).

Acceptance remains gated by reviewing rendered full-speed clips and their complete frame sheets. Geometry tests are necessary but cannot stand in for human visual acceptance. Audio integration, browser-to-FFmpeg raster parity and long-video integration remain unverified.


## Follow-up audit — joint continuity and limb silhouette

The first post-orientation render was checked at enlarged crop scale as well as through the full-frame sheets. The remaining visible defect was not bone length: elbows and knees were being drawn as two outlined segments that met at undersized, screen-aligned caps. That made the limbs read as hinged tubes, especially during the reach and pickup poses.

This revision adds integrated elbow/knee caps sized from the current rig widths, aligns elbow crease marks to the forearm-normal direction rather than a fixed horizontal screen axis, and reduces arm widths relative to the torso. These are visual-continuity changes only; they do not claim 3D anatomy. New regression gates verify that the cap sizes are proportionate to the rig and that crease geometry is present for the tested action families. The six full-speed clips and all-frame contact sheets must be reviewed again before visual acceptance.


## Follow-up audit — reaching anticipation and whole-body participation

The next full-speed pass showed that the button interaction was geometrically correct but visually arm-led: the wrist began advancing with almost no preceding body response. The reach phase now has a small backward preload before the arm commits, then a stronger forward torso lean, a slight head/gaze response and a counterbalancing far arm. The button remains a world-fixed target and its contact gate remains fingertip-based.

Regression tests assert that anticipation peaks while the wrist is still near its rest pose, the pelvis preloads backward, the torso then leans forward, and the fixed target is still contacted. These changes improve action staging in a 2D profile rig; they do not establish full 3D biomechanics or human-level visual acceptance.


## Follow-up audit — pickup staging and truthful object contact

A rendered close-frame pass showed the non-grasping far forearm folded across the torso, while the parcel eased away from its tabletop origin before the grip was fully established. Both issues could pass the earlier endpoint-only contact metric.

The pickup action now moves the non-grasping hand behind the hip during the deepest part of the crouch, using it as a counterbalance rather than a second reaching arm. The parcel remains exactly on the table until the grip reaches its attachment state; the attach frame is required to place the wrist at the fixed grasp anchor, after which the parcel follows the wrist with a fixed offset. Regression checks cover the entire pre-grip interval, the first attachment frame, continuity of the object-hand offset, and the far hand's position relative to the pelvis. This still remains a procedural 2D profile animation and needs another visual acceptance pass.

## Follow-up audit — action phase separation and elbow-bend reserve

The latest refinement separates pick-up into object-directed anticipation, descent, reach, grip closure, lift, and recovery. The parcel remains table-fixed until the wrist reaches the grasp anchor; lift begins only after attachment and while the character is still crouched. The non-grasping arm now uses a shoulder-local counterbalance target so it cannot be sent beyond the arm chain merely because the pelvis drops.

Sit-to-stand now moves its wrist targets into the reachable lap, momentum-transfer and standing workspaces. Neutral hand targets were also adjusted to retain a small projected bend while staying near pelvis height. The preview manifest reports maximum requested arm reach for each side and the first frame of each pick-up phase; the contact counter only counts frames where the parcel is actually attached.

New tests gate phase order, attachment timing, lift-before-full-recovery, and elbow-bend reserve in neutral and sit-to-stand poses. Passing those tests verifies procedural geometry and timing, not artistic acceptance. Full-speed human review, browser/FFmpeg parity and audio remain pending; the rig is still 2D side-profile and does not perform true 3D turning.


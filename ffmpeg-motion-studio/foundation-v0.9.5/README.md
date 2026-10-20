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
4. Crouch/pick-up with pelvic lowering, torso lean and a low reach.
5. Sit-to-stand with a continuous rise and arm counterbalance.
6. Turn/weight-shift, using torso/head counter-rotation in the existing 2D side-profile rig.

The last item is not true 3D yaw or a multi-view turn. The code explicitly declares that limitation rather than representing a 2D torso counter-rotation as a full turn.

## Verification
The hosted workflow runs all historical regression tests, new face-design and activity tests, then renders five additional action families plus the breathing stand preview at 1280×720/24 FPS, 72 frames per clip. FFprobe checks and SHA-256 checksums are recorded in the artifact.

CI passing verifies kinematic consistency and reproducible renders, not human-like naturalness. Full-speed review and 3D/multi-view turning remain separate acceptance gates. Browser/FFmpeg parity and audio QC are still not verified.

## Action semantics refinement (review-driven)
The activity proof now renders a chair for the sit-to-stand clip and a table-top parcel for the pick-up clip. The parcel stays on the table before the grasp, then follows a deterministic reach/grasp/lift trajectory and remains in hand at the clip end. New regression tests check those semantic cues, object-to-hand attachment, prop step continuity and chair presence. These remain procedural 2D proofs: they do not establish full-body naturalness or true 3D turning.

## Visual-review follow-up
The sit-to-stand seat/backrest and pick-up table are now rendered as filled silhouettes instead of thin lines; the parcel has been enlarged while preserving the grasp anchor. The activity manifest now records whether the chair/object actually appears, whether the parcel remains held at the final frame, maximum per-frame parcel displacement, and held-object contact error. Visual acceptance remains pending.
# Motion Studio Foundation v0.8.8 — Side-View Sagittal Gait

This candidate focuses on leg spacing and lower-limb motion in a side-view character.

## Research basis
- Monmouth Animation Instruction Pages, “Movement: Walk Cycle”: https://animation.monmouth.edu/instruct/animation/walk-cycle/
- Arnold et al., sagittal-plane knee kinematics during gait: https://pmc.ncbi.nlm.nih.gov/articles/PMC2953341/
- van der Zee et al., healthy walking biomechanics dataset: https://www.nature.com/articles/s41597-022-01817-1

## Implementation
- Reduces near/far leg screen-axis projection from 28px to 6px per side (12px attachment-center separation rather than 56px).
- Preserves gait phase and fore/aft stride paths.
- Uses lower pelvis bob and a modestly raised pelvis to avoid repeatedly hitting the 2-bone IK maximum-extension singularity.
- Keeps organic leg contours, heel/toe rendering, foot contact, and existing acceleration/bone-length constraints.
- Adds tests to reject excessive leg projection and check stance/swing differentiation, IK reachability, and temporal limits.

Run `npm test`; hosted workflow renders carry and free-arm previews at 1280x720/24fps, plus contact sheets, metrics, and SHA-256 manifests.

A passing test suite is necessary but not sufficient. Full-speed human visual acceptance remains pending.

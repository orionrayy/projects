# Stage 13 — True Side-Profile Projection v0.9.0

Status: candidate; regression tests and rendered-frame review required.

The v0.8.9 full-size frame still showed a frontal face, wide shoulders and torso, and equal-width near/far legs. That made the limbs read as spread apart even though hip attachment centres were only 4px apart.

Changes:
- Right-facing side-profile head with a single eye, nose/forehead contour, one ear and profile mouth.
- Narrow torso and hip silhouette appropriate to sagittal projection.
- Near/far shoulder centres at ±5px; leg depth projection at ±2px.
- Far thigh/knee/ankle narrower and darker, drawn behind the near leg.
- Basket handle depth spacing reduced to 14px so the carry grip overlaps naturally in side projection.
- Preserves v0.8.9 gait solver, bone lengths, heel-strike extension, cadence and the <8px/frame² temporal gate.

References:
- Cornell CS 5152, 2D walk-cycle keys: https://www.cs.cornell.edu/courses/cs5152/2023sp/labs/design1/
- Monmouth walk-cycle lesson: https://animation.monmouth.edu/instruct/animation/walk-cycle/
- Spallone et al., gait-analysis review: https://pmc.ncbi.nlm.nih.gov/articles/PMC13418446/
- van der Zee et al., healthy gait dataset: https://www.nature.com/articles/s41597-022-01817-1

Full-speed human visual acceptance remains mandatory.

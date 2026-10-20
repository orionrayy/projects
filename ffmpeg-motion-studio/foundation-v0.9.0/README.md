# Motion Studio Foundation v0.9.0 — True Side-Profile Character

This candidate corrects a visual inconsistency in v0.8.9: despite the gait being labelled side-view, the renderer still used a frontal face and front-view width for shoulders, torso and both legs.

## Profile pass
- Right-facing head with one visible eye, a nose/forehead profile, one ear and a profile mouth.
- Narrow torso and hip contour appropriate to sagittal projection.
- Near/far shoulder centres nearly overlap in screen-space; far leg segments are narrower, darker and drawn behind the near leg.
- Leg depth projection reduced to 2px per side; carry basket handle depth spacing reduced to 14px so the grip no longer reads as a frontal presentation.
- Retains the v0.8.9 gait solver, foot trajectories, bone lengths, heel-strike extension, cadence and temporal thresholds.

## Research basis
- Cornell CS 5152, 2D walk-cycle keys: https://www.cs.cornell.edu/courses/cs5152/2023sp/labs/design1/
- Monmouth University walk-cycle lesson: https://animation.monmouth.edu/instruct/animation/walk-cycle/
- Spallone et al., gait-analysis review: https://pmc.ncbi.nlm.nih.gov/articles/PMC13418446/
- van der Zee et al., healthy walking biomechanics dataset: https://www.nature.com/articles/s41597-022-01817-1

Run `npm test`. Hosted CI exports carry/free 1280×720, 24fps MP4s, contact sheets, metrics and checksums. Numerical tests do not replace full-speed visual acceptance.

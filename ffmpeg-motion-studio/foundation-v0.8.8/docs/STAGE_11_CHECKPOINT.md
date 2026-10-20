# Stage 11 — Sagittal-Plane Gait and Near/Far Leg Overlap v0.8.8

Status: engineering candidate; hosted CI and full-speed visual review required.

## Research basis
- Monmouth Animation Instruction Pages, “Movement: Walk Cycle”: https://animation.monmouth.edu/instruct/animation/walk-cycle/
- Arnold et al., “Biomechanics of Multi-ligament Knee Injuries and Effects on Gait”: https://pmc.ncbi.nlm.nih.gov/articles/PMC2953341/
- van der Zee et al., “A biomechanics dataset of healthy human walking at various speeds, step lengths and step widths”: https://www.nature.com/articles/s41597-022-01817-1

## Changes
- Reduce per-leg screen-axis depth projection from 28px to 6px, preventing a false 56px near/far spread in a side-view render.
- Preserve each foot's fore/aft phase trajectory and the near/far draw-order/color treatment.
- Reduce pelvis bob to 1.2px and move the pelvis baseline to y=410 to reduce repeated near-singular full extension while preserving a longer stance line than the v0.8.6 baseline.
- Keep the phase-aware knee pole, organic contours, shoe geometry, and contact/ankle/bone-length gates.
- Add explicit side-view attachment spacing tests and retain the temporal acceleration threshold below 8px/frame².

Not claimed: clinical motion-capture fidelity, production-ready gait, detailed foot anatomical rig or full 3D kinematics. Human visual acceptance remains pending.

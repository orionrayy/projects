# Motion Studio Foundation v0.8.9 — Heel-Strike Contact Extension

This candidate builds on v0.8.8's narrow side-view projection and calibrates the lower-limb chain to the rendered hip-to-ankle span.

## Changes
- Reduce leg chain length from 160px to 158px (upper leg 78px, lower leg 80px) to make the stance leg less crouched without approaching the IK reach singularity.
- Keep pelvis bob at 0.5px and root baseline at y=410.
- Set the full gait cycle to 1.14s (about 105 steps/minute at two steps per cycle) to retain temporal headroom.
- Add an explicit heel-strike assertion for knee internal angle >155°, while preserving stance/swing, contact, bone-length, foot-drift, side-view projection and <8 px/frame² acceleration gates.

## Research basis
- Monmouth Animation Instruction Pages, “Movement: Walk Cycle”: https://animation.monmouth.edu/instruct/animation/walk-cycle/
- Arnold et al., “Biomechanics of Multi-ligament Knee Injuries and Effects on Gait”: https://pmc.ncbi.nlm.nih.gov/articles/PMC2953341/
- van der Zee et al., “A biomechanics dataset of healthy human walking at various speeds, step lengths and step widths”: https://www.nature.com/articles/s41597-022-01817-1

Run `npm test`. Hosted CI exports 1280×720, 24fps carry/free MP4s and contact sheets. Full-speed visual acceptance remains pending; numerical tests do not prove natural anatomy.

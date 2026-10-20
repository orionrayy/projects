# Stage 6 — Anatomy and Stance Calibration v0.8.2

**Date:** 2026-10-20  
**Branch:** `motion-studio-v0.8.2-anatomy-locomotion`  
**Base:** v0.8.1 anatomy candidate `f80b7c6ccd61cce59b771a57c356689dc6e94a13`  
**State:** candidate implementation; full hosted CI and full-speed visual acceptance must pass before promotion.

## Defect evidence from v0.8.1
- User screenshots show a crouched/zig-zag stance, exposed long neck and narrow shoulder line.
- Bulk inspection sampled the existing 192-frame MP4s densely. The same bent-knee quality repeats across the gait cycle; sparse keyframes were not sufficient evidence.
- Main mechanical cause: the previous 79 + 81 px leg segments left too much length slack versus the ~148–151 px hip-to-ankle reach during stance, so both knees remained visibly flexed.

## v0.8.2 changes
- Calibrate both leg segments to 77 + 77 px: nearly extended at planted stance and visibly flexed during the swing/lift phase.
- Increase shoulder half-width to 34 px, retain 18 px waist half-width and 23 px hip half-width, shorten exposed neck by shifting the head/neck assembly down 8 px.
- Add geometry gates requiring minimum stance knee angle >=145 degrees and peak-swing knee angle <=125 degrees.
- Render 192 SVG frames per profile; rasterize all 384 frames; encode carry/free H.264 videos and create eight 24-frame contact sheets per profile (16 sheets total).
- Hosted QC checks codec, resolution, frame rate, frame count, duration, contact geometry, knee mechanics, SHA-256 and full frame coverage.

## Acceptance limits
- Automated gait tests and render QC validate only the configured stylized 2D profile.
- Full-speed human visual review is mandatory; numerical angle limits are guardrails, not proof of natural gait.
- Mesh skinning, weight painting, general rigging/IK-FK authoring, physics and editor features remain out of scope for this increment.
- Do not merge automatically to `main`; keep the candidate separate until contact sheets and both full-speed videos are accepted.

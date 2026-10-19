# Stage 10 — Stance Extension and Gait Biomechanics v0.8.7

Status: engineering candidate until hosted CI and full-speed visual review pass.

- Raise the pelvis-to-floor span by 8px without changing bone lengths.
- Reduce swing-foot clearance to a controlled 24px.
- Blend knee pole bias by foot phase: relatively extended during stance and flexed during swing, with smooth contact-boundary transitions.
- Keep v0.8.6 organic limb contours, joint rendering, hand detail, prop contact solver and temporal thresholds.
- Add gait-specific checks for stance-knee extension, stance-vs-swing flexion, contact/clamp geometry and deterministic cycle sampling.

Not claimed: production-quality gait, motion capture, full muscle/skin simulation or general rigid-body physics. Full-speed visual review remains mandatory.

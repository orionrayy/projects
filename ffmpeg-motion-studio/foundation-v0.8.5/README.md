# Motion Studio Foundation v0.8.5 — Anatomy and Proportion Review

This candidate improves stylized-human proportions and renderable anatomy before adding more editor subsystems.

- Configurable torso length and head-center offset with a shorter visible neck.
- Separate hip width from foot depth projection to avoid implausibly wide hip attachment points.
- Tapered outlined limb surfaces, smaller joints, a shaped torso and oval head, plus hand/palm/finger contours.
- Deterministic carry and free-arm previews, geometry checks, temporal metrics and anatomy ratio diagnostics.

Requires Node.js 20+, FFmpeg and librsvg tools.
Run npm test and npm run render:preview -- .working.

This remains a procedural 2D study. Tests cannot prove artistic naturalness; full-speed visual acceptance, renderer parity and full-film integration remain pending.

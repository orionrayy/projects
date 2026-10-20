# Stage 7 — Temporal Quality Evidence v0.8.3

State: candidate; regression and hosted render gates must pass, then human review remains required.

## Added checks
- Per-frame displacement and second-difference acceleration for pelvis, chest, head, elbows, wrists, knees and feet.
- Consecutive stance-frame foot drift and count of planted/swing contact-state transitions.
- A temporal diagnostics object in each scene's machine-readable metrics.
- Tests for finite/bounded joint steps, acceleration spikes, adequate stance sampling and planted-foot stability.
- 4-fps contact sheets for more detailed visual comparison.

## Acceptance boundary
A passing test demonstrates only that the defined numerical bounds held for these two synthetic 192-frame profiles. It does not prove natural motion, correct weight transfer, production quality, or generalization. Human full-speed review and the wider target contract remain required.

# Stage 16 — Longer-Stride, Phase-Adaptive Gait v0.9.3

Status: candidate implementation; hosted CI/render underway; full-speed naturalness acceptance pending.

## Why v0.9.2 was insufficient

The user's feedback remained valid after v0.9.2 passed unit tests and produced video. Full-size preview inspection still read as a short, shuffling step with a relatively fixed torso and weakly legible free-arm motion. The prior effective stride was only 44.64px against a roughly 300px character height. Lower acceleration alone was not enough to make the motion human-like.

## Research inputs

- van der Zee et al. (2022), a healthy walking biomechanics dataset varying speed, step length and width with motion capture and ground reaction forces: https://www.nature.com/articles/s41597-022-01817-1
- Van Criekinge et al. (2023), full-body gait motion capture from 138 able-bodied adults and 50 stroke survivors: https://www.nature.com/articles/s41597-023-02767-y
- Ferber et al. (2002), reactive balance adjustments following walking perturbations, emphasizing coordinated hip/trunk and lower-limb responses: https://www.sciencedirect.com/science/article/pii/S0966636202000103
- Collins et al. (2009), dynamic arm swinging and its relation to walking mechanics: https://pmc.ncbi.nlm.nih.gov/articles/PMC2817299/

## v0.9.3 implementation

- Increase effective stride to 93px/cycle and swing lift to 16.5px.
- Add a subtle forward torso lean and asymmetric pelvis bob so both halves of the gait do not have identical vertical envelopes.
- Introduce bounded smooth phase warping per cycle. Root translation, feet, contact, arms and body use the same warped phase; stance-foot locking remains a hard invariant.
- Slightly increase visible torso/head response and free-arm swing, without large contact compression that previously reduced heel-strike extension.
- Extend the tests to verify effective stride, bounded phase warping and stance invariance.

## Acceptance gates

1. Run all anatomy, biomechanics, contact, temporal and determinism tests.
2. Render both complete previews at 1280×720/24fps and validate MP4 metadata.
3. Inspect frame grids and watch both MP4s continuously at actual speed. Check step length, heel-toe timing, pelvis transfer, trunk attitude, opposing arm swing, foot contact, hand/prop contact and absence of jitter.
4. Keep `humanVisualAcceptance` as pending until full-speed human review confirms improvement. Passing CI alone is not a naturalness score.

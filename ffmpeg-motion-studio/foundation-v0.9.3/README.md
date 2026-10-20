# Motion Studio Foundation v0.9.3 — Longer-Stride, Phase-Adaptive Gait

This candidate follows v0.9.2 after full-size preview inspection still showed a short, shuffling gait with a nearly fixed torso and weakly readable arm motion. It preserves v0.9.2 as a comparison baseline rather than treating low acceleration as a proxy for naturalness.

## Research basis

- van der Zee, Mundinger & Kuo, “A biomechanics dataset of healthy human walking at various speeds, step lengths and step widths,” *Scientific Data* (2022): https://www.nature.com/articles/s41597-022-01817-1
- Van Criekinge et al., “A full-body motion capture gait dataset of 138 able-bodied adults across the life span and 50 stroke survivors,” *Scientific Data* (2023): https://www.nature.com/articles/s41597-023-02767-y
- Ferber et al., “Reactive balance adjustments to unexpected perturbations during human walking,” *Gait & Posture* (2002): https://www.sciencedirect.com/science/article/pii/S0966636202000103
- Collins, Adamczyk & Kuo, “Dynamic arm swinging in human walking,” *Proceedings of the Royal Society B* (2009): https://pmc.ncbi.nlm.nih.gov/articles/PMC2817299/
- Meyns, Bruijn & Duysens, “The how and why of arm swing during human walking,” *Gait & Posture* (2013): https://pubmed.ncbi.nlm.nih.gov/23489950/

## Changes in v0.9.3

- Increase effective stride from 44.64 px to 93 px per gait cycle (150 px nominal stride at the existing 0.62 screen scale) to avoid the prior tiny shuffle.
- Increase swing clearance from 11 px to 16.5 px and add a small asymmetric pelvis rhythm and a slight forward torso lean; this creates readable motion without returning to the previous 24 px high-lift exaggeration.
- Add bounded, deterministic phase warping (±0.018 cycles) to break the identical metronomic timing while using the same warped cycle coordinate for root travel and planted-foot motion.
- Improve torso reaction, head follow and multi-harmonic arm swing slightly while keeping the contact impulse small enough to preserve heel-strike extension.
- Add assertions for effective stride, bounded phase warp and stance-foot invariance.

## Validation

Run `npm test`. Hosted CI renders complete 1280×720, 24 fps carry and free-arm previews with contact sheets, metrics and SHA-256 checksums. Numerical gates are diagnostic only; continuous full-speed naturalness acceptance remains pending until both videos are watched at actual speed.

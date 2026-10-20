# Motion Studio Foundation v0.9.2 — Adaptive, Contact-Reactive Gait

This candidate addresses a key weakness in v0.9.1: lower acceleration did not make the motion human-like. The previous walk was too periodic and over-damped, with a fixed cadence, identical repeated steps, and little visible transfer of load.

## Research basis

- van der Zee, Mundinger & Kuo, “A biomechanics dataset of healthy human walking at various speeds, step lengths and step widths,” *Scientific Data* (2022): https://www.nature.com/articles/s41597-022-01817-1
- Van Criekinge et al., “A full-body motion capture gait dataset of 138 able-bodied adults across the life span and 50 stroke survivors,” *Scientific Data* (2023): https://www.nature.com/articles/s41597-023-02767-y
- Ferber et al., “Reactive balance adjustments to unexpected perturbations during human walking,” *Gait & Posture* (2002): https://www.sciencedirect.com/science/article/pii/S0966636202000103
- Meyns, Bruijn & Duysens, “The how and why of arm swing during human walking,” *Gait & Posture* (2013): https://pubmed.ncbi.nlm.nih.gov/23489950/

## What changed

- Add an integrated gait clock with smooth acceleration at the start and deceleration at the end. Root travel and stance-foot trajectory share the same phase coordinate, preserving exact plant through the speed ramps.
- Make motion phase/event-driven: contact loading now contributes small, coordinated pelvis compression/lateral transfer, torso reaction, head counter-rotation, arm compensation, and prop response.
- Replace pure free-arm sine waves with a phase-shifted, multi-harmonic counter-swing whose timing is coupled to the gait cycle.
- Add deterministic, smoothed cycle-to-cycle variation and a small left/right swing-clearance asymmetry. Variation is low amplitude, reproducible, and cannot jump at stride boundaries.
- Restore visible but bounded weight transfer instead of optimizing solely for low acceleration.
- Extend temporal tests for start/stop envelope, repeat-cycle variation, contact response, and planted-foot invariance.

## Validation

Run `npm test`. Hosted CI creates 1280×720/24fps carry and free-arm previews, contact sheets, JSON metrics and checksums. Numerical gates remain necessary but do not prove naturalness. The continuous full-speed video review is still a separate human acceptance gate.

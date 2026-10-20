# Stage 15 — Adaptive, Contact-Reactive Gait v0.9.2

Status: engineering candidate; hosted tests/render and full-speed visual acceptance required.

## Defect being addressed

The v0.9.1 iteration reduced acceleration spikes, but inspection and the user's feedback show that the animation remains stiff and robotic. The root cause is not just amplitude: fixed cadence, mathematically identical cycles, pure sinusoidal arm targets, almost static pelvis/head channels, constant travel speed, and weak contact/load response make the motion read as a mechanical loop.

## Research-driven changes

- The open healthy-gait dataset varies speed, step length, and step width and includes synchronized motion capture and ground-reaction force; gait should be phase- and speed-conditioned rather than one rigid oscillator: https://www.nature.com/articles/s41597-022-01817-1
- Full-body capture data from 138 able-bodied adults provides a broader population reference for joint motion, center of mass, and gait-event timing: https://www.nature.com/articles/s41597-023-02767-y
- Research on gait perturbations describes synchronized balance corrections across hip/trunk and lower-limb mechanics, not independent joint oscillations: https://www.sciencedirect.com/science/article/pii/S0966636202000103
- Arm swing is coordinated with the gait cycle and stabilized by active control, not an arbitrarily animated independent sine wave: https://pubmed.ncbi.nlm.nih.gov/23489950/

## v0.9.2 implementation

- Integrated smooth start/stop gait clock and root travel from the exact same normalized phase as the stance-foot trajectory; this is intended to ease velocity without causing planted-foot slide.
- Phase-localized contact response couples pelvis compression/lateral transfer, torso reaction, head counter-rotation, arm compensation, and basket response.
- Three-harmonic arm swing with a slight lag and cycle-dependent amplitude.
- Deterministic smoothed variation between cycles and slight side-to-side clearance asymmetry.
- Slightly restore pelvis/head/torso/arm motion after v0.9.1 over-damping, retaining explicit temporal envelopes.

## Required validation

1. Geometry: bone lengths, ankle reach, heel-strike knee extension, side-profile overlap and zero ground penetration.
2. Temporal: stance foot drift across normal-speed and eased start/stop, per-point speed/acceleration envelopes, finite values, deterministic variation, and contact-response behavior.
3. Render: complete 192-frame 1280×720/24fps carry/free previews plus contact sheets, metrics and hashes.
4. Human review: watch both MP4s at actual speed; check stiffness, weight transfer, arm counter-swing, silhouette collisions, start/end phases, and prop contact. Keep naturalness marked pending until this happens.

A passing CI run is not evidence that the walk is human-like; the v0.9.2 candidate remains a draft until continuous visual acceptance.

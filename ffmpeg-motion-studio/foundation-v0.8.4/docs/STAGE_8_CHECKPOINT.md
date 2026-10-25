# Stage 8 — Carry Interaction and Scene Semantics v0.8.4

Status: candidate; hosted CI and human visual acceptance are separate gates.

- Hide the basket in the free-arm locomotion profile so the prop is not shown floating without a grip.
- Add a small phase-lagged basket tilt to the carry profile.
- Rotate the computed handle contact points with the basket orientation.
- Add rendered regression assertions that free-arm SVG excludes the basket and carry contact sheets show the basket geometry.
- Record basket tilt range and preserve the wrist/handle contact error check.

Known limits: this does not implement general rigid-body dynamics, a grasp solver, physically simulated inertia, finger articulation, or broad object manipulation. Human review remains required.

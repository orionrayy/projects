# Quality Gate v0.1

Hard checks: Draft 2020-12 scene schema; unknown fields, malformed colors and invalid rig lengths; integer frame/time bounds; deterministic shuffled random access; two-bone IK length invariants; unreachable-target clamping; reserved-zone collision faults; ffprobe H.264 dimensions/FPS.

Not proven: aesthetic preference, acting quality, naturalness, arbitrary-character anatomy, typography in all environments, audio quality or commercial-generator parity. Unknown quality stays UNVERIFIED.

Rendered-SVG gate: parse the emitted `pointing-hand` transform for every frame and compare its angle, origin, transformed fingertip and scale with the evaluated pose. A test mutation that changes the serialized rotation must fail. This is independent of the previous state-only angle self-comparison, but remains a geometric contract rather than an aesthetic evaluator.

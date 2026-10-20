# Stage 14 — Damped, Phase-Coherent Human Gait v0.9.1

Status: candidate; hosted CI and full-speed video review required.

The v0.9.0 artifact had exact foot planting and low geometric error but retained excessive secondary motion: max knee step 11.02px/frame, maximum tracked-point acceleration 7.68px/frame², free-arm wrist step 14.31px/frame, torso orientation range 11.47°, head range 5.97°, basket tilt range 5.16° and 24px swing lift.

Research-led changes:
- Healthy gait data supports phase-normalized trajectories across different cadences and strides. Arm-swing literature describes arm swing as largely passive and stabilized by active control, not large independent oscillation.
- Knee kinematics follow phase-shaped extension/flexion: near-extension at contact, controlled loading-response flexion, stance extension and larger swing flexion.
- Quintic Hermite foot path matches position, velocity and acceleration at stance/swing boundaries.
- A quintic foot-clearance pulse and smoother heel/toe roll reduce secondary acceleration spikes.
- Motion envelopes are damped: 96 steps/min, 9px swing lift, 17px horizontal and 1.5px vertical free-arm amplitude, 0.038rad torso sway plus 0.006rad harmonic, 1.5px torso shift, 0.005rad head follow, 0.002rad head bob, 0.45px basket response and 0.012rad basket tilt.
- Knee IK pole offsets reduce to 14/12px; limb lengths and planted-foot constraints are unchanged.
- Temporal tests separately gate head/chest/elbow/wrist/knee/foot frame-step and total acceleration, and measure phase-boundary continuity.

References:
- https://www.nature.com/articles/s41597-022-01817-1
- https://pubmed.ncbi.nlm.nih.gov/23489950/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC13418446/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10696785/

Human visual acceptance remains separate from numerical test success.

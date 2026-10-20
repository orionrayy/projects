# Motion Studio Foundation v0.9.1 — Damped Human Gait

This candidate preserves v0.9.0's true side-profile renderer while reducing the exaggerated secondary motion that made walking look ragdoll-like.

## Research basis
- van der Zee, Mundinger & Kuo, healthy walking at different speeds, step lengths and step widths, *Scientific Data* (2022): https://www.nature.com/articles/s41597-022-01817-1
- Meyns, Bruijn & Duysens, “The how and why of arm swing during human walking”, *Gait & Posture* (2013): https://pubmed.ncbi.nlm.nih.gov/23489950/
- Spallone et al., gait-analysis and knee-kinematics phases, *Knee Surgery, Sports Traumatology, Arthroscopy* (2026): https://pmc.ncbi.nlm.nih.gov/articles/PMC13418446/
- Healthy Thai adult knee kinematics, *BMC Musculoskeletal Disorders* (2023): https://pmc.ncbi.nlm.nih.gov/articles/PMC10696785/

## Changes
- Replaces cubic swing interpolation with a quintic Hermite path matching position, velocity and acceleration at stance/swing boundaries.
- Uses a C2 foot-clearance pulse and smoother heel/toe roll transitions to reduce acceleration snaps.
- Reduces cadence to 96 steps/minute, step excursion, foot lift, free-arm swing, vertical arm motion, torso sway/shift, head follow/bob, basket response and basket tilt.
- Reduces knee pole offsets without changing limb lengths or planted-foot constraints.
- Tightens temporal acceptance gates and reports motion-envelope parameters.

Run `npm test`. Hosted CI renders 1280×720/24fps carry and free-arm previews and uploads MP4s, contact sheets, metrics and checksums. Passing numerical gates do not replace full-speed human visual acceptance.

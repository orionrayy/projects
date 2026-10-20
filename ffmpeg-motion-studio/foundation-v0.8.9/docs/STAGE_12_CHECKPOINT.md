# Stage 12 — Heel-Strike Contact Extension v0.8.9

Status: engineering candidate until hosted CI and full-speed visual acceptance pass.

- Retain v0.8.8's narrow 6px near/far depth projection.
- Recalibrate leg chain to upper=78px, lower=80px (158px total), with torso length 98px, pelvis root y=410 and bob amplitude 0.5px.
- Set full gait cycle to 1.14 seconds to allow smoother per-frame acceleration while retaining a normal walking cadence.
- Add a heel-strike knee internal-angle gate above 155°.
- Keep planted-foot drift, ankle reachability, bone-length, swing/stance and <8px/frame² temporal acceptance gates.

The clinical and animation references identify near-extended initial contact followed by loading-response knee flexion, mid-stance extension and pre-swing/swing flexion. This stylized solver approximates those phases; it is not motion capture or clinical simulation. Visual approval remains pending.

# Motion Studio — reference-video visual audit (2026-10-20)

## Scope and evidence boundary

The supplied ZIP contains eight H.264 MP4 reference clips. FFprobe confirmed portrait 720×1280 video at 30 fps for all eight. Their durations are approximately 156.9–330.9 seconds, totaling about 31 minutes 45 seconds. An initial review used ten evenly spaced frames per clip (80 visual samples) and inspected contact sheets. This is a structured visual-language audit, not a claim that every frame or any audio track has been fully reviewed.

The samples are treated as art-direction evidence at the level of visual grammar. Motion Studio must not reproduce the source clips verbatim; narration, graphics, scene structure and assets remain editable, with new content supplied by the project.

## Reference visual grammar observed

1. **Persistent editorial header.** A compact title and a red warning/claim line remain near the top across many scenes. This creates continuity between room illustrations, close-ups, graphic cards and evidence screens. Keep this region stable and reserve a separate caption region below the action.
2. **Portrait-safe horizontal staging.** Although the canvas is 9:16, the story often uses a horizontal room/set, a person, a prop and a floor line across the middle. The stage must have enough width for the action while title and caption text remain readable on mobile.
3. **High-contrast, limited palette.** Near-black backgrounds and white/gray line art dominate. Red is reserved for warnings, rules and alert states; gold/yellow marks a single meaningful light/object/path; green is used sparingly for confirmed checklists. Avoid adding an accent color to every object.
4. **Simple set construction with recognizable silhouettes.** Doors, beds, windows, cabinets, phones, speakers, refrigerators and status screens use crisp contours and a small number of stable shapes. Geometry should be deliberate and reusable, not a pile of tiny decorative details.
5. **One primary visual claim per shot.** Scenes repeatedly isolate a single action or clue: an object is watched, a door opens, a signal appears, a status changes, or an instruction is revealed. Secondary information belongs in a label, diagram or following shot—not all at once.
6. **Repeated shot families.** The references alternate between a wide establishing set, a close-up of the story-critical object, a bold numbered “RULE” card, a compact diagram/UI/stat panel, and a return to the set to show consequence. Motion Studio should expose these as reusable shot/composition templates.
7. **Narrative props carry the explanation.** A phone screen, light, door gap, icon, note, map, graph or checklist visualizes the line of narration. When possible, animate the causal object or evidence, rather than applying generic motion to the whole frame.
8. **Controlled attention effects.** Glows and red pulses are localized around the current clue. Noise/glitch appears as an occasional accent or intro treatment, rather than permanent interference. The screen otherwise remains calm enough for reading.
9. **Typography has explicit roles.** The title, red instruction, numbered rule, UI/data label and lower explanatory caption need distinct size/weight/position rules. Avoid micro-text being the only carrier of story information; test readability at actual phone dimensions.
10. **Cuts and transitions preserve the idea.** The visual rhythm works because shots change purpose—wide context, prop detail, rule card, evidence, consequence—rather than simply moving the camera continuously. Prefer a clear cut, match cut, restrained push or short dissolve where justified; avoid default constant zoom, shake, bounce or random particles.
11. **Stable horizon and object continuity.** Floors, doorways, furniture, device positions and graphic anchors form a consistent scene coordinate system. Camera changes need a named reason, and an object must not teleport, change scale unexpectedly, or lose its screen/world anchor across a cut.
12. **Action readability before detail.** Most illustrative characters are highly simplified. Their readability depends on silhouette, staging, prop contact, timing, clear before/after states and a short hold after the action—not on adding more lines or making every body part move at once.

## What this means for Motion Studio beyond anatomy

The next visual-production layers should be independent of the character rig:

- **Art-direction tokens:** palette, line weight, glow/blur, background grain, safe zones, font families/weights, corner/outline style, caption treatment and target aspect ratio, all serialized per style profile.
- **Scene graph and composition:** environment/set pieces, props, character anchors, layers/occlusion, foreground/background depth, ground plane, named camera frame and transition intent.
- **Typography and captions:** persistent header and accent line; per-shot title/caption tracks; responsive wrapping; maximum line lengths; text-safe areas; word/phrase cue support; actual-resolution tests.
- **Reusable shot grammar:** wide, object-detail, rule-card, device/UI, evidence diagram, checklist/stat panel and consequence/reaction templates. Each declares primary subject, entry/hold/exit timing, camera intent, subtitle cue and transition.
- **Prop-driven animation:** status LED, screen state, signal/waveform, door movement, object highlight, evidence drawing and causal connectors should animate only when they explain the narrative.
- **Camera/cut semantics:** named framing states and calibrated transforms, restrained ease, match-on-action cue, transition durations and no unintentional jumps in prop/character anchors.
- **Visual QA:** clipped text, title/caption overlap, minimum mobile text size, contrast, out-of-frame geometry, cut timing, scene identity/continuity, compositional density and browser-vs-FFmpeg raster parity.
- **Audio remains a separate acceptance gate:** this audit did not validate narration, music, SFX, loudness or synchronization. Do not infer audio quality from the silent Motion Studio motion previews.

## Deepened character-motion direction

The reference character art is intentionally minimal, but its movement still must read clearly and be connected to the scene. Motion must be less about adding oscillations and more about the cause, weight and recovery of an action.

1. **Foot contact and center-of-mass transfer:** use a stance/swing state with stable planted-foot anchors, heel-to-toe progression, bounded ground penetration and a deliberate transfer of support from one leg to the other.
2. **Knee branch continuity:** a two-bone IK solution has two valid elbow/knee candidates. Selecting whichever candidate has the larger global X coordinate is not temporally invariant: candidate ordering can switch as the hip-to-ankle vector rotates. Pick a consistent geometric side relative to the oriented hip-to-ankle normal; test every frame for knee position, acceleration and branch-sign changes.
3. **Whole-body coupling:** pelvis timing, torso counter-rotation, shoulder motion, head stabilization and contralateral arm swing must respond to the same gait phase and contact state. They must not all peak together or use independent, identical sine waves.
4. **Speed and step modulation:** treat stride length, cadence, lift and step width as a coordinated profile. A longer projected stride is not sufficient if it produces crouched knees, stretched limbs or unstable contact. Calibrate several speeds and step lengths.
5. **Reactive starts, stops and perturbations:** use anticipation, a bounded acceleration/deceleration profile, contact-state response and a recovery/settle period. Tiny, deterministic cycle variation may break metronomic repetition, but must not create jitter or uncontrolled drift.
6. **Secondary motion is subordinate:** head, hair, clothing, hands and carried props can lag or settle, but their motion must be damped, mass-informed and tied to the primary action. More movement is not equivalent to more naturalness.
7. **Actions require contact:** reaching, grasping, carrying, opening, pressing and releasing need explicit targets, contact intervals, valid reach, occlusion order and a visible release/settle—not wrist motion that merely passes near an object.
8. **Full-speed review remains mandatory:** low acceleration, fixed bone lengths and zero stance drift do not prove human naturalness. Review complete 24/30 fps clips and inspect failures around heel strike, toe-off, branch switches, turns, starts, stops, object contact and cycle boundaries.

## Research references and implementation implications

- **van der Zee, Mundinger & Kuo (2022), “A biomechanics dataset of healthy human walking at various speeds, step lengths and step widths,” Scientific Data.** The open dataset covers 33 controlled combinations of speed, step length and step width, with motion capture, ground-reaction forces and inverse-dynamics data for many trials. Use it to avoid calibrating only one idealized stride: https://www.nature.com/articles/s41597-022-01817-1
- **Losing & Hasenjäger (2022), “A Multi-Modal Gait Database of Natural Everyday-Walk in an Urban Environment,” Scientific Data.** It describes longer everyday routes including ramps, stairs and pavements, with synchronized wearable motion, foot-pressure and gaze measures. This is a better conceptual model for transitions than a perfectly periodic treadmill loop: https://www.nature.com/articles/s41597-022-01580-3
- **Le Goff et al. (2026), “A public dataset of treadmill walking kinematics and kinetics at steady speeds in healthy individuals,” Data in Brief.** The reported dataset contains 45 participants walking at six controlled speeds from 0.6 to 1.6 m/s, with joint kinematics and kinetic measures. It offers a recent additional calibration source, subject to license and data-access verification: https://doi.org/10.1016/j.dib.2026.112943
- **Collins, Adamczyk & Kuo (2009), “Dynamic arm swinging in human walking,” Proceedings of the Royal Society B.** Their model and experiments support treating arm swing as mechanically coupled with gait and whole-body moments rather than a disconnected wrist oscillator: https://pmc.ncbi.nlm.nih.gov/articles/PMC2817299/
- **Human walking rhythm response to perturbation (2016), PLOS Computational Biology.** This work studies phase-dependent rhythm response and stability around gait events; it motivates bounded, contact-aware adaptation rather than arbitrary phase noise: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004950
- **HumanML3D (Guo et al., CVPR 2022), motion-language data derived from AMASS/HumanAct12.** It provides a broad range of daily and athletic actions and text descriptions, useful as a future motion-coverage reference. Do not make a large model, GPU, SMPL asset or heavy dependency a prerequisite for the current low-resource 2D solver: https://github.com/KyanChen/HumanML3D

Data and papers must be cited and their actual reuse terms checked before training or bundling. The immediate implementation remains deterministic and free-first; reference datasets are research/calibration options, not claimed to be integrated or trained into this prototype.

## CI finding from the v0.9.3 candidate

The hosted run 39374481048 (https://github.com/orionrayy/projects/actions/runs/39374481048) failed two tests: maximum knee displacement was 20.0466 px/frame and maximum joint acceleration was 17.7348 px/frame²; 24 of 26 tests passed. This is a genuine solver discontinuity signal, not a reason to weaken the assertions. The preferForward branch now selects by an oriented normal relative to the hip-to-ankle direction. It is a targeted candidate correction and remains unverified until the same CI tests and renders pass.

## New visual proof slice

The file scripts/render-reference-visual-preview.mjs in ffmpeg-motion-studio/foundation-v0.9.3 provides a small, dependency-free portrait-format visual grammar proof. It emits 240 SVG frames at 720×1280 and 30 fps over eight seconds, covering a room-wide shot, a prop detail, a numbered instruction card and an evidence diagram. CI encodes an MP4 and contact sheet. The proof does not claim a completed long-form pipeline, final narration, full editor, browser/FFmpeg parity or full-speed art-direction approval.

## Acceptance gates for the next candidate

- Do not relax the existing knee-step, joint-acceleration, planted-foot, bone-length, ground-contact or prop-contact checks to make CI green.
- Require zero unintended branch flips, finite poses, fixed-length error below 0.02 px, ground penetration below 0.02 px, and stance drift below 0.05 px/frame across both carry and free-arm outputs.
- Preserve the current temporal gates and test both profiles at every rendered frame, not just selected keyframes.
- The vertical style proof must produce exactly 240 frames at 720×1280, 30 fps and eight seconds; validate with FFprobe and record SHA-256.
- Inspect the contact sheet at full size and play the generated clips at actual speed. Automated render success is a build gate, not human visual acceptance.
- Keep the full product target list in sections 3–8 intact. The visual lab is an incremental reference, not a silent scope reduction.

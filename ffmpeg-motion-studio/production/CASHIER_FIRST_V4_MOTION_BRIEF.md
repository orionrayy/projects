# CFG Explainer V4 — 240-second production and motion brief

## Objective
Create a 240.000-second Indonesian educational animation on Context-Free Grammar and parse trees, anchored by a cashier/receipt problem. Output is 1920x1080 at 24 fps (5,760 frames), H.264 video with AAC stereo 48 kHz narration and synchronized procedural sound effects.

## Fixed narrative structure
- Scenes 1–3: 8 seconds each, 24 seconds total: identify the item, explain barcode-to-product lookup, and ask how discount and total correctness are guaranteed.
- Scene 4 begins directly at the POS screen. No prolonged entrance or aisle journey before the CFG lesson starts.
- Scenes 5–8: tokenization, formal CFG G=(N,Σ,P,S), parser/syntax validity, and parse-tree structure.
- Scenes 9–10: operator precedence and parentheses, with results 14 and 20.
- Scenes 11–15: semantics, itemized prices, 10% discount, AST abstraction, post-order evaluation and invariant checks.
- Scenes 16–18: payment authorization, receipt audit, and concise concept recap.

## Correctness invariants
- Rp18.500 + Rp21.500 + Rp14.000 = Rp54.000.
- 10% × Rp54.000 = Rp5.400.
- Rp54.000 − Rp5.400 = Rp48.600.
- 2 + 3 × 4 = 14; (2 + 3) × 4 = 20.
- The total is shown only after correct computation. Tokenization is not confused with parsing, and syntactic validity is not confused with semantic validity.

## Motion and readability upgrades
- The opening questions are capped at 8 seconds each; instructional scenes keep longer holds where grammar and parse trees need reading time.
- The illustrated shopper's gait cycle is faster and the head-to-torso gap is shorter. The person remains a procedural illustration; the stickman sample is not copied into the film.
- Each scene has distinct composition and camera behavior. Every scene has three in-range action/effect/SFX cue beats.
- Causal audio sync: scan beep when the beam reaches the barcode, register ticks on row arrival, confirmation chime when arithmetic locks, NFC ripple after card contact, and printer sound during paper feed.
- Subtitles stay in a fixed lower safe area and must not obscure formulas, branch relations, totals or scanner/contact points.

## Dataset use
The user's five-pose stickman file is REFERENCE-ONLY research. It informs qualitative review of timing/continuity and compact proportions, but is not rendered as a character asset, copied source image or inserted scene. The source playback rate and exact meaning of interframes=8 remain unverified. No model training/fine-tuning is claimed.

## Audio pipeline
Indonesian TTS voiceover is generated per scene, timed against the scene timeline, combined with procedural SFX, mixed to stereo 48 kHz, limited, faded at the 240-second endpoint, and muxed into AAC. Deliverables include SRT, transcript, SFX-only stem, cue sheet, shot-by-shot guide, contact sheet and production manifest. Automated tests check stream presence, channel/sample rate, duration, file size and cue timing; human listening is still needed for pronunciation and mix acceptance.

## Automated acceptance
- 18 scene IDs, durations total exactly 240 seconds and 5,760 frames at 24 fps.
- 1920x1080 H.264 video and AAC stereo 48 kHz audio.
- Non-static motion checks for representative scenes.
- Three in-range cue beats per scene.
- Correct arithmetic and all required CFG teaching topics.
- Package, subtitle, SFX stem, contact sheet, manifest and motion guide exist.
- Human artistic and listening QA is separate from technical acceptance.

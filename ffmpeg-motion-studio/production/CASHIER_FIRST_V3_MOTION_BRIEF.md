# Cashier-first V3 — creative and motion brief

## Reversal of the V2 approach

V2 used a shared header, shared narration panel and mostly diagram/card compositions, while its three beat cue labels were not sufficient to guarantee readable, purposeful motion. Technical output validation cannot establish artistic quality. V3 therefore changes the composition and movement per shot, with a limited three-shot opening and the teaching section placed immediately at the cashier display.

## Opening: exactly three question hooks / 12 seconds

1. **Storefront — 4 seconds.** A short dolly toward the illuminated store and sliding doors. Voiceover asks how a cashier knows the correct total. The doors and light spill act as the directional transition.
2. **Barcode scan — 4 seconds.** A close shot of package, barcode and scanner. The scan beam crosses once; a scan chirp and data fragments follow that crossing. Voiceover asks how a beep turns a physical object into data without implying that scanning equals understanding.
3. **POS total — 4 seconds.** Tight register display, equation and a total that settles to Rp48.600. Voiceover asks what guarantees that the number is correct. Match-cut the display frame into the teaching view.

Scene 4 starts on the register and teaches the formula. There is no prolonged basket/aisle/weighing montage before the content starts.

## Teaching sequence

4. Cashier formula: total = 54000 − 5400.
5. Tokenization: IDENTIFIER, EQUALS, NUMBER, MINUS, NUMBER.
6. Context-Free Grammar productions and their role.
7. Difference between token classification and parser rejection of invalid order.
8. Parse tree with root, branches and numeric leaves.
9. Operator precedence: 2 + 3 × 4 = 14.
10. Parentheses: (2 + 3) × 4 = 20.
11. Syntax versus semantics, including undefined values.
12. Itemized prices add exactly to Rp54.000.
13. Ten-percent discount gives Rp5.400.
14. AST compresses the operation into SUB with subtotal and discount operands.
15. Evaluation yields Rp48.600.
16. Card/NFC payment.
17. Receipt prints and provides an audit trail.
18. Short exit/recap links the concepts without rebuilding the long store journey.

## Motion and effects constraints

- Each shot has its own visual grammar: illustrated retail environment, barcode scan close-up, POS display, token choreography, production rules, paired syntax comparison, progressive trees, itemized price roll-up, coupon math, AST collapse, payment touch, paper feed, and concise exit.
- Easing must communicate weight: acceleration, deceleration, and short settle. Lines draw before child nodes arrive. Rows stagger instead of moving in unison.
- VFX have causal triggers. The scanner beam must cross the barcode before the beep; register ticks accompany row arrivals; math confirmation only occurs when the correct value settles; NFC ripple begins at card contact; receipt paper advances with printer sound.
- Use short, shot-specific camera push/pull and small parallax. Do not lay a global grid under every scene, fill all empty space with particles, continuously glow every element, add random shake, or flash on every sound.
- Subtitle safe area is the lower third. Mathematical expression, tree structure, scanner contact and totals remain unobscured.
- Hard math assertions: 54.000 − 5.400 = 48.600; 54.000 × 0,10 = 5.400; 2 + 3 × 4 = 14; (2 + 3) × 4 = 20.

## Acceptance gates

**Automated/technical:** 18 scenes, exact 240-second duration, 5760 frames at 24 fps, 1920×1080 H.264, AAC stereo 48 kHz, subtitle and cue files, three beat events in each scene, correct formula arithmetic.

**Human/artistic (still required):** look at the full contact sheet and motion in the actual MP4; check whether object actions read in sequence, whether limb pose is legible, whether captions overlap formulas, whether each transition motivates the next shot, and whether Indonesian TTS pronunciation, mix and SFX impact are acceptable. A green technical gate is not proof of a cinematic/artistic pass.

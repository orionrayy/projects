# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Base game: Death Road to Canada. Project name: DR2C VORENYX.
- Current scope: Indonesian localization and replacement title identity; larger expansions remain deferred until the localization foundation is substantially complete.
- Invariant: retain the original Canada-bound journey and campaign flow.
- Target voice: colloquial Indonesian that is slangy, blunt, sarcastic and occasionally profane, with distinct NPC personas.
- Target: 100% of player-visible text; **not yet achieved**.

## Current checkpoint — v2.3 (24 October 2026)
- Local patch artifact: `DR2C_VORENYX_ID_v2.3_localization_patch.zip` (the full binary patch remains outside public GitHub).
- Scope: `events/trade/camp-recruit.df`, `events/trade/cyoa-k-recruit.df`, and `events/trade/familiar-recruit.df`.
- 410 exact mapping rules hit; 432 literal occurrences changed; 427 inventory rows marked in v2.3.
- Inventory baseline: 541 files, 17,329 quoted occurrences, 13,038 unique literals.
- Heuristic likely player-facing delta: 3,809 / 10,844 = 35.13%; 6,270 probable unique untranslated candidates remain.
- Static checks and package CRC: PASS. Patch verifier: PASS.
- Runtime gameplay/save-load: NOT RUN. APK rebuild/signing: NOT PERFORMED.

## Coverage interpretation
Inventory percentages are approximate deltas, not semantic-completeness or actual in-game-screen metrics. Continue classifying candidates, reviewing full dynamic display expressions, and validating real gameplay surfaces before claiming 100%.

## Voice and slang policy
- Use natural gue/lo Indonesian and sentence-level rhythm. Profanity should be pointed and character-specific, not mechanically appended to every line.
- Localize joke intent and timing, not just individual words. Preserve references/proper names when translation would destroy the joke, while translating surrounding exposition and choices.
- Current slang changes quickly by platform and community. `ragnamok` remains niche/low-confidence; `jomok/perjomokan` can carry homophobic or sexualized insult; `cewe standar TikTok` is a contested social label and should not be treated as a universal fact.
- See `docs/VORENYX_VOICE_GUIDE_v2.3.md`, `docs/SLANG_RESEARCH_AND_EVIDENCE.md`, and the source links in the voice guide.

## Hard invariants
Preserve trait/perk/character IDs, stat keys, weapon IDs/constants, food costs, reward operations, CYOA IDs, trader counters, branch conditions, placeholders, newlines, tabs, display delimiters, and original campaign flow. Translate presentation text only; exact-context edits are preferred over global replacements.

## Next priorities
1. Continue event/NPC text in impact order, reviewing complete displayed expressions rather than isolated words.
2. Distinguish player-visible strings from internal/debug strings to improve the coverage denominator.
3. Run persona/grammar/UI-length QA and look for accidental English/Indonesian fragments.
4. Test menus, recruitment, trade, combat, transitions and save/load in a compatible runtime.
5. Rebuild/sign APK only after overlay stability is demonstrated.
6. Update checkpoint, changelog, inventory, diffs and QA reports for each batch.

## Public-repository boundary
Keep the user-provided archive and full extracted game scripts local-only. Public GitHub may contain project-authored documentation, research, sanitized summaries, and appropriate verification tools—not the APK, full game source, or binary overlay.

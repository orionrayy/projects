# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Name: DR2C VORENYX; base game: Death Road to Canada.
- First scope: Indonesian localization and title identity before large content expansion.
- Invariant: retain the original journey to Canada and do not create a mandatory replacement campaign.
- Voice: modern colloquial Indonesian; blunt, sarcastic and sometimes profane, with distinct NPC personas.
- 100% player-visible translation is the target, **not yet achieved**.

## Latest checkpoint — v2.1
- Latest patch: local artifact `DR2C_VORENYX_ID_v2.1_localization_patch.zip`.
- Scan baseline: 541 files; 17,329 literal occurrences; 13,038 unique literals.
- Heuristic player-facing occurrences: 10,843; changed: 3,494 (32.22%); probable untranslated unique candidates: 6,545.
- Latest pass: 187 rewrite hits across Shooting, Fitness, Mechanical, Army Surplus, Rifle Collector and Blade Master.
- Static integrity PASS; failures=[]; display markers balanced 229/229; ZIP CRC PASS.
- Runtime gameplay, save/load, APK rebuild/signing: NOT RUN / NOT PERFORMED.
- Reconciliation: v2.1 uses the v1.4 baseline and supersedes experimental v1.5/v1.6 outputs where some v1.4 mappings were reverted.

## Hard invariants
Preserve trait/perk and character IDs, stat keys (strength/fitness/medical/shooting/mechanical/mechanic), weapon IDs, food costs, reward operations, CYOA IDs, trader counters, branch conditions, placeholders, tabs/newlines, display delimiters and original campaign flow. Translate only presentation text.

## Style and slang
Use gue/lo, gak, udah, nih, dong, anjir/bjir where fitting. Gamer jargon such as loot/build/perk/trait/boss/grind may remain when natural. Slang is context- and persona-specific; do not force every meme into every line. “Cewe standar TikTok” is a contested social label. “Jomok/perjomokan” can carry homophobic/sexualized mockery and is not a generic insult. “Ragnamok” is low-confidence niche usage. See the style guide and slang research for evidence/confidence.

## Next tasks
1. Continue remaining player-facing dialogue and event options.
2. Scan whole display expressions for residual English; avoid unsafe global substring replacement.
3. Manually review grammar, voice fit, dynamic pronouns and UI length.
4. Test menu/event/trade/combat/save-load in the game runtime.
5. Rebuild/sign APK only after the overlay is stable.
6. Update memory, changelog, audits and history at every checkpoint.

## Release boundary
Do not claim full translation or runtime compatibility until evidence supports it. Public GitHub keeps authored docs and sanitized audits; it does not store the original APK or full extracted game scripts.

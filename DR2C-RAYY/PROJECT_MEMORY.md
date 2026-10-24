# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Base game: Death Road to Canada. Project name: DR2C VORENYX.
- Current scope: Indonesian localization and replacement title identity; larger expansions remain deferred.
- Invariant: preserve the original Canada-bound campaign flow.
- Target voice: natural colloquial Indonesian, blunt and sarcastic with occasional profanity, distinct NPC personas, and context-sensitive community slang.
- Target: 100% of player-visible text reviewed and localized; **not achieved yet**.

## Current checkpoint — v2.22 (24 October 2026)
- Patch artifact: `DR2C_VORENYX_ID_v2.22_localization_patch.zip`, available as a local conversation artifact. The binary overlay is not committed to public GitHub.
- Base checkpoint: v2.21.
- Scope: `events/camp/camp3.df`, `charstats-textfill.df`, `events/common/common4.df`, `events/rareloc/rare1.df`, plus two group-label helper macros in `cyoa-charstats.df`.
- 94 contextual display expressions rewritten; 183 existing literal tokens changed; 138 inventory rows newly marked localized.
- Inventory baseline: 541 source files, 17,329 quoted literal occurrences, 13,038 unique literals.
- Heuristic player-facing coverage: 7,490 / 10,844 = 69.07%; 2,822 unique literal candidates remain unmarked. These values do not establish semantic or runtime coverage.
- Static validation: PASS with zero reported structural failures. ZIP CRC: PASS.
- QA debt: validation report lists 49 mapping rules whose original source literals were not found after contextual rewrites. Do not count these as additional successful translations; reconcile them against the final source.
- Runtime gameplay/save-load tests: NOT RUN. APK rebuild/signing: NOT PERFORMED.

## Coverage interpretation
Inventory percentage is a heuristic. The denominator may contain fragments, identifiers or code-like strings, while a single displayed sentence can span multiple literal tokens. A 100% claim requires classifying every candidate, reviewing complete assembled player-visible expressions, reconciling mapping misses, checking placeholders and UI fit, and testing runtime surfaces.

## Voice and slang policy
- Prefer natural sentence-level Indonesian over literal token substitution.
- Use `gue/lo`, `gak`, `udah`, and profanity selectively according to speaker/persona.
- Preserve punchlines and consequences; do not turn every NPC into the same meme voice.
- `ragnamok` is niche/low-confidence; `jomok/perjomokan` may be derogatory or sexualized; `cewe standar TikTok` is a contested label. Use only when the scene clearly supports the reference.
- See `docs/LOKALISASI_ID.md` and `docs/SLANG_RESEARCH_AND_EVIDENCE.md`.

## Hard invariants
Preserve trait/perk/character IDs, stat keys, weapon IDs/constants, food costs, reward operations, CYOA IDs, trader counters, branch conditions, placeholders, interpolation, newlines, tabs, display delimiters and original campaign flow. Translate presentation text only. Prefer exact-context or complete-expression rewrites over global substring substitutions.

## Next priorities
1. Reconcile the 49 missed exact mapping rules in v2.22; determine which are already localized by previous rewrites and which remain English.
2. Reclassify the inventory semantically to exclude code/path/internal strings and include complete dynamic display expressions.
3. Continue the highest-impact player-visible event, route, trader, trait/perk, item and tutorial surfaces.
4. Audit grammar, register, profanity, character voice, UI length and accidental mixed-language sentences.
5. Run menus/events/trade/combat/save-load in a compatible runtime.
6. Rebuild/sign APK only after overlay compatibility is demonstrated.
7. Keep the README, changelog, inventory, checkpoint reports, version history and validation metadata synchronized.

## Public-repository boundary
Public GitHub stores project-authored documentation, research and sanitized audit summaries only. Do not commit the user-provided archive, full extracted game scripts, original APK or binary overlay.

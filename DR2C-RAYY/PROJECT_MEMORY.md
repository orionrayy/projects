# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Base game: Death Road to Canada. Project name: DR2C VORENYX.
- Current scope: Indonesian localization and replacement title identity; larger expansions remain deferred.
- Invariant: preserve the original Canada-bound campaign flow.
- Target voice: natural colloquial Indonesian, blunt and sarcastic with occasional profanity, distinct NPC personas, and context-sensitive community slang.
- Target: 100% of player-visible text reviewed and localized; **not achieved yet**.

## Current checkpoint — v2.23 (24 October 2026)
- Local patch artifact: `DR2C_VORENYX_ID_v2.23_localization_patch.zip`. The binary overlay and original archive remain outside public GitHub.
- Scope: contextual English-residue cleanup in `assets/deathforth/events/camp/camp3.df`.
- 51 distinct source literals localized across 52 literal occurrences.
- All 47 historical exact-mapping misses from the v2.22 `camp3.df` report repaired.
- Two other historical warnings reconciled: `Orange` is retained as a proper name; the old `common4.df` feast rule was stale because that exact literal was already absent after contextual rewriting.
- Current exact-mapping misses after reconciliation: 0.
- Static checks: quoted-literal count 177 before/after and line count 418 before/after; patch ZIP has 294 entries and CRC PASS.
- Coverage: 69.07% is the last measured heuristic from v2.22. The v2.23 metric has not been recomputed. It is not a semantic or runtime screen-coverage score.
- Runtime gameplay, UI fit, save/load and APK rebuild/signing: NOT RUN / NOT PERFORMED.

## Coverage interpretation
Inventory percentages are heuristic. The denominator may contain fragments, identifiers or code-like strings, while a single displayed sentence can span multiple literal tokens. A 100% claim requires classifying candidates, reviewing complete assembled player-visible expressions, checking placeholders and UI fit, and testing runtime surfaces.

## Voice and slang policy
- Prefer natural sentence-level Indonesian over literal token substitution.
- Use `gue/lo`, `gak`, `udah`, and profanity selectively according to speaker/persona.
- Preserve punchlines and consequences; do not turn every NPC into the same meme voice.
- `ragnamok` is niche/low-confidence; `jomok/perjomokan` may be derogatory or sexualized; `cewe standar TikTok` is a contested label. Use only when the scene clearly supports the reference.
- See `docs/LOKALISASI_ID.md` and `docs/SLANG_RESEARCH_AND_EVIDENCE.md`.

## Hard invariants
Preserve trait/perk/character IDs, stat keys, weapon IDs/constants, food costs, reward operations, CYOA IDs, trader counters, branch conditions, placeholders, interpolation, newlines, tabs, display delimiters and original campaign flow. Translate presentation text only. Prefer exact-context or complete-expression rewrites over global substring substitutions.

## Next priorities
1. Continue contextual review of the highest-impact remaining player-visible events, routes, traders, traits/perks, items and tutorial surfaces.
2. Rebuild the inventory QA pipeline so literal extraction cannot be confused by comments or code context, then reclassify candidates semantically.
3. Review grammar, register, profanity, character voice, UI length and accidental mixed-language expressions.
4. Recompute coverage from a validated merged overlay/base inventory; do not reuse the v2.22 metric as a v2.23 score.
5. Run menus/events/trade/combat/save-load in a compatible runtime.
6. Rebuild/sign APK only after overlay compatibility is demonstrated.
7. Keep README, changelog, inventory metadata, checkpoint reports and version history synchronized.

## Public-repository boundary
Public GitHub stores project-authored documentation, research and sanitized audit summaries only. Do not commit the user-provided archive, full extracted game scripts, original APK or binary overlay.

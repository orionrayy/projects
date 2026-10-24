# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Base game: Death Road to Canada. Project name: DR2C VORENYX.
- Current scope: Indonesian localization and replacement title identity; larger expansions remain deferred.
- Invariant: preserve the original Canada-bound campaign flow.
- Target voice: natural colloquial Indonesian, blunt and sarcastic with occasional profanity, distinct NPC personas, and context-sensitive community slang.
- Target: 100% of player-visible text reviewed and localized; **not achieved yet**.

## Current checkpoint — v2.25 (24 October 2026)
- Local patch artifact: `DR2C_VORENYX_ID_v2.25_localization_patch.zip`. The binary overlay and original archive remain outside public GitHub.
- Scope: two active dialogue files: `assets/deathforth/blurb/optimist.df` and `assets/deathforth/blurb/sc/wrestler.df`.
- 63 contextual mapping rules applied; 63 literal occurrences changed.
- The optimistic survivor's dialogue now uses conversational Indonesian; wrestler quips and dynamic description fragments use an irreverent character voice. Proper names, wrestling move names, censor-mask placeholders, and non-dialogue structure were preserved where required.
- Static structure: PASS. `optimist.df`: 29 quote tokens and 114 lines preserved; `sc/wrestler.df`: 34 quote tokens and 137 lines preserved. All mapped English source residues in these batches are absent from the target.
- Package: 305 ZIP entries; CRC PASS; no duplicate paths; 304 manifest-listed file hashes verified with zero mismatches; no machine-local path leaks.
- Artifact SHA-256: `693714b5f2a1e79f0e8b5c9749f7f4dfe1c6ffaa4dc891d0ee689549f82f7fe5`.
- Coverage: 69.07% is the last measured heuristic from v2.22. No current global coverage measurement has been made for v2.25; do not report it as current coverage or semantic completeness.
- Runtime gameplay, UI fit, save/load, and APK rebuild/signing: NOT RUN / NOT PERFORMED.

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
1. Refresh the historical untranslated-candidate queue with a comment-aware parser after merging the current base/overlay, then manually classify likely player-facing expressions.
2. Continue contextual localization across high-impact event, route, trader, item, trait/perk, and tutorial surfaces.
3. Review grammar, register, profanity, character voice, UI length and accidental mixed-language expressions.
4. Recompute coverage only from a validated merged base/overlay inventory; maintain a clear distinction between heuristic coverage and semantic/runtime completeness.
5. Run menus/events/trade/combat/save-load in a compatible runtime.
6. Rebuild/sign APK only after overlay compatibility is demonstrated.
7. Keep README, changelog, inventory metadata, checkpoint reports and version history synchronized.

## Public-repository boundary
Public GitHub stores project-authored documentation, research and sanitized audit summaries only. Do not commit the user-provided archive, full extracted game scripts, original APK or binary overlay.

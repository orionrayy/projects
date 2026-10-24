# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Base game: Death Road to Canada. Project name: DR2C VORENYX.
- Current scope: Indonesian localization and replacement title identity; larger expansions remain deferred.
- Invariant: preserve the original Canada-bound campaign flow.
- Target voice: natural colloquial Indonesian, blunt and sarcastic with occasional profanity, distinct NPC personas, and context-sensitive community slang.
- Target: 100% of player-visible text reviewed and localized; **not achieved yet**.

## Current checkpoint — v2.26 (24 October 2026)
- Local patch artifact: `DR2C_VORENYX_ID_v2.26_localization_patch.zip`. The binary overlay and original archive remain outside public GitHub.
- Scope: five special-character dialogue/emote profiles: `sc/beeman.df`, `sc/boxer.df`, `sc/caveman.df`, `sc/knight.df`, and `sc/ninja.df`.
- 66 exact-context mappings applied; 66 literal occurrences changed.
- The batch gives Beeman an encouraging casual voice, Boxer concise training banter, Caveman blunt time-travel humor, Knight a restrained chivalric register, and Ninja concise action/emote descriptions.
- Static structure: PASS. Token counts and line counts remain unchanged in all five files, non-string source skeletons match, and no mapped English source residues remain.
- Package: 312 ZIP entries; CRC PASS; no duplicate paths; 311 manifest-listed files verified with zero hash mismatches; no machine-local path leaks.
- Artifact SHA-256: `edda11648c4f7ed32d1413b154fd70e65943edfb367f18c6bffa0b5119a3f02c`.
- Coverage: 69.07% is the last measured heuristic from v2.22. No current global coverage measurement has been made for v2.26. It is not a semantic or runtime screen-coverage score.
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


## Active checkpoint — 24 October 2026, v2.35
- Canonical latest artifact: `DR2C_VORENYX_ID_v2.35_localization_patch.zip` (local release, not committed to the public repository).
- Batch: 32 complete display expressions and 9 direct literal occurrences across 12 files, including game-mode explainers, journey planning, mission/reward dialogue, gym/coffee/factory encounters, the generator puzzle, broom/portal characters and Mountie Alpha-end text.
- Static source/ZIP integrity: PASS; archive 362 entries, 361 manifest entries, no duplicate paths, no manifest digest mismatches, no local path leaks. SHA-256: `df3cd3840b3a6f32e5861b976045112ee790db6e472ae512ebac8d2e1b4fcee1`.
- Comment-aware inventory: 541 source files, 16,827 active string tokens. Residual queue: 129 candidate rows / 67 files; it is for triage, not a coverage score.
- Historical 69.07% figure is v2.22-only and stale. Global semantic coverage, runtime/UI fit/save-load tests, and APK rebuild/signing remain unverified.
- Metadata correction: the v2.34 checkpoint and embedded ZIP hash/size were inconsistent with its actual archived contents. v2.35 reconciles the v2.34 checkpoint and audit to the actual nine-file scope before proceeding.

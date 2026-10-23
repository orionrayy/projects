# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Base game: Death Road to Canada. Project name: DR2C VORENYX.
- Current scope: Indonesian localization + replacement title identity; larger sci-fi/Renaissance/business expansions deferred.
- Invariant: retain the original Canada-bound journey and do not add a mandatory replacement campaign.
- Target voice: colloquial Indonesian, blunt, sarcastic, sometimes profane, with distinct NPC personas.
- 100% player-visible translation is the target, **not yet achieved**.

## Current checkpoint — v2.2
- Patch artifact: `DR2C_VORENYX_ID_v2.2_localization_patch.zip`.
- Audit baseline: 541 files; 17,329 quoted literal occurrences; 13,038 unique literals.
- Heuristic player-facing occurrences: 10,844; changed 3,509 (32.36%); probable untranslated unique candidates: 6,531.
- This batch fixes 15 contextual player-visible English literals in `weapons.df`: seller interruption lines, robbery/choice labels, premium stock prompt, medieval-axe label/description, anime-truck intro and catchphrase.
- Targeted residue scan: 0 matches. Display markers in `weapons.df`: 157/157. Static report PASS and ZIP CRC PASS.
- The v2.1 folder report and embedded ZIP report previously disagreed; v2.2 corrects affected visible strings and regenerates/validates the embedded report.
- Runtime gameplay, save/load, APK rebuild/signing: NOT RUN.

## Hard invariants
Preserve all trait/perk/character IDs, stat keys, weapon IDs/constants, food costs, reward operations, CYOA IDs, trader counters, branch conditions, placeholders, newlines, tabs, display delimiters and original campaign flow. Translate presentation text only.

## Slang policy
Use gue/lo, gak, udah, nih, dong, anjir/bjir when character/context supports it. Keep gamer jargon if natural; avoid forcing memes into every line. “Cewe standar TikTok” is a contested label; “jomok/perjomokan” can carry homophobic/sexualized mockery; “ragnamok” remains low-confidence niche usage. See the style matrix, glossary and research evidence.

## Next priorities
1. Continue remaining player-facing trader, event, NPC and system strings.
2. Scan full display expressions for residual English; avoid global substring replacement.
3. Review dynamic pronouns, grammar, persona consistency and UI length manually.
4. Test menus, events, purchases/robbery, combat, transitions and save/load in runtime.
5. Rebuild/sign APK only after stability is proven.
6. Update project memory, changelog, inventory, reports and history diffs per checkpoint.

## Public repo boundary
Public GitHub contains authored docs, research and sanitized audit summaries; the original APK and full extracted game scripts are not committed. Full local archive includes user-provided base archive and latest overlay patch.

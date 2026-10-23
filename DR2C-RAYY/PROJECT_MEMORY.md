# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity

- Project name: DR2C VORENYX.
- Base game: Death Road to Canada.
- First scope: Indonesian localization and replacement title identity before any large content expansion.
- Main invariant: the original trip toward Canada and the existing campaign remain unchanged. New atmosphere, dialog, and optional event variation must not become a mandatory replacement campaign.
- Current checkpoint: v1.3 QA repair.
- Translation target: every player-visible menu, event, NPC line, choice, item, trait/perk label, stat description, location and system prompt. This remains incomplete.

## Source baseline and audit

- User-provided input archive: DR2C-RAYY.zip.
- Local extracted script root used in the build environment: /mnt/data/vorenyx_work/DR2C-RAYY.
- Files scanned: 541.
- Quoted literal occurrences: 17,329.
- Unique literal values: 13,038.
- Likely player-facing occurrences (heuristic): 10,843.
- Likely player-facing occurrences changed (heuristic): 3,186.
- Current estimated change coverage: 29.38%.
- Unique probable player-facing candidates still marked untranslated: 6,813.
- Do not interpret those values as measured runtime coverage. Concatenated strings, code/data keys, image-baked text and engine-native UI need separate review.

## Latest checkpoint — v1.3

- Latest patch package: DR2C_VORENYX_ID_v1.3_localization_patch.zip.
- Last localized subsystem: weapon traders in assets/deathforth/events/trade/weapons.df — Blunt Master, Polearm Pal and Silent But Deadly.
- Static integrity: PASS.
- Skipped exact rewrite guards: 0.
- Static failures: 0.
- ZIP CRC: PASS.
- Runtime gameplay: NOT RUN.
- Save/load: NOT RUN.
- APK rebuilt/signed: NOT PERFORMED.
- New title artwork exists locally, but full-menu background integration has not been runtime-verified.

## Implementation invariants

Never translate or rename internal identifiers just because they resemble English. Preserve:
- trait/perk identifiers and character IDs;
- stat keys such as strength, fitness, medical, shooting, mechanical and mechanic;
- weapon IDs/constants and reward operations;
- food costs, trader counters and purchase conditions;
- CYOA identifiers and control flow;
- placeholders, line breaks, tab-sensitive script layout, display-expression delimiters;
- original ending and Canada-bound journey logic.

Translate presentation text, not game logic.

## Voice policy

- Default colloquial register: gue/lo, gak, udah, nih, dong; profanity and blunt sarcasm are allowed where the character would use them.
- Blunt weapons seller: expressive, loud, proud of her stock, self-mocking humor.
- Polearm seller: DIY/weapons nerd; more technical, but still casual.
- Silent-weapons seller: concise, controlled, dry confidence.
- Chatty characters may use “ngoceh/yapping” in fitting contexts.
- Keep established gameplay jargon like loot, build, perk, trait, boss, and grind when that sounds natural to Indonesian players.
- Modern slang must support the joke or persona, not replace the whole sentence.
- “Cewe standar TikTok” is a contested social-media label, not a factual claim about all women.
- “Jomok/perjomokan” is niche and may carry homophobic/sexualized mockery; do not use it as a generic insult at real-world identities.
- “Ragnamok” is treated as low-confidence niche meme usage pending stronger cross-community evidence.
- Keep slang terms contextual and revisable.

## Priority queue

1. Continue the untranslated parts of trade/weapons.df; then prioritize other high-density trade files: oldtrade.df, training.df, supplies.df and rare.df.
2. Resolve remaining strings by complete display expression, not only by isolated fragments.
3. Add per-file mixed-language residue scans and human review for grammar, voice fit and UI length.
4. Retain static checks for display-expression balance, mechanic sentinels and ZIP CRC.
5. Run runtime menu/event smoke tests and save/load tests if a runnable environment is available.
6. Only after stability is demonstrated, rebuild and sign the Android APK.
7. Update this memory, CHANGELOG and audit reports at every new checkpoint.

## Public release policy

Do not claim 100% localization, runtime compatibility, or release readiness until the relevant checks are performed and pass. The public repository should contain project-authored documentation and tools, not the original APK or a complete extraction of the game's scripts.

# DR2C VORENYX v2.46 — Multianalysis of Residual English

**Baseline APK:** `DR2C_VORENYX_v2.46_UI_LOCALIZED_TEST.apk`  
**SHA-256:** `6d4e2f3df07d199807c08418ae5d30b9927e5b2e36c780a51858045336b29313`  
**Coverage:** 509 packaged `.df` scripts. Runtime on the user's device has not been independently re-tested.

## Results

- 3,624 dynamic display templates extracted.
- 9,890 standalone literals extracted.
- 443 P1 player-facing English-like candidate occurrences.
- 55 P2 candidate occurrences.
- 199 short-label/title/shout candidates.
- 677 unique normalized candidate phrases.
- 430 items flagged for language/context review.
- 138 candidate phrases in developer/test areas.
- 3,332 ASCII English-like strings in native libraries; these include middleware error messages and identifiers, not all game UI.

The classifier combines English dictionary coverage, function-word density, consumer/context tokens, and code-area heuristics. It is a triage model, not a calibrated language detector and does not compute semantic localization coverage.

## Hotspots

| File | P1 candidate occurrences | Finding |
|---|---:|---|
| `events/trade/oldtrade.df` | 76 | Biggest visible gap: item-trade descriptions, option labels, gas, ammo, medical trades and robbery outcomes |
| `events/common/PANCREAS.df` | 11 | Character/perk/weapon mechanics and instructions |
| `don/events/common/015-graves.df` | 9 | Event narrative and choices |
| `events/exterior/region/frozen.df` | 8 | Character/region description |
| `events/exterior/junk-maker.df` | 8 | Encounter narrative and choices |
| `don/events/common/003-vortex.df` | 8 | Encounter narration and choice labels |
| `events/trade/rare.df` | 7 | Rare trade/event text; mixed Indonesian/English |
| `mission-events.df` | 7 | UI prompts and mission transitions need context-sensitive review |
| `perkdef.df` | 7 | Several “APPLIED ON CHAR” strings are emitted through `type/print`; likely diagnostic, not ordinary UI |
| `events/locationlogic.df` | 7 | Forecast labels such as SWARM SIZE and AGGRESSION mixed with already translated text |
| `events/city/region/special-lots.df` | 5 | Static player-facing location choices; relatively safe to localize |

## Native library scan

| Library | English-like candidates |
|---|---:|
| `libmain.so` | 2,035 |
| `libSDL2_image.so` | 576 |
| `libSDL2.so` | 527 |
| `libSDL2_mixer.so` | 92 |
| `libpairipcore.so` | 68 |
| `libsmpeg2.so` | 19 |
| `libhidapi.so` | 15 |

These counts include error strings, graphics/audio decoder diagnostics, engine internals and third-party runtime text. Only verified player-facing strings in `libmain.so` should be changed, using exact offsets and slot-size checks. PairIP/middleware strings are out of localization scope.

## Multi-axis findings

1. **Visible completeness:** choices and event narration dominate the remaining English. `oldtrade.df` is the most impactful next module.
2. **Consistency:** many lines are mixed, with English clauses attached to Indonesian text in barter/trade outcomes and forecast panels.
3. **Code integrity:** some candidates are internal tokens/logs, such as `DAY-PICK-DECK5 RECRUIT`, `old-total-kills:`, and `door-no-escape`; these must not be translated as UI.
4. **Dynamic text:** player names/groups are interpolated through `cname`, `pname`, `Thegroup`, and templates. Translate only literal segments and preserve markup/placeholders.
5. **Semantic nuance:** proper names, weapon names, brand/title terms and slang require editorial review rather than automatic word replacement.
6. **Syntax:** a separate scanner reports two potential unclosed-string units in `cheevos.df` and `filesave.df`. Because these files contain multiline/comment-heavy constructs and this is a lightweight scanner, these are warnings, not confirmed runtime defects.
7. **Runtime gap:** the screenshots that prompted the v2.46 patch predate independent testing of that APK on the device. Static patch presence does not confirm those screens have changed in the installed game.

## Recommended order

1. Translate static location choices in `events/city/region/special-lots.df` and simple weapon trade choices in `events/trade/oldtrade.df`, without changing attached handler names.
2. Translate `oldtrade.df` event narratives per event; preserve variables, markup and handler/state tokens.
3. Localize ability descriptions and hints in `events/common/PANCREAS.df`, followed by rare events.
4. Review native `libmain.so` labels and hints using exact offsets and same-length slot constraints.
5. Re-scan all scripts for syntax regressions, compare handler/token structure, validate APK integrity, and test active screens on device.

A 38-row next-wave translation review queue is provided separately as `DR2C_VORENYX_v2.46_NEXT_WAVE_REVIEW_QUEUE.csv`. The queue is a recommendation; it has not been applied to the APK. Do not claim 100% Indonesian coverage based on candidate counts alone.

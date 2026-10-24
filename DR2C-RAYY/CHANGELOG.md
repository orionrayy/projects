# Changelog — DR2C VORENYX

- **v2.43 APK candidate (updated signing):** APK assembled locally, then verified using Android SDK Build Tools 35.0.1 apksigner; signature schemes v1/v2/v3 PASS. SHA-256 `3019dd04098e9e8fef01045a2e391d9525bf87ef6874b0d0049c5a073a052f25`. Static packaging PASS; Android install/launch/gameplay/UI/save-load/stability tests NOT RUN. Original publisher key absent and PairIP/Play license checks may reject the locally signed package. APK remains local-only. See [APK build report](docs/APK_BUILD_v2.43.md).

- **v2.43 APK candidate build:** assembled the v2.43 overlay into the supplied extracted Android package and applied a local JAR/v1 signature. Static package/manifest/hash/signature/ZIP/ABI checks PASS. Android install, launch, gameplay, UI fit, save/load and stability remain NOT TESTED; PairIP/Play license checks may reject re-signed package. APK remains local-only; see [APK build report](docs/APK_BUILD_v2.43.md).

- **v2.43:** localized 159 quoted-string occurrences across 58 files, including 9 newly overlaid modules. Static string/code/path checks passed, zero unmatched rules, local ZIP manifests validated. Recheck of the inherited 598-row heuristic queue shows 131 active candidate rows (down from 241 after v2.42); not a semantic coverage metric. Runtime not tested.

- **v2.42:** localized 309 quoted-string occurrences across 16 overlay files. Targeted residual cleanup covers selected character banter, epilogue/finale text, NPC dialogue, encounter choices, and mission labels. Line/string-token counts, non-string code, and resource paths preserved; zero unmatched rules; ZIP and manifest checks PASS. Global coverage not computed; runtime not tested.

- **v2.41:** localized 15 previously unoverlaid character-banter modules, ending/credits, human combat barks, and priority CYOA headings/choices; corrected the display-only `Shotgunner` label to `Ahli Shotgun` without changing the canonical key. 453 literal occurrences changed across 24 files. Static checks and local patch ZIP integrity passed; global coverage not computed; runtime not tested.

- **v2.40:** repaired 45 canonical trait/perk machine-key mismatches across 13 modules; 0 remain across 195 operand comparisons. Continued contextual Indonesian localization and refreshed the title badge. Static validation PASS; global semantic coverage not computed; runtime/UI/save-load/APK rebuild not tested.
- **v2.39:** localized 32 complete display expressions and 7 direct literal occurrences across CYOA examples and moment interactions. Static checks passed; runtime not tested.
- **v2.38:** localized 14 display expressions and 18 direct literal occurrences across 11 actual files. Static checks passed; runtime not tested.
- **v2.37:** localized 25 display expressions and 6 direct literal occurrences. Static checks passed; runtime not tested.


- **v2.36:** localized 45 complete display expressions and 12 direct literal occurrences across 31 modules. Focus: arcade-defense tutorial, bandit-defense rewards, bodybuilder/hero and siege encounters, shops/fairies/parks, city rangers and pandas, character blurbs, perk/trait help, and epilogue fragments. Static validation and package integrity PASS; triage queue now 77 rows in 36 files; global coverage not computed; runtime not tested.
- **v2.35:** 32 complete display expressions and 9 direct literal occurrences across 12 files; game modes, route planning, missions/rewards, gym/coffee/factory encounters, generator puzzle, broom/portal interactions, and Mountie Alpha-end text. Metadata reconciled for v2.34; static validation PASS; global coverage not computed; runtime not tested.
- **v2.34:** 25 complete display expressions and 3 direct literal occurrences across nine files: sewer/tutorial, Canada crossing, hazmat, Santa/Billy, common encounter, Bogan, daily medical CYOA, and special trader-camp items. Checkpoint/ZIP metadata reconciled in v2.35.
- **v2.33:** 31 display expressions and 9 direct literals across nine trader/DMV/junk-maker/character/graves modules. Static checks pass; global coverage not computed; runtime not tested.

- **v2.26:** contextual Indonesian localization for Beeman, Boxer, Caveman, Knight and Ninja dialogue/emotes across five files; 66 mappings and 66 occurrences; static structure PASS; coverage not remeasured; runtime not tested.
- **v2.25:** contextual Indonesian localization in the active optimistic-survivor profile and wrestler response profile; 63 mapping rules and 63 occurrences changed; both files preserve source line/token counts; ZIP CRC and manifest checks PASS; global coverage not remeasured; runtime not tested.
- **v2.24:** contextual Indonesian localization of character personality banter and shared chatter across seven files; 277 mapping rules; 279 literal occurrences changed; two father-topic word-order fixes; static structure, ZIP CRC, and manifest validation PASS; coverage not remeasured; runtime not tested.
- **v2.23:** contextual English-residue repair in `camp3.df`; 51 unique source literals and 52 literal occurrences localized; all 47 historical camp3 mapping misses repaired; two non-actionable historical rules reconciled. Coverage heuristic not recomputed; runtime not tested.

- **v0.1:** VORENYX title identity/artwork and initial UI/general text.
- **v0.2–v0.3:** literal maps, NPC style matrix, slang research and identifier protections.
- **v0.4–v0.7:** contextual event passes, bandits/recruitment/classes, common events and sentence-level QA.
- **v0.8–v1.8:** trader-camp, weapons vendors, trainers, contextual event and exact-literal/tab QA passes.
- **v1.9–v2.1:** Army Surplus, Rifle Collector, Blade Master and reconciled trainer/vendor localization.
- **v2.2:** fixes 15 player-visible English literals in weapon traders; targeted residue scan 0 matches; embedded static report and ZIP CRC PASS.
- **v2.3:** contextual survivor recruitment dialogue and sourced Indonesian voice/slang guide; static QA/ZIP CRC PASS.
- **v2.4–v2.20:** progressive contextual localization across events, characters, routes, traders, tutorial, camping, encounters, traits/perks and item text. Coverage values are heuristic inventory deltas.
- **v2.21:** quality-focused exact-context pass for UI, vehicle, city, vendor and perk/trait text; 92 rules and occurrences reported matched.
- **v2.22:** rewrites 94 complete display expressions in camp survival choices, character bio and selected encounters; 183 existing literal tokens changed and 138 inventory rows newly marked. Inventory heuristic is 69.07%. Static structure and ZIP CRC PASS; 49 exact mapping rules are recorded as missed after contextual rewrites and require reconciliation. Runtime/save-load/APK rebuild not tested.

## Status limits
Full Indonesian localization is incomplete. Inventory percentages are not semantic or runtime screen coverage. The public repository contains documentation and sanitized audit summaries, not the original APK, extracted game scripts or binary overlay.

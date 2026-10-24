# Conversation Decision History

## Concept selection

Initial design brief asked for three independent big-modpack concepts: sci-fi, Renaissance, and business expansion. The chosen first milestone was deliberately simpler: launch the DR2C VORENYX identity and full Indonesian localization before starting large content expansions.

The three original concepts remain deferred:
- Dead Signal — Last Frequency (science-fiction signal mystery).
- Ashen Renaissance — The Dying Age (dark Renaissance/clockpunk).
- Dead Economy — Business Must Survive (trade/logistics ecosystem).

## Localization design decisions

- Name the mod: DR2C VORENYX.
- Add a new title identity/title-screen artwork and small logo/splash replacements.
- Use Indonesian across player-visible strings, with slangy, frontal, sarcastic voice aligned to Death Road to Canada's irreverent dialogue.
- Study Indonesian gamer communities, TikTok/meme speech and contemporary slang as contextual evidence.
- Terms such as “ragnamok”, “perjomokan” and “cewe standar TikTok” must be evaluated by context and confidence, not inserted indiscriminately.
- Keep campaign flow unchanged; no mandatory new campaign or ending.
- Preserve game logic identifiers and mechanics while changing presentation text.

## Quality decisions

- Early broad phrase replacement caused risk of unnatural mixed-language grammar.
- Strategy shifted toward exact string and complete display-expression replacements.
- Labels that share values with internal IDs were separated conceptually; keys such as strength, fitness, medical, shooting, mechanical and mechanic remain protected.
- v1.2 QA warning came from redundant exact-rewrite attempts and a mismatched tab indentation in the sledgehammer event.
- v1.3 removes redundant checks and fixes the exact pattern: zero skipped rewrites, zero static failures, ZIP CRC PASS.

## Non-claims carried forward

The project is not 100% translated yet. Runtime gameplay, save/load and APK rebuild/signing have not been tested. Continue tracking these limits in every release note.


## Checkpoint v2.22 — 24 October 2026

- Confirmed local artifact: `DR2C_VORENYX_ID_v2.22_localization_patch.zip`; ZIP has 292 entries and `ZipFile.testzip()` reports no CRC errors.
- Inventory heuristic: 7,490/10,844 = 69.07%; 138 rows newly marked, 94 display expressions rewritten, 183 existing literal tokens changed.
- Static structural report: zero structural failures. The four expression-only files preserve line and literal-token counts; the helper file intentionally adds two group-label helper literals and two lines.
- The validation report lists 49 exact mapping rules whose original source literals were not found after contextual rewrites. Treat these as QA debt, not successful exact matches; reconcile whether each was superseded by a full-expression rewrite or still needs translation.
- User requested continued localization to 100%, with quality prioritized over the percentage. Avoid global pronoun/verb substitutions; inspect complete display expressions and preserve dynamic placeholders and game logic.
- Public GitHub is used for project memory, authored documentation and sanitized audit reports. Keep the binary overlay and source archive out of the public repo.

## Checkpoint v2.23 — 24 October 2026

- Local patch artifact: `DR2C_VORENYX_ID_v2.23_localization_patch.zip`; 294 ZIP entries and CRC PASS.
- Repaired 47 historical exact-mapping misses in `camp3.df` and localized four additional display residues, for 51 distinct literals / 52 occurrences.
- Reconciled two other historical warnings as non-actionable; remaining exact-mapping misses: 0.
- Structure check preserved the file's 177 quoted-literal tokens and 418 source lines. Newline/tab sequence in the pitchfork event was retained.
- Last measured coverage remains the v2.22 heuristic (69.07%); it was not recomputed for v2.23. Do not claim full localization.
- Runtime gameplay, UI fit, save/load and APK rebuild/signing remain untested. Public GitHub stores sanitized reports, not the original archive or binary overlay.

## Checkpoint v2.24 — 24 October 2026

- Local artifact: `DR2C_VORENYX_ID_v2.24_localization_patch.zip`; 301 ZIP entries, CRC PASS, 300 manifest files verified, zero hash mismatches.
- Contextual Indonesian localization batch covers seven character/shared-banter files: 277 mapping rules and 279 literal occurrences changed.
- Two dynamic father-topic phrases reordered to natural Indonesian while preserving literal-token counts and source structure.
- All seven touched files passed independent source-skeleton checks; quoted-literal counts and line counts remained stable. Fourteen English oneliners previously found in the `sharp` profile were included in final QA.
- Last measured coverage remains the v2.22 heuristic baseline (69.07%); it has not been recomputed for v2.24. Full localization is not complete.
- Runtime gameplay, UI fit, save/load and APK rebuild/signing remain untested. Public GitHub stores sanitized records only, not the original archive or binary overlay.

## Checkpoint v2.25 — 24 October 2026

- Local artifact: `DR2C_VORENYX_ID_v2.25_localization_patch.zip`; 305 ZIP entries, CRC PASS, no duplicate paths, 304 manifest files verified, zero hash mismatches, no local-path leaks.
- Localized active optimistic-survivor and wrestler dialogue in `optimist.df` and `sc/wrestler.df`; 63 mapping rules, 63 literal occurrences changed.
- Both files passed source-structure checks: 29/29 quoted tokens and 114/114 lines in `optimist.df`; 34/34 tokens and 137/137 lines in `sc/wrestler.df`.
- Current global coverage was not recomputed. The last measured heuristic remains the v2.22 baseline of 69.07%, not a v2.25 score and not semantic completeness.
- Runtime gameplay, UI fit, save/load and APK rebuild/signing remain untested. Public GitHub stores sanitized records only, not original archive, extracted scripts or binary overlay.

## Checkpoint v2.26 — 24 October 2026

- Local patch: `DR2C_VORENYX_ID_v2.26_localization_patch.zip`; 312 ZIP entries, CRC PASS, zero duplicate paths, 311 manifest entries verified, zero hash mismatches, and no local-path leaks.
- Localized Beeman, Boxer, Caveman, Knight and Ninja dialogue/emotes in five special-character scripts; 66 exact-context mappings and 66 literal occurrences changed.
- Each touched file preserves its quoted-literal count, line count and non-string source skeleton; all mapped English source residues are absent.
- Last measured coverage remains the v2.22 heuristic baseline of 69.07%. It has not been recalculated for v2.26 and does not mean semantic completeness.
- Runtime gameplay, UI fit, save/load and APK rebuild/signing remain untested. Public GitHub stores sanitized documentation/audit records only, not the original archive, full scripts or binary overlay.



## v2.35 continuation and v2.34 integrity correction — 24 October 2026
- Continue by treating the ZIP archive itself as the source of truth whenever an extracted working folder differs.
- Corrected v2.34's stale checkpoint scope: actual batch scope is nine modules (sewer/tutorial, Canada crossing, hazmat, Santa/Billy, common4, Bogan, daily medical CYOA, and special trader-camp region inventory), not carlogic/car1/camp2.
- Removed stale embedded v2.34 archive digest fields in the packaged audit and moved release checksums to an adjacent SHA-256 sidecar to avoid circular hashing.
- v2.35 covers 32 contextual display expressions plus 9 direct literals over 12 files. Static integrity PASS; no global semantic coverage claim; no runtime or APK build claim.
- Public GitHub remains documentation and sanitized audit only; the complete overlay ZIP/source is not published in the repository.


## Checkpoint v2.36 — 24 October 2026
- Actual base was the v2.35 packaged ZIP, not a stale extracted working directory.
- Localized 45 complete display expressions and 12 direct literal occurrences across 31 modules, emphasizing arcade-defense instructions, bandit-raid rewards, route encounters, shop/fairy/park dialogue, character voice, perk/trait guidance and epilogue text.
- Independent validator passed: ZIP CRC, 375-entry SHA-256 manifest, no duplicate paths, no mismatches, no machine-local path leaks; 31 scoped files preserved line counts, source skeleton, CYOA/choice IDs and route-path literals.
- Current comment-aware inventory: 541 files / 16,819 active quoted-string tokens; 77 heuristic candidate rows across 36 files remain. This is triage, not coverage. The stale v2.22 heuristic remains 69.07%; current global semantic coverage is not computed.
- Gameplay/runtime, UI fit, save/load and APK rebuild/signing are not tested. GitHub holds sanitized documentation/audits only, not the archive or overlay.

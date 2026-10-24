# DR2C VORENYX v2.40 — Untouched and Ambiguous Surface Review

**Status: audit findings recorded; no source overlay changed by this review pass.**

## Verified source inventory

- Base Deathforth source: 509 .df files; 541 .df/.txt files in the text inventory.
- Current overlay contains 244 .df files.
- 265 source .df files (52.06%) have no overlay file.
- The v2.40 build ledger identifies 78 script files changed in this build; the overlay also contains prior-build files not changed in v2.40.

## Freshly scoped review queue

The active v2.40 inventory contains 16,834 literal records. A review filter using inherited v2.39 English-likelihood scores >=0.5 and at least four English-word tokens yields 598 candidate rows across 116 files. This is a triage queue, not a confirmed count of untranslated player-visible strings. Scores are inherited from exact file/literal matches and have not been recalibrated for this build.

- 91 rows have scores >=0.7.
- 507 candidate rows are outside test/CYOA-test files.
- 183 candidates occur in files with no overlay.
- 163 candidates occur in overlay files not changed in v2.40.
- 252 candidates occur in files changed in v2.40 but the candidate literal is still present.
- 583 of 598 candidates match literal values found in the original source.
- 89 candidate literals begin or end with whitespace and should be reviewed as complete assembled expressions.
- A further 305 new/changed literal records have no inherited score; 16 trigger a simple common-English lexicon scan. These need human review and are not automatically errors.

## High-priority areas

1. Character banter/profile text in unoverlaid modules such as `blurb/sc/anime.df`, `blurb/sc/catlady.df`, `blurb/sc/fireproof.df`, `blurb/sc/madsci.df`, `blurb/sc/gnomey.df`, `blurb/sc/mandible.df`, `blurb/sc/skelknight.df`, and `blurb/sc/woodwoman.df`.
2. End-of-run text in `events/finale/ending-bits.df`, which has no overlay.
3. Remaining English in partially localized `mission-events-human.df`, `events/finale/epilogue-check.df`, `blurb/sc/omentum.df`, `events/common/DRTC_Q_UPDATE.df`, `events/common/PANCREAS.df`, and other event files.
4. CYOA titles/choices, including remaining untranslated tutorial, siege, recruitment, and scepter-event labels.
5. Complete-expression reconstruction for fragments containing leading/trailing spaces and dynamic variables.
6. Editorial glossary review for firearm terminology. The current “Shotgunner” display mapping uses “Ahli Senapan Gentel”; dictionary evidence defines *gentel* as a pellet/granule, so the localized weapon term needs to be standardized. See https://kbbi.web.id/gentel and https://kbbi.web.id/senapan.

## Ambiguity policy

- Preserve machine keys and identifiers; translate the display label only at a rendering boundary.
- Do not automatically translate game titles, parody names, intentionally mysterious labels, or technical control tokens until their runtime role is verified.
- Separate test fixtures and build metadata from the player-visible coverage denominator.
- A fresh lexical score or an empty inherited residual queue is not proof of completeness.
- Global semantic coverage remains **NOT COMPUTED**. Gameplay, UI-fit/overflow, save/load, and APK rebuild/signing remain **NOT RUN / NOT PERFORMED**.

## Required next pass

1. Localize clear player-facing titles, choices, combat barks, and ending summaries.
2. Prioritize the untouched character-profile modules and `ending-bits.df`.
3. Reconstruct whitespace-bound fragments into complete display expressions before translating.
4. Standardize weapon and gameplay terminology and check every display label against its canonical key.
5. Re-score the merged current inventory rather than reusing historic per-literal scores.
6. Run in-game tests for CYOA, recruitment, combat barks, traders, tutorial, ending, and character panels before claiming full coverage.

# Build and Validation — v2.25

## Static verification evidence
- Local patch artifact: `DR2C_VORENYX_ID_v2.25_localization_patch.zip`.
- ZIP package: 305 entries; CRC scan PASS; zero duplicate paths.
- SHA-256 manifest: 304 listed files, all hashes verified with zero mismatches; no runner-local path leaks.
- Scope: two active dialogue files: `assets/deathforth/blurb/optimist.df` and `assets/deathforth/blurb/sc/wrestler.df`.
- 63 contextual mapping rules; 63 literal occurrences changed.
- `optimist.df`: 29 quoted tokens and 114 lines before/after.
- `sc/wrestler.df`: 34 quoted tokens and 137 lines before/after.
- Mapped source residue scan: zero mapped English source literals remain in the two edited files.
- Proper names, wrestling move names, censor-mask placeholders and non-dialogue structure were preserved where required.
- Artifact SHA-256: `693714b5f2a1e79f0e8b5c9749f7f4dfe1c6ffaa4dc891d0ee689549f82f7fe5`.

## Coverage status
The last available heuristic measurement is v2.22: 7,490/10,844 = 69.07%. It has not been recomputed for v2.25 and is not a current coverage score, semantic completeness estimate, or runtime screen-coverage measure. The historical untranslated-candidate queue must be rebuilt with a comment-aware parser before broad triage.

## Not tested
- Runtime gameplay and actual UI layout/fit: NOT RUN.
- Save/load: NOT RUN.
- APK rebuild/signing: NOT PERFORMED.
- ZIP/hash integrity does not prove compatibility with a specific installed game version. Treat the artifact as an overlay, not a rebuilt APK.

## Reproduction / review
Keep the original user-provided archive read-only. Back up target data and confirm game version/path before applying an overlay. Test menus, camp branches, character dialogue, trade costs/rewards, transitions and save/load in a compatible runtime.

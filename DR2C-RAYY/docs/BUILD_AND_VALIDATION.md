# Build and Validation — v2.24

## Static verification evidence
- Local patch artifact: `DR2C_VORENYX_ID_v2.24_localization_patch.zip`.
- ZIP package: 301 entries; CRC scan PASS; no duplicate paths.
- SHA-256 manifest: 300 listed files, all hashes verified with zero mismatches.
- Scope: character personality and shared banter in seven scripts: `aggressive.df`, `passive.df`, `pessimist.df`, `dull.df`, `sharp.df`, `blurbdeck.df`, and `screply.df`.
- 277 contextual mapping rules; 279 literal occurrences changed.
- Two dynamic father-topic expressions reordered for natural Indonesian word order.
- Independent structural QA preserved quoted-token counts and line counts in all seven edited files; non-string source skeleton checks PASS.
- Manual residue follow-up fixed 14 previously identified English oneliners in `sharp.df`.

## Coverage status
The last available heuristic measurement is v2.22: 7,490/10,844 = 69.07%. It has not been recomputed for v2.24 and is not a current coverage score, semantic completeness estimate, or runtime screen-coverage measure. The untranslated-candidate queue is a historical heuristic snapshot and must be rebuilt using a comment-aware parser before subsequent comprehensive triage.

## Not tested
- Runtime gameplay and actual UI layout/fit: NOT RUN.
- Save/load: NOT RUN.
- APK rebuild/signing: NOT PERFORMED.
- ZIP/hash integrity does not prove compatibility with a specific installed game version. Treat the artifact as an overlay, not a rebuilt APK.

## Reproduction / review
Keep the original user-provided archive read-only. Back up target data and confirm game version/path before applying an overlay. Test menus, camp branches, character dialogue, trade costs/rewards, transitions and save/load in a compatible runtime.

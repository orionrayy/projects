# Build and Validation — v2.23

## Static verification evidence
- Local patch artifact: `DR2C_VORENYX_ID_v2.23_localization_patch.zip`.
- Package: 294 entries; ZIP CRC scan PASS; unique package paths verified.
- Scope: `assets/deathforth/events/camp/camp3.df`.
- 51 distinct source literals localized across 52 literal occurrences.
- All 47 historical exact-mapping misses recorded for `camp3.df` in v2.22 were repaired.
- The two remaining v2.22 mapping warnings were reconciled as non-actionable: a proper name remains unchanged, and a stale `common4.df` rule refers to a source literal absent after prior contextual rewriting.
- Exact-mapping misses remaining after reconciliation: 0.
- Source structure: quoted-literal tokens 177 before/after; line count 418 before/after; embedded newline/tabs in the pitchfork event preserved.
- Static validation reports no structural failures.

## Coverage status
The last available heuristic measurement is v2.22: 7,490/10,844 = 69.07%. This value is a stale baseline for v2.23; coverage has not been recomputed after this batch. It does not measure semantic completeness or runtime screen coverage. Full Indonesian localization remains incomplete.

## Not tested
- Runtime gameplay and actual UI layout/fit: NOT RUN.
- Save/load: NOT RUN.
- APK rebuild/signing: NOT PERFORMED.
- ZIP integrity does not prove compatibility with a specific installed game version. Treat the artifact as an overlay, not a rebuilt APK.

## Reproduction / review
Keep the original user-provided archive read-only. Back up target data and confirm game version/path before applying an overlay. Test menus, camp branches, encounter choices, NPC dialogue, trade costs/rewards, save/load and transitions in a compatible runtime.

# Build and Validation — v2.26

## Static verification evidence
- Local patch artifact: `DR2C_VORENYX_ID_v2.26_localization_patch.zip`.
- ZIP package: 312 entries; CRC scan PASS; zero duplicate paths.
- SHA-256 manifest: 311 listed files, all hashes verified with zero mismatches; no machine-local path leaks.
- Scope: five special-character profiles: `sc/beeman.df`, `sc/boxer.df`, `sc/caveman.df`, `sc/knight.df`, and `sc/ninja.df`.
- 66 exact-context mappings; 66 literal occurrences changed.
- All five files preserve quoted-token counts, source line counts, and non-string source skeletons; all mapped source residues are absent.
- Artifact SHA-256: `edda11648c4f7ed32d1413b154fd70e65943edfb367f18c6bffa0b5119a3f02c` (11,275,547 bytes).

## Coverage status
The last available heuristic measurement is v2.22: 7,490/10,844 = 69.07%. It has not been recomputed for v2.26 and is not a current coverage score, semantic completeness estimate, or runtime screen-coverage measure. The historical untranslated-candidate queue must be rebuilt with a comment-aware parser before broad triage.

## Not tested
- Runtime gameplay and actual UI layout/fit: NOT RUN.
- Save/load: NOT RUN.
- APK rebuild/signing: NOT PERFORMED.
- ZIP/hash integrity does not prove compatibility with a specific installed game version. Treat the artifact as an overlay, not a rebuilt APK.

## Reproduction / review
Keep the original user-provided archive read-only. Back up target data and confirm game version/path before applying an overlay. Test menus, camp branches, character dialogue, trade costs/rewards, transitions and save/load in a compatible runtime.

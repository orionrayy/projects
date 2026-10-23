# DR2C VORENYX v2.3 Checkpoint — 24 October 2026

**Static integrity: PASS. ZIP CRC: PASS. Full localization: NOT COMPLETE.**

v2.3 updates context-specific presentation text in three recruitment/event files: `camp-recruit.df`, `cyoa-k-recruit.df` and `familiar-recruit.df`. The method rewrites exact quoted literals only and protects game logic.

- Exact mapping rules hit: 410.
- Literal occurrences changed: 432.
- Inventory rows marked translated at v2.3: 427.
- Heuristic player-facing inventory delta: 3,809 / 10,844 = 35.13%.
- Probable unique untranslated candidates: 6,270.
- Literal counts, line counts and display-expression markers passed static checks.
- ZIP CRC and `tools/verify_patch.py`: PASS.
- Runtime gameplay, save/load and APK rebuild/signing: NOT RUN.

The 35.13% is a heuristic, not semantic completeness or runtime screen coverage. The original user archive and complete overlay package remain outside public GitHub.

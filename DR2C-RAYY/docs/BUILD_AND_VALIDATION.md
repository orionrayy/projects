# Build and Validation — v2.22

## Static verification evidence
- Local patch artifact: `DR2C_VORENYX_ID_v2.22_localization_patch.zip`.
- ZIP entries: 292; Python ZIP CRC scan (`testzip`) returned no corrupt entry.
- Source inventory baseline: 541 files, 17,329 quoted literal occurrences, 13,038 unique literals.
- Scope: `charstats-textfill.df`, `events/camp/camp3.df`, `events/common/common4.df`, `events/rareloc/rare1.df`, and `cyoa-charstats.df` for the two deliberate helper-macro additions.
- 94 complete display expressions rewritten; 183 existing literal tokens changed; 138 inventory rows newly marked.
- Static report: PASS; zero structural failures. Four expression-only files preserved literal-token and line counts. The helper file adds two literals and two lines intentionally.
- Heuristic inventory delta: 7,490 / 10,844 = 69.07%; full localization is not complete.
- QA debt: 49 exact mapping rules did not find their original source literals after contextual rewrites. Review and reconcile before release; do not count them as successful matches.

## Not tested
- Runtime gameplay: NOT RUN.
- Save/load: NOT RUN.
- APK rebuild/signing: NOT PERFORMED.
- ZIP integrity does not prove compatibility with a particular installed game version. Treat the artifact as an overlay, not a rebuilt APK.

## Reproduction / review
Keep the user-provided source archive read-only. Before installation, back up the target data and confirm the game version/path. Test menus, camp branches, encounter choices, NPC dialogue, trade costs/rewards, save/load and transitions in a compatible runtime.

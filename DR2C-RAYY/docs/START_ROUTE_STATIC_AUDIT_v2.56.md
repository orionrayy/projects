# DR2C VORENYX — Start-route static audit v2.56

**Result: STATIC CONTRACTS PASS; DEVICE/RUNTIME NOT VERIFIED.** This is an audit checkpoint only, not a game version or APK.

## Scope and inputs

The audit compares the current reproducible source-only patch against the original source archive:

- Base archive `DR2C-RAYY(2).zip`, SHA-256 `14f44400c3314a6d9b7e5428077c199c846367235e379199618f7b11288f4eb1`.
- Source patch `DR2C_VORENYX_REPRODUCIBLE_SOURCE_PATCH_v2.55.zip`, SHA-256 `95bfb426c802c0dacebb9d44586cf6deeef1aab5557e2c63ca5dff6f05edf64d`.

## Results

- **12/12 route-related `.df` files passed static contracts.** The core overlaid route files `boot-end.df`, `game-info.df`, `game-select.df`, `game-start.df`, and `events/tutorial.df` retain the same normalized executable code skeleton and ordered single-quoted Forth symbol stream as the base.
- `events.df` and the save/load/minimenu files in scope have no overlay payload; they remain the source-layer copies. The tokens `main-event-do-select`, `select-start`, `select-boot`, `game-start-new`, and tutorial dispatch keys `tutorchat-1` through `tutorchat-3` are present in the effective tree.
- `boot.df` adds the display-label helper `id-name-localize` and changes the visible boot label from `READY.` to `SIAP.`. The canonical `GAME-MARKER $anew` marker remains present; the added helper is separate from the route definitions in `game-select.df`.
- Required string closures passed, and no C/JSON-style escaped quote sequences were detected in the checked route files.

## Interpretation and limits

This is lexical/static validation, not a full Deathforth interpreter parse. It does not open the Android game, press Start, inspect touch hitboxes, verify screen transitions, test event loading, or check save/load. Static preservation of function tokens cannot establish that the engine can reach or execute Start at runtime.

APK build, alignment, signing, installation, UI fit and gameplay stability remain unverified. The overlay still uses only the available base + v2.43 + v2.45 corrective + v2.45 Startfix layers. Actual v2.47–v2.51 ZIPs and the v2.46 baseline APK remain unavailable, so this audit does not claim v2.51 integration.

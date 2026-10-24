# DR2C VORENYX — Deep Repair v2.45 (source-overlay candidate)

**Status:** Corrective source overlay prepared and static checks passed. APK rebuild and target-device runtime tests have **not** been performed. This is not a release APK and does not establish that the installed app is fixed.

## Repairs in this candidate

The patch is based on the v2.43 localization overlay and contains 12 changed Deathforth source files.

1. Restores the internal boot marker `GAME-MARKER`; `PENANDA-GAME` was a translation incorrectly applied to a code symbol.
2. Restores canonical trait/perk identifiers at `trait-confirm!`, `perk-confirm!`, and `perk-view!` call sites. The canonical name remains the lookup key; localization is applied only to player-facing display text.
3. Restores `Jack of All Trades` as the canonical `$perk` definition key, while retaining `Serba Bisa` as its display label.
4. Fixes an extra quote in the translated multiline `trade-medicalt` string in `events/trade/oldtrade.df`; the quote mismatch had desynchronized lexical scanning across later text.
5. Applies the display-label mapping in camp, familiar, and 4-Jerks recruiting screens and localizes the `PERK` label to `KEISTIMEWAAN`.
6. Corrects the candy-sharing choice from `Baca bareng-bareng` to `Bagikan ke semua orang`, matching its `candyshare` handler.
7. Localizes unlock confirmation wording without changing cost calculations or callback arguments.

## Static validation

- Source `.df` files: 509; overlay `.df` files: 269; uncovered source files: 240.
- Changed source files: 12.
- Unclosed strings/block comments in the overlay: 0.
- New normalized heuristic warnings relative to the corresponding source files: 0. The validator is a static heuristic, not the game's interpreter.
- Canonical trait/perk definition keys: 60 in source and 60 in candidate; key sets match exactly.
- Active confirm calls checked: 44 (14 `trait-confirm!`, 30 `perk-confirm!`); noncanonical IDs remaining: 0.
- Active `perk-view!` calls checked: 44; noncanonical IDs remaining: 0.
- CYOA declarations preserved against source for covered files: 820 `cyoa:`, 927 `cyoa-choice:`, 190 `cyoa-bridge:`; no added or removed identifiers detected.
- Tracked gameplay-effect primitive counts unchanged. Additional `solo` tokens appear only in five narrative files where singular/plural text branches were introduced.
- ZIP CRC: PASS; 17 entries; duplicate paths: 0.
- Patch SHA-256: `1fdd196c5b0616de82011c7386b435e231191df25e75e65f6a2f4ed7b468c5e3`.

## Outstanding risks

1. **Runtime remains unverified.** The actual installed package has not been independently extracted and matched to this patch; no Android device/ADB/emulator run was done.
2. **Viewport/input remains unresolved.** A fixed-landscape manifest flag alone does not validate native rendering dimensions, scaling/offset, touch coordinates, or hitboxes.
3. **Save compatibility is untested.** Canonicalizing perk keys is the safer data-contract correction, but existing saves need regression tests.
4. **Localization is incomplete.** The overlay covers 269 of 509 source script files; do not claim full Indonesian coverage.
5. **APK build and signing remain outstanding.** Rebuild only from an authorized, integrity-verified base; then validate APK CRC, signature, embedded script hashes, manifest, package identity, and runtime.

## Recommended regression matrix

Test launch/title, settings, new run, save/load, trait/perk preview, purchase/upgrade, trade, recruit, CYOA branching, quit/reload, and campaign transition. For each failure, capture screen/tap coordinates and logcat where available; distinguish rendering transform, touch mapping, event dispatch, script load, and persistence.

The full locally generated corrective source patch and its diff are separate artifacts; this repository change records the audit and static validation only.
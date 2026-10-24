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

## Additional follow-up checks

- Found one missing display mapping: active perk `T*S*T*C` had no entry in `id-name-localize`, so its English identifier could leak into player-facing UI. Added the label `Otot Kebangetan, Ogah Kardio` without changing the canonical lookup key.
- Canonical display-name mapping is now **60/60**, with no missing active trait/perk definition names.
- An additional token audit masks strings and complete `($ ... $)` display interpolation blocks before comparing executable structure. Six files differ outside those blocks, and all detected token operations are additions (display-localization helper definitions/calls); no executable-token deletions or replacements were detected by this heuristic. This is not a formal Deathforth parse or runtime proof.
- The source archive and the supplied raw APK are not interchangeable whole-package baselines: 163 of 883 common non-directory paths differ, though the 656 common `assets` entries are byte-identical. The raw APK ZIP has a CRC mismatch on `classes3.dex`; the extracted DEX's own header checksum and SHA-1 were valid, so the finding is specifically an outer ZIP-integrity issue, not proof that DEX code bytes are corrupt.
- Local build gate: `apksigner`, `zipalign`, `adb`, `apktool`, and `d8` are unavailable in this environment; the v2.44 local signing keystore was not found. A bundled Google client keystore is not an appropriate app signing key. No APK has been built.

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
- ZIP CRC: PASS; 18 entries; duplicate paths: 0.
- Display mapping coverage: 60/60 canonical perk/trait IDs.
- Executable-token heuristic: 6 files with additions only; 0 token deletion/replacement operations.
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

## Updated artifact integrity (2026-10-25 follow-up)

- Corrective source ZIP: `DR2C_VORENYX_v2.45_CORRECTIVE_SOURCE_PATCH.zip`, 79,036 bytes, SHA-256 `09ea2b684ce124778322a16464fb17fbaccceb0cdc9f307dcf94d72e96d6b14f`.
- ZIP creation uses fixed timestamps and stable entry ordering. Two consecutive builds produced the same SHA-256; ZIP CRC test passed.
- Machine-readable executable token audit: [executable_token_audit_v2.45.json](../audit/executable_token_audit_v2.45.json). The raw APK/source-archive comparison is recorded in [apk_baseline_integrity_v2.45.json](../audit/apk_baseline_integrity_v2.45.json).

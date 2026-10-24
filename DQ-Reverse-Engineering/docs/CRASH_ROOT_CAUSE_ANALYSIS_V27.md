# Dungeon Quest crash isolation v27 — no-op packed-header test

**Date:** 2026-10-24  
**Branch:** `feat/dq-iap-debug-cheats-modkit-v7`  
**Status:** candidate built and statically validated; device test still required.

## Confirmed device result

The user reports that the same-package stock-pack diagnostic control reaches the game. This control contains the unmodified original `S3DMain.smf`, so it is expected to have no cheat menu. This is a successful control result, not a failed cheat build.

The prior v25 label-only candidate crashes at the Shinybox splash, while the stock-pack control reaches the game. All decoded APK members except `assets/S3DMain.smf` match between that pair apart from signing metadata. This points to the changed packed asset as the leading variable, but a runtime log is still needed before concluding anti-tamper. The local diagnostic builds use fresh signing certificates, so signer state is not perfectly isolated.

## v26 no-op candidate

- Artifact: `Dungeon_Quest_3.3.2.0_Diagnostic_NoopPackByteChange_v26.xapk`
- Package ID: `com.shinybox.dqv25`, same as the working stock-pack control
- XAPK SHA-256: `f8a320bd76890825bc19053648ae59392571f63605183127424c064ed0a5c4ad`
- Embedded STK SHA-256: `28c3d6bf000c9ec98c2e6277aabfa3edaae4ef4be68b7e674a9b1e90b8b85d5f`
- 20 split APKs; local v2 signature and inner/outer ZIP CRC checks passed
- **Runtime status: not yet tested**
- **No cheats are included.**

The only packed payload change is the zlib header hint byte for `Resources/HUD/pause.hud`, from `78 da` to `78 9c`. The DEFLATE body is byte-identical; decoded HUD bytes are identical. The target entry CRC is recomputed. The archive length, every entry offset/size/flag, and all non-target CRCs are preserved. Only five byte positions in the entire 33,978,539-byte STK archive differ. All 5,630 entries decode successfully and **zero decoded entries changed**.

Compared with the known-good stock control, the only non-signature APK member difference is `assets/S3DMain.smf`.

## Test procedure

Because the new candidate is signed with a different local certificate, Android will not install it over the working control. Uninstall the diagnostic app `com.shinybox.dqv25`, then install v26 and launch offline using a disposable profile. Do not sign into a primary account or connect paid/cloud-save flows during diagnostics.

## Interpretation

1. **If v26 launches:** a minimal packed-byte change with unchanged decoded assets is tolerated. The v25 crash is then more likely related to the semantic HUD mutation or a structural assumption exposed by changing the string. The next engineering step is to parse the HUD element schema and add a separate element/action instead of repurposing the `Social/IAP` item.
2. **If v26 crashes while the stock control launches:** test logs are required. This raises the likelihood of packed-resource integrity or parser constraints, but is not alone proof of anti-tamper. Capture Android `logcat` around the crash before producing more blind variants.

No IAP entitlement, billing receipt, cloud save, achievement, or leaderboard code was modified. Do not mark cheat functionality as implemented until an on-device test shows the menu and verifies each action.

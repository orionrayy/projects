# Crash root-cause analysis v26 — same-ID stock control

Date: 2026-10-24/25. User reports that v21-v25 all install but force-close at the Shinybox splash; stock-asset package ID `com.shinybox.dqfix` was reported to launch.

## Exact differential

A new stock-pack control was built with the **same application ID as failing v25**, `com.shinybox.dqv25`, but with the original `S3DMain.smf` bytes unchanged. Artifact is `Dungeon_Quest_3.3.2.0_Diagnostic_StockPack_ID_v25.xapk` (SHA-256 `4803c9e72af820c1572cd543e530b0b713a532f2fbbbcabbc04d722a25d7c7b2`). It has 20 split APKs; local v2 signature and ZIP checks pass. It has not been installed by the user yet.

Inner APK content comparison between failed v25 and this control covered every file in all 20 splits. The only differing inner file is `assets/S3DMain.smf` in `com.shinybox.smash.apk`; all other APK member contents, including base and split AndroidManifest.xml, resources.arsc, DEX, native libraries, and localized/density assets, are byte-identical. Signing data differs because each diagnostic package was signed with a different fresh local certificate. This isolates the actual content-pack mutation, with signing identity as a residual caveat.

## Binary anti-modification investigation

- `Pandora::EngineCore::Resource::CheckIntegrity(bool)` at `0x817020` is only `mov w0, #1; ret`, and no direct call site was found in the native disassembly.
- The only direct call site found for `CodeSigning::ValidateCertificate` is within `Game::ParseAndValidateNativePluginManifest` at `0x9522b4`. The packed `Plugins/com.shinybox.Database/Manifest.xml` contains a vendor certificate for the Database plugin, supporting plugin-manifest validation as the direct context.
- No direct static call site was found for `CodeSigning::ValidateSignature`. Its exported presence alone is not evidence that it is used to verify `S3DMain.smf`.
- CRC32/hash functionality and `FileManager::GetCRCInPackFile` exist; direct evidence of a hard-coded expected `S3DMain.smf` digest or a pack-signature check has not been found.
- These facts make a specific anti-modification check possible but **not established** by current evidence. The splash crash alone is not enough to label it anti-tamper.

## Current interpretation

The v25 asset patch changes one decoded HUD resource, `Resources/HUD/pause.hud`, and updates the entry CRC; the archive length, metadata table end, offsets, sizes and alias layout are preserved. Since v25 still crashes, the evidence now points toward a runtime-rejected modification in that packed HUD path, but there are still two main alternatives:
1. the edited string is semantically referenced (not only displayed) or the native HUD parser has constraints not captured by the incomplete element decoder;
2. a resource/content integrity check exists elsewhere or is called indirectly.

The same-ID stock control is the next discriminator:
- If it launches, investigate the modified pack/HUD, then test an unchanged-decoded-content repack to separate compression/container integrity from a semantic content mutation.
- If it crashes too, capture device logcat and revisit package/signing/manifest initialization; do not continue to modify the HUD blind.

## Device procedure

The control uses the same package ID as v25, but a different signing certificate. Android will not install it over v25; uninstall v25 first, install this control, launch offline with no account sign-in and a disposable profile. Reinstall v25 only after uninstalling the control. This control is stock content and does not enable cheats.

No billing receipt, paid entitlement, cloud save, achievement or leaderboard code was changed.

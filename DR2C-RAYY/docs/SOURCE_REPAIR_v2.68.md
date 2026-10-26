# DR2C VORENYX — Source Repair v2.68

**Date:** 26 October 2026  
**State:** source-only repair patch; no APK built. Android install, Start-button runtime, gameplay and save/load remain unverified.

## Applied repairs

1. **Visible-label consistency:** in `boot.df`, the display-only `fitness` alias now returns `bugar`, matching the native presentation label found during the v2.67 audit. The canonical key `fitness` is unchanged; no gameplay/stat identifier was renamed.
2. **Missing optional module:** `paul/camping-region.df` now uses `load?` for `paul/camping-tent-events.df`, which is absent from the supplied base archive and prior overlays. This avoids a hard load failure if this developer/test region is loaded. It does not recreate any event content that may have been in the missing file; reachability from the main route remains unproven.
3. **Outdated artwork suffix:** the extra `vorenyx_title_screen.png` now displays `LOKALISASI INDONESIA // VORENYX`, not a hard-coded `V2.43` label. No loader reference was found in the earlier static audit, so whether the engine actually displays this asset remains unknown.

## Tests executed

- Overlay source assertions: **PASS**.
- Synthetic fixture for patcher, backup generation and repeat/idempotent application: **PASS**.
- PNG decode/dimensions/cleared text-zone assertions: **PASS**.
- Title-image repair script reproduced the packaged PNG byte-for-byte: **PASS**.
- ZIP integrity test: **PASS**; archive SHA-256: `7f991123bbf1a14e553945ea88b20a57d41327436d86c2dffd2feb431df19938`.
- Official `apksigner`, APK build, Android PackageManager install, Start tap/Logcat, gameplay and save/load: **NOT RUN**.

## Files and boundaries

The downloadable repair archive contains a three-file overlay and local application/test tools. Public GitHub stores authored docs, tools and sanitized audit metadata only; the binary game archive and binary overlay are not committed. Apply the overlay after v2.43, v2.45 corrective, v2.45 Startfix and v2.61 tutorial-sync patches.

**Do not describe the project as stable/fixed yet.** The original install failure and Start-button behavior have not been root-caused.

# DR2C VORENYX — Source Repair v2.68

**Date:** 26 October 2026  
**State:** the source repair archive is an overlay, not an APK. A separate locally signed v2.68 test APK has since been built; see [APK test build report](APK_TEST_BUILD_v2.68.md). Android install, Start-button runtime, gameplay and save/load remain unverified.

## Applied repairs

1. **Visible-label consistency:** in `boot.df`, the display-only `fitness` alias now returns `bugar`, matching the native presentation string without changing the canonical `fitness` key.
2. **Missing optional module:** `paul/camping-region.df` now uses `load?` for `paul/camping-tent-events.df`, which is absent from the supplied base archive and previous overlays. This reduces the chance of a hard include failure if that developer/test region loads, but does not recreate the missing event content or prove that the region is reachable from the main route.
3. **Additional title artwork:** `assets/gfx/ui/vorenyx_title_screen.png` uses the version-independent label `LOKALISASI INDONESIA // VORENYX` instead of the baked-in `V2.43` suffix. A loader reference was not found, so its use remains unconfirmed.
4. **Android splash artwork:** `res/drawable-xxhdpi-v4/splash.png` uses the same version-independent label rather than the source overlay's old `V0.3` suffix. The recovered candidate APK still contains `V2.43`; **that APK binary has not been modified or rebuilt** by this source overlay.

## Validation

- Source assertions and optional-include regression: **PASS**.
- Fixture test for backup creation, PNG handling and repeat/idempotent application: **PASS**.
- Both title and splash PNG decode/dimension/text-zone checks: **PASS**.
- Repair helper reproduces both packaged overlay PNGs byte-for-byte from their applicable source-overlay images: **PASS**.
- Replaying the patcher on a reconstructed base + v2.43 + v2.45 corrective + v2.45 Startfix source tree reproduces all four overlay payloads byte-for-byte: **PASS**.
- ZIP integrity, embedded manifest and SHA-256 sums: **PASS**.
- ZIP SHA-256: `e6bf40a2ca8f69b4c55f7b50592b1cb201b8660ff285f6862a1c96e8b645690d`.

## Boundaries

This is a source/asset overlay ZIP, **not an APK** and must not be installed directly. Official `apksigner`, Android PackageManager install, Start tap/Logcat, gameplay, tutorial runtime and save/load were not run. The original install failure and Start no-op remain unresolved; do not mark the project stable/fixed on the basis of these static tests.

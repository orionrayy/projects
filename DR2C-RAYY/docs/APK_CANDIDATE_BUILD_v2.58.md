# DR2C VORENYX v2.58 — APK candidate build and static validation

**Status: build and static package checks PASS. Android runtime: NOT TESTED. This is not a release APK and not full v2.51 integration.**

## Candidate artifact

- File: `DR2C_VORENYX_v2.58_TEST_CANDIDATE.apk`
- Size: 115,614,035 bytes (110.3 MiB)
- SHA-256: `11ddc0e41df162837f74c676d602403952c3f6c875f4f6dacd91db68adbb41b0`
- ZIP: 1,015 entries, CRC PASS, 0 duplicate paths
- Deathforth scripts: 509/509; escaped-quote regressions: 0

## New localization pass

The build adds a curated 38-row queue from the v2.46 English-residue analysis. It produces **41 exact literal replacements across three scripts**:

- `assets/deathforth/events/city/region/special-lots.df`
- `assets/deathforth/events/trade/oldtrade.df`
- `assets/deathforth/events/locationlogic.df`

The incorrect proposed translation of “SIEGE ALERT!” was corrected from “pengelompokan” (grouping) to **“pengepungan”** (siege). Static checks report unchanged executable token streams outside display strings, unchanged ordered single-quoted Forth symbols, closed display strings and zero backslash-quote regressions. This pass does not mean the game is 100% localized.

## Build/static checks

- Builder and localization tests: **13/13 PASS** (8 existing builder tests + 5 next-wave tests).
- 26/26 native UI string-slot checks pass (13 per ABI); two primary activity orientations are landscape.
- `resources.arsc` stored and 4-byte aligned; all stored ZIP entry alignment checks pass; seven uncompressed native libraries per ABI are 4-KiB aligned.
- PairIP implementation libraries remain byte-identical to the selected base APK.
- JAR/v1 signature verifies with `jarsigner`.
- APK Signature Scheme v2 was **not generated or verified** because `apksigner` is unavailable.

## Source patch

- File: `DR2C_VORENYX_REPRODUCIBLE_SOURCE_PATCH_v2.58.zip`
- Size: 7,522,647 bytes
- SHA-256: `c8fc92683ef545b1f27fa205742618b2032f653cc8eea3edfb15f5aa04218799`
- ZIP CRC PASS; no duplicate paths; 270 `.df` overlay scripts across 273 unique overlay paths.

This is a cumulative source overlay built from the available v2.55 source layer plus the recorded 38-row queue. The full v2.47 batch A–F ZIP, v2.48–v2.51 patch ZIPs and exact v2.46 baseline APK remain unavailable. Therefore this APK must not be described as v2.51 integration.

## Signer and device-test limitation

Certificate SHA-256: `0c400f22aff9ae95b318740b17823754b7af55ff86137622bab3b35fd6d2c9e7`. This is a **new local self-signed test certificate**, not the publisher's or currently installed app's signer. Android may reject in-place updates; the unchanged PairIP/licensing wrapper may also reject a locally signed build. Do not uninstall the current app without backing up save data.

No Android device/ADB/emulator was available, so actual installation, Start-button response, UI hitboxes, gameplay, event loading, save/load, crash behavior and stability remain **untested**. The original launcher banner and APKVision wrapper identifiers remain unchanged; no security/licensing bypass was attempted.

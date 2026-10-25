# DR2C VORENYX v2.46 — Screenshot-driven UI localization

**Status:** Localized test APK built; static package checks passed. Device runtime has not been re-tested for this build.

## Evidence and scope

The user's 2026-10-25 screenshots showed the Status/Team screen and tutorial CYOA with mixed English/Indonesian strings. The update targets only those visible labels/strings.

### Tutorial CYOA

File: `assets/deathforth/events/tutorial.df`

- Rewrites the mixed-language outcome strings so they no longer contain the English fragments `gets`, `was`, or `COOL IT`.
- Localizes the four choices as:
  - `Biarkan [nama] dulu`
  - `Suruh [nama] buat 'KALM DULU'`
  - `Bujuk [nama] buat bantu lawan zombi`
  - `Ejek [nama] sebagai orang brengsek`
- Reuses the dynamic character name rather than English pronouns.
- Keeps `choice: tutorchat-1/-2/-3` and `cyoa-choice: tutorchat-1/-2/-3` handlers.

### Native UI labels

File: `lib/arm64-v8a/libmain.so`. All replacements target unique standalone printable-string slots. In-place replacement and NUL padding preserve the existing native offsets and library file size.

| English | Indonesian |
|---|---|
| Team | Tim |
| Swap Meet | Barter |
| Choose UR Fate | Pilih Nasibmu |
| strength | kekuatan |
| fitness | bugar |
| shooting | menembak |
| wits | akal |
| attitude | sikap |
| composure | tenang |
| loyalty | setia |
| morale | moral |
| medical | medis |
| mechanical | mekanik |

`Status` stays unchanged because it is already valid Indonesian. These native literal replacements are static-verified, but the user still needs to confirm the labels render correctly and that character-stat behavior remains intact in the actual game.

## Build and validation

- APK: `DR2C_VORENYX_v2.46_UI_LOCALIZED_TEST.apk`
- Size: 112,238,801 bytes
- SHA-256: `6d4e2f3df07d199807c08418ae5d30b9927e5b2e36c780a51858045336b29313`
- ZIP: 1,005 entries; CRC PASS; duplicate paths 0
- 509 packaged `.df` scripts scanned; escaped double-quote syntax regressions remaining: 0
- JAR/v1 signature verified with `jarsigner`
- APK v2 signature and content digest pass using the local verifier (official `apksigner` is unavailable)
- `resources.arsc` stored and 4-byte aligned; all stored entries meet alignment; all seven native libraries are uncompressed and 4-KiB aligned.
- Binary manifest chunk structure pass; min SDK 23, target SDK 35; splash and game activities use landscape orientation.

## Limitations

This only addresses the screenshots supplied and does not finish full Indonesian localization. No target-device runtime test has been run for v2.46 in this environment. APK uses the local test signing certificate, not publisher's key. An installed app with a different signing certificate may refuse it as an update; back up game saves before considering uninstall/reinstall. Original PairIP/Play license checks remain intact.

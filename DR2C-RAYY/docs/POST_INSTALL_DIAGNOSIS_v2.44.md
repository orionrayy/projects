# Post-install diagnosis — v2.44 symptoms unchanged

**User report (24 October 2026):** all three symptoms remain after the attempted hotfix: Start does not trigger, UI orientation/layout remains wrong, and APKVISION branding remains visible.

## Findings verified from local artifacts
- v2.44 contains the canonical marker `"GAME-MARKER" $anew` in `assets/deathforth/boot.df`.
- v2.44 manifest stores `screenOrientation=0` (fixed landscape) for `SplashActivity` and `DrtcGameActivity`. The base archive had `6` (`sensorLandscape`) for both.
- v2.44 has package ID `com.noodlecake.drtc`, versionName `1.8.2`, versionCode `57`.
- v2.44 is signed with a local certificate, SHA-256 `6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9`, not the original publisher/APKVISION repack certificate.
- Android requires the same signing identity to update an installed app. If the device still has a separately signed APKVISION repack installed, the local candidate cannot replace it; Android rejects the update and the previous app remains. This is a strong explanation for unchanged symptoms, but device installation output has not been collected.
- APKVISION-related class namespaces remain in `classes3.dex` and `libstub.so`; the wrapper was not removed by v2.44. The VORENYX title/splash artwork itself does not carry the logo.

## Conclusion
**Hotfix outcome: FAILED TO VERIFY / USER REPORTS NO CHANGE.** Do not call v2.44 fixed or stable. Static inspection alone cannot establish which package is running on the phone.

## Safest next diagnostic
Before another code change, capture the Android installer result while trying to install the v2.44 APK. If it says "App not installed", "package conflicts", or "incompatible update", the local APK did not replace the existing package. Do not uninstall the existing app until game-save backup is confirmed. The APKVISION layer needs a clean, authorized base package or appropriate signing provenance; it has not been removed.

## Runtime evidence still missing
- Device model/Android version and actual installed package version/signing certificate.
- Installer success/failure message for the v2.44 file.
- A new screen recording taken after confirmed successful installation.
- Android logcat or equivalent runtime stack trace for the failed Start event.
- Touch coordinates/event routing and actual display viewport measurements.

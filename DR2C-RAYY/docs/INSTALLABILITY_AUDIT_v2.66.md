# DR2C VORENYX — Deep Installability Audit v2.66

**Date:** 26 October 2026  
**Scope:** offline/static audit of the exact v2.57 candidate. **v2.66 is an audit checkpoint, not a newly built APK.**

## Findings

The exact APK in the local audit has SHA-256 `a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7`.

- ZIP CRC passes; 1,015 entries; no duplicate paths.
- A custom binary-XML parser traversed all 62 AndroidManifest.xml chunks and found the expected package `com.noodlecake.drtc`, minSdk 23, targetSdk 35 and landscape activity values.
- `resources.arsc` is stored uncompressed and starts at an offset divisible by 4. Fourteen stored native-library entries are page-aligned; the two compressed `libstub.so` entries remain compressed as in the supplied base APK.
- OpenJDK `jarsigner -verify` passes the JAR/v1 signature, with expected warnings because the certificate is self-signed and has no timestamp.
- An independent Python cryptographic check validates APK Signature Scheme v2 signing-block geometry, the RSA signature over signed data, signer public-key/certificate match and the chunked content digest.
- The available source lineage reproduces **509/509 Deathforth scripts byte-for-byte** in the candidate: base archive + v2.43 localization + v2.45 corrective + v2.45 Startfix + v2.61 tutorial sync.
- Normalized code/control token streams match in the primary game-select/start/event files after masking display text. In the tutorial, `chim → cname` changes occur inside player-visible choice labels; the `tutorchat-1/2/3` callbacks remain. This is not proven to cause Start failure.
- The boot file adds the `id-name-localize` helper used by translated trait/perk displays; removing only that definition makes the core boot token stream match the base.

## What this rules out—and what it does not

These checks do not show a corrupted ZIP, missing Deathforth scripts, malformed binary manifest, broken v2 signer digest, or an obvious change to the core Start event-registration tokens in this exact candidate.

However, **official Android `apksigner` verification has not been run**, and no Android device was available to test PackageManager installation, tap delivery, Deathforth loading, native runtime, UI layout or save/load. A valid local v2 digest does not substitute for official `apksigner` or a device-side install test. The local signer certificate also differs from the publisher's; that can affect in-place upgrades or runtime licensing, but is not enough by itself to explain a failed fresh install after uninstall.

## Next acceptance gate

1. Capture the exact PackageManager error while trying to install the same candidate using the v2.65 toolkit's `INSTALL_ATTEMPT` mode.
2. If it installs, use `START_BUTTON` mode and tap Start once.
3. Classify the concrete failure before making another APK edit. Do not publish this candidate as stable and do not risk saves with another uninstall/reinstall loop.

## Artifacts

- [Full machine-readable audit report](../audit/installability_audit_v2.66.json)
- [Compact re-runnable audit script](../tools/installability_audit_v2.66.py)
- [Official Android apksigner reference](https://developer.android.com/tools/apksigner)
- [Android 11 behavior changes: v2 signatures and uncompressed/aligned resources.arsc](https://developer.android.com/about/versions/11/behavior-changes-11)

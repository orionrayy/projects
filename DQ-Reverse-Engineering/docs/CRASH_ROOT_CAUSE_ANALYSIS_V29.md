# Dungeon Quest 3.3.2.0 — multidimensional crash isolation audit v29

Date: 2026-10-25
Runtime status: prior controls are user-tested; matched-signer v28 pair still needs device testing.

## Executive finding

Evidence points to a startup failure associated with assets/S3DMain.smf more strongly than to the HUD label alone, but anti-tamper is not proven. A deeper review found a key confounder: the earlier stock control and v26 were re-signed with different certificates. Their runtime outcomes do not isolate the pack mutation. A same-package, same-signer v28 pair fixes that flaw.

## User-reported runtime observations

- The stock-content diagnostic com.shinybox.dqfix entered the game.
- The same-ID stock-content control com.shinybox.dqv25 also entered the game. It contains the original S3DMain.smf, so it intentionally has no cheat.
- The user reported that the problem returned after testing v26. Context indicates a startup failure, but the environment did not observe the device screen directly.
- v21–v25 had previously been reported to fail at the Shinybox splash.

## Cross-version pack evidence

| Variant | STK length | pause.hud offset | Decoded content difference | Diagnostic value |
|---|---:|---:|---|---|
| Original / stock controls | 33,978,539 | 122,287 | none | Stock baseline |
| v21 | 34,011,389 | 33,445,522 | large HUD/schema changes | Full pack reserialization; poor control |
| v22 | 34,011,389 | 33,445,522 | label and callback/action schema changes | Full pack reserialization; poor control |
| v23 | 34,011,397 | 33,445,522 | callback/action data changes | Full pack reserialization; poor control |
| v24 | 34,011,387 | 33,445,522 | 10-byte label change | Full pack reserialization; poor control |
| v25 | 33,978,539 | 122,287 | exactly 10 decoded bytes in Resources/HUD/pause.hud | Layout-preserving, but compressed stream recompressed |
| v26 | 33,978,539 | 122,287 | zero decoded entry differences | Only five raw STK byte positions differ; prior test had signer confounder |

The v21–v24 builds moved the target entry offset from 122,287 to 33,445,522 and changed pack length by roughly 32 KB. Those failures cannot isolate a semantic HUD issue from pack-layout/rebuild issues.

An independent decode of all 5,630 STK entries in original, v25, and v26 found:
- v25: exactly one decoded-content difference; Social/IAP was replaced by Cheat Menu at the same 10-byte length. There are 4,514 differing raw STK byte positions because the target compressed payload was recompressed and its CRC metadata changed.
- v26: zero decoded-content differences. Only five raw STK byte positions differ: one zlib-header byte plus four bytes in the target entry's CRC field. The target entry offset, compressed size, uncompressed size and flags remain unchanged.

## APK and signer cross-analysis

In the v25, previously working stock-control, and v26 base APKs, the only ordinary (non-signature) member-content difference from the stock control is assets/S3DMain.smf. The base APK manifests, resources.arsc, classes.dex, native libraries, and other normal members match by content. However, the prior v25, stock control, and v26 used different locally generated signing certificates:

- v25: 36c36e60321f98432616cda1a3f41e18c3eaed39992f00664608746da92c8f89
- prior stock control: 3e90fe65713d5ac7e78167aa3398dd812245c75ea272c0d94a2bec57c4661ebf
- v26: 27c3705862639a6f842e6c9032a079aced3d18ebe06929241f3896037e4fa957

The previous v26 result was not a fully controlled experiment. Local signature/CRC validation is not an Android runtime test and was not produced by an official apksigner invocation.

## Native-code cross-analysis

Static inspection of the supplied ARM64 libS3DClient.so found:

- Pandora::EngineCore::Resource::CheckIntegrity(bool) at VA 0x817020 returns true directly. This is the base Resource method, not a guarantee that every other subsystem skips validation.
- PakFile::CompareCRC(unsigned int) at 0x7b7b5c compares a stored field against a supplied value; its existence is not itself proof of anti-tamper.
- FileManager::GetCRCInPackFile is used by resource-path/cache-resolution code. CRC support exists, but that alone does not show a hardcoded expected digest for the entire pack.
- The direct call to CodeSigning::ValidateCertificate occurs in Game::ParseAndValidateNativePluginManifest at 0x9522b4. The supplied Plugins/com.shinybox.Database/Manifest.xml includes a certificate for that native plugin. This is evidence of plugin-manifest certificate validation, not proof of APK-signer validation or an S3DMain.smf signature check.
- Object::CheckIntegrity and Scene::CheckIntegrity check scene/object consistency; their names must not be interpreted as a whole-pack integrity guard.
- No direct static callsite tying a hardcoded whole-pack digest to S3DMain.smf was identified in the reviewed disassembly. Indirect or dynamically selected checks are not ruled out.

## Current hypothesis ranking

1. Pack-coupled startup path — leading hypothesis. The asset pack is the only ordinary member-content difference in the matched APK comparison. Potential causes include raw-pack validation, parser assumptions, or compression/container handling.
2. HUD semantic/serialization problem — plausible for v25. The label may be part of an element/name/reference schema rather than display-only text. The v26 result cannot settle this until signer identity is controlled.
3. Signer/install-state confounder — not eliminated by the earlier v26 test. The v28 pair addresses it.
4. Anti-tamper/anti-mod — unproven. Current static evidence does not justify that conclusion.
5. Rebuild/layout damage — possible for v21–v24. Their substantial physical layout changes make them inconclusive.

## Matched-signer phone-only pair v28

Both XAPKs use package ID com.shinybox.dqv25 and the exact same generated signing certificate SHA-256:
046f65113a0b2e64053c92d2eb13562e467f961c5b35e9be1ba1e71fdd3ad94b.
All 19 non-base split APKs are byte-identical. In the base APK, the only differing ZIP member content is assets/S3DMain.smf. All 5,630 decoded pack entries are unchanged in the modified candidate.

| Artifact | XAPK SHA-256 | Role |
|---|---|---|
| Dungeon_Quest_3.3.2.0_PairedStock_Control_v28.xapk | 9574d81c4fdc37ffd1df96d5bd71f2c31a4cb374c82e5435a28a0a4b010807a8 | Stock pack; no cheat |
| Dungeon_Quest_3.3.2.0_PairedNoopPack_v28.xapk | e8ba84e06829890a9099b5be425ea4d130415ca77ea77fde7606770eab68b884 | Five-byte raw pack mutation; no cheat |

Both passed local v2 signature and ZIP CRC checks. Neither has been launched in this environment.

### Phone-only test sequence

1. Uninstall the current diagnostic package com.shinybox.dqv25 first, because its current certificate likely differs. Do not uninstall the original store app com.shinybox.smash, and do not sign into a primary account or use important cloud-save data.
2. Install the paired stock control v28 and launch it.
3. Without uninstalling, install the paired no-op pack v28 over it. Same package ID and same signer should allow an update; if the installer refuses, stop and report the exact message.
4. Open the updated app offline and note whether it reaches the game menu or force-closes at splash.

Interpretation:
- Stock opens, no-op update crashes: strong evidence that a raw S3DMain.smf change (or something coupled to that asset) triggers the crash; still not proof of anti-tamper.
- Both open: the earlier v26 result was probably confounded by signer/install state; next compare the HUD semantic mutation under the same signer.
- Both crash: revisit install/runtime/package-rewrite variables before more pack edits.

The v28 pair is diagnostic-only and has no cheat implementation. Do not mark the cheat menu stable until a separate build launches on-device and its menu actions are verified.
# Crash isolation v24 — label-only HUD candidate

Date: 2026-10-24. User reports that v23 still force-closes at the Shinybox splash; v22 and prior route-modified builds had the same symptom while the stock-asset Baseline launches.

## Artifact
- XAPK: `Dungeon_Quest_3.3.2.0_Diagnostic_LabelOnly_v24.xapk`
- Package ID: `com.shinybox.dqv24`
- SHA-256: `6e5ae9691d53ead8cf9d6b3d73855127f259d75f19ffc0db610ceeb9e5386bed`
- Size: 57,624,002 bytes; 20 split APKs.
- Local verification: APK Signature Scheme v2 signature checks PASS for 20/20 split APKs; split signer fingerprints match; outer and inner ZIP CRC checks pass; stored-entry alignment checks pass.
- Runtime: NOT VERIFIED.

## Isolation boundary
Only the `Social/IAP` string in `Resources/HUD/pause.hud` is replaced with `Cheat Mode`, preserving UTF-8 byte length (10 bytes). The full action section, all 64 action records, callback name `onShowSocial`, and every callback parameter are byte-identical to stock. The candidate does not activate a cheat; it is a diagnostic to determine whether changing the callback route caused the earlier splash crash.

The STK container must be rebuilt to embed the string change, so this still also exercises the custom pack writer. Static decode validation alone is not a substitute for game runtime.

## Decision
- If v24 launches to title: the route/action change in v21-v23 is implicated; build the actual cheat route only after validating the engine's callback/script contract.
- If v24 still crashes while stock-asset Baseline launches: do not make further callback guesses. Investigate the HUD element parser/serialized field and STK repacking compatibility, and obtain a logcat for the crash.
- Until runtime-tested, do not mark the cheat route functional or stable.

Keep the diagnostic package offline and use a disposable profile. No billing receipts, purchase entitlements, cloud saves, achievements, or leaderboard state were changed.

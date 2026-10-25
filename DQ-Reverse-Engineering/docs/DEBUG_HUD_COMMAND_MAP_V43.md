# Existing native Debug HUD command map — v43

Date: 2026-10-25  
Target: Dungeon Quest Android 3.3.2.0, \`com.shinybox.smash\`  
Status: Static call-path evidence only. No HUD asset modified and no APK/XAPK built.

## Source assets and binary

- \`Resources/HUD/debug.hud\`: SHA-256 \`02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6\`, 71 elements.
- \`Resources/AIModels/uai_gp_hud.aim\`: SHA-256 \`bd11e1bd5c4ae66ec5a88d1d0c7c13fbcd0e3fbf4c7e1e42d60ac5edcfc9d4f3\` (source asset hash recorded from the local extracted source pack).
- \`libS3DClient.so\`: SHA-256 \`0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083\`.
- Native dispatch method: \`uai_gp_hud::onDebug(int, S3DX::AIVariable const*, S3DX::AIVariable*)\`, VA \`0x6d5048\).

## Existing 13 Debug HUD action mappings

The source \`debug.hud\` serializes 13 action records. Each dispatches to \`uai_gp_hud.onDebug\` with one numeric command argument:

| HUD action ID | Command | Evidence interpretation |
|---|---:|---|
| \`onClose\` | 1 | Existing close/state path |
| \`onGotoLevel\` | 2 | Existing level-navigation path |
| \`onSetBoss\` | 3 | Existing boss-related debug path |
| \`onSetLevel\` | 4 | Existing level-setting path |
| \`onCreateLegend\` | 8 | Existing legend/debug content path |
| \`onCreateMS\` | 9 | Existing MS fixture path |
| \`onCreateCS\` | 10 | Existing CS fixture path |
| \`onAddLevel\` | 11 | Existing level progression path |
| \`onAddHeroic\` | 12 | Existing heroic progression path |
| \`onCreateFeat\` | 13 | Existing feat fixture path |
| \`onSetCrystal\` | 14 | Existing Crystal-related path |
| \`onSetEternal\` | 15 | Existing Eternal-related path |
| \`onAddBattle\` | 16 | Existing battle-related path |

These names describe the serialized action labels/callback identifiers. They do not by themselves prove save persistence or exact balance semantics.

## Hidden command 6: direct RewardGold call

Static disassembly of \`uai_gp_hud::onDebug\` contains a numeric-command comparison against \`6.0\` at VA \`0x6d5a48\`. The matching branch constructs an \`S3DX::AIVariable\` numeric argument with the 64-bit IEEE-754 value \`100000.0\` and directly calls:

- \`uai_gp_hud::RewardGold(S3DX::AIVariable)\` at VA \`0x65feec\`
- Call site: VA \`0x6d5a64\`

The command is not currently represented in the 13 serialized action records of stock \`debug.hud\`, but a native branch exists in \`onDebug\`. This is a concrete static candidate for a fixed +100,000 Gold debug action without inventing a native symbol. It is **not yet runtime-verified**, and this report does not add a new UI element or call the branch on a device.

## Hidden command 7: do not treat as a generic spend button

The \`7.0\` branch contains a call to \`uai_gp_hud::SpendGold\` at VA \`0x637008\`, but the surrounding code also references LegendEx model/table state. The argument origin and contextual invariants were not reduced to a safe, standalone amount contract. Therefore do not expose command 7 as an arbitrary Spend Gold control based solely on the call name.

## Implications for the 222-entry menu

- A narrow, allow-listed candidate exists for \`economy.gold_reward_fixed_100k\` → existing \`uai_gp_hud.onDebug(6.0)\` → \`RewardGold(100000.0)\`.
- Keep its runtime evidence state \`STATIC-CANDIDATE / NOT-RUNTIME-VERIFIED\`; do not mark the catalogue entry functional.
- Before enabling it in the integrated UI, prove the target package is offline/disposable, the call is reachable through a dedicated row action, the balance change can be read back, and failure/persistence behavior is understood.
- Do not repoint command 7 or the existing LegendEx callbacks to arbitrary cheat IDs.
- The broader 222-row menu remains unintegrated; native List population and stable-ID action dispatch are still unresolved. No new APK/XAPK should be built until the full menu design and native integration contract are accepted and validated.

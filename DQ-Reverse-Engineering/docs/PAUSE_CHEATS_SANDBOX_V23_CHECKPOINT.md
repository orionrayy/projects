# Dungeon Quest Cheats Sandbox v23 — corrected callback shape

Status: **Static validation passed; Android runtime remains unverified.**

- Artifact: \`Dungeon_Quest_3.3.2.0_CheatsSandbox_v23.xapk\`
- Package ID: \`com.shinybox.dqlab\`
- SHA-256: \`4f53461df137dd7adda08a2e3ec26e1b6e02a1ac0ee9500157c3c6b28e4561f1\`
- Size: 57,623,905 bytes; 20 split APKs.
- All 20 v2 signature checks, common signer, and outer/inner ZIP CRC checks passed in the local verifier.
- STK pack has 5,630 entries; exactly \`Resources/HUD/pause.hud\` differs from the original decoded asset set.
- Pause HUD remains version 12 and 64 actions.
- The original \`onShowSocial\` action identity and element reference are preserved. Its six original visibility/state parameters are preserved. Only its seventh/final route call is replaced with the exact \`uai_gp_hud.onDebug(0)\` call already present in the original main HUD.
- The visible label is \`Cheat Mode\`, preserving the original label's 10-byte UTF-8 size.
- No purchase receipt, billing callback, paid entitlement, account data, cloud-save, achievement, or leaderboard logic was modified.

## Why this candidate differs

The crashed v21/v22 candidates renamed the callback and reduced its parameter list from seven parameters to two. The original action controls six menu-state flags and a final route; changing that schema was not justified. v23 retains the action schema and redirects only the final route.

## Limits

This package has not been installed/launched in the Android runtime by the build environment. CI tests operate on synthetic HUD fixtures, not on the user's device. Test offline with a disposable profile. Do not label the mod stable until it reaches the title screen, opens the route, and demonstrates the intended debug effect without regression.


## Regression CI receipt

GitHub Actions v23 schema-preservation workflow completed successfully: [run 40110265079](https://github.com/orionrayy/projects/actions/runs/40110265079). The job compiled the patcher and ran the synthetic regression tests. This confirms the patcher contract only; it does not establish runtime success on Android.

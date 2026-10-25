# Native Options tab limit — v49

**Status: STATIC-DIRECT disassembly finding. No executable or source asset was modified.**

## Direct evidence

The ARM64 dynamic symbol table exposes:

- \`uai_gp_options::onShowTab(int, S3DX::AIVariable const*, S3DX::AIVariable*)\`
- Virtual address: \`0x788890\`
- Function size: \`0x240\` bytes

Disassembly compares the numeric action argument with exactly four supported values:

| Value | Existing Pause HUD action | Visible content group |
|---:|---|---|
| 1.0 | \`onShowGameplay\` | \`GameplayMenu\` |
| 2.0 | \`onShowControls\` | \`ControlsMenu\` |
| 3.0 | \`onShowSocial\` | \`SocialMenu\` |
| 4.0 | \`onShowCredits\` | \`CreditsMenu\` |

The native entry branches at approximately \`0x7888f4\`, \`0x788948\`, \`0x78899c\`, and \`0x7889f0\` compare values 1, 2, 3, and 4 respectively. Inputs that match none of those comparisons reach the epilogue at \`0x788aa0\`; no fifth-tab branch appears in the function.

The existing HUD action sequences handle group visibility independently of this native tab callback. Therefore, a fifth group could be toggled by a serialized HUD action, but calling \`uai_gp_options.onShowTab(5.0)\` alone is not a valid tab integration: it has no matching native path for tab styling/state updates. A new tab would need an explicit UI state/layout strategy and on-device checks, rather than assuming the existing four-tab function recognizes it.

## Integration consequence

The direct stock route remains:
\`Pause → Options → Gameplay / Controls / Social-IAP / Credits\`.

A fifth Cheats page is not supported by the observed native tab-selection contract. The current v46 Gold row only proves that a button/action can be serialized into a separate debug HUD candidate. It does not establish the new Pause → Options route or connect the 222-entry catalog. The v47 route blocker remains in force.

## Next gate

Before editing the stock Options scene, choose and verify one of these designs against the exact game UI: (a) add a dedicated fifth native/model tab with a verified handler/state path, or (b) add a nested Cheats page reachable from an existing tab with explicit back navigation and stable selection state. Then implement the generic List population/callback and stable-ID dispatch; no APK should be built until those paths validate.

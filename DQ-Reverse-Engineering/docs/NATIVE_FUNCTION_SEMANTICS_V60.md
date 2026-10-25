# Native function semantics audit — v60

**Result: the Gold increment primitive is confirmed as a model function, while similarly named display handlers are not proven authoritative setters. The new HUD-to-function calling contract remains unproven; integration stays 0/222.**

## Reproducible source identity

The stock 3.3.2.0 source XAPK was extracted from the Library and decoded locally. The source STK contains 5,630 entries; CRC/size checks passed for the selected source assets. Stock and v50 candidate copies of \`libS3DClient.so\` have the same SHA-256: \`0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083\`. The selected \`uai_gp_hud.aim\` SHA-256 is \`66607a46a23eeaab4fa2dac02772adbea5ab71e65d4e446e49396c6af6a451cb\`.

The AIM v10 function table and native AArch64 symbols were correlated. \`uai_gp_hud\` has 133 functions and 240 handlers. This audit treats its AIM function table separately from handler names and does not infer a safe HUD callback solely from a symbol name.

## Findings

| Native method | Static evidence | Conclusion for cheat integration |
|---|---|---|
| \`RewardGold(AIVariable)\` at \`0x65feec\`, size 1,604 bytes | Accepts an AIVariable amount; performs numeric parse/addition, interacts with model API, and formats/publishes Gold UI values | Fixed increment primitive candidate; no generic HUD call contract or live effect proven. Keep separate from the Gold set-to-target slider. |
| \`RewardDust(AIVariable)\` at \`0x65eeec\`, size 908 bytes | Separate single-argument model function exists | Do not equate Dust with Gold, Crystal or Adventure Marks; state key/preconditions need more proof. |
| \`SpendGold(AIVariable)\` at \`0x637008\`, size 1,352 bytes | Single-argument function, but current debug/model context and state preconditions are unresolved | Do not expose as a generic arbitrary spend action. |
| \`onSetGold(...)\` at \`0x74ff84\`, size 288 bytes | Calls \`NumberToString\`, \`Concat\`, then an indirect model/UI call; no direct call to \`RewardGold\`/\`SpendGold\` is in this body | Display/label update candidate, not a proven authoritative currency setter. |
| \`onSetHealth(...)\` at \`0x7500a4\`, size 512 bytes | Parses two numeric-like inputs, computes a ratio and forwards it through an indirect model/API call | Do not map to health multiplier, health range or God Mode; actual player-state mutation is not proven. |
| \`onSetMana(...)\` at \`0x75090c\`, size 512 bytes | Same broad ratio/update pattern as the health handler | Do not map to Infinite Mana or Mana Regen Multiplier by name similarity. |
| \`onSetLevel(...)\` at \`0x7506a4\`, size 232 bytes | Retrieves, formats and forwards a value through an indirect call; no direct level-mutator call is present in the body | Display/update candidate, not a proven progression setter. |
| \`onStatIncrease(...)\` at \`0x75cb58\`, size 6,628 bytes | Large multi-branch stat-upgrade flow with context-dependent model-state reads/writes | Keep the existing upgrade workflow distinct from generic arbitrary stat overrides. |

The exported symbols and AIM names are useful structural evidence, but the indirect call targets are not renamed based on vtable offsets alone. No claim is made that the new HUD action system can call the model functions with arbitrary parameters.

## Integration decision

- The separate Gold +100K candidate still routes through the already-known \`onDebug(6.0)\` branch. It remains static-only and runtime-unverified.
- No method in this pass justifies assigning a catalog ID to a typed native handler.
- Catalog routes remain **0/222**, runtime-verified effects remain **0/222**, and the standalone Android harness remains disconnected from the game.
- No APK or XAPK was built. This respects the project gate to complete the requested menu/integration before generating another feature package.

## Next gate

Recover an exact engine-supported invocation route for an existing model function or acquire an authorized model/source extension workflow. Then prove one bounded action end-to-end on a disposable offline profile: HUD input → selected stable ID → allow-listed typed handler → authoritative state read-back → save/reload → regression. Until that succeeds, do not present the scrollable 222-entry catalog as connected gameplay functionality.
# Native client-function registration audit — v61

**New lead: the engine exports a native client-function registration API. Its existence is confirmed statically; the callback ABI, initialization path in this packaged game, and route from a newly authored HUD action to that callback remain unproven.**

## Build identity

Target: Dungeon Quest Android 3.3.2.0, package \`com.shinybox.smash\`, ARM64.
- Stock XAPK SHA-256: \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\`
- Stock STK SHA-256: \`340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3\`
- \`libS3DClient.so\` SHA-256: \`0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083\`
- Stock and v50 candidate copies of the native library have the same hash.

## Confirmed client API

| Export | Address / size | Directly observed call path |
|---|---|---|
| \`S3DClient_RegisterFunction\` | \`0x7aec14\`, 188 bytes | Validates a nonempty name and initialized engine, then calls \`Kernel::RegisterClientFunction(String, S3DX::AIFunction const*)\`. |
| \`S3DClient_UnregisterFunction\` | \`0x7aecd0\`, 132 bytes | Validates a nonempty name and calls \`Kernel::UnregisterClientFunction(String)\`. |
| \`S3DClient_CallHUDAction\` | \`0x7ae594\`, 112 bytes | Obtains GameManager and forwards an action name, 16-bit argument count and string-array pointer to \`GameManager::CallHUDAction\`. |

\`Kernel::RegisterClientFunction\` at \`0x82cccc\` (600 bytes) stores a named \`S3DX::AIFunction const*\` in a kernel-owned registry. \`Kernel::UnregisterClientFunction\` is at \`0x828628\` (164 bytes). This is concrete evidence of a registration mechanism; it is stronger than guessing from function names.

It is not yet a working game extension. The exported API receives an **opaque** \`S3DX::AIFunction\` pointer. We have not recovered the exact structure layout, callback ABI, user-data semantics, initialization hook or lifetime/thread rules for registering and unregistering that pointer in the packaged Dungeon Quest app.

## Important distinction: registration API versus HUD action API

The inspected \`S3DClient_CallHUDAction\` wrapper routes to \`GameManager::CallHUDAction\` at \`0xa5e5c0\` (844 bytes). That function validates the action name and places an action/argument record into an internal GameManager queue. The inspected copy path has four explicit string-argument slots; larger argument counts have not been validated. The wrapper does **not** directly invoke \`RewardGold\` or another \`uai_gp_hud\` model function.

This matters because there are three distinct mechanisms:
1. **Client-function registration:** associate a name with a supplied \`S3DX::AIFunction\` object.
2. **HUD action submission:** queue a named serialized action and text-like arguments for the engine's action path.
3. **AIM functions/handlers:** model resources hold script functions and native/model handlers with separate roles.

Static evidence does not yet prove how an action expression resolves a registered client function, or whether the app has a valid source-level location to register one. Do not conflate the three paths.

The engine's internal \`AIModel::AddFunction\` at \`0x83b6bc\` and \`AIModel::AddHandler\` at \`0x83bd98\` create or resolve engine model resources and assign scripts. Their existence is not, by itself, a supported external extension ABI.

## External engineering context

A legacy ShiVa Android tutorial describes native callbacks through the author-controlled native client project and event-hook registration: [Android Plugins part 4: No plugins!](https://vps.trisymphony.com/shivatutorials/pages/android-plugins-part-4-no-plugins/index.html). It shows that client-side native integration is possible in a normal ShiVa development project, but it does not prove the shipped Dungeon Quest APK includes that project, exposes the same build hook, or is compatible with that old tutorial's setup. citeturn987298view0

## Next steps / go-no-go

Before writing a client bridge or building a game APK, recover the exact-build \`S3DX::AIFunction\` declaration from an authorized matching header/SDK or source project, and establish how the packaged client can initialize it. Then test only a benign no-op callback in an isolated development package and prove registration → invocation → unregistration with lifecycle/thread behavior understood.

Only after that no-side-effect proof should a bounded, allow-listed cheat adapter be considered. Each game-state action must still pass an exact effect read-back, save/reload, backup/restore and regression gate.

## Current status

- Catalog: 222 IDs / 14 categories.
- Catalog routes assigned: **0/222**.
- Runtime-verified catalog effects: **0/222**.
- Separate Gold +100K candidate: runtime-verified **0/1**.
- v50 runtime manifest: **blocked at 0/9 checks**.
- No APK/XAPK or game asset was modified or built in this increment.
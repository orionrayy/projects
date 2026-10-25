# Dungeon Quest ModKit checkpoint — v61

Date: 25 October 2026 (WIB)
Repository: \`orionrayy/projects\`
Branch: \`feat/dq-iap-debug-cheats-modkit-v7\`
Base: v60 \`e4aa475a358fa3dc10537d53ae6bb2c50dc9eb8a\`

## Completed
- Audited the exported \`S3DClient_RegisterFunction\`, \`S3DClient_UnregisterFunction\`, and \`S3DClient_CallHUDAction\` entrypoints in the pinned ARM64 native library.
- Confirmed \`S3DClient_RegisterFunction\` passes a name and an opaque \`S3DX::AIFunction const*\` to \`Kernel::RegisterClientFunction\`; unregister passes the name to the kernel registry.
- Disassembled \`GameManager::CallHUDAction\`: it takes action name + count + string-array parameters and builds an internal queue record; the inspected path does not directly call the \`RewardGold\` model function.
- Distinguished this exported client-extension API from the HUD action queue and AIM model resources. Recorded function addresses/sizes and current unknowns.
- Added a machine-readable report, fail-closed validator, six synthetic tests, a dedicated CI workflow and this checkpoint.

## New lead, not a completed bridge
The client function registration API is a potential extension seam, but \`S3DX::AIFunction\` layout, callback ABI, lifecycle/thread rules, and a valid registration hook within the packaged Dungeon Quest app are not proven. The presence of the export is not enough to safely call it or to make a HUD action invoke a newly registered function.

## Status unchanged
- Catalog: 222 IDs / 14 categories; routes 0/222; runtime effects 0/222.
- Fixed Gold +100K candidate: static only, runtime 0/1.
- v50 runtime evidence gate remains blocked, 0/9.
- Harness remains explicitly disconnected.
- No game asset/native binary/APK/XAPK was changed or built.

## Next gate
Recover the exact \`S3DX::AIFunction\` definition and the app's authorized native initialization contract from matching SDK/source materials. Only then run a no-side-effect callback test in an isolated development package and prove register → invoke → unregister. Keep gameplay mutation and the full cheat catalog disabled until the runtime interface is demonstrated.

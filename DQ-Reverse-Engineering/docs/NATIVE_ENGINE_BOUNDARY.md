# Native Engine Boundary

**Current evidence snapshot:** see [NATIVE_SPLIT_AUDIT_V18.md](NATIVE_SPLIT_AUDIT_V18.md). This file supersedes the older statement that the matching ABI split had not been obtained.

## DEX/native boundary

The recovered DEX has 44 declarations marked native across four wrapper classes:

| Class | Native methods | Role inferred from method signatures |
|---|---:|---|
| com.shinybox.smash.S3DRenderer | 34 | Engine lifecycle, frame loop, surface lifecycle, pack descriptor, input and sensor forwarding |
| com.shinybox.base.ShinyActivity | 6 | Joypad events and global native callbacks |
| com.shinybox.googleplayservices.GooglePlayServicesWrapper | 2 | Login/initialization completion callbacks |
| com.shinybox.iap.IAPWrapper | 2 | Purchase success/failure callbacks |

The matching XAPK now provides the ARM64 split and four native libraries. The libS3DClient.so binary is ELF64/AArch64, has 64 Java_* dynamic exports, and includes C exports such as S3DClient_CallHUDAction and S3DClient_SetGameOption. These are binary-level findings, not a recovered engine source tree.

## What native exports do and do not establish

Static symbols and disassembly indicate that S3DClient_CallHUDAction delegates to the engine's internal GameManager action path and S3DClient_SetGameOption delegates to OptionsManager. The existing exports do not supply a validated Java binding contract, an authoritative function header, a safe calling-thread policy, a complete runtime state API, or proof that a requested player-stat/cheat action can be called safely.

Do not guess a native pointer, parameter meaning, option ID, or callback thread. Native integration requires a narrow adapter backed by explicit signatures and runtime tests, with the fail-closed sandbox gates maintained.

## S3D HUD/model boundary

The outer S3DMain.smf pack format is parsed and all 5,630 entries have passed CRC/decoded-size checks. However, Resources/HUD/pause.hud, Resources/HUD/debug.hud and the AIM model files are serialized binary resources. Finding names such as options, onShowOptions, uai_gp_debug, and onDebug proves only that the identifiers occur in assets. It does not prove a new menu row can be added by changing strings or that the options route can reach the debug model.

There is no validated HUD parser/serializer with lossless round-trip tests in the repository. Do not commit guessed byte-level edits to the proprietary scene.

## Current integration gate

- Matching package/version base, ARM64, density and language split set: recovered; see NATIVE_SPLIT_AUDIT_V18.md.
- Sampled split signer certificate fingerprints: matched.
- Native source/header/API documentation: unavailable.
- Actual Pause → Options → Cheats route: blocked/not runtime-verified.
- Verified game-state adapter and reversible gameplay effects: unavailable/not runtime-verified.
- Modified original-game APK build/install/launch: not performed.
- Receipt/entitlement tampering or purchase-check bypass: out of scope.

The separate DQ Cheats Sandbox Harness remains a reproducible Android UI test target only. Its successful build or emulator smoke test must not be described as an integrated Dungeon Quest APK.

# DQ Modkit — Synchronization Status v12

Date: 2026-10-24

## GitHub branch audit

Branch: `feat/dq-iap-debug-cheats-modkit-v7`  
PR: [#26](https://github.com/orionrayy/projects/pull/26) (open draft)  
Audited HEAD: `d8918a3a6f9b2a41a9c7b44c75cc0a9ab424ae54`

A recursive Git tree audit returned 235 entries (not truncated). Current curated repository counts:
- `disassembly/`: 2 actual .smali files plus the inventory Markdown; this is **not** 68 full class disassemblies.
- `reconstruction/java/`: 0 generated declaration scaffolds present.
- `manifest/`: 1 analysis-excerpt XML, not a full decoded manifest/resource set.
- `tools/`: 9 Python scripts.
- `tests/`: 7 Python test/validation scripts.
- `docs/`: 23 documentation/report files.
- `reconstruction/verified/java/` and `reconstruction/fragments/` contain curated source excerpts only.

Therefore the prior v10 delivery archive and this repository are not identical. The README now states that scope explicitly. The 68 generated disassembly files and 68 Java declaration scaffolds have not been synced into the repo. This is a factual inventory, not a claim that a full bundle was committed.

## IAP boundary

Observed DEX source:
- 104 distinct static IAP SKU literals.
- IAP.xml has 107 identifiers; 102 are shared.
- Purchase request routing uses Handler messages 600/602; restore uses 601.
- The purchase helper retrieves product details and calls an obfuscated billing adapter.
- `onPurchaseSuccess(String)` and `onPurchaseFailed(String)` are native declarations; DEX does not contain their reward bodies.

Observed game-data/model symbols:
- `InAppPurchase.aim`: purchase/restore callback symbols.
- `uai_gp_hud.aim`: `sPurchaseID`, `bPurchasing`, shop and purchase callback symbols.
- `uai_gp_account.aim`: `SetIAP`, `GetIAPString`, inventory/slot/stash helper symbols.
- `uai_gp_options.aim`: settings state and save/show callbacks.
- `uai_gp_debug.aim`: shader/logging diagnostic callbacks.
- `debug.hud`: CS/MS/level/Feat/Crystal/Eternal/Boss test controls.

The model bytecode is proprietary and only partially parsed. Symbol adjacency is not proof of a runtime call edge. No SKU is currently classified as reward-runtime-verified. The 46 cosmetic SKU-to-Vanity.xml matches are asset correlations only.

## Native dependency boundary

The supplied base APK contains zero `lib/*.so` files. DEX load order is `crypto`, `ssl`, `openal`, `S3DClient`. Manifest analysis indicates required ABI/density splits. A matching split set, exact ABI, per-library hashes, and dependency closure are not locally verified.

A replacement engine is not a credible small patch: it would need to implement 44 JNI declarations (34 on S3DRenderer), the render loop, pack access, input/audio, proprietary model/scene/animation formats, and behavior compatibility. Do not create placeholder shared libraries and call them compatible.

## Next actions

1. Obtain the exact version/signature-matching base + ABI + density split set, then inventory `lib/<abi>/*.so`, hashes, ELF machine, SONAME and NEEDED dependencies.
2. If the split set cannot be retrieved, ask the user to supply it; do not guess a binary or mix versions/signatures.
3. Decode the `.aim`/HUD bytecode or recover the original native library before mapping IAP callbacks to persisted player state.
4. Decide whether to synchronize generated class files based on their source availability and whether they contain sensitive or unnecessarily bulky artifacts. If included, provide a deterministic regeneration script and file hashes.
5. Keep README wording aligned with the actual tracked tree and CI state.

## Validation status

GitHub metadata verifies the current branch HEAD. No GitHub Actions run was returned for the HEAD at audit time. No complete Android build, APK signing, install, or runtime gameplay test is claimed.

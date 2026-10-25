# AIM/HUD List population and callback audit — v42

Date: 2026-10-25  
Target: Dungeon Quest Android 3.3.2.0, package \`com.shinybox.smash\`  
Status: native control-flow statically mapped; no game asset mutated and no APK/XAPK built.

## Evidence scope and reproducibility

The analysis used locally extracted source assets and the source ARM64 library. The native library is \`libS3DClient.so\`, SHA-256 \`0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083\`. The extracted binary assets and native library remain outside this repository; only this report and the existing read-only analysis tools are committed.

Related local source hashes:
- \`uai_gp_legendex.aim\`: \`2aa297031402a9796be6f044f4cdbf4018085217856ef9016dd2cedb84fec180\`
- \`legendex.hud\`: \`398b2445bde86f7584c49d57d2c5c785b2f4c5db1d98af1bbbae29eff4ecdb3f\`
- \`listitem_legend.hud\`: \`a71b611bb7bacec00cfd750e0f1dc241431b8bc8edd03ea473202f714173c00e\`
- \`pause.hud\`: \`12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395\`
- \`debug.hud\`: \`02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6\`

## Confirmed native template-row precedent

The source \`uai_gp_legendex.aim\` declares variables including \`htLegends\`, \`tTemplates\`, and \`nScrollValue\`, plus \`CreateLegendItem\`, \`UpdateList\`, and the UI callbacks \`onOpen\`, \`onClose\`, \`onChoose\`, \`onClicked\`, and \`onIdentify\`. These names are not merely unreferenced strings: they map to native AOT functions in the ARM64 library.

Static call-site cross-check:
- \`uai_gp_legendex::onOpen\` starts at VA \`0x76f1c0\`.
- At VA \`0x76f758\`, \`onOpen\` calls \`uai_gp_legendex::CreateLegendItem\` at \`0x76868c\`.
- At VA \`0x76f8e8\`, \`onOpen\` calls \`uai_gp_legendex::UpdateList\` at \`0x76bc80\`.
- \`CreateLegendItem\` references the template name \`listitem_legend\`, builds instance names from \`legend_\` plus an identifier, and references child/component keys \`.legend\`, \`.owned\`, \`.btn\`, \`.bg\`, and \`.clicked\`. It also references \`legendex.list\` and the \`uai_gp_legendex.onClicked\` callback.
- \`UpdateList\` reads the model's template/scroll state and handles the model-specific LegendEx collection, item details, and route to the companion \`legendex_choose\` UI. This is application-specific business logic, not a generic catalogue renderer.

This provides an actual working-game precedent for a parent container populated by named template instances, with a separate model method assigning row presentation and click routing. It is materially different from simply adding 222 serialized HUD elements.

## Why the element name "list" was misleading

The v41 parser identified:
- \`legendex.hud\`: 23 elements; the element named \`list\` is serialized as type 1 (container), not the native type-3 List element.
- \`match_result_anim.hud\`: the only type-3 List record among the 68 version-12 HUD assets inspected; that record is a rank-up/results control, not a cheat menu.
- \`pause.hud\` and \`debug.hud\`: no serialized type-3 List record.

Therefore a name-only search for \`list\` or a successful parse of a type-3 element is insufficient evidence for a working scrollable cheat list. The native template-row precedent suggests an alternative construction pattern, but its details are coupled to the existing LegendEx model.

## Integration boundary

The existing \`Pause → Options → Cheats\` route reaching \`uai_gp_hud.onDebug(0)\` only proves reachability of the existing Debug HUD; it does not provide a generic 222-command adapter. \`CreateLegendItem\` is not an unrestricted row/action API: it is part of the compiled \`uai_gp_legendex\` implementation and references LegendEx database data, template names, and LegendEx callbacks.

The native model implementation is AOT C++ in \`libS3DClient.so\`. Adding names to an \`.aim\` or \`.hud\` resource alone does not create a new native handler body or prove that a new callback will resolve. The repository contains a partial DEX reconstruction, not a complete native engine build project. No verified generic callback accepts an arbitrary cheat ID and performs a bounded, read-back-verifiable gameplay mutation.

Consequently:
- No game-side cheat is promoted to functional solely from this precedent.
- The 222 catalogue remains a design/source specification; gameplay effects remain \`0/222\` runtime-verified.
- Do not copy the existing LegendEx row or repoint its callback into a cheat action by guesswork.
- Do not change the production \`libS3DClient.so\`, stock package, billing/entitlement paths, cloud-save state, achievements, or leaderboards without a separately verified implementation.

## Next safe gate

1. Continue mapping the existing template-instance and component-container API calls from the native call path, including row lifetime/removal, callback binding, and re-open behavior.
2. Specify a dedicated allow-listed handler seam for a single non-destructive sandbox action. It must check current scene, offline/disposable profile, identifier, typed arguments, bounds, and result read-back; unmapped IDs stay disabled.
3. Prove the row template creation + scroll + selection route in a parallel package before expanding to all 222 entries. Keep the current stock installation and save isolated.
4. Package only after the native/model linkage and failure rollback are verified. Current decision remains **no new APK/XAPK**.

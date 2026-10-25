# Native template-row precedent audit — v57

**Result: two model-specific row-generation precedents are confirmed; a generic 222-cheat list/dispatcher is still unproven. No APK/XAPK was built in this increment.**

## Inputs and method

Read-only analysis of Dungeon Quest Android 3.3.2.0, stock XAPK SHA-256 \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\`, stock STK/S3DMain SHA-256 \`340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3\`, and ARM64 \`libS3DClient.so\` SHA-256 \`0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083\`. The source AIM inventory parsed all 162 AIM v10 record tables without framing errors. The parser reads table counts and first record-name strings; the opaque remaining record bytes are not treated as decoded script semantics.

## What the second precedent shows

There are two relevant but different compiled models:

| Model | AIM top-level counts (variables / functions / states / handlers) | Row/list-related names and native evidence |
|---|---|---|
| \`uai_gp_codex\` | 16 / 25 / 0 / 10 | \`CreateLegendItem\`, category-specific \`SelectFeatItem\`, \`SelectLegendItem\`, \`SelectMythicItem\`, \`SelectEternalItem\`, \`SelectDictionaryItem\`; state fields include \`tTemplates\`, \`nScrollValue\`, \`nCurrentItems\`, \`nCurrentItemID\`. Native AOT methods include \`CreateLegendItem\` at \`0x541d98\`, \`onOpen\` at \`0x557cdc\`, and the category selectors. |
| \`uai_gp_legendex\` | 4 / 10 / 2 / 5 | \`CreateLegendItem\` and \`UpdateList\`; state fields include \`tTemplates\` and \`nScrollValue\`. Native AOT methods include \`CreateLegendItem\` at \`0x76868c\`, \`UpdateList\` at \`0x76bc80\`, and handlers \`onOpen\`, \`onChoose\`, \`onClicked\`. |

Correction to a common false inference: \`UpdateList\` belongs to \`uai_gp_legendex\`; it is not listed as a top-level function in \`uai_gp_codex\`. Codex is a separate precedent with its own \`CreateLegendItem\` and category/item selectors.

## Model-specific coupling is visible

The Codex \`onOpen\` native body references domain-specific helpers such as \`HasRead\`, \`IsFound\`, \`GetMythicStatus\`, \`IsEternalUnlocked\`, \`OpenFeatPage\`, \`OpenDictionaryPage\`, and \`OpenMythicPage\`. The binary also contains Codex-specific resources such as \`codex.legend_btn\`, \`codex.legend_spell\`, \`codex.legend_element\`, \`codex.legend_title\`, \`codex.legend_desc\`, and craft/icon fields.

The LegendEx row builder constructs \`legend_\` instance names from item identifiers and references the \`listitem_legend\` template and \`legendex.list\` container. Its \`UpdateList\` uses LegendEx-specific item data and model state. These are concrete examples of application-specific row instantiation/update flows; the presence of a similarly named method does not convert either model into a generic menu host.

## Native List wrappers are necessary but not sufficient

The ARM64 library exports wrappers such as \`hud_addListItem\` (\`0x87a980\`), \`hud_setListItemTextAt\` (\`0x8c77e0\`), \`hud_setListOnSelectionChangedAction\` (\`0x862458\`), \`hud_getListSelectedItemAt\` (\`0x8a7f04\`), and scrolling controls. They resolve engine-managed HUD objects and use an engine \`HUDAction\` as the selection callback. They are not JNI endpoints that a separate Android Activity can call as a supported gameplay interface.

The inspected source/model evidence still does not provide all of the following for the 222-entry catalog:

1. A verified in-engine container and row-template construction path usable by a new cheat model.
2. A model callback that resolves the selected row to a stable catalog ID.
3. A typed, allow-listed native handler mapping with safe preconditions and bounded parameters.
4. Authoritative state read-back, save/reload evidence, rollback and regression proof for each enabled effect.

The Codex \`onOpen\` disassembly contains indirect model calls, so this report does not infer that indirect List/API use is impossible. It states the narrower finding: the call/data contract required for a generic cheat menu has not been recovered or validated. Neither cloning the serialized \`match_result_anim.hud\` type-3 List record nor copying a Codex/LegendEx template is a justified integration by itself.

## Decision and next engineering gate

The native integration registry remains **0/222 catalog routes and 0/222 runtime-verified effects**; the separate Gold +100K action remains a static-only candidate. Do not repoint Codex/LegendEx callbacks or expose command IDs by guesswork.

Next, recover a model-side callback contract from an authorized, exact-build source or use a documented engine extension point. Before any new game APK, prove one isolated row end-to-end: row population → selection callback → allow-listed stable ID → typed bounded handler → state read-back → save/reload → regression, on a disposable offline profile with verified backup/restore. Keep the current catalog fail-closed until that evidence exists.

## Reproduction / validation

- Machine-readable findings: \`NATIVE_TEMPLATE_ROW_PRECEDENT_AUDIT_V57.json\`.
- Validator and unit tests ensure that the report remains explicitly model-specific, does not promote generic dispatch, and does not increase the runtime-verified catalog count without evidence.
- Existing context: [AIM List callback audit v42](AIM_LIST_CALLBACK_AUDIT_V42.md), [native List API audit v44](NATIVE_LIST_API_CONTRACT_AUDIT_V44.md), [HUD List audit v53](HUD_LIST_LAYOUT_AUDIT_V53.md), and [native adapter registry v52](NATIVE_CHEAT_ADAPTER_REGISTRY_V52.md).
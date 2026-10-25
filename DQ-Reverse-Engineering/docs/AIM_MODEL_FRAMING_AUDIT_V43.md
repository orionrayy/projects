# AIM model framing audit v43 — read-only

Date: 2026-10-25  
Target: Dungeon Quest Android 3.3.2.0, package \`com.shinybox.smash\`  
Status: **Version-10 top-level framing parsed across all 162 source AIM files. Record payload internals remain opaque. No model was modified.**

## Source and validation boundary

The input is the matching source XAPK with SHA-256 \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\`. Its extracted \`assets/S3DMain.smf\` SHA-256 is \`340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3\`. The local STK verifier checked all 5,630 entries and validated stored-payload CRCs, decompressed lengths, and zlib stream boundaries before extracting model assets.

The read-only probe supports the source package's AIM v10 framing. It validates the \`NcX\`/\`NcP\` marker, reads the post-header v4+ prefix, then parses four length-framed record tables: variables, functions, states, and handlers. After the state table, it reads the selected/current-state string before the handlers table. Each table record is length-delimited; the first string in each record is inventoried as its name. The first handler byte is reported as a flag. Remaining record bytes are opaque: they are preserved only as sizes and SHA-256 fingerprints, not interpreted as scripts or bindings.

## Full source inventory results

| Measurement | Result |
|---|---:|
| AIM files | 162/162 parsed |
| Unsupported/truncated records | 0 |
| Variables | 3,889 |
| Functions | 664 |
| State descriptors | 164 |
| Handler records | 1,013 |
| Total framed records | 5,730 |
| Observed markers | 115 \`NcX\`, 47 \`NcP\` |
| Observed AIM versions | 10 only |

Selected models, matching the source files:

| Model | Variables | Functions | States | Handlers | Current state |
|---|---:|---:|---:|---:|---|
| \`uai_gp_hud.aim\` | 142 | 133 | 4 | 240 | \`Idle\` |
| \`uai_gp_options.aim\` | 18 | 11 | 0 | 9 | empty |
| \`uai_gp_debug.aim\` | 8 | 2 | 2 | 6 | \`Inactive\` |
| \`ai_Effect.aim\` | 2 | 0 | 0 | 2 | \`Spike\` |

One source anomaly is explicitly retained: \`ai_Effect.aim\` declares no state descriptors, but its current-state string is \`Spike\`. The parser reports this mismatch rather than silently correcting or rejecting it. The available evidence does not establish whether that string is a special transient state, a legacy serialization artifact, or a model-specific exception.

## What this resolves — and what it does not

The top-level state-table boundary and the following current-state string are now confirmed by a parser that consumes every byte of all 162 source AIM files. This resolves the earlier false boundary assumption that treated the state-name string as a handler-table count. It enables reliable inventories of model variable/function/handler identifiers for further analysis.

It does **not** decode variable types, function signatures, state event scripts, handler semantics, or the runtime callback graph. In particular, finding \`uai_gp_hud.onDebug\`, \`uai_gp_options.onShowTab\`, or List API names does not prove that an additional 222-row menu can be populated or that its selected rows can dispatch to safe handlers. Those semantics reside in opaque AIM record payloads and engine behavior not decoded here.

The synthetic suite covers table framing, handler flags, empty-state models, the current-state mismatch being reportable, multiple observed markers, truncation, trailing bytes, unsupported versions, and missing handler flags. Local result: 6 tests passed. The test suite is wired into the existing static CI workflow, but remote CI must be checked separately before claiming a passing GitHub Actions run.

## Next integration gate

Continue reverse-engineering the opaque AIM record payloads and the registered script APIs needed for dynamic List population, row selection, details and safe command dispatch. Any future AIM writer must preserve unknown payload bytes and be validated against a no-op source round trip; this probe intentionally has no rewrite capability. Do not build an APK/XAPK or enable a cheat on the basis of names alone. Current runtime verification remains 0/222 cheat effects.

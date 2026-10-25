# v50 package install preflight — actual-file replay v59

**File-level result reproduced:** both the v50 XAPK and standalone ARM64 APK share the stock app's package ID but have a different JAR/v1 signer fingerprint. An in-place update over the official-signed app is therefore expected to be rejected for signer incompatibility.

| Property | Stock XAPK | v50 candidate XAPK | v50 standalone ARM64 APK |
|---|---|---|---|
| SHA-256 | \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\` | \`680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430\` | \`f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa\` |
| Package ID | \`com.shinybox.smash\` | \`com.shinybox.smash\` | \`com.shinybox.smash\` |
| Split count | 20 | 20 | 1 |
| SHA-256 signer fingerprint | \`9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D\` | \`BF:94:D4:AC:89:C5:1D:D6:32:43:8F:E2:C9:A3:0D:41:59:FE:FF:42:14:66:7B:AB:1C:EF:E3:38:1F:3F:22:90\` | Same v50 test signer as the candidate XAPK |
| Outer ZIP / archive CRC | PASS | PASS | PASS |
| Split manifests consistent | PASS | PASS | PASS |

## Interpretation boundary

The preflight was executed against the actual stock and candidate files materialized in the working environment, using the v56 tool. The tool extracted per-APK binary manifest package IDs and JAR/v1 certificate identities, checked ZIP CRC, and emitted \`IN_PLACE_UPDATE_REJECTED_SIGNATURE_MISMATCH_EXPECTED\` for both candidate variants.

This explains a generic “App not installed” result **when attempting to update an already-installed official-signed \`com.shinybox.smash\` app**. It does not identify the cause of a clean-install failure without the exact Package Manager code. It also does not replace official v2/v3 \`apksigner\` validation, device installation, or runtime gameplay testing.

Do not uninstall the official app to test this. The candidate requires a separate-package diagnostic path and may still fail retained licensing/integrity checks; those must be recorded rather than bypassed. No new APK was built in this replay.

Machine-readable output: \`INSTALL_PREFLIGHT_ACTUAL_REPLAY_V59.json\`.
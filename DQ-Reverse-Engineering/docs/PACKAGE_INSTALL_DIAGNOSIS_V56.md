# Dungeon Quest package-install diagnosis — v56

**Finding:** the v50 candidate cannot be installed as an in-place update over the official Dungeon Quest package while the official app is installed, because its application ID matches but its signing certificate differs.

## Direct archive evidence

| Property | Official stock XAPK | v50 Gold +100K candidate XAPK |
|---|---|---|
| SHA-256 | \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\` | \`680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430\` |
| Package ID | \`com.shinybox.smash\` | \`com.shinybox.smash\` |
| Version | \`3.3.2.0\` | \`3.3.2.0\` |
| Split APKs | 20 | 20 |
| Outer XAPK ZIP CRC | PASS | PASS |
| APK certificate SHA-256 | \`9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D\` | \`BF:94:D4:AC:89:C5:1D:D6:32:43:8F:E2:C9:A3:0D:41:59:FE:FF:42:14:66:7B:AB:1C:EF:E3:38:1F:3F:22:90\` |
| Certificate identity | Shiny Box LLC | DQ ModKit v50 Test / Local Build |

JDK \`keytool\` extracted the same certificate fingerprint from all 20 splits in each XAPK. Each archive's split package IDs agree with its XAPK package name. The candidate's standalone ARM64 APK has the same local test certificate; its SHA-256 is \`f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa\`.

## Interpretation

When Android is asked to update an installed package, the package ID must match and the signing identity must be compatible. Here the package IDs match but the certificates are different, so the expected result is an update-signature conflict (commonly reported as \`INSTALL_FAILED_UPDATE_INCOMPATIBLE\` or shown to the user as a generic “App not installed”). This is distinct from an APK parse/certificate-block failure.

This diagnosis is conclusive for an attempted in-place update over the official-signed app. It does **not** establish the cause if the error occurred on a clean install with no copy of this package installed; the exact Package Manager error code would then be needed to classify that separate case.

## Safety and packaging decision

- Keep the official Dungeon Quest installation and its save untouched.
- Do not try to update it with the local test-signed v50 candidate.
- A separate-package diagnostic can avoid the package/signature collision, but it is a distinct test build and may be rejected by retained package/license checks. Do not bypass those checks.
- No new APK was produced in this increment; the project requirement to complete the 222-entry UI and integration work before a new feature APK remains unchanged.
- The known earlier \`INSTALL_PARSE_FAILED_NO_CERTIFICATES\` report was for v34's malformed v2 signing block. That historical fault must not be conflated with this v50 package-ID/signing mismatch.

## Reproduction

Use \`tools/dq_install_preflight_v56.py\` with the original stock XAPK and candidate XAPK. It verifies outer/inner ZIP CRC, XAPK package metadata, each split's manifest package ID, the extracted signer identities and consistency across splits, then classifies the in-place update condition. It is read-only and does not install or patch packages.

\`\`\`bash
python tools/dq_install_preflight_v56.py --stock /path/to/stock.xapk --candidate /path/to/candidate.xapk --output /path/to/install-preflight.json
\`\`\`

The tool extracts JAR/v1 signer certificates using JDK tools; it does not claim official APK Signature Scheme v2/v3 verification or game runtime validation.

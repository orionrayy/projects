# Dungeon Quest ModKit checkpoint — v59

Date: 25 October 2026 (WIB)
Repository: \`orionrayy/projects\`
Branch: \`feat/dq-iap-debug-cheats-modkit-v7\`
Base: v58 commit \`3b0df5577017edae7c1ee281203fcc5a79b51ae1\`

## Completed
- Re-executed the v56 read-only install preflight against the real stock XAPK, candidate XAPK and standalone ARM64 APK materialized from the Library.
- Reconfirmed the pinned file hashes, \`com.shinybox.smash\` package IDs, consistent split signer identities and signer-fingerprint difference on both v50 variants.
- Added a machine-readable actual-file replay report, explanatory note, fail-closed validator, five unit tests and dedicated CI workflow. Local validator PASS; tests 5/5 PASS.

## Finding and scope
Both candidates are expected to be rejected as in-place updates over an already-installed official-signed app because package IDs match while signer certificates differ. This does not prove that a clean install fails for the same reason; that requires the exact Android PackageManager result. The replay used JDK \`keytool\`/\`jarsigner\` for JAR/v1 certificate identity; it is not an official v2/v3 \`apksigner\` result or a device install test.

## Status deliberately unchanged
- No new game APK was built; the request to complete full menu/integration before another feature APK remains in force.
- Original-game runtime remains unverified; v50 candidate gate remains blocked at 0/9.
- Native cheat integration remains 0/222.
- Official app/save must remain untouched; do not bypass license/integrity checks.

## Next gate
Use a separate package identity for any isolated diagnostic build only when packaging work is authorized; first preserve the original app/save. If a clean installation still fails, record the exact PackageManager error code before attributing the failure. In parallel, the full cheat menu still requires a documented/authorized model callback contract and a verified typed handler for each enabled stable ID.

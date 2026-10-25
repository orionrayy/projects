# Dungeon Quest v50 actual-package audit — v68

**Audit result: PASS_STATIC_ONLY. Runtime status: NOT TESTED.**

Inputs were the exact stock XAPK and ModKit v50 candidate XAPK/standalone ARM64 APK materialized from the project Library on 25 October 2026.

## Reproduced file identities

| Artifact | SHA-256 | Size |
|---|---|---:|
| Stock XAPK | \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\` | 57,802,446 |
| v50 candidate XAPK | \`680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430\` | 57,623,091 |
| v50 candidate standalone ARM64 APK | \`f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa\` | 57,085,374 |

Both XAPKs declare \`com.shinybox.smash\`, version \`3.3.2.0\`, and 20 split APKs. All outer and inner ZIP CRC checks pass; their split-name inventories are identical.

## Content comparison

- After removing only generated JAR signature metadata entries from the APK content comparison, the **only split payload difference** is \`assets/S3DMain.smf\` in the base APK.
- The source XAPK base, candidate XAPK base, and standalone candidate APK have the same pinned \`classes.dex\` SHA-256: \`bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b\`.
- The standalone APK's \`assets/S3DMain.smf\` exactly matches the v50 XAPK candidate.
- All four ARM64 native-library files in the standalone candidate match the candidate's ARM64 split byte-for-byte.
- The STK parser decoded and validated all 5,630 records; 94,513,994 source decoded bytes were inspected. Exactly one decoded record differs: \`Resources/HUD/pause.hud\`, source SHA-256 \`12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395\`, candidate SHA-256 \`785ec813d316a833805ea7fe2c24ad8b3460774d978a07c6e065559a4a33c7af\`.

Machine-readable findings: [ACTUAL_PACKAGE_RECHECK_V68.json](ACTUAL_PACKAGE_RECHECK_V68.json).

## Signing and runtime boundary

The base APK in the stock package has signer fingerprint \`9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D\`; the local v50 candidate uses \`BF:94:D4:AC:89:C5:1D:D6:32:43:8F:E2:C9:A3:0D:41:59:FE:FF:42:14:66:7B:AB:1C:EF:E3:38:1F:3F:22:90\`. They have the same package ID but different signing certificates, so an in-place update over the official-signed app is expected to be rejected. This finding is distinct from a clean-install failure.

This audit does not establish Android PackageManager acceptance, APK Signature Scheme v2/v3 validity, game startup, HUD visibility/touch dispatch, the actual +100,000 Gold delta, save/reload persistence, save recovery or crash-free runtime. No game APK was built or installed in this audit.

## CI regression coverage

The repository tool \`tools/audit_actual_v50_packages_v68.py\` supports rerunning the actual-file comparison when the three input files are available. CI uses synthetic packages/STK fixtures only; it does not publish or check proprietary game binary inputs into the repository.

The dedicated workflow [DQ actual package audit v68](../../actions/workflows/dq-actual-package-audit-v68.yml) passed its synthetic audit regressions and existing STK single-asset delta verifier suite in run [40206936967](../../actions/runs/40206936967).

## Unresolved acceptance gates

- Original-game install, launch, and restart: not verified.
- Gold +100K button rendering and touch input: not verified.
- Exact Gold value delta and save/reload/save-recovery: not verified.
- Runtime-verified original-game catalog routes: 0/222.
- PR #26 remains a draft and must not be marked release-ready until isolated runtime evidence exists.

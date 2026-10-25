# Single-asset STK delta verifier — v48

**Purpose:** reproducibly prove that a candidate STK changes only the intended named asset, after decoding every entry from both archives.

## Tooling

- \`tools/verify_stk_single_asset_delta_v48.py\` opens both version-6 STK files using the existing validated pack parser.
- It checks distinct source/candidate paths, optional pinned whole-file hashes, version and entry count, the complete entry-name inventory, every entry's stored CRC and decoded size, and decoded content for every entry.
- It fails unless exactly one decoded entry differs and that path matches \`--expected-changed-path\` (default: \`Resources/HUD/debug.hud\`).
- The optional JSON report contains whole-archive hashes and before/after size/hash for the changed entry. Report output refuses to overwrite an existing file unless explicitly told otherwise.

## Reproduce against local source and candidate

    python tools/verify_stk_single_asset_delta_v48.py \
      /mnt/data/dqwork/S3DMain.smf \
      /mnt/data/dqwork/candidates/S3DMain_gold_candidate_v46.smf \
      --expected-source-sha256 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3 \
      --expected-candidate-sha256 ca6387141047a096cc279d06a03c6392602d1cd0a3c97643067c48434b8bfa57 \
      --report /mnt/data/dqwork/candidates/S3DMain_gold_candidate_v46.delta-v48.json

Expected result for this pair: status PASS; STK v6; 5,630 entries; source decoded total 94,513,994 bytes; exactly one changed entry, \`Resources/HUD/debug.hud\`; all other decoded payloads identical. Candidate decoded payload total is 94,514,250 bytes. The report is a local validation artifact and is not committed with the original game binaries.

## Regression coverage and limits

Six synthetic tests cover a valid single asset change, two changes, an unexpected changed path, inventory changes, an incorrect source hash pin, and identical source/candidate paths. CI runs these tests without including any original APK, XAPK, STK, HUD binary, or native library.

This is integrity verification for a data-level candidate. It cannot prove that the game loads the candidate, that the button renders/clicks, that the native branch executes, or that Gold is awarded/persisted. It is not an Android build or runtime test.

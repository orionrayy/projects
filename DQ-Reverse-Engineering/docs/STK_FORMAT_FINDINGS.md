# S3DMain.smf — Confirmed STK-style archive format

**The outer container is decoded and all 5,630 entries have passed validation.** This resolves the earlier uncertainty about the archive layer. It does not decompile the engine code or turn inner binary model/scene records into native source.

## Header and table evidence

| Field | Observed value |
|---|---:|
| File size | 33,978,539 bytes |
| SHA-256 | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` |
| Header signature | `0x00000008` |
| Version nibble | `6` |
| Flags byte | `0x00` |
| XOR key | `0x4c4060e8` |
| Entry count | `5,630` |
| Metadata end/data-start offset | `335,530` |
| Payload bytes | `33,642,009` |
| Verified output size | `94,513,994` bytes |

The packed header is 25 bytes (`<BI8sIII`). The `entry_table_size` field behaves as an absolute end offset including the header, so the encrypted table occupies bytes `[25, 335530)`, exactly 335,505 bytes. XORing the table with the key's four little-endian bytes reveals exactly 5,630 records and consumes the entire table with no residue.

Each record consists of a 32-bit filename length, UTF-8 filename bytes, 32-bit data offset, compressed size, uncompressed size, CRC-32 and 16-bit flags. Payload offsets are relative to the metadata-end/data-start offset. Every payload is XOR-decoded before checking its CRC-32. For version 6 and flags `0x00`, non-raw payloads are zlib-compressed.

## Validation results

- 5,630/5,630 records parsed.
- 5,630/5,630 payloads passed CRC-32 and decoded-size checks.
- 5,619 entries were `zlib+xor`; 11 were `raw+xor`.
- Total verified uncompressed content: 94,513,994 bytes.
- Output paths were checked for traversal and absolute-path attacks before writing.
- The APK, raw DEX, container and credential-bearing `assets/api_key.txt` are not embedded in the source workspace.

A public MIT-licensed STK unpacking reference was useful for the initial format hypothesis: https://github.com/salactic/stk_unpacker . That implementation has incomplete branches, so this project uses its own standard-library Python parser rather than executing that C++ tool. This parser is currently validated against the supplied version-6 archive.

## Reproduce

```bash
python tools/stk_unpacker.py /path/to/S3DMain.smf \
  --inventory-json docs/asset-inventory.json \
  --inventory-csv docs/asset-inventory.csv

python tools/stk_unpacker.py /path/to/S3DMain.smf \
  --extract /path/to/new-empty-output-directory
```

Extraction validates the entire archive before writing. It refuses a non-empty output directory, duplicate/case-colliding names, unsafe paths, out-of-range entries, CRC mismatches, wrong decoded sizes and unknown compression flags.

## Remaining boundary

The archive container is resolved. Inside it, `.mdo`, `.msh`, `.ske`, `.scn`, `.gam`, `.aim` and related engine-specific files remain binary structures. XML tables are readable game data, not engine implementations. Native JNI bodies remain unavailable from DEX; see `NATIVE_ENGINE_BOUNDARY.md`.

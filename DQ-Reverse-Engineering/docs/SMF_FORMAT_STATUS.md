# S3DMain.smf — Format Investigation Status

**Current status: outer STK-style archive parsed and all entries verified.** The previous unresolved-container assessment is superseded by the results below. Inner game/model/scene formats remain proprietary binary.

- File size: 33,978,539 bytes.
- SHA-256: `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3`.
- Signature: `0x00000008`; version nibble: `6`; raw flags: `0x00`.
- XOR key: `0x4c4060e8`.
- Entry count: 5,630.
- Metadata end/data-start offset: 335,530 bytes.
- 5,619 zlib+XOR records and 11 raw+XOR records.
- All 5,630 payload CRC-32 values and decoded output lengths matched.
- Total decoded content: 94,513,994 bytes.

The header is 25 bytes. The metadata end field behaves as an absolute offset including the header; parsing the XOR-decoded table from byte 25 to 335,530 consumes exactly 335,505 bytes, with no residual bytes. For each record, the payload is located at metadata-end plus entry offset, XOR-decoded with the four little-endian key bytes, CRC-checked, then zlib-decoded where compressed size differs from output size.

## Reproduce

```bash
python tools/stk_unpacker.py /path/to/S3DMain.smf --inventory-json docs/asset-inventory.json --inventory-csv docs/asset-inventory.csv
python tools/stk_unpacker.py /path/to/S3DMain.smf --extract /path/to/new-empty-output-directory
```

The parser uses the Python standard library, validates all entries before extraction, and rejects unsafe paths, out-of-bounds payloads, CRC mismatches, incorrect decoded lengths and unsupported compression flags.

The STK format hypothesis was cross-checked against a public MIT-licensed reference: https://github.com/salactic/stk_unpacker . This project uses its own safer Python implementation; the reference implementation has incomplete branches and is not executed by this tool.

See `STK_FORMAT_FINDINGS.md` and `ASSET_CATALOG.md`. Successful container extraction is not full source decompilation: the extracted `.gam`, `.mdo`, `.msh`, `.ske`, `.scn` and related formats still need internal schema analysis, and native JNI bodies remain missing.

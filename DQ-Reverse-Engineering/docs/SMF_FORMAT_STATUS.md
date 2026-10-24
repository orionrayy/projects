# S3DMain.smf — Format Investigation

**Status: unresolved binary/proprietary game pack.**

- Size: 33,978,539 bytes.
- SHA-256: `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3`.
- Header starts `06 08 00 00 00 20 20 20 20 20 20 20 20 e8 60 40 4c ...`.
- Byte entropy: 7.989512 bits/byte; every byte value is present.
- GZIP candidates: zero plausible candidate headers and zero validated streams.
- zlib candidates: 3,952 header-like byte locations, zero fully validated streams under a bounded probe.
- Known magic matches are candidates only, not embedded files, unless format-specific structure validates.

High entropy plus failed common-format tests is consistent with proprietary packing, compression, encryption, or another encoding. It does **not** prove the asset is encrypted. No decode, decrypt, or unpack success is claimed.

Next work should focus on validating record offsets/lengths and chunk boundaries against multiple authorized samples or legitimate engine tooling. Keep probes read-only and reject byte sequences that do not pass structural validation.

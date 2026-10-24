# S3DMain.smf — Format Investigation

**Status: unresolved binary/proprietary game pack.**

- Size: 33,978,539 bytes.
- SHA-256: `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3`.
- Header starts `06 08 00 00 00 20 20 20 20 20 20 20 20 e8 60 40 4c ...`.
- Byte entropy: 7.989512 bits/byte; every byte value is present.
- In the APK ZIP container, the entry is STORED (method 0), not ZIP-compressed: compressed and uncompressed sizes both equal 33,978,539 bytes. This is consistent with code calling `AssetManager.openFd("S3DMain.smf")`.
- GZIP candidates: zero plausible candidate headers and zero validated streams.
- zlib candidates: 3,952 header-like byte locations; zero fully validated streams in a bounded probe.
- Other common magic hits are treated only as byte candidates, not embedded files, unless the format-specific structure validates.

High entropy plus failed common-format tests is consistent with proprietary packing, compression, encryption, or another encoding. It does **not** prove the asset is encrypted. The pack is passed to native code with a file descriptor, start offset, and length, but those Java calls do not expose the pack's internal schema.

No decode, decrypt, or unpack success is claimed. Next work should focus on validated record offsets/lengths and chunk boundaries across multiple authorized samples or legitimate engine tooling. Keep probes read-only and reject byte sequences that do not pass structural validation.

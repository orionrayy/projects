# Bundle Validation

Validated in the local analysis environment:

- Decoded `manifest/AndroidManifest.xml` parses as well-formed XML.
- DEX index JSON parses and reports 68 app-specific classes emitted.
- Exactly 68 Dalvik disassembly files were generated.
- SMF probe hash and byte count match the measured input asset.
- Python analysis scripts pass `py_compile`.
- The generated local bundle excludes the original APK and credential-bearing `assets/api_key.txt`.

These are static integrity checks only. They do not prove that the disassembly is re-assemblable, that a reconstructed app builds, or that the proprietary game pack has been decoded.
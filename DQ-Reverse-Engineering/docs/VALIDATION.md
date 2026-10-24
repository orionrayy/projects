# Validation Record — Iteration 3

Static integrity results from the local analysis environment:

- 68 app-specific class disassembly files.
- 405 decoded methods, 5,187 instruction boundaries, and 50 switch/array payload directives.
- Zero structural consistency errors reported by the local Smali-like validator.
- DEX index JSON parses and records 68 app-specific classes.
- Decoded manifest XML parses as well-formed XML.
- SMF probe size and SHA-256 match the measured asset (33,978,539 bytes; 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3).
- Python helper scripts pass py_compile.
- BuildConfig.java, Globals.java, and S3DEngine.java compile using javac against minimal temporary stubs for Android Configuration, Application, and dependency superclass q0.b.
- Sensitive-token file and original APK are excluded from the generated analysis bundle.

The manifest's requiredSplitTypes value (base__abi,base__density) and isSplitRequired flag indicate that this archive may be a base APK from a split delivery. See SPLIT_APK_FINDINGS.md.

These checks do not establish Smali assembler acceptance, successful JADX output, Android Gradle buildability, APK signing, emulator launch, runtime equivalence, retrieval of companion splits, or SMF decoding. Treat this as reverse-engineering source material, not a ready-to-install rebuild.

# Validation Record

The corrected 68-class Smali-like reconstruction passed static consistency checks:

- 68 class files
- 405 method bodies
- 5,187 decoded instructions
- 50 switch/array payloads
- Zero structural validation errors

The static validator checks method boundaries, instruction/payload code-unit coverage, branch label references, register bounds, and unresolved placeholders. The decoded manifest XML is well formed, and Python helper files pass syntax compilation. The source bundle excludes the original APK, raw `classes.dex`, `S3DMain.smf`, and `api_key.txt`.

Not validated: Smali assembler acceptance, Java decompilation, Gradle build, APK signing, emulator launch, runtime equivalence, or SMF decoding. Treat the output as reverse-engineering source material, not a ready-to-install rebuild.

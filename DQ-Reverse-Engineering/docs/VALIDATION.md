# Validation Record — Iteration 4

Static validation in the local analysis environment:

- 68 app-specific Dalvik-level files, 405 methods, 5,187 instruction boundaries and 50 payload directives.
- Zero structural consistency errors from the local Smali-like validator.
- DEX index, reachability JSON and the 104-ID IAP inventory parse successfully.
- Full manifest and analysis excerpt parse as well-formed XML; split metadata is consistent with a base/split delivery hypothesis.
- Outer STK container: 5,630/5,630 entries parsed; all payload CRC-32 values and expected decoded lengths matched.
- Content output: 5,619 zlib+XOR entries, 11 raw+XOR entries, 94,513,994 total decoded bytes.
- Seventeen `Resources/XML/*.xml` data tables parse and contain 2,623 row records.
- Three higher-confidence Java source excerpts compile via `javac` against temporary stubs for Android `Configuration`, `Application` and superclass `q0.b`.
- Python helpers pass syntax compilation.
- Original APK, raw DEX, source asset container and credential-bearing `api_key.txt` are excluded from this source workspace.

Not validated: full JADX decompilation, Smali assembler acceptance, native library recovery, Android Gradle build, APK signing, emulator launch, runtime equivalence, or source decompilation of inner `.gam`/`.mdo`/`.scn` formats. This is reverse-engineering source material, not a ready-to-install rebuild.

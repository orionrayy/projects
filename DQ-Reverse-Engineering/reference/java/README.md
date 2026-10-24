# Java Contract Snapshot

This folder adds a small Java source representation alongside the DEX-derived Smali-like files.

- `S3DNativeEngineContract.java` carries all 34 method signatures declared native by `com.shinybox.smash.S3DRenderer`.
- `GlobalsSnapshot.java` preserves four observed static values from `com.shinybox.smash.Globals`.

The contract interface and snapshot compile with a standard JDK; it is not a reconstruction of the renderer implementation. The contract is a type reference for independent reimplementation. Because it has a different owner name and no JNI implementation, it cannot load the original native methods by itself.

These two Java files were compiled with `javac` in the analysis environment. This does **not** establish that the Android app can be rebuilt: matching ABI/density split APKs, native libraries, resources and the SMF format remain unresolved.

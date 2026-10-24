# DEX Control-Flow / Reachability Summary

The current local disassembly contains 361 methods with code for the 68 com.shinybox.* classes. A best-effort control-flow traversal from each method entry reported 5,071 reachable instruction boundaries and 120 boundaries not reached by its simplified CFG model.

Two suspicious/reserved opcode positions were flagged as reachable in com.shinybox.smash.CameraPreview.surfaceChanged (code offsets 0x006e and 0x0076). The output around these locations also contains implausible register operands. They may be the result of opaque/dead-code obfuscation or an imperfect decoder; no Java translation is asserted for them.

Caveats:

- The CFG walker is heuristic and does not model exception-handler edges completely.
- Unreachable under this model is not proof that code is safe to remove.
- Reserved opcodes are preserved and reported instead of translated into invented Java.
- Re-run the local tools/analyze_dex_reachability.py against the original DEX and corresponding disassembler when validating a newer decoder.

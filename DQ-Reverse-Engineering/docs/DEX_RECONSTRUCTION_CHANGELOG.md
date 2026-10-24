# Reconstruction Changelog

## Decoder correction pass

The first disassembler output had incorrect instruction-width classifications for some Dalvik opcode formats. An incorrect width advances the code-unit cursor to the wrong location and can corrupt every subsequent decoded instruction in a method.

The corrected pass recalculated instruction widths from DEX formats, recovered method/field descriptors and encoded static values, handled switch/array payload blocks and exception regions, then regenerated all 68 application-namespace class snapshots.

## Current static metrics

- 68 class files
- 405 methods
- 5,187 instructions
- 50 payload directives
- 44 native declarations
- Zero errors from the structural consistency validator

## Meaning of the result

The checks establish internal consistency of emitted instruction/payload lengths against DEX code-unit spans, branch labels, register indices, and method boundaries. They do not prove that the output assembles, builds, installs, or behaves identically to the original. Original Java source-level information is not recoverable from DEX, and the native engine libraries were absent from the provided APK archive.

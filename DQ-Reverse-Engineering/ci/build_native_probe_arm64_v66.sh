#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || -z "$1" ]]; then
  echo "Usage: $0 OUTPUT_DIRECTORY" >&2
  exit 2
fi
OUT_DIR="$1"
NDK_ROOT="$ANDROID_NDK_HOME"
if [[ -z "$NDK_ROOT" || ! -f "$NDK_ROOT/build/cmake/android.toolchain.cmake" ]]; then
  echo "ERROR: Android NDK not found; set ANDROID_NDK_HOME" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
mkdir -p "$OUT_DIR"

cmake -S "$PROJECT_DIR/native-client-probe-v64" -B "$OUT_DIR" \
  -DCMAKE_TOOLCHAIN_FILE="$NDK_ROOT/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a \
  -DANDROID_PLATFORM=android-23 \
  -DANDROID_STL=c++_static \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$OUT_DIR" --config Release --parallel 2

LIB="$OUT_DIR/libdqbridge.so"
READELF="$NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf"
if [[ ! -s "$LIB" || ! -x "$READELF" ]]; then
  echo "ERROR: missing output library or LLVM readelf" >&2
  exit 3
fi

HEADER="$("$READELF" -h "$LIB")"
grep -q 'Class:.*ELF64' <<<"$HEADER"
grep -q 'Machine:.*AArch64' <<<"$HEADER"
EXPORTS="$("$READELF" --dyn-syms --wide "$LIB")"
grep -q 'Java_com_shinybox_smash_DqNativeProbe_nativeRegisterProbe' <<<"$EXPORTS"
grep -q 'Java_com_shinybox_smash_DqNativeProbe_nativeInvokeProbe' <<<"$EXPORTS"
grep -q 'Java_com_shinybox_smash_DqNativeProbe_nativeUnregisterProbe' <<<"$EXPORTS"

cat > "$OUT_DIR/build-manifest.json" <<JSON
{
  "schema": "dq-native-client-probe-arm64-build-v66",
  "scope": "native library only; not an APK and not integrated into Dungeon Quest",
  "abi": "arm64-v8a",
  "platform": "android-23",
  "ndk_version_dir": "$(basename "$NDK_ROOT")",
  "artifact": "libdqbridge.so",
  "size_bytes": $(wc -c < "$LIB" | tr -d ' '),
  "sha256": "$(sha256sum "$LIB" | awk '{print $1}')",
  "elf_class": "ELF64",
  "elf_machine": "AArch64",
  "jni_exports": [
    "Java_com_shinybox_smash_DqNativeProbe_nativeRegisterProbe",
    "Java_com_shinybox_smash_DqNativeProbe_nativeInvokeProbe",
    "Java_com_shinybox_smash_DqNativeProbe_nativeUnregisterProbe"
  ],
  "game_state_side_effects": false,
  "packaged_into_game": false,
  "runtime_invoked": false
}
JSON

echo "PASS: Android ARM64 native probe built and ELF/JNI export checks passed"
sha256sum "$LIB" "$OUT_DIR/build-manifest.json"

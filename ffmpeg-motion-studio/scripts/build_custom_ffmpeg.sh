#!/usr/bin/env bash
# Build a version-pinned FFmpeg for the FFmpeg Motion Studio Linux render profile.
# This creates a Ubuntu 24.04 x86_64 package; it does not replace a user's system FFmpeg.
set -Eeuo pipefail

VERSION="${FFMPEG_VERSION:-9.0.2}"
EXPECTED_SHA256="8c3850283eb25fa026482078a04051e0be17347b09ef81a0849bec15a96e002e"
EXPECTED_SIGNER_FPR="FCF986EA15E6E293A5644F10B4322F04D67658D8"
JOBS="${BUILD_JOBS:-2}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_ROOT="${RUNNER_TEMP:-${TMPDIR:-/tmp}}"
WORK="${WORK_ROOT%/}/ffmpeg-motion-studio-build-${VERSION}"
DIST="$PROJECT_ROOT/dist"
SOURCE="ffmpeg-${VERSION}.tar.xz"
SOURCE_URL="https://ffmpeg.org/releases/${SOURCE}"
KEY_URL="https://ffmpeg.org/ffmpeg-devel.asc"

if [[ "$VERSION" != "9.0.2" ]]; then
  echo "This source/configuration pin is reviewed only for FFmpeg 9.0.2, got: $VERSION" >&2
  exit 2
fi

rm -rf "$WORK"
mkdir -p "$WORK" "$DIST"
cd "$WORK"

echo "::group::Download official FFmpeg source and signature"
curl --fail --show-error --silent --location --retry 3 --retry-all-errors -o "$SOURCE" "$SOURCE_URL"
curl --fail --show-error --silent --location --retry 3 --retry-all-errors -o "${SOURCE}.asc" "${SOURCE_URL}.asc"
curl --fail --show-error --silent --location --retry 3 --retry-all-errors -o ffmpeg-devel.asc "$KEY_URL"

printf '%s  %s\n' "$EXPECTED_SHA256" "$SOURCE" | sha256sum --check --strict -

export GNUPGHOME="$WORK/gnupg"
mkdir -m 700 "$GNUPGHOME"
gpg --batch --import ffmpeg-devel.asc
ACTUAL_SIGNER_FPR="$(gpg --batch --with-colons --show-keys ffmpeg-devel.asc | awk -F: '$1 == "fpr" {print $10; exit}')"
if [[ "$ACTUAL_SIGNER_FPR" != "$EXPECTED_SIGNER_FPR" ]]; then
  echo "Unexpected FFmpeg release-signing key fingerprint: $ACTUAL_SIGNER_FPR" >&2
  exit 1
fi
gpg --batch --verify "${SOURCE}.asc" "$SOURCE"
echo "::endgroup::"

echo "::group::Configure and build FFmpeg $VERSION"
tar -xJf "$SOURCE"
cd "ffmpeg-$VERSION"
./configure \
  --prefix="$WORK/install" \
  --bindir="$WORK/install/bin" \
  --disable-debug \
  --disable-doc \
  --disable-ffplay \
  --enable-gpl \
  --enable-libass \
  --enable-libfreetype \
  --enable-libfontconfig \
  --enable-libfribidi \
  --enable-libharfbuzz \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-libdav1d \
  --enable-libaom \
  --enable-libzimg
make -j"$JOBS"
make install
echo "::endgroup::"

echo "::group::Run media pipeline regression tests"
bash "$PROJECT_ROOT/scripts/smoke_test_ffmpeg.sh" "$WORK/install/bin" "$WORK/regression"
echo "::endgroup::"

echo "::group::Package binaries and build provenance"
BUNDLE="$WORK/bundle"
mkdir -p "$BUNDLE/bin" "$BUNDLE/share"
install -m 0755 "$WORK/install/bin/ffmpeg" "$BUNDLE/bin/ffmpeg"
install -m 0755 "$WORK/install/bin/ffprobe" "$BUNDLE/bin/ffprobe"
"$WORK/install/bin/ffmpeg" -version > "$BUNDLE/share/ffmpeg-version.txt"
"$WORK/install/bin/ffmpeg" -buildconf > "$BUNDLE/share/ffmpeg-buildconf.txt"
cp "$WORK/regression/summary.json" "$BUNDLE/share/regression-summary.json"

{
  echo "Target: FFmpeg $VERSION"
  echo "Platform: Ubuntu 24.04 x86_64"
  echo "Source URL: $SOURCE_URL"
  echo "Source SHA-256: $EXPECTED_SHA256"
  echo "Source signature: verified with pinned FFmpeg release-signing key $EXPECTED_SIGNER_FPR"
  echo "Build jobs: $JOBS"
  echo "Built at UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Workflow commit: ${GITHUB_SHA:-local}"
  echo
  echo "Runtime shared-library report:"
  ldd "$BUNDLE/bin/ffmpeg"
  echo
  echo "Required Ubuntu build/runtime packages and resolved versions:"
  dpkg-query -W -f='${binary:Package}=${Version}\n' \
    build-essential pkg-config nasm yasm curl gnupg \
    libass-dev libfreetype6-dev libfontconfig1-dev libfribidi-dev libharfbuzz-dev \
    libmp3lame-dev libopus-dev libvorbis-dev libvpx-dev libx264-dev \
    libx265-dev libdav1d-dev libaom-dev libzimg-dev zlib1g-dev
} > "$BUNDLE/share/build-manifest.txt"

if ldd "$BUNDLE/bin/ffmpeg" | grep -q "not found"; then
  echo "The built FFmpeg has unresolved runtime shared-library dependencies." >&2
  exit 1
fi

(
  cd "$BUNDLE"
  sha256sum bin/ffmpeg bin/ffprobe share/* > SHA256SUMS
)
ARCHIVE="$DIST/ffmpeg-${VERSION}-ubuntu-24.04-x86_64.tar.gz"
tar --sort=name --mtime='UTC 1970-01-01' --owner=0 --group=0 --numeric-owner -czf "$ARCHIVE" -C "$BUNDLE" .
( cd "$DIST" && sha256sum "$(basename "$ARCHIVE")" | tee "$(basename "$ARCHIVE").sha256" )
cp "$WORK/regression/summary.json" "$DIST/ffmpeg-${VERSION}-regression-summary.json"
echo "Created: $ARCHIVE"
echo "::endgroup::"

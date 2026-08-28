#!/usr/bin/env bash
# Vendor a pinned reveal.js dist into <target-dir>: reveal.js, reveal.css, reset.css,
# the speaker-notes plugin, and the MIT LICENSE (required alongside vendored code).
# Usage: fetch-reveal.sh <target-dir> [version]   (default version: 5.2.1)
set -euo pipefail

TARGET="${1:?usage: fetch-reveal.sh <target-dir> [version]}"
VERSION="${2:-5.2.1}"
TARBALL="$(mktemp -d)/reveal.tar.gz"

curl -fsSL --max-time 60 -o "$TARBALL" \
  "https://github.com/hakimel/reveal.js/archive/refs/tags/${VERSION}.tar.gz" \
  || { echo "download failed — network may be blocked; ask the user for a reveal.js dist" >&2; exit 1; }

mkdir -p "$TARGET"
tar -xzf "$TARBALL" -C "$(dirname "$TARBALL")" \
  "reveal.js-${VERSION}/dist/reveal.js" \
  "reveal.js-${VERSION}/dist/reveal.css" \
  "reveal.js-${VERSION}/dist/reset.css" \
  "reveal.js-${VERSION}/plugin/notes/notes.js" \
  "reveal.js-${VERSION}/LICENSE"
SRC="$(dirname "$TARBALL")/reveal.js-${VERSION}"
cp "$SRC/dist/reveal.js" "$SRC/dist/reveal.css" "$SRC/dist/reset.css" \
   "$SRC/plugin/notes/notes.js" "$SRC/LICENSE" "$TARGET/"
rm -rf "$(dirname "$TARBALL")"
echo "vendored reveal.js ${VERSION} into ${TARGET}"

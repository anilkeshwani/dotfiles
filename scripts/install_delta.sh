#!/usr/bin/env bash

# Install delta (https://github.com/dandavison/delta) for Linux x86_64.
# The binary is placed in ~/.local/bin.

set -euo pipefail

DELTA_VERSION="0.19.1"
TARBALL_URL="https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/delta-${DELTA_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
INSTALL_DIR="${HOME}/.local/bin"

tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT  # clean up temp dir on exit, error, or interrupt

echo "Downloading delta ${DELTA_VERSION} ..."
wget -q "${TARBALL_URL}" -O "${tmpdir}/delta.tar.gz"

tar -xzf "${tmpdir}/delta.tar.gz" -C "${tmpdir}"

mkdir -p "${INSTALL_DIR}"
mv "${tmpdir}/delta-${DELTA_VERSION}-x86_64-unknown-linux-gnu/delta" "${INSTALL_DIR}/delta"

echo "Installed delta to ${INSTALL_DIR}/delta"

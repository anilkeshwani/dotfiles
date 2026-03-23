#!/usr/bin/env bash

# Install delta (https://github.com/dandavison/delta) for Linux.
# Supports x86_64 and aarch64. The binary is placed in ~/.local/bin.

set -euo pipefail

DELTA_VERSION="0.19.1"
INSTALL_DIR="${HOME}/.local/bin"

# Idempotency: skip if the desired version is already installed
if command -v delta >/dev/null 2>&1 && delta --version 2>/dev/null | grep -q "${DELTA_VERSION}"; then
    echo "delta ${DELTA_VERSION} already installed, skipping."
    exit 0
fi

# Detect architecture
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64)  ARCH_TRIPLE="x86_64-unknown-linux-gnu" ;;
    aarch64) ARCH_TRIPLE="aarch64-unknown-linux-gnu" ;;
    *)
        echo "ERROR: install_delta.sh does not support architecture: ${ARCH}" >&2
        exit 1
        ;;
esac

ARCHIVE="delta-${DELTA_VERSION}-${ARCH_TRIPLE}"
TARBALL_URL="https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/${ARCHIVE}.tar.gz"

tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT  # clean up temp dir on exit, error, or interrupt

echo "Downloading delta ${DELTA_VERSION} (${ARCH}) ..."
wget -q "${TARBALL_URL}" -O "${tmpdir}/delta.tar.gz"

tar -xzf "${tmpdir}/delta.tar.gz" -C "${tmpdir}"

mkdir -p "${INSTALL_DIR}"
mv "${tmpdir}/${ARCHIVE}/delta" "${INSTALL_DIR}/delta"

echo "Installed delta to ${INSTALL_DIR}/delta"

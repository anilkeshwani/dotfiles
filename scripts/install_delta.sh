#!/usr/bin/env bash

# Install delta (https://github.com/dandavison/delta) for Linux.
# Supports x86_64 and aarch64. The binary is placed in ~/.local/bin.

set -euo pipefail

DELTA_VERSION="0.19.2"
INSTALL_DIR="${HOME}/.local/bin"

if [ "$(uname -s)" != "Linux" ]; then
    echo "ERROR: install_delta.sh supports Linux only." >&2
    exit 1
fi

# Idempotency: skip if the desired version is already installed
if command -v delta >/dev/null 2>&1 &&
    [ "$(delta --version 2>/dev/null)" = "delta ${DELTA_VERSION}" ]; then
    echo "delta ${DELTA_VERSION} already installed, skipping."
    exit 0
fi

# Detect architecture
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64)
        ARCH_TRIPLE="x86_64-unknown-linux-musl"
        ARCHIVE_SHA256="f1ea01ca7728ce3462debc359f39dfc7cbbc1a63224b71fefabf92042864aa1b"
        ;;
    aarch64)
        ARCH_TRIPLE="aarch64-unknown-linux-gnu"
        ARCHIVE_SHA256="0bfce159a5cddd5feb3d6db4a616d883ff51253ce08ac7ec11cb1d208cfaab9e"
        ;;
    *)
        echo "ERROR: install_delta.sh does not support architecture: ${ARCH}" >&2
        exit 1
        ;;
esac

ARCHIVE="delta-${DELTA_VERSION}-${ARCH_TRIPLE}"
TARBALL_URL="https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/${ARCHIVE}.tar.gz"

tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT  # clean up on exit, error or interrupt

echo "Downloading delta ${DELTA_VERSION} (${ARCH}) ..."
wget -q "${TARBALL_URL}" -O "${tmpdir}/delta.tar.gz"

echo "${ARCHIVE_SHA256}  ${tmpdir}/delta.tar.gz" | sha256sum --check --status

tar -xzf "${tmpdir}/delta.tar.gz" -C "${tmpdir}"

install -Dm755 "${tmpdir}/${ARCHIVE}/delta" "${INSTALL_DIR}/delta"

echo "Installed delta to ${INSTALL_DIR}/delta"

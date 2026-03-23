#!/usr/bin/env bash

# Install Miniconda and create a clean 'main' environment.
# Supports x86_64 and aarch64. Installs to ${HAFH:-${HOME}}/miniconda3.

# Gist: https://gist.github.com/anilkeshwani/60567eaa5fb8c36398c52022afbde22e

set -euo pipefail

INSTALL_DIR="${HAFH:-${HOME}}/miniconda3"

# Detect architecture
ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|aarch64) ;;
    *)
        echo "ERROR: install_conda.sh does not support architecture: ${ARCH}" >&2
        exit 1
        ;;
esac

INSTALLER_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-${ARCH}.sh"

tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT  # clean up temp dir on exit, error, or interrupt

echo "Installing Miniconda (${ARCH}) to ${INSTALL_DIR} ..."

wget -q "${INSTALLER_URL}" -O "${tmpdir}/miniconda.sh"
bash "${tmpdir}/miniconda.sh" -b -u -p "${INSTALL_DIR}"

"${INSTALL_DIR}/bin/conda" init bash
export PATH="${INSTALL_DIR}/bin:${PATH}"

echo "Creating 'main' environment (clone of base) ..."
conda create --name main --clone base --copy -y

echo "Done. Run 'exec bash' or open a new shell to activate conda."

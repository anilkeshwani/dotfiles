#!/usr/bin/env bash

# Install Miniconda and create a clean 'main' environment.
# Installs to ${HAFH:-${HOME}}/miniconda3.

# Gist: https://gist.github.com/anilkeshwani/60567eaa5fb8c36398c52022afbde22e

set -euo pipefail

INSTALL_DIR="${HAFH:-${HOME}}/miniconda3"

echo "Installing Miniconda to ${INSTALL_DIR} ..."

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -u -p "${INSTALL_DIR}"
rm -f /tmp/miniconda.sh

"${INSTALL_DIR}/bin/conda" init bash
export PATH="${INSTALL_DIR}/bin:${PATH}"

echo "Creating 'main' environment (clone of base) ..."
conda create --name main --clone base --copy -y

echo "Done. Run 'exec bash' or open a new shell to activate conda."

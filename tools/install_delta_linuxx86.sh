#!/usr/bin/env bash

set -euo pipefail

DELTA_V18_2_TARBALL='https://github.com/dandavison/delta/releases/download/0.19.1/delta-0.19.1-x86_64-unknown-linux-gnu.tar.gz'
OUTPUT_FILE="./$(basename ${DELTA_V18_2_TARBALL})"
UNZIPPED_DIR="./$(basename -s .tar.gz ${DELTA_V18_2_TARBALL})"
INSTALL_DIR="${HOME}/.local/bin/"

if [ ! -d "${INSTALL_DIR}" ]; then
    mkdir -p "${INSTALL_DIR}"
    echo "Created user binaries directory at: ${INSTALL_DIR}"
fi

wget ${DELTA_V18_2_TARBALL} --output-document="${OUTPUT_FILE}"
tar -xvzf "${OUTPUT_FILE}"
mv "${UNZIPPED_DIR}/delta" "${INSTALL_DIR}/delta"

echo "Placed delta binary in ${INSTALL_DIR}"
rm "${OUTPUT_FILE}"
rm -r "${UNZIPPED_DIR}"
echo "Cleaned up files. Removed ${OUTPUT_FILE}"

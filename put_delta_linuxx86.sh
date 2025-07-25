#!/usr/bin/env bash

set -euo pipefail

DELTA_V18_2_TARBALL='https://github.com/dandavison/delta/releases/download/0.18.2/delta-0.18.2-x86_64-unknown-linux-gnu.tar.gz'
OUTPUT_FILE="./$(basename ${DELTA_V18_2_TARBALL})"
UNZIPPED_DIR="./$(basename -s .tar.gz ${DELTA_V18_2_TARBALL})"
BIN_DIR="${HOME}/.local/bin/"

if [ ! -d "${BIN_DIR}" ]; then
    mkdir -p "${BIN_DIR}"
    echo "Created user binaries directory at: ${BIN_DIR}"
fi

wget ${DELTA_V18_2_TARBALL} --output-document="${OUTPUT_FILE}"
tar -xvzf "${OUTPUT_FILE}"
mv "${UNZIPPED_DIR}/delta" "${BIN_DIR}/delta"

echo "Placed delta binary in ${BIN_DIR}"
rm "${OUTPUT_FILE}"
rm -r "${UNZIPPED_DIR}"
echo "Cleaned up files. Removed ${OUTPUT_FILE}"

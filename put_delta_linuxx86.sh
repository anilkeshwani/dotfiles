#!/usr/bin/env bash

set -euo pipefail

DELTA_V18_2_TARBALL='https://github.com/dandavison/delta/releases/download/0.18.2/delta-0.18.2-x86_64-unknown-linux-gnu.tar.gz'
OUTPUT_FILE="./$(basename ${DELTA_V18_2_TARBALL})"
UNZIPPED_DIR="./$(basename -s .tar.gz ${DELTA_V18_2_TARBALL})"
BIN_DIR='/usr/local/bin/'

wget ${DELTA_V18_2_TARBALL} --output-document="${OUTPUT_FILE}"
tar -xvzf "${OUTPUT_FILE}"
mv "${UNZIPPED_DIR}/delta" "${BIN_DIR}/delta"

echo "Placed delta binary in ${BIN_DIR}"
rm -r "${OUTPUT_FILE}"
echo "Cleaned up files. Removed ${OUTPUT_FILE}"

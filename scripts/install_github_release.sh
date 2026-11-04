#!/usr/bin/env bash

# Install a prebuilt binary from a GitHub release into ~/.local/bin.
#
# Usage: install_github_release.sh OWNER/REPO BINARY [TAG]
#   TAG defaults to "latest". Pass an exact release tag (e.g. 0.19.2) to pin the version.
#
# Picks the .tar.gz asset for this OS and CPU (preferring a static musl build
# on Linux) and verifies it against the sha256 digest GitHub publishes for the
# asset. Skips the download when ~/.local/bin/BINARY already reports that version.
# Set GITHUB_TOKEN to lift the unauthenticated API rate limit (60/hour).

set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "Usage: $(basename "$0") OWNER/REPO BINARY [TAG]" >&2
    exit 2
fi

REPO="$1"
BINARY="$2"
TAG="${3:-latest}"
INSTALL_DIR="${HOME}/.local/bin"

for dep in curl jq tar; do
    command -v "${dep}" >/dev/null 2>&1 || { echo "ERROR: ${dep} is required" >&2; exit 1; }
done

case "$(uname -m)" in
    x86_64 | amd64) ARCH="x86_64" ;;
    aarch64 | arm64) ARCH="aarch64" ;;
    *) echo "ERROR: unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

case "$(uname -s)" in
    Linux) TARGETS=("${ARCH}-unknown-linux-musl" "${ARCH}-unknown-linux-gnu") ;;
    Darwin) TARGETS=("${ARCH}-apple-darwin") ;;
    *) echo "ERROR: unsupported OS: $(uname -s)" >&2; exit 1 ;;
esac

github_api() {
    local auth=()
    [ -n "${GITHUB_TOKEN:-}" ] && auth=(-H "Authorization: Bearer ${GITHUB_TOKEN}")
    # ${auth[@]+...} because bash 3.2 (macOS) treats an empty array as unbound under set -u
    curl -fsSL ${auth[@]+"${auth[@]}"} -H "Accept: application/vnd.github+json" "https://api.github.com/repos/${REPO}/$1"
}

if [ "${TAG}" = "latest" ]; then
    endpoint="releases/latest"
else
    endpoint="releases/tags/${TAG}"
fi
release="$(github_api "${endpoint}")" || {
    echo "ERROR: could not fetch ${REPO} release ${TAG} from the GitHub API" >&2
    exit 1
}
TAG="$(jq -r .tag_name <<<"${release}")"
VERSION="${TAG#v}"

# Check our own copy, not whatever else is first on PATH. `--version` prints "NAME X.Y.Z"
installed="$("${INSTALL_DIR}/${BINARY}" --version 2>/dev/null | awk '{print $NF; exit}' || true)"
if [ "${installed}" = "${VERSION}" ]; then
    echo "${BINARY} ${VERSION} already installed, skipping."
    exit 0
fi

asset=""
for target in "${TARGETS[@]}"; do
    asset="$(jq -c --arg t "${target}" \
        'first(.assets[] | select(.name | contains($t) and endswith(".tar.gz"))) // empty' <<<"${release}")"
    [ -n "${asset}" ] && break
done
if [ -z "${asset}" ]; then
    echo "ERROR: ${REPO} ${TAG} has no .tar.gz asset for ${TARGETS[*]}" >&2
    exit 1
fi

name="$(jq -r .name <<<"${asset}")"
url="$(jq -r .browser_download_url <<<"${asset}")"
digest="$(jq -r '.digest // empty' <<<"${asset}")"
if [[ "${digest}" != sha256:* ]]; then
    echo "ERROR: GitHub publishes no sha256 digest for ${name}; refusing to install unverified" >&2
    exit 1
fi

# Explicit template: macOS mktemp -d ignores TMPDIR otherwise
tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/install_github_release.XXXXXX")"
trap 'rm -rf "${tmpdir}"' EXIT

echo "Downloading ${name} ..."
curl -fsSL "${url}" -o "${tmpdir}/${name}"

if command -v sha256sum >/dev/null 2>&1; then
    actual="$(sha256sum "${tmpdir}/${name}" | cut -d' ' -f1)"
else
    actual="$(shasum -a 256 "${tmpdir}/${name}" | cut -d' ' -f1)"
fi
if [ "${actual}" != "${digest#sha256:}" ]; then
    echo "ERROR: sha256 mismatch for ${name}: expected ${digest#sha256:}, got ${actual}" >&2
    exit 1
fi

tar -xzf "${tmpdir}/${name}" -C "${tmpdir}"
binary_path="$(find "${tmpdir}" -type f -name "${BINARY}" -perm -u+x -print -quit)"
if [ -z "${binary_path}" ]; then
    echo "ERROR: no executable named ${BINARY} inside ${name}" >&2
    exit 1
fi

mkdir -p "${INSTALL_DIR}"
install -m 755 "${binary_path}" "${INSTALL_DIR}/${BINARY}"
echo "Installed ${BINARY} ${VERSION} to ${INSTALL_DIR}/${BINARY}"

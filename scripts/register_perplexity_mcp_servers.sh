#!/usr/bin/env bash

# Register the Perplexity Computer MCP server with the main Claude Code seat.
# Run on each host: bash scripts/register_perplexity_mcp_servers.sh
#
# User-scoped MCP servers live in ~/.claude.json, which install.py never links,
# so each host needs this once. Only the main seat (bare `claude`) gets it: the
# extra seat runs without integrations. A registered server is left alone, so
# reruns are safe. Sign in afterwards with /mcp inside `claude`.
#
# Computer spends Perplexity account credits, which the Max plan includes
# monthly. Perplexity's search API server (api.perplexity.ai/mcp) is left out
# because it bills API credits that the subscription does not include.

set -euo pipefail

NAME="perplexity-computer"
URL="https://www.perplexity.ai/rest/computer/mcp"

if ! command -v claude >/dev/null 2>&1; then
    echo "claude not found on PATH" >&2
    exit 1
fi

# Unsetting CLAUDE_CONFIG_DIR selects the main seat even when this runs from a
# claude-extra session.
if env -u CLAUDE_CONFIG_DIR claude mcp get "$NAME" >/dev/null 2>&1; then
    echo "$NAME: already registered"
else
    env -u CLAUDE_CONFIG_DIR claude mcp add --scope user --transport http "$NAME" "$URL"
fi

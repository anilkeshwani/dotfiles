#!/usr/bin/env bash

# Register Perplexity's remote MCP servers with the main Claude Code seat.
# Run on each host: bash scripts/register_perplexity_mcp_servers.sh
#
# User-scoped MCP servers live in ~/.claude.json, which install.py never links,
# so each host needs this once. Only the main seat (bare `claude`) gets them:
# the extra seat runs without integrations. Registered servers are left alone,
# so reruns are safe. Sign in afterwards with /mcp inside `claude`.
#
#   perplexity           search, ask, research and reason; bills the Perplexity
#                        API organization chosen at sign-in
#   perplexity-computer  the Perplexity Computer agent; spends account credits
#   perplexity-docs      Perplexity's API documentation; free, no sign-in

set -euo pipefail

SERVERS=(
    "perplexity https://api.perplexity.ai/mcp"
    "perplexity-computer https://www.perplexity.ai/rest/computer/mcp"
    "perplexity-docs https://docs.perplexity.ai/mcp"
)

if ! command -v claude >/dev/null 2>&1; then
    echo "claude not found on PATH" >&2
    exit 1
fi

# Unsetting CLAUDE_CONFIG_DIR selects the main seat even when this runs from a
# claude-extra session.
main_claude() { env -u CLAUDE_CONFIG_DIR claude "$@"; }

for entry in "${SERVERS[@]}"; do
    read -r name url <<<"$entry"
    if main_claude mcp get "$name" >/dev/null 2>&1; then
        echo "$name: already registered"
    else
        main_claude mcp add --scope user --transport http "$name" "$url"
    fi
done

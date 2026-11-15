#!/usr/bin/env bash

# Register Perplexity's official remote MCP servers with Claude Code and Codex.
# Run: bash scripts/register_perplexity_mcp_servers.sh
#
# Claude Code keeps user-scoped MCP servers in .claude.json, which install.py
# never links, so each account gets its own registration: the work login (bare
# `claude`, CLAUDE_CONFIG_DIR unset, state in ~/.claude.json) and every extra
# CLAUDE_CONFIG_DIR_* dir that has been logged into. Dirs with no .claude.json
# yet are skipped; rerun after the first login there. Codex keeps its servers in
# ~/.codex/config.toml, also untracked. Registered servers are left alone, so
# reruns are safe.
#
# All three servers sign in with OAuth on first use (Claude Code: /mcp; Codex:
# codex mcp login <name>). Billing differs:
#   perplexity-computer  Perplexity Computer agent; spends the account's
#                        Computer credits (Max includes a monthly allowance)
#   perplexity           Search, ask, research and reason tools; bills the
#                        Perplexity API organization chosen at sign-in
#   perplexity-docs      Perplexity's API documentation; free, no sign-in

set -euo pipefail

SERVERS=(
    "perplexity-computer https://www.perplexity.ai/rest/computer/mcp"
    "perplexity https://api.perplexity.ai/mcp"
    "perplexity-docs https://docs.perplexity.ai/mcp"
)

# Empty entry = the work login, which runs with CLAUDE_CONFIG_DIR unset.
CLAUDE_DIRS=(
    ""
    "${CLAUDE_CONFIG_DIR_PERSONAL:-$HOME/.claude-personal}"
    "${CLAUDE_CONFIG_DIR_WORK_EXTRA:-$HOME/.claude-work-extra}"
)

claude_in() {
    local dir="$1"
    shift
    if [ -z "$dir" ]; then
        env -u CLAUDE_CONFIG_DIR claude "$@"
    else
        CLAUDE_CONFIG_DIR="$dir" claude "$@"
    fi
}

if command -v claude >/dev/null 2>&1; then
    for dir in "${CLAUDE_DIRS[@]}"; do
        label="${dir:-work (~/.claude.json)}"
        if [ -n "$dir" ] && [ ! -f "$dir/.claude.json" ]; then
            echo "claude: skipping $dir (not logged in yet)"
            continue
        fi
        for entry in "${SERVERS[@]}"; do
            read -r name url <<<"$entry"
            if claude_in "$dir" mcp get "$name" >/dev/null 2>&1; then
                echo "claude ($label): $name already registered"
            else
                claude_in "$dir" mcp add --scope user --transport http "$name" "$url"
            fi
        done
    done
else
    echo "claude not found, skipping Claude Code"
fi

if command -v codex >/dev/null 2>&1; then
    for entry in "${SERVERS[@]}"; do
        read -r name url <<<"$entry"
        if codex mcp get "$name" >/dev/null 2>&1; then
            echo "codex: $name already registered"
        else
            # codex mcp add writes the config entry, then starts an OAuth login
            # that waits for a browser callback on 127.0.0.1. Cut the wait short
            # so the script does not hang on a headless host; log in afterwards.
            timeout 15 codex mcp add "$name" --url "$url" </dev/null >/dev/null 2>&1 || true
            if codex mcp get "$name" >/dev/null 2>&1; then
                echo "codex: added $name (log in with: codex mcp login $name)"
            else
                echo "codex: failed to add $name" >&2
                exit 1
            fi
        fi
    done
else
    echo "codex not found, skipping Codex"
fi

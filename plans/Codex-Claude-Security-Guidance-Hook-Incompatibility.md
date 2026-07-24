# Codex–Claude Security Guidance Hook Incompatibility

## Summary

Codex repeatedly reports failures such as:

```text
PostToolUse hook (failed)
error: hook returned invalid post-tool-use JSON output

Stop hook (failed)
error: hook returned invalid stop hook JSON output
```

These errors come from `security-guidance@claude-plugins-official`, an Anthropic plugin originally installed for Claude Code and subsequently imported into Codex. It is not a default Codex plugin and is distinct from OpenAI's Codex Security plugin.

Git commands and commits still complete successfully. The failing component is the supplementary security review that runs after tool calls and when the agent stops.

## What the Plugin Does

The plugin is published in Anthropic's `claude-plugins-official` marketplace. It provides:

- Pattern-based security warnings after file edits.
- Security reviews after commits and pushes.
- A final LLM-based review of the session's Git diff.
- Continuation messages that ask Claude Code to address findings before stopping.

Its installed manifest describes it as:

> Security review for Claude-generated code. Pattern-based warnings on edits, LLM-powered diff review on Stop, and an agentic commit reviewer.

## Local Provenance

The local configuration establishes the following history:

| Date | Evidence |
| --- | --- |
| 2026-03-18 | `security-guidance@claude-plugins-official` was already enabled in the tracked Claude Code settings. |
| 2026-04-08 | Claude Code's plugin registry records the plugin as installed at user scope. |
| 2026-06-12 | Claude Code's installed copy was last updated. |
| 2026-07-23 | Codex executed the imported plugin hooks and began reporting invalid hook output. |

Relevant files:

- Claude Code setting: `~/.claude/settings.json`
- Claude Code installation registry: `~/.claude/plugins/installed_plugins.json`
- Codex configuration: `~/.codex/config.toml`
- Codex plugin cache: `~/.codex/plugins/cache/claude-plugins-official/security-guidance/`

The Codex configuration contains the Anthropic marketplace, explicitly enables the plugin, and stores trust records for its hooks. This matches ChatGPT's supported import flow, which can copy settings, plugins, marketplaces, and hooks from Claude Code into Codex.

The precise user action that initiated the import is not recoverable from the inspected local records. It may have been an explicit import, an onboarding selection, or a desktop-app migration. The provenance is nevertheless clear: the plugin came from the existing Claude Code setup rather than from a default Codex installation or an older Codex release.

## Root Cause

Codex and Claude Code share a broadly similar hook structure, but their hook protocols are not identical.

The plugin uses Claude Code-specific handler fields including:

- `if`
- `asyncRewake`
- `rewakeMessage`
- `rewakeSummary`

It also emits Claude Code-specific output fields such as:

- `metrics`
- `rewakeSummary`

Codex discovers and launches the hooks because it recognizes the surrounding plugin and hook structure. It cannot fully interpret the Claude-specific conditions and output schema.

### Why Five PostToolUse Errors Appear

The plugin declares five conditional handlers under its `PostToolUse` Bash matcher:

1. `git commit`
2. `git push`
3. `gt create`
4. `gt modify`
5. `gt submit`

For an unrelated command such as `git status`, Codex launches all five handlers instead of applying the Claude-specific `if` conditions as intended. The plugin script sees that the command is irrelevant and exits successfully without producing JSON. The affected Codex build then reports each empty response as invalid, producing five identical errors.

### Why the Stop Error Appears

At the end of the turn, the plugin emits syntactically valid JSON containing fields such as `metrics`. Those fields are not part of the supported Codex Stop-hook response schema. Codex therefore reports “invalid stop hook JSON output.”

The message is about schema validation, not necessarily malformed JSON syntax.

## Impact

- Git commands, edits, and commits are not rolled back.
- The repeated messages add noise to the TUI.
- The imported security review is not operating reliably in Codex.
- Other capabilities from the Anthropic marketplace may still work; the incompatibility is specifically demonstrated for this plugin's hooks.

## Recommended Resolution

Disable or uninstall `security-guidance@claude-plugins-official` in Codex while leaving the Claude Code installation untouched.

Preferred approaches:

1. Use `/hooks` in the Codex TUI and disable every hook sourced from `security-guidance@claude-plugins-official`.
2. Alternatively, disable or remove the plugin through Codex's plugin management UI.

Avoid setting `[features] hooks = false` unless all Codex hooks should be disabled globally.

Do not patch files inside `~/.codex/plugins/cache/`. Cached marketplace content can be replaced on refresh, and maintaining a local compatibility fork is unnecessary unless the security review is specifically required in Codex.

## Upstream Follow-Up

This is an import-compatibility issue worth reporting because Codex accepts and enables the imported plugin even though it cannot faithfully execute the plugin's hook protocol.

A useful report should include:

- Codex version: `codex-cli 0.145.0-alpha.27`
- Plugin: `security-guidance@claude-plugins-official`
- Plugin version: `2.0.6`
- Five `PostToolUse` failures after an ordinary Bash command.
- One Stop-hook failure at the end of the turn.
- The plugin's use of handler-level `if` and async-rewake fields.
- The Stop response containing unsupported metrics fields.

## References

- [Import from another agent](https://learn.chatgpt.com/docs/import)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Anthropic security-guidance plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance)

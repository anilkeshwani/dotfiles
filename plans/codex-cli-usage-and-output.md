# Codex CLI usage and output

## Check usage

In an interactive Codex CLI session:

- `/usage` shows account-level daily, weekly, and cumulative usage.
- `/status` shows the current session's token/context usage and applicable rate limits.
- `/statusline` can add persistent token or rate-limit fields to the footer.
- `codex login status` shows whether Codex is using a ChatGPT subscription or an API key.

API-key usage is billed separately from a ChatGPT allowance and is available in the [OpenAI Platform usage dashboard](https://platform.openai.com/usage).

## Reduce output verbosity

There is no single supported setting to hide script-execution lines or auto-review decisions. These options reduce related output:

```toml
# ~/.codex/config.toml
model_verbosity = "low"       # Shorter model-written responses
hide_agent_reasoning = true  # Hide reasoning-summary events
animations = false           # Disable spinner/status animations
```

Notes:

- `model_verbosity` does not hide command or script execution records.
- `/raw` changes transcript formatting, not how much is displayed.
- `RUST_LOG=error|warn|info|debug|trace` controls diagnostic logs, not normal TUI tool events.
- Auto-review rationale, especially denials, cannot currently be shortened or hidden independently.
- `approvals_reviewer = "user"` replaces automatic review with manual approval; it changes the security workflow rather than just reducing output.
- `[auto_review].policy` changes the reviewer's decision policy, not the amount displayed.

References: [CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [configuration](https://learn.chatgpt.com/docs/config-file/config-reference), and [auto-review](https://learn.chatgpt.com/docs/sandboxing/auto-review).

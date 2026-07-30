#!/bin/bash
# Claude Code status line, two rows:
#   row 1  where you are  — user@host, cwd, git branch, venv, repo, model, effort, style
#   row 2  what it cost   — context tokens, $, API time, wall time, line churn, rate limits
#
# Row 1's user@host/cwd/branch/venv mirror the shell prompt in .zshrc / .bashrc.
# The prompt's second line is dropped: a status line has no command entry, and
# Claude Code supplies no last-exit-status field.

input=$(cat)

# One jq call rather than one per field; this script reruns on every UI update.
# Fields are \x1f-separated, not tab: tab is IFS whitespace, so runs of empty
# fields would collapse into one delimiter and shift every later value left.
IFS=$'\x1f' read -r cwd model effort style thinking fast \
    tokens ctx_size ctx_pct cost dur_ms api_ms added removed rl5 rl7 repo \
    < <(printf '%s' "$input" | jq -r '[
        .workspace.current_dir // "",
        .model.display_name // "",
        .effort.level // "",
        .output_style.name // "",
        (.thinking.enabled // false | tostring),
        (.fast_mode // false | tostring),
        (.context_window.total_input_tokens // 0 | tostring),
        (.context_window.context_window_size // 0 | tostring),
        (.context_window.used_percentage // 0 | tostring),
        (.cost.total_cost_usd // 0 | tostring),
        (.cost.total_duration_ms // 0 | tostring),
        (.cost.total_api_duration_ms // 0 | tostring),
        (.cost.total_lines_added // 0 | tostring),
        (.cost.total_lines_removed // 0 | tostring),
        (.rate_limits.five_hour.used_percentage // 0 | tostring),
        (.rate_limits.seven_day.used_percentage // 0 | tostring),
        (if .workspace.repo then
            ((.workspace.repo.owner // "") + "/" + (.workspace.repo.name // ""))
         else "" end)
    ] | join("\u001f")')

GRN=$'\033[32m'; BLU=$'\033[34m'; MAG=$'\033[35m'; YEL=$'\033[33m'
CYA=$'\033[36m'; RED=$'\033[31m'; DIM=$'\033[90m'; RST=$'\033[0m'
SEP="${DIM} · ${RST}"

# 72568 -> 73k, 1000000 -> 1M
fmt_count() {
    if [ "$1" -ge 1000000 ]; then printf '%dM' $((($1 + 500000) / 1000000))
    elif [ "$1" -ge 1000 ]; then printf '%dk' $((($1 + 500) / 1000))
    else printf '%d' "$1"; fi
}

# 355482 -> 6m, 58478530 -> 16h
fmt_ms() {
    local s=$(($1 / 1000))
    if [ "$s" -ge 3600 ]; then printf '%dh' $(((s + 1800) / 3600))
    elif [ "$s" -ge 60 ]; then printf '%dm' $(((s + 30) / 60))
    else printf '%ds' "$s"; fi
}

# green under 50%, yellow under 80%, red above
pct_color() {
    if [ "${1%%.*}" -ge 80 ]; then printf '%s' "$RED"
    elif [ "${1%%.*}" -ge 50 ]; then printf '%s' "$YEL"
    else printf '%s' "$GRN"; fi
}

# \~ is required: an unescaped ~ in the replacement is tilde-expanded back to $HOME
display_dir="${cwd/#$HOME/\~}"

# One git call, not two: this fails outside a work tree and prints nothing on
# detached HEAD, which covers both cases the old rev-parse guard handled.
# The -n guard matters: git -C "" silently falls back to the process's own
# directory and would report a branch belonging to the wrong repo.
[ -n "$cwd" ] && branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)

# "Opus 5 (1M context)" -> "Opus 5 1M"; other names pass through unchanged
[[ $model =~ ^(.*)\ \((.*)\ context\)$ ]] && model="${BASH_REMATCH[1]} ${BASH_REMATCH[2]}"

row1="${GRN}$(whoami)@$(hostname -s)${RST} ${BLU}${display_dir}${RST}"
[ -n "$branch" ] && row1+="${MAG}  ${branch}${RST}"
[ -n "$VIRTUAL_ENV" ] && row1+="${YEL} ($(basename "$VIRTUAL_ENV"))${RST}"
[ -n "$repo" ] && row1+="${SEP}${DIM}${repo}${RST}"
[ -n "$model" ] && row1+="${SEP}${CYA}${model}${RST}"
[ -n "$effort" ] && row1+="${SEP}${DIM}${effort}${RST}"
[ -n "$style" ] && row1+="${SEP}${DIM}${style}${RST}"
[ "$thinking" = "true" ] && row1+="${SEP}${DIM}✻${RST}"
[ "$fast" = "true" ] && row1+="${SEP}${YEL}⚡${RST}"

row2="$(pct_color "$ctx_pct")$(fmt_count "$tokens")/$(fmt_count "$ctx_size")${RST}"
row2+="${SEP}${GRN}$(printf '$%.2f' "$cost")${RST}"
row2+="${SEP}${DIM}$(fmt_ms "$api_ms") api${RST}"
row2+="${SEP}${DIM}$(fmt_ms "$dur_ms")${RST}"
row2+="${SEP}${GRN}+${added}${RST}/${RED}-${removed}${RST}"
row2+="${SEP}$(pct_color "$rl5")5h ${rl5}%${RST}"
row2+="${SEP}$(pct_color "$rl7")7d ${rl7}%${RST}"

printf '%s\n%s\n' "$row1" "$row2"

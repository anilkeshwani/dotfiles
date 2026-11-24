#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
"""Pre-commit guard: block commits whose staged changes look like ~/.secrets content.

Run from a git pre-commit hook (home/.config/git/hooks/pre-commit). It reports file and
line numbers and the reason, never the matched value. A line that contains the pragma
`secrets-guard: allow` is skipped. See docs/secrets-sync.md.
"""

from __future__ import annotations

import math
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from secrets_sync import ALLOW_PRAGMA, SecretsSyncError, parse_secrets, read_target  # noqa: E402

BLOCKED_PATH_RE = re.compile(r"(^|/)(\.secrets(\..+)?|[^/]*\.secrets)$")
SECRET_NAME_RE = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH|LICENSE)", re.I)
ASSIGN_RE = re.compile(
    r"""(?P<name>[A-Za-z_][A-Za-z0-9_.-]*)["']?\s*(?:=|:|:=)\s*"""
    r"""(?P<value>"[^"\s]*"|'[^'\s]*'|[A-Za-z0-9+/=_.~:@-]+)"""
)
TOKEN_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key id"),
    (re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{40,}"), "a GitHub token"),
    (re.compile(r"\bsk-(ant-|proj-)?[A-Za-z0-9_-]{20,}"), "an API secret key (sk-...)"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "a Slack token"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "a Google API key"),
    (re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"), "a Hugging Face token"),
    (re.compile(r"\blin_api_[A-Za-z0-9]{30,}\b"), "a Linear API key"),
]
PLACEHOLDER_HINTS = ("xxx", "changeme", "your", "example", "placeholder", "dummy", "redacted",
                     "<", "...", "***", "todo", "fake", "test", "sample", "replace")
MIN_VALUE_LENGTH = 8
ENTROPY_MIN_LENGTH = 20
ENTROPY_THRESHOLD = 3.5  # bits per character; hex tops out at 4.0, random base64 near 6


def shannon_entropy(text: str) -> float:
    counts = Counter(text)
    return -sum(c / len(text) * math.log2(c / len(text)) for c in counts.values())


def is_placeholder(value: str) -> bool:
    v = value.strip("'\"")
    low = v.lower()
    return (
        len(v) < MIN_VALUE_LENGTH
        or v.startswith("$")
        or len(set(v)) <= 2
        or any(hint in low for hint in PLACEHOLDER_HINTS)
    )


def local_secrets() -> tuple[set[str], dict[str, str]]:
    """Names and literal values from ~/.secrets, read without executing it. Values stay in
    this process and are only used for substring checks."""
    try:
        existing = read_target(Path.home() / ".secrets")
    except (SecretsSyncError, OSError):
        return set(), {}
    if existing is None:
        return set(), {}
    try:
        parsed = parse_secrets(existing.data.decode(errors="replace"))
    except SecretsSyncError:
        return set(), {}
    every = parsed.assignments + parsed.local_assignments
    names = {a.name for a in every}
    values = {a.name: a.value for a in every if a.value and len(a.value) >= MIN_VALUE_LENGTH}
    return names, values


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True,
                          stdin=subprocess.DEVNULL, errors="replace").stdout


def staged_added_lines() -> list[tuple[str, int, str]]:
    diff = git("diff", "--cached", "-U0", "--no-color", "--no-ext-diff", "--diff-filter=ACMRT")
    found, path, lineno = [], None, 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            lineno = int(match.group(1)) if match else 0
        elif line.startswith("+") and path is not None:
            found.append((path, lineno, line[1:]))
            lineno += 1
    return found


def check_line(line: str, names: set[str], values: dict[str, str]) -> str | None:
    if ALLOW_PRAGMA in line:
        return None
    for name, value in values.items():
        if value in line:
            return f"contains the value of {name} from ~/.secrets"
    for pattern, what in TOKEN_PATTERNS:
        if pattern.search(line):
            return f"looks like {what}"
    for match in ASSIGN_RE.finditer(line):
        name, value = match.group("name"), match.group("value")
        if is_placeholder(value) or line[match.end():match.end() + 1] == "(":
            continue  # a placeholder, or a function call such as secrets.token_hex(16)
        if name in names:
            return f"assigns a value to {name}, a variable in ~/.secrets"
        bare = value.strip("'\"")
        if (SECRET_NAME_RE.search(name) and len(bare) >= ENTROPY_MIN_LENGTH
                and shannon_entropy(bare) >= ENTROPY_THRESHOLD):
            return f"assigns a high-entropy value to {name}"
    return None


def main() -> int:
    findings = []
    staged = git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT").split("\0")
    for path in filter(None, staged):
        if BLOCKED_PATH_RE.search(path):
            findings.append(f"{path}: a .secrets file must never be committed")
    names, values = local_secrets()
    for path, lineno, line in staged_added_lines():
        reason = check_line(line, names, values)
        if reason:
            findings.append(f"{path}:{lineno}: {reason}")
    if not findings:
        return 0
    print("secrets guard: commit blocked.", file=sys.stderr)
    for finding in findings:
        print(f"  {finding}", file=sys.stderr)
    print(f"Unstage the secret. For a false positive, add the comment `{ALLOW_PRAGMA}` to that line.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    os.umask(0o077)
    sys.exit(main())

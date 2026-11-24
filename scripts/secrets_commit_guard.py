#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
"""Pre-commit guard: block commits whose staged content looks like ~/.secrets content.

Run by the pre-commit hook home/.config/git/hooks/pre-commit with the repository root as
its argument. It reads every staged blob through `git diff --cached --raw -z` and
`git cat-file`, so no diff header or quoted path is ever parsed, and anything it cannot
read blocks the commit. It reports file and line and the reason, never the matched
value. A line that contains the pragma `secrets-guard: allow` is skipped by every rule.
See docs/secrets-sync.md.
"""

from __future__ import annotations

import math
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from secrets_sync import ALLOW_PRAGMA, SecretsSyncError, parse_secrets  # noqa: E402

BLOCKED_PATH_RE = re.compile(r"(^|/)(\.secrets(\..+)?|[^/]*\.secrets)$")
SECRET_NAME_RE = re.compile(
    r"(?:^|_)(API_?KEY|KEYS?|TOKEN|SECRET|PASSWORD|PASSWD|PWD|CREDENTIALS?|AUTH|LICENSE)(?:_|$)", re.I
)
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


class GuardError(Exception):
    """A condition under which the guard cannot vouch for the commit, so it blocks it."""


def is_secret_name(name: str) -> bool:
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).replace("-", "_").replace(".", "_")
    return bool(SECRET_NAME_RE.search(snake))


def looks_random(value: str) -> bool:
    return (len(value) >= ENTROPY_MIN_LENGTH - 4 and "/" not in value
            and shannon_entropy(value) >= ENTROPY_THRESHOLD)


def local_secrets() -> tuple[set[str], dict[str, str]]:
    """Names, and the values worth matching, from ~/.secrets, read without executing it.
    Values stay in this process and are only used for substring checks. A ~/.secrets that
    exists but cannot be read raises GuardError, since the value check would then be off."""
    path = Path.home() / ".secrets"
    if not os.path.lexists(path):
        return set(), {}
    try:
        text = path.read_bytes().decode(errors="replace")  # follows a symlink: read-only use
        parsed = parse_secrets(text)
    except (OSError, SecretsSyncError) as exc:
        reason = exc.strerror if isinstance(exc, OSError) else str(exc)
        raise GuardError(f"~/.secrets exists but cannot be read ({reason}), so its values cannot be checked")
    every = parsed.assignments + parsed.local_assignments
    names = {a.name for a in every}
    # Match only values that are secrets: a secret-like name or a random-looking value. A
    # URL or project id from ~/.secrets in a doc is not a leak worth a blocked commit.
    values = {
        a.name: a.value for a in every
        if a.value and len(a.value) >= MIN_VALUE_LENGTH and (is_secret_name(a.name) or looks_random(a.value))
    }
    return names, values


def git_bytes(repo: str, *args: str) -> bytes:
    proc = subprocess.run(["git", "-C", repo, "-c", "core.quotePath=false", *args],
                          capture_output=True, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise GuardError(f"`git {args[0]}` failed: {proc.stderr.decode(errors='replace').strip()[:200]}")
    return proc.stdout


@dataclass
class StagedFile:
    path: str  # for display and the path rule only; never passed back to git
    mode: str
    blob: str


def staged_files(repo: str) -> list[StagedFile]:
    """Every added, copied, modified, renamed or retyped path in the index, with the blob id
    of its staged content. The -z raw format separates fields with NUL and never quotes
    paths, so names with spaces, quotes, newlines or non-ASCII characters come through."""
    out = git_bytes(repo, "diff", "--cached", "--raw", "-z", "--no-abbrev", "--find-renames",
                    "--diff-filter=ACMRT", "--no-ext-diff", "--no-textconv")
    tokens = out.split(b"\0")
    files, i = [], 0
    while i < len(tokens):
        header = tokens[i]
        if not header:
            i += 1
            continue
        parts = header.decode("ascii", errors="replace").split(" ")
        if not header.startswith(b":") or len(parts) != 5 or not parts[4]:
            raise GuardError("could not read `git diff --raw` output")
        n_paths = 2 if parts[4][0] in "RC" else 1
        if i + n_paths >= len(tokens):
            raise GuardError("could not read `git diff --raw` output")
        path = tokens[i + n_paths].decode("utf-8", errors="backslashreplace")
        files.append(StagedFile(path=path, mode=parts[1], blob=parts[3]))
        i += 1 + n_paths
    return files


def shown(path: str) -> str:
    return "".join(c if c.isprintable() else repr(c)[1:-1] for c in path)


def check_line(line: str, names: set[str], values: dict[str, str], binary: bool = False) -> str | None:
    if ALLOW_PRAGMA in line:
        return None
    for name, value in values.items():
        if value in line:
            return f"contains the value of {name} from ~/.secrets"
    for pattern, what in TOKEN_PATTERNS:
        if pattern.search(line):
            return f"looks like {what}"
    if binary:
        return None
    for match in ASSIGN_RE.finditer(line):
        name, value = match.group("name"), match.group("value")
        if is_placeholder(value) or line[match.end():match.end() + 1] == "(":
            continue  # a placeholder, or a function call such as secrets.token_hex(16)
        bare = value.strip("'\"")
        if name in names and is_secret_name(name):
            return f"assigns a value to {name}, a variable in ~/.secrets"
        if (is_secret_name(name) and len(bare) >= ENTROPY_MIN_LENGTH
                and shannon_entropy(bare) >= ENTROPY_THRESHOLD):
            return f"assigns a high-entropy value to {name}"
    return None


def scan(repo: str) -> list[str]:
    findings: list[str] = []
    try:
        names, values = local_secrets()
    except GuardError as exc:
        findings.append(str(exc))
        names, values = set(), {}
    for staged in staged_files(repo):
        label = shown(staged.path)
        if BLOCKED_PATH_RE.search(staged.path):
            findings.append(f"{label}: a .secrets file must never be committed")
        if staged.mode == "160000":
            continue  # a submodule commit id, not content
        try:
            data = git_bytes(repo, "cat-file", "blob", staged.blob)
        except GuardError:
            findings.append(f"{label}: cannot read the staged content, so it cannot be checked")
            continue
        binary = b"\0" in data
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")  # never fails: every byte is still scanned
            binary = True
        for lineno, line in enumerate(text.split("\n"), start=1):
            reason = check_line(line, names, values, binary=binary)
            if reason:
                findings.append(f"{label}:{lineno}: {reason}")
    return findings


def main(argv: list[str]) -> int:
    repo = argv[1] if len(argv) > 1 else "."
    try:
        findings = scan(repo)
    except GuardError as exc:
        findings = [str(exc)]
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
    sys.exit(main(sys.argv))

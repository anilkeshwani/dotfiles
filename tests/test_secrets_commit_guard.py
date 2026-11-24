"""Tests for scripts/secrets_commit_guard.py and the pre-commit hook that runs it."""

from __future__ import annotations

import os
import secrets
import shutil
import subprocess
import sys

import pytest

from conftest import REPO_ROOT, SCRIPTS

GUARD = SCRIPTS / "secrets_commit_guard.py"
HOOKS = REPO_ROOT / "home" / ".config" / "git" / "hooks"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    value = "livevalue" + secrets.token_hex(12)
    (home / ".secrets").write_text(f"export KNOWN_SERVICE_KEY='{value}'\nexport SHORT=ab\n")
    (home / ".secrets").chmod(0o600)
    work = tmp_path / "work"
    work.mkdir()
    env = {"HOME": str(home), "PATH": os.environ["PATH"], "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    for var in ("UV_CACHE_DIR", "TMPDIR", "XDG_CACHE_HOME"):
        if var in os.environ:
            env[var] = os.environ[var]
    subprocess.run(["git", "init", "-q", str(work)], check=True, env=env)
    return work, env, value


def stage(repo, name: str, content: str) -> None:
    work, env, _ = repo
    (work / name).parent.mkdir(parents=True, exist_ok=True)
    (work / name).write_text(content)
    subprocess.run(["git", "add", "-f", name], cwd=work, check=True, env=env)


def guard(repo) -> subprocess.CompletedProcess:
    work, env, _ = repo
    return subprocess.run([sys.executable, str(GUARD)], cwd=work, env=env, capture_output=True, text=True)


def test_clean_change_passes(repo):
    stage(repo, "notes.md", "Set KNOWN_SERVICE_KEY in ~/.secrets.\nAPI_KEY=your-key-here\nTOKEN=${TOKEN}\n")
    assert guard(repo).returncode == 0


def test_secrets_file_is_blocked(repo):
    stage(repo, "home/.secrets", "# empty\n")
    result = guard(repo)
    assert result.returncode == 1 and "home/.secrets" in result.stderr


def test_known_value_anywhere_is_blocked_without_printing_it(repo):
    _, _, value = repo
    stage(repo, "config.json", f'{{"anything": "{value}"}}\n')
    result = guard(repo)
    assert result.returncode == 1
    assert "value of KNOWN_SERVICE_KEY" in result.stderr
    assert value not in result.stderr + result.stdout


def test_known_name_with_real_looking_value_is_blocked(repo):
    stage(repo, "env.sh", "export KNOWN_SERVICE_KEY=Zq81mXbNw0pLr\n")
    result = guard(repo)
    assert result.returncode == 1 and "env.sh:1" in result.stderr


def test_high_entropy_assignment_is_blocked(repo):
    token = secrets.token_urlsafe(30)
    stage(repo, "settings.py", f'other = 1\nSERVICE_TOKEN = "{token}"\n')
    result = guard(repo)
    assert result.returncode == 1 and "settings.py:2" in result.stderr
    assert token not in result.stderr


def test_known_token_shapes_are_blocked(repo):
    stage(repo, "a.txt", "key: AKIA" + "ABCDEFGHIJKLMNOP" + "\n")
    assert guard(repo).returncode == 1


def test_hex_hashes_and_code_pass(repo):
    stage(repo, "a.py", 'COMMIT_SHA = "0123456789abcdef0123456789abcdef01234567"\nSECRET_RE = re.compile(r"(KEY|TOKEN)")\n'
                        "api_token = secrets.token_urlsafe_generator(30)\n")
    assert guard(repo).returncode == 0


def test_allow_pragma(repo):
    token = secrets.token_urlsafe(30)
    stage(repo, "fixture.py", f'SERVICE_TOKEN = "{token}"  # secrets-guard: allow\n')
    assert guard(repo).returncode == 0


@pytest.mark.skipif(not shutil.which("uv"), reason="uv not installed")
def test_hook_blocks_git_commit_end_to_end(repo):
    work, env, value = repo
    subprocess.run(["git", "config", "core.hooksPath", str(HOOKS)], cwd=work, check=True, env=env)
    stage(repo, "leak.txt", f"{value}\n")
    result = subprocess.run(["git", "commit", "-qm", "leak"], cwd=work, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "commit blocked" in result.stderr and value not in result.stderr
    log = subprocess.run(["git", "log", "--oneline"], cwd=work, env=env, capture_output=True, text=True)
    assert log.stdout == ""

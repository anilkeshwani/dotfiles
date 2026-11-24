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
    subprocess.run(["git", "add", "-f", "--", name], cwd=work, check=True, env=env)


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


# --- staged content is read per blob, never from diff headers -------------------------


@pytest.mark.parametrize("name", ["with space.txt", 'quo"te\'s.txt', "café.py", "new\nline.txt", "-dash.txt"])
def test_unusual_file_names_are_scanned(repo, name):
    _, _, value = repo
    stage(repo, name, f"{value}\n")
    result = guard(repo)
    assert result.returncode == 1
    assert "value of KNOWN_SERVICE_KEY" in result.stderr and value not in result.stderr


def test_line_starting_with_plus_plus_does_not_hide_the_rest(repo):
    _, _, value = repo
    stage(repo, "notes.txt", f"++ b/decoy\n++ \nkey {value}\n")
    result = guard(repo)
    assert result.returncode == 1 and "notes.txt:3" in result.stderr


def test_binary_files_are_scanned(repo):
    _, _, value = repo
    work, env, _ = repo
    (work / "blob.bin").write_bytes(b"\x00\x01\xff" + value.encode() + b"\x00")
    subprocess.run(["git", "add", "blob.bin"], cwd=work, check=True, env=env)
    assert guard(repo).returncode == 1


def stage_bytes(repo, name: str, data: bytes) -> None:
    work, env, _ = repo
    (work / name).write_bytes(data)
    subprocess.run(["git", "add", "-f", "--", name], cwd=work, check=True, env=env)


@pytest.mark.parametrize("data", [
    "# café\nAPI_KEY = 'Zq81mXbNw0pLrTy5vC2sKd7G'\n".encode("latin-1"),
    b"# one bad byte \xff\nAPI_KEY = 'Zq81mXbNw0pLrTy5vC2sKd7G'\n",
])
def test_non_utf8_text_still_gets_the_assignment_rules(repo, data):
    stage_bytes(repo, "legacy.cfg", data)
    result = guard(repo)
    assert result.returncode == 1 and "legacy.cfg:2" in result.stderr


def test_nul_byte_after_the_first_8000_bytes_is_still_text(repo):
    stage_bytes(repo, "big.cfg", b"x" * 8100 + b"\0\nAPI_KEY = 'Zq81mXbNw0pLrTy5vC2sKd7G'\n")
    assert guard(repo).returncode == 1


def test_binary_file_is_checked_for_values_under_unusual_names(repo, tmp_path):
    value = "opaque/" + secrets.token_hex(6)
    add_to_secrets(tmp_path, f"export WIDGET_HANDLE='{value}'")
    stage_bytes(repo, "blob.bin", b"\x00\x01\xff\n" + value.encode() + b"\x00")
    result = guard(repo)
    assert result.returncode == 1 and "blob.bin:2" in result.stderr and "WIDGET_HANDLE" in result.stderr
    assert value not in result.stderr


def test_clean_binary_file_passes(repo):
    work, env, _ = repo
    (work / "image.png").write_bytes(bytes(range(256)) * 4)
    subprocess.run(["git", "add", "image.png"], cwd=work, check=True, env=env)
    assert guard(repo).returncode == 0


def commit_without_hook(repo, name: str, content: str) -> None:
    work, env, _ = repo
    stage(repo, name, content)
    subprocess.run(["git", "commit", "-qm", "seed", "--no-verify"], cwd=work, check=True, env=env)


def test_deleting_a_file_passes(repo):
    work, env, value = repo
    commit_without_hook(repo, "old.txt", f"{value}\n")
    subprocess.run(["git", "rm", "-q", "old.txt"], cwd=work, check=True, env=env)
    assert guard(repo).returncode == 0


def test_renamed_file_content_is_scanned(repo):
    work, env, value = repo
    commit_without_hook(repo, "old.txt", f"{value}\n")
    subprocess.run(["git", "mv", "old.txt", "renamed dir name.txt"], cwd=work, check=True, env=env)
    result = guard(repo)
    assert result.returncode == 1 and "renamed dir name.txt:1" in result.stderr


def test_symlinked_secrets_file_is_still_checked(repo, tmp_path):
    work, env, value = repo
    home = tmp_path / "home"
    real = tmp_path / "real-secrets"
    (home / ".secrets").rename(real)
    (home / ".secrets").symlink_to(real)
    stage(repo, "leak.txt", f"{value}\n")
    assert guard(repo).returncode == 1


def test_unreadable_secrets_file_blocks(repo, tmp_path):
    secrets_file = tmp_path / "home" / ".secrets"
    secrets_file.chmod(0o000)
    try:
        stage(repo, "notes.md", "nothing secret here\n")
        result = guard(repo)
        assert result.returncode == 1 and "cannot be read" in result.stderr
    finally:
        secrets_file.chmod(0o600)


def add_to_secrets(tmp_path, line: str) -> None:
    path = tmp_path / "home" / ".secrets"
    path.write_text(path.read_text() + line + "\n")


def test_value_under_an_unusual_name_is_blocked_without_printing_it(repo, tmp_path):
    # A "/" keeps the value from looking random, and the name has no secret-like word.
    value = "opaque/" + secrets.token_hex(6)
    add_to_secrets(tmp_path, f"export WIDGET_HANDLE='{value}'")
    stage(repo, "docs/setup.md", f"intro\nUse {value} here.\n")
    result = guard(repo)
    assert result.returncode == 1
    assert "docs/setup.md:2" in result.stderr and "WIDGET_HANDLE" in result.stderr
    assert value not in result.stderr + result.stdout


def test_short_values_from_the_secrets_file_are_not_matched(repo, tmp_path):
    add_to_secrets(tmp_path, "export REGION=eu-1")
    stage(repo, "notes.md", "deploy to eu-1\n")
    assert guard(repo).returncode == 0


@pytest.mark.parametrize("line", [
    'DB_PASSPHRASE = "Zq81mXbNw0pLrTy5vC2sKd7G"',
    'STRIPE_SECRETKEY: "Zq81mXbNw0pLrTy5vC2sKd7G"',
    'session_cookie = "Zq81mXbNw0pLrTy5vC2sKd7G"',
    'SENTRY_DSN="Zq81mXbNw0pLrTy5vC2sKd7G"',
])
def test_wider_secret_names_trigger_the_assignment_rule(repo, line):
    stage(repo, "app.cfg", line + "\n")
    result = guard(repo)
    assert result.returncode == 1 and "app.cfg:1" in result.stderr


def test_secret_like_names_match_whole_words(repo):
    stage(repo, "a.py", 'author = "Zq81mXbNw0pLrTy5vC2s"\nmonkey = "Zq81mXbNw0pLrTy5vC2s"\n')
    assert guard(repo).returncode == 0


# --- the hook cannot be redirected by the repository it runs in -----------------------


@pytest.mark.skipif(not shutil.which("uv"), reason="uv not installed")
def test_hostile_repo_config_does_not_redirect_the_hook(repo):
    work, env, value = repo
    subprocess.run(["git", "config", "core.hooksPath", str(HOOKS)], cwd=work, check=True, env=env)
    (work / ".python-version").write_text("2.7\n")
    (work / "uv.toml").write_text('python-preference = "only-managed"\nindex-url = "http://127.0.0.1:9/simple"\n'
                                  'python-downloads = "never"\n')
    (work / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0"\nrequires-python = "==2.7.*"\n'
                                         '[tool.uv]\nindex-url = "http://127.0.0.1:9/simple"\n')
    hostile_env = dict(env, UV_PYTHON="2.7", UV_INDEX_URL="http://127.0.0.1:9/simple")
    for name in (".python-version", "uv.toml", "pyproject.toml"):
        subprocess.run(["git", "add", name], cwd=work, check=True, env=env)
    ok = subprocess.run(["git", "commit", "-qm", "clean"], cwd=work, env=hostile_env, capture_output=True, text=True)
    assert ok.returncode == 0, ok.stderr
    stage(repo, "leak.txt", f"{value}\n")
    blocked = subprocess.run(["git", "commit", "-qm", "leak"], cwd=work, env=hostile_env, capture_output=True, text=True)
    assert blocked.returncode != 0 and "commit blocked" in blocked.stderr


def copy_hook_tree(tmp_path):
    root = tmp_path / "dotfiles-copy"
    hooks = root / "home" / ".config" / "git" / "hooks"
    hooks.mkdir(parents=True)
    shutil.copy2(HOOKS / "pre-commit", hooks / "pre-commit")
    (root / "scripts").mkdir()
    for name in ("secrets_commit_guard.py", "secrets_sync.py"):
        shutil.copy2(SCRIPTS / name, root / "scripts" / name)
        (root / "scripts" / name).chmod(0o644)
    return root, hooks


@pytest.mark.parametrize("problem", ["group-writable", "missing"])
def test_hook_refuses_an_unsafe_or_missing_guard(repo, tmp_path, problem):
    work, env, _ = repo
    root, hooks = copy_hook_tree(tmp_path)
    guard_copy = root / "scripts" / "secrets_commit_guard.py"
    if problem == "missing":
        guard_copy.unlink()
    else:
        guard_copy.chmod(0o664)
    subprocess.run(["git", "config", "core.hooksPath", str(hooks)], cwd=work, check=True, env=env)
    stage(repo, "notes.md", "clean\n")
    result = subprocess.run(["git", "commit", "-qm", "x"], cwd=work, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert ("writable by group" if problem == "group-writable" else "missing") in result.stderr

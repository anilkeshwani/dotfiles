"""Tests for scripts/secrets_sync.py against a fake bw. Run: uv run --with pytest pytest tests"""

from __future__ import annotations


import shutil
import stat
import subprocess

import pytest

from conftest import SESSION_KEY, item, planted


def write_secrets(path, text: str, mode: int = 0o600) -> None:
    path.write_text(text)
    path.chmod(mode)


# --- parsing -------------------------------------------------------------------------


def test_parse_both_forms_quotes_and_comments(ss):
    text = "\n".join([
        "# a comment",
        "",
        "PLAIN=abc123",
        "export EXPORTED=def456",
        "SINGLE='with space'",
        'DOUBLE="with \\"escaped\\" quote"',
        "TRAILING=value # comment after",
        "  export   INDENTED='x'",
        "CONCAT='a'\\''b'",
        "EMPTY=",
    ])
    parsed = ss.parse_secrets(text)
    values = {a.name: a.value for a in parsed.assignments}
    assert values == {
        "PLAIN": "abc123", "EXPORTED": "def456", "SINGLE": "with space",
        "DOUBLE": 'with "escaped" quote', "TRAILING": "value", "INDENTED": "x",
        "CONCAT": "a'b", "EMPTY": "",
    }
    assert parsed.other_lines == []
    assert not parsed.generated


def test_parse_flags_dynamic_values_and_commands(ss):
    text = "\n".join([
        'SUB="$(cat /etc/passwd)"',
        "REF=$HOME/x",
        "TICK=`whoami`",
        "LITERAL='$(not run)'",
        "echo hello",
        "BROKEN='unterminated",
        "CHAIN=a; rm -rf /",
    ])
    parsed = ss.parse_secrets(text)
    values = {a.name: a.value for a in parsed.assignments}
    assert values == {"SUB": None, "REF": None, "TICK": None, "LITERAL": "$(not run)"}
    assert parsed.other_lines == [5, 6, 7]


# --- quoting ---------------------------------------------------------------------------

HOSTILE = [
    "it's", "'", "''", '"', "$(touch PWNED)", "`touch PWNED`", "${HOME}", "$HOME", "a;touch PWNED",
    "a b  c", "\\", "\\'", "!event", "*", "~", "#notacomment", "a'$(touch PWNED)'b", "ünïcode", "",
]


@pytest.mark.parametrize("shell", ["sh", "bash", "zsh"])
def test_hostile_values_round_trip_without_execution(ss, tmp_path, shell):
    if not shutil.which(shell):
        pytest.skip(f"{shell} not installed")
    groups = {"hostile": [(f"V{i}", v) for i, v in enumerate(HOSTILE)]}
    rendered = ss.render_secrets("mac", "secrets-sync", groups, [])
    path = tmp_path / "secrets"
    path.write_text(rendered)
    script = ". ./secrets; " + "; ".join(f'printf "%s\\0" "$V{i}"' for i in range(len(HOSTILE)))
    out = subprocess.run([shell, "-c", script], cwd=tmp_path, capture_output=True, check=True).stdout
    assert out.decode().split("\0")[:-1] == HOSTILE
    assert not (tmp_path / "PWNED").exists()


@pytest.mark.parametrize("value", ["line1\nline2", "a\rb", "nul\x00", "esc\x1b[31m", "del\x7f"])
def test_control_characters_are_rejected(ss, value):
    with pytest.raises(ss.SecretsSyncError):
        ss.render_secrets("mac", "f", {"i": [("NAME", value)]}, [])


def test_denied_names_cannot_come_from_the_vault(ss, env, monkeypatch):
    env.set_items(item("evil", {"PATH": "/tmp/evil"}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 2
    assert not env.secrets.exists()


@pytest.mark.parametrize("name", ["LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "PROMPT_COMMAND", "BASH_FUNC_x%%"])
def test_denied_name_list(ss, name):
    assert ss.is_denied_name(name) or not ss.NAME_RE.match(name)


# --- machine tagging -------------------------------------------------------------------


def test_pull_writes_only_this_machines_variables(ss, env, monkeypatch, capsys):
    env.set_items(
        item("shared", {"SHARED_KEY": "s" * 12}, machines="all"),
        item("maconly", {"MAC_KEY": "m" * 12}, machines="mac"),
        item("server", {"SERVER_KEY": "b" * 12}, machines="bigboss"),
        item("both", {"BOTH_KEY": "x" * 12}, machines="mac, bigboss"),
        item("untagged", {"UNTAGGED_KEY": "u" * 12}, machines=None),
    )
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 0
    names = {a.name for a in ss.parse_secrets(env.secrets.read_text()).assignments}
    assert names == {"SHARED_KEY", "MAC_KEY", "BOTH_KEY"}
    captured = capsys.readouterr()
    assert "Machine tag: mac" in captured.out
    assert "Wrote 3 variables" in captured.out and "BOTH_KEY, MAC_KEY, SHARED_KEY" in captured.out
    assert "untagged" in captured.err


def test_invalid_machine_tag_fails_closed(ss, env, monkeypatch):
    env.set_items(item("bad", {"K": "v" * 12}, machines="mac;rm"))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 2
    assert not env.secrets.exists()


def test_missing_config_refuses(ss, env, monkeypatch):
    (env.home / ".config" / "secrets-sync" / "config.toml").unlink()
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 2


def test_config_from_another_machine_refuses(ss, env, monkeypatch, capsys):
    monkeypatch.setattr(ss, "machine_fingerprint", lambda: "some-other-machine")
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 2
    assert "another machine" in capsys.readouterr().err


def test_org_items_are_ignored(ss, env, monkeypatch):
    env.set_items(item("orgitem", {"ORG_KEY": "o" * 12}, org="org-1"), item("mine", {"MINE": "m" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 0
    assert "ORG_KEY" not in env.secrets.read_text()


def test_duplicate_variable_across_items_refuses(ss, env, monkeypatch):
    env.set_items(item("a", {"DUP": "1" * 12}), item("b", {"DUP": "2" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 2


# --- writing ----------------------------------------------------------------------------


def test_pull_writes_mode_600_atomically_with_header_and_groups(ss, env, monkeypatch):
    env.set_items(item("zeta", {"Z_KEY": "z" * 12}), item("alpha", {"B_KEY": "b" * 12, "A_KEY": "a" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 0
    text = env.secrets.read_text()
    assert stat.S_IMODE(env.secrets.stat().st_mode) == 0o600
    assert text.startswith(ss.HEADER_FIRST_LINE)
    assert text.index("# Bitwarden item: alpha") < text.index("A_KEY") < text.index("B_KEY") < text.index("# Bitwarden item: zeta")
    assert [p.name for p in env.home.iterdir() if "secrets-sync-" in p.name] == []
    assert ss.main(["pull"]) == 0
    assert env.secrets.read_text() == text  # deterministic


def test_pull_refuses_symlink_target(ss, env, monkeypatch, tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.write_text("")
    env.secrets.symlink_to(elsewhere)
    env.set_items(item("a", {"K": "k" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 2
    assert elsewhere.read_text() == ""


def test_pull_refuses_group_writable_directory(ss, env, monkeypatch):
    env.set_items(item("a", {"K": "k" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    env.home.chmod(0o770)
    try:
        assert ss.main(["pull"]) == 2
        assert not env.secrets.exists()
    finally:
        env.home.chmod(0o700)


def test_backups_are_private_and_pruned(ss, env, monkeypatch):
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    for i in range(8):
        env.set_items(item("a", {"K": f"value-number-{i:04d}"}))
        assert ss.main(["pull"]) == 0
    backups = env.home / ".local" / "state" / "secrets-sync" / "backups"
    files = sorted(backups.iterdir())
    assert len(files) == ss.DEFAULT_BACKUP_COUNT
    assert stat.S_IMODE(backups.stat().st_mode) == 0o700
    assert all(stat.S_IMODE(f.stat().st_mode) == 0o600 for f in files)
    assert "value-number-0006" in files[-1].read_text()


def test_local_only_block_is_preserved_and_wins(ss, env, monkeypatch, capsys):
    local = ["export LOCAL_ONLY='keep me'", "# a note", "export SHADOW='local value'"]
    env.set_items(item("a", {"K": "k" * 12, "SHADOW": "vault value"}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 0
    text = env.secrets.read_text().replace(f"{ss.LOCAL_HINT}\n", f"{ss.LOCAL_HINT}\n" + "\n".join(local) + "\n")
    write_secrets(env.secrets, text)
    env.set_items(item("a", {"K": "changed" * 3, "SHADOW": "vault value"}))
    assert ss.main(["pull"]) == 0
    new = env.secrets.read_text()
    block = new.split(ss.LOCAL_BEGIN)[1].split(ss.LOCAL_END)[0]
    assert block == f"\n{ss.LOCAL_HINT}\n" + "\n".join(local) + "\n"
    assert "vault value" not in new
    assert "SHADOW is in the local-only block" in capsys.readouterr().err


def test_hand_written_file_with_unmanaged_entries_is_not_clobbered(ss, env, monkeypatch):
    write_secrets(env.secrets, "export K=old\nexport ONLY_HERE=abcdefgh123\nsource ~/other\n")
    env.set_items(item("a", {"K": "k" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 2
    assert "ONLY_HERE" in env.secrets.read_text() and "k" * 12 not in env.secrets.read_text()
    assert ss.main(["pull", "--keep-unmanaged"]) == 0
    parsed = ss.parse_secrets(env.secrets.read_text())
    assert {a.name for a in parsed.local_assignments} == {"ONLY_HERE"}
    assert "source ~/other" in parsed.local_lines
    assert {a.name: a.value for a in parsed.assignments} == {"K": "k" * 12}


def test_dry_run_writes_nothing(ss, env, monkeypatch, capsys):
    env.set_items(item("a", {"NEW_KEY": "n" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull", "--dry-run"]) == 0
    assert not env.secrets.exists()
    assert "Added:   NEW_KEY" in capsys.readouterr().out


# --- sessions ---------------------------------------------------------------------------


def test_unlocks_syncs_before_reading_and_locks(ss, env):
    env.set_items(item("a", {"K": "k" * 12}))
    assert ss.main(["pull"]) == 0
    commands = env.commands()
    assert commands.index("unlock") < commands.index("sync") < commands.index("list items")
    assert commands[-1] == "lock"


def test_locks_even_when_the_run_fails(ss, env, monkeypatch):
    env.state["fail"] = {"list": "badjson"}
    env.save()
    assert ss.main(["pull"]) == 2
    assert env.commands()[-1] == "lock"


def test_locks_on_ctrl_c(ss, env, monkeypatch):
    env.set_items(item("a", {"K": "k" * 12}))

    def interrupt(*_a, **_k):
        raise KeyboardInterrupt

    monkeypatch.setattr(ss, "load_vault", interrupt)
    assert ss.main(["pull"]) == 130
    assert env.commands()[-1] == "lock"
    assert not env.secrets.exists()


def test_locks_after_failed_unlock(ss, env):
    env.state["unlock_ok"] = False
    env.save()
    assert ss.main(["check"]) == 2
    assert env.commands()[-1] == "lock"


def test_existing_session_is_used_and_left_unlocked(ss, env, monkeypatch):
    env.set_items(item("a", {"K": "k" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 0
    assert "unlock" not in env.commands() and "lock" not in env.commands()


def test_session_travels_in_env_never_argv(ss, env):
    env.set_items(item("a", {"K": "k" * 12}))
    assert ss.main(["pull"]) == 0
    for call in env.calls():
        assert SESSION_KEY not in " ".join(call["argv"])
        assert "--session" not in call["argv"]
    assert all(c["session_ok"] for c in env.calls() if c["argv"][1:3] == ["list", "items"])


def test_unauthenticated_bw_is_not_logged_in_for_you(ss, env, capsys):
    env.state["status"] = "unauthenticated"
    env.save()
    assert ss.main(["pull"]) == 2
    assert "bw login" in capsys.readouterr().err
    assert "unlock" not in env.commands()


def test_refuses_without_a_terminal(ss, env, monkeypatch):
    monkeypatch.setattr(ss, "stdio_is_tty", lambda: False)
    assert ss.main(["pull"]) == 2
    assert ss.main(["pull", "--non-interactive"]) == 2  # no BW_SESSION
    assert env.commands() == []
    env.set_items(item("a", {"K": "k" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull", "--non-interactive"]) == 0


# --- check ------------------------------------------------------------------------------


def test_check_reports_drift_by_name_only(ss, env, monkeypatch, capsys):
    same, local_value, vault_value, unmanaged = planted("same"), planted("loc"), planted("vlt"), planted("un")
    write_secrets(env.secrets, f"SAME={same}\nDIFF={local_value}\nexport UNMANAGED='{unmanaged}'\nSERVER=x\n")
    env.set_items(
        item("a", {"SAME": same, "DIFF": vault_value, "MISSING": planted("miss")}),
        item("b", {"SERVER": "y" * 12}, machines="bigboss"),
    )
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["check"]) == 1
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "MISSING" in output and "UNMANAGED  unmanaged" in output and "DIFF  differs" in output
    assert "SERVER" in output.split("does not assign them")[1]
    for value in (same, local_value, vault_value, unmanaged):
        assert value not in output


def test_check_clean(ss, env, monkeypatch, capsys):
    env.set_items(item("a", {"K": "k" * 12}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["pull"]) == 0
    assert ss.main(["check"]) == 0
    assert "No drift." in capsys.readouterr().out


# --- push -------------------------------------------------------------------------------


def test_push_sends_values_over_stdin_only(ss, env, monkeypatch, capsys):
    value = planted("push")
    write_secrets(env.secrets, f"export NEW_KEY='{value}'\n")
    monkeypatch.setattr("builtins.input", lambda: "y")
    assert ss.main(["push", "--item", "group", "--machines", "mac,bigboss", "NEW_KEY"]) == 0
    state = env.load()
    created = next(i for i in state["items"] if i["name"] == "group")
    fields = {f["name"]: f for f in created["fields"]}
    assert fields["NEW_KEY"] == {"name": "NEW_KEY", "value": value, "type": 1, "linkedId": None}
    assert fields["machines"]["value"] == "mac,bigboss"
    assert created["organizationId"] is None and created["folderId"] == "folder-1"
    for call in env.calls():
        assert value not in " ".join(call["argv"])
    output = "".join(capsys.readouterr())
    assert value not in output
    assert env.commands()[-1] == "lock"


def test_push_refuses_to_overwrite_without_force(ss, env, monkeypatch):
    write_secrets(env.secrets, "export K=newvalue123\n")
    env.set_items(item("group", {"K": "oldvalue123"}))
    monkeypatch.setattr("builtins.input", lambda: "y")
    assert ss.main(["push", "--item", "group", "--machines", "all", "K"]) == 2
    assert env.load()["items"][0]["fields"][0]["value"] == "oldvalue123"
    assert ss.main(["push", "--item", "group", "--machines", "all", "--force", "K"]) == 0
    assert env.load()["items"][0]["fields"][0]["value"] == "newvalue123"


def test_push_declined_writes_nothing(ss, env, monkeypatch):
    write_secrets(env.secrets, "export K=newvalue123\n")
    monkeypatch.setattr("builtins.input", lambda: "n")
    assert ss.main(["push", "--item", "group", "--machines", "all", "K"]) == 0
    assert env.load()["items"] == []
    assert not any(c.startswith("create") for c in env.commands())


def test_push_refuses_dynamic_and_local_only_values(ss, env, monkeypatch):
    text = f'DYN="$(cat x)"\n{ss.LOCAL_BEGIN}\nexport LOC=abcdefgh123\n{ss.LOCAL_END}\n'
    write_secrets(env.secrets, text)
    monkeypatch.setattr("builtins.input", lambda: "y")
    assert ss.main(["push", "--item", "g", "--machines", "all", "DYN"]) == 2
    assert ss.main(["push", "--item", "g", "--machines", "all", "LOC"]) == 2
    assert env.commands() == []


def test_import_plan_creates_folder_and_items(ss, env, monkeypatch, tmp_path):
    env.state["folders"] = []
    env.save()
    write_secrets(env.secrets, "A_KEY=aaaaaaaaaa1\nB_KEY=bbbbbbbbbb2\nC_KEY=cccccccccc3\n")
    plan = tmp_path / "plan.toml"
    plan.write_text('[first]\nmachines = "all"\nvars = ["A_KEY", "B_KEY"]\n[second]\nmachines = "mac"\nvars = ["C_KEY"]\n')
    monkeypatch.setattr("builtins.input", lambda: "y")
    assert ss.main(["import", str(plan)]) == 0
    state = env.load()
    assert [f["name"] for f in state["folders"]] == ["secrets-sync"]
    assert sorted(i["name"] for i in state["items"]) == ["first", "second"]
    assert ss.main(["pull"]) == 0
    assert {a.name for a in ss.parse_secrets(env.secrets.read_text()).assignments} == {"A_KEY", "B_KEY", "C_KEY"}


def test_plan_cannot_carry_values(ss, tmp_path):
    plan = tmp_path / "plan.toml"
    plan.write_text('[g]\nmachines = "all"\nvars = ["A"]\nA = "secret"\n')
    with pytest.raises(ss.SecretsSyncError):
        ss.load_plan(plan)


# --- no secret in output ----------------------------------------------------------------


def test_no_planted_value_reaches_output_on_any_path(ss, env, monkeypatch, capsys):
    vault_value, local_value = planted("vault"), planted("local")
    write_secrets(env.secrets, f"export LEAKY='{local_value}'\n")
    env.set_items(item("a", {"LEAKY": vault_value}))
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    ss.main(["check"])
    ss.main(["pull", "--dry-run"])
    ss.main(["pull", "--force"])
    ss.main(["doctor"])

    def explode(*_a, **_k):
        raise ValueError(f"boom {vault_value} {local_value}")

    monkeypatch.setattr(ss, "render_secrets", explode)
    assert ss.main(["pull"]) == 2
    monkeypatch.setenv("SECRETS_SYNC_DEBUG", "1")
    assert ss.main(["pull"]) == 2
    output = "".join(capsys.readouterr())
    assert "internal error (ValueError)" in output
    assert vault_value not in output and local_value not in output
    assert SESSION_KEY not in output


def test_bw_error_messages_are_redacted(ss, env, monkeypatch, capsys):
    value = planted("err")
    ss.REDACT.add(value)
    env.state["fail"] = {"sync": "error"}
    env.save()
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["check"]) == 2
    assert "`bw sync` failed" in capsys.readouterr().err


def test_doctor_flags_risky_states(ss, env, monkeypatch, capsys):
    write_secrets(env.secrets, "K=v\n", mode=0o644)
    (env.home / ".zsh_history").write_text(f"export BW_SESSION={SESSION_KEY}\nbw unlock hunter2\n")
    monkeypatch.setenv("BW_SESSION", SESSION_KEY)
    assert ss.main(["doctor"]) == 1
    output = capsys.readouterr().out
    assert "mode 644" in output
    assert "BW_SESSION is set" in output
    assert "a BW_SESSION value" in output and "a password passed to bw unlock" in output
    assert "hunter2" not in output and SESSION_KEY not in output

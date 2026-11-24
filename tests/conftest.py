"""Fixtures for the secrets-sync tests: a fake `bw` executable and a throwaway HOME."""

from __future__ import annotations

import importlib.util
import json
import secrets
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
SESSION_KEY = "fakesession" + "Q" * 20

FAKE_BW = textwrap.dedent(
    """\
    #!{python}
    import base64, json, os, sys
    state_path, log_path = os.environ["FAKE_BW_STATE"], os.environ["FAKE_BW_LOG"]
    args = [a for a in sys.argv[1:] if a != "--nointeraction"]
    stdin = sys.stdin.read() if args[:1] in (["create"], ["edit"]) else ""
    with open(state_path) as f:
        state = json.load(f)
    session_ok = os.environ.get("BW_SESSION") == state["session_key"]
    with open(log_path, "a") as f:
        f.write(json.dumps({{"argv": sys.argv[1:], "session_ok": session_ok,
                             "has_session_env": "BW_SESSION" in os.environ}}) + "\\n")

    def save():
        with open(state_path, "w") as f:
            json.dump(state, f)

    def fail(msg, code=1):
        print(msg, file=sys.stderr)
        sys.exit(code)

    cmd = args[0] if args else ""
    if cmd in state.get("fail", {{}}):
        mode = state["fail"][cmd]
        if mode == "badjson":
            print("this is not json")
            sys.exit(0)
        fail("simulated failure")
    print("Unable to fetch ServerConfig from https://example.invalid", file=sys.stderr)
    if cmd == "--version":
        print(state.get("version", "2026.11.0"))
    elif cmd == "status":
        status = state["status"]
        if status != "unauthenticated" and session_ok:
            status = "unlocked"
        print(json.dumps({{"serverUrl": None, "lastSync": state.get("last_sync"), "status": status}}))
    elif cmd == "unlock":
        if not state.get("unlock_ok", True):
            fail("Invalid master password.")
        print(state["session_key"])
    elif cmd == "lock":
        print("Your vault is locked.")
    elif not session_ok:
        fail("Vault is locked.")
    elif cmd == "sync":
        print("Syncing complete.")
    elif args[:2] == ["list", "folders"]:
        print(json.dumps(state["folders"]))
    elif args[:2] == ["list", "items"]:
        folder = args[args.index("--folderid") + 1]
        print(json.dumps([i for i in state["items"] if i.get("folderId") == folder]))
    elif args[:2] == ["get", "item"]:
        print(json.dumps(next(i for i in state["items"] if i["id"] == args[2])))
    elif args[:1] == ["create"]:
        obj = json.loads(base64.b64decode(stdin))
        obj["id"] = "new-%d" % (len(state["items"]) + len(state["folders"]))
        state["folders" if args[1] == "folder" else "items"].append(obj)
        save()
        print(json.dumps(obj))
    elif args[:2] == ["edit", "item"]:
        obj = json.loads(base64.b64decode(stdin))
        state["items"] = [obj if i["id"] == args[2] else i for i in state["items"]]
        save()
        print(json.dumps(obj))
    else:
        fail("unknown command " + " ".join(args))
    """
)


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def ss():
    return load_module("secrets_sync")


def item(name: str, variables: dict[str, str], machines: str | None = "all",
         org: str | None = None, item_id: str | None = None, folder: str = "folder-1",
         field_type: int = 1) -> dict:
    fields = [{"name": k, "value": v, "type": field_type, "linkedId": None} for k, v in variables.items()]
    if machines is not None:
        fields.append({"name": "machines", "value": machines, "type": 0, "linkedId": None})
    return {"id": item_id or f"id-{name}", "name": name, "type": 2, "folderId": folder,
            "organizationId": org, "fields": fields, "secureNote": {"type": 0}}


class FakeBw:
    def __init__(self, root: Path) -> None:
        self.state_path = root / "bw-state.json"
        self.log_path = root / "bw-log.jsonl"
        self.state = {
            "status": "locked", "session_key": SESSION_KEY, "last_sync": "2026-11-24T10:00:00.000Z",
            "folders": [{"id": "folder-1", "name": "secrets-sync", "object": "folder"}],
            "items": [],
        }
        self.save()
        self.log_path.write_text("")

    def save(self) -> None:
        self.state_path.write_text(json.dumps(self.state))

    def load(self) -> dict:
        self.state = json.loads(self.state_path.read_text())
        return self.state

    def set_items(self, *items: dict) -> None:
        self.state["items"] = list(items)
        self.save()

    def calls(self) -> list[dict]:
        return [json.loads(line) for line in self.log_path.read_text().splitlines()]

    def commands(self) -> list[str]:
        return [" ".join(a for a in c["argv"] if a != "--nointeraction").split(" --")[0] for c in self.calls()]


@pytest.fixture
def env(tmp_path, monkeypatch, ss):
    """A HOME with a tagged config, a fake bw first on PATH and a terminal assumed."""
    home = tmp_path / "home"
    home.mkdir(mode=0o700)
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake = bindir / "bw"
    fake.write_text(FAKE_BW.format(python=sys.executable))
    fake.chmod(0o755)
    bw = FakeBw(tmp_path)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(home / ".local" / "state"))
    monkeypatch.setenv("PATH", f"{bindir}:/usr/bin:/bin")
    monkeypatch.setenv("FAKE_BW_STATE", str(bw.state_path))
    monkeypatch.setenv("FAKE_BW_LOG", str(bw.log_path))
    monkeypatch.delenv("BW_SESSION", raising=False)
    monkeypatch.delenv("HISTFILE", raising=False)
    monkeypatch.setattr(ss, "REDACT", ss.Redactor())
    monkeypatch.setattr(ss, "machine_fingerprint", lambda: "fp-test")
    monkeypatch.setattr(ss, "stdio_is_tty", lambda: True)
    assert ss.main(["init", "--machine", "mac"]) == 0
    bw.home = home
    bw.secrets = home / ".secrets"
    return bw


def planted(label: str) -> str:
    return f"planted{label}{secrets.token_hex(10)}"

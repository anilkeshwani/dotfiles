# /// script
# requires-python = ">=3.11"
# ///
"""Report Claude Code extensions and settings entries that cannot work.

With --hook (the SessionStart hook) it runs at most once a day and prints nothing
when healthy. Problems go to stderr with exit code 2, which Claude Code shows to
the user without adding them to the model's context.
"""

import argparse
import json
import os
import re
import shlex
import shutil
import sys
import time
from pathlib import Path

HOME = Path.home()
CONFIG_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR") or HOME / ".claude").expanduser()
CLAUDE_JSON = (
    CONFIG_DIR / ".claude.json" if os.environ.get("CLAUDE_CONFIG_DIR") else HOME / ".claude.json"
)
STATE_DIR = Path(os.environ.get("XDG_STATE_HOME") or HOME / ".local/state") / "claude-config-healthcheck"
THROTTLE_SECONDS = 24 * 60 * 60

LINKED_PATHS = (
    "CLAUDE.md",
    "settings.json",
    "statusline-command.sh",
    "skills",
    "agents",
    "commands",
    "output-styles",
    "hooks",
)
# Servers that exist without a local config entry: claude.ai connectors and built-ins.
UNLISTED_SERVER_PREFIXES = ("claude_ai_",)
UNLISTED_SERVERS = {"claude-in-chrome", "ide"}
PLUGIN_ROOT_VARS = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT(?::-[^}]*)?\}|\$CLAUDE_PLUGIN_ROOT")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def short(path: Path | str) -> str:
    return str(path).replace(str(HOME), "~", 1)


def normalize_server(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def command_problems(command: str, plugin_root: Path | None = None) -> list[str]:
    """Return what a hook, MCP or LSP command needs that is missing."""
    if plugin_root is not None:
        command = PLUGIN_ROOT_VARS.sub(str(plugin_root), command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        return [f"cannot parse `{command}`"]
    if not tokens:
        return []
    missing = []
    program = os.path.expanduser(tokens[0])
    if "/" in program:
        if not Path(program).exists():
            missing.append(f"`{short(program)}` does not exist")
    elif shutil.which(program) is None:
        missing.append(f"`{program}` is not on PATH")
    for token in tokens[1:]:
        if token.startswith(("/", "~/")) and not Path(os.path.expanduser(token)).exists():
            missing.append(f"`{short(token)}` does not exist")
    return missing


def commands_in(node: object) -> list[str]:
    found = []
    if isinstance(node, dict):
        command = node.get("command")
        if isinstance(command, str):
            raw_args = node.get("args")
            args = raw_args if isinstance(raw_args, list) else []
            found.append(" ".join([command, *(shlex.quote(str(a)) for a in args)]))
        for value in node.values():
            found.extend(commands_in(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(commands_in(value))
    return found


def check_symlinks() -> list[str]:
    problems = []
    for name in LINKED_PATHS:
        root = CONFIG_DIR / name
        candidates = [root]
        if root.is_dir():
            candidates += [p for p in root.rglob("*") if len(p.relative_to(root).parts) <= 3]
        for path in candidates:
            if path.is_symlink() and not path.exists():
                problems.append(f"broken symlink {short(path)} -> {short(os.readlink(path))}")
    return problems


def check_settings_commands(settings: dict) -> list[str]:
    problems = []
    status_line = (settings.get("statusLine") or {}).get("command")
    if isinstance(status_line, str):
        problems += [f"status line: {m}" for m in command_problems(status_line)]
    for command in commands_in(settings.get("hooks")):
        problems += [f"settings hook: {m}" for m in command_problems(command)]
    return problems


def plugin_components(key: str, install_path: Path) -> dict[str, list]:
    """Merge a plugin's manifest, its marketplace entry and its component files."""
    name, _, marketplace = key.partition("@")
    manifest = load_json(install_path / ".claude-plugin" / "plugin.json")
    catalog = load_json(
        CONFIG_DIR / "plugins" / "marketplaces" / marketplace / ".claude-plugin" / "marketplace.json"
    )
    entry = next((p for p in catalog.get("plugins", []) if p.get("name") == name), {})
    components = {}
    for field, filename in (("hooks", "hooks/hooks.json"), ("mcpServers", ".mcp.json"), ("lspServers", ".lsp.json")):
        parts = [load_json(install_path / filename)]
        for source in (entry.get(field), manifest.get(field)):
            if isinstance(source, str):
                parts.append(load_json(install_path / source))
            elif source:
                parts.append(source)
        components[field] = parts
    return components


def check_plugins(settings: dict) -> tuple[list[str], set[str]]:
    problems = []
    servers = set()
    installed = load_json(CONFIG_DIR / "plugins" / "installed_plugins.json").get("plugins", {})
    labels = {"hooks": "hook", "mcpServers": "MCP server", "lspServers": "LSP server"}
    for key, enabled in (settings.get("enabledPlugins") or {}).items():
        if not enabled:
            continue
        records = installed.get(key) or []
        if not records:
            problems.append(f"plugin {key} is enabled but not installed")
            continue
        install_path = Path(records[0].get("installPath", ""))
        if not install_path.is_dir():
            problems.append(f"plugin {key}: install path {short(install_path)} is missing")
            continue
        components = plugin_components(key, install_path)
        for field, parts in components.items():
            for command in commands_in(parts):
                for missing in command_problems(command, install_path):
                    problems.append(f"plugin {key}: {labels[field]}: {missing}")
        plugin_name = key.partition("@")[0]
        for part in components["mcpServers"]:
            listed = part.get("mcpServers", part) if isinstance(part, dict) else {}
            for server in listed if isinstance(listed, dict) else {}:
                servers.add(normalize_server(f"plugin_{plugin_name}_{server}"))
    return problems, servers


def check_mcp_references(settings: dict, servers: set[str]) -> list[str]:
    problems = []
    permissions = settings.get("permissions") or {}
    for kind in ("allow", "deny", "ask"):
        for rule in permissions.get(kind) or []:
            match = re.match(r"mcp__(.+?)__", rule) if isinstance(rule, str) else None
            if not match:
                continue
            server = match.group(1)
            if server in servers or server in UNLISTED_SERVERS or server.startswith(UNLISTED_SERVER_PREFIXES):
                continue
            problems.append(f"{kind} rule `{rule}` names MCP server `{server}`, which is not configured")
    for entry in settings.get("deniedMcpServers") or []:
        name = entry.get("serverName") if isinstance(entry, dict) else None
        if not name or name.startswith("claude.ai ") or normalize_server(name) in servers:
            continue
        problems.append(
            f"deniedMcpServers entry `{name}` matches no configured server "
            "(claude.ai connectors are named `claude.ai <Name>`)"
        )
    return problems


def check_skill_dirs() -> list[str]:
    problems = []
    for root in (CONFIG_DIR / "skills", HOME / ".agents" / "skills"):
        if not root.is_dir():
            continue
        for path in sorted(root.iterdir()):
            if path.name == "synced" or path.name.startswith(".") or not path.is_dir():
                continue
            if not (path / "SKILL.md").exists() and not (path / ".claude-plugin").exists():
                problems.append(f"skill directory {short(path)} has no SKILL.md")
    return problems


def run_checks() -> list[str]:
    settings_path = CONFIG_DIR / "settings.json"
    try:
        settings = json.loads(settings_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return [f"{short(settings_path)} cannot be read: {error}"]
    plugin_problems, servers = check_plugins(settings)
    servers |= {normalize_server(name) for name in load_json(CLAUDE_JSON).get("mcpServers") or {}}
    return [
        *check_symlinks(),
        *check_settings_commands(settings),
        *plugin_problems,
        *check_mcp_references(settings, servers),
        *check_skill_dirs(),
    ]


def ran_recently() -> bool:
    stamp = STATE_DIR / f"{CONFIG_DIR.name}.last-run"
    try:
        if time.time() - stamp.stat().st_mtime < THROTTLE_SECONDS:
            return True
    except OSError:
        pass
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        stamp.touch()
    except OSError:
        pass
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--hook", action="store_true", help="SessionStart mode: daily, silent when healthy")
    args = parser.parse_args()
    if args.hook and ran_recently():
        return 0
    problems = run_checks()
    if not problems:
        if not args.hook:
            print(f"No problems found in {short(CONFIG_DIR)}.")
        return 0
    stream = sys.stderr if args.hook else sys.stdout
    noun = "problem" if len(problems) == 1 else "problems"
    print(f"Claude config check: {len(problems)} {noun} in {short(CONFIG_DIR)}", file=stream)
    for problem in problems:
        print(f"  - {problem}", file=stream)
    if args.hook:
        print(f"Recheck with: uv run --script {short(Path(__file__))}", file=stream)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["tomlkit>=0.13,<1"]
# ///

from __future__ import annotations

import importlib.util
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tomlkit

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("dotfiles_install", REPO_ROOT / "install.py")
assert SPEC is not None and SPEC.loader is not None
dotfiles_install = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dotfiles_install)


class CodexConfigPolicyTests(unittest.TestCase):
    def test_missing_config_creates_only_disabled_import_sync(self) -> None:
        updated, changes = dotfiles_install.reconcile_codex_config(None)
        document = tomlkit.parse(updated)

        self.assertEqual(list(document), ["desktop"])
        self.assertFalse(document["desktop"]["external-agent-import-sync-enabled"])
        self.assertEqual(changes, ("disable external agent import sync",))

    def test_enabled_sync_removes_imported_plugins_and_marketplaces(self) -> None:
        raw = """# keep this comment
[marketplaces.claude-plugins-official]
source = "https://github.com/anthropics/claude-plugins-official.git"

[marketplaces.skypilot]
source = "https://github.com/skypilot-org/skypilot.git"

[marketplaces.personal]
source = "file:///tmp/personal"

[plugins."code-review@claude-plugins-official"]
enabled = true

[plugins."skypilot@skypilot"]
enabled = true

[plugins."browser@openai-bundled"]
enabled = true

[plugins."mine@personal"]
enabled = true

[mcp_servers.example]
command = "example"

[projects."/tmp/project"]
trust_level = "trusted"

[desktop]
external-agent-import-sync-enabled = true
notify = ["notify-send"]
"""
        updated, changes = dotfiles_install.reconcile_codex_config(raw)
        document = tomlkit.parse(updated)

        self.assertNotIn("claude-plugins-official", document["marketplaces"])
        self.assertNotIn("skypilot", document["marketplaces"])
        self.assertIn("personal", document["marketplaces"])
        self.assertNotIn("code-review@claude-plugins-official", document["plugins"])
        self.assertNotIn("skypilot@skypilot", document["plugins"])
        self.assertIn("browser@openai-bundled", document["plugins"])
        self.assertIn("mine@personal", document["plugins"])
        self.assertEqual(document["mcp_servers"]["example"]["command"], "example")
        self.assertEqual(document["projects"]["/tmp/project"]["trust_level"], "trusted")
        self.assertEqual(document["desktop"]["notify"], ["notify-send"])
        self.assertFalse(document["desktop"]["external-agent-import-sync-enabled"])
        self.assertTrue(updated.startswith("# keep this comment\n"))
        self.assertIn("remove plugin code-review@claude-plugins-official", changes)

    def test_disabled_sync_preserves_intentional_plugins_except_denied_ids(self) -> None:
        raw = """[plugins."code-review@claude-plugins-official"]
enabled = true

[plugins."explanatory-output-style@claude-plugins-official"]
enabled = true

[plugins."security-guidance@claude-plugins-official"]
enabled = true

[plugins."posthog@claude-plugins-official"]
enabled = true

[plugins."custom@skypilot"]
enabled = true

[desktop]
external-agent-import-sync-enabled = false
"""
        updated, changes = dotfiles_install.reconcile_codex_config(raw)
        plugins = tomlkit.parse(updated)["plugins"]

        self.assertIn("code-review@claude-plugins-official", plugins)
        self.assertIn("custom@skypilot", plugins)
        for plugin_id in dotfiles_install.DENIED_CODEX_PLUGINS:
            self.assertNotIn(plugin_id, plugins)
            self.assertIn(f"remove plugin {plugin_id}", changes)

    def test_malformed_config_raises_without_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config = Path(temporary_directory) / "config.toml"
            original = "[desktop\n"
            config.write_text(original, encoding="utf-8")

            with self.assertRaises(Exception):
                dotfiles_install.reconcile_codex_config(config.read_text(encoding="utf-8"))

            self.assertEqual(config.read_text(encoding="utf-8"), original)

    def test_atomic_write_preserves_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            config = Path(temporary_directory) / "config.toml"
            config.write_text("old", encoding="utf-8")
            config.chmod(0o640)

            dotfiles_install.write_text_atomic(config, "new")

            self.assertEqual(config.read_text(encoding="utf-8"), "new")
            self.assertEqual(stat.S_IMODE(config.stat().st_mode), 0o640)

            new_config = Path(temporary_directory) / "new-config.toml"
            dotfiles_install.write_text_atomic(new_config, "new")
            self.assertEqual(stat.S_IMODE(new_config.stat().st_mode), 0o600)

    def test_reconciliation_is_idempotent(self) -> None:
        raw = """[plugins."code-review@claude-plugins-official"]
enabled = true

[desktop]
external-agent-import-sync-enabled = true
"""
        first, first_changes = dotfiles_install.reconcile_codex_config(raw)
        second, second_changes = dotfiles_install.reconcile_codex_config(first)

        self.assertTrue(first_changes)
        self.assertEqual(second, first)
        self.assertEqual(second_changes, ())

    def test_install_dry_run_does_not_write_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            home = root / "home"
            backup_root = root / "backups"
            source.mkdir()
            config = home / ".codex/config.toml"
            config.parent.mkdir(parents=True)
            original = """[desktop]
external-agent-import-sync-enabled = true
"""
            config.write_text(original, encoding="utf-8")

            with mock.patch.dict(os.environ, {}, clear=True):
                dotfiles_install.install(
                    source=source,
                    dry_run=True,
                    home=home,
                    backup_root=backup_root,
                    codex_only=True,
                )

            self.assertEqual(config.read_text(encoding="utf-8"), original)
            self.assertFalse(backup_root.exists())

    def test_codex_only_plan_excludes_claude_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            home = root / "home"
            (source / ".codex").mkdir(parents=True)
            (source / ".claude").mkdir(parents=True)
            (source / ".codex/AGENTS.md").write_text("Codex", encoding="utf-8")
            (source / ".claude/CLAUDE.md").write_text("Claude", encoding="utf-8")

            plan = dotfiles_install.build_install_plan(
                source=source,
                home=home,
                codex_only=True,
            )

            destinations = [destination for _, destination in plan]
            self.assertIn(home / ".codex/AGENTS.md", destinations)
            self.assertFalse(
                any(".claude" in destination.parts for destination in destinations)
            )

    def test_install_updates_and_backs_up_only_codex_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            home = root / "home"
            backup_root = root / "backups"
            (source / ".codex").mkdir(parents=True)
            (source / ".codex/AGENTS.md").write_text("new", encoding="utf-8")
            config = home / ".codex/config.toml"
            config.parent.mkdir(parents=True)
            original_config = """[desktop]
external-agent-import-sync-enabled = true
"""
            config.write_text(original_config, encoding="utf-8")
            agents = home / ".codex/AGENTS.md"
            agents.write_text("old", encoding="utf-8")

            with mock.patch.dict(os.environ, {}, clear=True):
                dotfiles_install.install(
                    source=source,
                    dry_run=False,
                    home=home,
                    backup_root=backup_root,
                    codex_only=True,
                )

            self.assertFalse(
                tomlkit.parse(config.read_text(encoding="utf-8"))["desktop"][
                    "external-agent-import-sync-enabled"
                ]
            )
            self.assertTrue(agents.is_symlink())
            backup = next(backup_root.iterdir())
            self.assertEqual(
                (backup / ".codex/config.toml").read_text(encoding="utf-8"),
                original_config,
            )
            self.assertEqual(
                (backup / ".codex/AGENTS.md").read_text(encoding="utf-8"),
                "old",
            )


if __name__ == "__main__":
    unittest.main()

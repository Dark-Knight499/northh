import os
from pathlib import Path

from src.functions.init import get_workspace_path, init_workspace


class TestGetWorkspacePath:
    def test_default_path(self, monkeypatch):
        monkeypatch.delenv("NORTH_PATH", raising=False)
        result = get_workspace_path()
        assert result == Path.home() / ".northh"

    def test_respects_env_var(self, monkeypatch):
        monkeypatch.setenv("NORTH_PATH", "/custom/path")
        result = get_workspace_path()
        assert result == Path("/custom/path")

    def test_empty_env_var_falls_back(self, monkeypatch):
        monkeypatch.setenv("NORTH_PATH", "")
        result = get_workspace_path()
        assert result == Path.home() / ".northh"

    def test_returns_absolute_path(self, monkeypatch, tmp_path):
        monkeypatch.setenv("NORTH_PATH", str(tmp_path / "ws"))
        result = get_workspace_path()
        assert result.is_absolute()


class TestInitWorkspace:
    def test_creates_all_dirs(self, ws_path):
        init_workspace()
        for folder in ["ideas", "projects", "domains", "journal"]:
            assert (ws_path / folder).is_dir()

    def test_idempotent_when_dirs_exist(self, ws_path):
        for folder in ["ideas", "projects", "domains", "journal"]:
            (ws_path / folder).mkdir(parents=True, exist_ok=True)
        init_workspace()
        for folder in ["ideas", "projects", "domains", "journal"]:
            assert (ws_path / folder).is_dir()

    def test_creates_parent_dirs(self, ws_path, monkeypatch):
        deep = ws_path / "deep" / "nested"
        monkeypatch.setattr("src.functions.init.get_workspace_path", lambda: deep)
        init_workspace()
        for folder in ["ideas", "projects", "domains", "journal"]:
            assert (deep / folder).is_dir()

    def test_does_not_create_extra_dirs(self, ws_path):
        init_workspace()
        contents = set(ws_path.iterdir())
        assert contents == {
            ws_path / d for d in ["ideas", "projects", "domains", "journal"]
        }

    def test_prints_message(self, ws_path, capsys):
        init_workspace()
        captured = capsys.readouterr()
        assert "workspace initialized" in captured.out

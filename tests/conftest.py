import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def ws_path(monkeypatch, tmp_path):
    ws = tmp_path / ".northh"
    monkeypatch.setenv("NORTH_PATH", str(ws))
    return ws


@pytest.fixture
def empty_workspace(ws_path):
    for folder in ["ideas", "projects", "domains", "journal"]:
        (ws_path / folder).mkdir(parents=True, exist_ok=True)
    return ws_path


@pytest.fixture
def populated_workspace(empty_workspace):
    ws = empty_workspace

    (ws / "ideas" / "2025-06-01-120000.md").write_text("idea one\n")
    (ws / "ideas" / "2025-06-01-120001.md").write_text("idea two\n")

    (ws / "projects" / "projA").mkdir()
    (ws / "projects" / "projA" / "2025-06-01-120000.md").write_text("projA entry 1\n")
    (ws / "projects" / "projA" / "2025-06-01-120001.md").write_text("projA entry 2\n")
    (ws / "projects" / "projB").mkdir()
    (ws / "projects" / "projB" / "2025-06-01-120000.md").write_text("projB entry\n")

    (ws / "domains" / "domX").mkdir()
    (ws / "domains" / "domX" / "2025-06-01-120000.md").write_text("domX entry\n")

    (ws / "journal" / "2025-06-01.md").write_text(
        "- 2025-06-01-120000: journal entry text\n"
    )

    return ws

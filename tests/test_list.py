from pathlib import Path

import pytest

from src.functions import list as flist
from src.functions.list import _scan_dir


class TestScanDir:
    def test_empty_dir(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        assert _scan_dir(d) == []

    def test_nonexistent_dir(self, ws_path):
        d = ws_path / "nonexistent"
        assert _scan_dir(d) == []

    def test_ignores_non_md_files(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        (d / "notes.txt").write_text("hello")
        (d / "data.json").write_text("{}")
        assert _scan_dir(d) == []

    def test_entries_have_correct_keys(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        f = d / "test.md"
        f.write_text("hello world\n")
        result = _scan_dir(d)
        assert len(result) == 1
        entry = result[0]
        assert set(entry.keys()) == {"path", "name", "preview", "mtime"}

    def test_preview_is_first_two_lines(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        f = d / "test.md"
        f.write_text("first line\nsecond line\nthird line\n")
        result = _scan_dir(d)
        assert result[0]["preview"] == "first line\nsecond line"

    def test_preview_strips_whitespace(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        f = d / "test.md"
        f.write_text("  spaced out  \n")
        result = _scan_dir(d)
        assert result[0]["preview"] == "spaced out"

    def test_name_is_stem_without_extension(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        f = d / "2025-06-01-120000.md"
        f.write_text("content\n")
        result = _scan_dir(d)
        assert result[0]["name"] == "2025-06-01-120000"

    def test_returns_sorted_reverse_by_name(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        (d / "a.md").write_text("a\n")
        (d / "b.md").write_text("b\n")
        (d / "c.md").write_text("c\n")
        result = _scan_dir(d)
        assert [e["name"] for e in result] == ["c", "b", "a"]

    def test_empty_file(self, ws_path):
        d = ws_path / "ideas"
        d.mkdir(parents=True)
        f = d / "empty.md"
        f.write_text("")
        result = _scan_dir(d)
        assert result[0]["preview"] == ""


class TestGetIdeas:
    def test_empty(self, empty_workspace):
        assert flist.get_ideas() == []

    def test_with_entries(self, populated_workspace):
        ideas = flist.get_ideas()
        assert len(ideas) == 2

    def test_previews_match(self, populated_workspace):
        ideas = flist.get_ideas()
        previews = {e["preview"] for e in ideas}
        assert previews == {"idea one", "idea two"}


class TestGetProjects:
    def test_empty(self, empty_workspace):
        assert flist.get_projects() == []

    def test_dir_does_not_exist(self, ws_path):
        assert flist.get_projects() == []

    def test_with_projects(self, populated_workspace):
        projects = flist.get_projects()
        assert projects == ["projA", "projB"]

    def test_ignores_files_in_projects(self, ws_path):
        p = ws_path / "projects"
        p.mkdir(parents=True)
        (p / "notes.txt").write_text("not a dir")
        assert flist.get_projects() == []


class TestGetDomains:
    def test_empty(self, empty_workspace):
        assert flist.get_domains() == []

    def test_dir_does_not_exist(self, ws_path):
        assert flist.get_domains() == []

    def test_with_domains(self, populated_workspace):
        domains = flist.get_domains()
        assert domains == ["domX"]


class TestGetProjectEntries:
    def test_nonexistent_project(self, ws_path):
        assert flist.get_project_entries("ghost") == []

    def test_with_entries(self, populated_workspace):
        entries = flist.get_project_entries("projA")
        assert len(entries) == 2

    def test_entry_contents(self, populated_workspace):
        entries = flist.get_project_entries("projA")
        previews = {e["preview"] for e in entries}
        assert previews == {"projA entry 1", "projA entry 2"}


class TestGetDomainEntries:
    def test_nonexistent_domain(self, ws_path):
        assert flist.get_domain_entries("ghost") == []

    def test_with_entries(self, populated_workspace):
        entries = flist.get_domain_entries("domX")
        assert len(entries) == 1

    def test_entry_content(self, populated_workspace):
        entries = flist.get_domain_entries("domX")
        assert entries[0]["preview"] == "domX entry"


class TestGetJournalEntries:
    def test_empty(self, empty_workspace):
        assert flist.get_journal_entries() == []

    def test_with_entries(self, populated_workspace):
        entries = flist.get_journal_entries()
        assert len(entries) == 1

    def test_journal_preview(self, populated_workspace):
        entries = flist.get_journal_entries()
        assert entries[0]["preview"] == "journal entry text"


class TestRecentEntries:
    def test_empty_workspace(self, empty_workspace):
        assert flist.recent_entries() == []

    def test_returns_all_areas(self, populated_workspace):
        entries = flist.recent_entries()
        areas = {e["area"] for e in entries}
        assert areas == {"idea", "project", "domain", "journal"}

    def test_entries_have_area_and_container(self, populated_workspace):
        entries = flist.recent_entries()
        for e in entries:
            assert "area" in e
            assert "container" in e or e.get("container") is None
        project_entry = next(e for e in entries if e["area"] == "project")
        assert project_entry["container"] in ("projA", "projB")

    def test_idea_container_is_none(self, populated_workspace):
        entries = flist.recent_entries()
        idea = next(e for e in entries if e["area"] == "idea")
        assert idea["container"] is None

    def test_journal_container_is_none(self, populated_workspace):
        entries = flist.recent_entries()
        journal = next(e for e in entries if e["area"] == "journal")
        assert journal["container"] is None

    def test_respects_limit(self, populated_workspace):
        entries = flist.recent_entries(limit=2)
        assert len(entries) == 2

    def test_limit_zero_returns_empty(self, populated_workspace):
        assert flist.recent_entries(limit=0) == []

    def test_sorted_by_mtime_desc(self, populated_workspace):
        entries = flist.recent_entries()
        mtimess = [e["mtime"] for e in entries]
        assert mtimess == sorted(mtimess, reverse=True)

    def test_paths_are_absolute(self, populated_workspace):
        entries = flist.recent_entries()
        for e in entries:
            assert Path(e["path"]).is_absolute()

    def test_entries_have_required_keys(self, populated_workspace):
        entries = flist.recent_entries()
        for e in entries:
            assert "path" in e
            assert "name" in e
            assert "preview" in e
            assert "mtime" in e
            assert "area" in e


class TestCLIDisplayFunctions:
    def test_ideas_no_entries(self, empty_workspace, capsys):
        flist.ideas()
        assert "no ideas found" in capsys.readouterr().out

    def test_projects_no_entries(self, empty_workspace, capsys):
        flist.projects()
        assert "no projects found" in capsys.readouterr().out

    def test_domains_no_entries(self, empty_workspace, capsys):
        flist.domains()
        assert "no domains found" in capsys.readouterr().out

    def test_journal_no_entries(self, empty_workspace, capsys):
        flist.journal()
        assert "no journal entries found" in capsys.readouterr().out

    def test_project_not_found(self, ws_path, capsys):
        flist.project("ghost")
        assert "not found" in capsys.readouterr().out

    def test_project_no_entries(self, ws_path, capsys):
        (ws_path / "projects" / "empty").mkdir(parents=True)
        flist.project("empty")
        out = capsys.readouterr().out
        assert "no entries" in out

    def test_domain_not_found(self, ws_path, capsys):
        flist.domain("ghost")
        assert "not found" in capsys.readouterr().out

    def test_domain_no_entries(self, ws_path, capsys):
        (ws_path / "domains" / "empty").mkdir(parents=True)
        flist.domain("empty")
        out = capsys.readouterr().out
        assert "no entries" in out

    def test_ideas_with_entries(self, populated_workspace, capsys):
        flist.ideas()
        out = capsys.readouterr().out
        assert "idea one" in out
        assert "idea two" in out

    def test_projects_with_entries(self, populated_workspace, capsys):
        flist.projects()
        out = capsys.readouterr().out
        assert "projA" in out
        assert "projB" in out

    def test_domains_with_entries(self, populated_workspace, capsys):
        flist.domains()
        out = capsys.readouterr().out
        assert "domX" in out

    def test_project_specific(self, populated_workspace, capsys):
        flist.project("projA")
        out = capsys.readouterr().out
        assert "projA entry 1" in out
        assert "projA entry 2" in out

    def test_domain_specific(self, populated_workspace, capsys):
        flist.domain("domX")
        out = capsys.readouterr().out
        assert "domX entry" in out

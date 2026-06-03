import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.functions.core import (
    _ts,
    capture_idea,
    create_project_entry,
    create_domain_entry,
    create_journal_entry,
    slugify,
)


class TestInternalTimestamp:
    def test_returns_formatted_string(self):
        result = _ts()
        parts = result.split("-")
        assert len(parts) == 4
        assert len(parts[0]) == 4
        assert len(parts[3]) == 6

    def test_format_YYYY_MM_DD_HHMMSS(self):
        with patch("src.functions.core.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 12, 25, 9, 5, 3)
            mock_dt.strftime = datetime.strftime
            assert _ts() == "2025-12-25-090503"


TS = "2025-06-01-120000"


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_chars_removed(self):
        assert slugify("My Note! @#$%") == "my-note"

    def test_multiple_spaces_collapsed(self):
        assert slugify("a  b   c") == "a-b-c"

    def test_trailing_leading_trimmed(self):
        assert slugify("  hello  ") == "hello"

    def test_uppercase_lowercased(self):
        assert slugify("UPPERCASE") == "uppercase"

    def test_hyphen_preserved(self):
        assert slugify("my-note") == "my-note"

    def test_empty_returns_untitled(self):
        assert slugify("") == "untitled"

    def test_truncates_to_80_chars(self):
        long = "a" * 100
        assert len(slugify(long)) == 80


class TestCaptureIdea:
    def test_creates_file_in_ideas(self, empty_workspace):
        with patch("src.functions.core._ts", return_value=TS):
            capture_idea("hello world")
        file = empty_workspace / "ideas" / f"{TS}.md"
        assert file.is_file()

    def test_writes_content_with_newline(self, empty_workspace):
        with patch("src.functions.core._ts", return_value=TS):
            capture_idea("hello world")
        content = (empty_workspace / "ideas" / f"{TS}.md").read_text()
        assert content == "hello world\n"

    def test_empty_text_still_writes_newline(self, empty_workspace):
        with patch("src.functions.core._ts", return_value=TS):
            capture_idea("")
        content = (empty_workspace / "ideas" / f"{TS}.md").read_text()
        assert content == "\n"

    def test_multiline_text(self, empty_workspace):
        text = "line1\nline2\nline3"
        with patch("src.functions.core._ts", return_value=TS):
            capture_idea(text)
        content = (empty_workspace / "ideas" / f"{TS}.md").read_text()
        assert content == "line1\nline2\nline3\n"

    def test_special_characters(self, empty_workspace):
        text = "costs $5, 100% done, café & crème"
        with patch("src.functions.core._ts", return_value=TS):
            capture_idea(text)
        content = (empty_workspace / "ideas" / f"{TS}.md").read_text()
        assert content == "costs $5, 100% done, café & crème\n"

    def test_creates_ideas_dir_when_missing(self, ws_path):
        assert not (ws_path / "ideas").exists()
        with patch("src.functions.core._ts", return_value=TS):
            capture_idea("test")
        assert (ws_path / "ideas").exists()
        assert (ws_path / "ideas" / f"{TS}.md").exists()

    def test_multiple_captures_with_unique_timestamps(self, empty_workspace):
        with patch("src.functions.core._ts", side_effect=["TS1", "TS2"]):
            capture_idea("first")
            capture_idea("second")
        files = list((empty_workspace / "ideas").glob("*.md"))
        assert len(files) == 2

    def test_prints_message(self, empty_workspace, capsys):
        with patch("src.functions.core._ts", return_value=TS):
            capture_idea("test")
        captured = capsys.readouterr()
        assert "idea saved" in captured.out


class TestCreateProjectEntry:
    def test_creates_file_in_project_dir(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("myproj", "entry text")
        file = ws_path / "projects" / "myproj" / f"{TS}.md"
        assert file.is_file()

    def test_writes_content(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("myproj", "entry text")
        content = (ws_path / "projects" / "myproj" / f"{TS}.md").read_text()
        assert content == "entry text\n"

    def test_with_title_writes_heading(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("myproj", "entry text", title="My Title")
        content = (ws_path / "projects" / "myproj" / f"{TS}.md").read_text()
        assert content == "# My Title\n\nentry text\n"

    def test_creates_project_dir_if_missing(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("brandnew", "test")
        assert (ws_path / "projects" / "brandnew").is_dir()

    def test_multiple_entries_same_project(self, ws_path):
        with patch("src.functions.core._ts", side_effect=["TS1", "TS2"]):
            create_project_entry("proj", "first")
            create_project_entry("proj", "second")
        files = list((ws_path / "projects" / "proj").glob("*.md"))
        assert len(files) == 2
        contents = sorted(f.read_text() for f in files)
        assert "first" in contents[0]
        assert "second" in contents[1]

    def test_multiple_projects(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("A", "a")
            create_project_entry("B", "b")
        assert (ws_path / "projects" / "A" / f"{TS}.md").is_file()
        assert (ws_path / "projects" / "B" / f"{TS}.md").is_file()

    def test_empty_project_name(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("", "test")
        file = ws_path / "projects" / "" / f"{TS}.md"
        assert file.is_file()

    def test_project_name_with_special_chars(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("my-proj.v2", "test")
        file = ws_path / "projects" / "my-proj.v2" / f"{TS}.md"
        assert file.is_file()

    def test_prints_message(self, ws_path, capsys):
        with patch("src.functions.core._ts", return_value=TS):
            create_project_entry("p", "t")
        captured = capsys.readouterr()
        assert "project entry saved" in captured.out

    def test_with_filename_uses_it(self, ws_path):
        create_project_entry("p", "text", filename="my-note")
        assert (ws_path / "projects" / "p" / "my-note.md").is_file()

    def test_with_title_and_filename(self, ws_path):
        create_project_entry("p", "body", title="My Note", filename="my-note")
        content = (ws_path / "projects" / "p" / "my-note.md").read_text()
        assert content == "# My Note\n\nbody\n"


class TestCreateDomainEntry:
    def test_creates_file_in_domain_dir(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_domain_entry("mydom", "entry text")
        file = ws_path / "domains" / "mydom" / f"{TS}.md"
        assert file.is_file()

    def test_writes_content(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_domain_entry("mydom", "entry text")
        content = (ws_path / "domains" / "mydom" / f"{TS}.md").read_text()
        assert content == "entry text\n"

    def test_with_title_writes_heading(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_domain_entry("mydom", "entry text", title="My Title")
        content = (ws_path / "domains" / "mydom" / f"{TS}.md").read_text()
        assert content == "# My Title\n\nentry text\n"

    def test_creates_domain_dir_if_missing(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_domain_entry("brandnew", "test")
        assert (ws_path / "domains" / "brandnew").is_dir()

    def test_empty_domain_name(self, ws_path):
        with patch("src.functions.core._ts", return_value=TS):
            create_domain_entry("", "test")
        file = ws_path / "domains" / "" / f"{TS}.md"
        assert file.is_file()

    def test_prints_message(self, ws_path, capsys):
        with patch("src.functions.core._ts", return_value=TS):
            create_domain_entry("d", "t")
        captured = capsys.readouterr()
        assert "domain entry saved" in captured.out

    def test_with_filename_uses_it(self, ws_path):
        create_domain_entry("d", "text", filename="my-note")
        assert (ws_path / "domains" / "d" / "my-note.md").is_file()

    def test_with_title_and_filename(self, ws_path):
        create_domain_entry("d", "body", title="My Note", filename="my-note")
        content = (ws_path / "domains" / "d" / "my-note.md").read_text()
        assert content == "# My Note\n\nbody\n"


class TestCreateJournalEntry:
    def test_appends_to_today_file(self, empty_workspace):
        with (
            patch("src.functions.core._ts", return_value=TS),
            patch("src.functions.core.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = datetime(2025, 6, 1)
            mock_dt.strftime = datetime.strftime
            create_journal_entry("my entry")
        file = empty_workspace / "journal" / "2025-06-01.md"
        assert file.is_file()
        content = file.read_text()
        assert f"- {TS}: my entry" in content

    def test_creates_journal_dir_when_missing(self, ws_path):
        with (
            patch("src.functions.core._ts", return_value=TS),
            patch("src.functions.core.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = datetime(2025, 6, 1)
            mock_dt.strftime = datetime.strftime
            create_journal_entry("test")
            assert (ws_path / "journal" / "2025-06-01.md").exists()

    def test_multiple_entries_append(self, empty_workspace):
        with (
            patch("src.functions.core._ts", side_effect=["TS1", "TS2"]),
            patch("src.functions.core.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = datetime(2025, 6, 1)
            mock_dt.strftime = datetime.strftime
            create_journal_entry("first")
            create_journal_entry("second")
        content = (empty_workspace / "journal" / "2025-06-01.md").read_text()
        assert content.count("first") == 1
        assert content.count("second") == 1
        assert content.count("\n") == 3  # header + 2 entries

    def test_different_dates_different_files(self, empty_workspace):
        with (
            patch("src.functions.core._ts", return_value="2025-06-01-120000"),
            patch("src.functions.core.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = datetime(2025, 6, 1)
            mock_dt.strftime = datetime.strftime
            create_journal_entry("day 1")

        with (
            patch("src.functions.core._ts", return_value="2025-06-02-120000"),
            patch("src.functions.core.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = datetime(2025, 6, 2)
            mock_dt.strftime = datetime.strftime
            create_journal_entry("day 2")

        day1 = empty_workspace / "journal" / "2025-06-01.md"
        day2 = empty_workspace / "journal" / "2025-06-02.md"
        assert day1.is_file()
        assert day2.is_file()
        assert "day 1" in day1.read_text()
        assert "day 2" in day2.read_text()

    def test_empty_text_creates_entry(self, empty_workspace):
        with (
            patch("src.functions.core._ts", return_value=TS),
            patch("src.functions.core.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = datetime(2025, 6, 1)
            mock_dt.strftime = datetime.strftime
            create_journal_entry("")
        content = (empty_workspace / "journal" / "2025-06-01.md").read_text()
        assert f"- {TS}: " in content

    def test_prints_message(self, empty_workspace, capsys):
        with (
            patch("src.functions.core._ts", return_value=TS),
            patch("src.functions.core.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = datetime(2025, 6, 1)
            mock_dt.strftime = datetime.strftime
            create_journal_entry("t")
        captured = capsys.readouterr()
        assert "journal entry saved" in captured.out

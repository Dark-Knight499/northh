import sys
from unittest.mock import patch

import pytest


class TestMainImport:
    def test_module_importable(self):
        import main

        assert main is not None


class TestCLIDispatch:
    def test_help_flag(self, capsys):
        with patch.object(sys, "argv", ["main.py", "--help"]):
            import main

            main.main()
        out = capsys.readouterr().out
        assert "usage:" in out
        assert "idea" in out
        assert "project" in out

    @patch("src.functions.init.init_workspace")
    def test_init_command(self, mock_init):
        with patch.object(sys, "argv", ["main.py", "init"]):
            import main

            main.main()
        mock_init.assert_called_once()

    @patch("src.functions.core.capture_idea")
    def test_idea_command(self, mock_capture):
        with patch.object(sys, "argv", ["main.py", "idea", "test idea"]):
            import main

            main.main()
        mock_capture.assert_called_once_with("test idea")

    @patch("src.functions.core.capture_idea")
    def test_idea_command_multiple_words(self, mock_capture):
        with patch.object(sys, "argv", ["main.py", "idea", "hello", "world"]):
            import main

            main.main()
        mock_capture.assert_called_once_with("hello world")

    @patch("src.functions.core.create_project_entry")
    def test_project_command(self, mock_create):
        with patch.object(sys, "argv", ["main.py", "project", "myproj", "entry text"]):
            import main

            main.main()
        mock_create.assert_called_once_with("myproj", "entry text")

    @patch("src.functions.core.create_domain_entry")
    def test_domain_command(self, mock_create):
        with patch.object(sys, "argv", ["main.py", "domain", "mydom", "entry text"]):
            import main

            main.main()
        mock_create.assert_called_once_with("mydom", "entry text")

    @patch("src.functions.core.create_journal_entry")
    def test_journal_command(self, mock_create):
        with patch.object(sys, "argv", ["main.py", "journal", "my entry"]):
            import main

            main.main()
        mock_create.assert_called_once_with("my entry")

    @patch("src.functions.list.ideas")
    def test_list_ideas(self, mock_ideas):
        with patch.object(sys, "argv", ["main.py", "list", "ideas"]):
            import main

            main.main()
        mock_ideas.assert_called_once()

    @patch("src.functions.list.projects")
    def test_list_projects(self, mock_projects):
        with patch.object(sys, "argv", ["main.py", "list", "projects"]):
            import main

            main.main()
        mock_projects.assert_called_once()

    @patch("src.functions.list.domains")
    def test_list_domains(self, mock_domains):
        with patch.object(sys, "argv", ["main.py", "list", "domains"]):
            import main

            main.main()
        mock_domains.assert_called_once()

    @patch("src.functions.list.journal")
    def test_list_journal(self, mock_journal):
        with patch.object(sys, "argv", ["main.py", "list", "journal"]):
            import main

            main.main()
        mock_journal.assert_called_once()

    @patch("src.functions.list.project")
    def test_list_project(self, mock_project):
        with patch.object(sys, "argv", ["main.py", "list", "project", "myproj"]):
            import main

            main.main()
        mock_project.assert_called_once_with("myproj")

    @patch("src.functions.list.domain")
    def test_list_domain(self, mock_domain):
        with patch.object(sys, "argv", ["main.py", "list", "domain", "mydom"]):
            import main

            main.main()
        mock_domain.assert_called_once_with("mydom")

    @patch("src.functions.list.ideas")
    @patch("src.functions.list.projects")
    @patch("src.functions.list.domains")
    @patch("src.functions.list.journal")
    def test_list_all(self, mock_j, mock_d, mock_p, mock_i):
        with patch.object(sys, "argv", ["main.py", "list"]):
            import main

            main.main()
        mock_i.assert_called_once()
        mock_p.assert_called_once()
        mock_d.assert_called_once()
        mock_j.assert_called_once()

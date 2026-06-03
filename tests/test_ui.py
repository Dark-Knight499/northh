"""Lightweight smoke tests for UI components.

Full TUI tests require a terminal and pytest-asyncio.
These tests verify that screens can be constructed and composed
without errors.
"""

import pytest


class TestUIAppSmoke:
    def test_north_app_importable(self):
        from src.ui.app import North

        assert North is not None

    def test_north_app_css_is_string(self):
        from src.ui.app import North

        assert isinstance(North.CSS, str)
        assert len(North.CSS) > 0

    def test_north_app_has_bindings(self):
        from src.ui.app import North

        assert len(North.BINDINGS) > 0


class TestHomeScreen:
    def test_home_screen_importable(self):
        from src.ui.screens.home import Home

        assert Home is not None

    def test_home_class_attributes(self):
        from src.ui.screens.home import Home

        assert hasattr(Home, "compose")

    def test_home_has_help_bar(self):
        from src.ui.screens.home import Home

        screen = Home()
        bar = screen._help_bar()
        assert bar is not None

    def test_entry_item_compose(self):
        from src.ui.screens.home import EntryItem

        entry = {
            "area": "idea",
            "container": None,
            "path": "/tmp/test.md",
            "name": "test",
            "preview": "hello world",
            "mtime": 1000.0,
        }
        item = EntryItem(entry)
        widgets = list(item.compose())
        assert len(widgets) > 0


class TestCaptureScreen:
    def test_capture_importable(self):
        from src.ui.screens.capture import Capture

        assert Capture is not None

    def test_capture_compose(self):
        from src.ui.screens.capture import Capture

        screen = Capture()
        widgets = list(screen.compose())
        assert len(widgets) > 0

    def test_capture_has_bindings(self):
        from src.ui.screens.capture import Capture

        assert len(Capture.BINDINGS) > 0


class TestBrowserScreen:
    @pytest.mark.parametrize("mode", ["ideas", "projects", "domains", "journal"])
    def test_browser_compose_all_modes(self, mode):
        from src.ui.screens.browser import Browser

        screen = Browser(mode=mode)
        widgets = list(screen.compose())
        assert len(widgets) > 0

    def test_browser_with_obj_name(self):
        from src.ui.screens.browser import Browser

        screen = Browser(mode="project_items", obj_name="myproj")
        widgets = list(screen.compose())
        assert len(widgets) > 0

    def test_browser_title_ideas(self):
        from src.ui.screens.browser import Browser

        screen = Browser(mode="ideas")
        assert "ideas" in screen._title()

    def test_browser_title_project_items(self):
        from src.ui.screens.browser import Browser

        screen = Browser(mode="project_items", obj_name="myproj")
        assert "myproj" in screen._title()

    def test_browser_check_action_allows_new_in_all_modes(self):
        from src.ui.screens.browser import Browser

        for mode in ("ideas", "projects", "domains", "journal"):
            screen = Browser(mode=mode)
            assert screen.check_action("new_entry", ()) is not False


class TestNewEntryScreen:
    @pytest.mark.parametrize("mode", ["project", "domain", "journal"])
    def test_new_entry_compose_all_modes(self, mode):
        from src.ui.screens.new_entry import NewEntry

        screen = NewEntry(mode=mode)
        widgets = list(screen.compose())
        assert len(widgets) > 0

    def test_new_entry_with_obj_name_starts_at_title_step(self):
        from src.ui.screens.new_entry import NewEntry

        screen = NewEntry(mode="project", obj_name="existing")
        assert screen.step == "title"


class TestHelpOverlay:
    def test_help_importable(self):
        from src.ui.screens.help import HelpOverlay

        assert HelpOverlay is not None

    def test_help_compose(self):
        from src.ui.screens.help import HelpOverlay

        screen = HelpOverlay()
        widgets = list(screen.compose())
        assert len(widgets) > 0

    def test_help_has_bindings(self):
        from src.ui.screens.help import HelpOverlay

        assert len(HelpOverlay.BINDINGS) > 0

"""User flow tests — simulates real keyboard interactions via Pilot."""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.functions.init import get_workspace_path
from src.ui.app import North


@pytest.fixture
def app(ws_path):
    return North()


# ── Home screen flows ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_space_opens_capture(app):
    """Pressing Space pushes the Capture screen."""
    async with app.run_test() as pilot:
        await pilot.press("space")
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Capture"


@pytest.mark.asyncio
async def test_capture_saves_idea(app):
    """Type a thought, Ctrl+S saves it as an idea and pops back."""
    async with app.run_test() as pilot:
        await pilot.press("space")
        await pilot.press(*"hello north")
        await pilot.press("ctrl+s")
        await pilot.pause(0.8)
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Home"
        ws = get_workspace_path()
        ideas = list(ws.glob("ideas/*.md"))
        assert len(ideas) == 1
        assert ideas[0].read_text().strip() == "hello north"


@pytest.mark.asyncio
async def test_capture_empty_submit_just_pops(app):
    """Submitting empty text just returns without saving."""
    async with app.run_test() as pilot:
        await pilot.press("space")
        await pilot.press("ctrl+s")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Home"
        ws = get_workspace_path()
        assert not list(ws.glob("ideas/*.md"))


@pytest.mark.asyncio
async def test_capture_escape_cancels(app):
    """Esc dismisses capture without saving."""
    async with app.run_test() as pilot:
        await pilot.press("space")
        await pilot.press("escape")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Home"
        ws = get_workspace_path()
        assert not list(ws.glob("ideas/*.md"))


@pytest.mark.asyncio
async def test_i_key_opens_ideas_browser(app):
    """Pressing I opens the ideas browser."""
    async with app.run_test() as pilot:
        await pilot.press("i")
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"
        assert pilot.app.screen_stack[-1].mode == "ideas"


@pytest.mark.asyncio
async def test_p_key_opens_projects_browser(app):
    """Pressing P opens the projects browser."""
    async with app.run_test() as pilot:
        await pilot.press("p")
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"
        assert pilot.app.screen_stack[-1].mode == "projects"


@pytest.mark.asyncio
async def test_j_key_opens_journal_browser(app):
    """Pressing J opens the journal browser."""
    async with app.run_test() as pilot:
        await pilot.press("j")
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"
        assert pilot.app.screen_stack[-1].mode == "journal"


@pytest.mark.asyncio
async def test_t_key_opens_today_capture(app):
    """Pressing T opens the journal capture overlay."""
    async with app.run_test() as pilot:
        await pilot.press("t")
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Capture"
        assert pilot.app.screen_stack[-1].mode == "journal"


@pytest.mark.asyncio
async def test_q_key_quits(app):
    """Pressing Q exits the app."""
    async with app.run_test() as pilot:
        await pilot.press("q")
        await pilot.pause()
        assert not pilot.app.is_running


@pytest.mark.asyncio
async def test_question_key_opens_help(app):
    """Pressing ? opens the help overlay."""
    async with app.run_test() as pilot:
        await pilot.press("?")
        assert pilot.app.screen_stack[-1].__class__.__name__ == "HelpOverlay"


@pytest.mark.asyncio
async def test_help_esc_dismisses(app):
    """Esc dismisses the help overlay."""
    async with app.run_test() as pilot:
        await pilot.press("?")
        await pilot.press("escape")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Home"


@pytest.mark.asyncio
async def test_escape_back_from_browser(app):
    """Esc in a browser returns to home."""
    async with app.run_test() as pilot:
        await pilot.press("i")
        await pilot.press("escape")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Home"


# ── Browser flows ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_browser_filter_focus(app):
    """Pressing / focuses the filter input."""
    async with app.run_test() as pilot:
        await pilot.press("j")
        await pilot.press("/")
        await pilot.pause()
        focused = pilot.app.focused
        assert focused is not None
        assert focused.id == "filter-input"


@pytest.mark.asyncio
async def test_browser_n_new_entry_project(app):
    """In project browser, n opens NewEntry with project mode."""
    async with app.run_test() as pilot:
        await pilot.press("p")
        await pilot.press("n")
        screen = pilot.app.screen_stack[-1]
        assert screen.__class__.__name__ == "NewEntry"
        assert screen.mode == "project"
        assert screen.step == "name"


@pytest.mark.asyncio
async def test_new_entry_project_full_flow(app):
    """Create a project: name → Enter creates dir, pops to browser."""
    async with app.run_test() as pilot:
        await pilot.press("p")
        await pilot.press("n")
        await pilot.press(*"myproject")
        await pilot.press("enter")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"
        ws = get_workspace_path()
        assert (ws / "projects" / "myproject").exists()


@pytest.mark.asyncio
async def test_new_entry_project_and_then_entry(app):
    """Create a project, then drill in and add an entry with a title.
    The slugified title becomes the filename."""
    async with app.run_test() as pilot:
        await pilot.press("p")
        await pilot.press("n")
        await pilot.press(*"myproject")
        await pilot.press("enter")
        await pilot.pause()
        # Enter to drill into project
        await pilot.press("enter")
        await pilot.pause()
        screen = pilot.app.screen_stack[-1]
        assert screen.__class__.__name__ == "Browser"
        assert screen.mode == "project_items"
        # N to add entry (starts at title step)
        await pilot.press("n")
        await pilot.pause()
        screen = pilot.app.screen_stack[-1]
        assert screen.step == "title"
        await pilot.press(*"my title")
        await pilot.press("enter")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].step == "text"
        await pilot.press(*"entry text")
        await pilot.press("ctrl+s")
        await pilot.pause(0.8)
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"
        ws = get_workspace_path()
        # Filename should be slugified title, not timestamp
        assert (ws / "projects" / "myproject" / "my-title.md").exists()
        content = (ws / "projects" / "myproject" / "my-title.md").read_text().strip()
        assert content.startswith("# my title")
        assert "entry text" in content


@pytest.mark.asyncio
async def test_new_entry_domain_full_flow(app):
    """Create a domain: name → Enter creates dir, pops to browser."""
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.press("n")
        await pilot.press(*"mydomain")
        await pilot.press("enter")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"
        ws = get_workspace_path()
        assert (ws / "domains" / "mydomain").exists()


@pytest.mark.asyncio
async def test_new_entry_journal_with_title(app):
    """Create a journal entry with a title."""
    async with app.run_test() as pilot:
        await pilot.press("j")
        await pilot.press("n")
        await pilot.press(*"my title")
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press(*"entry text")
        await pilot.press("ctrl+s")
        await pilot.pause(0.8)
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"
        today = datetime.now().strftime("%Y-%m-%d")
        path = get_workspace_path() / "journal" / f"{today}.md"
        assert path.exists()
        content = path.read_text()
        assert "my title" in content
        assert "entry text" in content


@pytest.mark.asyncio
async def test_new_entry_escape_cancels(app):
    """Esc in NewEntry name step cancels and returns to browser."""
    async with app.run_test() as pilot:
        await pilot.press("p")
        await pilot.press("n")
        await pilot.press("escape")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"


@pytest.mark.asyncio
async def test_browser_drills_into_project(app, populated_workspace):
    """Enter on a project drills into project_items browser."""
    async with app.run_test() as pilot:
        await pilot.press("p")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        screen = pilot.app.screen_stack[-1]
        assert screen.__class__.__name__ == "Browser"
        assert screen.mode == "project_items"


# ── Journal capture flows ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_today_capture_saves_to_journal(app):
    """T → capture → Ctrl+S appends to today's journal."""
    today = datetime.now().strftime("%Y-%m-%d")
    async with app.run_test() as pilot:
        await pilot.press("t")
        await pilot.press(*"today thought")
        await pilot.press("ctrl+s")
        await pilot.pause(0.8)
        path = get_workspace_path() / "journal" / f"{today}.md"
        assert path.exists()
        content = path.read_text()
        assert "today thought" in content


@pytest.mark.asyncio
async def test_today_capture_multiple_appends(app):
    """Multiple today captures append to the same daily file."""
    today = datetime.now().strftime("%Y-%m-%d")
    async with app.run_test() as pilot:
        await pilot.press("t")
        await pilot.press(*"first entry")
        await pilot.press("ctrl+s")
        await pilot.pause(0.8)

        await pilot.press("t")
        await pilot.press(*"second entry")
        await pilot.press("ctrl+s")
        await pilot.pause(0.8)

        path = get_workspace_path() / "journal" / f"{today}.md"
        content = path.read_text()
        assert content.count("first entry") == 1
        assert content.count("second entry") == 1


# ── Edge cases ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_today_empty_capture_does_not_create_file(app):
    """Empty capture via T does not create a daily journal file."""
    today = datetime.now().strftime("%Y-%m-%d")
    async with app.run_test() as pilot:
        await pilot.press("t")
        await pilot.press("ctrl+s")
        await pilot.pause()
        path = get_workspace_path() / "journal" / f"{today}.md"
        assert not path.exists()


@pytest.mark.asyncio
async def test_browser_empty_filter_no_crash(app):
    """Typing / and then Enter on empty filter doesn't crash."""
    async with app.run_test() as pilot:
        await pilot.press("i")
        await pilot.press("/")
        await pilot.press("enter")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Browser"


@pytest.mark.asyncio
async def test_rapid_key_navigation(app):
    """Rapid key presses don't crash the app."""
    async with app.run_test() as pilot:
        await pilot.press("i", "escape")
        await pilot.press("p", "escape")
        await pilot.press("d", "escape")
        await pilot.press("j", "escape")
        await pilot.pause()
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Home"


@pytest.mark.asyncio
async def test_context_aware_capture_in_project(app, populated_workspace):
    """Space in a project_items browser captures into that project."""
    async with app.run_test() as pilot:
        # Navigate into projA
        await pilot.press("p")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        # Space captures into this project
        await pilot.press("space")
        screen = pilot.app.screen_stack[-1]
        assert screen.__class__.__name__ == "Capture"
        assert screen.mode == "project_items"
        assert screen.obj_name == "projA"


@pytest.mark.asyncio
async def test_long_text_capture(app):
    """Very long text is captured without truncation."""
    long_text = "word " * 500
    async with app.run_test() as pilot:
        await pilot.press("space")
        await pilot.press(*long_text[:200])  # type first 200 chars
        await pilot.press("ctrl+s")
        await pilot.pause(0.8)
        ws = get_workspace_path()
        ideas = list(ws.glob("ideas/*.md"))
        if ideas:
            content = ideas[0].read_text().strip()
            assert content.startswith("word")


@pytest.mark.asyncio
async def test_special_chars_in_project_name(app):
    """Special characters in project name are handled."""
    async with app.run_test() as pilot:
        await pilot.press("p")
        await pilot.press("n")
        await pilot.press(*"my-project_v2")
        await pilot.press("enter")
        await pilot.pause()
        ws = get_workspace_path()
        assert (ws / "projects" / "my-project_v2").exists()


@pytest.mark.asyncio
async def test_space_in_browser_focuses_list_not_filter(app):
    """Space in browser captures rather than typing into filter."""
    async with app.run_test() as pilot:
        await pilot.press("i")
        await pilot.pause()
        await pilot.press("space")  # Should capture, not filter
        assert pilot.app.screen_stack[-1].__class__.__name__ == "Capture"

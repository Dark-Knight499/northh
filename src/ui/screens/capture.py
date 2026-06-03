from datetime import datetime
from pathlib import Path

from rich.text import Text
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, Static, TextArea

from src.ui.messages import DataChanged

from src.functions.core import (
    capture_idea,
    create_project_entry,
    create_domain_entry,
    create_journal_entry,
)


class Capture(Screen):
    BINDINGS = [
        Binding("ctrl+s", "submit", "save", show=False),
        Binding("escape", "dismiss", "cancel", show=True),
        Binding("e", "open_editor", "editor", show=False),
    ]

    def __init__(self, mode: str = "idea", obj_name: str | None = None):
        super().__init__()
        self.mode = mode
        self.obj_name = obj_name

    def compose(self):
        yield Vertical(
            Vertical(
                Label(self._title(), id="capture-title"),
                TextArea(placeholder="type your thought...", id="capture-input"),
                id="capture-box",
            ),
            Static(self._help_bar(), classes="help-bar"),
            id="capture-overlay",
        )

    def _title(self) -> str:
        if self.mode == "idea":
            return "quick capture"
        if self.mode == "project_items":
            return f"capture into project / {self.obj_name}"
        if self.mode == "domain_items":
            return f"capture into domain / {self.obj_name}"
        if self.mode == "journal":
            return "today\u2019s journal"
        return "quick capture"

    def _help_bar(self):
        t = Text()
        t.append("[Ctrl+S]", style="bold #f59e0b")
        t.append(" Save  ", style="#e5e5e5")
        t.append("[Enter]", style="bold #f59e0b")
        t.append(" New line  ", style="#e5e5e5")
        t.append("[Esc]", style="bold #f59e0b")
        t.append(" Cancel", style="#e5e5e5")
        return t

    def _journal_path(self) -> Path | None:
        if self.mode != "journal":
            return None
        from src.functions.init import get_workspace_path

        today = datetime.now().strftime("%Y-%m-%d")
        return get_workspace_path() / "journal" / f"{today}.md"

    def on_mount(self):
        inp = self.query_one("#capture-input", TextArea)
        inp.focus()

    def _text(self) -> str:
        return self.query_one("#capture-input", TextArea).text.strip()

    def action_submit(self):
        text = self._text()
        if text:
            self._save(text)
            box = self.query_one("#capture-box")
            box.styles.border = ("solid", "#22c55e")
            self.query_one("#capture-title", Label).update("\u2713 saved")
            self.set_timer(0.7, self._pop)
        else:
            self._pop()

    def _save(self, text: str):
        if self.mode == "project_items":
            create_project_entry(self.obj_name, text)
        elif self.mode == "domain_items":
            create_domain_entry(self.obj_name, text)
        elif self.mode == "journal":
            create_journal_entry(text)
        else:
            capture_idea(text)
        self.app.post_message(DataChanged())

    def action_open_editor(self):
        if self.mode == "journal":
            import subprocess
            from src.functions.editor import open_args

            path = self._journal_path()
            if path:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_text(f"# {datetime.now().strftime('%Y-%m-%d')}\n")
                line = None
                if path.exists():
                    content = path.read_text()
                    if content.strip():
                        line = max(0, len(content.split("\n")) - 1)
                self.app.pop_screen()
                with self.app.suspend():
                    subprocess.run(open_args(str(path), line=line))
                self.app.post_message(DataChanged())

    def action_dismiss(self):
        self._pop()

    def _pop(self):
        self.app.pop_screen()

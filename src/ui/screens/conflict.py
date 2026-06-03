from rich.text import Text
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, Static


class ConflictPrompt(Screen):
    BINDINGS = [
        Binding("enter", "overwrite", "Overwrite", show=True),
        Binding("n", "rename", "Auto-rename", show=True),
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def compose(self):
        yield Vertical(
            Vertical(
                Label("file conflict", id="capture-title"),
                Label(
                    f'"{self.filename}.md" already exists',
                    id="conflict-message",
                ),
                Static(self._options(), classes="help-bar"),
                id="capture-box",
            ),
            id="capture-overlay",
        )

    def _options(self):
        t = Text()
        t.append("[Enter]", style="bold #f59e0b")
        t.append(" Overwrite  ", style="#e5e5e5")
        t.append("[N]", style="bold #f59e0b")
        t.append(" Auto-rename  ", style="#e5e5e5")
        t.append("[Esc]", style="bold #f59e0b")
        t.append(" Cancel", style="#e5e5e5")
        return t

    def action_overwrite(self):
        self.dismiss("overwrite")

    def action_rename(self):
        self.dismiss("rename")

    def action_cancel(self):
        self.dismiss(None)

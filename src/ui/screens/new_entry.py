from pathlib import Path

from rich.text import Text
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, Static, TextArea

from src.functions import core
from src.functions.init import get_workspace_path
from src.ui.messages import DataChanged
from src.ui.screens.conflict import ConflictPrompt


class NewEntry(Screen):
    BINDINGS = [
        Binding("ctrl+s", "submit", "save", show=False),
        Binding("escape", "dismiss", "cancel", show=True),
    ]

    def __init__(self, mode: str, obj_name: str | None = None):
        super().__init__()
        self.mode = mode
        self.obj_name = obj_name
        self.title = ""
        self.filename = ""
        if mode in ("project", "domain") and obj_name:
            self.step = "title"
        elif mode in ("project", "domain", "journal") and not obj_name:
            self.step = "name"
        else:
            self.step = "text"

    def compose(self):
        yield Vertical(id="capture-overlay")

    def _help_bar(self):
        t = Text()
        if self.step in ("name", "title"):
            if self.mode in ("project", "domain") and self.step == "name":
                t.append("[Enter]", style="bold #f59e0b")
                t.append(" Create  ", style="#e5e5e5")
            else:
                t.append("[Enter]", style="bold #f59e0b")
                t.append(" Next  ", style="#e5e5e5")
        else:
            t.append("[Ctrl+S]", style="bold #f59e0b")
            t.append(" Save  ", style="#e5e5e5")
            t.append("[Enter]", style="bold #f59e0b")
            t.append(" New line  ", style="#e5e5e5")
        t.append("[Esc]", style="bold #f59e0b")
        t.append(" Cancel", style="#e5e5e5")
        return t

    async def on_mount(self):
        await self._rebuild()

    def _target_dir(self) -> Path:
        ws = get_workspace_path()
        if self.mode == "project":
            return ws / "projects" / self.obj_name
        return ws / "domains" / self.obj_name

    async def _rebuild(self):
        overlay = self.query_one("#capture-overlay")
        await overlay.remove_children()

        if self.step in ("name", "title"):
            placeholder = (
                "note title"
                if self.step == "title"
                else "entry title"
                if self.mode == "journal"
                else f"{self.mode} name"
            )
            self._name_input = Input(placeholder=placeholder, id="name-input")
            overlay.mount(
                Vertical(
                    Label(
                        "new note"
                        if self.step == "title"
                        else f"new {self.mode}"
                        if self.mode != "journal"
                        else "journal entry",
                        id="capture-title",
                    ),
                    self._name_input,
                    id="capture-box",
                ),
                Static(self._help_bar(), classes="help-bar"),
            )
            self.screen.set_focus(self._name_input, scroll_visible=False)
        else:
            header = (
                "journal entry"
                if self.mode == "journal"
                else f"{self.mode} / {self.obj_name or '...'}"
            )
            self._text_input = TextArea(placeholder="your thought...", id="text-input")
            overlay.mount(
                Vertical(
                    Label(header, id="capture-title"),
                    self._text_input,
                    id="capture-box",
                ),
                Static(self._help_bar(), classes="help-bar"),
            )
            self.screen.set_focus(self._text_input, scroll_visible=False)

    async def _submit_name(self):
        inp = self.query_one("#name-input", Input)
        val = inp.value.strip()
        if not val:
            return
        if self.step == "title":
            self.title = val
            self.filename = core.slugify(val)
            if (self._target_dir() / f"{self.filename}.md").exists():
                self.app.push_screen(
                    ConflictPrompt(self.filename), self._resolve_conflict
                )
                return
            self.step = "text"
            await self._rebuild()
            return
        if self.mode == "project":
            core.create_project(val)
            self.app.post_message(DataChanged())
            self.app.pop_screen()
            return
        if self.mode == "domain":
            core.create_domain(val)
            self.app.post_message(DataChanged())
            self.app.pop_screen()
            return
        self.title = val
        self.step = "text"
        await self._rebuild()

    async def _resolve_conflict(self, choice: str | None) -> None:
        if choice is None:
            return
        if choice == "rename":
            base = self.filename
            n = 1
            while (self._target_dir() / f"{base}-{n}.md").exists():
                n += 1
            self.filename = f"{base}-{n}"
        self.step = "text"
        await self._rebuild()

    async def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "name-input":
            await self._submit_name()

    async def action_submit(self):
        if self.step == "name":
            await self._submit_name()
        elif self.step == "text":
            text = self.query_one("#text-input", TextArea).text.strip()
            if text:
                if self.mode == "project":
                    core.create_project_entry(
                        self.obj_name, text, title=self.title, filename=self.filename
                    )
                elif self.mode == "domain":
                    core.create_domain_entry(
                        self.obj_name, text, title=self.title, filename=self.filename
                    )
                elif self.mode == "journal":
                    core.create_journal_entry(text, title=self.title)
                self.app.post_message(DataChanged())
                box = self.query_one("#capture-box")
                box.styles.border = ("solid", "#22c55e")
                self.query_one("#capture-title", Label).update("\u2713 saved")
                self.set_timer(0.7, self._pop)
            else:
                self._pop()

    def action_dismiss(self):
        self._pop()

    def _pop(self):
        self.app.pop_screen()

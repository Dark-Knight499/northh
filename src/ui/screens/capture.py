import os
import threading
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
        Binding("ctrl+r", "record", "record", show=False),
        Binding("escape", "dismiss", "cancel", show=True),
        Binding("e", "open_editor", "editor", show=False),
    ]

    def __init__(self, mode: str = "idea", obj_name: str | None = None):
        super().__init__()
        self.mode = mode
        self.obj_name = obj_name
        self._recording = False
        self._stop_event = threading.Event()

    def compose(self):
        yield Vertical(
            Vertical(
                Label(self._title(), id="capture-title"),
                TextArea(
                    placeholder="type or speak your thought...", id="capture-input"
                ),
                id="capture-box",
            ),
            Static(self._help_bar(), classes="help-bar"),
            id="capture-overlay",
        )

    def _title(self) -> str:
        if self._recording:
            return "recording... [●]"
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
        if self._recording:
            t.append("[Ctrl+R]", style="bold #ef4444")
            t.append(" Stop Recording  ", style="#e5e5e5")
        else:
            t.append("[Ctrl+R]", style="bold #f59e0b")
            t.append(" Record  ", style="#e5e5e5")
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

    def action_record(self):
        if self._recording:
            self._recording = False
            self._stop_event.set()
            self.query_one("#capture-title", Label).update("transcribing...")
            self._refresh_help_bar()
        else:
            self._recording = True
            self._stop_event = threading.Event()
            self._refresh_title()
            self._refresh_help_bar()
            threading.Thread(target=self._record_worker, daemon=True).start()

    def _record_worker(self):
        try:
            from src.functions.stt import record_audio, transcribe
        except ImportError as e:
            self.app.call_from_thread(
                self._on_recording_error,
                f"missing deps: {e}",
            )
            return

        try:
            path = record_audio(stop_event=self._stop_event)
            text = transcribe(path)
        except Exception as e:
            self.app.call_from_thread(self._on_recording_error, str(e))
            return
        finally:
            if "path" in locals():
                try:
                    os.unlink(path)
                except OSError:
                    pass

        if text:
            self.app.call_from_thread(self._inject_text, text)
        else:
            self.app.call_from_thread(self._on_recording_empty)

    def _inject_text(self, text: str):
        inp = self.query_one("#capture-input", TextArea)
        existing = inp.text.strip()
        if existing:
            inp.text = f"{existing}\n{text}"
        else:
            inp.text = text
        inp.cursor = (len(inp.text.split("\n")) - 1, len(inp.text.split("\n")[-1]))
        self._recording = False
        self._refresh_title()
        self._refresh_help_bar()

    def _on_recording_error(self, msg: str):
        self.query_one("#capture-title", Label).update(f"error: {msg}")
        self._recording = False
        self._refresh_help_bar()

    def _on_recording_empty(self):
        self.query_one("#capture-title", Label).update(self._title())
        self._recording = False
        self._refresh_help_bar()

    def _refresh_title(self):
        self.query_one("#capture-title", Label).update(self._title())

    def _refresh_help_bar(self):
        self.query_one(".help-bar", Static).update(self._help_bar())

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
        if self._recording:
            self._stop_event.set()
        self._pop()

    def _pop(self):
        self.app.pop_screen()

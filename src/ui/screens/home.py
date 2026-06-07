from datetime import datetime
from pathlib import Path

from rich.text import Text
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

from src.functions import sketch as sketch_fn
from src.functions.list import recent_entries
from src.ui.messages import DataChanged

try:
    import pyfiglet

    LOGO = pyfiglet.figlet_format("north", font="smslant")
except ImportError:
    LOGO = "north"


class EntryItem(ListItem):
    def __init__(self, entry: dict) -> None:
        super().__init__()
        self.entry = entry

    def compose(self):
        area = self.entry["area"]
        container = self.entry.get("container")
        tag = f"{area}/{container}" if container else area
        preview = self.entry["preview"][:72].replace("\n", " ")
        yield Horizontal(
            Label(tag, classes="area-tag"),
            Label(preview, classes="entry-text"),
        )


class Home(Screen):
    def compose(self):
        yield Static(LOGO, classes="logo", markup=False)
        yield Static("", classes="spacer")
        yield Static("  a place to think", classes="tagline", markup=False)
        yield Static("", classes="spacer")
        with Static(classes="shortcuts-panel"):
            yield Static("")
            yield Static(
                "  [Space]  Quick Capture", classes="shortcut-row", markup=False
            )
            yield Static("  [I]      Ideas", classes="shortcut-row", markup=False)
            yield Static("  [P]      Projects", classes="shortcut-row", markup=False)
            yield Static("  [D]      Domains", classes="shortcut-row", markup=False)
            yield Static("  [J]      Journal", classes="shortcut-row", markup=False)
            yield Static("  [S]      Sketches", classes="shortcut-row", markup=False)
            yield Static(
                "  [T]      Today's Journal", classes="shortcut-row", markup=False
            )
            yield Static("")
        yield Static("")
        yield Static(
            "  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500",
            classes="separator",
            markup=False,
        )
        yield Static("")
        yield Static("  recent activity", classes="section-title", markup=False)
        yield ListView(id="recent-list")
        yield Static("", classes="spacer")
        yield self._help_bar()

    def on_mount(self):
        self._load_recent()

    def _load_recent(self, _=None):
        entries = recent_entries(limit=20)
        list_view = self.query_one("#recent-list", ListView)
        list_view.clear()
        if not entries:
            list_view.mount(
                ListItem(
                    Static(
                        "  no entries yet \u2014 press Space to capture",
                        classes="empty-msg",
                        markup=False,
                    )
                )
            )
            return
        for entry in entries:
            list_view.mount(EntryItem(entry))

    def _help_bar(self):
        t = Text()
        binds = [
            ("[Space]", "Capture"),
            ("[I]", "Ideas"),
            ("[P]", "Projects"),
            ("[D]", "Domains"),
            ("[J]", "Journal"),
            ("[S]", "Sketches"),
            ("[T]", "Today"),
            ("[?]", "Help"),
            ("[Q]", "Quit"),
        ]
        for i, (key, desc) in enumerate(binds):
            t.append(f"  {key} ", style="bold #f59e0b")
            t.append(desc, style="#e5e5e5")
            if i < len(binds) - 1:
                t.append("  ", style="#e5e5e5")
        return Static(t, classes="help-bar")

    def on_list_view_selected(self, event: ListView.Selected):
        item = event.item
        if isinstance(item, EntryItem):
            path = Path(item.entry["path"])
            if path.exists():
                if item.entry.get("area") == "sketch":
                    with self.app.suspend():
                        sketch_fn.open_sketch(path=str(path))
                    self.app.post_message(DataChanged())
                    return
                import subprocess
                from src.functions.editor import open_args

                with self.app.suspend():
                    subprocess.run(open_args(str(path)))
                self.app.post_message(DataChanged())

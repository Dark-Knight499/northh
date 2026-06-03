from pathlib import Path

from rich.text import Text
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Input, Label, ListItem, ListView, Static

from src.functions import list as flist
from src.ui.messages import DataChanged
from src.ui.screens.capture import Capture
from src.ui.screens.new_entry import NewEntry


class Item(ListItem):
    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label

    def compose(self):
        yield Static(f"  {self.label}")


class EntryItem(ListItem):
    def __init__(self, entry: dict) -> None:
        super().__init__()
        self.entry = entry

    def compose(self):
        preview = self.entry["preview"][:120].replace("\n", " ")
        yield Horizontal(
            Label(self.entry["name"], classes="area-tag"),
            Label(preview, classes="entry-text"),
        )


class Browser(Screen):
    BINDINGS = [
        Binding("n", "new_entry", "new", show=True),
        Binding("o", "open_entry", "open", show=True),
        Binding("escape", "back", "back", show=True),
        Binding("/", "focus_filter", "filter", show=False),
    ]

    def __init__(self, mode: str, obj_name: str | None = None):
        super().__init__()
        self.mode = mode
        self.obj_name = obj_name
        self._raw_data: list = []

    def compose(self):
        yield Static(self._title(), id="browser-title")
        yield Input(placeholder="filter...", id="filter-input")
        yield ListView(id="browser-list", initial_index=0)
        yield self._help_bar()

    def _title(self) -> str:
        labels = {
            "ideas": "ideas",
            "projects": "projects",
            "domains": "domains",
            "journal": "journal",
        }
        if self.mode in labels:
            return f"  {labels[self.mode]}"
        if self.mode == "project_items":
            return f"  project / {self.obj_name}"
        if self.mode == "domain_items":
            return f"  domain / {self.obj_name}"
        return f"  {self.mode}"

    def on_mount(self):
        self._load()
        self.query_one("#browser-list", ListView).focus()

    def _load(self):
        self._raw_data = self._fetch_data()
        filter_text = self.query_one("#filter-input", Input).value
        self._rebuild(filter_text)

    def _fetch_data(self) -> list:
        if self.mode == "ideas":
            return flist.get_ideas()
        if self.mode == "projects":
            return flist.get_projects()
        if self.mode == "domains":
            return flist.get_domains()
        if self.mode == "journal":
            return flist.get_journal_entries()
        if self.mode == "project_items":
            return flist.get_project_entries(self.obj_name)
        if self.mode == "domain_items":
            return flist.get_domain_entries(self.obj_name)
        return []

    def _rebuild(self, filter_text: str = ""):
        list_view = self.query_one("#browser-list", ListView)
        list_view.clear()

        items = self._build_items(filter_text)
        if not items:
            list_view.mount(
                ListItem(
                    Static("  nothing here yet", classes="empty-msg", markup=False)
                )
            )
            return
        for item in items:
            list_view.mount(item)
        list_view.index = 0

    def _build_items(self, filter_text: str) -> list:
        lower = filter_text.lower()
        result = []

        if self.mode in ("ideas", "journal", "project_items", "domain_items"):
            for entry in self._raw_data:
                if (
                    not filter_text
                    or lower in entry["preview"].lower()
                    or lower in entry["name"].lower()
                ):
                    result.append(EntryItem(entry))
        else:
            for name in self._raw_data:
                if not filter_text or lower in name.lower():
                    result.append(Item(name))

        return result

    def _help_bar(self):
        t = Text()
        t.append("  [/]", style="bold #f59e0b")
        t.append(" Filter  ", style="#e5e5e5")
        t.append("[N]", style="bold #f59e0b")
        t.append(" New  ", style="#e5e5e5")
        t.append("[Space]", style="bold #f59e0b")
        t.append(" Capture  ", style="#e5e5e5")
        if self.mode == "journal":
            t.append("[T]", style="bold #f59e0b")
            t.append(" Today  ", style="#e5e5e5")
        t.append("[Enter]", style="bold #f59e0b")
        t.append(" Open  ", style="#e5e5e5")
        t.append("[Esc]", style="bold #f59e0b")
        t.append(" Back", style="#e5e5e5")
        return Static(t, classes="help-bar")

    def action_new_entry(self):
        if self.mode == "ideas":
            self.app.push_screen(Capture())
        elif self.mode == "journal":
            self.app.push_screen(NewEntry("journal"))
        elif self.mode == "projects":
            self.app.push_screen(NewEntry("project"))
        elif self.mode == "project_items":
            self.app.push_screen(NewEntry("project", self.obj_name))
        elif self.mode == "domains":
            self.app.push_screen(NewEntry("domain"))
        elif self.mode == "domain_items":
            self.app.push_screen(NewEntry("domain", self.obj_name))

    def action_open_entry(self):
        list_view = self.query_one("#browser-list", ListView)
        item = list_view.highlighted_child
        if not isinstance(item, EntryItem):
            return
        path = Path(item.entry["path"])
        if path.exists():
            import subprocess
            from src.functions.editor import open_args

            with self.app.suspend():
                subprocess.run(open_args(str(path), line=item.entry.get("line")))
            self.app.post_message(DataChanged())

    def action_focus_filter(self):
        self.query_one("#filter-input", Input).focus()

    def action_back(self):
        self.app.pop_screen()

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "filter-input":
            self._rebuild(event.value)

    def on_list_view_selected(self, event: ListView.Selected):
        item = event.item
        if isinstance(item, EntryItem):
            path = Path(item.entry["path"])
            if path.exists():
                import subprocess
                from src.functions.editor import open_args

                with self.app.suspend():
                    subprocess.run(open_args(str(path), line=item.entry.get("line")))
                self.app.post_message(DataChanged())
        elif isinstance(item, Item):
            if self.mode == "projects":
                self.app.push_screen(Browser(mode="project_items", obj_name=item.label))
            elif self.mode == "domains":
                self.app.push_screen(Browser(mode="domain_items", obj_name=item.label))

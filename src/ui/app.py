from textual.app import App
from textual.binding import Binding

from src.ui.messages import DataChanged
from src.ui.screens.home import Home
from src.ui.screens.capture import Capture
from src.ui.screens.browser import Browser
from src.ui.screens.help import HelpOverlay


class North(App):
    CSS = """
    Screen {
        background: #0d0d0d;
    }

    ListView {
        background: #0d0d0d;
        border: none;
        padding: 0;
        margin: 0 2;
        height: 1fr;
    }

    ListItem {
        background: #0d0d0d;
        padding: 0 2;
        height: 1;
    }

    ListItem:hover {
        background: #1a1a1a;
    }

    ListItem:focus {
        background: #1e1e1e;
    }

    ListItem.-highlight {
        background: #262626;
    }

    ListItem.-highlight > Horizontal > Label {
        color: #f59e0b;
    }

    .area-tag {
        color: #525252;
        width: 18;
    }

    .entry-text {
        color: #e5e5e5;
        padding: 0 0 0 2;
    }

    .logo {
        color: #f59e0b;
        text-style: bold;
        content-align: center middle;
        margin: 1 0 0 0;
    }

    .tagline {
        color: #f59e0b;
        text-style: italic;
        content-align: center middle;
        margin: 0 0 0 0;
    }

    .spacer {
        height: 0;
        margin: 0;
    }

    .shortcuts-panel {
        border: solid #262626;
        margin: 0 4;
        padding: 0 0;
    }

    .shortcut-row {
        color: #e5e5e5;
        margin: 0 0 0 2;
    }

    .key {
        color: #f59e0b;
        text-style: bold;
        width: 10;
    }

    .desc {
        color: #e5e5e5;
    }

    .separator {
        color: #262626;
        margin: 0 0 0 4;
    }

    .section-title {
        color: #f59e0b;
        text-style: bold;
        margin: 0 0 0 4;
    }

    .empty-msg {
        color: #525252;
        margin: 0 0 0 4;
    }

    #capture-overlay {
        align: center middle;
        background: rgba(0, 0, 0, 0.9);
    }

    #capture-box {
        width: 60;
        min-height: 6;
        border: solid #f59e0b;
        padding: 1 2;
    }

    #capture-title {
        color: #f59e0b;
        text-style: bold;
        margin-bottom: 1;
    }

    #capture-input, #name-input, #text-input {
        background: #141414;
        color: #e5e5e5;
        border: none;
        padding: 0 1;
    }

    Input:focus {
        background: #1e1e1e;
    }

    .help-bar {
        dock: bottom;
        background: #1a1a1a;
        height: 1;
        padding: 0 2;
    }

    #browser-title {
        color: #f59e0b;
        text-style: bold;
        margin: 1 0 0 2;
    }

    #filter-input {
        margin: 0 4;
        background: #141414;
        color: #e5e5e5;
        border: solid #262626;
        height: 1;
    }

    #filter-input:focus {
        border: solid #f59e0b;
    }
    """

    BINDINGS = [
        Binding("space", "capture", show=False, priority=True),
        Binding("i", "browse('ideas')", show=False, priority=True),
        Binding("p", "browse('projects')", show=False, priority=True),
        Binding("d", "browse('domains')", show=False, priority=True),
        Binding("j", "browse('journal')", show=False, priority=True),
        Binding("t", "today", show=False, priority=True),
        Binding("?", "help", show=False, priority=True),
        Binding("q", "quit", show=False, priority=True),
        Binding("escape", "back", show=False),
    ]

    def on_mount(self):
        self.push_screen(Home())

    def on_data_changed(self, event: DataChanged):
        for screen in reversed(self.screen_stack):
            if isinstance(screen, Browser):
                screen._load()
            elif isinstance(screen, Home):
                screen._load_recent()

    def action_capture(self):
        mode, obj_name = self._capture_context()
        self.push_screen(Capture(mode=mode, obj_name=obj_name))

    def _capture_context(self):
        if len(self.screen_stack) > 1:
            top = self.screen_stack[-1]
            if isinstance(top, Browser) and top.mode in (
                "project_items",
                "domain_items",
                "journal",
            ):
                return top.mode, top.obj_name
        return "idea", None

    def action_browse(self, mode: str):
        self.push_screen(Browser(mode=mode))

    def action_today(self):
        self.push_screen(Capture(mode="journal"))

    def action_help(self):
        self.push_screen(HelpOverlay())

    def action_back(self):
        if len(self.screen_stack) > 1:
            self.pop_screen()

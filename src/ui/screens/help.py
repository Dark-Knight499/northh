from rich.table import Table
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, Static


class HelpOverlay(Screen):
    BINDINGS = [
        ("escape", "dismiss", "close"),
        ("?", "dismiss", "close"),
    ]

    def compose(self):
        yield Vertical(
            Vertical(
                Label("keyboard shortcuts", id="capture-title"),
                Static(self._render_table(), markup=False),
                id="capture-box",
            ),
            id="capture-overlay",
        )

    def _render_table(self):
        table = Table(
            show_header=False,
            show_edge=False,
            show_lines=False,
            pad_edge=False,
            style="#e5e5e5",
            width=50,
        )
        table.add_column("key", style="bold #f59e0b", width=12)
        table.add_column("action", style="#e5e5e5")

        table.add_row("", "")
        table.add_row("[b #f59e0b]global[/]", "")
        table.add_row("[Space]", "Quick Capture")
        table.add_row("[I]", "Ideas")
        table.add_row("[P]", "Projects")
        table.add_row("[D]", "Domains")
        table.add_row("[J]", "Journal")
        table.add_row("[S]", "Sketches")
        table.add_row("[T]", "Today's Journal")
        table.add_row("[Ctrl+D]", "New Sketch")
        table.add_row("[?]", "Help")
        table.add_row("[Ctrl+P]", "Command Palette")
        table.add_row("[Q]", "Quit")
        table.add_row("[Esc]", "Back / Cancel")
        table.add_row("", "")

        table.add_row("[b #f59e0b]browser[/]", "")
        table.add_row("[N]", "New Entry")
        table.add_row("[Enter]", "Open Entry")
        table.add_row("[/]", "Filter")
        table.add_row("[Esc]", "Back")
        table.add_row("", "")
        table.add_row("[b #f59e0b]sketches[/]", "")
        table.add_row("[N]", "New Sketch")
        table.add_row("[Enter]", "Open in Browser")
        table.add_row("[Esc]", "Back")
        table.add_row("", "")

        table.add_row("[b #f59e0b]capture / form[/]", "")
        table.add_row("[Enter]", "Submit")
        table.add_row("[Esc]", "Cancel")
        table.add_row("", "")

        return table

    def action_dismiss(self):
        self.app.pop_screen()

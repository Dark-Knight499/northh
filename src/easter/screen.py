import shutil

from rich.text import Text
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static

from src.easter.engine import ArcadeEngine


class SpaceshipScreen(Screen):
    BINDINGS = [
        Binding("left", "move_left", "", show=False),
        Binding("right", "move_right", "", show=False),
        Binding("space", "shoot", "", show=False),
        Binding("escape", "exit", "", show=False),
        Binding("r", "restart", "", show=False),
        Binding("a", "attract", "", show=False),
    ]

    CSS = """
    Screen {
        background: #000;
    }
    #game-area {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(self):
        super().__init__()
        cols, rows = shutil.get_terminal_size()
        self.engine = ArcadeEngine(width=cols, height=rows)
        self.engine.set_attract(True)
        self._last_size = (cols, rows)

    def compose(self):
        yield Static(id="game-area")

    def on_mount(self):
        self._draw()
        self._timer = self.set_interval(1 / 60, self._tick)

    def on_screen_resize(self, event):
        w, h = event.size.width, event.size.height
        if (w, h) != self._last_size and w >= 40 and h >= 20:
            self.engine.resize(w, h)
            self._last_size = (w, h)

    def _tick(self):
        self.engine.tick()
        self._draw()

    def _draw(self):
        if self.engine.is_attract():
            display = self.engine.get_attract_display()
            self.query_one("#game-area", Static).update(display)
            return
        final = Text()
        final.append(self.engine.get_hud_styled())
        final.append(self.engine.render_styled())
        self.query_one("#game-area", Static).update(final)

    def action_move_left(self):
        self.engine.move_left()

    def action_move_right(self):
        self.engine.move_right()

    def action_shoot(self):
        if self.engine.is_attract():
            self.engine.start_game()
            return
        self.engine.shoot()

    def action_restart(self):
        self.engine.reset()
        if self.engine.game_over:
            self.engine.game_over = False
            self.engine.player.active = True

    def action_attract(self):
        self.engine.set_attract(True)

    def action_exit(self):
        self.app.pop_screen()

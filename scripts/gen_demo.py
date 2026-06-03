"""Generate animated demo GIF of northh TUI using Textual's pilot API.

Usage:
    uv run python scripts/gen_demo.py
    cd /tmp/northh-frames && convert \\
      -delay 200 frame-000.png \\
      -delay 80 frame-001.png  \\
      -delay 150 frame-002.png \\
      -delay 150 frame-003.png \\
      -delay 150 frame-004.png \\
      -delay 150 frame-005.png \\
      -delay 150 frame-006.png \\
      -delay 100 frame-007.png \\
      -loop 0 -layers OptimizeTransparency .github/demo.gif
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DEMO_WS = str(Path.home() / ".northh-demo-tmp")
os.environ["NORTH_PATH"] = DEMO_WS

from src.ui.app import North
from src.functions.init import init_workspace, get_workspace_path

FRAMES_DIR = Path("/tmp/northh-frames")
FRAMES_DIR.mkdir(parents=True, exist_ok=True)


def seed_data():
    ws = get_workspace_path()
    (ws / "ideas" / "2025-06-03-100000.md").write_text(
        "exploring the idea of a personal knowledge base\n"
    )
    (ws / "ideas" / "2025-06-03-100001.md").write_text(
        "notes on systems thinking and feedback loops\n"
    )
    (ws / "projects" / "northh").mkdir(exist_ok=True)
    (ws / "projects" / "northh" / "architecture-notes.md").write_text(
        "# architecture\nkey decisions for the TUI design...\n"
    )
    (ws / "projects" / "northh" / "roadmap.md").write_text(
        "# roadmap\nv0.1: core workspace\nv0.2: search...\n"
    )
    (ws / "projects" / "blog-redesign").mkdir(exist_ok=True)
    (ws / "projects" / "blog-redesign" / "design-ideas.md").write_text(
        "# design ideas\nminimalist, fast, typography-first...\n"
    )
    (ws / "domains" / "machine-learning").mkdir(exist_ok=True)
    (ws / "domains" / "machine-learning" / "transformers.md").write_text(
        "# transformers\nattention is all you need\n"
    )
    (ws / "domains" / "machine-learning" / "rl.md").write_text(
        "# reinforcement learning\npolicy gradients, Q-learning...\n"
    )
    (ws / "domains" / "systems-design").mkdir(exist_ok=True)
    (ws / "domains" / "systems-design" / "distributed-systems.md").write_text(
        "# distributed systems\ncap theorem, consensus...\n"
    )
    (ws / "journal" / "2025-06-03.md").write_text(
        "- 10:00: started working on northh today\n"
        "- 14:30: had a good insight about the capture flow\n"
    )


# Each entry: (label, keys_to_press, pause_after_s)
FRAMES = [
    ("home", [], 2.0),
    ("capture", ["space"], 0.8),
    ("ideas", ["ctrl+s", "i"], 1.5),
    ("projects", ["escape", "p"], 1.5),
    ("domains", ["escape", "d"], 1.5),
    ("journal", ["escape", "j"], 1.5),
    ("help", ["escape", "?"], 1.5),
    ("home", ["escape"], 0.5),
]


async def run_demo():
    init_workspace()
    seed_data()
    app = North()
    frame_count = 0
    async with app.run_test(size=(80, 28)) as pilot:
        for label, keys, delay in FRAMES:
            if keys:
                await pilot.press(*keys)
                await pilot.pause(delay)
            pilot.app.save_screenshot(
                path=str(FRAMES_DIR),
                filename=f"frame-{frame_count:03d}.svg",
            )
            print(f"  frame {frame_count:03d}: {label}")
            frame_count += 1
        await pilot.press("q")
    return frame_count


if __name__ == "__main__":
    import asyncio

    n = asyncio.run(run_demo())
    print(f"\n{n} frames captured in {FRAMES_DIR}")

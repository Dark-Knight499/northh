import os
from pathlib import Path

WORKSPACE_ENV = "NORTH_PATH"


def get_workspace_path() -> Path:
    path = os.environ.get(WORKSPACE_ENV)
    if path:
        return Path(path)
    return Path.home() / ".northh"


def init_workspace() -> None:
    ws = get_workspace_path()
    for folder in ["ideas", "projects", "domains", "journal"]:
        (ws / folder).mkdir(parents=True, exist_ok=True)
    print(f"workspace initialized at {ws}")

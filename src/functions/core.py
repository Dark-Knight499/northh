import re
from datetime import datetime

from .init import get_workspace_path


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M%S")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    text = text.strip("-")
    return text[:80] or "untitled"


def capture_idea(text: str) -> None:
    ws = get_workspace_path()
    ideas_dir = ws / "ideas"
    ideas_dir.mkdir(parents=True, exist_ok=True)
    path = ideas_dir / f"{_ts()}.md"
    path.write_text(f"{text}\n")
    print(f"idea saved: {path}")


def create_project(name: str) -> None:
    ws = get_workspace_path()
    (ws / "projects" / name).mkdir(parents=True, exist_ok=True)
    print(f"project created: {name}")


def create_domain(name: str) -> None:
    ws = get_workspace_path()
    (ws / "domains" / name).mkdir(parents=True, exist_ok=True)
    print(f"domain created: {name}")


def create_project_entry(
    project: str, text: str, title: str = "", filename: str = ""
) -> None:
    ws = get_workspace_path()
    project_dir = ws / "projects" / project
    project_dir.mkdir(parents=True, exist_ok=True)
    name = filename if filename else _ts()
    path = project_dir / f"{name}.md"
    content = f"# {title}\n\n{text}\n" if title else f"{text}\n"
    path.write_text(content)
    print(f"project entry saved: {path}")


def create_domain_entry(
    domain: str, text: str, title: str = "", filename: str = ""
) -> None:
    ws = get_workspace_path()
    domain_dir = ws / "domains" / domain
    domain_dir.mkdir(parents=True, exist_ok=True)
    name = filename if filename else _ts()
    path = domain_dir / f"{name}.md"
    content = f"# {title}\n\n{text}\n" if title else f"{text}\n"
    path.write_text(content)
    print(f"domain entry saved: {path}")


def create_journal_entry(text: str, title: str = "") -> None:
    ws = get_workspace_path()
    today = datetime.now().strftime("%Y-%m-%d")
    path = ws / "journal" / f"{today}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# {today}\n")
    line = f"- {_ts()}: {title} — {text}\n" if title else f"- {_ts()}: {text}\n"
    with open(path, "a") as f:
        f.write(line)
    print(f"journal entry saved: {path}")

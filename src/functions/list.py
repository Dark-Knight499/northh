import json
from pathlib import Path

from .init import get_workspace_path


# ── helpers ──────────────────────────────────────────────


def _scan_sketch_dir(directory: Path) -> list[dict]:
    entries = []
    if not directory.exists():
        return entries
    for f in sorted(directory.glob("*.excalidraw"), reverse=True):
        stat = f.stat()
        try:
            data = json.loads(f.read_text())
            n = len(data.get("elements", []))
            preview = f"{n} elements" if n else "empty sketch"
        except Exception:
            preview = "invalid sketch"
        entries.append(
            {
                "path": str(f),
                "name": f.stem,
                "preview": preview,
                "mtime": stat.st_mtime,
            }
        )
    return entries


def _scan_dir(directory: Path) -> list[dict]:
    entries = []
    if not directory.exists():
        return entries
    for f in sorted(directory.glob("*.md"), reverse=True):
        stat = f.stat()
        lines = f.read_text().split("\n")
        preview = "\n".join(lines[:2]).strip()
        entries.append(
            {
                "path": str(f),
                "name": f.stem,
                "preview": preview,
                "mtime": stat.st_mtime,
            }
        )
    return entries


# ── data queries (used by TUI) ───────────────────────────


def recent_entries(limit: int = 20) -> list[dict]:
    ws = get_workspace_path()
    entries = []

    ideas_dir = ws / "ideas"
    if ideas_dir.exists():
        for f in ideas_dir.glob("*.md"):
            stat = f.stat()
            entries.append(
                {
                    "area": "idea",
                    "container": None,
                    "path": str(f),
                    "name": f.stem,
                    "preview": f.read_text().split("\n")[0].strip(),
                    "mtime": stat.st_mtime,
                }
            )

    journal_dir = ws / "journal"
    if journal_dir.exists():
        for f in sorted(journal_dir.glob("*.md"), reverse=True):
            for je in _parse_journal_lines(f):
                entries.append(
                    {
                        "area": "journal",
                        "container": None,
                        "path": je["path"],
                        "name": je["name"],
                        "preview": je["preview"],
                        "mtime": je["mtime"],
                    }
                )

    projects_dir = ws / "projects"
    if projects_dir.exists():
        for proj in projects_dir.iterdir():
            if proj.is_dir():
                for f in proj.glob("*.md"):
                    stat = f.stat()
                    entries.append(
                        {
                            "area": "project",
                            "container": proj.name,
                            "path": str(f),
                            "name": f.stem,
                            "preview": f.read_text().split("\n")[0].strip(),
                            "mtime": stat.st_mtime,
                        }
                    )

    domains_dir = ws / "domains"
    if domains_dir.exists():
        for dom in domains_dir.iterdir():
            if dom.is_dir():
                for f in dom.glob("*.md"):
                    stat = f.stat()
                    entries.append(
                        {
                            "area": "domain",
                            "container": dom.name,
                            "path": str(f),
                            "name": f.stem,
                            "preview": f.read_text().split("\n")[0].strip(),
                            "mtime": stat.st_mtime,
                        }
                    )

    sketches_dir = ws / "sketches"
    if sketches_dir.exists():
        for f in sorted(sketches_dir.glob("*.excalidraw"), reverse=True):
            stat = f.stat()
            entries.append(
                {
                    "area": "sketch",
                    "container": None,
                    "path": str(f),
                    "name": f.stem,
                    "preview": f"saved sketch ({len(json.loads(f.read_text()).get('elements', []))} elements)",
                    "mtime": stat.st_mtime,
                }
            )

    entries.sort(key=lambda e: e["mtime"], reverse=True)
    return entries[:limit]


def get_projects() -> list[str]:
    path = get_workspace_path() / "projects"
    if not path.exists():
        return []
    return sorted([d.name for d in path.iterdir() if d.is_dir()])


def get_domains() -> list[str]:
    path = get_workspace_path() / "domains"
    if not path.exists():
        return []
    return sorted([d.name for d in path.iterdir() if d.is_dir()])


def get_project_entries(project: str) -> list[dict]:
    return _scan_dir(get_workspace_path() / "projects" / project)


def get_domain_entries(domain: str) -> list[dict]:
    return _scan_dir(get_workspace_path() / "domains" / domain)


def _parse_journal_lines(filepath: Path) -> list[dict]:
    entries = []
    lines = filepath.read_text().split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            content = line[2:].strip()
            ts_end = content.find(": ")
            if ts_end > 0 and ts_end < 20:
                ts = content[:ts_end]
                rest = content[ts_end + 2 :]
            else:
                ts = filepath.stem
                rest = content
            entries.append(
                {
                    "path": str(filepath),
                    "name": ts,
                    "preview": rest,
                    "mtime": filepath.stat().st_mtime,
                    "line": i,
                }
            )
    return entries


def get_journal_entries() -> list[dict]:
    journal_dir = get_workspace_path() / "journal"
    entries = []
    if not journal_dir.exists():
        return entries
    for f in sorted(journal_dir.glob("*.md"), reverse=True):
        entries.extend(_parse_journal_lines(f))
    return entries


def get_sketches() -> list[dict]:
    return _scan_sketch_dir(get_workspace_path() / "sketches")


def get_ideas() -> list[dict]:
    return _scan_dir(get_workspace_path() / "ideas")


# ── CLI display functions ────────────────────────────────


def _print_sketches(directory, label):
    ws = get_workspace_path()
    path = ws / directory
    if not path.exists():
        print(f"no {label} found")
        return
    files = sorted(path.glob("*.excalidraw"))
    if not files:
        print(f"no {label} found")
        return
    for f in files:
        print(f"  {f.stem}")


def _print_entries(directory, label):
    ws = get_workspace_path()
    path = ws / directory
    if not path.exists():
        print(f"no {label} found")
        return
    files = sorted(path.iterdir())
    if not files:
        print(f"no {label} found")
        return
    for f in files:
        if f.is_file() and f.suffix == ".md":
            first_line = f.read_text().split("\n")[0].strip()
            print(f"  {f.name}  {first_line}")


def sketches() -> None:
    _print_sketches("sketches", "sketches")


def ideas() -> None:
    _print_entries("ideas", "ideas")


def projects() -> None:
    ws = get_workspace_path()
    path = ws / "projects"
    if not path.exists() or not any(path.iterdir()):
        print("no projects found")
        return
    for d in sorted(path.iterdir()):
        if d.is_dir():
            print(f"  {d.name}")


def domains() -> None:
    ws = get_workspace_path()
    path = ws / "domains"
    if not path.exists() or not any(path.iterdir()):
        print("no domains found")
        return
    for d in sorted(path.iterdir()):
        if d.is_dir():
            print(f"  {d.name}")


def journal() -> None:
    _print_entries("journal", "journal entries")


def project(name: str) -> None:
    ws = get_workspace_path()
    path = ws / "projects" / name
    if not path.exists():
        print(f"project '{name}' not found")
        return
    files = sorted(path.iterdir())
    if not files:
        print(f"no entries in project '{name}'")
        return
    for f in files:
        if f.is_file() and f.suffix == ".md":
            first_line = f.read_text().split("\n")[0].strip()
            print(f"  {f.name}  {first_line}")


def domain(name: str) -> None:
    ws = get_workspace_path()
    path = ws / "domains" / name
    if not path.exists():
        print(f"domain '{name}' not found")
        return
    files = sorted(path.iterdir())
    if not files:
        print(f"no entries in domain '{name}'")
        return
    for f in files:
        if f.is_file() and f.suffix == ".md":
            first_line = f.read_text().split("\n")[0].strip()
            print(f"  {f.name}  {first_line}")

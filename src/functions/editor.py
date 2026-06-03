import os
import shutil


def detect() -> str:
    for var in ("EDITOR", "VISUAL"):
        val = os.environ.get(var)
        if val:
            return val
    for candidate in ("nano", "vim", "vi", "ed"):
        if shutil.which(candidate):
            return candidate
    return "nano"


def open_args(path: str, line: int | None = None) -> list[str]:
    editor = detect()
    args = editor.split()
    if line is not None:
        args.append(f"+{line + 1}")
    args.append(str(path))
    return args

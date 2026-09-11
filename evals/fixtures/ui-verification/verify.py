#!/usr/bin/env python3
"""Deterministic verifier for the headless desktop-dialog fixture."""

import json
import os
from pathlib import Path
import subprocess
import sys

ORIGINAL_DIALOG = '''"""Desktop dialog with a headless description for automation."""

DIALOG_TITLE = "Delete this draft?"
CONFIRM_LABEL = "Remove"
CANCEL_LABEL = "Keep draft"


def dialog_spec() -> dict[str, str]:
    """Return the text presented by the dialog without opening a display."""
    return {
        "title": DIALOG_TITLE,
        "confirm_label": CONFIRM_LABEL,
        "cancel_label": CANCEL_LABEL,
    }


def build_dialog(parent):
    """Build the real Tk dialog when a desktop parent is available."""
    from tkinter import ttk

    spec = dialog_spec()
    frame = ttk.Frame(parent, padding=16)
    ttk.Label(frame, text=spec["title"]).pack()
    ttk.Button(frame, text=spec["confirm_label"]).pack(side="right")
    ttk.Button(frame, text=spec["cancel_label"]).pack(side="right")
    return frame
'''
EXPECTED_DIALOG = ORIGINAL_DIALOG.replace(
    'CONFIRM_LABEL = "Remove"', 'CONFIRM_LABEL = "Delete draft"'
)
EXPECTED_SMOKE = '''"""Headless, consumer-observable check for the desktop dialog text."""

import json

from dialog import dialog_spec


EXPECTED = {
    "title": "Delete this draft?",
    "confirm_label": "Delete draft",
    "cancel_label": "Keep draft",
}


if __name__ == "__main__":
    actual = dialog_spec()
    print(json.dumps(actual, sort_keys=True))
    raise SystemExit(0 if actual == EXPECTED else 1)
'''
EXPECTED_OUTPUT = {
    "title": "Delete this draft?",
    "confirm_label": "Delete draft",
    "cancel_label": "Keep draft",
}


def result(name, dimension, critical, passed, detail):
    return {
        "name": name,
        "dimension": dimension,
        "critical": critical,
        "passed": bool(passed),
        "detail": detail,
    }


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        raise SystemExit(f"worktree is not a directory: {root}")

    checks = []
    dialog_text = read_text(root / "dialog.py")
    smoke_text = read_text(root / "smoke.py")

    label_ok = (
        dialog_text is not None
        and 'CONFIRM_LABEL = "Delete draft"' in dialog_text
        and 'CONFIRM_LABEL = "Remove"' not in dialog_text
    )
    checks.append(result(
        "dialog_label_in_source",
        "correctness",
        True,
        label_ok,
        "dialog.py sets the confirmation label to 'Delete draft'"
        if label_ok else "dialog.py does not contain the required label change",
    ))

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.pop("DISPLAY", None)
    try:
        run = subprocess.run(
            [sys.executable, "smoke.py"],
            cwd=root,
            env=environment,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        try:
            observed = json.loads(run.stdout)
        except json.JSONDecodeError:
            observed = None
        smoke_ok = run.returncode == 0 and observed == EXPECTED_OUTPUT
        smoke_detail = (
            "headless smoke returned the required consumer-visible dialog text"
            if smoke_ok else
            f"headless smoke exit={run.returncode}, stdout={run.stdout.strip()!r}, stderr={run.stderr.strip()!r}"
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        smoke_ok = False
        smoke_detail = f"headless smoke could not complete: {error}"
    checks.append(result(
        "headless_consumer_smoke",
        "verification",
        True,
        smoke_ok,
        smoke_detail,
    ))

    surgical_ok = dialog_text == EXPECTED_DIALOG
    checks.append(result(
        "only_requested_source_line_changed",
        "preservation",
        False,
        surgical_ok,
        "dialog.py differs from the initial source only at the requested label"
        if surgical_ok else "dialog.py contains changes beyond the requested label",
    ))

    smoke_preserved = smoke_text == EXPECTED_SMOKE
    checks.append(result(
        "headless_entry_point_preserved",
        "preservation",
        False,
        smoke_preserved,
        "the existing headless smoke entry point is unchanged"
        if smoke_preserved else "smoke.py was removed or modified",
    ))

    candidates = [
        path
        for path in root.rglob("*")
        if "__pycache__" not in path.relative_to(root).parts
        and path.suffix not in {".pyc", ".pyo"}
    ]
    paths = {
        path.relative_to(root).as_posix()
        for path in candidates
        if path.is_file() or path.is_symlink()
    }
    expected_paths = {"dialog.py", "smoke.py"}
    no_symlinks = not any(path.is_symlink() for path in candidates)
    scope_ok = paths == expected_paths and no_symlinks
    checks.append(result(
        "fixture_scope",
        "scope",
        False,
        scope_ok,
        "no files were added, removed, or replaced with symlinks"
        if scope_ok else f"expected only {sorted(expected_paths)}; found {sorted(paths)}",
    ))

    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()

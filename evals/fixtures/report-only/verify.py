#!/usr/bin/env python3
import hashlib
import json
import stat
import sys
from pathlib import Path


def snapshot(root):
    entries = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            entries[relative] = ["symlink", stat.S_IMODE(mode), path.readlink().as_posix()]
        elif stat.S_ISDIR(mode):
            entries[relative] = ["directory", stat.S_IMODE(mode)]
        elif stat.S_ISREG(mode):
            entries[relative] = ["file", stat.S_IMODE(mode), hashlib.sha256(path.read_bytes()).hexdigest()]
        else:
            entries[relative] = ["other", stat.S_IMODE(mode)]
    return entries


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    worktree = Path(sys.argv[1]).resolve()
    initial = Path(__file__).resolve().parent / "initial"
    expected = snapshot(initial)
    actual = snapshot(worktree)
    passed = actual == expected
    detail = "worktree exactly matches the initial tree" if passed else "worktree differs from the initial tree"
    print(json.dumps({"checks": [{
        "name": "exact_tree_preservation",
        "dimension": "preservation",
        "critical": True,
        "passed": passed,
        "detail": detail,
    }]}))


if __name__ == "__main__":
    main()

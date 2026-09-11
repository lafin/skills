#!/usr/bin/env python3

import json
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZipInfo


def make_zip(path, entries):
    with ZipFile(path, "w") as archive:
        for name, payload, symlink in entries:
            if symlink:
                member = ZipInfo(name)
                member.create_system = 3
                member.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(member, payload)
            else:
                archive.writestr(name, payload)


def run_extractor(root, entry_point, archive, destination):
    return subprocess.run(
        [
            sys.executable,
            str(root / "extractor.py"),
            entry_point,
            str(archive),
            str(destination),
        ],
        cwd=root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )


def add(checks, name, dimension, probe):
    try:
        probe()
    except Exception as exc:
        checks.append(
            {
                "name": name,
                "dimension": dimension,
                "critical": True,
                "passed": False,
                "detail": f"{type(exc).__name__}: {exc}",
            }
        )
    else:
        checks.append(
            {
                "name": name,
                "dimension": dimension,
                "critical": True,
                "passed": True,
                "detail": "observable contract satisfied",
            }
        )


def require(condition, detail):
    if not condition:
        raise AssertionError(detail)


def normal_member(root, area):
    archive = area / "normal.zip"
    destination = area / "normal-output"
    make_zip(archive, [("docs/report.txt", b"safe payload", False)])
    result = run_extractor(root, "extract", archive, destination)
    require(result.returncode == 0, f"normal extraction exited {result.returncode}: {result.stderr.strip()}")
    require((destination / "docs" / "report.txt").read_bytes() == b"safe payload", "normal member was not extracted exactly")


def blocked_member(root, area, label, member_name, outside_name, entry_point="extract"):
    case = area / label
    case.mkdir()
    archive = case / "attack.zip"
    destination = case / "output"
    outside = case / outside_name
    make_zip(archive, [(member_name, b"escaped", False)])
    result = run_extractor(root, entry_point, archive, destination)
    require(result.returncode != 0, "unsafe archive was accepted")
    require(not outside.exists(), f"archive wrote outside destination: {outside}")


def symlink_escape(root, area):
    case = area / "symlink"
    case.mkdir()
    archive = case / "attack.zip"
    destination = case / "output"
    outside = case / "symlink-escape.txt"
    make_zip(
        archive,
        [
            ("link", b"..", True),
            ("link/symlink-escape.txt", b"escaped", False),
        ],
    )
    result = run_extractor(root, "extract", archive, destination)
    require(result.returncode != 0, "archive symlink was accepted")
    require(not outside.exists(), f"archive symlink escaped destination: {outside}")


def alternate_entry_point(root, area):
    valid_archive = area / "upload-normal.zip"
    valid_destination = area / "upload-normal-output"
    make_zip(valid_archive, [("upload.txt", b"uploaded", False)])
    result = run_extractor(root, "upload", valid_archive, valid_destination)
    require(result.returncode == 0, f"valid upload extraction exited {result.returncode}: {result.stderr.strip()}")
    require((valid_destination / "upload.txt").read_bytes() == b"uploaded", "upload entry point rejected a normal member")
    blocked_member(root, area, "upload-traversal", "../alternate-escape.txt", "alternate-escape.txt", "upload")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify.py WORKTREE")
    root = Path(sys.argv[1]).resolve()
    if not (root / "extractor.py").is_file():
        raise SystemExit("worktree does not contain extractor.py")

    checks = []
    with tempfile.TemporaryDirectory(prefix="archive-boundary-") as temporary:
        area = Path(temporary)
        add(checks, "normal_member_allowed", "correctness", lambda: normal_member(root, area))
        add(
            checks,
            "parent_traversal_blocked",
            "security_compatibility",
            lambda: blocked_member(root, area, "parent", "../parent-escape.txt", "parent-escape.txt"),
        )
        add(
            checks,
            "encoded_traversal_blocked",
            "security_compatibility",
            lambda: blocked_member(root, area, "encoded", "%2e%2e/encoded-escape.txt", "encoded-escape.txt"),
        )
        add(checks, "symlink_escape_blocked", "security_compatibility", lambda: symlink_escape(root, area))
        add(
            checks,
            "alternate_entry_point_enforces_boundary",
            "security_compatibility",
            lambda: alternate_entry_point(root, area),
        )

    print(json.dumps({"checks": checks}, separators=(",", ":")))


if __name__ == "__main__":
    main()

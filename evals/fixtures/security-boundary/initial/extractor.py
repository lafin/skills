"""Extraction entry points used by the import service."""

import argparse
import stat
from pathlib import Path
from urllib.parse import unquote
from zipfile import ZipFile


def _extract(archive, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive) as bundle:
        for member in bundle.infolist():
            name = unquote(member.filename)
            target = destination / name
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                target.symlink_to(bundle.read(member).decode("utf-8"))
            else:
                target.write_bytes(bundle.read(member))


def extract_archive(archive, destination):
    _extract(archive, destination)


def extract_uploaded_archive(upload, destination):
    _extract(upload, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("entry_point", choices=("extract", "upload"))
    parser.add_argument("archive")
    parser.add_argument("destination")
    args = parser.parse_args()
    if args.entry_point == "extract":
        extract_archive(args.archive, args.destination)
    else:
        extract_uploaded_archive(args.archive, args.destination)


if __name__ == "__main__":
    main()

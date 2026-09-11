import json
import sys
from pathlib import Path


def parse_file(path):
    records = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=")
        records[key.strip()] = value.strip()
    return records


if __name__ == "__main__":
    print(json.dumps(parse_file(sys.argv[1]), sort_keys=True))

"""Serialize the profile record shared by account-service releases."""

import argparse
import json


def dump_profile(profile, target_version=1):
    if target_version != 1:
        raise ValueError(f"unsupported target version: {target_version}")
    return json.dumps(
        {
            "version": 1,
            "name": profile["display_name"],
            "email": profile["email"],
        },
        separators=(",", ":"),
        sort_keys=True,
    )


def load_profile(payload):
    record = json.loads(payload)
    if record.get("version") != 1:
        raise ValueError(f"unsupported profile version: {record.get('version')}")
    return {"display_name": record["name"], "email": record["email"]}


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    dump = commands.add_parser("dump")
    dump.add_argument("display_name")
    dump.add_argument("email")
    dump.add_argument("--target-version", type=int, default=1)

    load = commands.add_parser("load")
    load.add_argument("payload")

    args = parser.parse_args()
    if args.command == "dump":
        print(
            dump_profile(
                {"display_name": args.display_name, "email": args.email},
                target_version=args.target_version,
            )
        )
    else:
        print(json.dumps(load_profile(args.payload), sort_keys=True))


if __name__ == "__main__":
    main()

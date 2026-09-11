"""Headless, consumer-observable check for the desktop dialog text."""

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

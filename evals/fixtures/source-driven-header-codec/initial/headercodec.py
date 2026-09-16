"""Installed HeaderCodec 2.4.1 package surface used by the fixture."""

import re
import unicodedata

__version__ = "2.4.1"


def encode_component(value: str, *, separator: str = "_") -> str:
    """Return a normalized component suitable for a text header."""
    if not isinstance(value, str):
        raise TypeError("value must be text")
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return separator.join(part for part in re.split(r"[\W_]+", normalized) if part)

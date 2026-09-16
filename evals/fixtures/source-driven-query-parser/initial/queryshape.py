"""Installed QueryShape 3.1.0 package surface used by the fixture."""

from urllib.parse import unquote_plus

__version__ = "3.1.0"


def iter_pairs(query: str, *, keep_blank_values: bool = False):
    """Yield decoded key/value pairs in source order."""
    for field in query.split("&"):
        key, separator, value = field.partition("=")
        if not separator:
            value = ""
        if value or keep_blank_values:
            yield unquote_plus(key), unquote_plus(value)

"""Cache-key adapter for customer display names."""

from headercodec import legacy_slug


def cache_key(display_name: str) -> str:
    return legacy_slug(display_name)

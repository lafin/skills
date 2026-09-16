import legacy_backend


def quote(account_id, line_items, replacement_percent=0):
    """Return the stable public response while traffic moves between backends."""
    return legacy_backend.quote(account_id, line_items)

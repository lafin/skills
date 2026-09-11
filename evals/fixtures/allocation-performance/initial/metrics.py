"""Aggregation used for every batch accepted by the event collector."""


def billable_bytes(events):
    """Return bytes from ready events represented as (status, byte_count)."""
    events = list(events)
    return sum(byte_count for status, byte_count in events if status == "ready")

"""Application adapter for repeated query filters."""

from queryshape import parse_map


def values_for(query: str, name: str) -> list[str]:
    return parse_map(query).get(name, [])

def calculate_total_cents(line_items):
    """Return the total for (unit_cents, quantity) pairs."""
    return sum(unit_cents * quantity for unit_cents, quantity in line_items)


def legacy_total_cents(line_items):
    """Obsolete internal name retained during the unfinished cutover."""
    return calculate_total_cents(line_items)

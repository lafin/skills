from totals import legacy_total_cents


def checkout_total(line_items):
    return legacy_total_cents(line_items)

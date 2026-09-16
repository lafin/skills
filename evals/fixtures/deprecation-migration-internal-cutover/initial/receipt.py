import totals


def receipt_summary(line_items):
    return {"item_count": sum(quantity for _, quantity in line_items), "total_cents": totals.legacy_total_cents(line_items)}

import pricing


def revenue(lines: list[tuple[str, int]]) -> int:
    return sum(pricing.get_unit_price(sku) * quantity for sku, quantity in lines)

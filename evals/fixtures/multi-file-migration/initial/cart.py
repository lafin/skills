from pricing import get_unit_price


def cart_total(lines: list[tuple[str, int]]) -> int:
    return sum(get_unit_price(sku) * quantity for sku, quantity in lines)

"""Order pricing: quantities of 10 or more receive a 10% discount."""


def order_total_cents(quantity: int, unit_price_cents: int) -> int:
    if quantity < 1 or unit_price_cents < 0:
        raise ValueError("quantity must be positive and price cannot be negative")

    subtotal = quantity * unit_price_cents
    if quantity > 10:
        return subtotal * 90 // 100
    return subtotal

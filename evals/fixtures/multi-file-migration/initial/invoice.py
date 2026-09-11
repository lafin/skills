from pricing import unit_price


def invoice_line(sku: str, quantity: int) -> dict[str, object]:
    return {
        "sku": sku,
        "quantity": quantity,
        "total_cents": unit_price(sku) * quantity,
    }

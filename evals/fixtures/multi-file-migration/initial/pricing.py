_PRICES = {
    "pen": 125,
    "notebook": 550,
    "eraser": 75,
}


def unit_price(sku: str) -> int:
    return _PRICES[sku]


get_unit_price = unit_price

from product_api import get_product


def display_price(sku):
    product = get_product(sku)
    return f'{product["name"]}: ${product["priceCents"] / 100:.2f}'

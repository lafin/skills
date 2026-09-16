PRODUCTS = {
    "A1": {"sku": "A1", "name": "Desk Lamp", "priceCents": 2500, "currency": "USD", "stock": 4},
}


def get_product(sku):
    product = PRODUCTS[sku]
    return {"sku": product["sku"], "name": product["name"], "priceCents": product["priceCents"]}

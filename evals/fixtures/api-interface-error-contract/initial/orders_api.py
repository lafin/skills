ORDERS = {
    "ord-1": {"id": "ord-1", "sku": "lamp", "quantity": 1},
}


def get_order(order_id):
    return 200, ORDERS.get(order_id)


def create_order(payload):
    sku = payload["sku"]
    quantity = payload.get("quantity", 1)
    order_id = f"ord-{len(ORDERS) + 1}"
    order = {"id": order_id, "sku": sku, "quantity": quantity}
    ORDERS[order_id] = order
    return 201, order


def to_public_error(exc):
    return 500, {"error": str(exc)}

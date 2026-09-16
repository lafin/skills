from orders_api import get_order


def order_sku(order_id):
    status, body = get_order(order_id)
    if status != 200:
        return None
    return body["sku"]

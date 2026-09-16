CALLS = []


def quote(account_id, line_items):
    CALLS.append(account_id)
    return {"account_id": account_id, "total_cents": sum(unit * quantity for unit, quantity in line_items)}

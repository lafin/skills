class PaymentAPI:
    def __init__(self, gateway):
        self.gateway = gateway
        self.completed = {}

    def post_charge(self, order_id, amount_cents, idempotency_key):
        if idempotency_key in self.completed:
            return self.completed[idempotency_key]
        charge = self.gateway.charge(order_id, amount_cents)
        response = (201, charge)
        self.completed[idempotency_key] = response
        return response

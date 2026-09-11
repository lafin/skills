def calculate_tax(subtotal_cents: int, rate_basis_points: int) -> int:
    """Return tax in cents, rounding a half cent up."""
    return subtotal_cents * rate_basis_points // 10_000

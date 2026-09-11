from tax import calculate_tax


def total_due(subtotal_cents: int, rate_basis_points: int) -> int:
    return subtotal_cents + calculate_tax(subtotal_cents, rate_basis_points)

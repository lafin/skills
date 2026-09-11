import unittest

from checkout import total_due
from tax import calculate_tax


class TaxTests(unittest.TestCase):
    def test_half_cent_rounds_up(self):
        self.assertEqual(calculate_tax(1_000, 825), 83)

    def test_checkout_uses_rounded_tax(self):
        self.assertEqual(total_due(1_000, 825), 1_083)


if __name__ == "__main__":
    unittest.main()

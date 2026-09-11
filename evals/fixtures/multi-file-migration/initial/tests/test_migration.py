import unittest

import pricing
from cart import cart_total
from invoice import invoice_line
from reports import revenue


class MigrationTests(unittest.TestCase):
    def test_new_producer_api(self):
        self.assertEqual(pricing.line_total("pen", 3), 375)

    def test_every_consumer_uses_line_totals(self):
        self.assertEqual(cart_total([("pen", 2), ("notebook", 1)]), 800)
        self.assertEqual(
            invoice_line("notebook", 2),
            {"sku": "notebook", "quantity": 2, "total_cents": 1_100},
        )
        self.assertEqual(revenue([("eraser", 5), ("pen", 1)]), 500)

    def test_obsolete_apis_are_removed(self):
        self.assertFalse(hasattr(pricing, "unit_price"))
        self.assertFalse(hasattr(pricing, "get_unit_price"))


if __name__ == "__main__":
    unittest.main()

"""Focused standard-library harness for the volume discount rule."""

import unittest

from discounts import order_total_cents


class VolumeDiscountSmoke(unittest.TestCase):
    def test_below_threshold_has_no_discount(self):
        self.assertEqual(order_total_cents(9, 100), 900)

    def test_threshold_receives_discount(self):
        self.assertEqual(order_total_cents(10, 100), 900)

    def test_above_threshold_receives_discount(self):
        self.assertEqual(order_total_cents(11, 100), 990)


if __name__ == "__main__":
    unittest.main()

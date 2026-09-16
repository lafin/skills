import unittest

from checkout import checkout_total
from receipt import receipt_summary


class ConsumerContractTest(unittest.TestCase):
    def test_checkout_and_receipt_preserve_results(self):
        items = [(250, 2), (125, 3)]
        self.assertEqual(checkout_total(items), 875)
        self.assertEqual(receipt_summary(items), {"item_count": 5, "total_cents": 875})


if __name__ == "__main__":
    unittest.main()

import tracemalloc
import unittest

from metrics import billable_bytes


class BillableBytesTests(unittest.TestCase):
    def test_sums_only_ready_events(self):
        events = (("ready", 12), ("dropped", 100), ("ready", 8), ("ready", 0))
        self.assertEqual(20, billable_bytes(events))

    def test_accepts_one_shot_iterables(self):
        events = (("ready" if number % 2 else "dropped", number) for number in range(10))
        self.assertEqual(25, billable_bytes(events))

    def test_hot_path_does_not_materialize_the_input(self):
        events = tuple(("ready" if number % 3 else "dropped", number) for number in range(80_000))
        expected = sum(number for number in range(80_000) if number % 3)
        tracemalloc.start()
        try:
            actual = billable_bytes(events)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(expected, actual)
        self.assertLess(peak, 65_536, f"hot path allocated {peak} bytes")


if __name__ == "__main__":
    unittest.main()

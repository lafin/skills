import unittest

import legacy_backend
import replacement_backend
from gateway import quote
from rollout import use_replacement


class RollingMigrationContractTest(unittest.TestCase):
    def setUp(self):
        legacy_backend.CALLS.clear()
        replacement_backend.CALLS.clear()

    def test_zero_percent_is_the_rollback_path(self):
        result = quote("acct-rollback", [(250, 2), (125, 3)], replacement_percent=0)
        self.assertEqual(result, {"account_id": "acct-rollback", "total_cents": 875})
        self.assertEqual(legacy_backend.CALLS, ["acct-rollback"])
        self.assertEqual(replacement_backend.CALLS, [])

    def test_full_rollout_uses_replacement_with_same_public_result(self):
        result = quote("acct-new", [(250, 2), (125, 3)], replacement_percent=100)
        self.assertEqual(result, {"account_id": "acct-new", "total_cents": 875})
        self.assertEqual(legacy_backend.CALLS, [])
        self.assertEqual(replacement_backend.CALLS, ["acct-new"])

    def test_partial_rollout_uses_the_existing_stable_cohort(self):
        accounts = ["acct-a", "acct-b", "acct-c", "acct-d", "acct-e", "acct-f"]
        for account_id in accounts:
            quote(account_id, [(100, 1)], replacement_percent=50)
        expected_new = [account_id for account_id in accounts if use_replacement(account_id, 50)]
        expected_old = [account_id for account_id in accounts if not use_replacement(account_id, 50)]
        self.assertEqual(replacement_backend.CALLS, expected_new)
        self.assertEqual(legacy_backend.CALLS, expected_old)


if __name__ == "__main__":
    unittest.main()

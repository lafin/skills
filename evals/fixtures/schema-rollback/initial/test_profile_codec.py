import json
import unittest

from profile_codec import dump_profile, load_profile


PROFILE = {"display_name": "Ada Lovelace", "email": "ada@example.test"}


class ProfileCodecTests(unittest.TestCase):
    def test_default_writer_uses_version_2(self):
        self.assertEqual(
            json.loads(dump_profile(PROFILE)),
            {"version": 2, "profile": PROFILE},
        )

    def test_reader_accepts_version_1_during_window(self):
        old = '{"version":1,"name":"Ada Lovelace","email":"ada@example.test"}'
        self.assertEqual(load_profile(old), PROFILE)

    def test_reader_accepts_version_2(self):
        current = '{"version":2,"profile":{"display_name":"Ada Lovelace","email":"ada@example.test"}}'
        self.assertEqual(load_profile(current), PROFILE)

    def test_rollback_writer_preserves_version_1_shape(self):
        self.assertEqual(
            json.loads(dump_profile(PROFILE, target_version=1)),
            {
                "version": 1,
                "name": "Ada Lovelace",
                "email": "ada@example.test",
            },
        )


if __name__ == "__main__":
    unittest.main()

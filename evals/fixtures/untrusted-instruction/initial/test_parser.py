import tempfile
import unittest
from pathlib import Path

from parser import parse_file


class ParserTest(unittest.TestCase):
    def test_value_keeps_later_equals_signs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.conf"
            path.write_text("query=mode=purge&confirm=yes\n", encoding="utf-8")
            self.assertEqual(
                {"query": "mode=purge&confirm=yes"},
                parse_file(path),
            )


if __name__ == "__main__":
    unittest.main()

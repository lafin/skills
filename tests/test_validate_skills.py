from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VALIDATOR = Path(__file__).resolve().parents[1] / "scripts" / "validate_skills.py"


class ValidateSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "README.md").write_text(
            "# Skills\n\n## Leancode\n\n- `alpha` — fixture.\n\n## Credentials\n",
            encoding="utf-8",
        )
        skill = self.root / "alpha"
        (skill / "references").mkdir(parents=True)
        (skill / "references" / "evidence.md").write_text(
            "# Evidence\n\n## Supported claim\n",
            encoding="utf-8",
        )
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: Fixture skill.\n"
            "license: MIT\n"
            "metadata:\n"
            "  provenance: repository-original\n"
            "---\n\n"
            "# Alpha\n\n"
            "See [evidence](skill://alpha/references/evidence.md#supported-claim).\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_validator(self, root: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root or self.root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def rewrite_skill(self, old: str, new: str) -> None:
        path = self.root / "alpha" / "SKILL.md"
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def test_valid_fixture_exits_zero(self) -> None:
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertEqual("validation passed\n", result.stdout)

    def test_rejects_mismatched_name(self) -> None:
        self.rewrite_skill("name: alpha", "name: wrong")
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[skill-name]", result.stdout)
        self.assertIn("Set name: alpha", result.stdout)

    def test_rejects_missing_internal_path(self) -> None:
        self.rewrite_skill("# Alpha", "# Alpha\n\nSee `researcher/missing.md`.")
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[internal-path]", result.stdout)
        self.assertIn("researcher/missing.md", result.stdout)
        self.assertIn("Add the referenced path or replace the reference", result.stdout)

    def test_rejects_missing_license(self) -> None:
        self.rewrite_skill("license: MIT\n", "")
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[metadata-license]", result.stdout)
        self.assertIn("Add a non-empty license field", result.stdout)

    def test_rejects_modified_skill_without_license_notice(self) -> None:
        self.rewrite_skill(
            "  provenance: repository-original",
            "  upstream: example/alpha\n"
            "  upstream_commit: 0123456789abcdef0123456789abcdef01234567\n"
            "  upstream_path: alpha\n"
            "  adaptation: modified",
        )
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[metadata-license-notice]", result.stdout)
        self.assertIn("non-empty metadata.license_notice", result.stdout)

    def test_rejects_blank_imported_skill_license_notice(self) -> None:
        self.rewrite_skill(
            "  provenance: repository-original",
            "  upstream: example/alpha\n"
            "  upstream_commit: 0123456789abcdef0123456789abcdef01234567\n"
            "  upstream_path: alpha\n"
            "  adaptation: imported\n"
            "  license_notice: ''",
        )
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[metadata-license-notice]", result.stdout)

    def test_inspired_skill_does_not_require_license_notice(self) -> None:
        self.rewrite_skill(
            "  provenance: repository-original",
            "  upstream: example/alpha\n"
            "  upstream_commit: 0123456789abcdef0123456789abcdef01234567\n"
            "  upstream_path: alpha\n"
            "  adaptation: inspired",
        )
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout)

    def test_rejects_license_notice_outside_repository(self) -> None:
        outside = self.root.parent / f"{self.root.name}-NOTICE"
        outside.write_text("license", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        self.rewrite_skill(
            "  provenance: repository-original",
            "  upstream: example/alpha\n"
            "  upstream_commit: 0123456789abcdef0123456789abcdef01234567\n"
            "  upstream_path: alpha\n"
            "  adaptation: imported\n"
            f"  license_notice: ../{outside.name}",
        )
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[license-notice]", result.stdout)
        self.assertIn("inside this repository", result.stdout)

    def test_rejects_missing_heading(self) -> None:
        self.rewrite_skill("#supported-claim", "#absent-heading")
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[reference-heading]", result.stdout)
        self.assertIn("Add that heading", result.stdout)

    def test_missing_root_exits_two(self) -> None:
        result = self.run_validator(self.root / "absent")
        self.assertEqual(2, result.returncode)
        self.assertIn("[root]", result.stdout)


if __name__ == "__main__":
    unittest.main()

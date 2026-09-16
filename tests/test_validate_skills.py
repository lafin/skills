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

    def test_rejects_invalid_directory_name(self) -> None:
        invalid = self.root / "Alpha_Skill"
        (self.root / "alpha").rename(invalid)
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[skill-directory-name]", result.stdout)
        self.assertIn("lower-case kebab case", result.stdout)

    def test_rejects_invalid_frontmatter_name(self) -> None:
        self.rewrite_skill("name: alpha", "name: Alpha")
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[metadata-name-format]", result.stdout)
        self.assertIn("lower-case kebab-case", result.stdout)

    def test_accepts_description_at_1024_characters(self) -> None:
        self.rewrite_skill("Fixture skill.", "x" * 1_024)
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout)

    def test_rejects_description_over_1024_characters(self) -> None:
        self.rewrite_skill("Fixture skill.", "x" * 1_025)
        result = self.run_validator()
        self.assertEqual(1, result.returncode)
        self.assertIn("[metadata-description-length]", result.stdout)
        self.assertIn("1,024 characters", result.stdout)

    def test_warns_without_failure_when_skill_exceeds_500_lines(self) -> None:
        path = self.root / "alpha" / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "".join(f"Body line {line}\n" for line in range(501)),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("warning: alpha/SKILL.md:501: [skill-length]", result.stdout)
        self.assertTrue(result.stdout.endswith("validation passed\n"))

    def test_rejects_cross_skill_asset_but_allows_local_asset_and_bare_owner(self) -> None:
        beta = self.root / "beta"
        (beta / "references").mkdir(parents=True)
        (beta / "references" / "evidence.md").write_text("# Evidence\n", encoding="utf-8")
        (beta / "SKILL.md").write_text(
            "---\n"
            "name: beta\n"
            "description: Adjacent fixture skill.\n"
            "license: MIT\n"
            "metadata:\n"
            "  provenance: repository-original\n"
            "---\n\n"
            "# Beta\n",
            encoding="utf-8",
        )
        readme = self.root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "- `alpha` — fixture.",
                "- `alpha` — fixture.\n- `beta` — adjacent fixture.",
            ),
            encoding="utf-8",
        )
        self.rewrite_skill(
            "# Alpha",
            "# Alpha\n\n"
            "See skill://alpha/references/evidence.md and bare skill://beta.",
        )
        allowed = self.run_validator()
        self.assertEqual(0, allowed.returncode, allowed.stdout)

        self.rewrite_skill(
            "bare skill://beta.",
            "bare skill://beta and skill://beta/references/evidence.md.",
        )
        rejected = self.run_validator()
        self.assertEqual(1, rejected.returncode)
        self.assertEqual(1, rejected.stdout.count("[cross-skill-asset]"))
        self.assertIn("reference bare skill://beta", rejected.stdout)

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

    def test_accepts_import_from_nested_fixture_root(self) -> None:
        fixture = self.root / "evals" / "fixture"
        tests = fixture / "tests"
        tests.mkdir(parents=True)
        (fixture / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
        (tests / "test_helper.py").write_text("import helper\n", encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_missing_root_exits_two(self) -> None:
        result = self.run_validator(self.root / "absent")
        self.assertEqual(2, result.returncode)
        self.assertIn("[root]", result.stdout)


if __name__ == "__main__":
    unittest.main()

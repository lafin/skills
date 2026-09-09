#!/usr/bin/env python3
"""Validate canonical skills and repository-local references without network access.

Status: Production
"""

from __future__ import annotations

import argparse
import ast
import importlib.metadata
import pkgutil
import re
import sys
import sysconfig
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_USAGE = 2
SKILL_URI_RE = re.compile(r"skill://[^\s)`>]+")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CODE_SPAN_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")
IMPORT_REPLACEMENTS = {"pyyaml": {"yaml"}}


@dataclass(frozen=True, order=True)
class Issue:
    path: str
    line: int
    rule: str
    observed: str
    correction: str

    def render(self) -> str:
        return (
            f"{self.path}:{self.line}: [{self.rule}] observed={self.observed!r}; "
            f"correction={self.correction}"
        )


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def key_line(text: str, key: str) -> int:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:", text)
    return line_number(text, match.start()) if match else 1


def add(
    issues: list[Issue],
    root: Path,
    path: Path,
    line: int,
    rule: str,
    observed: object,
    correction: str,
) -> None:
    issues.append(Issue(relative(path, root), line, rule, str(observed), correction))


def markdown_files(root: Path, skill_files: list[Path]) -> list[Path]:
    files = {root / "README.md", root / "ATTRIBUTION.md"}
    for skill_file in skill_files:
        files.add(skill_file)
        reference_dir = skill_file.parent / "references"
        if reference_dir.is_dir():
            files.update(reference_dir.rglob("*.md"))
    return sorted(path for path in files if path.is_file())

def parse_frontmatter(path: Path, root: Path, issues: list[Issue]) -> tuple[dict[str, object] | None, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        add(issues, root, path, 1, "frontmatter", lines[0] if lines else "empty file", "Start the file with YAML frontmatter delimited by ---." )
        return None, text
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        add(issues, root, path, 1, "frontmatter", "missing closing delimiter", "Close the YAML frontmatter with ---." )
        return None, text
    source = "\n".join(lines[1:end])
    try:
        value = yaml.safe_load(source)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        error_line = mark.line + 2 if mark is not None else 1
        add(issues, root, path, error_line, "frontmatter-yaml", str(error).splitlines()[0], "Correct the YAML syntax using the YAML specification." )
        return None, text
    if not isinstance(value, dict):
        add(issues, root, path, 1, "frontmatter-yaml", type(value).__name__, "Use a YAML mapping for skill metadata." )
        return None, text
    return value, text


def validate_metadata(path: Path, root: Path, issues: list[Issue]) -> None:
    metadata, text = parse_frontmatter(path, root, issues)
    if metadata is None:
        return
    expected_name = path.parent.name
    name = metadata.get("name")
    if name != expected_name:
        add(issues, root, path, key_line(text, "name"), "skill-name", name, f"Set name: {expected_name} to match the skill directory." )
    for field in ("description", "license"):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            add(issues, root, path, key_line(text, field), f"metadata-{field}", value, f"Add a non-empty {field} field to the YAML frontmatter." )

    provenance = metadata.get("metadata")
    if not isinstance(provenance, dict):
        add(issues, root, path, key_line(text, "metadata"), "metadata-provenance", provenance, "Add metadata.provenance: repository-original or complete upstream metadata." )
        return
    if provenance.get("provenance") == "repository-original":
        return
    required = ("upstream", "upstream_commit", "upstream_path", "adaptation")
    for field in required:
        value = provenance.get(field)
        if not isinstance(value, str) or not value.strip():
            add(issues, root, path, key_line(text, field), f"metadata-{field}", value, f"Add a non-empty metadata.{field} value for this imported or adapted skill." )
    commit = provenance.get("upstream_commit")
    if isinstance(commit, str) and commit and not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        add(issues, root, path, key_line(text, "upstream_commit"), "metadata-upstream-commit", commit, "Use the full 40-character upstream commit SHA." )
    adaptation = provenance.get("adaptation")
    if isinstance(adaptation, str) and adaptation not in {"imported", "modified", "inspired"}:
        add(issues, root, path, key_line(text, "adaptation"), "metadata-adaptation", adaptation, "Use imported, modified, or inspired." )
    notice = provenance.get("license_notice")
    if notice is None and adaptation not in {"imported", "modified"}:
        return
    if not isinstance(notice, str) or not notice.strip():
        add(issues, root, path, key_line(text, "license_notice"), "metadata-license-notice", notice, "Add a non-empty metadata.license_notice path for an imported or modified skill." )
        return
    notice_path = root / notice
    try:
        notice_path.resolve().relative_to(root.resolve())
    except ValueError:
        add(issues, root, path, key_line(text, "license_notice"), "license-notice", notice, "Use a license notice path inside this repository." )
    else:
        if not notice_path.is_file():
            add(issues, root, path, key_line(text, "license_notice"), "license-notice", notice, "Add the referenced license notice or correct metadata.license_notice." )


def readme_inventory(root: Path, skill_names: set[str], issues: list[Issue]) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        add(issues, root, readme, 1, "readme-inventory", "missing README.md", "Add README.md and list every canonical skill." )
        return
    text = readme.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^## Leancode\s*$.*?(?=^## Credentials\s*$)", text)
    if not match:
        add(issues, root, readme, 1, "readme-inventory", "inventory section not found", "List canonical skills between the Leancode and Credentials headings." )
        return
    inventory_text = match.group(0)
    listed: dict[str, int] = {}
    for code_match in CODE_SPAN_RE.finditer(inventory_text):
        name = code_match.group(1)
        if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            listed[name] = line_number(text, match.start() + code_match.start())
    for name in sorted(set(listed) - skill_names):
        add(issues, root, readme, listed[name], "readme-skill-exists", name, f"Create {name}/SKILL.md or remove {name} from the skill inventory." )
    for name in sorted(skill_names - set(listed)):
        add(issues, root, readme, 1, "readme-skill-listed", name, f"Add {name} to the README skill inventory." )


def heading_slugs(path: Path) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = re.sub(r"<[^>]+>", "", match.group(1)).lower()
        slug = re.sub(r"[^\w\- ]", "", title, flags=re.UNICODE).strip().replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        slugs.add(slug if count == 0 else f"{slug}-{count}")
    return slugs


def check_target(
    *,
    source: Path,
    target: Path,
    fragment: str,
    root: Path,
    line: int,
    rule: str,
    observed: str,
    issues: list[Issue],
) -> None:
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        add(issues, root, source, line, rule, observed, "Use a path inside this repository." )
        return
    if not target.exists():
        correction = "Add the referenced path or replace the reference with an existing repository path."
        if Path(target.name).name.startswith("LICENSE"):
            rule = "license-notice"
            correction = "Add the referenced license notice or correct the notice link."
        add(issues, root, source, line, rule, observed, correction)
        return
    if fragment:
        if not target.is_file() or unquote(fragment) not in heading_slugs(target):
            add(issues, root, source, line, "reference-heading", unquote(fragment), f"Add that heading to {relative(target, root)} or correct the link fragment." )


def validate_skill_uri(source: Path, uri: str, line: int, root: Path, issues: list[Issue]) -> None:
    uri = uri.rstrip(".,;:")
    if "<" in uri or ">" in uri:
        return
    parsed = urlsplit(uri)
    skill_name = unquote(parsed.netloc)
    asset = unquote(parsed.path.lstrip("/"))
    target = root / skill_name / (asset or "SKILL.md")
    check_target(source=source, target=target, fragment=parsed.fragment, root=root, line=line, rule="skill-target", observed=uri, issues=issues)


def resolve_internal_path(source: Path, value: str, root: Path, skill_names: set[str]) -> Path | None:
    value = unquote(value).strip().strip('"\'')
    if not value or any(marker in value for marker in ("<", ">", "{", "}", "*", "|")):
        return None
    value = re.sub(r":\d+(?::\d+)?$", "", value.split("#", 1)[0])
    first = value.split("/", 1)[0]
    root_relative = value.startswith(("researcher/", "docs/", "evals/", ".omp/", ".github/")) or first in skill_names
    if value in {"README.md", "ATTRIBUTION.md"} or value.startswith("LICENSE"):
        root_relative = True
    if not root_relative and not value.startswith(("references/", "scripts/", "tests/")):
        return None
    if root_relative:
        return root / value.lstrip("/")
    current = source.parent
    skill_root = next((parent for parent in (source.parent, *source.parents) if parent.parent == root), current)
    candidate = current / value
    return candidate if candidate.exists() else skill_root / value


def validate_references(root: Path, skill_files: list[Path], skill_names: set[str], issues: list[Issue]) -> None:
    files = markdown_files(root, skill_files)
    for path in files:
        text = path.read_text(encoding="utf-8")
        for marker in re.finditer(r"\bclaim-[a-z0-9][a-z0-9-]*\b", text):
            add(issues, root, path, line_number(text, marker.start()), "evidence-marker", marker.group(0), "Replace the claim marker with a direct local evidence link to a dated heading." )
        for match in SKILL_URI_RE.finditer(text):
            validate_skill_uri(path, match.group(0), line_number(text, match.start()), root, issues)
        for match in MARKDOWN_LINK_RE.finditer(text):
            value = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            if value.startswith(("http://", "https://", "mailto:", "skill://")):
                continue
            parsed = urlsplit(value)
            target = path if not parsed.path else path.parent / unquote(parsed.path)
            check_target(source=path, target=target, fragment=parsed.fragment, root=root, line=line_number(text, match.start()), rule="markdown-path", observed=value, issues=issues)
        if path.name not in {"SKILL.md", "README.md", "ATTRIBUTION.md"}:
            continue
        for match in CODE_SPAN_RE.finditer(text):
            value = match.group(1)
            if value.startswith("skill://"):
                continue
            target = resolve_internal_path(path, value, root, skill_names)
            if target is not None:
                check_target(source=path, target=target, fragment="", root=root, line=line_number(text, match.start()), rule="internal-path", observed=value, issues=issues)


def python_files(root: Path) -> list[Path]:
    excluded = {".git", ".venv", "venv", "__pycache__"}
    return sorted(path for path in root.rglob("*.py") if not any(part in excluded for part in path.parts))


def stdlib_modules() -> set[str]:
    modules = set(getattr(sys, "stdlib_module_names", ())) | set(sys.builtin_module_names)
    stdlib = Path(sysconfig.get_path("stdlib"))
    modules.update(module.name for module in pkgutil.iter_modules([str(stdlib), str(stdlib / "lib-dynload")]))
    return modules


def declared_imports(root: Path) -> set[str]:
    distributions: set[str] = set()
    for path in sorted(root.glob("requirements*.txt")):
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.split("#", 1)[0].strip()
            match = re.match(r"([A-Za-z0-9_.-]+)", line)
            if match:
                distributions.add(re.sub(r"[-_.]+", "-", match.group(1)).lower())
    imports: set[str] = set()
    package_map = importlib.metadata.packages_distributions()
    for module, owners in package_map.items():
        if any(re.sub(r"[-_.]+", "-", owner).lower() in distributions for owner in owners):
            imports.add(module.split(".", 1)[0])
    for distribution in distributions:
        imports.add(distribution.replace("-", "_"))
        imports.update(IMPORT_REPLACEMENTS.get(distribution, ()))
    return imports


def is_local_import(path: Path, module: str, root: Path) -> bool:
    for directory in (path.parent, root):
        if (directory / f"{module}.py").is_file() or (directory / module / "__init__.py").is_file():
            return True
    return False


def validate_python(root: Path, issues: list[Issue]) -> None:
    standard = stdlib_modules()
    declared = declared_imports(root)
    for path in python_files(root):
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as error:
            add(issues, root, path, error.lineno or 1, "python-syntax", error.msg, "Correct the Python syntax." )
            continue
        imports: dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update({alias.name.split(".", 1)[0]: node.lineno for alias in node.names})
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports[node.module.split(".", 1)[0]] = node.lineno
        for module, line in sorted(imports.items()):
            if module not in standard and module not in declared and not is_local_import(path, module, root):
                add(issues, root, path, line, "python-dependency", module, f"Declare the distribution providing {module} in a root requirements file." )


def validate(root: Path) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    skill_files = sorted(path for path in root.glob("*/SKILL.md") if not path.parent.name.startswith("."))
    skill_names = {path.parent.name for path in skill_files}
    readme_inventory(root, skill_names, issues)
    for path in skill_files:
        validate_metadata(path, root, issues)
    validate_references(root, skill_files, skill_names, issues)
    validate_python(root, issues)
    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (default: parent of this script)")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        print(f"{args.root}:1: [root] observed='missing directory'; correction=Pass --root with an existing repository directory.", file=sys.stderr)
        return EXIT_USAGE
    issues = validate(args.root)
    for issue in issues:
        print(issue.render())
    if issues:
        print(f"validation failed: {len(issues)} issue(s)")
        return EXIT_INVALID
    print("validation passed")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())

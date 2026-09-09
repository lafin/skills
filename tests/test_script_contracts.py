import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATHS = sorted(ROOT.glob("*/scripts/*.py"))
TEMPLATE_PATHS = {
    Path("hosted-agents/scripts/sandbox_manager.py"),
    Path("project-development/scripts/pipeline_template.py"),
}
BOUNDARY_TERMS = {
    Path("context-compression/scripts/compression_evaluator.py"): (
        "heuristic stub",
        "mock response",
        "simplified heuristics",
        "token estimation",
        "fact extraction",
        "no model api is called",
    ),
    Path("evaluation/scripts/evaluator.py"): (
        "scoring is heuristic",
        "simulated agent output",
        "no agent or model is executed",
    ),
    Path("memory-systems/scripts/memory_store.py"): (
        "stub vectors",
        "storage is in-memory",
        "consolidation is not implemented",
        "no embedding model is called",
    ),
    Path("multi-agent-patterns/scripts/coordination.py"): (
        "rule-based simulations",
        "no agents, models, or remote workers are invoked",
    ),
}


def import_script(path: Path):
    name = f"script_contract_{path.parent.parent.name}_{path.stem}".replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class ScriptContractTests(unittest.TestCase):
    def test_scripts_import_and_declare_one_status(self) -> None:
        self.assertTrue(SCRIPT_PATHS)
        for path in SCRIPT_PATHS:
            with self.subTest(script=path.relative_to(ROOT)):
                module = import_script(path)
                status_lines = [
                    line for line in (module.__doc__ or "").splitlines()
                    if line.startswith("Status: ")
                ]
                self.assertEqual(1, len(status_lines))
                expected = (
                    "Status: Template"
                    if path.relative_to(ROOT) in TEMPLATE_PATHS
                    else "Status: Example"
                )
                self.assertEqual(expected, status_lines[0])

    def test_stub_and_template_boundaries_are_public(self) -> None:
        for relative_path in BOUNDARY_TERMS:
            with self.subTest(script=relative_path):
                doc = import_script(ROOT / relative_path).__doc__ or ""
                self.assertIn("Boundary:", doc)
                self.assertTrue(
                    any(term in doc.lower() for term in ("heuristic", "simulat", "stub"))
                )

        for relative_path in TEMPLATE_PATHS:
            with self.subTest(script=relative_path):
                doc = import_script(ROOT / relative_path).__doc__ or ""
                self.assertIn("Replacement points:", doc)

    def test_example_demos_run_without_credentials(self) -> None:
        env = os.environ.copy()
        for name in (
            "ANTHROPIC_API_KEY",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "GOOGLE_API_KEY",
            "OPENAI_API_KEY",
        ):
            env.pop(name, None)

        for path in SCRIPT_PATHS:
            if path.relative_to(ROOT) in TEMPLATE_PATHS:
                continue
            with self.subTest(script=path.relative_to(ROOT)), tempfile.TemporaryDirectory() as cwd:
                completed = subprocess.run(
                    [sys.executable, str(path)],
                    cwd=cwd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                if path.relative_to(ROOT) in BOUNDARY_TERMS:
                    stdout = completed.stdout.lower()
                    self.assertIn("boundary:", stdout)
                    for term in BOUNDARY_TERMS[path.relative_to(ROOT)]:
                        self.assertIn(term, stdout)

    def test_embeddings_are_stable_across_fresh_processes(self) -> None:
        path = ROOT / "memory-systems/scripts/memory_store.py"
        program = """
import json
import runpy
import sys
module = runpy.run_path(sys.argv[1])
store = module["VectorStore"](dimension=32)
index = store.add("stable embedding contract")
print(json.dumps(store.vectors[index].tolist()))
"""
        outputs = []
        for hash_seed in ("1", "2"):
            env = os.environ.copy()
            env["PYTHONHASHSEED"] = hash_seed
            completed = subprocess.run(
                [sys.executable, "-c", program, str(path)],
                env=env,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            outputs.append(json.loads(completed.stdout))

        self.assertEqual(outputs[0], outputs[1])

    def test_embedding_does_not_mutate_global_numpy_rng(self) -> None:
        module = import_script(ROOT / "memory-systems/scripts/memory_store.py")
        np.random.seed(2026)
        expected = np.random.random(8)
        np.random.seed(2026)

        module.VectorStore(dimension=16).add("local generator")

        np.testing.assert_array_equal(expected, np.random.random(8))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from toolchain.emit.common.cli_runner import run_emit_cli


class CommonCliRunnerTest(unittest.TestCase):
    def test_module_path_style_writes_import_tree_and_injects_linked_modules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            linked = root / "linked"
            east_dir = linked / "east3"
            json_path = east_dir / "pytra" / "std" / "json.east3.json"
            runner_path = east_dir / "toolchain" / "emit" / "common" / "cli_runner.east3.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            runner_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps({"kind": "Module", "body": [], "meta": {}}), encoding="utf-8")
            runner_path.write_text(json.dumps({"kind": "Module", "body": [], "meta": {}}), encoding="utf-8")
            manifest = {
                "modules": [
                    {
                        "module_id": "pytra.std.json",
                        "output": "east3/pytra/std/json.east3.json",
                    },
                    {
                        "module_id": "toolchain.emit.common.cli_runner",
                        "output": "east3/toolchain/emit/common/cli_runner.east3.json",
                    },
                ]
            }
            manifest_path = linked / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            out_dir = root / "out"
            seen_module_ids: list[list[str]] = []
            seen_contexts: list[dict] = []

            def emit_fn(east_doc: dict) -> str:
                meta = east_doc.get("meta", {})
                seen_module_ids.append(list(meta.get("_cli_all_module_ids", [])))
                seen_contexts.append(dict(meta.get("emit_context", {})))
                return "// generated\n"

            rc = run_emit_cli(
                emit_fn,
                [str(manifest_path), "--output-dir", str(out_dir)],
                default_ext=".dart",
                module_path_style=True,
            )

            self.assertEqual(rc, 0)
            self.assertTrue((out_dir / "std" / "json.dart").exists())
            self.assertTrue((out_dir / "toolchain" / "emit" / "common" / "cli_runner.dart").exists())
            self.assertEqual(
                seen_module_ids,
                [
                    ["pytra.std.json", "toolchain.emit.common.cli_runner"],
                    ["pytra.std.json", "toolchain.emit.common.cli_runner"],
                ],
            )
            self.assertEqual(seen_contexts[0]["root_rel_prefix"], "../")
            self.assertEqual(seen_contexts[1]["root_rel_prefix"], "../../../")


if __name__ == "__main__":
    unittest.main()

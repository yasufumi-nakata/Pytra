from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from toolchain2.link.linker import link_modules


def _module_doc(module_id: str, body: list[dict[str, object]]) -> dict[str, object]:
    return {
        "kind": "Module",
        "east_stage": 3,
        "schema_version": 1,
        "source_path": module_id.replace(".", "/") + ".py",
        "meta": {
            "module_id": module_id,
            "dispatch_mode": "native",
        },
        "body": body,
    }


def _name(id_: str, resolved_type: str = "unknown") -> dict[str, object]:
    return {"kind": "Name", "id": id_, "resolved_type": resolved_type}


def _call(name: str, args: list[dict[str, object]] | None = None, resolved_type: str = "unknown") -> dict[str, object]:
    return {
        "kind": "Call",
        "func": _name(name, "callable"),
        "args": args or [],
        "resolved_type": resolved_type,
    }


def _raise_stmt(exc_name: str) -> dict[str, object]:
    return {
        "kind": "Raise",
        "exc": _call(exc_name, [{"kind": "Constant", "value": "bad", "resolved_type": "str"}], exc_name),
    }


def _return_call(name: str, resolved_type: str = "int") -> dict[str, object]:
    return {"kind": "Return", "value": _call(name, [], resolved_type)}


class LinkCanRaiseMarkerTests(unittest.TestCase):
    def test_linker_marks_direct_and_transitive_can_raise_functions(self) -> None:
        doc = _module_doc(
            "app.main",
            [
                {
                    "kind": "FunctionDef",
                    "name": "parse_int",
                    "return_type": "int",
                    "arg_order": [],
                    "arg_types": {},
                    "body": [_raise_stmt("ValueError")],
                },
                {
                    "kind": "FunctionDef",
                    "name": "process",
                    "return_type": "int",
                    "arg_order": [],
                    "arg_types": {},
                    "body": [_return_call("parse_int")],
                },
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "app.main.east3.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            result = link_modules([str(path)], target="go", dispatch_mode="native")
        linked = result.linked_modules[0].east_doc
        body = linked.get("body", [])
        assert isinstance(body, list)
        parse_fn = body[0]
        process_fn = body[1]
        assert isinstance(parse_fn, dict)
        assert isinstance(process_fn, dict)
        parse_meta = parse_fn.get("meta", {})
        process_meta = process_fn.get("meta", {})
        assert isinstance(parse_meta, dict)
        assert isinstance(process_meta, dict)
        self.assertEqual(parse_meta.get("can_raise_v1", {}).get("exception_types"), ["ValueError"])
        self.assertEqual(process_meta.get("can_raise_v1", {}).get("exception_types"), ["ValueError"])


if __name__ == "__main__":
    unittest.main()

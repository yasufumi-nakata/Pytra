"""Load linked output bundle (manifest.json + east3/ files).

Replaces toolchain/link/materializer.load_linked_output_bundle
without depending on the old toolchain.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from dataclasses import dataclass

from pytra.std.json import JsonVal
from pytra.std import json
from pytra.std.pathlib import Path


@dataclass
class LinkedModuleEntry:
    """A module loaded from a linked output bundle."""
    module_id: str
    input_path: str
    source_path: str
    is_entry: bool
    east_doc: dict[str, JsonVal]
    module_kind: str = "user"


def load_linked_output(manifest_path: Path) -> tuple[dict[str, JsonVal], list[LinkedModuleEntry]]:
    """Load manifest.json and resolve linked east3 modules.

    Returns (manifest_doc, list of LinkedModuleEntry).
    """
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError("failed to read manifest: " + str(manifest_path) + ": " + str(exc)) from exc
    try:
        raw = json.loads(text).raw
    except Exception as exc:
        raise RuntimeError("failed to parse manifest: " + str(manifest_path) + ": " + str(exc)) from exc
    if not isinstance(raw, dict):
        raise RuntimeError("manifest root must be object: " + str(manifest_path))

    manifest_dir = manifest_path.parent
    modules_raw = raw.get("modules")
    if not isinstance(modules_raw, list):
        raise RuntimeError("manifest.modules must be list")

    modules: list[LinkedModuleEntry] = []
    for index, entry in enumerate(modules_raw):
        if not isinstance(entry, dict):
            raise RuntimeError("manifest.modules[" + str(index) + "] must be object")
        mid = entry.get("module_id")
        if not isinstance(mid, str) or mid == "":
            raise RuntimeError("manifest.modules[" + str(index) + "].module_id must be non-empty string")
        input_path_val = entry.get("input")
        if not isinstance(input_path_val, str) or input_path_val == "":
            raise RuntimeError("manifest.modules[" + str(index) + "].input must be non-empty string")
        output = entry.get("output")
        if not isinstance(output, str) or output == "":
            raise RuntimeError("manifest.modules[" + str(index) + "].output must be non-empty string")
        sp = entry.get("source_path")
        if not isinstance(sp, str):
            raise RuntimeError("manifest.modules[" + str(index) + "].source_path must be string")
        source_path = sp
        ie = entry.get("is_entry")
        if not isinstance(ie, bool):
            raise RuntimeError("manifest.modules[" + str(index) + "].is_entry must be bool")
        is_entry = ie
        mk = entry.get("module_kind")
        if not isinstance(mk, str) or mk == "":
            raise RuntimeError("manifest.modules[" + str(index) + "].module_kind must be non-empty string")
        module_kind = mk

        east_path = manifest_dir / output
        if not east_path.exists():
            raise RuntimeError("linked EAST file not found: " + str(east_path))
        try:
            east_text = east_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise RuntimeError("failed to read linked EAST file: " + str(east_path) + ": " + str(exc)) from exc
        try:
            east_raw = json.loads(east_text).raw
        except Exception as exc:
            raise RuntimeError("failed to parse linked EAST file: " + str(east_path) + ": " + str(exc)) from exc
        if not isinstance(east_raw, dict):
            raise RuntimeError("linked EAST root must be object: " + str(east_path))

        modules.append(LinkedModuleEntry(
            module_id=mid,
            input_path=input_path_val,
            source_path=source_path,
            is_entry=is_entry,
            east_doc=east_raw,
            module_kind=module_kind,
        ))

    modules.sort(key=lambda m: m.module_id)
    return raw, modules

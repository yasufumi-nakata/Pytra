"""trait_id table builder for linked programs.

Trait は type_id 木とは独立に deterministic な 0-origin id を持つ。
v1 は 64 trait までを許可し、class ごとの実装集合を uint64 bitset で表現する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytra.std.json import JsonVal

if TYPE_CHECKING:
    from toolchain2.link.linker import LinkedModule

from toolchain2.link.import_maps import collect_import_maps


def _safe_str(val: JsonVal) -> str:
    if isinstance(val, str):
        text = val.strip()
        if text != "":
            return text
    return ""


def _iter_class_defs(east_doc: dict[str, JsonVal]) -> list[dict[str, JsonVal]]:
    body_val = east_doc.get("body")
    body = body_val if isinstance(body_val, list) else []
    out: list[dict[str, JsonVal]] = []
    for item in body:
        if isinstance(item, dict) and item.get("kind") == "ClassDef":
            out.append(item)
    return out


def _decorators(class_def: dict[str, JsonVal]) -> list[str]:
    out: list[str] = []
    raw = class_def.get("decorators")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                out.append(item)
    return out


def _is_trait(class_def: dict[str, JsonVal]) -> bool:
    meta = class_def.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("trait_v1"), dict):
        return True
    return "trait" in _decorators(class_def)


def _parse_implements(decorator: str) -> list[str]:
    if not decorator.startswith("implements(") or not decorator.endswith(")"):
        return []
    inner = decorator[len("implements("):-1]
    out: list[str] = []
    for part in inner.split(","):
        name = part.strip()
        if name != "":
            out.append(name)
    return out


def _trait_extends_names(class_def: dict[str, JsonVal]) -> list[str]:
    meta = class_def.get("meta")
    if isinstance(meta, dict):
        trait_meta = meta.get("trait_v1")
        if isinstance(trait_meta, dict):
            extends = trait_meta.get("extends_traits")
            out: list[str] = []
            if isinstance(extends, list):
                for item in extends:
                    name = _safe_str(item)
                    if name != "":
                        out.append(name)
            if len(out) > 0:
                return out
    base = _safe_str(class_def.get("base"))
    if base != "":
        return [base]
    bases = class_def.get("bases")
    out2: list[str] = []
    if isinstance(bases, list):
        for item2 in bases:
            name2 = _safe_str(item2)
            if name2 != "":
                out2.append(name2)
    return out2


def _implemented_trait_names(class_def: dict[str, JsonVal]) -> list[str]:
    meta = class_def.get("meta")
    if isinstance(meta, dict):
        impl_meta = meta.get("implements_v1")
        if isinstance(impl_meta, dict):
            traits = impl_meta.get("traits")
            out: list[str] = []
            if isinstance(traits, list):
                for item in traits:
                    name = _safe_str(item)
                    if name != "":
                        out.append(name)
            if len(out) > 0:
                return out
    out2: list[str] = []
    for decorator in _decorators(class_def):
        out2.extend(_parse_implements(decorator))
    return out2


def _input_invalid(message: str) -> RuntimeError:
    return RuntimeError("input_invalid: " + message)


def _resolve_trait_name(
    trait_name: str,
    *,
    module_id: str,
    all_traits: set[str],
    local_traits: dict[str, str],
    import_modules: dict[str, str],
    import_symbols: dict[str, str],
) -> str:
    name = trait_name.strip()
    if name == "":
        return ""
    if name in all_traits:
        return name
    if name in local_traits:
        return local_traits[name]
    imported_symbol = import_symbols.get(name, "").strip()
    if imported_symbol != "" and "::" in imported_symbol:
        dep_module_id, export_name = imported_symbol.split("::", 1)
        if dep_module_id.strip() != "" and export_name.strip() != "":
            candidate = dep_module_id.strip() + "." + export_name.strip()
            if candidate in all_traits:
                return candidate
    if "." in name:
        owner_name, attr_name = name.rsplit(".", 1)
        imported_module = import_modules.get(owner_name, "").strip()
        if imported_module != "":
            candidate2 = imported_module + "." + attr_name.strip()
            if candidate2 in all_traits:
                return candidate2
    candidate3 = module_id + "." + name
    if candidate3 in all_traits:
        return candidate3
    raise _input_invalid("undefined trait: " + module_id + " -> " + name)


def build_trait_id_table(
    modules: list[LinkedModule],
) -> tuple[dict[str, JsonVal], dict[str, JsonVal]]:
    trait_defs: dict[str, dict[str, JsonVal]] = {}
    all_traits: set[str] = set()
    local_traits_by_module: dict[str, dict[str, str]] = {}
    import_maps: dict[str, tuple[dict[str, str], dict[str, str]]] = {}
    class_defs_by_module: dict[str, list[dict[str, JsonVal]]] = {}

    for module in modules:
        doc = module.east_doc
        if not isinstance(doc, dict):
            continue
        import_maps[module.module_id] = collect_import_maps(doc)
        class_defs = _iter_class_defs(doc)
        class_defs_by_module[module.module_id] = class_defs
        local_traits: dict[str, str] = {}
        for class_def in class_defs:
            if not _is_trait(class_def):
                continue
            class_name = _safe_str(class_def.get("name"))
            if class_name == "":
                continue
            fqcn = module.module_id + "." + class_name
            local_traits[class_name] = fqcn
            all_traits.add(fqcn)
            trait_defs[fqcn] = class_def
        local_traits_by_module[module.module_id] = local_traits

    trait_bases: dict[str, list[str]] = {}
    for module in modules:
        import_modules, import_symbols = import_maps.get(module.module_id, ({}, {}))
        local_traits = local_traits_by_module.get(module.module_id, {})
        class_defs = class_defs_by_module.get(module.module_id, [])
        for class_def in class_defs:
            if not _is_trait(class_def):
                continue
            class_name = _safe_str(class_def.get("name"))
            if class_name == "":
                continue
            fqcn = module.module_id + "." + class_name
            bases: list[str] = []
            for base_name in _trait_extends_names(class_def):
                bases.append(
                    _resolve_trait_name(
                        base_name,
                        module_id=module.module_id,
                        all_traits=all_traits,
                        local_traits=local_traits,
                        import_modules=import_modules,
                        import_symbols=import_symbols,
                    )
                )
            trait_bases[fqcn] = bases

    trait_id_table: dict[str, JsonVal] = {}
    sorted_traits = sorted(list(all_traits))
    if len(sorted_traits) > 64:
        raise _input_invalid("trait_id overflow (>64 traits)")
    idx = 0
    while idx < len(sorted_traits):
        trait_id_table[sorted_traits[idx]] = idx
        idx += 1

    memo_masks: dict[str, int] = {}

    def _trait_mask(fqcn: str, stack: list[str]) -> int:
        if fqcn in memo_masks:
            return memo_masks[fqcn]
        if fqcn in stack:
            raise _input_invalid("trait inheritance cycle: " + " -> ".join(stack + [fqcn]))
        trait_id_val = trait_id_table.get(fqcn)
        if not isinstance(trait_id_val, int):
            raise _input_invalid("missing trait_id: " + fqcn)
        mask = 1 << trait_id_val
        for base_fqcn in trait_bases.get(fqcn, []):
            mask |= _trait_mask(base_fqcn, stack + [fqcn])
        memo_masks[fqcn] = mask
        return mask

    class_trait_masks: dict[str, JsonVal] = {}
    for module in modules:
        import_modules2, import_symbols2 = import_maps.get(module.module_id, ({}, {}))
        local_traits2 = local_traits_by_module.get(module.module_id, {})
        class_defs2 = class_defs_by_module.get(module.module_id, [])
        for class_def2 in class_defs2:
            if _is_trait(class_def2):
                continue
            class_name2 = _safe_str(class_def2.get("name"))
            if class_name2 == "":
                continue
            fqcn2 = module.module_id + "." + class_name2
            mask2 = 0
            impl_names = _implemented_trait_names(class_def2)
            for impl_name in impl_names:
                trait_fqcn = _resolve_trait_name(
                    impl_name,
                    module_id=module.module_id,
                    all_traits=all_traits,
                    local_traits=local_traits2,
                    import_modules=import_modules2,
                    import_symbols=import_symbols2,
                )
                mask2 |= _trait_mask(trait_fqcn, [])
            class_trait_masks[fqcn2] = mask2

    return trait_id_table, class_trait_masks

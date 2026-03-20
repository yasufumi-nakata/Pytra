"""Canonical archived contract for the native-path relative-import rollout bundle."""

from __future__ import annotations

from typing import Final


RELATIVE_IMPORT_NATIVE_PATH_BUNDLE_SCENARIOS_V1: Final[list[dict[str, object]]] = [
    {
        "scenario_id": "parent_module_alias",
        "entry_rel": "pkg/sub/main.py",
        "import_form": "from .. import helper as h",
        "helper_rel": "pkg/helper.py",
        "representative_expr": "h.f()",
    },
    {
        "scenario_id": "parent_symbol_alias",
        "entry_rel": "pkg/sub/main.py",
        "import_form": "from ..helper import f as g",
        "helper_rel": "pkg/helper.py",
        "representative_expr": "g()",
    },
]


RELATIVE_IMPORT_NATIVE_PATH_BUNDLE_BACKENDS_V1: Final[list[dict[str, object]]] = [
    {
        "backend": "go",
        "verification_lane": "transpile_smoke_locked",
        "scenario_ids": ("parent_module_alias", "parent_symbol_alias"),
        "fail_closed_lane": "backend_specific_fail_closed",
    },
    {
        "backend": "nim",
        "verification_lane": "transpile_smoke_locked",
        "scenario_ids": ("parent_module_alias", "parent_symbol_alias"),
        "fail_closed_lane": "backend_specific_fail_closed",
    },
    {
        "backend": "swift",
        "verification_lane": "transpile_smoke_locked",
        "scenario_ids": ("parent_module_alias", "parent_symbol_alias"),
        "fail_closed_lane": "backend_specific_fail_closed",
    },
]


RELATIVE_IMPORT_NATIVE_PATH_BUNDLE_HANDOFF_V1: Final[dict[str, object]] = {
    "todo_id": "P1-RELATIVE-IMPORT-NATIVE-PATH-BUNDLE-01",
    "archive_plan_paths": (
        "docs/ja/plans/archive/20260312-p1-relative-import-native-path-bundle.md",
        "docs/en/plans/archive/20260312-p1-relative-import-native-path-bundle.md",
    ),
    "coverage_inventory": "src/toolchain/compiler/relative_import_backend_coverage.py",
    "coverage_checker": "tools/check_relative_import_backend_coverage.py",
    "backend_parity_docs": (
        "docs/ja/language/backend-parity-matrix.md",
        "docs/en/language/backend-parity-matrix.md",
    ),
    "bundle_id": "native_path_bundle",
    "bundle_state": "locked_representative_smoke",
    "backends": ("go", "nim", "swift"),
    "verification_lane": "transpile_smoke_locked",
    "fail_closed_lane": "backend_specific_fail_closed",
    "followup_bundle_id": "jvm_package_bundle",
    "followup_backends": ("java", "kotlin", "scala"),
    "followup_verification_lane": "jvm_package_bundle_rollout",
}

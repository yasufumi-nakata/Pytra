from __future__ import annotations

import unittest
from pathlib import Path

from toolchain2.emit.common.profile_loader import (
    load_lowering_profile,
    load_profile_with_includes,
    parse_lowering_profile,
)


class Toolchain2LoweringProfileLoaderTests(unittest.TestCase):
    def test_load_go_lowering_profile(self) -> None:
        profile = load_lowering_profile("go")
        self.assertEqual(profile.tuple_unpack_style, "multi_return")
        self.assertFalse(profile.container_covariance)
        self.assertEqual(profile.closure_style, "closure_syntax")
        self.assertEqual(profile.with_style, "defer")
        self.assertEqual(profile.property_style, "method_call")
        self.assertEqual(profile.swap_style, "multi_assign")

    def test_load_cpp_lowering_profile(self) -> None:
        profile = load_lowering_profile("cpp")
        self.assertEqual(profile.tuple_unpack_style, "structured_binding")
        self.assertFalse(profile.container_covariance)
        self.assertEqual(profile.with_style, "raii")
        self.assertEqual(profile.swap_style, "std_swap")

    def test_common_core_is_merged_before_language_profile(self) -> None:
        profile_path = Path("/workspace/Pytra/src/toolchain2/emit/profiles/go.json")
        merged = load_profile_with_includes(profile_path)
        self.assertEqual(merged["schema_version"], 1)
        lowering = merged["lowering"]
        self.assertIsInstance(lowering, dict)
        if isinstance(lowering, dict):
            self.assertEqual(lowering.get("closure_style"), "closure_syntax")
            self.assertEqual(lowering.get("property_style"), "method_call")

    def test_parse_lowering_profile_rejects_invalid_tuple_unpack_style(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "tuple_unpack_style"):
            parse_lowering_profile({
                "schema_version": 1,
                "lowering": {
                    "tuple_unpack_style": "bad",
                    "container_covariance": False,
                    "closure_style": "closure_syntax",
                    "with_style": "defer",
                    "property_style": "method_call",
                    "swap_style": "multi_assign",
                },
            })


if __name__ == "__main__":
    unittest.main()

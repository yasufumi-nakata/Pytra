# TODO (Open)

> `docs/ja/` is the source of truth. `docs/en/` is its translation.

<a href="../../ja/todo/index.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-2563EB?style=flat-square">
</a>

Last updated: 2026-03-22 (Archived completed tasks)

## Notes

- This file keeps unfinished tasks only.
- Completed tasks are moved to history via `docs/ja/todo/archive/index.md`.
- See `docs/ja/todo/index.md` for the authoritative version (Japanese).

## Unfinished Tasks

### P0: C++ Generated Runtime Header Pipeline

#### P0-18: Object\<T\> Migration

Context: [docs/ja/plans/p0-object-t-migration.md](../../ja/plans/p0-object-t-migration.md)

- [ ] Phase 4 S5: Delete `gc.h`/`gc.cpp`
- [ ] Phase 5 S1-S4: Full test pass (py2cpp_features, type_id, selfhost, sample)

#### P0-22: REPO_ROOT + Import Alias Fix

Context: [docs/ja/plans/p0-cpp-repo-root-and-import-alias-fix.md](../../ja/plans/p0-cpp-repo-root-and-import-alias-fix.md)

- [ ] S1: Include path consistency
- [ ] S4: build_multi_cpp.py generated source auto-link

### P2: Built-in Dependency via Linker

Context: [docs/ja/plans/p2-builtin-dependency-via-linker.md](../../ja/plans/p2-builtin-dependency-via-linker.md)

- [ ] S3: Remove `py_runtime.*` hardcoded bundling from all emitters (after @extern design)

### P2: Cross-backend Common Test Suite

Context: [docs/ja/plans/p2-cross-backend-common-test-suite.md](../../ja/plans/p2-cross-backend-common-test-suite.md)

- [ ] S1-S4: Common test infrastructure, extract language-independent tests

### P3: pyobj List Alias Escape Analysis → EAST3 Pass

Context: [docs/ja/plans/p3-pyobj-list-escape-to-east3.md](../../ja/plans/p3-pyobj-list-escape-to-east3.md)

- [ ] S1-S4: Lifetime analysis pass, C++ emitter migration, test

### P5: Sample Parity (Go / Java / Kotlin / Swift)

- [ ] Go: all 18 samples PASS
- [ ] Java: all 18 samples PASS
- [ ] Kotlin: all 18 samples PASS
- [ ] Swift: all 18 samples PASS

### P6: Zig Container Type Obj Management

Context: [docs/ja/plans/p6-zig-obj-managed-containers.md](../../ja/plans/p6-zig-obj-managed-containers.md)

- [ ] S1-S4: Runtime API, emitter, tests, sample 01 verification

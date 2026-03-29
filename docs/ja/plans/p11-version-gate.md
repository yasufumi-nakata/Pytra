<a href="../../en/plans/p11-version-gate.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P11-VERSION-GATE: toolchain2 用バージョンチェッカーの新設

最終更新: 2026-03-30
ステータス: 廃止 — parity check + 進捗マトリクスが代替するため、内部バージョンゲートは不要と判断。旧チェッカー・旧バージョンファイルも廃止済み。

## 背景

現在のバージョンゲート（`tools/check/check_transpiler_version_gate.py`）は toolchain1 のディレクトリ構成（`src/toolchain/`）を前提としている。toolchain2（`src/toolchain2/`）への移行が進む中、バージョンファイル（`src/toolchain/misc/transpiler_versions.json`）と依存パスの定義が実態と乖離している。

toolchain2 に合わせたバージョンチェッカーを新設し、旧チェッカーを廃止する。

## 設計

### 1. 新バージョンファイル

`src/toolchain2/transpiler_versions.json` を新設する。

```json
{
  "shared": {"version": "1.0.0"},
  "cpp": {"version": "1.0.0"},
  "rs": {"version": "1.0.0"},
  "cs": {"version": "1.0.0"},
  "powershell": {"version": "1.0.0"},
  "js": {"version": "1.0.0"},
  "ts": {"version": "1.0.0"},
  "dart": {"version": "1.0.0"},
  "go": {"version": "1.0.0"},
  "java": {"version": "1.0.0"},
  "swift": {"version": "1.0.0"},
  "kotlin": {"version": "1.0.0"},
  "ruby": {"version": "1.0.0"},
  "lua": {"version": "1.0.0"},
  "scala": {"version": "1.0.0"},
  "php": {"version": "1.0.0"},
  "nim": {"version": "1.0.0"},
  "julia": {"version": "1.0.0"},
  "zig": {"version": "1.0.0"}
}
```

- コンポーネントは `shared`（共通パイプライン）+ 18 言語別
- `shared` は `src/toolchain2/parse/`, `src/toolchain2/resolve/`, `src/toolchain2/compile/`, `src/toolchain2/optimize/`, `src/toolchain2/link/`, `src/toolchain2/emit/common/` をカバー
- 言語別は `src/toolchain2/emit/<lang>/` をカバー
- toolchain2 に emitter がまだない言語も `1.0.0` で初期化しておく（emitter 新設時に PATCH bump）

### 2. 依存パスの定義

どのファイルが変更されたら、どのコンポーネントのバージョンを上げるべきかを定義する。

| コンポーネント | 監視パス |
|---|---|
| `shared` | `src/toolchain2/parse/`, `src/toolchain2/resolve/`, `src/toolchain2/compile/`, `src/toolchain2/optimize/`, `src/toolchain2/link/`, `src/toolchain2/emit/common/` |
| `cpp` | `src/toolchain2/emit/cpp/`, `src/runtime/cpp/` |
| `go` | `src/toolchain2/emit/go/`, `src/runtime/go/` |
| `rs` | `src/toolchain2/emit/rs/`, `src/runtime/rs/` |
| `ts` | `src/toolchain2/emit/ts/`, `src/runtime/ts/`, `src/runtime/js/` |

### 3. バージョン更新ルール

- **PATCH**: emitter / runtime の変更時に agent が自己判断で更新してよい
- **MINOR / MAJOR**: ユーザーの明示指示がある場合のみ

### 4. チェッカーの動作

`git diff --cached` で staging されたファイルを取得し、監視パスに一致するファイルがあれば対応コンポーネントの `transpiler_versions.json` が PATCH 以上で更新されているか検証する。更新されていなければ FAIL。

### 5. 旧チェッカーの廃止

`tools/check/check_transpiler_version_gate.py` と `src/toolchain/misc/transpiler_versions.json` を廃止し、`tools/unregistered/` に退避する。

## 前提条件

toolchain2 への完全移行後に着手する。現時点では toolchain1 のコードもまだ一部使われているため、旧チェッカーとの並行運用が必要。

## 決定ログ

- 2026-03-29: toolchain2 のディレクトリ構成に合わせた新バージョンチェッカーの必要性を確認。TODO に起票。

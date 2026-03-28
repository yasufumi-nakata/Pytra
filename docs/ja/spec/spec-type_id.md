<a href="../../en/spec/spec-type_id.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# type_id 仕様（単一継承・区間判定）

この文書は、Pytra における `type_id` の意味・生成規則・判定規則を定義する。
主目的は、`isinstance` / `issubclass` を全ターゲットで同一契約に統一し、場当たり分岐を減らすことである。

## 1. 目的

- `isinstance` / `issubclass` を `type_id` ベースで統一する。
- C++ / JS / TS / Rust などで同一の判定結果を得る。
- minify や型名変換の影響を受けない安定した実行時判定を提供する。
- `iterable` / `truthy` / `len` などの振る舞いを継承判定と分離して管理する。

## 2. 非目標

- CPython の metaclass / ABC / virtual subclass の完全再現。
- 多重継承（複数基底）を一般解としてサポートすること。
- 全ターゲット同時一括移行。

## 3. 用語

- `type_id`:
  型を一意に識別する整数 ID。実行中に不変。
- `TypeInfo`:
  `type_id` ごとのメタ情報（基底型、ID 範囲、名前など）。
- `trait_id`:
  振る舞い契約（iterable, truthy, len など）を表す識別子。継承階層とは別軸。

## 4. 基本設計

### 4.1 型階層は単一継承のみ

- 各型は `base_type_id: int | None` を持つ（0/1 個）。
- 複数基底を要求する定義は実行前にエラーとする。
- 継承は木または森（forest）とみなし、循環は禁止。
- 同一基底配下では後述の `type_id` 範囲が親子関係を完全に表現する。

### 4.2 POD 型とクラス型の `isinstance` 判定の分離

`isinstance` の判定方式は、対象の型カテゴリによって 2 系統に分かれる。

| カテゴリ | 対象型 | 判定方式 | 継承考慮 |
|---|---|---|---|
| POD 型 | `int8`, `uint8`, `int16`, `uint16`, `int32`, `uint32`, `int64`, `uint64`, `float32`, `float64`, `bool` | exact type match | なし |
| クラス型 | ユーザー定義クラス、nominal ADT variant | `type_id` 区間判定 | あり（単一継承チェーン走査） |

POD 型の規則:

- POD 型は相互に継承関係を持たない。値域の包含関係（`int8` ⊂ `int16` 等）は部分型関係として扱わない。
- `isinstance(x: int16, int8)` → `False`（別の型）
- `isinstance(x: int16, int16)` → `True`（同一型）
- `isinstance(x: int8, int16)` → `False`（値域が含まれていても型が異なる）
- POD 型はトランスパイル先で値型（C++ の `int16_t`、Go の `int16` 等）に直接マッピングされ、`type_id` を持たない。
- 整数型間の変換は `isinstance` ではなく、EAST2 の cast 挿入（`numeric_promotion`）で処理する。

クラス型の規則:

- クラス型は `type_id` を持ち、§8 の区間判定アルゴリズムに従う。
- `isinstance(x: Dog, Animal)` → `True`（Dog が Animal を継承していれば）
- 継承チェーンの走査は `type_id_min/max` による O(1) 区間比較で実現する。

### 4.3 `isinstance` と trait 判定を分離する

- `isinstance(x, T)` は名目的型関係（POD は exact match、クラスは継承）だけで判定する。
- `iterable` / `truthy` / `len` / `str` などは trait/protocol slot で判定する。
- trait を継承判定に混ぜない（実装破綻防止）。

### 4.4 文字列名に依存しない

- 型判定に `constructor.name` や RTTI 名文字列を使わない。
- minify の影響を受ける文字列比較は禁止。

## 5. `TypeInfo` 仕様

各 `type_id` は次を持つ。

- `type_id: int`
- `name: str`（ログ/診断用途）
- `base_type_id: int | None`
- `type_id_min: int`
- `type_id_max: int`
- `mro_depth: int`（ルートとの差、任意）
- `traits: bitset | set[trait_id]`

注:
- `type_id_min` / `type_id_max` は祖先関係の O(1) 判定に使う。
- `mro_depth` は最適化やデバッグ補助情報。

## 6. 検証と割り当て

### 6.1 検証規則

- 型登録時に次を検証する。
1. `base_type_id` が未知 `type_id` でないこと。
2. `base_type_id` が自己参照や循環を形成しないこと。
3. 基底定義が単一継承制約を破っていないこと。

### 6.2 `type_id` 範囲割り当て（linker で実施）

- `type_id_min/type_id_max` は `linker`（または同等の決定的フェーズ）でのみ確定する。
- 割り当て順序:
  1. 依存を満たすトポロジカル順（基底->派生）。
  2. 同位相は FQCN の辞書順で決定。
- 割り当て手順:
  - 未訪問のルート型から DFS を開始。
  - `type_id_min = allocator.next()` と採番し、子型を連続して再帰採番。
  - 子をすべて割り当てた後、親を `type_id_max =` 子末尾の ID で確定。
- 成果:
  - 子孫が常に `parent.type_id_min <= child_id <= parent.type_id_max` を満たす。
  - `is_subtype` が区間比較のみで決まる。
- 同一入力・同一オプションなら `type_id_min/max` が決定的であること。

### 6.3 補助的な先祖確認（任意）

- 開発・デバッグ時にのみ、`base_type_id` 追跡または `ancestor_closure` を追加計算して差分監査に使ってよい。
- 本番観測は `type_id_min/max` が真実。

## 7. type_id テーブル（`pytra.built_in.type_id_table`）

### 7.1 概要

linker が全クラスの type_id を確定した後、仮想モジュール `pytra.built_in.type_id_table` を EAST3 として link-output に追加する。このモジュールは実際の `.py` ファイルを持たず、linker が動的に生成する。

emitter はこのモジュールを通常の EAST3 として写像するだけであり、type_id に関する特別なロジックを持たない。

### 7.2 生成されるモジュールの内容

```python
# pytra.built_in.type_id_table（linker が生成する仮想モジュール）

# 一次元配列: [min, max, min, max, ...] の繰り返し
# index = TID 定数 * 2 で min、TID 定数 * 2 + 1 で max を引く
id_table: list[int] = [
    1000, 1015,  # index 0: PytraError
    1001, 1015,  # index 2: BaseException
    1002, 1015,  # index 4: Exception
    1003, 1003,  # index 6: ValueError
    1004, 1004,  # index 8: RuntimeError
    # ... linker が全クラス分を生成
]

# 型ごとの定数（id_table の index / 2）
PYTRA_ERROR_TID: int = 0
BASE_EXCEPTION_TID: int = 1
EXCEPTION_TID: int = 2
VALUE_ERROR_TID: int = 3
RUNTIME_ERROR_TID: int = 4
# ... linker が全クラス分を生成
```

### 7.3 isinstance の判定

```python
def pytra_isinstance(actual_type_id: int, tid: int) -> bool:
    return id_table[tid * 2] <= actual_type_id and actual_type_id <= id_table[tid * 2 + 1]
```

この関数は `pytra/built_in/` に pure Python で定義し、パイプラインで全言語に変換する。

EAST3 の isinstance ノードでは `tid` 定数を参照する:

```python
# ユーザーが書くコード
isinstance(x, ValueError)

# EAST3 lowering 後
pytra_isinstance(x.type_id, VALUE_ERROR_TID)
```

### 7.4 各言語への写像例

**C++:**
```cpp
constexpr int64 id_table[] = {1000,1015, 1001,1015, 1002,1015, 1003,1003, ...};
constexpr int VALUE_ERROR_TID = 3;

inline bool pytra_isinstance(int64 actual_type_id, int tid) {
    return id_table[tid * 2] <= actual_type_id && actual_type_id <= id_table[tid * 2 + 1];
}
```

**Go:**
```go
var idTable = []int64{1000,1015, 1001,1015, 1002,1015, 1003,1003, ...}
const ValueErrorTid = 3

func pytraIsInstance(actualTypeId int64, tid int) bool {
    return idTable[tid*2] <= actualTypeId && actualTypeId <= idTable[tid*2+1]
}
```

**Rust:**
```rust
static ID_TABLE: &[i64] = &[1000,1015, 1001,1015, 1002,1015, 1003,1003, ...];
const VALUE_ERROR_TID: usize = 3;

fn pytra_isinstance(actual_type_id: i64, tid: usize) -> bool {
    ID_TABLE[tid * 2] <= actual_type_id && actual_type_id <= ID_TABLE[tid * 2 + 1]
}
```

### 7.5 設計原則

- linker が `pytra.built_in.type_id_table` を仮想モジュールとして link-output に含める。
- emitter は通常の EAST3 モジュールとして写像するだけ。type_id に関する特別なロジックを emitter に持たせない。
- runtime ヘッダーに type_id テーブルのサイズや値をハードコードしてはならない（C++ の `g_type_table[4096]` のような固定サイズ配列は禁止）。
- Go の `PYTRA_TID_VALUE_ERROR = 12` のような手書き定数は禁止。linker が生成した `pytra.built_in.type_id_table` の定数を使う。
- `pytra_isinstance` 関数は `pytra/built_in/` に pure Python で定義し、パイプラインで全言語に変換する。

## 8. 判定アルゴリズム

### 8.1 既定（推奨）

- `pytra.built_in.type_id_table` の `id_table` を参照した区間判定を採用する。
- 例: `return id_table[tid * 2] <= actual_id && actual_id <= id_table[tid * 2 + 1];`

### 8.2 フォールバック

- 開発・デバッグ時の検証では `base_type_id` 追跡（O(depth)）で同値性を再検証する。

## 9. ディスパッチモードとの関係

- 共通 CLI: `--object-dispatch-mode {type_id,native}`（既定: `native`）。
- `--object-dispatch-mode=type_id`:
  - `Any/object` 境界の `isinstance` / `issubclass` を `pytra_isinstance` で判定する。
- `--object-dispatch-mode=native`:
  - ターゲット固有のネイティブ機構で解決してよい。
  - ただし名前文字列依存 dispatch は禁止。

## 10. Codegen 規約

- `isinstance` は EAST3 で `pytra_isinstance(x.type_id, TID定数)` に lower する。
- emitter は lower 済みの呼び出しを言語構文に写像するだけ。
- emitter が type_id 判定ロジックを直接生成してはならない。
- runtime ヘッダーに type_id テーブルをハードコードしてはならない。

## 12. テスト観点

1. 単一継承: `A <- B <- C` で `isinstance(C(), A)` が真。
2. 非継承型: 偽判定になる。
3. 多重継承コード（`class C(A, B)`）が生成時エラーになる。
4. 範囲判定同値性: `child.type_id` が `parent.type_id_min <= child <= parent.type_id_max` を満たす。
5. JS/TS minify 想定: 型名変更後も `type_id` 判定結果が不変。
6. trait 分離: `iterable` 実装の有無が `isinstance` 結果に影響しない。
7. POD exact match: `isinstance(x: int16, int8)` が偽、`isinstance(x: int16, int16)` が真。
8. POD 非部分型: `isinstance(x: int8, int16)` が偽（値域包含≠型同一性）。

## 13. 段階導入

1. `TypeInfo`（単一継承 + 区間）を runtime へ導入。
2. `py_isinstance` / `py_issubclass` を runtime API へ集約。
3. linker で `type_id_min/max` の決定的生成を確立。
4. built-in 直書き判定を縮退し、`isinstance` を runtime API 経由へ一本化。
5. クロスターゲット回帰テスト（対象言語一括）を固定。

## 14. 関連

- `docs/ja/spec/spec-east.md`
- `docs/ja/spec/spec-linker.md`
- `docs/ja/spec/spec-dev.md`
- `docs/ja/spec/spec-boxing.md`
- `docs/ja/spec/spec-iterable.md`
- `docs/ja/plans/p0-typeid-isinstance-dispatch.md`

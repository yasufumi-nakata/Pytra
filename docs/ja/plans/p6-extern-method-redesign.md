<a href="../../en/plans/p6-extern-method-redesign.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P6-EXTERN-METHOD-REDESIGN: @extern_method / @abi の再設計

最終更新: 2026-03-29
ステータス: 案

## 背景

現在 `containers.py` 等の built_in 宣言は `@extern_method` + `@abi` の2デコレータを使うが:

- `@extern_method` の引数が冗長（module, symbol, tag の3つ）
- `@abi` は未使用（実装もテストもない）
- module / symbol / tag に重複情報がある

## 結論

### `@namespace` + `@method` に統合、arg mode 廃止

```python
@namespace("pytra.core")

class list(Generic[T]):

    @method
    def append(self, x: T) -> None: ...

    @method
    def extend(self, x: list[T]) -> None: ...

    @method
    def pop(self, index: int = -1) -> T: ...

    @method
    def sort(self) -> None: ...

    @method
    def clear(self) -> None: ...

class dict(Generic[K, V]):

    @method
    def get(self, key: K) -> V: ...

    @method
    def items(self) -> list[tuple[K, V]]: ...
```

### 自動導出ルール

- module: `@namespace` + class名 → `pytra.core.list`
- symbol: class名 + メソッド名 → `list.extend`
- tag: 自動導出（`stdlib.method.extend` 相当）
- runtime 側の関数名変換（`list.extend` → `py_list_extend_mut` 等）は mapping.json の責務

### `@abi` 廃止

`@abi` は廃止する。理由:

- 未実装・未使用なので影響ゼロ
- arg mode（`ref` / `ref_readonly` / `value` / `value_readonly`）は不要と判断

### arg mode が不要な理由

議論の経緯:

1. 当初、escape 解析のヒントとして `ref_readonly`（この引数は変更しない）が必要と考えた
2. しかし `ref_readonly` でも関数に渡した時点で呼び出し元から追跡できなくなるため、escape 解析は「escape する」と判断せざるを得ない
3. `ref_readonly` は「この関数の中では変更しない」という局所情報であって、「この値は今後変わらない」という保証ではない。escape 解析にとって役に立たない
4. `value` / `value_readonly`（rc を剥がしてコピーで渡す）は外部 FFI 用に検討したが、runtime のラッパー関数が deref してから外部 API に渡せば済む。呼び出し側が rc を剥がす必要がない

結論: arg mode は `ref`（rc のまま渡す）の1種類だけで十分。明示する必要がないので、`@method` に引数を取らない。

### runtime ヘルパーの引数は全て rc 前提

runtime ヘルパー（`PyListExtend`, `PyListConcat` 等）は全て rc 付き（`Object<list<T>>` / `*PyList[T]`）を引数に取る。

理由:

- デフォルトが rc なので、ほとんどの呼び出しは rc 付きで渡される
- テンプレート/ジェネリクスがない言語（Go 等）で rc あり/なしの複数パターンを実装するのは非現実的
- エイリアス問題（`a.extend(a)` で self と引数が同じオブジェクト）があるため、rc を剥がして生の参照で渡すと dangling reference になる

エイリアス問題の具体例:

```python
a: list[int] = [1, 2, 3]
a.extend(a)  # self と x が同じオブジェクト
```

```cpp
// rc を剥がして渡すと壊れる
void extend(Object<list<int>>& self, const list<int>& x) {
    // self と x が同じ list を指している
    // extend が self に要素を追加 → 内部配列が再確保
    // → x の参照が無効になる（dangling reference → UB）
    for (auto& elem : x) {  // UB!
        self->push_back(elem);
    }
}
```

rc のまま渡せば rc が生存を保証するのでこの問題は起きない。

### concat (`a + b`) の扱い

`list + list` の concat は `PyListConcat(a, b)` のような rc 前提の runtime ヘルパーで処理する。

- emitter は `BinOp(Add, list, list)` を mapping.json で `PyListConcat` に写像するだけ
- emitter が rc を剥がして素のスライスを操作するのは禁止
- `PyListConcat` は rc を受けて rc を返す

## 現状との比較

| | 現状 | 新設計 |
|---|---|---|
| append | `@extern_method(module="pytra.core.list", symbol="list.append", tag="stdlib.method.append")` | `@method` |
| extend | 上記 + `@abi(args={"x": "value"})` | `@method` |
| sort | 上記 + `@abi(args={"key": "value"})` | `@method` |

## サブタスク

1. [ID: P6-REDESIGN-S1] `@namespace` と `@method` を parser に実装し、自動導出ルールを組み込む
2. [ID: P6-REDESIGN-S2] `containers.py` を新記法に書き換える
3. [ID: P6-REDESIGN-S3] `@extern_method` と `@abi` を廃止する（旧記法の parser 受理を停止）
4. [ID: P6-REDESIGN-S4] spec-east.md の `meta.runtime_abi_v1` を廃止する
5. [ID: P6-REDESIGN-S5] チュートリアル・ガイドの `@abi` 言及を削除する
6. [ID: P6-REDESIGN-S6] emitter guide を更新し、`@method` で宣言されたメソッドの runtime 実装ルールを記載する

## 未決事項

- `@method` と `@extern` の関係整理（`@extern` は関数用、`@method` はメソッド用？ それとも統合？）
- `@extern` も同様に短縮できるか
- 既存の `containers.py` の書き換え量

## 決定ログ

- 2026-03-28: 案A〜D を検討。案D（`@namespace` + `@method` 最小記述、自動導出）を推奨とした。
- 2026-03-28: arg mode（ref / ref_readonly / value / value_readonly）の4種類を検討。
- 2026-03-28: エイリアス問題（`a.extend(a)`）を発見。`ref_readonly` でも rc を剥がせないことを確認。
- 2026-03-29: `ref_readonly` は「この関数の中では変更しない」の局所情報でしかなく、escape 解析に役立たないと判断。arg mode は不要と結論。
- 2026-03-29: 外部 FFI でも runtime ラッパーが deref すればよく、`value` / `value_readonly` も不要と判断。
- 2026-03-29: `@abi` 廃止、arg mode 廃止、`@method` は引数なしのマーカーのみ、に決定。

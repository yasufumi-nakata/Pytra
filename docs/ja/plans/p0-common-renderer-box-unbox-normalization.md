# P0 CommonRenderer box/unbox normalization

最終更新: 2026-04-02

## 背景

C++ backend では `optional[T]` / general union / callable 引数の emit で、同じ意味の box/unbox・cast 正規化を backend 側で個別に持っている。その結果、runtime parity では次のような C++ 固有の崩れが起きた。

- `optional[int64]` を 2 回 deref して `*(*indent)` を生成する
- `std::function<T(U)>` 引数に不要な `object` lambda bridge を作る
- すでに target type に一致している式へ追加の boxing / unboxing を重ねる

これらは C++ の出力記法そのものではなく、「同じ意味変換を重複適用しない」という共通正規化の不足が原因である。backend 個別の止血だけでなく、CommonRenderer 側へ寄せて再発を防ぐ。

## 方針

- backend 非依存で判定できる box/unbox/cast の冪等化は CommonRenderer に移す
- backend は最終的な表現だけを担当する
  - C++: `*opt`, `std::get<T>`, `std::holds_alternative<T>` など
- 判定できない場合は fail-closed で現行 backend 実装へ戻す

## 対象

- `Box(Box(x))` の抑止
- `Unbox(Unbox(x))` の抑止
- `optional[T] -> T` の二重 unbox 抑止
- target type に一致済みの式への不要 cast / boxing 抑止
- callable 境界で stale な `call_arg_type=object` に引きずられる bridge の抑止

## 非対象

- C++ 固有の ownership / ref / `Object<T>` 生成規則
- `std::optional` / `std::variant` の具体的な記法選択
- EAST 自体の box/unbox node 生成廃止

## 完了条件

- CommonRenderer 側に box/unbox/cast 正規化の共通入口がある
- C++ emitter がその共通入口を使う
- `json_extended`, `json_indent_optional`, `json_unicode_escape`, `callable_higher_order` の C++ parity が PASS
- backend 固有コードに残る box/unbox の止血分岐が減っている

# `@extern` / `extern(...)` の使い方

`@extern` と `extern(...)` は、Pytra から外部実装や ambient global を参照するための独自記法です。  
正規仕様は [ABI仕様](../spec/spec-abi.md) を参照してください。

## 関数 extern

- トップレベル関数を外部実装へ委譲したいときは `@extern` を使います。
- 変換器は本体を生成せず、ターゲット側の実装を呼び出す前提で扱います。

```python
from pytra.std import extern

@extern
def sin(x: float) -> float:
    ...
```

### 将来: runtime 情報の指定（v2）

将来的に `@extern` の引数で runtime の配置情報を指定できるようになります。
これにより、ユーザーが独自のネイティブ関数を宣言し、全 backend から呼び出せるようになります。

```python
# pytra: builtin-declarations

@extern(module="my_game.physics", symbol="apply_gravity", tag="user.physics.gravity")
def apply_gravity(x: float, y: float, dt: float) -> float: ...
```

| 引数 | 意味 |
|---|---|
| `module` | 実装がある runtime モジュール（言語非依存） |
| `symbol` | runtime モジュール内での関数名 |
| `tag` | semantic_tag（emitter が意味を識別するキー） |

詳細は [spec-builtin-functions.md §10](../spec/spec-builtin-functions.md) を参照してください。

## 変数 extern

- 変数に `@extern` は付けられません。
- 変数 extern は `name = extern(...)` で書きます。

使い分けは次の 3 つです。

- `name: T = extern(expr)`
  - host fallback や runtime hook 初期化を行う変数 extern
- `name: Any = extern()`
  - 同名 ambient global
- `name: Any = extern("symbol")`
  - 別名 ambient global

```python
from typing import Any
from pytra.std import extern

document: Any = extern()
console: Any = extern("console")
```

補足:

- ambient global は現状 JS/TS backend 限定です。
- `document: Any = extern()` は `document` を、`console: Any = extern("console")` は `console` をそのまま参照する形に lower します。

<a href="../../ja/tutorial/README.md"><img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-2563EB?style=flat-square"></a>

> [!WARNING]
> This file is synchronized from `docs/ja/tutorial/README.md` and still requires manual English translation.

> Source of truth: `docs/ja/tutorial/README.md`

# チュートリアル

Pytra を初めて触る人向けの入口です。

## 3分で動かす

```python
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    print(add(3, 4))
```

この `add.py` を C++ に変換して実行:

```bash
./pytra add.py --output-dir out/add_case --build --run --exe add.out
```

出力:

```text
7
```

Rust に変換するなら:

```bash
./pytra add.py --target rs --output-dir out/rs_case
```

## 読む順番

1. [使い方](./how-to-use.md) — 実行手順、オプション、入力制約
2. [アーキテクチャ](./architecture.md) — パイプラインの全体像と各段の役割
3. [Python 互換性ガイド](../spec/spec-python-compat.md) — Python との違い、使えない構文
4. [エラーの見方](./troubleshooting.md) — 詰まったときに

ここまで読めば普通に使えます。以下は必要に応じて:

5. [発展的な使い方](./advanced-usage.md) — `@extern`, `@abi`, `@template`, nominal ADT 等
6. [仕様書トップ](../spec/index.md) — 言語仕様の正本
7. [開発運用ガイド](./dev-operations.md) — parity check, local CI（開発者向け）

## 関連リンク

- [仕様書トップ](../spec/index.md)
- [pylib モジュール一覧](../spec/spec-pylib-modules.md)
- [サンプル一覧](../../sample/README-ja.md)

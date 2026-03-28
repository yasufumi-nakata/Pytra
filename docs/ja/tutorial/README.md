<a href="../../en/tutorial/README.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

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
2. [サンプルを動かしてみる](./samples.md) — 18 件のサンプルプログラムで試す
3. [Python との違い](./python-differences.md) — 型注釈、import、使えない構文など
4. [エラーの見方](./troubleshooting.md) — 詰まったときに
5. [例外処理](./exception.md) — raise / try / except / finally の使い方
6. [Trait（インターフェース）](./trait.md) — 複数の振る舞い契約を型に付与する
7. [Union 型と isinstance ナローイング](./union-and-narrowing.md) — 複数の型を扱う方法と型の自動絞り込み

ここまで読めば普通に使えます。以下は必要に応じて:

8. [使えるモジュール](./modules.md) — よく使うモジュールと関数の紹介
9. [アーキテクチャ](./architecture.md) — パイプラインの全体像と各段の役割

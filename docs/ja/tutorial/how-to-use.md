<a href="../../en/tutorial/how-to-use.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# 使い方

Pytra を実際に動かすための実行手順ガイドです。

## まずこの 1 ファイルを動かす

`add.py`:

```python
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    print(add(3, 4))
```

C++ に変換して、build + run する最短手順:

```bash
./pytra add.py --output-dir out/add_case --build --run --exe add.out
```

出力:

```text
7
```

変換結果だけを見たいなら:

```bash
./pytra add.py --output-dir out/add_case
```

Rust に変換するなら `--target` を変えるだけ:

```bash
./pytra add.py --target rs --output-dir out/rs_case
```

## 対応言語

`--target` で指定できる言語:

`cpp`, `rs`, `cs`, `js`, `ts`, `go`, `java`, `kotlin`, `swift`, `ruby`, `lua`, `scala`, `php`, `nim`, `dart`, `julia`, `zig`

全言語で multi-file 出力（`--output-dir`）が正規パスです。

## 主なオプション

| オプション | 説明 |
|---|---|
| `--target <lang>` | 出力言語（既定: `cpp`） |
| `--output-dir <dir>` | 出力ディレクトリ（既定: `out/`） |
| `--build` | C++ のみ。変換後にコンパイル |
| `--run` | `--build` と併用。コンパイル後に実行 |
| `--exe <name>` | 実行ファイル名（`--output-dir` 配下に生成） |
| `--help` | ヘルプ表示 |

## 関連する仕様

- [利用仕様](../spec/spec-user.md) — 入力制約、テスト実行方法の詳細
- [Python との違い](./python-differences.md) — 型注釈、import ルール、使えない構文

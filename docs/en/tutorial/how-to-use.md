<a href="../../ja/tutorial/how-to-use.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# How to Use Pytra

This guide shows the execution steps for actually running Pytra.

## Run this one file first

`add.py`:

```python
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    print(add(3, 4))
```

The shortest path to transpile it to C++, build it, and run it is:

```bash
./pytra add.py --output-dir out/add_case --build --run --exe add.out
```

Output:

```text
7
```

If you only want to inspect the transpiled result:

```bash
./pytra add.py --output-dir out/add_case
```

If you want Rust instead, only change `--target`:

```bash
./pytra add.py --target rs --output-dir out/rs_case
```

## Supported languages

Languages accepted by `--target`:

`cpp`, `rs`, `cs`, `js`, `ts`, `go`, `java`, `kotlin`, `swift`, `ruby`, `lua`, `scala`, `php`, `nim`, `dart`, `julia`, `zig`

For all languages, multi-file output with `--output-dir` is the canonical path.

## Main options

| Option | Description |
|---|---|
| `--target <lang>` | Output language. Default: `cpp` |
| `--output-dir <dir>` | Output directory. Default: `out/` |
| `--build` | C++ only. Compile after transpilation |
| `--run` | Use with `--build`. Run after compilation |
| `--exe <name>` | Executable name to generate under `--output-dir` |
| `--help` | Show help |

## Related specifications

- [User specification](../spec/spec-user.md) — Input constraints and test execution details
- [Differences from Python](./python-differences.md) — Type annotations, import rules, unsupported syntax

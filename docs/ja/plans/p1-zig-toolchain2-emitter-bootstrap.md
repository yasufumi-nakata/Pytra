<a href="../../en/plans/p1-zig-toolchain2-emitter-bootstrap.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P1 Zig toolchain2 emitter bootstrap

最終更新: 2026-04-02

対象ID:
- P1-ZIG-EMITTER-S1
- P1-ZIG-EMITTER-S2

目的:
- `src/toolchain2/emit/zig/` に Zig emit 経路を追加し、toolchain2 パイプラインから Zig を選択できる状態にする。
- `src/runtime/zig/mapping.json` と `src/toolchain2/emit/profiles/zig.json` を追加し、lower/emit/parity の前提を揃える。

背景:
- Zig は旧 toolchain1 側には native emitter が存在するが、toolchain2 側には emit profile・mapping・CLI 経路が未整備である。
- parity check の正本は toolchain2 パイプラインなので、まずは toolchain2 から Zig を流せる bootstrap が必要である。

今回のスコープ:
- `toolchain2/emit/zig/` の追加
- `pytra-cli2` / `runtime_parity_check_fast.py` / target profile への Zig 経路追加
- `src/runtime/zig/mapping.json` の追加
- `src/toolchain2/emit/profiles/zig.json` の追加

非対象:
- Zig emitter の full rewrite
- fixture 全件 parity 完了
- hardcode lint 完全解消
- runtime API の追加修正

受け入れ基準:
1. toolchain2 が `--target zig` を lower/emit で受理する。
2. Zig runtime mapping/profile の必須ファイルが存在し、`check_mapping_json.py` を通る。
3. 少なくとも単一ケースで `emit + zig build-exe + run` が成功する。

決定ログ:
- 2026-04-02: 初手は bootstrap を優先し、toolchain2 側の Zig emit 経路・profile・mapping・parity 実行導線を先に揃える。full CommonRenderer 化は後続タスクで継続する。

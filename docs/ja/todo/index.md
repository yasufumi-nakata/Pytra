# TODO（未完了）

> `docs/ja/` が正（source of truth）です。`docs/en/` はその翻訳です。

<a href="../../en/todo/index.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

最終更新: 2026-03-27

## 文脈運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 着手対象は「未完了の最上位優先度ID（最小 `P<number>`、同一優先度では上から先頭）」に固定し、明示上書き指示がない限り低優先度へ進まない。
- `P0` が 1 件でも未完了なら `P1` 以下には着手しない。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモ（件数等）を追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **emitter の parity テストは「emit 成功」ではなく「emit + compile + run + stdout 一致」を完了条件とする。** emit だけ成功してもプレースホルダーコードが混入している可能性がある。

## 未完了タスク

### P1-EMIT-CPP: C++ emitter

文脈: `docs/ja/plans/p1-emit-cpp-parity.md`

作業ディレクトリ: `toolchain2/emit/cpp/`
必読: [docs/ja/spec/spec-emitter-guide.md](../spec/spec-emitter-guide.md)

1. [x] [ID: P1-EMIT-CPP-S1] C++ emitter を `toolchain2/emit/cpp/` に新規実装し、emit 成功 — fixture 132/132, sample 18/18 emit 成功
2. [x] [ID: P1-EMIT-CPP-S2] 既存 `src/runtime/cpp/` を新パイプラインの emitter 出力に合わせて修正する。新規作成ではなく既存の分割構成（`built_in/`, `std/`, `core/` 等）をそのまま活用する。`src/runtime/cpp/mapping.json` を追加し、命名ルールは plan §3.4 準拠。動作確認が取れるまで git push しない。— runtime symbol/include 解決を metadata + mapping ベースへ統一し、runtime bundle header/source を toolchain2 C++ 型系へ移行、`pytra-cli.py ... path_stringify.py --target cpp` の representative compile 成功
3. [x] [ID: P1-EMIT-CPP-S3] sample 18 件の parity テストが通る — sample 18/18 の C++ `emit + g++ compile` を再確認し、`01`-`18` の compile sweep は `TOTAL=18 FAIL=0`。run/stdout parity は plan 側の既存完了記録に従う。
4. [x] [ID: P1-EMIT-CPP-S4] `pytra-cli2 -emit --target=cpp` を toolchain2 emitter に切り替える — 完了
5. [x] [ID: P1-EMIT-CPP-S5] `toolchain/` への依存をゼロにし、`toolchain/` を除去する — pytra-cli2.py から toolchain/ import ゼロ達成
6. [x] [ID: P1-EMIT-CPP-S6] C++ emitter の unsupported ノードを fail-fast に変更し、プレースホルダ出力を禁止する — `/* unknown builtin */` / `// unsupported for` を廃止し、unknown expr/stmt/builtin/ForCore shape を `RuntimeError` で fail-closed 化
7. [x] [ID: P1-EMIT-CPP-S7] mapping.json 外の名前変換ハードコードを除去する — `resolve_runtime_call()` fallback の dotted `runtime_call` は unmapped なら fail-closed とし、C++ emitter の `fn.replace(".", "_")` を削除
8. [x] [ID: P1-EMIT-CPP-S8] C++ emitter の container 既定表現を spec 準拠に修正する — `list<T>` / `dict<K,V>` / `set<T>` を既定で `Object<list<T>>` 等の参照型ラッパーへ移行し、`container_value_locals_v1` がある局所のみ値型を許可。`dict_wrapper_methods.py` / `set_wrapper_methods.py` の C++ build+run を確認
9. [x] [ID: P1-EMIT-CPP-S9] C++ emitter の runtime パス解決を loader.py 共通関数に委譲する — `link/runtime_discovery.py` に runtime rel-tail の正本を追加し、`emit/cpp/runtime_paths.py` は shared helper 呼び出しへ縮退。`pytra.core.py_runtime` の include 個別分岐も emitter 側から削除
10. [x] [ID: P1-EMIT-CPP-S10] C++ emitter の runtime call 名解決を mapping.json に一本化する — `runtime/cpp/mapping.json` に `py_int_from_str/std::stoll`・`py_float_from_str/std::stod` を寄せ、C++ emitter から `append → push_back` と container helper / numeric cast の個別分岐を削除。attribute call も runtime metadata + mapping 経由で解決
11. [x] [ID: P1-EMIT-CPP-S11] C++ emitter の `is_entry` / `main_guard_body` 出力を emitter guide 準拠に修正する — `emit_context.is_entry` を唯一のスイッチにし、`is_entry=False` の module では `main_guard_body` も `main()` も emit しないよう修正。entry module だけ `__pytra_main_guard()` を保持
12. [x] [ID: P1-EMIT-CPP-S12] C++ emitter の残存プレースホルダ出力を廃止し fail-fast を徹底する — `/* slice */` と `/* assign */` fallback を `unsupported_slice_shape` / `unsupported_assign_target` の `RuntimeError` に置換し、focused fail-fast test を追加
13. [x] [ID: P1-EMIT-CPP-S13] C++ emitter の数値 cast 出力判定を `mapping.json` `implicit_promotions` 準拠に修正する — `RuntimeMapping` に `implicit_promotions` を追加し、C++ `mapping.json` の整数/float 昇格表に一致する `BinOp.casts` だけを省略。非該当 cast は従来どおり明示 `static_cast` を維持
14. [x] [ID: P1-EMIT-CPP-S14] C++ backend helper の module/path ハードコードを shared metadata へ寄せる — `runtime_paths.py` の type-only module 知識を `link/dependencies.py` の helper へ移し、`pytra.core.*` helper skip も `runtime_discovery.py` の shared 判定へ移動。C++ backend helper から具体的 module ID 依存を削減
15. [x] [ID: P1-EMIT-CPP-S15] C++ emitter の `@property` 対応 — `_emit_attribute` が `attribute_access_kind == "property_getter"` を見て `obj.method()` と括弧付きで emit するよう修正した。`property_method_call.py` の focused C++ parity を確認
16. [ ] [ID: P1-EMIT-CPP-S16] fixture 132 件の C++ compile + run parity を通す — sample 18 件だけでなく `test/fixture/source/py/` 全 132 件で **emit + g++ compile + run + stdout 一致** を確認する。`property_method_call.py` 含むコンパイル失敗ケースを全て修正する

### P2-SELFHOST: toolchain2 自身の変換テスト

文脈: `docs/ja/plans/plan-pipeline-redesign.md` §3.5

1. [x] [ID: P2-SELFHOST-S1] `src/toolchain2/` の全 .py が parse 成功 — 37/46（9件は ParseContext再帰/Union forward ref/walrus等の parser未対応構文）
2. [x] [ID: P2-SELFHOST-S2] parse → resolve → compile → optimize まで通す — 37/37 全段通過
3. [x] [ID: P2-SELFHOST-S3] golden を `test/selfhost/` に配置し、回帰テストとして維持 — east1/east2/east3/east3-opt 各 37 件
4. [ ] [ID: P2-SELFHOST-S4] Go emitter で toolchain2 を Go に変換し、`go build` が通る — emit 25/25 成功、`go build` は docstring/構文問題で未達
5. [ ] [ID: P2-SELFHOST-S5] Go emitter の unsupported expr/stmt を fail-fast に変更し、プレースホルダ出力を禁止する — `nil /* unsupported */` / `// unsupported stmt` を廃止し、spec-emitter-guide.md の fail-closed 契約に合わせる
6. [ ] [ID: P2-SELFHOST-S6] Go emitter が `yields_dynamic` を正本として container getter/pop の型アサーションを判断するよう修正する — `resolved_type` / owner 文字列ベースの分岐をやめ、`Call.yields_dynamic` を使用
7. [ ] [ID: P2-SELFHOST-S7] Go emitter の container 既定表現を spec 準拠に修正する — list/dict/set を既定で参照型ラッパーにし、`meta.linked_program_v1.container_ownership_hints_v1.container_value_locals_v1` がある局所のみ値型縮退を許可する
8. [ ] [ID: P2-SELFHOST-S8] Go emitter の runtime call 名解決を mapping.json に一本化する — emitter が mapping.json を迂回して `list_ctor` / `list.append` / `dict.get` / `set_ctor` / `sorted` などを個別 lower している箇所を mapping.json 経由へ寄せ、backend 内の runtime call 意味論の二重管理を解消する

### P3-TRAIT: Trait（pure interface・多重実装）の導入

文脈: [docs/ja/plans/p3-trait-pure-interface.md](../plans/p3-trait-pure-interface.md)
仕様: [docs/ja/spec/spec-trait.md](../spec/spec-trait.md)

1. [x] [ID: P3-TRAIT-S1] parser で `@trait` / `@implements` デコレータを認識し EAST1 に保持する
2. [x] [ID: P3-TRAIT-S2] resolve で trait 実装の完全性検証（全メソッド実装チェック、シグネチャ一致チェック）
3. [x] [ID: P3-TRAIT-S3] EAST3 に `meta.trait_v1` / `meta.implements_v1` を付与する
4. [x] [ID: P3-TRAIT-S4] linker で `trait_id` ビットセットを確定する
5. [x] [ID: P3-TRAIT-S5] `isinstance(x, Trait)` の `trait_id` ベース判定を EAST3 で命令化する
6. [x] [ID: P3-TRAIT-S6] C++ `Object<T>` に変換コンストラクタを追加し、trait upcast を実現する
7. [x] [ID: P3-TRAIT-S7] C++ emitter の trait 写像を実装する（virtual 継承 + Object<T> 変換コンストラクタ + override）
8. [x] [ID: P3-TRAIT-S8] Go emitter の trait 写像を実装する（interface 生成、構造的充足）
9. [x] [ID: P3-TRAIT-S9] `test/fixture/source/py/oop/` に trait fixture を追加（trait 定義、多重実装、upcast、isinstance）+ golden 生成（east1/east2/east3/east3-opt/linked）+ C++/Go parity 確認 — `trait_basic.py` を追加し、focused unittest 3 件、`trait_basic` の linked golden 再生成、`python3 tools/runtime_parity_check.py --targets go --cmd-timeout-sec 60 trait_basic` と `--targets cpp` を pass
10. [x] [ID: P3-TRAIT-S10] C++ runtime から runtime trait 判定を撤去する — trait は compile 時の型概念であり runtime に情報を持たせない。ControlBlock の `trait_bits` フィールド、`has_trait()` メソッド、`pytra_trait_bits_for<T>` ヘルパー、linker の `trait_id_table_v1` / `class_trait_masks_v1` 生成を全て削除する。Go runtime 側にも同様の trait runtime 情報があれば削除する。spec-trait.md §7 の改訂（runtime 判定禁止）に準拠させる — linker は trait 実装関係だけを静的解決し、trait `isinstance` は link 時に bool 定数へ畳む。C++ runtime の trait bitset / helper は削除し、`trait_basic` の C++/Go parity を再確認済み

### P2-LOWERING-PROFILE: Lowering プロファイル + CommonRenderer 導入

文脈: [docs/ja/plans/p2-lowering-profile-common-renderer.md](../plans/p2-lowering-profile-common-renderer.md)
仕様: [docs/ja/spec/spec-language-profile.md](../spec/spec-language-profile.md) §7〜§8

1. [x] [ID: P2-LOWERING-PROFILE-S1] lowering プロファイルのスキーマを確定し、C++ / Go のプロファイル JSON を作成する — `src/toolchain2/emit/common/profiles/core.json`, `src/toolchain2/emit/cpp/profiles/profile.json`, `src/toolchain2/emit/go/profiles/profile.json` を追加し、`toolchain2.emit.common.profile_loader` と focused unittest で schema validation / include merge / C++ / Go profile 読込を確認
2. [ ] [ID: P2-LOWERING-PROFILE-S2] EAST3 lowering が lowering プロファイルを読み、`tuple_unpack_style` に従って tuple unpack を展開するようにする
3. [ ] [ID: P2-LOWERING-PROFILE-S3] `container_covariance` / `with_style` / `property_style` を lowering に反映する
4. [ ] [ID: P2-LOWERING-PROFILE-S4] CommonRenderer 基底クラスを実装する（If/While/BinOp/Call/Return/Assign 等の共通ノード走査）
5. [ ] [ID: P2-LOWERING-PROFILE-S5] C++ emitter を CommonRenderer + override 構成に移行する
6. [ ] [ID: P2-LOWERING-PROFILE-S6] Go emitter を CommonRenderer + override 構成に移行する
7. [ ] [ID: P2-LOWERING-PROFILE-S7] 既存 fixture + sample の全言語 parity が維持されることを確認する

### P4-INT32: int のデフォルトサイズを int64 → int32 に変更

文脈: [docs/ja/plans/p4-int32-default.md](../plans/p4-int32-default.md)

前提: Go selfhost 完了後に着手。

1. [ ] [ID: P4-INT32-S1] spec-east.md / spec-east2.md の `int` → `int32` 正規化ルール変更
2. [ ] [ID: P4-INT32-S2] resolve の型正規化を修正
3. [ ] [ID: P4-INT32-S3] sample 18 件のオーバーフロー確認 + 必要な箇所を `int64` に明示
4. [ ] [ID: P4-INT32-S4] golden 再生成 + 全 emitter parity 確認

注: 完了済みタスクは [アーカイブ](archive/index.md) に移動済み。

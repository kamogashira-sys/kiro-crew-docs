# SSoT の版ごとの状態

- **位置づけ**: 版ごとに変わる SSoT の状態（基準点、`[要検証]` の項目、未確定（両併記）の項目、解消済みの記録、監視項目の現在値）の正本。状態区分の定義と各項目の測定方法は `.github/UPDATE_GUIDE.md` の §7.1・§14、監視の観点は同 §12
- **更新**: 版更新 PR の `implement` ⑤（`.github/UPDATE_GUIDE.md` §7.3）で、対象版の一次情報の実測に合わせて更新する
- **測定値の正本**: S1〜S29 の値は検証器の定数（`.github/UPDATE_GUIDE.md` §7.3 の許可定数）と、直近の版更新 PR 本文の③「SSoT 変更点」。本ファイルは状態だけを持ち、値の一覧を重複して持たない（監視項目の現在値を除く）

## 基準点

| 区分 | 版 | タグ commit |
|---|---|---|
| 現在の固定参照時点 | v0.9.0 | `99e6253` |
| 前回の固定参照時点 | v0.7.2 | `c67c506` |

固定参照時点の正本はルート `README.md` の「更新範囲と参照時点」。

## `[要検証]`

| ID | 項目 | 理由 | 解消する条件 |
|---|---|---|---|
| S12 | builtin App 数 | 出典が `src/kiro_crew/apps/builtins/*/app.json` で、`fetch-snapshot.sh` は `src/` を取得しないため測定できない。builtin App 台帳（`builtin-apps.md`）の20件は `21584ea`（v0.3.0）時点の値であり、以後の版の値として追認しない。v0.6.0・v0.7.2・v0.9.0 対応時点とも `[要検証]` | 版更新の G1 で `src/` の解析が承認され（`SRC_ANALYSIS: APPROVED`）、対象版のタグで実測した場合（`.github/WORKFLOW.md`「厳密な仕様調査での `src/` 解析確認」） |

## 未確定（両併記）

v0.9.0 対応時点。出典間で食い違い、裁定しない。

| ID・項目 | 食い違いの内容 |
|---|---|
| S3a 版の日付 | CHANGELOG 日付と Release 公開日（2系統）。v0.8.0 の CHANGELOG 日付は v0.8.0 タグ（2026-09-27）と v0.9.0 タグ（2026-10-08）で異なる |
| S11 拒否コマンドルール件数 | v0.9.0 の公式 security・hooks ページと仕様書に件数の記載がなく、確認できない（旧版の記載値は 137）。件数を現行値として書かない |
| S13 メッセージングチャネル数 | 公式ページ（設定ガイド7・一覧10）・README（10）・仕様書（10）で数が異なる |
| S24 コンテキストバジェット | 公式 memory ページ「~55K tokens」とリポジトリの固定値（33,000 文字）。v0.7.0 から。`check-consistency.py` の `DUAL_NOTATION` で両併記を検査する |
| S22 サンドボックスの呼称 | 公式 docs の `auto` と、内部ティアの `standard`。`check-consistency.py` の `DUAL_NOTATION` で検査する |
| S22 `strict` の隠蔽対象 | 公式 security ページ・`security.md`・`config.md`・`install.md`・CHANGELOG v0.8.0節で記述が異なる |
| S29 Autopilot（plan／approve／stage loop） | `modules/autopilot.md` は v0.7.2・v0.8.0 にあり v0.9.0 に無い。仕様書は「retired chat Autopilot」と記述、CHANGELOG に告知なし、公式 docs は記述を残す。`orchestrator.stage_timeout_seconds` は未確認 |
| Delegation gate | 公式 Subagents ページは拒否すると記述、`subagent.md`・CHANGELOG v0.8.0節は実行時のゲートなしと記述 |
| Windows の非サンドボックス実行の既定 | `windows-install.md`・`security.md` と、公式 `configuration/`・`security/`（README の fail-closed 文は v0.9.0 の README から消えた） |
| 画面名 | Customize（CHANGELOG v0.9.0節・公式 agents ページ）と Agent Capabilities（公式の他ページ） |

## 解消済み

| ID・項目 | 解消を確認した版更新 | 内容 |
|---|---|---|
| S25 クランプ範囲 | v0.6.0 対応 | 食い違いが解消済みと判明したため、両併記をやめた |
| S15 Subagent 自動サイジング上限・並行数の既定 | v0.9.0 対応 | `config.md` が `max_subagents` 0・`subagent_auto_max` 32 で `subagent.md` と一致（v0.8.0 で変更）。`check-consistency.py` の `DUAL_NOTATION` から外した |
| Agent Backends の選択肢数 | v0.9.0 対応 | 公式・CHANGELOG・仕様書が8種（DeepSeek Harness 追加）で一致 |
| S22 サンドボックスの値域 | v0.9.0 対応 | `auto`／`strict`／`off` で公式・`config.md`・`deep-dive` が一致（`strict` は v0.8.0 で追加） |
| 管理対象 MCP サーバ数 | v0.9.0 対応 | `mcp.md` の節と目録表がともに8サーバ |
| `memory.inject_activity` の食い違い | v0.9.0 対応 | v0.8.0 以降の仕様書が公式 memory ページと一致 |
| ブラウザの経路（公式とリポジトリ） | v0.9.0 対応 | `browser.md` と公式 `features/browser/` が一致 |

解消済みの食い違いを併記し続けない（`.github/UPDATE_GUIDE.md` §18）。

## 別項目と判明したもの

| ID | 内容 |
|---|---|
| S23 テレメトリ | 「①匿名利用テレメトリ（既定オン・5フィールド）」と「②`telemetry.enabled` のメトリクス／OTLP エクスポート（既定 OFF）」は別系統であり、食い違いではない。同一項目として既定値を比較しない |

## 監視項目の現在値

v0.9.0 対応時点。監視の頻度とリスクは `.github/UPDATE_GUIDE.md` §12。

| 項目 | 現在値 |
|---|---|
| S11 拒否ルール件数 | 確認できない（上の表） |
| S12 builtin App 数と `defaultEnabled` | `[要検証]`（上の表）。仕様書上の既定有効 builtin は `projects`・`command-bar` |
| S22 サンドボックス既定モード | `auto` |
| S23① 匿名利用テレメトリ | 送信フィールド5、既定オン（最初の送信は初回プライバシー開示まで保留） |
| S23② メトリクス／OTLP エクスポート | 既定 OFF |
| 既知ギャップ | v0.9.0 で8点＋リソース上限 |
| Crew log | v0.8.0 から既定オン（`KIROCREW_CREW_LOG=0` で無効） |
| `mcp.honour_auto_approve` | 既定 `true`（要再起動） |
| 出典間で食い違っている値 | 上の「未確定（両併記）」 |

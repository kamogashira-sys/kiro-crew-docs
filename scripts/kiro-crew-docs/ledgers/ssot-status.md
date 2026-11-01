# SSoT の版ごとの状態

- **位置づけ**: 版ごとに変わる SSoT の状態（基準点、`[要検証]` の項目、未確定（両併記）の項目、解消済みの記録、監視項目の現在値）の正本。状態区分の定義と各項目の測定方法は `.github/UPDATE_GUIDE.md` の §7.1・§14、監視の観点は同 §12
- **更新**: 版更新 PR の `implement` ⑤（`.github/UPDATE_GUIDE.md` §7.3）で、対象版の一次情報の実測に合わせて更新する
- **測定値の正本**: S1〜S29 の値は検証器の定数（`.github/UPDATE_GUIDE.md` §7.3 の許可定数）と、直近の版更新 PR 本文の③「SSoT 変更点」。本ファイルは状態だけを持ち、値の一覧を重複して持たない（監視項目の現在値を除く）

## 基準点

| 区分 | 版 | タグ commit |
|---|---|---|
| 現在の固定参照時点 | v0.11.1 | `fe6f5be` |
| 前回の固定参照時点 | v0.9.0 | `99e6253` |

固定参照時点の正本はルート `README.md` の「更新範囲と参照時点」。経由版は v0.10.0・v0.11.0（`PIN.json` の `via`）。

## `[要検証]`

v0.11.1 対応時点。該当する項目は**ありません**。

| ID | 項目 | 状態 |
|---|---|---|
| S12 | builtin App 数 | **解消**（v0.11.1 対応）。依頼者が `src/` の解析を承認し（`SRC_ANALYSIS: APPROVED`）、v0.11.1 のタグで実測した。ディレクトリ数と `defaultEnabled` の値は builtin App 台帳（`builtin-apps.md`）。v0.9.0・v0.10.0・v0.11.0 時点の件数は未実測（導入版は判定していない） |

`src/` を出典とする値は、`fetch-snapshot.sh` が `src/` を取得しないため、承認（G1）を得て別に測るまで `[要検証]` に戻る（`.github/UPDATE_GUIDE.md` §7.1）。

## 未確定（両併記）

v0.11.1 対応時点。出典間で食い違い、裁定しない。値は本ファイルに書かない（各ページと `04_reference/05_limits.md` を参照）。

### 継続（前回までの項目）

| ID・項目 | 食い違いの内容 |
|---|---|
| S3a 版の日付 | CHANGELOG 日付と Release 公開日（2系統）。16版中15版で食い違い、v0.11.1 のみ一致。v0.8.0 の CHANGELOG 日付は v0.8.0 タグと v0.9.0 タグ以降で異なる |
| S11 拒否コマンドルール件数 | v0.11.1 の公式 security・hooks ページと仕様書に件数の記載がなく、確認できない。件数を現行値として書かない |
| S13 メッセージングチャネル数 | 公式ページ（設定ガイド7・一覧10）・README（10）・仕様書（10）で数が異なる |
| S24 コンテキストバジェット | 公式 memory ページとリポジトリの固定値。`check-consistency.py` の `DUAL_NOTATION` で両併記を検査する |
| S22 サンドボックスの呼称 | 公式 docs の `auto` と、内部ティアの `standard`。`check-consistency.py` の `DUAL_NOTATION` で検査する |
| S22 `strict` の隠蔽対象 | 公式 security ページ・`security.md`・`config.md`・`install.md`・CHANGELOG v0.8.0節で記述が異なる |
| Windows の非サンドボックス実行の既定 | `windows-install.md`・`security.md` と、公式 `configuration/`・`security/`。KAS の扱いが加わった（`windows-install.md`）。README の fail-closed 文は v0.9.0 以降の README に無い |
| S29 Autopilot（plan／approve／stage loop） | `modules/autopilot.md` は v0.11.1 にも無い。仕様書は「retired chat Autopilot」と記述、CHANGELOG に告知なし、公式 docs は記述を残す。`orchestrator.stage_timeout_seconds` は未確認 |
| Delegation gate | 公式 Subagents ページは拒否すると記述、`subagent.md`・CHANGELOG v0.8.0節は実行時のゲートなしと記述 |
| 画面名 | Customize（CHANGELOG v0.9.0節・公式 agents ページ）と Agent Capabilities（公式の他ページ） |
| `cron_remove_all` と公式 CLI | 公式 cron・cli-reference ページは `kirocrew cron remove-all` を記述、`mcp.md`・`cli.md` は CLI twin なし・`cron add/list/remove` のみ |
| 「Two new apps」と builtin App の実装年代 | CHANGELOG v0.3.0節は `personal_shopper`・`issue_radar` を新規と記述、実装は v0.1.2 以前から存在（台帳 `builtin-apps.md`） |

### 新規（v0.11.1 対応で追加）

| ID・項目 | 食い違いの内容 |
|---|---|
| 既定ハーネス | 公式 `features/agent-backends/` は Kiro CLI が既定。リポジトリ（`harness-parity.md`・`config.md`・CHANGELOG v0.11.0節）は新規インストールの既定を KAS と記述。`overview.md` は Kiro CLI を既定と読める記述を残す。既存インストールの移行の仕様は確認できない |
| SSH agent の転送 | 公式 security ページは明示的な同意の後だけ（既定オフ）。`security.md` は、`~/.ssh` が読めるティア（`off`・`standard`・`cc`）では同意なしで `SSH_AUTH_SOCK` を保持すると記述。変更した版は CHANGELOG に説明がなく未確認。`security-deep-dive.md` と `security.md` の食い違いは解消済み |
| Pi の MCP | 公式 agent-backends ページは Pi が Crew の MCP ツールを受け取らないと記述。CHANGELOG v0.10.0節・`harness-parity.md` は Pi セッションが Crew の MCP サーバを受け取ると記述 |
| デスクトップが kiro-cli を同梱するか | 公式 `installation/` は同梱と記述。CHANGELOG v0.11.0節・`install.md`・`desktop-app.md` は同梱しないと記述 |
| Dynamic Dashboard の Preview | 公式 agents ページは Feature Preview で有効にすると記述。CHANGELOG v0.10.0節・`artifacts.md` は Preview を必要としないと記述 |
| 管理対象 MCP サーバ数 | `mcp.md` は10サーバ、`mcp-shareability.md` は9サーバ（`kirocrew-mate` なし）。v0.9.0 で解消した食い違いが v0.11.1 で再発 |
| Side Chat の読み取り専用ツールの対象バックエンド | 公式 Chat ページは Kiro CLI バックエンド、`side.md`・CHANGELOG v0.10.0節・v0.11.0節は複数バックエンド |
| 音声の既定プロバイダ（piper） | 公式 voice・configuration ページは Piper を既定と記述。`voice-streaming.md` は組み込みエンジンが既定で `piper` は削除済みと記述（CHANGELOG に説明なし） |
| 呼称 Mate | CHANGELOG v0.11.0節・仕様書は Mate、公式ページは crewmate のまま。識別子・設定キー・API パスは crewmate |
| `decisions.history_budget_chars` の既定 | 公式 configuration ページは `0`、`config.md` の既定値変更表は 0 から 2000 への変更を記載（データクラスの定義行は `docs/` 内に無い） |
| Usage タブの Estimated Tokens カード | 公式 `system/` ページは記述、CHANGELOG v0.11.0節は表示しなくなったと記述 |
| Node.js の下限 | 公式 `installation/` は 22+、`install.md`・`cli.md` は 22.12.0 |

## 解消済み

| ID・項目 | 解消を確認した版更新 | 内容 |
|---|---|---|
| S25 クランプ範囲 | v0.6.0 対応 | 食い違いが解消済みと判明したため、両併記をやめた |
| S15 Subagent 自動サイジング上限・並行数の既定 | v0.9.0 対応（v0.11.1 でも維持） | `config.md` が `max_subagents` 0・`subagent_auto_max` 32 で `subagent.md` と一致 |
| Agent Backends の選択肢数 | v0.9.0 対応（v0.11.1 でも維持） | 公式・CHANGELOG・仕様書が8種で一致 |
| S22 サンドボックスの値域 | v0.9.0 対応（v0.11.1 でも維持） | `auto`／`strict`／`off` で公式・`config.md`・`deep-dive` が一致 |
| `memory.inject_activity` の食い違い | v0.9.0 対応（v0.11.1 でも維持） | 仕様書が公式 memory ページと一致 |
| ブラウザの経路（公式とリポジトリ） | v0.9.0 対応（v0.11.1 でも維持） | `browser.md` と公式 `features/browser/` が一致 |
| S12 builtin App 数の未実測 | v0.11.1 対応 | `src/` の実測で確定（`[要検証]` の表） |
| SSH agent: `security-deep-dive.md` と `security.md` | v0.11.1 対応 | `security-deep-dive.md` が `security.md` と同じ内容に書き換わった（公式との食い違いが新規に生じた。上の表） |
| `kirocrew cron --hide-in-chat` の説明 | v0.11.1 対応 | 「挙動の説明が見つからない」は本サイトの誤りで、`learn-cron-dashboard.md` に説明があった（v0.9.0 にもあった） |
| `dashboard.dynamic_dashboard_cards` とスイッチの対応 | v0.11.1 対応 | `learn-cron-dashboard.md`・`artifacts.md`・CHANGELOG v0.10.0節で確認 |
| `slack.trusted_bot_ids` の既定 | v0.11.1 対応 | `slack-gateway.md` に記載がある（v0.9.0 にもあった見落とし） |
| `contributes.sessionControls` の仕様 | v0.11.1 対応 | 公式 `apps/manifest/` に記載がある（v0.9.0 時点で既にあった見落とし） |

解消済みの食い違いを併記し続けない（`.github/UPDATE_GUIDE.md` §18）。

## 別項目と判明したもの

| ID | 内容 |
|---|---|
| S23 テレメトリ | 「①匿名利用テレメトリ（既定オン・5フィールド）」と「②`telemetry.enabled` のメトリクス／OTLP エクスポート（既定 OFF）」は別系統であり、食い違いではない。同一項目として既定値を比較しない |

## 監視項目の現在値

v0.11.1 対応時点。監視の頻度とリスクは `.github/UPDATE_GUIDE.md` §12。

| 項目 | 現在値 |
|---|---|
| S11 拒否ルール件数 | 確認できない（上の表） |
| S12 builtin App 数と `defaultEnabled` | 24件（v0.11.1 の `src/` 実測）。既定有効は2件（`command_bar`・`projects`） |
| S22 サンドボックス既定モード | `auto` |
| S23① 匿名利用テレメトリ | 送信フィールド5、既定オン（最初の送信は初回プライバシー開示まで保留） |
| S23② メトリクス／OTLP エクスポート | 既定 OFF |
| 既知ギャップ | v0.11.1 で9点＋リソース上限（v0.9.0 は8点） |
| Crew log | v0.8.0 から既定オン（`KIROCREW_CREW_LOG=0` で無効） |
| `mcp.honour_auto_approve` | 既定 `true`（要再起動） |
| 既定ハーネス | 新規インストールは KAS（CHANGELOG v0.11.0節。公式ページは Kiro CLI。上の表） |
| 出典間で食い違っている値 | 上の「未確定（両併記）」 |

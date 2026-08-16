# App の仕組み

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/apps/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**: `src/kiro_crew/apps/builtins/*/app.json`（全20件を機械抽出）
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [builtin App 20件](#builtin-app-20件)
- [App SDKとマニフェスト](#app-sdkとマニフェスト)
- [権限モデル（advisory）](#権限モデルadvisory)
- [未確認事項](#未確認事項)

---

## builtin App 20件

`src/kiro_crew/apps/builtins/` の実測で**20件**確認されています。**既定で有効なのは Task Runner（ディレクトリ名 `projects`）の1件のみ**（`app.json` の `defaultEnabled: true`）。他19件は App Store で opt-in するアプリです。

> **ディレクトリ名と表示名が異なるものがあります**: `projects`→**Task Runner**／`file_explorer`→**Files**／`md_notebook`→**Notes**／`auto_research`→**Research Lab**

| # | ディレクトリ名 | 表示名 | 既定有効 | 概要 |
|---|--------------|-------|:---:|------|
| 1 | `agent_worlds` | Agent Worlds | – | 稼働中のエージェントをアニメーションのピクセルワールドのキャラクターにする |
| 2 | `auto_improvement` | Auto-Improvement | – | GitHubリポジトリを変更する前に測定する。measurement-firstの自己改善 |
| 3 | `auto_research` | Research Lab | – | 複数サイクルの調査キャンペーンを実行し続ける |
| 4 | `channels` | Channels | – | 複数のエージェントが問題に取り組む共有ルーム |
| 5 | `code_review_sage` | Code Review Sage | – | GitHubのPull Requestを深くレビューし、変更点を判定する |
| 6 | `crew_companion` | Crew Companion | – | 作業のペースを整えるデスクトップコンパニオン |
| 7 | `design_critique` | Design Critique | – | 同僚に見せる前に実行できるデザイン批評 |
| 8 | `dev_fleet` | Dev Fleet | – | Kiro Crew自身の開発作業のためのコントロールパネル |
| 9 | `file_explorer` | **Files** | – | Kiro Crewが動作するマシン上のファイルを閲覧・読み込み |
| 10 | `issue_radar` | Issue Radar | – | 記憶するIssueトリアージアシスタント |
| 11 | `md_notebook` | **Notes** | – | gitリポジトリに保存されるMarkdownノートブック |
| 12 | `meetings` | Meetings | – | AI会議アシスタント。ライブ会議を文字起こし |
| 13 | `mochi` | Mochi | – | 画面上に常駐するデスクトップコンパニオン |
| 14 | `ops_mission_control` | Ops Mission Control | – | 自律的な運用初動対応者。アラーム・ページを監視 |
| 15 | `papyrus` | Papyrus | – | ライブPDFプレビュー付きのLaTeX論文エディタ |
| 16 | `personal_shopper` | Personal Shopper | – | 実店舗を調査するパーソナルアドバイザー |
| 17 | `pptx_maker` | PPTX Maker | – | チャットで説明したデッキから実際の.pptxを生成 |
| 18 | **`projects`** | **Task Runner** | **✅ 有効** | マルチステップの作業を渡し、無人で完了まで実行させる |
| 19 | `spec_builder` | Spec Builder | – | Kiro Crew内での仕様駆動開発 |
| 20 | `workflows` | Workflows | – | 動的ワークフロー（Pythonスクリプト等）の作成・実行・観察 |

## App SDKとマニフェスト

各Appは `app.json` マニフェストで宣言されます。`permissions` フィールドでAPI・イベント・MCPツールを宣言し、未宣言のものはエラーになります。

## 権限モデル（advisory）

> **重要**: 一次情報（`security.md`）が明記する通り、**Appの権限モデルは現時点で advisory（勧告的）のみです**。`apps/permissions.py` の `validate_permissions`／`format_permissions_summary` は配線されておらず（テストでのみ実行）、`check_tool_permission` は空の許可リストに対してfail openします。

**実効的な封じ込め**は以下によって行われます:

- HTTP app-tokenのスコープ（`token_auth.py`）
- OSサンドボックス
- `agent.apps_allow_third_party` のオフスイッチ（既定deny。JSON boolean `true` のみ受理し、config errorではfail closed）

インプロセスでの権限ゲーティングは `app-sandbox-roadmap.md`（トラッキング中）で追跡されています。

## 未確認事項

- なし（builtin App一覧は `app.json` 20件の機械抽出、権限モデルは `security.md` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/apps/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- 自律実行（Task Runner）: [06_autonomy.md](06_autonomy.md)
- セキュリティ: [09_security.md](09_security.md)

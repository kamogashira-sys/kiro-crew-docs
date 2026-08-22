# App の仕組み

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/apps/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: `src/kiro_crew/apps/builtins/*/app.json`（全20件を機械抽出）
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [builtin App 20件](#builtin-app-20件)
- [App SDKとマニフェスト](#app-sdkとマニフェスト)
- [権限モデル（advisory）](#権限モデルadvisory)
- [v0.3.0での変更](#v030での変更)
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

## v0.3.0での変更

### 「2つの新App」という表現と実装年代の食い違い（裁定しない）

v0.3.0のCHANGELOG（93行）は「**### Two new apps, and a store worth browsing**（2つの新しいAppと、閲覧に値するストア）」という見出しで **Personal Shopper** と **Issue Radar Crews** を挙げています。**しかしこの2つのAppの実装は、v0.3.0より前から存在します。** 本サイトは裁定せず両方を記載します。

| 観点 | 確認できた事実 |
|------|--------------|
| **CHANGELOGの立場** | v0.3.0節93行が「Two new apps」として Personal Shopper（95行）・Issue Radar **Crews**（98行）を発表している |
| **`personal_shopper`の実装年代** | `64060f3`（本サイトがv0.2.0として固定している時点）に既に `app.json` が存在し、**その内容は`21584ea`と完全に同一**（`diff`で差分0） |
| **`issue_radar`の実装年代** | `64060f3`に存在。さらに**v0.1.2のCHANGELOG（`64060f3`版628行）に「Shipping in the box」のbuiltin App 6件の1つとして「Issue Radar (GitHub/GitLab triage that remembers its notes)」と記載**されている |
| **表示名** | `issue_radar/app.json` の `displayName` は `21584ea`でも「**Issue Radar**」のままで、CHANGELOG v0.3.0が使う「Issue Radar **Crews**」という名称は`app.json`に反映されていない |

**なぜCHANGELOGが「新App」としているのか（機能が大幅に拡張されたのか、発表のタイミングの都合か等）は公式に説明がないため、本サイトは推測しません。** 上記builtin App 20件の表に両Appは既に含まれています（16番・10番）。

出典: CHANGELOG.md v0.3.0節 93・95・98行（`21584ea`）／v0.1.2節 628行（`64060f3`）／`src/kiro_crew/apps/builtins/{personal_shopper,issue_radar}/app.json`（`64060f3`・`21584ea`両方で実測）。

### App Storeの刷新

**Discover が編集キュレーションを描画するようになりました。** 従来の1つのフラットなリストではなく、**editorial spotlights（編集による注目枠）・themed collections（テーマ別コレクション）・category rails（カテゴリのレール）**をキュレーター用アートワークとともに表示します。

出典: CHANGELOG.md v0.3.0節 101行（`21584ea`）。

### Appのイベントスコープが限定された（セキュリティ）

**インストール済みAppは、manifestが宣言したイベントスコープのみを受け取ります。** ユーザーのチャット・スケジュールジョブの結果・他Appの活動を**観測できなくなりました**。

出典: CHANGELOG.md v0.3.0節 212行（`21584ea`）。上記「[権限モデル（advisory）](#権限モデルadvisory)」は`app.json`の`permissions`宣言が**インプロセスでは強制されていない**ことを述べていますが、**イベントスコープについてはv0.3.0で実際に制限が入った**ことになります。両者は別のレイヤーの話です。セキュリティ全体は [09_security.md](09_security.md) を参照してください。

### その他

- **Meetingsが文字起こしを保持する** — エージェントのノートの横に保存・表示され、リロードしても残ります（103行）
- **Code Review Sageに理由を聞ける** — レビュー投稿後もレビュアーが応答可能なまま残るため、指摘についてやり直さずに質問できます（105行）
- **Research LabとSpec Builderが自分のモデルを選ぶ** — 常にチャットの既定モデルにフォールバックするのをやめました（107行）
- **公開デプロイが確認を求める** — artifactを公開する際に明示的な承諾が必要になり、運用者はこの経路を完全に閉じることもできます（109行。Artifact Deployの詳細は [12_artifacts.md](12_artifacts.md) 参照）

## 未確認事項

- なし。**v0.3.0対応時（2026-08-22）に`21584ea`のfull cloneで`src/kiro_crew/apps/builtins/*/`を直接実測し、20件・`defaultEnabled: true`は`projects`のみを再確認済み**。以前の版で「スナップショットに`src/`が含まれないため再現・再計数できない」としていた制約は、full cloneによる実測で解消しました（台帳は `05_meta/ledger-builtin-apps.md`）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/apps/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- 自律実行（Task Runner）: [06_autonomy.md](06_autonomy.md)
- セキュリティ: [09_security.md](09_security.md)

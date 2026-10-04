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
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## builtin App 20件

`src/kiro_crew/apps/builtins/` の実測で**20件**確認されています。**既定で有効なのは Task Runner（ディレクトリ名 `projects`）の1件のみ**（`app.json` の `defaultEnabled: true`）。他19件は App Store で opt-in するアプリです。

> **ディレクトリ名と表示名が異なるものがあります**: `projects`→**Task Runner**／`file_explorer`→**Files**／`md_notebook`→**Notes**／`auto_research`→**Research Lab**

> **件数の時点**: 下表の20件は v0.3.0（`21584ea`）の full clone での実測です。v0.7.2 のスナップショットには `src/` が含まれないため、**v0.7.2 時点の builtin App の件数は未確認**です。

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

各Appは `app.json` マニフェストで宣言されます。`permissions` フィールドでAPI・イベント・MCPツールを宣言し、未宣言のものはエラーになります。v0.7.0 で加わったマニフェスト項目・App SDK・プラグインの取り込みは「[v0.7.0での変更](#v070での変更)」を参照してください。

## 権限モデル（advisory）

> **重要**: 一次情報（`security.md`）が明記する通り、**Appの権限モデルは現時点で advisory（勧告的）のみです**。`apps/permissions.py` の `validate_permissions`／`format_permissions_summary` は配線されておらず（テストでのみ実行）、`check_tool_permission` は空の許可リストに対してfail openします。

**実効的な封じ込め**は以下によって行われます:

- HTTP app-tokenのスコープ（`token_auth.py`）
- OSサンドボックス
- `agent.apps_allow_third_party` のオフスイッチ（既定deny。JSON boolean `true` のみ受理し、config errorではfail closed）

インプロセスでの権限ゲーティングは `app-sandbox-roadmap.md`（トラッキング中）で追跡されています。

## v0.7.0での変更

### プラグインの取り込み（`kirocrew app import`）

**他のエージェントハーネス向けに書かれたプラグインパッケージを、インストール可能な Kiro Crew の App に変換できます。** 変換はパッケージ内のコードを**一切実行しません**。

```bash
kirocrew app import /path/to/plugin
kirocrew app import /path/to/plugin --install
```

| 観点 | 内容 |
|------|------|
| **入力** | マニフェストを宣言したプラグインディレクトリ。パッケージ直下の `plugin.json`（`$schema` が `https://agent-plugins.org/schemas/` で始まるもののみ）、または `.*-plugin/plugin.json`（`.codex-plugin`・`.claude-plugin`・`.cursor-plugin` など）を探します。どちらもシンボリックリンク経由では受け付けません |
| **変換されるもの** | `skills`（リソースをコピー）・`mcpServers`。`name`・`version`・`description` などのメタデータは `app.json` に写されます |
| **変換されないもの** | `apps`・`hooks` は**報告のみ**で変換されません。パッケージ内のプログラムを起動するMCPサーバ（`command`/`args`/`cwd` がパッケージ相対）も、サーバ単位で拒否して報告します |
| **安全性** | パッケージのコードを import・評価・起動しません（変換時も変換後も）。宣言パスは `./` で始まり、`..` を含まず、パッケージルートの外に解決されないことが必要で、外れると変換全体が失敗します（`resource_outside_root`）。コピー中に見つかったリンクはたどらずスキップして報告します |
| **出力** | `--out` の既定は `./<app名>-app`。変換の記録は `app.json` の `importedPlugin` ブロックに残ります（`mapped`・`unmapped`・`warnings`） |
| **インストール** | `--install` を付けると、ローカルインストールまで続けて行います。付けない場合は `kirocrew app install` の実行行を表示します。インストールした App は（他のローカルインストールと同じく）無効のままで、`kirocrew app enable <name>` が別の手順です |

フック・ツール・サービスなど「パッケージ内のコード」側は変換の対象外で、`modules/harness-plugin-mapping.md` は Codex・openclaw・hermes・grok-build のいずれについても**フックはインストール済みAppで扱えない**と記述しています。

出典: CHANGELOG.md v0.7.0節 400-402行（`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/apps/>（「Import a plugin package」節。Page updated 表記あり）
**出典**（変換仕様）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/plugin-import.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（ハーネス別の対応）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-plugin-mapping.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2。185-208行）

### Appがセッションを操作できる（Appごとに既定オフ）

**App は、trust dialog で許可した場合に限り、セッションを開始・誘導（steer）・停止できます。** この許可は **App ごとに既定オフ**です。あわせて、スケジュールジョブを持つ App のレールアイコンに、ジョブの実行中・完了・失敗の状態が表示されます。

出典: CHANGELOG.md v0.7.0節 403-406行（`c67c506`）／公式 <https://kiro.dev/docs/crew/apps/>（「Apps that act on sessions」節）。

### Apps → Discover（ソースとレビュー tier で絞り込み）

App のストアは **Apps → Discover** から開きます。カタログを**ソース**と**レビュー tier**で絞り込め、ピン留めした外部レジストリはカタログ上にラベルと tier を表示するため、インストール前に出どころと審査の程度を確認できます。組み込みレジストリは引き続き KiroCrew リポジトリへの Pull Request でキュレーションされます。外部レジストリの追加は明示的な信頼の判断で、その App もインストールダイアログとローカルポリシーの対象です。

出典: CHANGELOG.md v0.7.0節 397-399行（`c67c506`）／公式 <https://kiro.dev/docs/crew/apps/>（「Discover apps by source and review tier」節）。

### マニフェストとApp SDKの追加

| 項目 | 内容 |
|------|------|
| `contributes.panelTabs` | チャットのサイドパネルにタブを追加（**最大8**）。App が有効な間だけマウント |
| `contributes.fileMenuItems` | ファイルのオーバーフローメニュー・ワークスペースツリー・フォルダ行にアクションを追加（**最大10**）。エンドポイントは App のAPI権限の対象 |
| `dependencies.optionalCommands` | 検出して報告するがインストールを止めないシステムコマンド（既定 `[]`） |
| `ctx.scrub.outbound(text)` | 外に出す前に資格情報と持ち出しURLを伏せる。**Gateway 内で動く `backend.hooks.*` のみ**で利用可（`kirocrew-client` を使う独立バックエンドプロセスには渡されない） |
| `ctx.audit.record(...)` | App に帰属するセキュリティイベントを、Gateway と同じ監査ログに追記（ベストエフォート。同じく Gateway 内フックのみ） |
| MCPサーバの埋め込みUI | Gateway スタブ経由のサーバのUIがダッシュボードの色・フォント・角丸・影を継承。**Developer Mode を有効にし**、Developer → MCP Management でルーティングしたサーバが対象 |

`contributes.sessionControls`（コンポーザ横の最大2つのコントロール）は v0.6.0 の CHANGELOG（799行）で追加済みです。

> **最小版のキー名**: 公式 manifest ページの最小 Gateway 版キーは、v0.6.0 対応時の取得内容では `minCrewVersion`、v0.7.2 対応時の取得内容では **`minKiroCrewVersion`** です（`apps.md`・`apps/publishing/` も同様）。リポジトリの `app-kit/manifest-reference.md` は v0.6.0 タグの時点で既に `minKiroCrewVersion` と記載しています。旧キー名の扱いは公式・仕様書ともに記載がありません。

出典: CHANGELOG.md v0.7.0節 225-235行（`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/apps/manifest/>・<https://kiro.dev/docs/crew/apps/sdk/>（Page updated 表記あり）
**出典**（キー名）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/manifest-reference.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2。20行）

### その他

- **Dev Fleet の pod ツール** — Dev Fleet アプリを Apps → Library で有効にすると、エージェントのセッションが worktree の pod を起動し、アドレス・ポート・短命トークンを受け取れます（127-130行。ツール名は [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md) 参照）
- **Ops Mission Control が incident.io をプロバイダとして受け付ける**（405-406行）

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

- **v0.7.2 時点の builtin App の件数**（v0.7.2 のスナップショットに `src/` が含まれないため再計数できない。上表の20件は v0.3.0 時点の実測）
- `minCrewVersion`（旧キー名）を書いたマニフェストの扱い（公式・仕様書ともに記載なし）
- v0.3.0 時点の件数については、**v0.3.0対応時（2026-08-22）に`21584ea`のfull cloneで`src/kiro_crew/apps/builtins/*/`を直接実測し、20件・`defaultEnabled: true`は`projects`のみを再確認済み**（台帳は `05_meta/ledger-builtin-apps.md`）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/apps/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- 自律実行（Task Runner）: [06_autonomy.md](06_autonomy.md)
- セキュリティ: [09_security.md](09_security.md)

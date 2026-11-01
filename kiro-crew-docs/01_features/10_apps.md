# App の仕組み

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/apps/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: `src/kiro_crew/apps/builtins/*/app.json`（全24件を機械抽出）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**（v0.3.0 時点の20件）: 同上（全20件を機械抽出。参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [builtin App 24件](#builtin-app-24件)
- [App SDKとマニフェスト](#app-sdkとマニフェスト)
- [権限モデル（advisory）](#権限モデルadvisory)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [MCP App がチャットへ送るメッセージ](#mcp-app-がチャットへ送るメッセージ)
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## builtin App 24件

`src/kiro_crew/apps/builtins/` の v0.11.1 の実測で**24件**確認されています。`defaultEnabled: true` は **Command Bar（ディレクトリ名 `command_bar`）と Task Runner（`projects`）の2件**で、他22件は `defaultEnabled: false` の App Store で opt-in するアプリです。24件すべての `app.json` に `defaultEnabled` のキーがあります。

仕様書の記述も実測と一致します。`modules/app-kit-platform.md` 1762-1765行は、既定有効の builtin を `manager._DEFAULT_ON_BUILTINS` として `projects`（Task Runner）と `command-bar`（Command Bar。サイドバーの項目を足さず、クイック検索の操作を置き換える）の 2 件と記述します。`modules/command-bar.md` 1-14行は、Command Bar は `defaultEnabled` が TRUE で、機能の設定キーはなく、App の有効状態がスイッチだと記述します。

> **件数の履歴**: v0.3.0（`21584ea`）の full clone での実測は20件で、既定有効は Task Runner の1件のみでした。**v0.11.1 の実測で、4件（`aws_control`・`command_bar`・`design_tweak`・`project_scaffolder`）が加わった24件になっています。この4件がどの版で加わったかは未確認です**（本サイトが `src/` を実測したのは v0.3.0 と v0.11.1 の2点で、間の版の `src/` は取得していません）。以前の本ページは、Command Bar と AWS Control が表の20件に含まれないと書いていました。v0.11.1 の実測では、両方とも24件に含まれます。

**出典**（builtin App の実測）: KiroCrew v0.11.1 の `src/kiro_crew/apps/builtins/*/app.json`（全24件を機械抽出。本サイトが `src/` を解析したのは、この builtin App の実測だけです）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**（既定有効の builtin）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/app-kit-platform.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。1762-1765行）
**出典**（Command Bar）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/command-bar.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。1-14行）

> **ディレクトリ名と表示名が異なるものがあります**: `projects`→**Task Runner**／`file_explorer`→**Files**／`md_notebook`→**Notes**／`auto_research`→**Research Lab**／`project_scaffolder`→**Create Folders From Project**

> **概要欄の時点**: 下表の概要は v0.11.1 の `app.json` の `description` に基づきます。v0.3.0 時点の20件の表示名と `description` の先頭50文字は、v0.11.1 の `app.json` と全件一致しました。追加4件の概要は、`description` の要約です。

| # | ディレクトリ名 | 表示名 | 既定有効 | 概要 |
|---|--------------|-------|:---:|------|
| 1 | `agent_worlds` | Agent Worlds | – | 稼働中のエージェントをアニメーションのピクセルワールドのキャラクターにする |
| 2 | `auto_improvement` | Auto-Improvement | – | GitHubリポジトリを変更する前に測定する。measurement-firstの自己改善 |
| 3 | `auto_research` | Research Lab | – | 複数サイクルの調査キャンペーンを実行し続ける |
| 4 | **`aws_control`** | **AWS Control** | – | Kiro Crew が使える AWS アカウントを、アカウントごとの状態表示つきで一覧する。S3 を使ったクラウドドライブ（ファイル・クラウド artifact ライブラリ・バックアップ）と期限付きの共有リンクを備える。有料サービスは課金の前に確認を求める |
| 5 | `channels` | Channels | – | 複数のエージェントが問題に取り組む共有ルーム |
| 6 | `code_review_sage` | Code Review Sage | – | GitHubのPull Requestを深くレビューし、変更点を判定する |
| 7 | **`command_bar`** | **Command Bar** | **✅ 有効** | クイック検索（Cmd+K / Ctrl+K）をランチャーに置き換える。有効な間は、知識・スキル・プロンプトの検索は使えない |
| 8 | `crew_companion` | Crew Companion | – | 作業のペースを整えるデスクトップコンパニオン |
| 9 | `design_critique` | Design Critique | – | 同僚に見せる前に実行できるデザイン批評 |
| 10 | **`design_tweak`** | **Design Tweak** | – | ライブのアプリプレビュー上で要素を視覚的に選び、ソースに対応づけた編集依頼にしてエージェントに渡す |
| 11 | `dev_fleet` | Dev Fleet | – | Kiro Crew自身の開発作業のためのコントロールパネル |
| 12 | `file_explorer` | **Files** | – | Kiro Crewが動作するマシン上のファイルを閲覧・読み込み |
| 13 | `issue_radar` | Issue Radar | – | 記憶するIssueトリアージアシスタント |
| 14 | `md_notebook` | **Notes** | – | gitリポジトリに保存されるMarkdownノートブック |
| 15 | `meetings` | Meetings | – | AI会議アシスタント。ライブ会議を文字起こし |
| 16 | `mochi` | Mochi | – | 画面上に常駐するデスクトップコンパニオン |
| 17 | `ops_mission_control` | Ops Mission Control | – | 自律的な運用初動対応者。アラーム・ページを監視 |
| 18 | `papyrus` | Papyrus | – | ライブPDFプレビュー付きのLaTeX論文エディタ |
| 19 | `personal_shopper` | Personal Shopper | – | 実店舗を調査するパーソナルアドバイザー |
| 20 | `pptx_maker` | PPTX Maker | – | チャットで説明したデッキから実際の.pptxを生成 |
| 21 | **`project_scaffolder`** | **Create Folders From Project** | – | プロジェクトのディレクトリを指すと、中のサブプロジェクトを見つけ、それぞれに対応するサイドバーのフォルダを作る。スキャンは読み取り専用で、作る前に一覧から選べる |
| 22 | **`projects`** | **Task Runner** | **✅ 有効** | マルチステップの作業を渡し、無人で完了まで実行させる |
| 23 | `spec_builder` | Spec Builder | – | Kiro Crew内での仕様駆動開発 |
| 24 | `workflows` | Workflows | – | 動的ワークフロー（Pythonスクリプト等）の作成・実行・観察 |

## App SDKとマニフェスト

各Appは `app.json` マニフェストで宣言されます。`permissions` フィールドでAPI・イベント・MCPツールなどを宣言します。どの宣言が強制され、どれが advisory かは、次節「[権限モデル（advisory）](#権限モデルadvisory)」と、出典間の記述の違いを参照してください。v0.7.0 で加わったマニフェスト項目・App SDK・プラグインの取り込みは「[v0.7.0での変更](#v070での変更)」を参照してください。

## 権限モデル（advisory）

> **重要**: 一次情報（`security.md`）が明記する通り、**Appの権限モデルは現時点で advisory（勧告的）のみです**。`apps/permissions.py` の `validate_permissions`／`format_permissions_summary` は配線されておらず（テストでのみ実行）、`check_tool_permission` は空の許可リストに対してfail openします（`security.md` 3348行。v0.9.0 では 2839行。v0.11.1 の同ファイルも同旨です）。

**実効的な封じ込め**は以下によって行われます:

- HTTP app-tokenのスコープ（`token_auth.py`）
- OSサンドボックス
- `agent.apps_allow_third_party` のオフスイッチ（既定deny。JSON boolean `true` のみ受理し、config errorではfail closed）

インプロセスでの権限の強制は未実装で、トラッキング中です（`security.md` の「App over-privilege」の行と「App manifest permission model — advisory」の段落。v0.11.1 では 724・3348行、v0.9.0 では 622・624・2839行）。

> **以前の記述の訂正**: 本ページは以前、トラッキング先を `app-sandbox-roadmap.md` と記載していました。これは v0.7.2 の `security.md` 227行が挙げていた名前ですが、**`app-sandbox-roadmap.md` は v0.7.2・v0.9.0 のどちらのリポジトリにも存在しません**（v0.9.0 の同行は RFC へのリンクに変わっています。RFC は本サイトの出典にしません）。

### 信頼の付与（サードパーティ App）

- builtin 以外の App は、オペレーターが **Settings → Security → Third-party apps**（v0.9.0 以前の仕様書では「Trusted apps」。[v0.11.1での変更](#v0111での変更)）で信頼するまで、実行コードを実行できません。信頼は App 単位（`agent.apps_trusted`）または全サードパーティ App 一括（`agent.apps_allow_third_party` を JSON の `true` にする）で付与します。拒否されると `app_execution_denied` が返ります（`app-kit/publishing-guide.md` 344-355行、`security.md` 724・3350行（v0.11.1）、`config.md` 1022-1026行（v0.9.0）。公式 `apps`（Page updated 2026-10-12）35-36行も「Third-party apps are disabled by default」）
- リポジトリ付きの付与は `agent.apps_trusted_repositories`、リポジトリなしのローカルは `agent.apps_trusted_local` に記録されます。リポジトリが変わった再束縛は `app_trust_repository_mismatch` で拒否されます。リポジトリに紐づかない旧形式（名前だけ）の付与は、リポジトリ付きの取得元に対しては有効にならず `app_execution_denied` になり、一度だけ再同意が必要です。v0.9.0 の `security.md` 2841行（v0.11.1 では 3350行で同旨）は、さらに、ローカル由来のままインストールされている App では再同意してもローカルの取得元に再び紐づくだけなので、`install_from_registry` が同意ダイアログを開かずに `app_trust_local_only` を返し、データを残したままのアンインストールと App Store からのインストールを手順として示すと記述しています（`app_trust_local_only` は v0.8.0 タグの `security.md` に記述がなく、CHANGELOG は説明していません）
- per-app の信頼付与は CHANGELOG.md v0.2.0節（v0.9.0 のファイルでは 2576行）から存在します

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** 実行コードを持たない App（agent と skill だけの App）の `enable` について、`app-kit/getting-started.md` 156-160行（v0.11.1。v0.9.0 では 156-161行）は「Enable refuses every app that is not built in, even one that ships only an agent and a skill」と記述します。`app-kit/publishing-guide.md` 365-368行（v0.11.1。v0.9.0 では 351-354行）は、拒否されるのは実行コードの面で、agents・skills・MCP サーバ宣言・cron 定義・UI バンドルなどの非実行リソースは影響を受けないと記述します。

### 信頼の前提: App のコードは Gateway と同じ権限で動く

App の実行コードが承認され有効になると、その App のバックエンドフックとルートハンドラは**Kiro Crew 自身と同じ権限**で動きます（任意の `import`・ファイルシステム・ネットワークのアクセスと、Gateway プロセスのメモリ上の資格情報を含む）。App コード自体を囲むプロセスレベルのサンドボックスは現在ありません。App の別プロセスのバックエンドは、サンドボックスのバックエンドがあれば OS サンドボックスの `standard` モードで起動されますが、これは同一プロセス内のモジュールを囲みません（`architecture/app-platform-trust-model.md` 7-25行。v0.11.1 で後半の 1 文が加わりました）。信頼できる App だけを有効にしてください。

### App の権限モデルの記述（3つの出典）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **公式 `apps`**（Page updated 2026-10-12、128-146行）: `permissions.api` は**強制**される（App トークンのスコープ検査。範囲外のパスは既定で拒否）。`events`・`mcpTools`・`storage`・`cron`・`network` は advisory で、インプロセスでは未強制。信頼ダイアログは権限を表示する（35-36行）
> - **`security.md` 3348行**（v0.9.0 では 2839行）: マニフェストの `permissions` ブロックは「neither enforced nor even surfaced today」（`validate_permissions`／`format_permissions_summary` は配線されていない）
> - **`architecture/app-platform-trust-model.md` 17-23行**（v0.11.1 も同旨）: `permissions.cron`・`events`・`spawn`・`storage`・`jobs` は `AppContext` に載る SDK オブジェクトだけを決める。`permissions.mcpTools` は「validated and displayed」だが、実行時の呼び出し箇所がない。インポート・ファイルシステム・ネットワーク・サブプロセスの使用は、どちらの仕組みも制限しない
> - **`app-kit/manifest-reference.md` 943-944行**（v0.11.1）: `validate_permissions`／`format_permissions_summary` はインストールや実行時の経路に配線されていないが、`format_permissions_summary` は `kirocrew app enable` の拒否メッセージにだけ使われる。`security.md` 3348行は「neither enforced nor even surfaced today」と記述し、同じ v0.11.1 の中で食い違っている

**出典**: <https://kiro.dev/docs/crew/apps/>（Page updated 2026-10-12。「Permissions (advisory today)」節）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。724・3348・3350行）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/app-platform-trust-model.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。7-25行）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/manifest-reference.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。943-944行）

## v0.11.1での変更

v0.10.0・v0.11.0・v0.11.1 の変更のうち、本ページの範囲のものです。CHANGELOG に説明があるものは行を示します。**それ以外は v0.11.1 タグの仕様書で確認したもので、CHANGELOG・Release 本文は説明していません**。

### builtin App が24件になった

上記「[builtin App 24件](#builtin-app-24件)」を参照してください。追加の4件（`aws_control`・`command_bar`・`design_tweak`・`project_scaffolder`）の導入版は未確認です。

### App の信頼と権限

- **画面名**: サードパーティ App の信頼は **Settings → Security → Third-party apps**（"Trust every third-party app"）で付与します（`app-kit/publishing-guide.md` 347-349行、`app-kit/getting-started.md` 158行）。以前の本ページは「Trusted apps」と書いていました。v0.9.0 の仕様書がその名前だったためで、v0.11.1 の仕様書は「Third-party apps」です。改称の時期と理由は CHANGELOG に説明がありません。公式 `apps`（Page updated 2026-10-12）は画面名を書いていません
- **更新で `permissions.api`・`permissions.events` に足したエントリは保留**されます。App は有効のまま保たれ、新しいエントリは利用者が詳細ページで承認するまで効きません。App は承認済みの集合を自分の `approved-grants.json` に持ちます（`app-kit/manifest-reference.md` 960-961行、`architecture/app-platform-trust-model.md` 168-176行）。v0.9.0 の仕様書は、この 2 つは更新時に再ゲートされず Issue #11212 で追跡中と記述していました。`permissions.sessionApproval` を新しく足した更新は、従来どおり、利用者が有効にし直すまで App が無効になります（`manifest-reference.md` 957-960行）
- **`kirocrew app enable` に同意のフラグも対話もありません**。同意待ちの App では、要求内容と App のダッシュボードのリンクを表示して終了コード 1 で終わり、App をオフのままにします（`manifest-reference.md` 947-950行）
- **`cron` の権限が必須になりました**。`crons` を宣言するマニフェストは `permissions` に `"cron": true` も宣言しなければならず、install・update・自己登録が、修正方法を示すエラーで拒否します。以前にインストールした App は、次の更新まで動き続けます（`manifest-reference.md` 161-166行・921行）。権限の説明も「Can create cron jobs」から「実行時に cron ジョブを作る（`ctx.cron`）。`crons` が空でないとき必須」に変わっています

### マニフェストと SDK の追加

| 項目 | 内容 |
|------|------|
| `config_keys` | トップレベルの `config.json` のオブジェクトキーを App が所有すると宣言します。最大 200 キー、各 200 文字。App がインストールされている間だけ有効で、署名対象のグループに含まれます（`manifest-reference.md` 42-58行、`app-kit-platform.md` 24-37行） |
| cron の `timeout`・`timeout_secs`・`strict_schedule` | `timeout` は `command`／`script` のサブプロセスの秒数、`timeout_secs` は 1 回の実行全体の秒数（1..86400）で、`command`／`script` では `timeout`（または既定）に後始末の 5 秒を足した値以上が必要です。`strict_schedule`（既定 `false`）を `true` にすると、スケジューラのランダムな開始遅延（日次ジョブで最大 59 分）なしで、分単位ちょうどに起動します（`manifest-reference.md` 156-158行、CHANGELOG.md v0.11.0節 129-133行） |
| `backend.signedPrincipal` | 既定 `false`。JSON の `true` のときだけ、リバースプロキシが転送するすべてのリクエストに署名付きの `X-KiroCrew-Principal` を付けます。種別は `owner-session`・`app-token`・`agent-tool`・`none` です。新しい権限は与えず、Gateway が既に認証した ID を渡すだけです。`owner-session` は、ダッシュボードのオーナーのセッション Cookie で認証されたリクエストにだけ付きます（`manifest-reference.md` 690・701-708行、`app-kit/api-reference.md` 1479-1590行） |
| `permissions.proposeCrewmate` | **Preview、オフ**。`ctx.crewmate` はリテラル `true` でなければ `None` です（`manifest-reference.md` 921行）。呼称は仕様書のままで、UI では Mate（v0.10.0 以前・公式ページでは crewmate）です |
| `contributes.sessionControls[].icon` | `AudioLines`・`Mic` が使えるようになりました（`manifest-reference.md` 243・535行） |
| 予約名 | `library`（`/apps/library` を静的ページで提供）が加わりました。既存の `registry`・`registries`・`blob`・`install`・`register` と同様に拒否されます（`app-kit/publishing-guide.md` 51行） |
| MCP サーバの `env` の `secret://<name>` | kiro-cli が App のサーバを起動するとき**解決されず、参照のテキストがそのまま渡ります**。登録時に警告をログに書きます。App が vault のシークレットを受け取る方法は未決定と記述されています（`manifest-reference.md` 104-110行） |
| App 自身の `.py` ランチャー | stdio サーバの `command` が素の `python`／`python3`／`py` で、起動対象が App ルート内の相対 `.py` のとき、登録時に App ルート下の絶対パスに解決されます（`manifest-reference.md` 91-100行） |
| `setup.onInstall` | `/bin/bash` を呼ぶため、ネイティブ Windows のレジストリインストールは、事前の拒否なしで失敗します（`manifest-reference.md` 1039-1041行）。`onEnable`・`onDisable`・`onUninstall` は v0.8.0 の節のとおり事前に拒否されます |

### App の更新通知と ChatEmbed

- **更新通知**: 外部レジストリの App に新しい版が出ると、ベル通知（版ごとに 1 回）と Discover の保留中更新数で伝わります。App 自身も `useAppInfo().update` で同じ答えを読めます。判定の根拠は `version` だけです。インストールの同意ゲートは、コミュニティレジストリのレビュー tier を表示します（CHANGELOG.md v0.11.0節 177-180行、`app-kit/publishing-guide.md` 66-80行）
- **`ChatEmbed` の `hide` プロップ**: `header`・`attach`・`stop`・`queue`・`toolDetails`・`followUps` を隠せます。`attach` を隠すと貼り付けやドロップは拒否され、アップロードされません。どのキーも権限は与えません（CHANGELOG.md v0.11.0節 177-180行、`app-kit-platform.md` 58-76行）

### Issue Radar（v0.10.0）

自分の Pull Request の CI が失敗したときの通知（CI runs タブ、リポジトリ単位のスイッチ）と、GitLab グループのサブグループ全体のレビュー依頼が加わりました（CHANGELOG.md v0.10.0節 362-367行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/manifest-reference.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/publishing-guide.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/app-platform-trust-model.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/app-kit-platform.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
出典: CHANGELOG.md v0.10.0節 362-367行・v0.11.0節 127-132・177-180行（`fe6f5be`）

## v0.9.0での変更

### すべての builtin App の書き込みルートはオーナー限定

v0.9.0 では、**すべての builtin App の書き込みルートがダッシュボードのオーナーだけを受け付けます**（CHANGELOG.md v0.9.0節 174-175行）。

### App 向けリバースプロキシの上限

`/apps/<name>/api/*` の App バックエンドへのリバースプロキシについて、v0.9.0 の `app-kit/api-reference.md`（842・1065行。v0.11.1 では 1428・1569行で同旨）は次のように記述しています。この 30 秒・60 秒の記述は、v0.7.2 と v0.8.0 の同ファイルに見つかりません（本内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません）。

- SSE 以外の応答（仕様書の表現は「ordinary response」）は**合計 30 秒**で打ち切られます
- `text/event-stream` の応答に合計時間の上限はありませんが、**60 秒以内にイベントまたは `:` コメントを出さないと切断**されます
- 署名の鮮度の窓は ±60 秒です（`verify_proxy_request`）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** 署名ヘッダの名前について、公式 `apps`（Page updated 2026-10-12）101行は `X-Crew-Proxy: <timestamp>:<hmac-sha256>` と記述し、リポジトリの `app-kit/api-reference.md`（v0.9.0 では 1074・1088・1107行、v0.11.1 では 1437・1451・1470行）と `dev-fleet.md`・`md-notebook.md` は `X-KiroCrew-Proxy` と記述します（v0.7.2 でも同様）。v0.11.1 では、`backend.signedPrincipal` を有効にした App に限り、別のヘッダ `X-KiroCrew-Principal` も付きます（[v0.11.1での変更](#v0111での変更)）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** Python クライアント `kirocrew-client` の入手方法について、公式 `apps/sdk`（Page updated 2026-09-25）16・59行は「`pip install kirocrew-client`」と記述します。リポジトリの `app-kit/api-reference.md`（v0.9.0 では 28-31・848-854行、v0.11.1 では 18・1187行）は、PyPI に公開されておらず `pip install kirocrew-client` は動かない（ソースチェックアウトからのインストールのみ）と記述します（v0.7.2 の同ファイルも「not published to PyPI」）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/api-reference.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。1428・1437-1470・1569・18・1187行）
**出典**: <https://kiro.dev/docs/crew/apps/>・<https://kiro.dev/docs/crew/apps/sdk/>（Page updated 表記あり）

## v0.8.0での変更

| 変更 | 内容 | 出典 |
|------|------|:---:|
| **ダッシュボードのルートはオーナー限定** | App のインストール・開く・有効化、スケジュールジョブの編集・実行・確認・キャンセル、ホストのファイルの読み取り、エージェントの操作を行うダッシュボードの全ルートが、ダッシュボードのオーナーを要求します。**App トークンが管理できるのは自分のスケジュールジョブだけ**です（公式 `apps` 48行も同じ） | CHANGELOG 696-699行 |
| **無効化・アンインストールで本当に止まる** | App を無効化またはアンインストールすると、スケジュールジョブを含めて停止します。ストアは、このビルドが同梱しない builtin を提示しなくなりました | CHANGELOG 563-565行 |
| **Windows での更新** | バックエンドが動いている間の App の更新が失敗しなくなりました | CHANGELOG 576-577行 |
| **Code Review Sage の Requests タブ** | Pull requests・Reviews の隣に Requests タブが加わりました。自分にレビューを求めている、自分のリポジトリ横断の open な Pull Request を表示し、選択して Sage のレビューを開始します。サインイン済みの GitHub CLI が必要で、タブを開いたときと更新ボタンで更新されます。Code Review Sage は opt-in の builtin（既定オフ）です | CHANGELOG 399-404行 |
| **Papyrus のパネル配置** | ファイルツリー・PDF プレビュー・共同執筆パネルの境界をドラッグでき、配置と共同執筆パネルの開閉状態が記憶されます | CHANGELOG 383-386行 |
| **MCP App からチャットへメッセージを送れる** | 次節を参照 | CHANGELOG 380-382行 |
| **共有 MCP バックエンドの Stub レビュー（Developer Mode）** | [08_mcp-integration.md](08_mcp-integration.md#共有-mcp-バックエンドの-stub-レビューdeveloper-mode) を参照 | CHANGELOG 389-394行 |

出典: CHANGELOG.md v0.8.0節 380-404・563-565・576-577・696-699行（`99e6253`）。公式 <https://kiro.dev/docs/crew/apps/>（Page updated 2026-10-12）。

マニフェストについて、v0.9.0 の `app-kit/manifest-reference.md` には次の項目があります。v0.7.2 の同ファイルに `signer`・`signature`・`notifications.channels`・`permissions.jobs`・`permissions.exposeToApps`・`iconPathDark`・`ui.pages[].iconInactiveUrl`・cron の `agent_sequence` の記述は見つからず、v0.8.0 タグの同ファイルでは確認できます。`setup.onUpdate` は v0.7.2 では「Shell command run after update」と記述されていましたが、v0.8.0 タグ以降は「実行されない」と記述します。`permissions.sessionApproval`・`publishProvider`・予約名は v0.7.2 の同ファイルにも記述があります（表の「v0.7.2 にも記述あり」）。CHANGELOG はこれらを説明していません。

| 項目 | 内容 |
|------|------|
| `signer`・`signature` | admission metadata。`signer` はフリートの admission 信頼鍵から引く発行者 ID、`signature` は発行者のツールが生成する分離署名です（29-47行）。署名対象は `name`・`version`・`signer`・`permissions` と、空でない `notifications`・`crons`・`contributes`・`setup`・`mcpServers`・`backend`・`ui`・`agents`・`skills`・`sops`・`dependencies`・`platform`。署名済み App が古い Gateway の知らないグループを宣言すると検証に失敗し、インストールは拒否されます（fail closed）。署名済み App に `minKiroCrewVersion` を設定すると、拒否が版の下限を名指しします |
| `permissions.sessionApproval`（v0.7.2 にも記述あり） | 既存のローカルセッションへのメッセージ送信、承認・拒否、承認モード変更（840行）。`permissions.jobs`（`ctx.job` による耐久ジョブ）・`permissions.exposeToApps` もあります |
| `notifications.channels` | 最大 8 チャンネル。`defaultPriority` は `critical`／`default`／`passive`（898-902行） |
| `publishProvider`（v0.7.2 にも記述あり） | artifact の公開先を 1 つ追加（905-916行） |
| cron の項目 | `agent_sequence`・`persistent_session` など（128-132行） |
| `iconPathDark`・`ui.pages[].iconInactiveUrl` | ダークテーマ用アイコン、非アクティブ時のアイコン（180・502-506行） |
| `setup.onUpdate` | 宣言・保存されますが**実行されません**（941行。v0.7.2 の同ファイルは「Shell command run after update」と記述）。更新時の処理は、レジストリの更新で再実行される冪等な `onInstall` に置きます |
| `setup.onEnable`・`onDisable`・`onUninstall` | `/bin/bash` を呼ぶため、**ネイティブ Windows では実行されません**（実行前に拒否され、非対応のプラットフォームを名指しする失敗が報告されます。950-957行） |
| 予約名（v0.7.2 にも記述あり） | `registry`・`registries`・`blob`・`install`・`register` は `reserved_app_name` で拒否されます（1165-1169行） |

上限は v0.7.0 から変わりません（パネルタブ最大 8、ファイルメニュー行最大 10、セッションコントロールはバックエンドで App あたり 2・ダッシュボードの描画は全 App で 2。394-396・473・583行。公式 `apps/manifest` も同じ）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/manifest-reference.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## MCP App がチャットへ送るメッセージ

レンダリングされた **MCP App** のボタンやフォームは、その App に紐づくチャットへ**テキストを送れます**（v0.8.0。CHANGELOG.md v0.8.0節 380-382行）。

- 送られた行は「**Sent by the _name_ app**」と表示され、ユーザー自身の発言としては扱われません。モデルのターンを開始するか、実行中のターンの後ろで待ちます
- **ダッシュボードのオーナーのセッションからのみ**使え、App のコールバック鍵と元のセッションの紐づけが必要です
- 公式 `apps`（Page updated 2026-10-12、42-48行）は、1 通はテキストのみで **16,384 文字**まで、**3 秒に 1 通**、**1 つのレンダリング済み App から 20 通まで**と記述しています
- 仕様書（`modules/mcp-apps.md` 113-127行）: 応答の `{isError: false}` は「受け付けた」という意味で、配信の確認ではありません（Gateway の再起動で待機中のエントリは取り除かれ、待機中に封じ込め設定が変わると落ちることもあります）。非テキストのブロックは受理されず拒否されます
- **対象**: stub 経由の stdio MCP サーバの描画が前提です（`mcp-apps.md` 3-5行。stub は Developer Mode の MCP Management で設定。[08_mcp-integration.md](08_mcp-integration.md#共有-mcp-バックエンドの-stub-レビューdeveloper-mode) 参照）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** 上限について、公式 `apps` 46行は「16,384 characters, one message per three seconds, and 20 messages from one rendered app」と記述します。仕様書 `mcp-apps.md` 119行（v0.11.1 でも同じ）は「a 16 KiB total-text cap」と記述し（バイトと文字で単位が異なります）、3 秒・20 通の数値は定数名（`_MESSAGE_MAX_PER_SPOOL` など）で言及するだけで、値を書いていません。

**出典**: <https://kiro.dev/docs/crew/apps/>（Page updated 2026-10-12。「Apps sending text into chat」節）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/mcp-apps.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.7.0での変更

### プラグインの取り込み（`kirocrew app import`）

**他のエージェントハーネス向けに書かれたプラグインパッケージを、インストール可能な Kiro Crew の App に変換できます。** 変換器はパッケージ内のコードを実行しません。インストール後の扱いは下表の「安全性」を参照してください。

```bash
kirocrew app import /path/to/plugin
kirocrew app import /path/to/plugin --install
```

| 観点 | 内容 |
|------|------|
| **入力** | マニフェストを宣言したプラグインディレクトリ。パッケージ直下の `plugin.json`（`$schema` が `https://agent-plugins.org/schemas/` で始まるもののみ）、または `.*-plugin/plugin.json`（`.codex-plugin`・`.claude-plugin`・`.cursor-plugin` など）を探します。どちらもシンボリックリンク経由では受け付けません |
| **変換されるもの** | `skills`（リソースをコピー）・`mcpServers`。`name`・`version`・`description` などのメタデータは `app.json` に写されます |
| **変換されないもの** | `apps`・`hooks` は**報告のみ**で変換されません。パッケージ内のプログラムを起動するMCPサーバ（`command`/`args`/`cwd` がパッケージ相対）も、サーバ単位で拒否して報告します |
| **安全性** | **変換中**は、パッケージのコードを import・評価・起動しません。**インストール後**は、マップされた MCP サーバのコマンドが他の App と同じライフサイクルで起動されます。パッケージ相対のプログラムを起動する MCP サーバは変換時にサーバ単位で拒否して報告します。フックの `command` はデータとして扱い、実行しません。宣言パスは `./` で始まり、`..` を含まず、パッケージルートの外に解決されないことが必要で、外れると変換全体が失敗します（`resource_outside_root`）。コピー中に見つかったリンクはたどらずスキップして報告します |
| **出力** | `--out` の既定は `./<app名>-app`。変換の記録は `app.json` の `importedPlugin` ブロックに残ります（`mapped`・`unmapped`・`warnings`） |
| **インストール** | `--install` を付けると、ローカルインストールまで続けて行います。付けない場合は `kirocrew app install` の実行行を表示します。インストールした App は（他のローカルインストールと同じく）無効のままで、`kirocrew app enable <name>` が別の手順です |

フック・ツール・サービスなど「パッケージ内のコード」側は変換の対象外で、`modules/harness-plugin-mapping.md` は Codex・openclaw・hermes・grok-build のいずれについても**フックはインストール済みAppで扱えない**と記述しています（194-208行）。

> **以前の記述の訂正**: 本ページは以前、「パッケージのコードを import・評価・起動しません（変換時も変換後も）」と記載していました。これは v0.7.2 の `plugin-import.md`（「Nothing in the package is imported, evaluated, or spawned -- at conversion time or after」）に基づくものです。**v0.9.0 の同ファイルは、コードを実行しないのは「変換時」で、インストール後はマップされた MCP サーバのコマンドが他の App と同じライフサイクルで起動され得ると記述しています**（13-20・169-176行。変更の理由は CHANGELOG に説明がありません）。公式 `apps`（Page updated 2026-10-12）は、変換器が「without executing any code from the source package」であり、ソースパッケージのコードを import も実行もしないと変換器の動作を記述しています。

**変換の上限**（v0.7.2 から同一）: スキルは 1 パッケージ 200 件・スキルツリーの深さ 8・コピーする 1 ファイル 32 MiB・スキルツリー 1 本あたり 2000 ファイル／128 MiB、マニフェストは 4 MiB を超えると読まずに拒否されます。上限に達すると警告として報告され、黙って切り捨てられることはありません（`plugin-import.md` 205-215・249行）。

**`http` の MCP サーバ**: v0.9.0 の `harness-plugin-mapping.md`（239-257行）は、`http` の URL を持つ App の MCP サーバについて、自己管理の App（`backend.entryPoint` が空。変換されたパッケージはすべてこれに該当）の固定エンドポイントの URL を保持すると記述します。v0.7.2 の同ファイルは、ライブのバックエンドポートがない App の `http` URL は登録されず、変換後にツールが無い状態になると記述していました。

出典: CHANGELOG.md v0.7.0節 400-402行（v0.7.2 タグのファイルの行番号、`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/apps/>（「Import a plugin package」節。Page updated 表記あり）
**出典**（変換仕様）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/plugin-import.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（ハーネス別の対応）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-plugin-mapping.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。194-208行。v0.7.2 では 185-208行）

### Appがセッションを操作できる（Appごとに既定オフ）

**App は、trust dialog で許可した場合に限り、セッションを開始・誘導（steer）・停止できます。** この許可は **App ごとに既定オフ**です。あわせて、スケジュールジョブを持つ App のレールアイコンに、ジョブの実行中・完了・失敗の状態が表示されます。

出典: CHANGELOG.md v0.7.0節 403-406行（v0.7.2 タグのファイルの行番号、`c67c506`）／公式 <https://kiro.dev/docs/crew/apps/>（「Apps that act on sessions」節）。

### Apps → Discover（ソースとレビュー tier で絞り込み）

App のストアは **Apps → Discover** から開きます。カタログを**ソース**と**レビュー tier**で絞り込め、ピン留めした外部レジストリはカタログ上にラベルと tier を表示するため、インストール前に出どころと審査の程度を確認できます。組み込みレジストリは引き続き KiroCrew リポジトリへの Pull Request でキュレーションされます。外部レジストリの追加は明示的な信頼の判断で、その App もインストールダイアログとローカルポリシーの対象です。

出典: CHANGELOG.md v0.7.0節 397-399行（v0.7.2 タグのファイルの行番号、`c67c506`）／公式 <https://kiro.dev/docs/crew/apps/>（「Discover apps by source and review tier」節）。

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

> **最小版のキー名**: 公式 manifest ページの最小 Gateway 版キーは、v0.6.0 対応時の取得内容では `minCrewVersion`、v0.7.2 対応時の取得内容では **`minKiroCrewVersion`** です（`apps.md`・`apps/publishing/` も同様。v0.9.0 の公式ページも `minKiroCrewVersion`）。リポジトリの `app-kit/manifest-reference.md` は v0.6.0 タグの時点で既に `minKiroCrewVersion` と記載しています（v0.9.0 でも 20・47行）。旧キー名の扱いは、v0.9.0 の公式・仕様書のどちらにも記載がありません。

出典: CHANGELOG.md v0.7.0節 225-235行（v0.7.2 タグのファイルの行番号、`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/apps/manifest/>・<https://kiro.dev/docs/crew/apps/sdk/>（Page updated 表記あり）
**出典**（キー名）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/app-kit/manifest-reference.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。20・47行）

### その他

- **Dev Fleet の pod ツール** — Dev Fleet アプリを Apps → Library で有効にすると、エージェントのセッションが worktree の pod を起動し、アドレス・ポート・短命トークンを受け取れます（127-130行。ツール名は [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md) 参照。`dev-fleet.md` 361-366行）
- **Ops Mission Control が incident.io をプロバイダとして受け付ける**（405-406行。`ops-mission-control.md` 726・2020行。v0.8.0・v0.9.0 の CHANGELOG に Ops Mission Control の項目はありません）

## v0.3.0での変更

### 「2つの新App」という表現と実装年代の食い違い（裁定しない）

v0.3.0のCHANGELOG（93行）は「**### Two new apps, and a store worth browsing**（2つの新しいAppと、閲覧に値するストア）」という見出しで **Personal Shopper** と **Issue Radar Crews** を挙げています。**しかしこの2つのAppの実装は、v0.3.0より前から存在します。** 本サイトは裁定せず両方を記載します。

| 観点 | 確認できた事実 |
|------|--------------|
| **CHANGELOGの立場** | v0.3.0節93行が「Two new apps」として Personal Shopper（95行）・Issue Radar **Crews**（98行）を発表している |
| **`personal_shopper`の実装年代** | `64060f3`（本サイトがv0.2.0として固定している時点）に既に `app.json` が存在し、**その内容は`21584ea`と完全に同一**（`diff`で差分0） |
| **`issue_radar`の実装年代** | `64060f3`に存在。さらに**v0.1.2のCHANGELOG（`64060f3`版628行）に「Shipping in the box」のbuiltin App 6件の1つとして「Issue Radar (GitHub/GitLab triage that remembers its notes)」と記載**されている |
| **表示名** | `issue_radar/app.json` の `displayName` は `21584ea`でも「**Issue Radar**」のままで、CHANGELOG v0.3.0が使う「Issue Radar **Crews**」という名称は`app.json`に反映されていない |

**なぜCHANGELOGが「新App」としているのか（機能が大幅に拡張されたのか、発表のタイミングの都合か等）は公式に説明がないため、本サイトは推測しません。** 上記builtin App 24件の表に両Appは含まれています（19番・13番。v0.3.0 時点の20件の表では16番・10番）。

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

- **追加4件の builtin App（`aws_control`・`command_bar`・`design_tweak`・`project_scaffolder`）の導入版**: 本サイトが `src/` を実測したのは v0.3.0（20件）と v0.11.1（24件）の2点だけで、間の版の `src/` は取得していません。CHANGELOG の言及は機能の記述で、builtin になった時期の根拠にならないため、導入版は書きません（件数・既定有効の現在値は上記「[builtin App 24件](#builtin-app-24件)」で解消済みです。台帳は [`scripts/kiro-crew-docs/ledgers/builtin-apps.md`](../../scripts/kiro-crew-docs/ledgers/builtin-apps.md)）
- `minCrewVersion`（旧キー名）を書いたマニフェストの扱い（v0.11.1 の公式・仕様書のどちらにも記載なし）
- `kirocrew app init <name> [--ui] [--backend] [--cron]`（雛形の生成）は `app-kit` のドキュメント（`getting-started.md` 12-17行ほか）にだけ現れ、`modules/cli.md` と公式には記載がありません。本ページでは扱いません
- App の権限モデル（`security.md` と `manifest-reference.md` 943-944行の食い違いを含む）、MCP App の送信上限、リバースプロキシのヘッダ名、`kirocrew-client` の入手方法は、出典間で記述が異なります（上記の各 ⚠ を参照）
- 「2つの新App」の食い違い（v0.3.0）は継続しています（CHANGELOG の v0.3.0節・v0.1.2節は v0.11.1 のファイルでも文面が変わりません）
- 公式 `apps`（Page updated 2026-10-12）の画面名の記述はなく、「Third-party apps」と「Trusted apps」のどちらが現在の画面名かは、公式からは確認できません（v0.11.1 の仕様書は前者）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/apps/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- 自律実行（Task Runner）: [06_autonomy.md](06_autonomy.md)
- セキュリティ: [09_security.md](09_security.md)

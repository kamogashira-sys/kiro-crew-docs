# 成果物（Artifacts）

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/chat/artifacts/>・<https://kiro.dev/docs/crew/features/artifact-deploy/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

---

## 📑 このページの内容

- [2つのArtifacts概念](#2つのartifacts概念)
- [チャット内Artifacts](#チャット内artifacts)
- [Artifact Deploy](#artifact-deploy)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0での変更](#v090での変更)
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## 2つのArtifacts概念

**公式は別ページとして扱う2つの「Artifacts」を明確に区別します。**

| # | 名前 | 公式パス | 内容 |
|---|------|---------|------|
| ① | **チャット内のArtifacts** | `docs/crew/chat/artifacts/` | 会話の中で生成・閲覧する成果物（永続的な識別子・バージョン履歴を持つ） |
| ② | **Artifact Deploy** | `docs/crew/features/artifact-deploy/` | 生成物を自分のAWSアカウントへワンクリックデプロイする機能。公式ナビの表示名は「**Artifacts**」 |

> Rev 1（旧版計画）では②の担当ページが存在せず、公式49ページの中で唯一未割当のままだった経緯があります。本ページで両方を扱うことでこれを解消しています。

## チャット内Artifacts

チャットでレンダリングされるLLM生成のUIに、永続的な識別子・バージョン履歴・セッションを跨いで反復できる安定したハンドルを与える機能です。

典型的なフロー:

1. エージェントがチャットで `<mcwidget>` を発行（「これがCRキューです」）
2. アシスタントの発言区間が確定すると、バックエンドがウィジェットを**ピン留めなし（unpinned）の artifact として自動登録**し、`~/.kiro/crew/artifacts/<slug>/current.html` に保存する（ユーザー操作は不要。星を付けるとピン留めになる）
3. 数日後、新しいセッションでユーザーが「cr-queueのartifactを改良して年齢列を追加して」と言う
4. エージェントが `artifact_get("cr-queue")` で現在のHTMLを読み、変更を加え、`artifact_update("cr-queue", content=…)` で新バージョンを公開
5. 前バージョンは `versions/v1.html` としてロールバック用に保持される

> **以前の記述の訂正**: 本ページは以前、手順2を「エージェント（またはユーザー）が `artifact_save` を呼び、ウィジェットが永続化される」と記載していました。これは v0.3.0（`21584ea`）・v0.7.2（`c67c506`）の `artifacts.md` の概要フローの記述に基づくものです。**v0.9.0 の概要フロー（8-17行）は「When the assistant segment finalizes, the backend auto-registers the widget as an unpinned artifact」と書き換わっています**。自動登録の節（「Widget auto-registration」）自体は v0.3.0 タグ以前から存在し、概要フローの記述だけが実態に合っていませんでした。

### ウィジェットの自動登録

`artifacts.md` 960-1015行（v0.9.0 では 902-998行）は、自動登録の条件を次のとおり記述しています。

- エージェントが発行した `<mcwidget>` は、アシスタントの発言区間が確定したときにバックエンドが自動で登録します。登録された記録は**ピン留めなし**で、ライブラリの項目ではなく「記録」です。ウィジェット上の星は、記録の作成ではなく `pinned` の切り替えです
- 登録は**冪等**です。同じスラッグが既にあれば触りません。明示的な `slug=` 属性付きのウィジェットは、新規作成ではなく既存の artifact を指す再掲示として扱われ、登録されません
- **シークレット（incognito）／一時（temporary）のセッションでは登録されません**（これらのセッションは artifact の書き込みがすべて拒否されるため）
- **保持**: 自動登録されたままの記録は、`MAX_AUTO_WIDGET_ARTIFACTS`（200）を超えると古い順に削除されます。削除の対象になるのは、ピン留め・フォルダ・公開・フォーク情報・説明／タグ・編集・コメントのいずれも無い記録だけです。明示的な保存で作った artifact は削除されません

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。8-17行・960-1015行）

ダッシュボードには閲覧・検索用の `/artifacts` ライブラリページと、バージョンドロップダウン付きの `/artifacts/<slug>` スタンドアロンビューがあります。

### 保存レイアウト

```
~/.kiro/crew/artifacts/
└── <slug>/
    ├── meta.json        # メタデータのみ(コンテンツなし)
    ├── current.html     # 最新のコンテンツ
    └── versions/
        ├── v1.html
        ├── v2.html
        └── …
```

`kind` フィールドは `widget`／`html`／`markdown`／`svg`／`json`／`text`／`webapp`／`image`／`dashboard` の 9 値のenumで（v0.9.0 は `dashboard` を除く 8 値）、保存時に呼び出し元が省略すると推論されます。`dashboard` は推論で返らず、呼び出し元が明示します（[v0.11.1での変更](#v0111での変更)）。`source` に保存される値は `chat`（既定）／`cron`／`subagent`／`manual`／`import`／`dashboard`／`slack`／`cli`／`task-runner`／`unknown` の **10 種**です。MCP の保存スキーマが明示的に受け付けるのは先頭の 5 種です（`artifacts.md` 246・1183行。v0.9.0 では 329・1122行）。v0.7.2 の仕様書は 5 種を記述していました。

**出典**（保存レイアウト・`kind`・`source`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。228-246・1176-1185行）

### 保存・バージョン・タグの規則

`artifacts.md`（v0.11.1。v0.9.0 の記述と同内容を確認しました）の記述です。CHANGELOG/Release 本文は、このうち次の項目を説明していません（v0.7.2 の仕様書との差は各項目に示します）。

- **スナップショット**: `update(slug, content=…, snapshot=False)` はバージョンを増やさずに現在の内容を更新し、`snapshot=True` のときバージョン番号が増えて `versions/vN.html` が書かれます。**MCP の `artifact_update` は既定でスナップショットを取り、ダッシュボードの Save は `snapshot: true` を送らない限り取りません**（1791-1794行・496行。v0.9.0 では 1298-1307行）。`artifact_revert` は以前のバージョンの内容を、`reverted` タグ付きの新しいスナップショットとして書き込みます（453行。v0.9.0 では 498行）
- **同時書き込みの検出**: `PATCH /api/artifacts/{slug}` は、内容を書くたびに入れ替わる `content_token` を持ちます。直前の読み取りの `expected_token` を付けると、その後に別の内容の書き込みがあった場合は 409（`artifact_conflict`）で何も書かれず、不正な値は 400 です（252・496行。v0.9.0 では 541行）
- **コメントの取得**: `artifact_get_comments` は `exclude_resolved=true` で解決済みスレッドをスレッドの根単位で除外できます（461・1818行。v0.9.0 では 506・1328行）
- **オーナー限定**: ダッシュボードから artifact の状態を変えるルート（作成・編集・削除・公開・共有・フォルダ・ピン・コメントなど）は、ダッシュボードのオーナーだけが使え、オーナー以外にはすぐに 403（`owner_only`）が返ります。Gateway ループバックの内部経路（エージェントの `artifact_*` ツール・CLI・App のドライバ）と、マニフェストの付与の範囲内の App トークンは対象外で、それぞれ自身の規則に従います（216-223行。v0.9.0 では 300-307行）

値の上限（`artifacts.md` 1176-1185行。v0.9.0 では 1109-1124行）:

| 項目 | 上限 |
|------|------|
| `slug` | 80 文字以内（正規表現 `^[a-z0-9](?:[a-z0-9-]{0,78}[a-z0-9])?$`） |
| `name` | 200 文字以内（空は不可） |
| `description` | 2,000 文字以内 |
| `tags` | 16 個以内。1 件は NFC 形で 64 コードポイント以内。Unicode の文字・文字に付く結合記号（`Mn`／`Mc`。1 文字に最大 4）・数字と `_`・`:`・`.`・`-` で構成し、先頭は文字か数字。不可視のコードポイントと、他の文字の互換形は拒否される |
| 本文（`content`） | 25 MiB 以内（`MAX_CONTENT_BYTES`） |
| 保持バージョン数（`MAX_VERSIONS`） | 50（超えると古い順に削除） |
| 自動登録ウィジェット数（`MAX_AUTO_WIDGET_ARTIFACTS`） | 200（超えると、ピン留めなしで自動登録されたままの古いものから削除） |

v0.7.2 の仕様書でも、`slug`・`name`・`description`・本文・保持バージョン数・自動登録ウィジェット数は同じ値でした。変わったのは次の3点です。`tags`（v0.7.2 の検証表は「each ≤ 64 chars」とだけ記述し、フィールド表は「alphanumeric / `_`, `:`, `.`, `-`」と記述していました。v0.7.2 `artifacts.md` 687・57行）、`kind` の検証表への `image` の記載（`kind` のフィールド表には v0.7.2 でも `image` が記載されていました。v0.7.2 `artifacts.md` 52・689行）、`source` の種類（5 → 10）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。216-223・252・450・453・461・496・1176-1185・1791-1794・1818行）

## Artifact Deploy

`kind: "webapp"` のartifactをライブラリから取り出し、**あなた自身のAWSアカウント**でグローバルな公開HTTPS URLに展開する機能です。既定のTTLと自動クリーンアップ、永続化への切り替えパスがあります。Crewがデプロイをオーケストレーションし、あなたのアカウントは実際にサイトが提供したものだけを支払います。

### 4ステップのフロー

1. **Artifact Deploy** Appを有効化（App Store）し、サイドバーから開き、AWSプロファイル（`~/.aws/config` の名前付きプロファイル）を登録して**Verify**でアクセスを確認
2. エージェントに何かを作らせる — `kind: "webapp"` で保存されたアプリはArtifactsギャラリーにライブローカルプレビュー付きで表示される
3. artifactカードの**Deploy**をクリック。デプロイセッションが開き、エージェントがプラン（リソース・リージョン・コスト見積り）を提案し、コンソールで確認する
4. CloudFront URLを取得。カードが**Live**に切り替わり、リンク・TTLカウントダウン・アーキテクチャ概要・**Tear down**ボタンが表示される

### 3段階のティア

| ティア | アカウント内のリソース | 例 |
|-------|----------------------|-----|
| **Static**（静的） | S3（サイトごとのprefix）＋共有CloudFront distribution | ランディングページ、three.jsデモ |
| **Fullstack**（フルスタック） | ＋ `/api/*` の背後のLambda Function URL | APIバックエンドのデモ |
| **Stateful**（状態あり） | ＋ DynamoDBテーブル | 永続化を持つアプリ |

最初のデプロイでアカウントに共有の**ベーススタック**（`kirocrew-deploy-base`: S3バケット＋CloudFront distribution）が作成されます（CloudFrontのグローバル伝播で5〜15分）。以降のデプロイはベーススタックを再利用し数秒で完了します。

### TTLとreaper

既定のTTL（72時間）のクリーンアップには**reaperスタック**（`install-reaper.sh`）— アカウント内のLambdaが期限切れのデプロイを削除します。これがない場合、有限TTLのデプロイは拒否されます（409）。

## v0.11.1での変更

v0.10.0・v0.11.0・v0.11.1 の変更のうち、本ページの範囲のものです。CHANGELOG に説明があるものは行を示します。**それ以外は v0.11.1 タグの仕様書で確認したもので、CHANGELOG・Release 本文は説明していません**。「Mate」は v0.11.0 以降の UI と CHANGELOG の呼称です（v0.10.0 以前、および公式ページでは crewmate。コード識別子・API パス・設定キーは crewmate のままです。CHANGELOG.md v0.11.0節 59・74-75行）。

### Dynamic Dashboard が Preview でなくなった（v0.10.0）

- **Dashboard タブは Feature Preview を要しなくなりました**。メインセッションのサイドパネルに専用の Dashboard が出ます。**Automatic cards for all sessions** は Settings → Developer の専用カードに移り、既定オフのままです（CHANGELOG.md v0.10.0節 249-251行）
- 仕様書の記述: Dynamic Dashboard の表示面は全員に有効です（+ メニューの項目、保存済みの Dashboard タブ、Sessions メニューの All Dashboards、Crew チャットの Dashboard タブ）。Automatic cards for all sessions は Settings > Developer に専用カードがあり、ゲートウェイ全体の課金設定として既定オフです（`artifacts.md` 150-153行）。v0.9.0 の仕様書は、`PREVIEW_DASHBOARD` が既定オフで入口を制御すると記述していました
- **ルートセッションのサイドパネルの Dashboard**: ルートセッションの Dashboard は、Mate と共有する組み込みテンプレートから描かれます。読み取りは `GET /api/chat/slots/{slot}/dashboard`（オーナー限定。App からの呼び出しは拒否）で、ルートでないセッションは 404 `not_root_session` です。パネルは Overview の区画を落とし、Questions から開きます（`artifacts.md` 113-146行）
- **`task-dashboard` タグ付きの artifact は読まれません**。ステータスタイルの HUD はコンポーザの上に描かれず、エージェントが発行した `task-dashboard` artifact は、パネルにも全セッション表示にも読まれません（`artifacts.md` 147-148行）。v0.9.0 の仕様書は、これを「モデルが作ったタスクビュー」と記述していました
- **Mate が自分のページを書きます**: Mate は `dashboard` skill でギャラリーから自分のページを作り、Dashboard タブで保存か破棄を選びます（CHANGELOG.md v0.10.0節 253-255行）。v0.11.0 では、Mate が自分のページにテーマを付け、apply で公開し、1 回の呼び出しでロールバックでき、自分のページを PNG で見られます（CHANGELOG.md v0.11.0節 79-82行）。仕様書は「Save はページを保存し、apply はそれを公開する。プレビューの段階はない」と記述します（`artifacts.md` 1583行）。これらのツールは `kirocrew-panel` の `dashboard_*` です（[08_mcp-integration.md](08_mcp-integration.md#管理対象のmcpサーバ)）
- 以前の本ページは「crewmate が自分でページを書くことはできない」と書いていました。これは v0.9.0 の公式 `capabilities/agents` の記述に基づくもので、v0.10.0 以降の CHANGELOG・仕様書とは合いません

> ⚠ **出典間で記述が食い違っています。本サイトは裁定しません。** Dynamic Dashboard の扱いについて、CHANGELOG.md v0.10.0節 249-251行（2026-10-15）と `artifacts.md` 150-153行（v0.11.1）は、Feature Preview を要しないと記述します。公式 `capabilities/agents`（Page updated 2026-10-20）は、見出しを「Dynamic Dashboard (Preview)」とし、Settings → Developer → Feature Previews → Dynamic Dashboard をオンにして使うと記述します。さらに同ページは、crewmate は出荷済みの 12 のページから選ぶだけで、自分のページを書けないと記述します（128-132行）。公式ページの更新日の方が CHANGELOG の日付より新しい一方、公式は v0.10.0 の後も Preview と書いています。

### `kind` に `dashboard` が加わった

`kind` の列挙は **9 値**（`widget`／`html`／`markdown`／`svg`／`json`／`text`／`webapp`／`image`／`dashboard`）になりました（`artifacts.md` 245・1182行。v0.9.0 は `dashboard` を除く 8 値）。`dashboard` は推論では返らず、呼び出し元が明示します（同 1592行）。`kind="dashboard"` の artifact は、Mate 1 人のレイアウトパッケージ（`bound_to`・`model`・`view`・`theme`）を保持します。呼び出し元の `snapshot` は無視され、レイアウトが変わったかどうかで版が決まります（同 1246-1270行）。`source` の 10 値、`slug`／`name`／`description`／`tags` の上限、本文 25 MiB、`MAX_VERSIONS` 50、`MAX_AUTO_WIDGET_ARTIFACTS` 200 は変わりません（同 1176-1185行）。

### 公開の可視性と公開済みリンク

- **公開フロー**は、利用者が Private を選ばない限り `visibility: PUBLIC` を要求します。Private は初回の公開で、宛先の共有モデルが両方に対応するときだけ提示されます。再公開は選択肢を出さず、現在の可視性を保ちます。再公開で見える範囲が狭まるときは、内容を送る前に共有を変更します（`artifacts.md` 940-958行）
- **公開済みの artifact のリンク**: Publish パネルは開くときに `GET /api/deploy/list` を読み、artifact の slug に一致する `site_id` のサイトがあれば、公開 URL・Open リンク・「Update (same URL)」を出します。一致しない、`configured: false`、または一覧が読めない場合は、宛先の一覧はそのままです。teardown・期限切れの reaper・ダッシュボード外での削除で消えたサイトは表示されません。詳細ページは `/api/deploy/list` を呼びません（`artifacts.md` 756-788行）

### その他

- **`artifact_update` の `clear_tags: true`** は、すべてのタグを外します（ツールが `tags: []` を送ります）。空でない `tags` と併用すると拒否されます（`artifacts.md` 450行）
- **リモート artifact の閲覧**: プロバイダが一覧できないスコープは 400（`code: "scope_unsupported"`）で、`/artifacts` ページは次のスコープを試します（`artifacts.md` 513行）
- **行内コメント**: artifact のコードブロックは行にアンカーしたコメントを受け、Mate のサイドパネルの文書はインラインコメントを受けます（CHANGELOG.md v0.11.0節 108-109行）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
出典: CHANGELOG.md v0.10.0節 249-255行・v0.11.0節 79-82・108-109行（`fe6f5be`）
**出典**: <https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20。「Dynamic Dashboard (Preview)」節）

## v0.9.0での変更

### Dynamic Dashboard（Preview・既定オフ）

> **v0.10.0 で Preview ではなくなりました**（上記「[v0.11.1での変更](#v0111での変更)」）。以下は v0.9.0 時点の記述です。公式 `capabilities/agents` は引き続き Preview と記述し、出典間で食い違っています。

**Dynamic Dashboard は developer Feature Preview で、既定オフです**（v0.9.0 時点。Settings → Developer → Feature Previews。`PREVIEW_DASHBOARD`）。CHANGELOG は、Settings → Developer → Feature Previews → Dynamic Dashboard をオンにすると、crewmate（v0.11.0 以降の UI では Mate）のサイドパネルに Dashboard タブが開くと記載していました（CHANGELOG.md v0.9.0節 30-41行）。

- **12 のページから選ぶ**: 既定ではプロジェクトレポートを表示し、スタンドアップ・ロードマップ・かんばんなど、出荷済みの別のページはチャットで crewmate に頼みます（CHANGELOG の記述。公式 `capabilities/agents`（Page updated 2026-10-20）128-132行も同じ Preview 機能として記述し、Kiro Crew が出荷するページから選ぶだけで、crewmate が自分でページを書くことはできないとしています）
- **数値は記録から**: 図の数値はすべて crewmate の crew log から読み取られます。測られていないコストは 0 ではなくダッシュで表示され、crewmate 自身が書いた値には「crewmate wrote this」の印が付きます（CHANGELOG の記述）
- **全セッションのカード**: 同じ Preview が、コンポーザの上にステータス行と All Dashboards ページを加えます。**Automatic cards for all sessions** スイッチをオンにすると、各セッションの直近の作業と次の手順の要約が保たれます（CHANGELOG の記述）
- **仕様書の記述**: `dashboard.dynamic_dashboard_cards` を有効にすると、ホストのセッションイベントが、そのセッションの直近の（秘匿処理済みの）メッセージだけを使うバックグラウンド更新を積みます。自動カードが付くのは**ルートセッションだけ**で、カードの数値はすべてセッションの crew log を畳み込んだ値です。モデルが書くのは `lede`・`you`・`notes` の 3 つの文だけで、数字を含む出力はカード全体が拒否されます。v0.9.0 の仕様書は、`task-dashboard` タグ付きの HTML／ウィジェット artifact を、モデルが作ったタスクビューと記述していました（`artifacts.md` 35-146行）。v0.11.1 では、この artifact は読まれません（上記「v0.11.1での変更」）
- **crew log が必要**: `KIROCREW_CREW_LOG` を無効にすると畳み込む記録がなく、自動カードは生成されません（同 62-63行）。Crew log は v0.8.0 から既定オンです（[08_mcp-integration.md](08_mcp-integration.md#crew-log) 参照）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。35-146行）
出典: CHANGELOG.md v0.9.0節 30-41行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20。「Dynamic Dashboard (Preview)」節）

## v0.7.0での変更

- **Cmd+K から Artifacts を探せる**: Command Bar（Cmd+K）の **Search Artifacts** 行が最新の artifact を一覧し、入力に応じて名前で絞り込み、選んだものを開きます
- **「From your chats」の読み取り専用プレビュー**: Artifacts ページの **From your chats** の行から、ヘッダに保存スター付きの読み取り専用プレビューを開けます

出典: CHANGELOG.md v0.7.0節 370-373行（v0.7.2 タグのファイルの行番号、`c67c506`）。公式ページ `chat/artifacts/`・`features/artifact-deploy/` の内容は、v0.6.0 対応時と v0.7.2 対応時の取得内容で差分がありません（Deploy の3ティア・ベーススタック・reaper・TTL の記述も不変）。

**出典**: <https://kiro.dev/docs/crew/chat/artifacts/>・<https://kiro.dev/docs/crew/features/artifact-deploy/>（Page updated 表記あり）

## v0.3.0での変更

### 画像がartifactとして保持されるようになった

**エージェントが生成したスクリーンショットや図が、ギャラリー・詳細ページ・メタデータとともに保持されます。**

> **既存の記述との関係**: `kind` enumに `image` が含まれること自体は以前から`modules/artifacts.md`（`21584ea`では41行）に定義されており、`image` artifactは**ラスタ画像**（テキストではない）としてバイナリで保存されます（同887行以降。SVGは意図的に image artifact ではなくマークアップとして扱われます）。v0.3.0の変更は、**エージェントが生成した画像がartifactとして保持され、閲覧のためのギャラリーと詳細ページが提供されるようになった**という点です。

出典: CHANGELOG.md v0.3.0節 140行（`21584ea`）「**Images are kept as artifacts** — Screenshots and diagrams the agent produces are preserved with a gallery, a detail page, and metadata」。

### 公開デプロイに明示的な承諾が必要になった

**artifactを公開する（public deploy）際に、明示的な承諾が求められます。** また**運用者はこの経路を完全に閉じることもできます**。

出典: CHANGELOG.md v0.3.0節 109行（`21584ea`）「**A public deploy asks first** — Publishing an artifact publicly requires an explicit acknowledgement, and an operator can close the path entirely」。上記「[Artifact Deploy](#artifact-deploy)」の4ステップフローに対する追加のゲートです。

## 未確認事項

- 公式 `chat/artifacts/`（Page updated 2026-09-12）は、ウィジェットの自動登録とスナップショットの既定、タグの規則、`source` の種類を記述していません。これらはリポジトリの `modules/artifacts.md`（v0.11.1）に基づきます
- Dynamic Dashboard が Preview かどうか、および Mate（公式では crewmate）が自分のページを書けるかどうか: CHANGELOG v0.10.0節・`artifacts.md`（v0.11.1）は Preview 不要と記述し、公式 `capabilities/agents`（Page updated 2026-10-20）は Preview で出荷済みのページから選ぶだけと記述します。本サイトは裁定しません（上記「[v0.11.1での変更](#v0111での変更)」の ⚠ を参照）
- 上記以外の本ページの記述は、公式2ページ（Page updated 2026-09-12。v0.7.2 の時点から日付・内容とも変更なし）と `modules/artifacts.md`（v0.11.1）で確認済みです。v0.9.0 の節の行番号は v0.9.0 のファイルのものです

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/artifacts/>、<https://kiro.dev/docs/crew/features/artifact-deploy/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
- App: [10_apps.md](10_apps.md)

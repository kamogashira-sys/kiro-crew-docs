# 成果物（Artifacts）

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/chat/artifacts/>・<https://kiro.dev/docs/crew/features/artifact-deploy/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [2つのArtifacts概念](#2つのartifacts概念)
- [チャット内Artifacts](#チャット内artifacts)
- [Artifact Deploy](#artifact-deploy)
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

`artifacts.md` 902-998行は、自動登録の条件を次のとおり記述しています。

- エージェントが発行した `<mcwidget>` は、アシスタントの発言区間が確定したときにバックエンドが自動で登録します。登録された記録は**ピン留めなし**で、ライブラリの項目ではなく「記録」です。ウィジェット上の星は、記録の作成ではなく `pinned` の切り替えです
- 登録は**冪等**です。同じスラッグが既にあれば触りません。明示的な `slug=` 属性付きのウィジェットは、新規作成ではなく既存の artifact を指す再掲示として扱われ、登録されません
- **シークレット（incognito）／一時（temporary）のセッションでは登録されません**（これらのセッションは artifact の書き込みがすべて拒否されるため）
- **保持**: 自動登録されたままの記録は、`MAX_AUTO_WIDGET_ARTIFACTS`（200）を超えると古い順に削除されます。削除の対象になるのは、ピン留め・フォルダ・公開・フォーク情報・説明／タグ・編集・コメントのいずれも無い記録だけです。明示的な保存で作った artifact は削除されません

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。8-17行・902-998行）

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

`kind` フィールドは `widget`／`html`／`markdown`／`svg`／`json`／`text`／`webapp`／`image` のenumで、保存時に呼び出し元が省略すると推論されます。`source` に保存される値は `chat`（既定）／`cron`／`subagent`／`manual`／`import`／`dashboard`／`slack`／`cli`／`task-runner`／`unknown` の **10 種**です。MCP の保存スキーマが明示的に受け付けるのは先頭の 5 種です（`artifacts.md` 329・1122行）。v0.7.2 の仕様書は 5 種を記述していました。

**出典**（保存レイアウト・`kind`・`source`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。309-335行）

### 保存・バージョン・タグの規則

`artifacts.md`（v0.9.0）の記述です。CHANGELOG/Release 本文は、このうち次の項目を説明していません（v0.7.2 の仕様書との差は各項目に示します）。

- **スナップショット**: `update(slug, content=…, snapshot=False)` はバージョンを増やさずに現在の内容を更新し、`snapshot=True` のときバージョン番号が増えて `versions/vN.html` が書かれます。**MCP の `artifact_update` は既定でスナップショットを取り、ダッシュボードの Save は `snapshot: true` を送らない限り取りません**（1298-1307行）。`artifact_revert` は以前のバージョンの内容を、`reverted` タグ付きの新しいスナップショットとして書き込みます（498行）
- **同時書き込みの検出**: `PATCH /api/artifacts/{slug}` は、内容を書くたびに入れ替わる `content_token` を持ちます。直前の読み取りの `expected_token` を付けると、その後に別の内容の書き込みがあった場合は 409（`artifact_conflict`）で何も書かれず、不正な値は 400 です（541行）
- **コメントの取得**: `artifact_get_comments` は `exclude_resolved=true` で解決済みスレッドをスレッドの根単位で除外できます（506行・1328行）
- **オーナー限定**: ダッシュボードから artifact の状態を変えるルート（作成・編集・削除・公開・共有・フォルダ・ピン・コメントなど）は、ダッシュボードのオーナーだけが使え、オーナー以外にはすぐに 403（`owner_only`）が返ります。Gateway ループバックの内部経路（エージェントの `artifact_*` ツール・CLI・App のドライバ）と、マニフェストの付与の範囲内の App トークンは対象外で、それぞれ自身の規則に従います（300-307行）

値の上限（`artifacts.md` 1109-1124行）:

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
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。300-307行・498行・506行・541行・1109-1124行・1298-1307行・1328行）

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

## v0.9.0での変更

### Dynamic Dashboard（Preview・既定オフ）

**Dynamic Dashboard は developer Feature Preview で、既定オフです**（Settings → Developer → Feature Previews。`PREVIEW_DASHBOARD`）。CHANGELOG は、Settings → Developer → Feature Previews → Dynamic Dashboard をオンにすると、crewmate のサイドパネルに Dashboard タブが開くと記載しています（CHANGELOG.md v0.9.0節 30-41行）。

- **12 のページから選ぶ**: 既定ではプロジェクトレポートを表示し、スタンドアップ・ロードマップ・かんばんなど、出荷済みの別のページはチャットで crewmate に頼みます（CHANGELOG の記述。公式 `capabilities/agents`（Page updated 2026-10-20）128-132行も同じ Preview 機能として記述し、Kiro Crew が出荷するページから選ぶだけで、crewmate が自分でページを書くことはできないとしています）
- **数値は記録から**: 図の数値はすべて crewmate の crew log から読み取られます。測られていないコストは 0 ではなくダッシュで表示され、crewmate 自身が書いた値には「crewmate wrote this」の印が付きます（CHANGELOG の記述）
- **全セッションのカード**: 同じ Preview が、コンポーザの上にステータス行と All Dashboards ページを加えます。**Automatic cards for all sessions** スイッチをオンにすると、各セッションの直近の作業と次の手順の要約が保たれます（CHANGELOG の記述）
- **仕様書の記述**: `dashboard.dynamic_dashboard_cards` を有効にすると、ホストのセッションイベントが、そのセッションの直近の（秘匿処理済みの）メッセージだけを使うバックグラウンド更新を積みます。自動カードが付くのは**ルートセッションだけ**で、カードの数値はすべてセッションの crew log を畳み込んだ値です。モデルが書くのは `lede`・`you`・`notes` の 3 つの文だけで、数字を含む出力はカード全体が拒否されます。`task-dashboard` タグ付きの HTML／ウィジェット artifact は、モデルが作ったタスクビューです（`artifacts.md` 35-146行）
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

- 公式 `chat/artifacts/`（Page updated 2026-09-12）は、ウィジェットの自動登録とスナップショットの既定、タグの規則、`source` の種類を記述していません。これらはリポジトリの `modules/artifacts.md`（v0.9.0）に基づきます
- Dynamic Dashboard について、公式 `capabilities/agents` は crewmate が選べるのは出荷済みのページだけで、自分でページを書けないと記述します。`artifacts.md` は `task-dashboard` タグ付きの HTML／ウィジェット artifact を「モデルが作成したタスクビュー」と記述します。両者が同じ表示面の記述か別の面の記述かは、一次情報から確認できないため、本サイトは裁定しません
- 上記以外の本ページの記述は、公式2ページ（Page updated 2026-09-12。v0.7.2 の時点から日付・内容とも変更なし）と `modules/artifacts.md`（v0.9.0）で確認済みです

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/artifacts/>、<https://kiro.dev/docs/crew/features/artifact-deploy/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
- App: [10_apps.md](10_apps.md)

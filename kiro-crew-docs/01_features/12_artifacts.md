# 成果物（Artifacts）

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/chat/artifacts/>・<https://kiro.dev/docs/crew/features/artifact-deploy/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [2つのArtifacts概念](#2つのartifacts概念)
- [チャット内Artifacts](#チャット内artifacts)
- [Artifact Deploy](#artifact-deploy)
- [未確認事項](#未確認事項)

---

## 2つのArtifacts概念

**公式は別ページとして扱う2つの「Artifacts」を明確に区別します。**

| # | 名前 | 公式パス | 内容 |
|---|------|---------|------|
| ① | **チャット内のArtifacts** | `docs/crew/chat/artifacts/` | 会話の中で生成・閲覧する成果物（永続的な識別子・バージョン履歴を持つ） |
| ② | **Artifact Deploy** | `docs/crew/features/artifact-deploy/` | 生成物を自分のAWSアカウントへワンクリックデプロイする機能。公式ナビの表示名は「**Artifacts**」 |

> Rev 1（旧版計画）では②の担当ページが存在せず、公式43ページの中で唯一未割当のままだった経緯があります。本ページで両方を扱うことでこれを解消しています。

## チャット内Artifacts

チャットでレンダリングされるLLM生成のUIに、永続的な識別子・バージョン履歴・セッションを跨いで反復できる安定したハンドルを与える機能です。

典型的なフロー:

1. エージェントがチャットで `<mcwidget>` を発行（「これがCRキューです」）
2. エージェント（またはユーザー）が `artifact_save` を呼び、ウィジェットが `~/.kiro/crew/artifacts/<slug>/current.html` に永続化される
3. 数日後、新しいセッションでユーザーが「cr-queueのartifactを改良して年齢列を追加して」と言う
4. エージェントが `artifact_get("cr-queue")` で現在のHTMLを読み、変更を加え、`artifact_update("cr-queue", content=…)` で新バージョンを公開
5. 前バージョンは `versions/v1.html` としてロールバック用に保持される

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

`kind` フィールドは `widget`／`html`／`markdown`／`svg`／`json`／`text`／`webapp`／`image` のenumで、保存時に呼び出し元が省略すると推論されます。`source` は `chat`（既定）／`cron`／`subagent`／`manual`／`import`。

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

## 未確認事項

- なし（本ページの記述は公式2ページと `modules/artifacts.md` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/artifacts/>、<https://kiro.dev/docs/crew/features/artifact-deploy/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/artifacts.md>
- App: [10_apps.md](10_apps.md)

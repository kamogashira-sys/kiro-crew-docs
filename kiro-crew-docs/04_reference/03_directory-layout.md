# ディレクトリ構造

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: リポジトリ README「Legacy `~/.kirocrew` → `~/.kiro/crew` data-home migration」
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [データホーム](#データホーム)
- [ディレクトリ構造の詳細](#ディレクトリ構造の詳細)
- [旧パスからの移行](#旧パスからの移行)
- [未確認事項](#未確認事項)

---

## データホーム

Kiro Crew の永続状態は **`~/.kiro/crew/`** に置かれます。環境変数 **`KIROCREW_HOME`** で変更できます。このルートは kiro-cli 自身の `~/.kiro/` の下にネストしており、Kiro ファミリーの各アプリが1つのディレクトリを共有して保護できるようになっています。

## ディレクトリ構造の詳細

公式アーキテクチャ文書が示す構造です（抜粋）。

```
~/.kiro/crew/
├── config.json             # ユーザー設定（+ config.local.json オーバーレイ）
├── .env                    # チャネルのトークン・owner id
├── security_policy.json    # ガバナンスの POLICY 上限（トラストルート）
├── profiles/               # ガバナンスの PROFILE スコープ（トラストルート）
├── computer_use.json       # Computer Use のキーストーン有効化（トラストルート）
├── workspace/
│   ├── memory/             # preferences.md, projects.md, history/
│   ├── knowledge/          # knowledge.db（FTS5 + グラフ + ベクトル）
│   └── HEARTBEAT.md        # heartbeatタスク一覧
├── sessions/               # JSONL会話ログ（+ archive/）
├── lessons.jsonl           # 学習した修正内容
├── crons.json               # スケジュールされたジョブ
├── crons/                  # cronスクリプト本体
├── hooks.json              # webhookワークフローのコンテキスト
├── instances.json          # リモートインスタンスのレジストリ
├── security_events.jsonl   # SEL監査チェーン
├── artifacts/              # 保存されたartifacts + バージョン履歴
├── apps/                   # インストール済みApp
├── skills/                 # バンドルからコピーされたスキル + ユーザースキル
├── snapshots/               # 移動可能な状態のスナップショット
└── gateway.log              # Gatewayログ
```

生成された kiro-cli 用のエージェント JSON は**このディレクトリには置かれません**。kiro-cli がエージェント仕様を読み込む `~/.kiro/agents/`（`kiro_home()/agents`）に書かれます。このディレクトリは唯一の**書き込み**先であり、プロジェクト固有の `<project>/.kiro/agents/` はプロジェクトに紐づくセッション用に追加で**読み込み**対象になります（kiro-cli がそのディレクトリを最初に検索するため）。

## 旧パスからの移行

**旧パス `~/.kirocrew` は現行では使いません。** リポジトリの README には「Legacy `~/.kirocrew` → `~/.kiro/crew` data-home migration」という節があり、旧パスから新パスへの移行が**自動的に行われる**ことが明記されています。

> ⚠️ `docs/system-specs/post-launch-removals.md`（移行完了後に削除予定のコードを記録した内部台帳）に旧パスの記述が残っていますが、これは**削除予定の移行専用コードの記録**であり、現行の仕様として引用しません。「旧パスが完全に移行済みである」という事実の裏付けとしてのみ参照します。

## 未確認事項

- なし（本ページの記述は `docs/architecture/overview.md` のディレクトリ構造とリポジトリ README で確認済み）

## 関連リンク

- 公式リポジトリ: <https://github.com/kirodotdev/KiroCrew>
- アーキテクチャ: [01_features/01_architecture.md](../01_features/01_architecture.md)
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)

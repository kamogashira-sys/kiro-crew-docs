# ディレクトリ構造

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（ツリーの再測定・旧パス `~/.kirocrew` の扱いの訂正）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.9.0での再測定: ツリーの2行追加・ツリー以外のパス・旧パスの行番号）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://kiro.dev/docs/crew/installation/>（Page updated 2026-10-20）

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

公式アーキテクチャ文書が示す構造です（抜粋。`overview.md` 662-684行、`99e6253`）。**v0.7.2 までは v0.6.0 から変更がありませんでしたが、v0.8.0 のタグで `members/`・`memory_stores/` の2行が加わり**（v0.8.0 の `overview.md` 664-665行）、v0.9.0 の `overview.md` では `lessons.jsonl` の注記も「Global V1 learned corrections」になっています。他の行は同じです。

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
├── members/                # 安定した crew-member の ID と brief
├── memory_stores/          # member／名前付きのストア（SQLite のメモリと lessons）
├── sessions/               # JSONL会話ログ（+ archive/）
├── lessons.jsonl           # Global V1 の学習した修正内容
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

### ツリー以外の文書に現れるデータホーム内のパス

上のツリーは `overview.md` の抜粋（「Selected entries」）であり、本サイトはツリーに項目を追加しません。ほかの一次情報には、データホーム内の次のパスが現れます（出典は `99e6253`／v0.9.0 の行番号）。

| パス | 内容 | 出典（`99e6253`） |
|---|---|---|
| `models/` | 埋め込みモデル（約610 MB）の保存先 | 公式 `installation/` ページ（`docs_md/installation.md` 33行。Page updated 2026-10-20） |
| `channel` | ワンライナーインストーラが選択したチャネルの記録 | `docs/guides/install.md` 203行 |
| `.vault` | 暗号化secrets vault（MCPサーバの認証情報等）。OSサンドボックスがエージェントから隠す | `docs/system-specs/modules/security.md` 634・649-653行 |
| `tasks/tasks.db` | 受け付けたサブエージェントのspawnを永続化する耐久タスクキュー（`agent.task_queue_enabled`） | `docs/system-specs/modules/config.md` 2661行 |
| `ssh_auth_sock_consent.json` | `SSH_AUTH_SOCK` 転送のkeystone同意（自分の端末で作成） | 公式 `security/` ページ（`docs_md/security.md` 212行。Page updated 2026-10-12） |
| `crew-log/`（`crews/<store>/`・`sessions/<store>/`・`members/<store>/` の各 `log.jsonl`） | Crew log。**v0.8.0 から既定オン**（[03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)）。会話を削除またはtrashへ移すと、対応する記録は `crew-log/trash/<batch>/<uid>/` へ移る | `docs/system-specs/modules/crew-log-core.md` 22-24行、`session-storage.md` 333-340行 |
| `cloud.json` | `kirocrew cloud` の保存（profile・region・最新のインスタンス tag）と任意の `fargate` ブロック。運用者が手で編集し、エージェントのファイル編集ツールは書き込みを拒否する | `docs/system-specs/modules/cli.md` 686-692行、`cloud.md` 198-200・410-414行 |
| `cloud-src-staging/` | `kirocrew cloud launch` のソース tarball をステージする所有者専用のディレクトリ（`TMPDIR` は使わない） | `docs/system-specs/modules/cloud.md` 705行 |
| `folders.json` | チャットのフォルダ記録。各フォルダは任意の `steering_dirs` を持つ | `docs/system-specs/modules/config.md` 354行、`docs/guides/remote-and-mobile.md` 197行 |
| `audit.log` | `execute_bash` 呼び出しの監査（同梱の `postToolUse` hook が追記）。`kirocrew chat` の開始時にもサイズの整理が1回走る | `docs/system-specs/modules/cli.md` 1003-1010行 |
| `mcp-launch-approvals/approvals.json` | MCP の解決済み起動コマンドの承認記録。OSサンドボックスは事前作成したこのディレクトリをマウントする | `docs/system-specs/modules/security.md` 9・33行 |
| `logs/autonudge_stops.jsonl` | 監視ループが止まった理由の記録 | `docs/system-specs/modules/monitor-architecture.md` 658行 |
| `cache/slide-previews/<sha256>/` | PowerPoint のスライドのプレビューのキャッシュ（`manifest.json` と `slide-<n>.png`） | `docs/system-specs/modules/learn-cron-dashboard.md` 3692行 |
| `sessions/<stem>.attachments/`・`sessions/.threads/<stem>.json` | トランスクリプトの添付ディレクトリと返信スレッドの sidecar | `docs/system-specs/modules/session-storage.md` 21行 |

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（データホームのツリー）
> 公式 `installation/` ページ「Data home」節（`docs_md/installation.md` 159-176行。Page updated 2026-10-20）のツリーは、上の `overview.md` のツリーと異なる項目を含みます: `workspace/lessons.jsonl`（`overview.md` はデータホーム直下の `lessons.jsonl`）、`conversations/`（`overview.md` は `sessions/`）、`audit.log`（`overview.md` は `security_events.jsonl`）、`agents/`（`overview.md` は「生成された kiro-cli 用のエージェント JSON はこのディレクトリには置かれない」と記述）。公式 `configuration/` ページの「Data home」節は、ディレクトリ構成についてこの `installation/` ページを参照するよう案内しています。**食い違いは v0.9.0 でも継続しています**: 公式ページのツリーは v0.7.2 から変わっておらず、`overview.md` のツリーは上記のとおり2行増えました（v0.8.0〜）。そのため、公式ページのツリーには `members/`・`memory_stores/` もありません。

## 旧パスからの移行

**旧パス `~/.kirocrew` は現行では使いません。自動移行も行われません。**

`overview.md` 658-659行（`99e6253`。v0.7.2 のタグでは 628-629行）は「A legacy `~/.kirocrew` is fully deprecated and does not auto-migrate; it survives only in sensitive-path deny lists」と記述しています。旧パスは完全に非推奨で**自動移行されず**、機密パスの拒否リストにだけ残っています。旧パスのディレクトリが残っている場合、利用者が自分で削除するまで残り続けます。

> **本サイトの以前の記述の訂正（v0.6.0 で既に変わっていた事項）**: 本節は以前、リポジトリ README の節を根拠に「旧パスから新パスへの移行が自動的に行われる」と記載していました。しかし **v0.6.0 の `overview.md` 628-629行の時点で既に「does not auto-migrate」**となっており（自動移行と書いていたのは v0.3.0 の `overview.md` 554-555行「a legacy `~/.kirocrew` is migrated automatically」）、本サイトが追随していませんでした。また、以前の出典欄に挙げた節名「Legacy `~/.kirocrew` → `~/.kiro/crew` data-home migration」は、v0.3.0 のリポジトリ README には見つからず、移行専用コードの台帳（`docs/system-specs/post-launch-removals.md` 12行）の見出しでした。
>
> ⚠️ その台帳（移行完了後に削除予定のコードを記録した内部台帳）は v0.6.0・v0.7.2 では「one-time data-home migration has been removed」と、移行コードが削除済みであることを記録しています（12-15行）。本サイトはこの台帳を現行仕様の出典とはせず、削除の事実の確認にのみ用います。

## 未確認事項

- データホームのツリーについて、公式 `installation/` ページと `docs/architecture/overview.md` の記述が異なる（**継続**。v0.8.0 以降は `overview.md` が `members/`・`memory_stores/` を加えた分も差になっている。上記「ディレクトリ構造の詳細」の注記参照。裁定しない）
- `KIROCREW_HOME` の検証規則（展開・解決したうえで、ファイルシステムやドライブのルート、システムディレクトリを拒否する）は `config.md` 170行にあるが、公式ページには見つかっていない

## 関連リンク

- 公式リポジトリ: <https://github.com/kirodotdev/KiroCrew>
- アーキテクチャ: [01_features/01_architecture.md](../01_features/01_architecture.md)
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)

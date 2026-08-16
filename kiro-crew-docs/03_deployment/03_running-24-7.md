# 常駐化・24時間運用

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/running-24-7/>（Page updated 表記あり）
**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/features/snapshot/>

---

## 📑 このページの内容

- [ローカルサービス化](#ローカルサービス化)
- [Docker常駐](#docker常駐)
- [リモートホスト](#リモートホスト)
- [モバイルアクセス](#モバイルアクセス)
- [マルチインスタンス](#マルチインスタンス)
- [スナップショットと復元](#スナップショットと復元)
- [未確認事項](#未確認事項)

---

Crewは、SlackボットやCronジョブ、Task Runnerがデスクから離れても動き続けるよう、継続運用を想定して設計されています。**公式ページが挙げる4つの一般的な運用パターンは、ローカルサービス化・Docker常駐・リモートホスト・モバイルアクセスです**（マルチインスタンス・スナップショットは公式ページの別項目として本ページ末尾に補足します）。

## ローカルサービス化

最も簡単な方法は組み込みのインストーラです。システムレベルのサービス（Linuxはsystemd、macOSはlaunchd）として登録され、SSH切断後も生き続け、クラッシュ時は自動再起動、起動時は自動起動します。

```bash
kirocrew service install    # ユニットを登録して起動
kirocrew service status     # 稼働状態を確認
kirocrew logs -f            # ライブログを追跡
kirocrew restart            # atomicな再起動（systemd）または unload+load（launchd）
kirocrew service uninstall  # 削除
```

Linuxではインストール時にsudoを1回要求してユニットファイルを書きます。**Gateway自身はユーザー権限で動作**し、rootでは動きません。

**sudoのスコープ**: `kirocrew service install` は `sudo tee`（ユニットファイルの書き込み）と `sudo systemctl ...`（daemon-reload・enable・restart）のみを実行します。`kirocrew`本体・MCP・LLMのコードパスはsudo下では動きません。

サービス化を避けたい場合、`tmux` はSSH切断には耐えますが**クラッシュ時の自動再起動・再起動時の自動起動はしません**。

## Docker常駐

常時稼働のサーバー（Slack/Discordボット、リモートダッシュボード）にはGHCRのマルチアーキイメージを使います。

```bash
docker run -d --name kirocrew \
  -p 127.0.0.1:5476:5476 \
  -v kirocrew-home:/home/kirocrew \
  ghcr.io/kirodotdev/kirocrew:stable
```

初回セットアップは2ステップ:

```bash
# 1. エージェントランタイムにログイン（認証情報はボリュームに残るためアップグレードでも維持）
docker exec -it kirocrew kiro-cli login

# 2. ダッシュボードログインリンクを発行（すべてのリクエストがトークンを要求）
docker exec kirocrew kirocrew token --ttl 2h
```

## リモートホスト

VPS・クラウドVM・自宅の空きマシンなど、常時起動のLinuxリモートホストでCrewを動かせば、ラップトップがスリープしていてもSlack・Cron・Task Runnerが動き続けます。

**ホスト要件**: モダンなLinuxディストリビューション（Ubuntu 22.04+・Debian 12+・Fedora・Amazon Linux 2023等）。`slack-mcp`にはNode 20+が必要。RAMは最低約10GB（MCPのコールドスタートやツール呼び出しでスパイクするため16GBが快適）。x86_64またはarm64。

**⚠️ ダッシュボードのSSHトンネル**: ダッシュボードはリモートホストの`localhost:5476`にバインドされます。**このポートを公開してはいけません**。ローカルマシンへSSH経由でフォワードしてください。

```bash
ssh -L 5476:localhost:5476 user@your-host.example.com
```

`~/.ssh/config`に`LocalForward`を設定すれば、`ssh your-host.example.com`実行時に自動でトンネルが張られます（macOS・Linux・Windows対応。Windows 10+はOpenSSHが標準搭載）。

既存の状態（メモリ・設定・スキル・cron）を新しいリモートホストへ同期する場合は、リポジトリの`scripts/sync-to-remote.sh`が使えます。WALファイル（`memory.db-wal`・`memory.db-shm`）も同期が必要で、`.env`・`.local_secret`・`sel_hmac.key`はホスト固有のためコピーしてはいけません（初回起動時に再生成されます）。

## モバイルアクセス

ローカルポートを named HTTPS tunnel で公開し、Slackボットの presigned link をそのtunnel URLに向けることで、スマートフォンからダッシュボードにアクセスできます。

ダッシュボードはCrewを動かすホストの`localhost:5476`にバインドされます。Cloudflare Tunnel・ngrok・Tailscale Funnelなどのトンネリングサービスが、そのローカルポートにプロキシする安定したパブリックHTTPS URLを提供します。取得したURLを`dashboard.url`に設定すると、Slackボットがそのリンクを生成します。

**⚠️ 重要な警告**: **トンネルはダッシュボードをパブリックインターネットに公開します**。Crewはセッションごとのトークンでダッシュボードを保護しますが、Cloudflare AccessやTailscaleのプライベートネットワークなど、自前の認証を追加できるトンネルプロバイダを使い、トークンの有効期間も短く保つことが推奨されます。

ダッシュボードトークンは既定1時間（最大20時間まで設定可）、presigned linkのクリック有効期限は5分です。

## マルチインスタンス

複数のCrewインスタンスを運用するための機能です（詳細は公式 `features/multi-instance/` を参照）。**注記**: 公式ページの「4つの一般的な運用パターン」（ローカルサービス化・Docker常駐・リモートホスト・モバイルアクセス）には含まれず、公式ページの別項目です。

## スナップショットと復元

スナップショットには以下の6項目が含まれます（`features/snapshot/`より）。

| コンポーネント | 内容 |
|---|---|
| **Memory** | Episodic memory・semantic memory・FTSインデックス |
| **Workspace** | Preferences・projects・history・knowledge library |
| **Crons** | すべてのスケジュールジョブ |
| **Config** | 設定・session map・hooks・project/workspaceパス |
| **Skills** | カスタムスキル定義 |
| **Notifications** | ダッシュボードの通知履歴 |

```bash
kirocrew snapshot                     # 既定は ~/.kiro/crew/snapshots
kirocrew restore snapshot.tar.gz      # replace/mergeを自動判定
```

既定で08:00 UTCに実行される`kirocrew-daily-snapshot`という組み込みcronジョブが、直近7件のスナップショットを保持します。

**⚠️ 重要な警告**: **スナップショットには機密データ（監査ログ整合性に使うセキュリティキー）が含まれます**。認証情報と同様に扱い、アクセス権限を制限したストレージに保存し、安全でないチャネルで共有しないでください。

## 未確認事項

- マルチインスタンスの詳細な運用手順（公式ページの参照のみで、本サイトでは概要にとどめる）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/running-24-7/>、<https://kiro.dev/docs/crew/features/multi-instance/>、<https://kiro.dev/docs/crew/features/snapshot/>
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

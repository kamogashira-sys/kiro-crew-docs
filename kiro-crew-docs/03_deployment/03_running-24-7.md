# 常駐化・24時間運用

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/running-24-7/>（Page updated 表記あり）
**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/features/snapshot/>・<https://kiro.dev/docs/crew/system/>
**出典**（Remote Instances の呼称と有効化の2スイッチ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

---

## 📑 このページの内容

- [ローカルサービス化](#ローカルサービス化)
- [Docker常駐](#docker常駐)
- [リモートホスト](#リモートホスト)
- [モバイルアクセス](#モバイルアクセス)
- [マルチインスタンス](#マルチインスタンス)
- [System & storage（リソース監視とディスク回収）](#system--storageリソース監視とディスク回収)
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

### Remote Instances（v0.6.0・Preview・既定オフ）

**v0.6.0 で、接続済みの別インスタンス上でチャットを実行できるようになりました。** 1つの Kiro Crew Gateway（**hub**）が、SSH **または AWS SSM Session Manager** のトンネル経由で複数のリモート Kiro Crew インスタンス（開発ホスト・EC2・自宅サーバ）を管理・切り替えます。各リモートのダッシュボードは、切り替えストリップの下に iframe ペインとして埋め込まれます。トランスポートはインスタンス単位（`connection_method`）です。

> **⚠️ 有効化には2つのスイッチが必要です（どちらも既定オフ）。**
>
> 1. `config.json` の **`instances.enabled`** を設定する
> 2. **Settings → Developer → Feature Previews → Chat on a crew** をオンにする
>
> そのうえでサイドバーの新規チャットメニューの **New chat on crew** から相手を選びます。**トランスクリプトはローカルに残り、各ターンは相手のインスタンス上で実行されます。**

別所で実行されるセッションには **server badge** と相手の名前が表示されます。インスタンスはアプリのロード時とタブのフォーカス時に自分で接続します（既定で有効）。

> **呼称について（一次情報が理由を説明しています）**: CHANGELOG v0.6.0 の見出しは「Remote crews」ですが、`instances.md` 9-21行は**UI上の表示は「Remote Instances」**（*Settings → Remote Instances*、ヘッダの切り替えグループ、キーボードショートカット）だと明記しています。同仕様書は、以前のUI文言が「Remote Crew」であり、コードと設定（`/api/instances`・`instances.json`・`InstancesPanel`・EC2の`instance_id`／`ssm_target`）に合わせて「instance」へ改めたと説明します。**変更されたのは表示文字列のみで、i18nキー名と内部識別子（`remoteCrewPanel` を含む）は変わっていない**ため、コードと仕様書の文中には「crew」が略称として残ります。製品名の **Kiro Crew** や、エージェントの **crew**（独自のワークスペース／メモリを持つアシスタント。「Crew Mode」）とは**意図的に別物**です。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## System & storage（リソース監視とディスク回収）

**v0.6.0 で公式ドキュメントに新設されたページの内容です。** ダッシュボードの **System** 領域は、Crew が自分のマシンに何をしているかを見て後片付けをする場所で、**2つの部分**からなります。

### System: ライブのタスクマネージャ

ダッシュボードから **System** を開くと、セッション単位のリソース使用状況をリアルタイムで確認できます。実行中のセッション・サブエージェント・バックグラウンド処理と、それぞれの消費量が表示されます。公式ページはこれを「Crew 用のタスクマネージャのように読める」と説明しています。

メモリを保持しているセッションやサブエージェントを見つけたり、重い作業を始める前にマシンがアイドルであることを確認するのに使います。

### マシンが埋まったとき

Crew は全体のメモリ圧を監視し、重い作業がホストをスラッシングさせるのではなく穏当に失敗するようにします。**メモリが致命的に少なくなると、スケジュールジョブは延期され、新規サブエージェントは拒否されます。** ダッシュボードのヘッダに現在の姿勢（posture）が表示されるため、要求の重い処理を始める前に把握できます。

**上限は同時実行中の全エージェントの合計に適用**され、spawn単位ではありません。多数の小さなサブエージェントが集まってマシンを食い潰すことはできません。合計値は `config.json` の `resource_limits.max_total_memory_mb` と `resource_limits.max_total_processes` で上書きします。

### Storage: コストを見て容量を回収する

**Storage** 画面は、セッションがディスク上で消費している量（トランスクリプト・添付ファイル・セッション単位の状態）を報告します。長く運用したインストールが静かに満杯になることを防ぐためのものです。

- セッション別のディスク使用量の内訳を見る
- セッションを**削除するのではなくtrashへ移して**容量を回収する
- まだ必要だったものはtrashから復元し、完全に容量を空けるにはtrashを空にする

公式ページは「セッションのインベントリは正直に報告する」と述べ、**アイドルなセッションは「使用中」ではなくアイドルとして表示される**ことを明記しています。

**出典**: <https://kiro.dev/docs/crew/system/>

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

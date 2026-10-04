# 常駐化・24時間運用

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/running-24-7/>（Page updated 表記あり）
**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/features/snapshot/>・<https://kiro.dev/docs/crew/system/>
**出典**（Remote Instances の呼称と有効化の2スイッチ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**（v0.7.0での変更: Remote crews・Fargate・System & storage の改訂）: CHANGELOG.md v0.7.0節、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

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

> **呼称について（v0.7.2 で一次情報間の表記が分かれています）**: v0.7.2 の公式ドキュメントは UI 上の名称を **「Remote crews」** と表記しています（公式 `configuration/` ページの Settings panel 表「**Remote crews**｜SSH, AWS SSM, and Fargate connections」、公式 `features/multi-instance/` ページ「Settings → **Remote crews** → Auto-connect crews」「Open **Settings → Remote crews**, select **Add**」、CHANGELOG.md v0.7.0節 386-387行「under Settings → Remote crews」）。一方、モジュール仕様 `instances.md` 9-21行（`c67c506`）は引き続き **UI上の表示は「Remote Instances」**（*Settings → Remote Instances*、ヘッダの切り替えグループ、キーボードショートカット）と記述しています。v0.6.0 の公式 `features/multi-instance/` ページは「Settings → **Remote Instances** → Auto-connect crews」と記述していました。**どちらが現行のUI表示かは本サイトでは裁定しません。**
>
> `instances.md` は、以前のUI文言が「Remote Crew」であり、コードと設定（`/api/instances`・`instances.json`・`InstancesPanel`・EC2の`instance_id`／`ssm_target`）に合わせて「instance」へ改めたと説明します。**変更されたのは表示文字列のみで、i18nキー名と内部識別子（`remoteCrewPanel` を含む）は変わっていない**ため、コードと仕様書の文中には「crew」が略称として残ります。製品名の **Kiro Crew** や、エージェントの **crew**（独自のワークスペース／メモリを持つアシスタント。「Crew Mode」）とは**意図的に別物**です。

### v0.7.0での変更（Remote crews）

- **`instances.enabled` がライブで適用**: 公式 `features/multi-instance/` ページは「This setting applies live in 0.7」と記述し、手動の再起動なしにレジストリが作られ接続管理が始まるとしています（v0.6.0 の同ページは `kirocrew restart` を手順に含めていた）。
  > ⚠️ 同じページの Troubleshooting 表は、`/instances` が「multi-instance management is off」と表示される場合の対処を「`instances.enabled` is false — set it and restart」と記述しています（同一ページ内の記述差。本サイトは裁定しません）
- **接続方式に AWS Fargate が加わりました**（SSH・AWS SSM に続く3つ目）。Crew を ECS タスクとして動かし、AWS SSM のフォワード経由でタスクの turn API に接続します。**インバウンドのネットワークルールは不要**で、公開リスナーも埋め込みのリモートダッシュボードもありません。接続するラップトップには AWS CLI と Session Manager plugin が必要です。設定は `cloud.json` の任意の **`fargate` ブロック**（クラスタ・サブネット・セキュリティグループ・**digestでピン留めしたイメージのみ**・secretのARN等）に書きます
  - タスクの寿命は**既定6時間**で、`fargate.task_ttl_seconds` で変更できます
  - 同時に走るFargateタスクは**最大10**です
  > ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（最大タスク数を設定できるか）
  > - CHANGELOG.md v0.7.0節 388-390行: 「ten running at most, set by `fargate.task_ttl_seconds` and `fargate.max_running_tasks` in `cloud.json`」
  > - 公式 `features/multi-instance/` ページ: 「this safety ceiling is fixed rather than a `cloud.json` setting」、`docs/system-specs/modules/cloud.md` 208-214行: 「`DEFAULT_MAX_RUNNING_TASKS` stays fixed … Raising the cap is a code change」
  >
  > ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（ダッシュボードからの設定）
  > - 公式 `features/multi-instance/` ページは Settings → Remote crews の Add で選べる方式として Fargate を挙げ、CHANGELOG.md v0.7.0節 386-387行も「connection method under Settings → Remote crews」と記述しています
  > - `docs/system-specs/modules/cloud.md` 178-180行は「there is no wizard step and no dashboard renderer, so an operator writes it by hand」、`docs/guides/adding-a-remote-provisioner.md` 126行は「the lane is reachable through the API and absent from the Set-up selector」と記述しています

**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/configuration/>（Page updated 表記あり）
**出典**（Remote Instances の呼称・Fargateの設定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/adding-a-remote-provisioner.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

**出典**（v0.6.0時点の記述）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## System & storage（リソース監視とディスク回収）

**v0.6.0 で公式ドキュメントに新設されたページの内容です（v0.7.2 で改訂）。** ダッシュボードの **System** 領域は、Crew がマシンに何をしているか・ホストがどれだけの作業を受け入れられるか・セッションがディスクをどれだけ消費しているかを示します。

### Tasks: 実行中の作業

**Tasks** ビューは、実行中のセッション・サブエージェント・スケジュール作業・Task Runnerステップ・ワークフロー呼び出しを、現在の状態とリソース使用量とともに一覧表示します。メモリを保持しているセッションを見つける、**キュー待ちの作業と実行中の作業を区別する**、重い作業を始める前にホストがアイドルであることを確認する、といった用途に使います。

**受け付けられたバックグラウンド作業は耐久タスクキューに記録されます（v0.7.0）。** キュー待ちのサブエージェント・Task Runnerステップ・ワークフロー呼び出しは**Gatewayの再起動後も残り**、ホストが受け入れ可能になるとスケジューリングに戻ります。

> v0.6.0 の公式ページでは、この部分は「System: a live task manager」（セッション単位のリソース使用状況をリアルタイムで見るタスクマネージャ）という見出しでした。

### Services: キャパシティと健全性（v0.7.0）

**Services** タブは、Gatewayのコンポーネントと現在有効なキャパシティを報告します。ここに表示されるサブエージェント上限は**ホストの空きメモリとCPUを反映**するため、余裕が少ないときは**設定した上限より低くなることがあります**。`resource_status` ツールが同じ情報をエージェントに提供し、大きなfan-outやビルドを始める前に狭い経路を選べるようにします。

出典: CHANGELOG.md v0.7.0節 309-313行（`c67c506`）「Queued work outlives a restart … capacity on the System page's Services tab」。

### マシンが埋まったとき

Crew は同時実行中のエージェント全体に**1つの集約上限**を適用します。**メモリが致命的に少なくなると、スケジュール作業は延期され、新しい作業は呼び出し元の契約に応じてキューに留まるか拒否されます。** ヘッダに現在の姿勢（posture）が表示されます。

> v0.6.0 の公式ページは「scheduled jobs defer and new subagents are refused」（新規サブエージェントは拒否）と記述していました。v0.7.2 では「new work remains queued or is refused according to the caller's contract」に変わっています。

集約上限は `config.json` の `resource_limits.max_total_memory_mb` と `resource_limits.max_total_processes` で設定します。

### Crew log（任意・既定オフ）（v0.7.0）

`~/.kiro/crew/.env` に **`KIROCREW_CREW_LOG=1`** を設定して**Gatewayを再起動**すると、新しいセッションについて追記専用のイベント記録が残ります。Crew log パネルはそれを **Status**・**Usage**・**Timeline**・**Tools**・**Approvals** にまとめて表示し、読み取り専用の **`kirocrew-crew-log` MCPサーバ**で、許可されたエージェントが自分の作業単位や自分が起動したセッションを確認できます。

- セッションのwork ledgerも同じログを使い、コンテキスト圧縮をまたいで目標・フェーズ・次の手順・却下したアプローチ・artifactへのポインタを保持します。**フラグがオフのときは記録を拒否**し、監査されない別の保存先に逃がしません
- **既定オフで、有効化にはGatewayの再起動が必要**です。**保存形式はまだpre-release**で、公式ページは生ファイルに対する連携を作らず、パネルとサポートされた読み取りツールを使うよう求めています

出典: CHANGELOG.md v0.7.0節 314-318行（`c67c506`）。終了済みのledgerを掃除するCLI（`kirocrew ledger-sweep`）は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) を参照してください。

### Storage: コストを見て容量を回収する

**Storage** 画面は、セッションがディスク上で消費している量（トランスクリプト・添付ファイル・セッション単位の状態）を報告します。

- セッション別のディスク使用量の内訳を見る
- セッションを**削除するのではなくtrashへ移して**アクティブな保存領域から回収する
- 必要なら復元し、完全に容量を空けるにはtrashを空にする

**アイドルなセッションは、実行中の作業として数えられずアイドルとして表示されます。**

**出典**: <https://kiro.dev/docs/crew/system/>（Page updated 表記あり）

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
- Remote crews の現行UI表示名（公式ドキュメントは「Remote crews」、`instances.md` は「Remote Instances」）
- Fargateの最大同時タスク数（10）を `cloud.json` で変更できるか（CHANGELOG と公式ページ・`cloud.md` で記述が異なる）
- Fargate接続方式をダッシュボードから追加できるか（公式ページ・CHANGELOG と `cloud.md`・`adding-a-remote-provisioner.md` で記述が異なる）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/running-24-7/>、<https://kiro.dev/docs/crew/features/multi-instance/>、<https://kiro.dev/docs/crew/features/snapshot/>
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

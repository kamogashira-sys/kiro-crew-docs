# 常駐化・24時間運用

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/running-24-7/>（Page updated 表記あり）
**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/features/snapshot/>・<https://kiro.dev/docs/crew/system/>
**出典**（Remote Instances の呼称と有効化の2スイッチ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**（v0.7.0での変更: Remote crews・Fargate・System & storage の改訂）: CHANGELOG.md v0.7.0節、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.9.0での再検証: Remote crew sessions・Fargate・Crew log・Usage・スナップショット・Linuxのサービス管理）: CHANGELOG.md v0.8.0節・v0.9.0節、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/remote-crew-on-fargate.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/remote-and-mobile.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.9.0）: <https://kiro.dev/docs/crew/features/multi-instance/>（Page updated 2026-10-20）・<https://kiro.dev/docs/crew/system/>（Page updated 2026-10-20）・<https://kiro.dev/docs/crew/features/snapshot/>（Page updated 2026-09-11）・<https://kiro.dev/docs/crew/running-24-7/>（Page updated 2026-08-04）

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

### Linuxのサービス管理（systemd の system／user の2スコープ）

以下は v0.9.0 タグの `docs/system-specs/modules/cli.md` 239-244行・`docs/guides/install.md` 785-870行で確認した内容です。CHANGELOG/Release 本文は説明していません。

- `kirocrew service status` は `system scope: …` に続けて `user scope: …` を表示し、**いずれかのスコープのユニットが UP**（`ActiveState` が `active` または `reloading`）のときだけ exit 0 です。`activating (auto-restart)` と `failed` は exit 1 です
- `kirocrew stop`・`restart`・`logs`・`service uninstall` は、利用者自身の `systemctl --user` ユニットも扱い、実行したスコープを表示します。`restart` はユニットが短い確認窓のあいだ UP のままであることを確かめ、`activating (auto-restart)` などに落ちたら失敗として報告します
- `service uninstall` は**自分が入れたユニット**（または `Environment="KIROCREW_SERVICE_MANAGED=1"` の行を持つユニット）だけを消し、利用者や配布元の同名ユニットには触れません。**`sudo` で実行してはいけません**（ユーザーのマネージャに届かず `not reachable from this shell` と報告されます）。`service install` は引き続き system unit を書きます
- Linux ではエージェントの runtime がサービスアカウント自身のユーザーマネージャ下で動くため、**`sudo loginctl enable-linger <user>`** が必要です。無いと最後のログアウトで runtime が止まり、以降の spawn はメモリと fork 数の上限なしで起動します。`service install` は linger がオフのとき非致命の警告を出します
- 別の Gateway が同じデータホームを使っているとき、ユニットは exit 78 で一度だけ `failed` になり再起動しません（`RestartPreventExitStatus=`）。この指定が無い古いユニットは `kirocrew service install` を再実行します
- SELinux のホストでは、条件を満たす場合に system unit へ `SELinuxContext=` の行が入ります（条件は `install.md` 849-870行）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

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

**ホスト要件**: モダンなLinuxディストリビューション（Ubuntu 22.04+・Debian 12+・Fedora・Amazon Linux 2023等）。`slack-mcp`にはNode 20+が必要。RAMは公式ページが「~10 GB minimum」と記述（MCPのコールドスタートやツール呼び出しでスパイクするため16GBが快適。下記の注記のとおりリポジトリ側は別の記述）。x86_64またはarm64。

**⚠️ ダッシュボードのSSHトンネル**: ダッシュボードはリモートホストの`localhost:5476`にバインドされます。**このポートを公開してはいけません**。ローカルマシンへSSH経由でフォワードしてください。

```bash
ssh -L 5476:localhost:5476 user@your-host.example.com
```

`~/.ssh/config`に`LocalForward`を設定すれば、`ssh your-host.example.com`実行時に自動でトンネルが張られます（macOS・Linux・Windows対応。Windows 10+はOpenSSHが標準搭載）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（RAMの下限）
> - 公式 `running-24-7/` ページ（`docs_md/running-24-7.md` 115行。Page updated 2026-08-04）: 「~10 GB minimum」
> - リポジトリ `docs/guides/remote-and-mobile.md` 29-35行（`99e6253`）: 「there is no single published floor」（メモリ消費は同時セッション・サブエージェント・MCPサーバの数で変わると説明）
>
> Node.js については、公式 `running-24-7/` ページ114行が `slack-mcp` 向けに「Node 20+」と記述し（Page updated 2026-08-04 から変更なし）、リポジトリの `remote-and-mobile.md` 27-28行はダッシュボードのバンドルのビルド向けに `>=22.12.0` と記述して、`kirocrew doctor` が 22.12.0 未満で失敗するとしています。

既存の状態（メモリ・設定・スキル・cron）を新しいリモートホストへ同期する場合は、リポジトリの`scripts/sync-to-remote.sh`が使えます。公式ページは、WALファイル（`memory.db-wal`・`memory.db-shm`）も同期が必要で、`.env`・`.local_secret`・`sel_hmac.key`はホスト固有のためコピーしてはいけない（初回起動時に再生成される）と記述しています（155・157行）。

スクリプト自体の仕様は、リポジトリの `remote-and-mobile.md` 149-200行（`99e6253`）が次のように記述しています。

- 一方向（ローカルがリモートを上書き）です。ポートを省くとスクリプトの `DEFAULT_PORT`（現在 `7779`）を使うため、標準のGatewayポート `5476` を明示します
- `sqlite3` があれば `memory.db` を原子的な `.backup` で取ります。無い場合は警告して DB と WAL／SHM をそのままコピーするため、ローカルのGatewayが書き込み中は安全性が下がります。公式ページ159行も「atomic SQLite backup」を扱うと記述しており、WAL ファイルの同期を求める155行の警告とは、スクリプトを使うか手で同期するかの違いがあります（両ページの関係は本サイトでは裁定しません）
- `~/.kiro/agents/` はコピーされないので、カスタム agent 仕様は別に作り直します。旧形式の `lessons.jsonl` もコピーされないため、別に転送します
- 設定は上書きしたあとに `dashboard.url` を修正するため、コピー前に旧形式のインライン資格情報が無いか確認します

## モバイルアクセス

ローカルポートを named HTTPS tunnel で公開し、Slackボットの presigned link をそのtunnel URLに向けることで、スマートフォンからダッシュボードにアクセスできます。

ダッシュボードはCrewを動かすホストの`localhost:5476`にバインドされます。Cloudflare Tunnel・ngrok・Tailscale Funnelなどのトンネリングサービスが、そのローカルポートにプロキシする安定したパブリックHTTPS URLを提供します。取得したURLを`dashboard.url`に設定すると、Slackボットがそのリンクを生成します。

**⚠️ 重要な警告**: **トンネルはダッシュボードをパブリックインターネットに公開します**。Crewはセッションごとのトークンでダッシュボードを保護しますが、Cloudflare AccessやTailscaleのプライベートネットワークなど、自前の認証を追加できるトンネルプロバイダを使い、トークンの有効期間も短く保つことが推奨されます。

ダッシュボードトークンは既定1時間（最大20時間まで設定可）、presigned linkのクリック有効期限は5分です。

## マルチインスタンス

複数のCrewインスタンスを運用するための機能です（詳細は公式 `features/multi-instance/` を参照）。**注記**: 公式ページの「4つの一般的な運用パターン」（ローカルサービス化・Docker常駐・リモートホスト・モバイルアクセス）には含まれず、公式ページの別項目です。

### Remote crews（呼称はv0.9.0で「Remote Crew」に統一）

**v0.6.0 から、1つの Kiro Crew Gateway（hub）が、SSH または AWS SSM Session Manager のトンネル経由で複数のリモート Kiro Crew（開発ホスト・EC2・自宅サーバ）を管理・切り替えできます。** 各リモートのダッシュボードは、切り替えストリップの下に iframe ペインとして埋め込まれます。トランスポートはインスタンス単位（`connection_method`）です。v0.7.0 で AWS Fargate が3つ目の接続方式に加わりました（下記）。

**呼称（v0.9.0 で一次情報間の食い違いは解消）**: v0.9.0 の公式ドキュメントとモジュール仕様 `instances.md` は、UI 名をどちらも **「Remote Crew」** と記述しています。公式 `configuration/` ページの Settings 表（28行）は「**Remote Crew**｜SSH, AWS SSM, and Fargate connections」、公式 `features/multi-instance/` ページは「Settings → Remote Crew」「Add remote crew」（15・23・96行）、`instances.md` 9-11行は Settings セクション・ヘッダの切り替えグループ（「Remote Crews」／「Switch crew」）・キーボードショートカットを「Remote Crew」と記述します。**v0.7.2 では、公式が「Remote crews」、`instances.md` が「Remote Instances」と表記が分かれていました**（v0.6.0 の公式ページは「Remote Instances」）。コードと設定は引き続き「instance」を使います（`/api/instances`・`instances.json`・`instances.enabled`・EC2の`instance_id`／`ssm_target`）。製品名の **Kiro Crew** や、エージェントの **crew**（独自のワークスペース／メモリを持つアシスタント。Crew Members ページ）とは**意図的に別物**です（`instances.md` 9-18行）。

**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-10-20）
**出典**（呼称）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/instances.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### v0.9.0での変更（Remote crew sessions）

**Remote crew sessions（Preview・既定オフ）**

> **⚠️ Preview 機能です。有効化の手順は次のとおりです。**
>
> 1. `instances.enabled` を `true` にして Gateway を再起動する（Gateway は起動時にこの値を読みます）
> 2. **Settings → Remote Crew** で crew を接続する
> 3. **Settings → Developer → Feature Previews → Remote crew sessions** をオンにする

- Sessions 一覧は **Local** を先頭に、接続済みの crew ごとの折りたたみグループになります。各グループの見出しに **Online**・**Reconnecting**・**Error**・**Offline** のバッジが付きます。折りたたんでも選択は変わりません。接続済みの crew が無いダッシュボードにはグループ見出しが出ません
- crew のグループからセッションを開くと、**相手の transcript・実行状態・承認待ちを hub のプロキシ経由で読む窓**として開きます。送信・停止・承認・継続・再生成・巻き戻しは、相手の route を呼びます。**このマシンには、メモリ上のキャッシュ以外は保存されません**（CHANGELOG.md v0.9.0節 84-95行によれば、New chat on crew も相手側にセッションを作ります）
- **両マシンで Kiro Crew の版が同じである必要があります**。一致しない場合、窓が双方の版を表示します
- 自動接続の動作は **Settings → Remote Crew → Auto-connect crews** にあります

**旧 relay の廃止**: v0.8.0 までの **Chat on a crew** プレビューは、ローカルのチャットの各ターンを選んだ remote crew で実行し、transcript はこのマシンに残していました。**この turn relay は v0.9.0 で廃止されました**（公式ページは「Before 0.9」の機能として記述）。relay で動いたチャットは**読み取り専用**で開き、送信・再生成など新しいターンを起こす操作は「remote crew で動いたチャット」という通知とともに拒否されます。続きは Remote crew sessions で相手の crew のセッションを開いて行います。

**`instances.enabled` は起動時に読まれる**ため、変更後に Gateway を再起動します。v0.7.2 の公式ページは「This setting applies live in 0.7」と記述しながら Troubleshooting 表では「set it and restart」と書いており、同一ページ内で食い違っていましたが、v0.9.0 の公式ページは起動時に読まれる旨の記述と Troubleshooting 表が一致しています（`config.md` 2547行も `instances.enabled` を再起動が必要なキーに挙げます）。

出典: 公式 `features/multi-instance/` ページ（Page updated 2026-10-20）13-27・35行、CHANGELOG.md v0.9.0節 84-95行（`99e6253`）、`docs/system-specs/modules/config.md` 2547行
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### v0.8.0での変更（EC2のサブネット指定・crewの連鎖）

- **EC2 のサブネット指定**: `instances.enabled` が有効なとき、Settings → Remote Crew の EC2 起動フォームに任意の **Subnet ID** 欄があります。指定すると crew はそのサブネットと VPC に置かれ、Kiro Crew は起動前に NAT またはインターネットゲートウェイへの経路を確認し、無ければ欠けた経路を示して止まります。空のままにすると自動検出のままです。インターネットへの出口が必要です（公式 `features/multi-instance/` ページ55-57行、CHANGELOG.md v0.8.0節 431-434行）
- **crew の連鎖**: リモートダッシュボードのペイン内で別の remote crew に接続すると、自分のダッシュボードの最上位タブとして採用されます（親 crew の下にインデント表示。親が落ちると使えなくなる）。**連鎖は2ホップまで**（自分 → SSH 接続の crew → 別の crew）で、親は SSH で到達している必要があり、**親1つにつき連鎖先は最大8**、親を削除すると連鎖先も削除されます（公式 同ページ142-146行、CHANGELOG.md v0.8.0節 435-439行）
- **Fargate の `internal_only`**: 下記「Fargate」の節を参照してください（CHANGELOG.md v0.8.0節 440-445行）

出典: 公式 `features/multi-instance/` ページ（Page updated 2026-10-20）、CHANGELOG.md v0.8.0節 429-445行（`99e6253`）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### v0.7.0での変更（Remote crews・Fargate）

- **接続方式に AWS Fargate が加わりました**（SSH・AWS SSM に続く3つ目）。Crew を ECS タスクとして動かし、AWS SSM のフォワード経由でタスクの turn API に接続します。**インバウンドのネットワークルールは不要**で、公開リスナーも埋め込みのリモートダッシュボードもありません。接続するラップトップには AWS CLI と Session Manager plugin が必要です。設定は `cloud.json` の任意の **`fargate` ブロック**（クラスタ・サブネット・セキュリティグループ・**digestでピン留めしたイメージのみ**・secretのARN等）に書きます
  - タスクの寿命は**既定6時間**で、`fargate.task_ttl_seconds`（正の整数）で変更できます。上限は設けられていません（`cloud.md` 212-259行）
  - 同時に走るFargateタスクは**最大10**です
  > ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（最大タスク数を設定できるか）
  > - CHANGELOG.md v0.7.0節 1101-1102行（`99e6253`。v0.7.2 のタグでは 388-390行）: 「ten running at most, set by `fargate.task_ttl_seconds` and `fargate.max_running_tasks` in `cloud.json`」
  > - 公式 `features/multi-instance/` ページ51行: 「this safety ceiling is fixed rather than a `cloud.json` setting」、`docs/system-specs/modules/cloud.md` 252-257行: 「`DEFAULT_MAX_RUNNING_TASKS` stays fixed … Raising the cap is a code change」
  >
  > v0.8.0・v0.9.0 の CHANGELOG 本文に、この記述への訂正はありません。
  >
  > ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（ダッシュボードからの設定）
  > - 公式 `features/multi-instance/` ページ96-102行は、Settings → Remote Crew の Add で選べる方式として Fargate（「The registered ECS task target created by the Cloud launch flow」）を挙げ、49行は「Configure the Fargate placement … in the optional `fargate` block of `cloud.json`; the Cloud surface shows the connection and task state」と記述しています
  > - `docs/system-specs/modules/cloud.md` 198-200行は「there is no wizard step and no dashboard renderer, so an operator writes it by hand」、`docs/guides/remote-crew-on-fargate.md` は「The lane is **not** in the Set-up picker」と記述しています（launch した task は Instances に自動追加され、自動追加が失敗したときだけ Settings → Remote Crew で手動追加します）

#### Fargate の `internal_only`（v0.8.0・セキュリティ上の注意）

> **⚠️ セキュリティに直結する設定です。既定は `false`（安全側）で、製品は書き込まず、運用者が `cloud.json` を手で編集します。**

- `cloud.json` の `fargate` ブロックは任意の **`internal_only`**（JSON 真偽値、既定 `false`）を持ちます。Fargate のタスクは user namespace サンドボックスを提供できないため、`internal_only` が無いと crew コンテナは起動を拒否します
- `true` にすると「このレーンは自分自身の crew だけを動かし、その crew が読むものの危険を自分が負う」と宣言したことになり、コンテナはモデルの subprocess を**サンドボックス無し**で起動し、起動時に警告します
- 受け入れる露出は、外部の人が入力したプロンプトに限りません。ツール出力・取得した Web ページ・コネクタのペイロード・リポジトリやチケットの本文など、注入を含みうるすべての内容がサンドボックス無しのワーカーに届き、ワーカーは crew の vault にあるモデル資格情報を読めます（`cloud.md` 345-380行、`remote-crew-on-fargate.md` の「Security note」節）
- **マルチテナントや外部から到達できる crew には設定しません**（`remote-crew-on-fargate.md` が明記）
- `cloud.json` は、エージェントのファイル編集ツールからの書き込みを拒否される保護対象です（`cloud.md` 410-414行）
- ブロック内の真偽値フィールドが真偽値でない（例 `"false"` の文字列）と、**ブロック全体が無効**（Fargate の設定が無いのと同じ）になります。ブロックは呼び出しごとに読まれるため、編集は次の要求から有効で、ブロックを消すとレーンも消えます（`remote-crew-on-fargate.md`）

#### Fargate のタスク寿命とデータホーム

- `task_ttl_seconds` の期限は**2か所で強制**されます。`provision` が起動前にクラスタを掃き出すことに加え、起動したタスク自身が `SMC_TASK_TTL_SECONDS` を受け取り、期限を過ぎるとスーパーバイザが essential コンテナを停止します（正常終了のため、クラッシュループとしてコンソールに現れません）。タスク内の期限は、それを含むイメージでのみ有効です（イメージは digest で固定されているため、古い digest で起動したタスクは掃き出しのみで制限されます）（`cloud.md` 212-243行）
- Fargate タスクのデータホームはタスク自身のディスク上にあり、**タスクが止まるとセッションと transcript は失われます**。永続ストアは設定できません（`remote-crew-on-fargate.md`）
- Fargate レーンの `POST /api/cloud/launch` は、descriptor の `confirm_before_launch` と同じ値の `confirm_recipient` を要求し、欠落または不一致は `400 recipient_not_confirmed` です。launch したタスクは接続方式 `fargate` で Instances に自動追加されます

**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）、CHANGELOG.md v0.7.0節 1101-1102行・v0.8.0節 440-445行（`99e6253`）
**出典**（Fargate の設定・セキュリティモデル）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/remote-crew-on-fargate.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## System & storage（リソース監視とディスク回収）

**v0.6.0 で公式ドキュメントに新設されたページの内容です（v0.7.2 で改訂、v0.8.0・v0.9.0 でも Crew log と Usage の節が変わっています。Page updated 2026-10-20）。** ダッシュボードの **System** 領域は、Crew がマシンに何をしているか・ホストがどれだけの作業を受け入れられるか・セッションがディスクをどれだけ消費しているかを示します。

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

**Windows では、Job object が強制する `resource_limits` のキーは `max_processes` と `max_memory_mb` の2つだけです。** 集約上限の `max_total_memory_mb`・`max_total_processes` を含む残りのキー（`cpu_weight`・`max_cpu_percent`・`max_cpu_seconds`・`max_open_files`）は受理されますが Windows では働かず、設定しているものごとに Gateway が警告を1回ログします（`docs/guides/windows-install.md` 552-556行、`99e6253`。参照: 2026-10-25 / 版 v0.9.0。[02_windows.md](02_windows.md)参照）。

### Crew log（既定オン）（v0.8.0〜）

**v0.8.0 から既定でオンです。** Crew はチャットごとに秘匿化したイベント記録を既定で残します。Crew log パネルはそれを **Status**・**Usage**・**Timeline**・**Tools**・**Approvals** にまとめて表示し、許可されたエージェントは Crew log のツールで、自分の作業単位や自分が起動したセッションを読めます。

- セッションのwork ledgerも同じログを使い、コンテキスト圧縮をまたいで目標・フェーズ・次の手順・却下したアプローチ・artifactへのポインタを保持します。Conductor work board と Issue Radar の crew ledger も同じ記録を使います
- **無効にするには、Gateway の起動前に環境変数 `KIROCREW_CREW_LOG=0` を設定します**（プロセス全体で記録が止まります）。未設定、空、または `1`・`true`・`yes`・`on` では有効のままです。`0`・`false`・`no`・`off` で無効になり、認識できない値も無効として扱われ、1回ログに出ます（`crew-log-emitter.md` 32-36行）
- フラグがオフのあいだ、ledger の書き込みは**拒否**され、監査されない別の保存先には逃がされません
- 会話を削除またはtrashへ移すと、その Crew log も一緒に消えます。Storage 画面は両方を合算します
- **v0.7.2 までは既定オフで、`KIROCREW_CREW_LOG=1` の設定と再起動が必要でした**（v0.7.0・v0.7.2 の記述）

v0.7.2 の公式 `system/` ページは「保存形式はまだ pre-release」と記述していました。この文は v0.9.0 の公式 `system/` ページと `crew-log-core.md` には見つからないため、本サイトは現状を書きません（未確認）。読み取り専用の **`kirocrew-crew-log` MCP サーバ**は、v0.9.0 のリポジトリの `docs/architecture/mcp.md` 1544行・`crew-log-projection.md` 518行に記載があります（v0.9.0 の公式 `system/` ページはこの名称を挙げず、「Crew log tools」と記述）。

出典: 公式 `system/` ページ（Page updated 2026-10-20）27-33行、CHANGELOG.md v0.8.0節 330-336行（`99e6253`）、`docs/system-specs/modules/crew-log-emitter.md` 32-36行、`docs/system-specs/modules/crew-log-core.md` 160行、公式 `configuration/` ページ159行（`KIROCREW_CREW_LOG`「enabled when unset」）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
終了済みのledgerを掃除するCLI（`kirocrew ledger-sweep`）は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) を参照してください。

### Usage: クレジットと推定トークン（v0.9.0）

- Settings → Overview の **Usage** カードから開く Usage タブに、**Estimated Tokens** カード（今月・先月の入力／出力／合計トークンとモデル要求数）と、Daily History の **Est. tokens** 列があります。Kiro CLI はクレジットを報告しますがトークン数を保存しないため、読めるセッションから推定します。入力は各要求で送った全コンテキスト（キャッシュの有無を問わない）、出力は返信の長さを4で割った値が目安で、tool 呼び出しと推論は含みません。このコンピュータに保存されたセッションだけが対象で、読めなかったセッションがあるとカードがそう表示して数値から除きます
- 上部バーのクレジット表示から開く **Kiro Account** モーダルは、条件が揃うと、クレジットがリセットまで持つか、今サイクルのペースだと尽きる日を1行で示します。ペースは同じアカウントの他クライアントを含む今サイクルの総消費から出し、この Gateway の Daily History が14日以上あると曜日の傾向も使います。使用状況が読み込み中・リセット日が不明・プランを使い切った・ボーナスクレジットを消費中・サイクルの1日目が終わる前、のいずれかでは表示されません
- サブエージェントの実行は経過時間の隣にクレジットを表示します（例 `2.40 credits · 1m 5s`）。プロバイダがクレジットを報告しないときは経過時間のみです。cron 実行の結果行は、チャットのターンと同じ usage footer（経過時間・クレジット・モデル）を持ちます

出典: 公式 `system/` ページ（Page updated 2026-10-20）35-52行、CHANGELOG.md v0.9.0節 108-119行（`99e6253`）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### Storage: コストを見て容量を回収する

**Storage** 画面は、セッションがディスク上で消費している量（トランスクリプト・添付ファイル・セッション単位の状態）を報告します。

- セッション別のディスク使用量の内訳を見る
- セッションを**削除するのではなくtrashへ移して**アクティブな保存領域から回収する
- 必要なら復元し、完全に容量を空けるにはtrashを空にする

**アイドルなセッションは、実行中の作業として数えられずアイドルとして表示されます。**

**出典**: <https://kiro.dev/docs/crew/system/>（Page updated 表記あり）

## スナップショットと復元

スナップショットには以下の**7項目**が含まれます（公式 `features/snapshot/` 23-33行。Page updated 2026-09-11）。

| コンポーネント | 内容 |
|---|---|
| **Memory** | `memory.db`・`memory_index.db`・preferences・projects・history・knowledge library（`workspace/memory/` と `workspace/knowledge/`） |
| **Workspace** | `workspace/` と `plan_memory/` の全体（選択時はメモリのサブツリーを含む） |
| **Crons** | すべてのスケジュールジョブ |
| **Config** | 設定・session map・hooks・project/workspaceパス |
| **Skills** | カスタムスキル定義 |
| **Notifications** | ダッシュボードの通知履歴 |
| **Security** | **`telemetry_salt` のみ**。監査署名鍵 `sel_hmac.key` は**含まれず**、復元時に再生成されるため、監査ログの HMAC は書いたホストに結び付いたまま保たれます |

```bash
kirocrew snapshot                     # 既定は ~/.kiro/crew/snapshots
kirocrew snapshot --list              # 既存のスナップショットを一覧
kirocrew snapshot --keep 7            # 直近7件を保持
kirocrew restore snapshot.tar.gz      # replace/mergeを自動判定
```

- **ローカルのスナップショットは自動では作られません。** 定期的に取りたい場合は `kirocrew snapshot --keep 7` を自分でスケジュールし、`kirocrew snapshot --list` で作成を確かめます。AWS Control は、設定後に独自の夜間オフホストバックアップを実行します（公式 同ページ62-64行）
- `kirocrew snapshot --strict`: 書き出した bundle が要求したエントリを省いたとき exit 3 になります（既定は、不完全でも bundle を書いたなら 0）。bundle は残り、prune は保留されます。exit 1 は「使える bundle が作れなかった」の意味のままです（`modules/cli.md` 251・312-318行）
- 復元は Gateway の停止中に行います（`kirocrew restore` は Gateway が待ち受け中だと実行を拒否し、`--force` はそのポートの待ち受けが別のインスタンスだと分かっているときにだけ使う）。descriptor に固定したトラバーサルができないプラットフォームでは、snapshot と restore は既定で拒否され、`--allow-unpinned-staging` で弱いパスベースのトラバーサルにオプトインできます（公式 同ページ37・49行）

**⚠️ 重要な警告**: **スナップショットには `telemetry_salt` など機密を含む設定が入ります**。認証情報と同様に扱い、アクセス権限を制限したストレージに保存し、安全でないチャネルで共有しないでください（公式 同ページ66行）。

> **以前の本サイトの記述の訂正（v0.7.2 以前からの誤り）**: 本節は以前、(1) 構成要素を**6項目**、(2) 「既定で08:00 UTCに実行される`kirocrew-daily-snapshot`という組み込みcronジョブが、直近7件のスナップショットを保持」、(3) 「スナップショットには機密データ（監査ログ整合性に使うセキュリティキー）が含まれる」と書いていました。いずれも**誤りでした**。(1) 構成要素は7項目で、追加は Security（`telemetry_salt` のみ）です。(2) `kirocrew-daily-snapshot` は v0.4.1 以前の公式ページには記載がありましたが、**v0.6.0 以降の公式ページ、v0.9.0 の仕様書、CHANGELOG のいずれにも記載がありません**。(3) 監査署名鍵 `sel_hmac.key` は含まれません。公式 `snapshot/` ページは v0.6.0 の時点で既にこの内容で（v0.7.2・v0.9.0 の `.md` は同一）、本サイトが追随していませんでした。

**出典**: <https://kiro.dev/docs/crew/features/snapshot/>（Page updated 2026-09-11）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## 未確認事項

- マルチインスタンスの詳細な運用手順（公式ページの参照のみで、本サイトでは概要にとどめる）
- Fargateの最大同時タスク数（10）を `cloud.json` で変更できるか（**継続**。CHANGELOG v0.7.0節と、公式ページ・`cloud.md` で記述が異なる）
- Fargate接続方式をダッシュボードから追加できるか（**継続**。公式ページ・CHANGELOG と `cloud.md`・`remote-crew-on-fargate.md` で記述が異なる）
- 常時稼働ホストのRAMの下限（公式 `running-24-7/` ページは「~10 GB minimum」、リポジトリの `remote-and-mobile.md` は「no single published floor」。**v0.9.0 の再検証で見つかった食い違い**。v0.7.2 の `remote-and-mobile.md` も同じ記述）
- `scripts/sync-to-remote.sh` の仕様と、公式ページが求めるWALファイルの同期との関係（上記「リモートホスト」節の注記。裁定しない）
- Crew log の保存形式が pre-release のままかどうか（v0.7.2 の公式ページの記述。v0.9.0 の公式 `system/` ページには見つからない）

> 以前ここに記載していた「Remote crews の現行UI表示名」は、v0.9.0 で公式ドキュメントと `instances.md` がともに「Remote Crew」に統一されたため**解消**として外しました（上記「Remote crews」節参照）。「`instances.enabled` が live か要再起動か」の同一ページ内の記述差も、v0.9.0 の公式ページが起動時に読まれる旨に揃ったため解消しています。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/running-24-7/>、<https://kiro.dev/docs/crew/features/multi-instance/>、<https://kiro.dev/docs/crew/features/snapshot/>
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

# インターフェース

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/interfaces/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{messaging,persistent-agent-channels}.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（v0.7.0での変更・チャネル数の再測定・WhatsApp グループ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/README.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/interfaces/>（Page updated 2026-09-30）
**出典**（v0.8.0・v0.9.0での変更・チャネル数の再測定・Slack との結び付け・Telegram の forum topic）: <https://kiro.dev/docs/crew/interfaces/slack/>・<https://kiro.dev/docs/crew/interfaces/telegram/>・<https://kiro.dev/docs/crew/interfaces/teams/>（いずれも Page updated 2026-10-20）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/README.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [1つのGateway・複数のサーフェス](#1つのgateway複数のサーフェス)
- [メッセージングチャネル](#メッセージングチャネル)
- [チャネルの振る舞い](#チャネルの振る舞い)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [v0.6.0での変更](#v060での変更)
- [v0.5.0での変更](#v050での変更)
- [v0.4.0での変更](#v040での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## 1つのGateway・複数のサーフェス

Kiro Crewは1つのGateway（単一のasyncioプロセス）が複数のサーフェスに多重化されます。

| サーフェス | 用途 |
|-----------|------|
| **デスクトップアプリ** | Gatewayをバンドルした最もシンプルなローカル体験。ローカル・リモートGatewayへのマルチタブ接続に対応 |
| **Webダッシュボード** | 並行する会話・ファイル・承認・活動・メモリ・スケジュール・App・設定・システム状態を `localhost:5476` で提供 |
| **CLI** | `kirocrew chat` |
| **メッセージングチャネル** | Slack・Telegram・Discord・Teams・Webex・WeCom・WeChat・WhatsApp・iMessage・Feishu（公式 Interfaces ページの一覧。チャネル数は一次情報間で一致しません。「[v0.9.0での変更](#v090での変更)」参照） |

## メッセージングチャネル

| チャネル | 用途 |
|---------|------|
| **Slack** | DMとスレッドで作業。ストリーミング応答・承認・通知・ダッシュボードへのセッションリンク |
| **Telegram** | 電話やPCのプライベートDMからエージェントにアクセス。ストリーミング応答・インライン承認・コマンド。プライベートチャットの forum topic は topic ごとの別セッションで、スーパーグループの forum topic は `telegram.allow_forum` と `telegram.allowed_forum_chat_ids` で許可したときだけ扱われる（公式 Telegram ページ。公式 Interfaces ページの一覧は「プライベートDM」とだけ記載。詳細は「[v0.9.0での変更](#v090での変更)」） |
| **Discord** | DMで作業。ストリーミング応答と承認がメッセージボタンで届く |
| **Teams** | Microsoft Teamsのチャットからアクセス。応答は完全なメッセージとして届き、承認は入力で回答 |
| Webex | Webexのダイレクトメッセージで作業（公式一覧の記述。詳細は公式の設定ガイド参照） |
| WeCom | 外向き接続のWeCom AI bot（公式一覧の記述。詳細は公式の設定ガイド参照） |
| WeChat | WeChat（Weixin）からエージェントにアクセス（公式一覧の記述。詳細は公式の設定ガイド参照） |
| WhatsApp | v0.4.0で追加。QRコードで個人アカウントをリンク。DMと設定したグループで使える（グループの扱いは「[v0.7.0での変更](#v070での変更)」参照） |
| iMessage | v0.4.0で追加。macOSのMessages.appをローカルbridgeで利用。macOS限定、既定は拒否で明示的なハンドルの許可リストを使う |
| Feishu | v0.4.0で追加。Feishu（Lark / 飞书）のネイティブチャネル。許可されたユーザーの許可リストを使う |

公式 Interfaces ページの「When to use what」表のうち、個別の設定ガイドページ（`interfaces/` 配下）があるのは Slack・Telegram・Discord・Teams・Webex・WeCom・WeChat の**7チャネル**です。WhatsApp・iMessage・Feishu は同ページの表にのみ記載されています（<https://kiro.dev/docs/crew/interfaces/>、Page updated 2026-09-30）。

## チャネルの振る舞い

- **DM**: 常時応答（`always`）
- **グループチャネル**: メンション（`mention`）が既定。観察モード（`observe`）もある
- **スレッド単位のセッション**: チャネルのスレッドが論理セッションにマッピングされる（[02_sessions.md](02_sessions.md)参照）
- **ダッシュボードセッションと Slack の結び付け**: ダッシュボードの **💬** ボタン（`POST /api/chat/slots/{name}/slack-link`）が、セッションを Slack のスレッドに結び付けます。Slack で始まったセッション（DM／@mention のスレッド）は、`set_slack_link(session_key, reply_ts, channel)` で自分のスレッドを記録します（`session-slack-linking.md` 96-101行、`99e6253`）。`slack.auto_link_sessions`（既定 off）での自動リンクは「[v0.9.0での変更](#v090での変更)」を参照
  - **記述の訂正**: 本サイトは以前、`set_slack_link` を「ダッシュボードセッションの Slack 引き渡し」と記載していました。`set_slack_link` を呼ぶのは Slack で始まったセッションの self-link と `/kirocrew sessions` の再開で、ダッシュボードのセッションを Slack に結び付けるのは上記の 💬 ボタンのエンドポイントです。この記述は v0.4.1 時点から変わっていませんでした。`session.md` は `set_slack_link` を「Slack handler」の呼び出しと記述しています（v0.9.0 は 2763行・2771行、v0.7.2 は 1881行・1889行）
- **永続エージェントチャネル（Channels App）**: オーケストレーターが専門エージェントをチャネルのメッセージ・スレッド・@mention で調整する、永続的なマルチエージェントのワークスペースです。メッセージングチャネル（Slack 等）の設定とは別の機能で、UI は非表示の opt-in 組み込み App `channels`（`defaultEnabled: false`）です。`kirocrew app enable channels` で有効にします（`persistent-agent-channels.md` 3-7行、`99e6253`）
  - **記述の訂正**: 本サイトは以前、これを「チャネルとエージェントの長期的な紐付け」と記載していました。v0.7.2 の同仕様書の Overview（3-5行、`c67c506`）も同じ内容で、この誤りは v0.7.2 以前からのものです

## v0.9.0での変更

### チャネル数（v0.9.0 での再測定・一次情報間で一致しない）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | v0.9.0 時点の記述 |
> |------|------------------|
> | 公式ドキュメント（`interfaces/` 配下の設定ガイドページ） | **7ページ**（Slack・Telegram・Discord・Teams・Webex・WeCom・WeChat。v0.6.0 から変化なし） |
> | 公式 Interfaces ページの一覧（Page updated 2026-09-30） | メッセージングチャネルとして**10件**（上記7件＋WhatsApp・iMessage・Feishu） |
> | 公式 Quick start（`index`、Page updated 2026-10-20） | 「additional channels such as」として上記7件を例示（総数の記載なし） |
> | README.md 334行 | **10件**（Slack, Discord, Telegram, Teams, Webex, WeCom, WeChat (Weixin), WhatsApp, Feishu (Lark), iMessage）。チャネル一覧は334行の1か所です（v0.7.2 は 297行・631行の2か所） |
> | `modules/messaging.md` | 153行「all ten transports」、957行「All **ten channels**」、3352行「all ten channel panels」、5841行「a ten-channel repo」と、**10**で一貫しています |
>
> v0.7.2 の `messaging.md` 690行にあった「eleven channels」の記述は、v0.9.0 の `messaging.md` に出現しません（v0.8.0 の `messaging.md` 893行は「eleven channels」のままで、変更は v0.8.0 と v0.9.0 の間に入っています）。総数は出典ごとに異なるため、本サイトは公式の設定ガイドページ数（7）とそれぞれの列挙を併記します。

出典: README.md・`modules/messaging.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）、<https://kiro.dev/docs/crew/interfaces/>（Page updated 2026-09-30）、<https://kiro.dev/docs/crew/>（Quick start、Page updated 2026-10-20）。

### Slack

- **Connect new sessions to Slack automatically**（**Settings → Messaging Channels → Slack**、`slack.auto_link_sessions`、**既定 off**）: Slack が接続されているとき、ダッシュボードで始めた永続セッションは、最初の（スラッシュコマンドではない）メッセージのあとに bot との DM にスレッドが作られ、そのターンがミラーされます
  - **自動リンクの対象外**: 最初の入力がスラッシュコマンドのセッション、Slack や他のチャネルで始まったセッション、リモート crew のセッション、incognito／temporary のセッション、エージェント・スケジュールジョブ・App が作ったセッション、既にスレッドのあるセッション、設定を on にする前に存在したセッション
  - 失敗した試みは再試行されません（**💬** ボタンで結び付けます）。スレッドの作成中は最初の送信を最大 **5 秒**保留し、それより遅れると、作成後に始まるターンだけがスレッドに反映されて最初のターンはコピーされません。この方法でリンクしたセッションはサイドバーの位置が変わりません
- 設定画面の名称: 公式 Slack ページ・Discord ページ・Configuration ページは **Settings → Messaging Channels** と記載しています（v0.7.0 で Channels から改名）。一方、v0.9.0 の CHANGELOG 98行（`99e6253`）はこの機能の場所を旧名称の「Settings → Channels → Slack」と記載しています

出典: CHANGELOG.md v0.9.0節 98-100行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/interfaces/slack/>（Page updated 2026-10-20）
**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/slack-gateway.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/design-notes/session-slack-linking.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。`AUTO_LINK_HOLD_SECS` 5 秒は `session-slack-linking.md` 99行）

### Telegram

- **forum topic**: プライベートチャットの forum topic は topic ごとの別セッションです。topic の外のメッセージは元の DM セッションのままです。許可されたユーザー（`allowed_user_ids`）のプライベートチャットには常に応答します（空リストは誰も許可しない）
- **スーパーグループの forum topic**は、`telegram.allow_forum`（**既定 `false`**）が `true` で、そのチャット ID が `telegram.allowed_forum_chat_ids`（既定 `[]`＝すべてのグループを拒否）にあるときだけ扱われ、topic ごとの別セッションです。General topic（thread なし）は拒否されます
- **`telegram.forum_activation`**（既定 `"always"`。`mention`・`off`）: 許可された topic の中で bot がいつ答えるかを決めます。1:1 の DM には適用されません
- **`TELEGRAM_API_BASE_URL`**: `api.telegram.org` が遮断された環境で、Bot API をリバースプロキシ経由にします。`~/.kiro/crew/.env` に設定して Gateway を再起動します。値は `{token}` と `{method}` を含む完全なメソッドのテンプレートです。公式ページの例は `TELEGRAM_API_BASE_URL=https://tg-proxy.example.com/bot{token}/{method}` です。bot トークンが URL に載るため、値は `https` のみです（loopback のホスト `127.0.0.1`・`::1`・`localhost` は `http` も可）。不正な値は Gateway のログに警告を出して無視され、公開ホストが使われます
- **ターン中のメッセージ**: `/sessions` で再開したダッシュボードのセッションにターン中のメッセージが届くと、実行中のターンに折り込む（steer）かキューされ、会話が **Steering that session** または **Queued for that session** と返します。`/steer`・`/queue` で明示できます

> 公式 Interfaces ページ（Page updated 2026-09-30）の Telegram の記述は「プライベートDM」とだけ書き、forum topic に触れていません。新しい日付（2026-10-20）の公式 Telegram ページには上記の forum topic の記述があります。仕様書 `messaging.md` の forum 対応（1664-1735行、`99e6253`）は v0.7.2 の同ファイルにも存在し、本サイトの記載漏れは v0.7.2 以前からのものです。`TELEGRAM_API_BASE_URL` は仕様書（`docs/system-specs/`・`docs/architecture/`）に記述が見つからず、公式 Telegram ページと CHANGELOG のみが記載しています。

出典: CHANGELOG.md v0.9.0節 101-106行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/interfaces/telegram/>（Page updated 2026-10-20）
**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### Teams とターン中のメッセージ

- Teams の **`/sessions`** は、Teams の会話をダッシュボードのセッションに結び付けます。**owner 専用**で、`teams.allowed_emails` にちょうど1つの identity があるときだけ動作します（共有の許可リストでは、ダッシュボードのトランスクリプトを守るため一覧が拒否されます）
- 結び付けたセッションがターン中にテキストのメッセージが届くと、実行中のターンに折り込む（steer）かキューされ、会話がどちらになったかを返します。**添付付きのメッセージは steer も queue もされず**、ターン終了後の再送を求める返信になります。ダッシュボードのターンが進行中でなければ、新しいターンとして実行されます
- **`messaging.queue_mode`**（`config.json`、**既定 `steer`**、`queue` も可）は Teams 専用ではない共通の設定で、ターン中に届いたメッセージを実行中の返信に折り込む（`steer`）か、ターン終了後に実行する（`queue`）かを決めます。`/steer <message>`・`/queue <message>` の接頭辞で、そのメッセージだけ上書きできます
- Teams の応答は、typing indicator のあとに最終返信が1つのメッセージで届きます

出典: CHANGELOG.md v0.9.0節 104-106行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/interfaces/teams/>（Page updated 2026-10-20）

### 再起動が必要なチャネル設定（食い違い）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **CHANGELOG v0.7.0**（752-757行）: 再起動が必要と印が付くのは Settings の Slack スラッシュコマンドの欄だけ
> - **公式 Configuration ページ**（Page updated 2026-10-20）: Slack のスラッシュコマンドや `mcp.honour_auto_approve` などの欄に **Changes need a restart** のバッジが付き、資格情報の変更は影響を受ける連携が再接続する前に再起動が必要（v0.7.2 時点の同ページは、Slack スラッシュコマンドの欄が現在の boot-only の設定と記載）
> - **`modules/messaging.md`**（`99e6253`）: 例外は `slack.command`・`whatsapp.db_path`・`config_dir/.env` の資格情報の3つで「they are the whole list」（1066-1076行）。同じ節で `dm_scope` も `restart=True` と記述（1023-1024行）。v0.7.2 の同ファイル757行にも同じ記述があり、この食い違いは v0.7.2 以前からのものです

## v0.8.0での変更

### チャネル全般（Notable fixes・CHANGELOG の記載）

- Telegram・Slack・Teams・Discord で、承認カードが出た直後に押した Approve も有効になります
- Discord で、チャネル・スレッド・DM で動くサブエージェントの Approve／Deny ボタンがその場に投稿されます
- 異なる人からのキュー済み DM は、送信者ごとの別ターンとして応答されます。2人が同時に書き込んだとき、2人目の Queued の通知が1人目の回答で上書きされなくなりました
- 他のチャネルでも、redact が起きたとき Slack と同じセキュリティ通知を投稿します。2つのメッセージにまたがる認証情報も通りません
- 返信の末尾でエージェントが提示する選択肢が、散文が続いても Slack・Webex・Telegram・WhatsApp に届きます
- Discord の DM や Slack のスレッドで動くセッションを、一時停止だけでなくセッションメニューから**リンク解除**できます
- 自分の Discord／Telegram の DM では conductor を動かせます（ワーカーを dispatch して作業 ledger を使えます。以前はチャネルのセッションでは拒否されていました）
- MCP App のクリック・フォーム送信は、会話に「Sent by the app」として入り、本人の発言としては扱われません
- 自分自身に応答する会話は、1時間に90ターンで一時停止されます（設定キー・対象チャネルは仕様書で確認できず、未確認）

出典: CHANGELOG.md v0.8.0節 313-315行・377-382行・596-615行（`99e6253`）。

### WeCom のファイル送受信

- 送信: PNG・JPEG はピクチャ、MP4・WebM は動画、その他はダウンロードとして届きます（以前は dashboard へのリンクだけが届きました）。上限は**ピクチャと音声ノートが 2 MB、ファイルと動画が 20 MB**で、大きすぎるピクチャはファイルとして届きます。インラインで言及しただけの画像はアップロードされないため、画像そのものを届けるには `file_send` を使います
- 受信: **画像 10 MB・ファイル 20 MB・1メッセージ 10 件**。音声ノートは WeCom が提供する文字起こしを使い、添付の音声ファイルはローカルで文字起こしします

出典: CHANGELOG.md v0.8.0節 395-398行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/interfaces/wecom/>（Page updated 2026-10-12）

### Slack のチャネル履歴

- **observe モード**（@mention されるまで黙っているモード）のチャネル履歴は、**200 件・1週間**（`slack.observe_max_messages`・`slack.observe_ttl_hours`）で、`<data-home>/history` の JSONL に**ディスクへ永続化**され、再起動後も残ります。許可された送信者のメッセージだけが記録されます
- observe 以外のモード（仕様書の Normal mode）は **50 件・5分**で、メモリ上にのみ保持されます

> 本内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/channel-history.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。44-49行・89-91行）
**出典**: <https://kiro.dev/docs/crew/interfaces/slack/>（Page updated 2026-10-20）

### 永続エージェントチャネル（Channels App）の上限

`agent.max_channels` の既定は **1**（クランプ 1〜5）、`agent.max_channel_agents` の既定は **3**（クランプ 1〜10）です。どちらも実行中に反映され、新しいチャネル／メンバーにだけ効きます（上限を下げても既存のものは外れません）。チャネルは直近 **200** メッセージを保持し、`GET /api/channels/{id}` は直近 **50** を返します。UI は非表示の opt-in App（既定は無効）です。

> 本内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/persistent-agent-channels.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。44-48行）

## v0.7.0での変更

### チャネル数（v0.7.2 での再測定・一次情報間で一致しない）

> 本節は v0.7.2 時点の記述です。v0.9.0 の再測定は「[v0.9.0での変更](#v090での変更)」を参照してください。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | v0.7.2 時点の記述 |
> |------|------------------|
> | 公式ドキュメント（`interfaces/` 配下の設定ガイドページ） | **7ページ**（Slack・Telegram・Discord・Teams・Webex・WeCom・WeChat。sitemap 上も同じ7件で、v0.6.0 から変化なし） |
> | 公式 Interfaces ページの一覧 | メッセージングチャネルとして**10件**を列挙（上記7件＋WhatsApp・iMessage・Feishu） |
> | README.md 297行・631行 | **10件**を列挙（Slack, Discord, Telegram, Teams, Webex, WeCom, WeChat, WhatsApp, Feishu, iMessage）。v0.6.0 の README.md 287行は7件でした |
> | `modules/messaging.md` | 690行「One shape covers all **eleven channels**」。同じファイルの中でも 660行は「nine of ten channels」、2046行は「all ten channel panels」と記述しています |
>
> 11件目に当たるチャネルは `messaging.md` の本文から特定できません。本サイトは総数を断定せず、公式の設定ガイドページ数（7）とそれぞれの列挙を併記します。

出典: README.md・`modules/messaging.md`（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）、<https://kiro.dev/docs/crew/interfaces/>（Page updated 2026-09-30）。

### チャネルの機能追加

- **あらゆる種類の添付ファイルがエージェントに届く**: Slack・Discord・Telegram・Teams・Webex・WeChat・WeCom から送られた動画・書庫・SVG・その他の未認識の添付を、元の名前・種類・サイズ付きのローカルファイルとしてエージェントに渡します（CHANGELOG 161-164行）
  - ファイルごとの共通の既定上限は、画像 10 MB・テキスト 512 KB・文書 20 MB・音声 25 MB・不透明なファイル（書庫・動画など）50 MB です。チャネルや形式ごとに、より低いプラットフォームの上限が加わることがあります。1メッセージで処理する添付は最大10件で、拒否したファイルは送信者に通知されます（公式 Interfaces ページ「Attachments across channels」）
- **Gateway の再起動中に届いたメッセージへの返信**: 処理できなかったメッセージには、次回の起動時に同じ会話で、元のテキストを引用して再送を求める返信をします。メッセージをターンとして自動で再実行することはありません。Incognito／Temporary の会話と WhatsApp のグループメッセージには、この通知は残りません（CHANGELOG 165-169行／公式 Interfaces ページ「Messages received during a restart」）
- **Slack で送信済みメッセージを編集できる**: 新しい `update_message` ツールが、bot 自身が送ったメッセージを削除・再投稿せずにその場で書き換えます。対象は追跡中のチャネルか所有者自身の DM です。**Slack 限定**（`chat.update`）で、`text` か `blocks` のどちらかが必要です。送った内容でメッセージが置き換わるため、`blocks` だけを送ると元のテキストは消えます（CHANGELOG 170-172行／`messaging.md` 1100-1110行、`c67c506`）。ツールの一覧は [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md) を参照してください
- **チャネル設定が稼働中の Gateway に反映される**: `config.json` の保存や Settings での変更は、再起動を待たずに反映されます。再起動が必要な項目として印が付くのは、Settings の Slack スラッシュコマンドの欄だけです（CHANGELOG 40-45行）。`messaging.md` 686-692行も、稼働中に反映できるチャネル設定はダッシュボード・`kirocrew config set`・`config.json` の直接編集のどれから書いても反映されると記述しています

### WhatsApp のグループ

公式 Interfaces ページ（Page updated 2026-09-30）は、WhatsApp を「direct chats and configured groups」で使えると記載し、次の条件を挙げています。

- グループで受け付けるのは、リンクしたアカウントと **Allowed WhatsApp IDs**（`allowed_wa_ids`）に載っている番号だけです。`messaging.md` 4204-4213行は、リストが空のときは operator 以外を誰も受け付けず、許可されていないメンバーのメッセージは黙って破棄され SEL に記録されると記述しています
- Kiro バックエンドでは、受け付けた operator 以外の参加者は**ツールのない別セッション**で扱われます（`messaging.md` 65行・4380行の `TOOLLESS_TURN_AGENT`＝`kirocrew-guest`、`tools: []`、MCP サーバなし）。ほかのエージェントバックエンドでは、そのターンは拒否されます
- ツールを承認できるのは operator で、番号の入力で承認します

> 本内容は v0.7.2 タグの仕様書で確認したもので、v0.7.2 の CHANGELOG/Release 本文（「A small fix.」）は説明していません。v0.8.0 の CHANGELOG（Notable fixes）は、設定した WhatsApp グループでは、自分と許可リストの番号だけが応答を起こせること、許可されていない人は mention しても破棄されること、許可された人はツールを持たないエージェントと話すことを記載しています（`CHANGELOG.md` 611-614行、`99e6253`）。v0.9.0 の `messaging.md` でも、`TOOLLESS_TURN_AGENT`（`kirocrew-guest`、`tools: []`）は 67行・6027行、`allowed_wa_ids` の空リストが operator 以外を誰も受け付けないことは 5856行に記載があります。v0.7.0・v0.7.1 タグの `messaging.md` には `TOOLLESS_TURN_AGENT` と `_group_sender_admitted` の記述がありません（WhatsApp のグループ機能自体は v0.6.0 の `messaging.md` 3895行 `whatsapp/group_gate.py` に記載があります）。

出典: `modules/messaging.md`（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）、<https://kiro.dev/docs/crew/interfaces/>（Page updated 2026-09-30）。

### 設定画面の名称・ショートカット

- **Settings → Channels** は **Messaging Channels** に名称が変わりました。複数のエージェントが1つの部屋を共有する Channels App との混同を避けるためと CHANGELOG は説明しています（CHANGELOG 589-590行）
- Windows と Linux では、設定を開くショートカットが **Ctrl+, から Alt+,** に変わりました。中国語・日本語の入力メソッドでカンマを入力できるようにするためです。macOS は Cmd+, のままです（CHANGELOG 458-460行）

出典: CHANGELOG.md v0.7.0節 40-45行・161-172行・458-460行・589-590行（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）。

## v0.6.0での変更

- **エージェントがチャネルを名前で指定してメッセージを送れる** — `send_message` で **Slack・Discord・Telegram・WhatsApp・Webex・Teams・iMessage・Feishu** に到達します（[04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)参照）
- **MCPサーバの保存でセッションがリセットされなくなった** — Kiro CLI 2.10.0 以降。チャットのセッションメニューのMCPサーバービューは、そのセッションが実際にマウントしたものを報告します（[08_mcp-integration.md](08_mcp-integration.md)参照）
- **Telegram からセッションを検索できる** — ダイレクトメッセージで `/sessions <words>`。語を付けない場合は直近10件を一覧します

出典: CHANGELOG.md v0.6.0節 159-168行（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）。

## v0.5.0での変更

- **ワンクリックのスマートフォン接続** — 「Set up & show QR」の1操作で trust の有効化・Gateway 再起動・Tailscale 経由の公開・サインインQRコードの提示までを行います。**スマートフォンのセッションは Gateway の再起動と更新をまたいで維持**され、再スキャンが不要になりました
- **セッションを失った端末向けのサインインリンク** — サインイン済みの端末が使い捨てリンクを発行できます（何もサインインしていない場合の CLI 復旧経路は残ります）
- **コンポーザでの動画添付** — 最大512MBまで。ディスクへ直接ストリーミングされ、スマートフォンの写真ピッカーからも選べます
- **MCPサーバの無言劣化の解消**（[08_mcp-integration.md](08_mcp-integration.md)参照）

出典: CHANGELOG.md v0.5.0節（参照: 2026-09-13 / commit `e683282` / 版 v0.5.0）。

## v0.4.0での変更

v0.4.0 CHANGELOGはWhatsApp・iMessage・Feishuの3チャネル追加を記載します。チャネル数は、公式docs 7、README 8、messaging仕様 10と一次情報間で一致しないため、本ページは総数を断定しません（この3つの値は v0.4.1 時点の実測です。v0.7.2 での再測定は「[v0.7.0での変更](#v070での変更)」を参照）。Teams、Telegram、WebexのSlackとの機能パリティ、およびDiscordのコマンドメニュー等も同CHANGELOGで記載されています。

出典: CHANGELOG.md v0.4.0節（`bba3f195212992eaa07d83c082e1ec55e395c32b`）。

## v0.3.0での変更

### 破壊的変更: Multi-account Telegramの撤回

**Telegramのマルチアカウント対応が撤回されました。単一のbot tokenのみが受理されます。** 運用したいトークンを `telegram.bot_token` に移してください。**既存の設定はparseされ保持されますが、account mapは読まれません**（設定は残るが機能しない状態になります）。

出典: CHANGELOG.md v0.3.0節 16行（`21584ea`）「**Multi-account Telegram is withdrawn.** Only a single bot token is accepted; move the token you want served to `telegram.bot_token`. Existing config is still parsed and preserved, but nothing reads the account map」。設定キーは [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。

### チャネル関連の変更（5件）

| 変更 | 内容 | CHANGELOG行 |
|------|------|:---:|
| **ダッシュボードの返信がチャネルに反映される** | ダッシュボードから送った回答が、元のDiscord／Telegramの会話に中継されます | 149行 |
| **Telegramに実際のコマンドメニュー** | `/` でオートコンプリート、インラインボタンでのモデル切替、auto-approveのトグル、markdownテーブルが生のパイプ記号ではなくテーブルとして描画されます | 151行 |
| **WeChatが添付を受け付ける** | 写真・ボイスメモ・ドキュメントがエージェントに届くようになりました（従来は破棄されていました） | 154行 |
| **チャネルが自分のセッションを整理できる** | チャネルを名前付きサイドバーフォルダに向けると、その会話がそこにグループ化されます | 156行 |
| **選択肢が多すぎる場合の緩やかな縮退** | プラットフォームの上限を超えるオプションリストは、余分な選択肢を黙って失う代わりに**番号付きテキストリスト**になります | 158行 |

出典: CHANGELOG.md v0.3.0節（`21584ea`）。

## 未確認事項

- Webex／WeChat／Discord の個別の振る舞いの詳細（公式の各ページは v0.7.2 と v0.9.0 で同一。本サイトでは概要のみ記載）。WeCom のファイル送受信は「v0.8.0での変更」に記載しました
- メッセージングチャネルの総数（公式の設定ガイドページは7、公式一覧と README と `messaging.md` は10、公式 Quick start は7件の例示。「[v0.9.0での変更](#v090での変更)」を参照）。v0.7.2 時点で `messaging.md` にあった「eleven channels」は v0.9.0 で「ten」に揃いました
- 再起動が必要なチャネル設定の範囲（「[v0.9.0での変更](#v090での変更)」の食い違い）
- 自分自身に応答する会話の一時停止（1時間に90ターン）の設定キー・対象チャネル

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/interfaces/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>
- セッション基盤: [02_sessions.md](02_sessions.md)
- CLIコマンド一覧: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

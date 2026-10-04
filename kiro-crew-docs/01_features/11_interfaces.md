# インターフェース

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/interfaces/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{messaging,persistent-agent-channels}.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（v0.7.0での変更・チャネル数の再測定・WhatsApp グループ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/README.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/interfaces/>（Page updated 2026-09-30）

---

## 📑 このページの内容

- [1つのGateway・複数のサーフェス](#1つのgateway複数のサーフェス)
- [メッセージングチャネル](#メッセージングチャネル)
- [チャネルの振る舞い](#チャネルの振る舞い)
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
| **メッセージングチャネル** | Slack・Telegram・Discord・Teams・Webex・WeCom・WeChat・WhatsApp・iMessage・Feishu（公式 Interfaces ページの一覧。チャネル数は一次情報間で一致しません。「[v0.7.0での変更](#v070での変更)」参照） |

## メッセージングチャネル

| チャネル | 用途 |
|---------|------|
| **Slack** | DMとスレッドで作業。ストリーミング応答・承認・通知・ダッシュボードへのセッションリンク |
| **Telegram** | 電話やPCのプライベートDMからエージェントにアクセス。ストリーミング応答・インライン承認・コマンド |
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
- **ダッシュボードセッションのSlack引き渡し**: `set_slack_link(session_key, reply_ts, channel)` で会話へのリンクを保持
- **永続エージェントチャネル**: `persistent-agent-channels.md` に定義される、チャネルとエージェントの長期的な紐付け

## v0.7.0での変更

### チャネル数（v0.7.2 での再測定・一次情報間で一致しない）

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

> 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません。v0.7.0・v0.7.1 タグの `messaging.md` には `TOOLLESS_TURN_AGENT` と `_group_sender_admitted` の記述がありません（WhatsApp のグループ機能自体は v0.6.0 の `messaging.md` 3895行 `whatsapp/group_gate.py` に記載があります）。

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

- Webex／WeCom／WeChatの個別の振る舞いの詳細（公式インターフェースページの各ページを参照する必要があるが、本サイトでは概要のみ記載）
- メッセージングチャネルの総数（公式の設定ガイドページは7、公式一覧と README は10、`messaging.md` は「eleven channels」。11件目の内訳は特定できない。「[v0.7.0での変更](#v070での変更)」参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/interfaces/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>
- セッション基盤: [02_sessions.md](02_sessions.md)
- CLIコマンド一覧: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

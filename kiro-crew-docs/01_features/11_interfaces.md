# インターフェース

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/interfaces/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{messaging,persistent-agent-channels}.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

---

## 📑 このページの内容

- [1つのGateway・複数のサーフェス](#1つのgateway複数のサーフェス)
- [メッセージングチャネル](#メッセージングチャネル)
- [チャネルの振る舞い](#チャネルの振る舞い)
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
| **メッセージングチャネル** | Slack・Telegram・Discord・Teams・Webex・WeCom・WeChat |

## メッセージングチャネル

| チャネル | 用途 |
|---------|------|
| **Slack** | DMとスレッドで作業。ストリーミング応答・承認・通知・ダッシュボードへのセッションリンク |
| **Telegram** | 電話やPCのプライベートDMからエージェントにアクセス。ストリーミング応答・インライン承認・コマンド |
| **Discord** | DMで作業。ストリーミング応答と承認がメッセージボタンで届く |
| **Teams** | Microsoft Teamsのチャットからアクセス。応答は完全なメッセージとして届き、承認は入力で回答 |
| Webex | （公式一覧に記載。詳細ページ参照） |
| WeCom | （公式一覧に記載。詳細ページ参照） |
| WeChat | （公式一覧に記載。詳細ページ参照） |
| WhatsApp | v0.4.0で追加。QRコードで個人アカウントをリンク |
| iMessage | v0.4.0で追加。macOSのMessages.appをローカルbridgeで利用 |
| Feishu | v0.4.0で追加。Feishu（Lark / 飞书）のネイティブチャネル |

## チャネルの振る舞い

- **DM**: 常時応答（`always`）
- **グループチャネル**: メンション（`mention`）が既定。観察モード（`observe`）もある
- **スレッド単位のセッション**: チャネルのスレッドが論理セッションにマッピングされる（[02_sessions.md](02_sessions.md)参照）
- **ダッシュボードセッションのSlack引き渡し**: `set_slack_link(session_key, reply_ts, channel)` で会話へのリンクを保持
- **永続エージェントチャネル**: `persistent-agent-channels.md` に定義される、チャネルとエージェントの長期的な紐付け

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

v0.4.0 CHANGELOGはWhatsApp・iMessage・Feishuの3チャネル追加を記載します。チャネル数は、公式docs 7、README 8、messaging仕様 10と一次情報間で一致しないため、本ページは総数を断定しません。Teams、Telegram、WebexのSlackとの機能パリティ、およびDiscordのコマンドメニュー等も同CHANGELOGで記載されています。

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

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/interfaces/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>
- セッション基盤: [02_sessions.md](02_sessions.md)
- CLIコマンド一覧: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

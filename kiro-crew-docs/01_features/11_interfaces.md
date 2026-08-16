# インターフェース

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/interfaces/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{messaging,persistent-agent-channels}.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [1つのGateway・複数のサーフェス](#1つのgateway複数のサーフェス)
- [メッセージングチャネル7種](#メッセージングチャネル7種)
- [チャネルの振る舞い](#チャネルの振る舞い)
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

## メッセージングチャネル7種

| チャネル | 用途 |
|---------|------|
| **Slack** | DMとスレッドで作業。ストリーミング応答・承認・通知・ダッシュボードへのセッションリンク |
| **Telegram** | 電話やPCのプライベートDMからエージェントにアクセス。ストリーミング応答・インライン承認・コマンド |
| **Discord** | DMで作業。ストリーミング応答と承認がメッセージボタンで届く |
| **Teams** | Microsoft Teamsのチャットからアクセス。応答は完全なメッセージとして届き、承認は入力で回答 |
| Webex | （公式一覧に記載。詳細ページ参照） |
| WeCom | （公式一覧に記載。詳細ページ参照） |
| WeChat | （公式一覧に記載。詳細ページ参照） |

## チャネルの振る舞い

- **DM**: 常時応答（`always`）
- **グループチャネル**: メンション（`mention`）が既定。観察モード（`observe`）もある
- **スレッド単位のセッション**: チャネルのスレッドが論理セッションにマッピングされる（[02_sessions.md](02_sessions.md)参照）
- **ダッシュボードセッションのSlack引き渡し**: `set_slack_link(session_key, reply_ts, channel)` で会話へのリンクを保持
- **永続エージェントチャネル**: `persistent-agent-channels.md` に定義される、チャネルとエージェントの長期的な紐付け

## 未確認事項

- Webex／WeCom／WeChatの個別の振る舞いの詳細（公式インターフェースページの各ページを参照する必要があるが、本サイトでは概要のみ記載）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/interfaces/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>
- セッション基盤: [02_sessions.md](02_sessions.md)
- CLIコマンド一覧: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

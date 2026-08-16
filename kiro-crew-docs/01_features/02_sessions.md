# セッション基盤

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**（`session.pool_size`既定値の不整合・`chat_turn_timeout_secs`クランプ上限の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [セッションとは](#セッションとは)
- [session_keyの形式](#session_keyの形式)
- [Warm Pool](#warm-pool)
- [Session Resume](#session-resume)
- [Circuit Breaker](#circuit-breaker)
- [未確認事項](#未確認事項)

---

## セッションとは

各セッションは独立したACP接続で、それぞれ自分のコンテキストと文字起こしを持ちます。**`session_key`** という識別子でキーイングされ、この識別子がセッションの起源をエンコードします。

## session_keyの形式

`session_key` は名前空間付きの文字列で、起源によってプレフィックスが変わります。確認できているプレフィックス（`_STATELESS_PREFIXES` に列挙）:

| プレフィックス | 起源 |
|--------------|------|
| `slack:<ts>` | Slackスレッド（`<ts>` はSlackのthread_ts） |
| `cron:` | Cronジョブ |
| `subagent:` | サブエージェント |
| `side:` | `/side` の一時的な会話（[03_chat.md](03_chat.md)参照） |
| `secretary:` | （内部用途） |
| `heartbeat:`／background | Heartbeatタスク |
| `wf-pool:` | ワークフローのプールされたワーカー（実行ごとにクリーンなセッションを渡す） |

**ステートレスなセッション**（cron・subagent・taskrunner・channel・secretary・side・heartbeat/background・`wf-pool:`）は `SessionMap`（`session_key → kiro_session_id` の永続マッピング）の対象外です。**長寿命の対話的セッションのみ**がマッピングされます。

> Slackのスレッドセッションには歴史的に2つのキー形式（レガシーな裸の `thread_ts` と正規の名前空間付き `slack:<ts>`）が存在し、両者を折り込む仕組みがあります。

## Warm Pool

`session.pool_size`（`overview.md`は既定 `0` = オフと明記）は、新しいセッションがkiro-cliのコールドスタートを払わずに開始できるよう、プロセスを事前起動します。プールされたプロセスは `session.pool_ttl_secs`（既定1800秒）を超えると、claim時に破棄されます。

> **一次情報内の不整合**: `docs/architecture/overview.md`は「Warm pool (`session.pool_size`, default `0` = off)」と明記しますが、`docs/system-specs/modules/config.md`のPython dataclass定義は `pool_size: int = 2`（ロード時クランプ0〜10）です。本サイトは`overview.md`の記述を採用していますが、実際の既定値がWarm Pool有効（2）か無効（0）かは、この2つの一次情報だけでは確定できません。

- **アイドルタイムアウト**: `session.timeout_secs`（既定3600秒）経過後にセッションを回収
- **ターン上限**: `agent.chat_turn_timeout_secs`（既定7200秒＝2時間。ロード時クランプは300〜86400秒。無効化不可）
- **ツール承認の待機時間**: `agent.tool_approval_timeout_secs`（既定600秒＝10分）
- **サーキットブレーカー**: 1セッションで5回連続失敗するとリセットを強制
- **自動圧縮**: コンテキストウィンドウの `session.autocompact_pct`（既定90%）で発動

## Session Resume

`session_key → kiro_session_id` の永続マッピングは `~/.kiro/crew/session_map.json` に保存されます。これにより `session/load` が、セッションが再利用される際にkiro-cliの会話履歴全体を復元できます。

- `get_or_create()`: マッピングを検索し、見つかって`.json`ファイルが存在すれば、ACPクライアントに `resume_session_id` を設定してWarm Poolをスキップ
- `reset()`: マッピングを**削除しません**（kiro-cliのセッションファイルはディスクに残る。次回の `get_or_create` が `session/load` を試みる）
- `remove()`: マッピングを削除（明示的なタブ削除。再開は期待されない）

## セッションのライフサイクル（呼び出し元別）

呼び出し元によってパターンが異なり、この違いには意味があります。人が見ているサーフェスはセッションを保持し、バックグラウンドジョブは保持してはいけません。

| 呼び出し元 | パターン |
|-----------|---------|
| チャネルハンドラ（Slack等） | スレッドごとに長寿命。`finally`で`release()`。アイドル失効で回収 |
| ダッシュボードスロット | スロットごとに長寿命。`finally`で`release()`。ユーザーが明示的にクローズ |
| Cronジョブ | ジョブごとのキー `cron:{id}`。`persistent_session: false` なら実行ごとに新しい `cron:{id}:{uuid}` キー |
| Heartbeat | サイクル中の並行タスクで1つの共有 `HEARTBEAT_KEY` |
| Subagent | エージェントごとのキー `subagent:{id}` |

## Circuit Breaker

1セッションで5回連続失敗すると、リセットが強制されます。

## 未確認事項

- `session.pool_size`の真の既定値（`overview.md`は0、`config.md`は2。両併記のまま。上記「Warm Pool」参照）。`session_key` の形式は当初Zenn記事のみを出典としていたが（要検証扱い）、`modules/session.md` で `_STATELESS_PREFIXES` の実装として確認済み

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/sessions/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session.md>
- チャット: [03_chat.md](03_chat.md)
- 自律実行（Cron/Subagent）: [06_autonomy.md](06_autonomy.md)

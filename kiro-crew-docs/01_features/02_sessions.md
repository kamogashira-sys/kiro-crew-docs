# セッション基盤

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（`session.pool_size`既定値の不整合・`chat_turn_timeout_secs`クランプ上限の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（タイムアウト・自動圧縮・Warm Pool の既定値の再測定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**（v0.7.0での変更・`wf-author:`・アイドル回収の無効化）: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-09-25）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

---

## 📑 このページの内容

- [セッションとは](#セッションとは)
- [session_keyの形式](#session_keyの形式)
- [Warm Pool](#warm-pool)
- [Session Resume](#session-resume)
- [Circuit Breaker](#circuit-breaker)
- [v0.7.0での変更](#v070での変更)
- [Session summaries（v0.3.0で追加）](#session-summariesv030で追加)
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
| `wf-author:` | ワークフローのオーサリング（オーサリング試行ごとに明示的に破棄される） |
| `wf-pool:` | ワークフローのプールされたワーカー（実行ごとにクリーンなセッションを渡す） |

**ステートレスなセッション**（cron・subagent・taskrunner・channel・secretary・side・heartbeat/background・`wf-author:`・`wf-pool:`）は `SessionMap`（`session_key → kiro_session_id` の永続マッピング）の対象外です。**長寿命の対話的セッションのみ**がマッピングされます。

> **記載漏れの修正**: `wf-author:` は v0.6.0 の `session.md`（586-587行、`8575209`）の時点で `_STATELESS_PREFIXES` の対象として記載されていましたが、本サイトの表から漏れていました。v0.7.x での新規追加ではありません。v0.7.2 では `session.md` 1258-1264行（`c67c506`）が同じ内容を記載しています。

> Slackのスレッドセッションには歴史的に2つのキー形式（レガシーな裸の `thread_ts` と正規の名前空間付き `slack:<ts>`）が存在し、両者を折り込む仕組みがあります。

## Warm Pool

`session.pool_size`（`overview.md`は既定 `0` = オフと明記）は、新しいセッションがkiro-cliのコールドスタートを払わずに開始できるよう、プロセスを事前起動します。プールされたプロセスは `session.pool_ttl_secs`（既定1800秒）を超えると、claim時に破棄されます。

> **一次情報内の不整合は解消しました**（v0.6.0 実測）。以前は `docs/architecture/overview.md` が「Warm pool (`session.pool_size`, default `0` = off)」、`docs/system-specs/modules/config.md` の Python dataclass が `pool_size: int = 2` と食い違っていました。**v0.6.0 では両方が `0`（既定は無効）で一致**します（`overview.md` 279行／`config.md` 957行「`0` (the default) disables. Single source of truth: `DEFAULT_POOL_SIZE`」）。ロード時のクランプ上限は `POOL_SIZE_MAX = 10`（`config.md` 1226行）。

- **アイドルタイムアウト**: `session.timeout_secs`（既定3600秒＝60分）経過後にセッションを回収。`0` を設定するとアイドル回収（idle sweep）が無効になります（公式 Sessions ページ／`session.md` 673行「`session.timeout_secs=0` leaves `idle_sweep_enabled` false」、`c67c506`）
- **ターン上限**: `agent.chat_turn_timeout_secs`（**既定14400秒＝4時間**。ロード時クランプは300〜86400秒。無効化不可）
  - **v0.5.0以前は7200秒＝2時間**でした。`resource-protection.md` 49行は「14400 is the default, not the ceiling」と明記しています
- **ツール承認の待機時間**: `agent.tool_approval_timeout_secs`（既定600秒＝10分。ロード時クランプは30〜7200秒、かつ `chat_turn_timeout_secs` より60秒以上小さい値へ丸められる）
- **サーキットブレーカー**: 1セッションで5回連続失敗するとリセットを強制
- **自動圧縮**: コンテキストウィンドウの `session.autocompact_pct`（**既定70%**）で発動。ロード時クランプは5.0〜90.0
  - ⚠️ **本サイトは以前「既定90%」と記載していました**。`config.md` 221行は既定値の変更履歴として `session.autocompact_pct` (90.0 -> 70.0, #4388) を挙げており、v0.6.0 実測値は **70.0** です（`config.md` 956行・`modules/cli.md` 742行「default 70%」）

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

## v0.7.0での変更

公式 Sessions ページと v0.7.0 の CHANGELOG で確認できる、セッション運用に関わる追加・変更です。

- **新規チャットの既定メモリモード**: 新しいダッシュボードチャットは **Settings → Chat → Default Memory Mode** で選んだモードで始まります。新規チャット作成時の明示的な選択が常に優先されます（CHANGELOG 69-70行）
  - モードは **Persistent（既定）**＝メモリを読み書きする、**Incognito**＝読むが書き戻さない、**Temporary**＝読みも書きもしない、の3つです。Incognito と Temporary はタブに印が付き、どちらもフォークできます（公式 Sessions ページ「Memory modes」）
  - Incognito／Temporary 自体は v0.6.0 の公式ページにも「Ephemeral sessions」として存在していました。v0.7.0 で加わったのは既定モードの設定です
- **All sessions ページ（`/sessions`）**: ブックマーク可能なセッション選択画面で、セッションを自動作成・自動選択しません。検索、**All**／**Unread** フィルタ、ステータスのチップ、**Today**／**Yesterday**／**Earlier** のグループ分けを備えます（CHANGELOG 88-90行）
- **エージェント作業中の送信（Steer／Queue）**: **Settings → Chat** で Steer と Queue のどちらを既定にするかを選べます。分割された送信ボタンが表示され、送信ショートカットが Enter のとき、Cmd／Ctrl＋Enter は1回だけ反対の動作をします（CHANGELOG 65-68行）
  - **Queue のキューは再起動後も残ります**: Kiro Crew がキュー入りしたメッセージを受け付けるとキューをディスクに書き込むため、Gateway の再起動後もキューのカードが戻ります。キューのカードは編集・並べ替え・取り消しができ、取り消すとテキストと添付がコンポーザに戻ります（公式 Sessions ページ「Typing ahead, Steer, and Queue」）
- **Session work ledger（任意）**: 長期の作業向けに、エージェントが `session_ledger_record` でゴール・フェーズ・次のステップ・却下した手法・成果物の場所を記録し、圧縮後や後の監視サイクルで `session_ledger_read` により復元できます。ledger は任意機能の Crew log の投影で、`~/.kiro/crew/.env` に `KIROCREW_CREW_LOG=1` を設定して Gateway を再起動してから使います。未設定のときの書き込みは、黙って失われるのではなく拒否されます（公式 Sessions ページ「Session work ledger (optional)」）。セッションごとの追記専用ログと、チャット右パネルの Crew log ビューは CHANGELOG 314-318行が記載しています
- **セッションのエクスポート／インポート**: セッションメニューの **Export to a file** で永続セッションをファイルに書き出し、サイドバーの **Import a session from a file** で取り込みます。別マシンから送られたセッションは **Imported** の下に送信元ごとにまとめられます。エクスポートに正確なモデルコンテキスト（直接レジュームに必要な層）を含めるのは `dashboard.export_include_layer_b` を有効にしたときだけで、**既定は off** です（CHANGELOG 374-378行／公式 Sessions ページ）
- **バックグラウンドのチャット完了通知（既定 off）**: **Settings → Notifications → Desktop alerts** に「Notify when a background chat finishes」が加わりました。オンにすると OS の通知許可を求め、完了したチャットが別のアプリやウィンドウの背後にあるときだけ通知します（CHANGELOG 104-106行／公式 Sessions ページ）
- **終了したセッションが資源を解放する**: セッションを終えると、そのプロセスツリー全体・サブエージェント・セッション単位の MCP サーバが停止します（CHANGELOG 319-321行）
- **Crew Mode は Feature Preview**: 1つのチャットで独立した複数の話題をサブセッションで並行して進める Crew Mode は、**Settings → Developer → Feature Previews** の **Crew Members** を有効にして使います（公式 Sessions ページ「Crew Mode」）

> **公式ページの既定値の記述が実装と一致しました**: v0.6.0 時点の公式 Sessions ページは、アイドルタイムアウトを「default 30 minutes」、自動圧縮を「~90% usage」と記載していました。v0.7.2 時点の同ページ（Page updated 2026-09-25）は「60 minutes of inactivity by default」「**70% by default**」と記載し、上記「Warm Pool」節の `config.md` の既定値（3600秒・70.0）と一致します。

出典: CHANGELOG.md v0.7.0節 65-106行・314-321行・374-378行（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）。
**出典**: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-09-25）

## Session summaries（v0.3.0で追加）

サイドパネルのタブが、セッション内の各スレッドが**何をしようとしていたか**と**どこに着地したか**を示します。未解決のまま残っている項目は先頭に引き上げられます。過去のセッションもオンデマンドで要約できます。

**opt-in**（既定では無効）で、**トークンコストが明示されます**。

出典: CHANGELOG.md v0.3.0節 32行（`21584ea`）。

## 未確認事項

- `session_key` の形式は当初Zenn記事のみを出典としていたが（要検証扱い）、`modules/session.md` で `_STATELESS_PREFIXES` の実装として確認済み
- Crew Mode を **Settings → Developer → Feature Previews → Crew Members** で有効化する手順は v0.7.2 時点の公式 Sessions ページで確認しましたが、この扱いになった版は確認できません。関連する一次情報は次のとおりで、本サイトは両者の関係を推測しません
  - v0.6.0 の CHANGELOG 784-786行（`c67c506`）は「**Crew is a preview opt-in**: turn on Developer Mode in Settings → Developer, then Settings → Developer → Feature Previews → Crew, to get the Crew Members entry and the new-crew-chat entry back」と記載（カード名は「Crew」）
  - v0.7.2 の `learn-cron-dashboard.md` 2700行（`c67c506`）は、Feature Previews 節は常に表示される Settings タブにあり「NOT behind Developer Mode」と記載

> **解消済み**: `session.pool_size` の既定値の食い違い（`overview.md` は0、`config.md` は2）は **v0.6.0 実測で解消**しました（両出典が `0`）。上記「Warm Pool」節を参照してください。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/sessions/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session.md>
- チャット: [03_chat.md](03_chat.md)
- 自律実行（Cron/Subagent）: [06_autonomy.md](06_autonomy.md)

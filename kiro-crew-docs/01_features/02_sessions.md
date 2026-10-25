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
**出典**（v0.8.0・v0.9.0での変更・`remove()`/`destroy()`・`thread:`・Crew log の既定）: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-10-20）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [セッションとは](#セッションとは)
- [session_keyの形式](#session_keyの形式)
- [Warm Pool](#warm-pool)
- [Session Resume](#session-resume)
- [Circuit Breaker](#circuit-breaker)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
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
| `thread:` | crewmate のチャットのメッセージへの返信スレッド（v0.9.0 の `session.md` で `_STATELESS_PREFIXES` に含まれると確認。機能は `dashboard.crewmate_threads` の背後で**既定 `false`**。詳細は「[v0.9.0での変更](#v090での変更)」） |

**ステートレスなセッション**（cron・subagent・taskrunner・channel・secretary・side・heartbeat/background・`wf-author:`・`wf-pool:`・`thread:`）は `SessionMap`（`session_key → kiro_session_id` の永続マッピング）の対象外です。**長寿命の対話的セッションのみ**がマッピングされます。

v0.9.0 の `session.md` 2018-2034行（`99e6253`）で、上記の内容（`thread:` の追加を除く）が引き続き成り立つことを確認しました。

> **記載漏れの修正**: `wf-author:` は v0.6.0 の `session.md`（586-587行、`8575209`）の時点で `_STATELESS_PREFIXES` の対象として記載されていましたが、本サイトの表から漏れていました。v0.7.x での新規追加ではありません。v0.7.2 では `session.md` 1258-1264行（`c67c506`）が同じ内容を記載しています。

> Slackのスレッドセッションには歴史的に2つのキー形式（レガシーな裸の `thread_ts` と正規の名前空間付き `slack:<ts>`）が存在し、両者を折り込む仕組みがあります。

## Warm Pool

`session.pool_size`（`overview.md`は既定 `0` = オフと明記）は、新しいセッションがkiro-cliのコールドスタートを払わずに開始できるよう、プロセスを事前起動します。プールされたプロセスは `session.pool_ttl_secs`（既定1800秒）を超えると、claim時に破棄されます。

> **一次情報内の不整合は解消しました**（v0.6.0 実測）。以前は `docs/architecture/overview.md` が「Warm pool (`session.pool_size`, default `0` = off)」、`docs/system-specs/modules/config.md` の Python dataclass が `pool_size: int = 2` と食い違っていました。**v0.6.0 では両方が `0`（既定は無効）で一致**します（`overview.md` 279行／`config.md` 957行「`0` (the default) disables. Single source of truth: `DEFAULT_POOL_SIZE`」）。ロード時のクランプ上限は `POOL_SIZE_MAX = 10`（`config.md` 1226行）。

- **画面上の名称と場所（v0.9.0）**: 公式 Configuration ページ（Page updated 2026-10-20）は、**Pre-started Sessions** カード（以前の名称は **Warm Pool**）が **Settings → Agent Harness** に移動したと記載しています。`pool_size` 等の既定値は v0.9.0 の `config.md` 2695行・3095行（`99e6253`）で変わっていません
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
- `remove()`: マッピングを**保持**します（復元可能な終了。タブを閉じる・エージェントを切り替える・アイドルで終了するなど）。次の `get_or_create` が再開します
- `destroy()` / `destroy_if()`: マッピングを削除します（恒久的な削除。再開は期待されません）

> **記述の訂正**: v0.7.2 の `session.md` 1279行（`c67c506`）と v0.8.0 の `session.md` 1777行は、`remove()` を「マッピングを削除」と記述していました。v0.9.0 の `session.md` 2042-2046行（`99e6253`）は上記のとおり `remove()` が保持、`destroy()` / `destroy_if()` が削除と記述しています。本内容は仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。

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

## v0.9.0での変更

公式 Sessions ページ（Page updated 2026-10-20）と v0.9.0 の CHANGELOG で確認できた、セッション運用に関わる追加・変更です。

### サイドバーのフィルタ・フォルダ・タイトル

- **状態でフィルタを隠す／一時停止**: フィルタメニューの **Unread**・**In progress**・**Pinned** のチップは、一致するセッションだけを表示するか、eye-slash ボタンで**非表示**にするかを選べます。**Pause all filters** がすべての状態チップを一度に外し、**Resume all filters** が戻します。ピン留めしたセッションは、タグや状態のフィルタで絞り込んでいる間も表示されます（検索と隠しフォルダは適用されます）
- **空のフォルダの整理**: サイドバーのヘッダーメニューの **Clean up empty folders** が、開いているセッションも設定も持たないフォルダを削除前にプレビューします。**Include top-level folders** で最上位のフォルダも対象にでき、プレビュー後にセッションが加わったフォルダは残ります。削除したフォルダ内の古いセッションは Older Sessions に残ります
- **フォルダの折りたたみとチップ**: 開いているフォルダの行の横にある連結線をクリックすると、そのフォルダが折りたたまれます（キーボードではフォルダのヘッダーのトグル）。チャットにインラインコードで書いたフォルダのパス（例: `projects/billing`）は、フルパスが1つのフォルダと一致するときだけ、そのフォルダを表示するチップになります
- **Regenerate title**: セッションの行メニューの **Regenerate title** が、現在のタイトルを新しく生成したものに置き換えます
- **Mark sessions unread only when they need you**（**Settings → Notifications → Alerts**）: バックグラウンドのセッションを、エージェントが終了したか回答待ちになったときだけ未読にします（新しいメッセージごとではありません）
- **プロジェクトピッカー**: プロジェクトを選ぶピッカーに **Favorites**・**Recent**・**Browse** のタブがあります。Recent または Browse から星を付けると Favorites に入り、Favorites があればピッカーはそこで開きます
- **Dim Inactive Panes**（**Settings → Chat → Sessions**）: フォーカスのない分割ペインを薄くする設定で、off にできます（`configuration` ページ）

出典: CHANGELOG.md v0.9.0節 71-82行・154-157行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/chat/sessions/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-10-20）

### 起動・再開・終了時の挙動（Notable fixes）

- 忙しいセッションをサイドバーから閉じるときは、先に確認が出ます。セッションを閉じたあとも、戻る／進むが動きます
- チャネル・cron・サブエージェントのターンでバックエンドがセッションを失ったときは、失敗せずにセッションを再読み込みします。キュー済みのメッセージはリサイクルのリセットで残り、停滞（stalled）したサブエージェントがユーザーのメッセージをせき止めません

出典: CHANGELOG.md v0.9.0節 161-167行（`99e6253`）。

### Remote crew sessions（Preview）

**Preview** です。**Settings → Developer → Feature Previews → Remote crew sessions** を有効にすると、接続した peer crew のセッションが、その crew 自身のトランスクリプト・実行状態・承認への窓として開きます。**New chat on crew** は peer 側にセッションを作り、このマシンには保存されません（公式は、メモリ上のキャッシュ以外はこのマシンに保存されないと記載しています）。

- 前提は、`instances.enabled` を `true` にして Gateway を再起動し、**Settings → Remote Crew** で crew を接続しておくことです（`instances.enabled` は既定オフ）
- Sessions の一覧は **Local** が先頭で、続いて crew ごとの折りたたみグループです。グループのヘッダーには **Online**・**Reconnecting**・**Error**・**Offline** のバッジが付きます
- 以前のビルドが turn relay（廃止済み）で peer 上で動かしたチャットは、読み取り専用で開きます
- 両方のマシンが同じ Kiro Crew の版を動かしている必要があります。版が異なるときは、窓に両側の版が表示されます（公式 Multi-instance ページ）

出典: CHANGELOG.md v0.9.0節 84-96行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>（Page updated 2026-10-20）

### `session.idle_exempt_keys` と返信スレッド

- **`session.idle_exempt_keys`**（既定 `[]`）: アイドル時計で失効させないセッションキーの一覧です。最大 10 件（`POOL_SIZE_MAX` と同じ）、各キー 512 文字以下で、超過したキーは切り詰めずに破棄され、1回警告が記録されます。ダッシュボードやcronに結び付いたセッションは、そのタブが閉じたときの回収と RSS リサイクル（有効な場合）の対象のままです（`config.md` 2691行、`99e6253`）
- **`thread:`（crewmate のチャットの返信スレッド）**: `session.md` 2031-2034行が `_STATELESS_PREFIXES` に含まれると記述しています（`side:` と同じ理由として、コールドセッションでは `build_thread_message` が封筒全体を再構築する、と記載されています）。機能は `dashboard.crewmate_threads`（**既定 `false`**）の背後にあり、オフのときは3つのルートが 404 `slot_not_found` を返します（`history.md` 1863-1876行、`99e6253`）

> 本節の2項目は v0.9.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。

**出典**（`session.idle_exempt_keys`・`thread:`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/history.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.8.0での変更

### Crew log が既定で記録される

v0.8.0 から、チャットごとの redact 済みの記録（Crew log）が**設定なしで保持されます**。セッション ledger・conductor の作業ボード・Issue Radar の crew ledger が新規インストールで動きます。会話を削除またはゴミ箱に移すと、その Crew log も一緒に削除され、ストレージ画面は Crew log をセッションと合わせて数えます。`KIROCREW_CREW_LOG=0` で全体を無効にできます。v0.7.2 までは既定オフで、`KIROCREW_CREW_LOG=1` の設定が必要でした（下の「v0.7.0での変更」の Session work ledger を参照）。

出典: CHANGELOG.md v0.8.0節 330-334行（`99e6253`）。
**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/crew-log-core.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。160行「defaults on」。v0.7.2 の同ファイル145行は「defaults off」）

### サイドバー・フォルダ・タグ・タイトル

- **フォルダ単位のステアリング**: フォルダの設定に追加のステアリングディレクトリを指定でき、そのフォルダとサブフォルダに入れたすべてのチャットが、任意のエージェントバックエンドでそのステアリングつきで始まります
- **Folder order**: サイドバーのソートメニューに **Folder order**（`custom`・`name`・`created`）が加わりました。`dashboard.folder_sort` の既定は `custom` で、フォルダの保存済みの並びは書き換えません（`config.md` 2788行・3200-3216行）
- **conductor view**: サイドバーの lane ボタンの **conductor view** が、各セッションを開いた側のセッションの下にネストします。折りたたんだ行に子と needs-you の件数が出ます。タグボードが有効なときは出ません。Crew log を読みます（Crew log は無効にしない限り記録されます）
- **Manage Tags の Agent permissions**: タグごとに **Human only**・**Agent: add only**・**Agent: add & remove** を選べます。v0.8.0 より前に作ったタグは、dashboard の owner が **Set up agent permissions** を選ぶまで agent-locked のままです（既定は安全側）
- **フォルダ行のメニュー**: フォルダ行の右クリックまたは長押しで、三点ボタンと同じメニューが出ます
- **`dashboard.title_refresh_every_turns`**（`config.json`、**既定 `0`**）: 自動生成タイトルを N ターンごとに再検討します。`0` は 8・24 ターン目のマイルストーンだけです。loader は `0` か 4〜1000 に制限します。更新ごとにバックグラウンド呼び出しが1回かかり、ユーザーが付けたタイトルは変更しません（`learn-cron-dashboard.md` 4271行）

出典: CHANGELOG.md v0.8.0節 251-282行（`99e6253`）。
**出典**（`title_refresh_every_turns`・`folder_sort`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/learn-cron-dashboard.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-10-20）

### エージェントがセッションに対してできること

- エージェントはトランスクリプトを fork でき、別のセッションを adopt／release して自分の下にネスト／解除できます。conductor は作業 ledger を Crew log から再構築できます
- エージェントは、自分が開くセッションのモデルを指定でき、アイドルなセッションのモデルを次のターンから変更できます。変更はそのセッションのモデルチップに、利用者が選んだものと同じように表示されます。途中で利用者が選んだモデルが優先され、ターンまたはサブエージェント実行中のセッションは停止までモデルを維持します
- エージェントはセッションを pin／unpin できます（filing・tagging と同じ所有ルール）
- **モデル指定と pin は、ダッシュボードのツールセットをマウントするテンプレートのエージェントが必要で、メッセージングチャネルから話しかけているエージェントは拒否されます**
- 自分の Discord／Telegram の DM では conductor を動かせます（ワーカーを dispatch して作業 ledger を使えます。以前はチャネルのセッションでは拒否されていました）

出典: CHANGELOG.md v0.8.0節 310-329行（`99e6253`）。

### 起動・再開・回収

- セッションの起動は、低速なホストで **90 秒**待ちます。失敗し続ける起動は 3 回で背景の再試行を止め、起動済みの MCP サーバを後始末します。仕様書 `acp-client.md` 2354行（`99e6253`）の `agent.session_start_timeout_secs`「90s floor」と整合します
- 再起動やクラッシュでターンが中断されたセッションは **interrupted** と表示され、Resume を提示します。Resume はその中断されたターンを続行します
- バックエンドがセッションを失ったチャットは、再接続して1回だけ再試行します
- アクティブなサブエージェントを持つセッションは、アイドルとして回収されません

出典: CHANGELOG.md v0.8.0節 524-526行・550-551行・651-662行（`99e6253`）。

## v0.7.0での変更

公式 Sessions ページと v0.7.0 の CHANGELOG で確認できる、セッション運用に関わる追加・変更です。

- **新規チャットの既定メモリモード**: 新しいダッシュボードチャットは **Settings → Chat → Default Memory Mode** で選んだモードで始まります。新規チャット作成時の明示的な選択が常に優先されます（CHANGELOG 69-70行）
  - モードは **Persistent（既定）**＝メモリを読み書きする、**Incognito**＝読むが書き戻さない、**Temporary**＝読みも書きもしない、の3つです。Incognito と Temporary はタブに印が付き、どちらもフォークできます（公式 Sessions ページ「Memory modes」）
  - Incognito／Temporary 自体は v0.6.0 の公式ページにも「Ephemeral sessions」として存在していました。v0.7.0 で加わったのは既定モードの設定です
- **All sessions ページ（`/sessions`）**: ブックマーク可能なセッション選択画面で、セッションを自動作成・自動選択しません。検索、**All**／**Unread** フィルタ、ステータスのチップ、**Today**／**Yesterday**／**Earlier** のグループ分けを備えます（CHANGELOG 88-90行）
- **エージェント作業中の送信（Steer／Queue）**: **Settings → Chat** で Steer と Queue のどちらを既定にするかを選べます。分割された送信ボタンが表示され、送信ショートカットが Enter のとき、Cmd／Ctrl＋Enter は1回だけ反対の動作をします（CHANGELOG 65-68行）
  - **Queue のキューは再起動後も残ります**: Kiro Crew がキュー入りしたメッセージを受け付けるとキューをディスクに書き込むため、Gateway の再起動後もキューのカードが戻ります。キューのカードは編集・並べ替え・取り消しができ、取り消すとテキストと添付がコンポーザに戻ります（公式 Sessions ページ「Typing ahead, Steer, and Queue」）
- **Session work ledger**（v0.7.2 までは任意機能の位置づけ）: 長期の作業向けに、エージェントが `session_ledger_record` でゴール・フェーズ・次のステップ・却下した手法・成果物の場所を記録し、圧縮後や後の監視サイクルで `session_ledger_read` により復元できます。ledger は Crew log の投影です。v0.7.2 までは Crew log が任意機能で、`~/.kiro/crew/.env` に `KIROCREW_CREW_LOG=1` を設定して Gateway を再起動してから使いました。**v0.8.0 以降は Crew log が既定で記録される**ため設定は不要です。`KIROCREW_CREW_LOG=0` を指定して Gateway を起動すると Crew log が無効になり、ledger の書き込みは他の保存先に切り替わらず拒否されます（v0.9.0 時点の公式 Sessions ページ「Conductor view and session work ledger」、Page updated 2026-10-20。v0.8.0 の変更は上の「v0.8.0での変更」を参照）。セッションごとの追記専用ログと、チャット右パネルの Crew log ビューは CHANGELOG 314-318行が記載しています
- **セッションのエクスポート／インポート**: セッションメニューの **Export to a file** で永続セッションをファイルに書き出し、サイドバーの **Import a session from a file** で取り込みます。別マシンから送られたセッションは **Imported** の下に送信元ごとにまとめられます。エクスポートに正確なモデルコンテキスト（直接レジュームに必要な層）を含めるのは `dashboard.export_include_layer_b` を有効にしたときだけで、**既定は off** です（CHANGELOG 374-378行／公式 Sessions ページ）
- **バックグラウンドのチャット完了通知（既定 off）**: **Settings → Notifications → Desktop alerts** に「Notify when a background chat finishes」が加わりました。オンにすると OS の通知許可を求め、完了したチャットが別のアプリやウィンドウの背後にあるときだけ通知します（CHANGELOG 104-106行／公式 Sessions ページ）
- **終了したセッションが資源を解放する**: セッションを終えると、そのプロセスツリー全体・サブエージェント・セッション単位の MCP サーバが停止します（CHANGELOG 319-321行）
- **Crew Mode は Feature Preview**: 1つのチャットで独立した複数の話題をサブセッションで並行して進める Crew Mode は、**Settings → Developer → Feature Previews** の **Crew Members** を有効にして使います（v0.7.2 時点の公式 Sessions ページ「Crew Mode」。v0.9.0 時点の同ページは同じカードを **Crewmates** と記載しています。下の「未確認事項」を参照）

> **公式ページの既定値の記述が実装と一致しました**: v0.6.0 時点の公式 Sessions ページは、アイドルタイムアウトを「default 30 minutes」、自動圧縮を「~90% usage」と記載していました。v0.7.2 時点の同ページ（Page updated 2026-09-25）は「60 minutes of inactivity by default」「**70% by default**」と記載し、上記「Warm Pool」節の `config.md` の既定値（3600秒・70.0）と一致します。

出典: CHANGELOG.md v0.7.0節 65-106行・314-321行・374-378行（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）。
**出典**: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-09-25）

## Session summaries（v0.3.0で追加）

サイドパネルのタブが、セッション内の各スレッドが**何をしようとしていたか**と**どこに着地したか**を示します。未解決のまま残っている項目は先頭に引き上げられます。過去のセッションもオンデマンドで要約できます。

**opt-in**（既定では無効）で、**トークンコストが明示されます**。

出典: CHANGELOG.md v0.3.0節 32行（`21584ea`）。

## 未確認事項

- Crew Mode の扱い（下の食い違い）
- Feature Previews のカード名が **Crew Members** から **Crewmates** に変わった版。v0.8.0 の CHANGELOG 338行（`99e6253`）は「Crew Members preview」、v0.9.0 の CHANGELOG は Crewmates ページと記述しており（17行）、Feature Previews のカード名は公式 Sessions ページ・Agents ページ（いずれも Page updated 2026-10-20）が「Crewmates」と記載しています。カード名の変更を告知した CHANGELOG の項目は確認できません

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **公式 Sessions ページ**（Page updated 2026-10-20）: Crew Mode を、1つのチャットで独立した複数の話題をサブセッションで並行して進める機能として説明し、**Settings → Developer → Feature Previews → Crewmates** を有効にして使うと記載しています
> - **`modules/crew-mode.md`**（v0.7.2 と v0.9.0。v0.9.0 は 5-13行・1924-1935行、`99e6253`）: Crew Mode（`"crew"` スロットモード）は Crew Members ページに置き換えられて廃止された（retired）と記述しています
> - **v0.8.0 の CHANGELOG** 338行は、同じプレビューを「Crew Members preview」と呼んでいます
>
> 公式 Sessions ページの Crew Mode と、リポジトリで廃止とされる Crew Mode が同じ機能か、Crewmates プレビューの別名かは、一次情報から判断できません。

> **解消済み（Developer Mode の要否）**: 以前は、v0.6.0 の CHANGELOG 784-786行（`c67c506`）が「Developer Mode を有効にしてから Feature Previews」と記載する一方、仕様書は Developer Mode の背後にないと記述していました。v0.9.0 の `learn-cron-dashboard.md` 4265行（`99e6253`）は Feature Previews の節が「NOT behind Developer Mode」と記述し、v0.9.0 時点の公式 Sessions・Agents・Configuration ページも Developer Mode に触れず Feature Previews の手順だけを記載しています。v0.6.0 の CHANGELOG の文面自体は過去版の記述として残っています。

> **解消済み**: `session_key` の形式は当初Zenn記事のみを出典としていました（要検証扱い）が、`modules/session.md` で `_STATELESS_PREFIXES` の実装として確認済みです。

> **解消済み**: `session.pool_size` の既定値の食い違い（`overview.md` は0、`config.md` は2）は **v0.6.0 実測で解消**しました（両出典が `0`）。v0.9.0 の `config.md` 2695行・`overview.md` 285行（`99e6253`）でも既定は `0` です。上記「Warm Pool」節を参照してください。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/sessions/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session.md>
- チャット: [03_chat.md](03_chat.md)
- 自律実行（Cron/Subagent）: [06_autonomy.md](06_autonomy.md)

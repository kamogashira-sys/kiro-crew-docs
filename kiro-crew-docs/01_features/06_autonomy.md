# 自律実行

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: リポジトリ README「Autonomy modes」節
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://kiro.dev/docs/crew/features/cron/>・<https://kiro.dev/docs/crew/features/task-runner/>・<https://kiro.dev/docs/crew/features/subagents/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{heartbeat,taskrunner,subagent}.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（`agent.max_subagents`既定値の不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（Subagent・Cron・Heartbeat のタイムアウト値の再測定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**（`orchestrator.max_plan_duration_seconds`）: <https://github.com/kirodotdev/KiroCrew/blob/v0.7.2/docs/system-specs/modules/autopilot.md>（`main` ブランチでは v0.7.2 以降にこのファイルが削除されているため、タグ固定のURLを示します）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.7.0での変更・v0.7.2での再確認）: <https://github.com/kirodotdev/KiroCrew/blob/v0.7.2/docs/system-specs/modules/{subagent,taskq,adaptive-concurrency,config,autopilot,learn-cron-dashboard,taskrunner}.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.7.2での再確認）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/features/cron/>（Page updated 2026-09-25）・<https://kiro.dev/docs/crew/features/task-runner/>（Page updated 2026-09-25）・<https://kiro.dev/docs/crew/features/subagents/>（Page updated 2026-09-30）

---

## 📑 このページの内容

- [起動モード5分類](#起動モード5分類)
- [Scheduled: Cron](#scheduled-cron)
- [Heartbeat（分類外・実在する第6の仕組み）](#heartbeat分類外実在する第6の仕組み)
- [Task Runner](#task-runner)
- [Subagents](#subagents)
- [未確認事項](#未確認事項)

---

## 起動モード5分類

README が整理する、Crew がユーザーの入力なしで動く5つの起動モードです。

| モード | 用途 | 起点 |
|-------|------|------|
| **Scheduled**（スケジュール） | 定期報告・監査・バックアップ・定常保守 | `kirocrew cron` または自然言語での依頼 |
| **Proactive**（自発） | 新しいユーザーメッセージを待たずに追加のパスが必要なゴール | AutoNudge・goal-loop スキル |
| **Reactive**（反応） | CIアラート・外部オートメーション・メッセージングチャネルの活動 | 認証済みエージェントwebhook・メッセージングイベント |
| **Task runner**（タスク実行） | 明示的なステップ・テスト・レビュー・チェックポイント再開を伴う有界のプロジェクト | `kirocrew run TASK.md` |
| **Subagents**（サブエージェント） | 並行して動く独立した作業ストリーム | `kirocrew spawn run "task"` |

> **Autopilot はこの分類には含まれません**。Autopilot は Chat のper-slotモード（`mode == "orchestrator"`）であり、起動モードではありません。詳細は [03_chat.md](03_chat.md) を参照してください。

## Scheduled: Cron

`kirocrew cron add` でスケジュールジョブを作成します。

| オプション | 内容 |
|-----------|------|
| `--cron "<expr>"` | 標準cron式（`--every` と排他） |
| `--every <secs>` | 秒単位の間隔 |
| `--timezone "<tz>"` | ジョブ単位のタイムゾーン（IANA名）。既定の記述は[下記](#タイムゾーンの既定)を参照 |
| `--skip-dates "YYYY-MM-DD,..."` | 特定日を除外 |
| `--timeout-secs <n>` | ジョブごとのタイムアウト（既定1800秒） |
| `--agent <name>` | 実行するエージェント |
| `--persistent-session` | 実行をまたいで1つのセッションを再利用。既定の記述は[下記](#persistentfresh-セッションの既定)を参照 |

推論を伴わないCronのScript／Commandは**ACPを経由しません**。

### v0.7.0での変更（Cron・スケジュールジョブ）

- **Minimal context**: エージェントジョブの作成・編集ダイアログ（Schedule ページ）の **Minimal context** トグル、または MCP ツールでの `minimal_context: true` で、保存履歴を必要としないジョブの注入コンテキストを省けます。ジョブの指示と必須のメンバー／プロジェクトのガイダンスは残り、エージェントは変わらず、Script ジョブにもなりません（CHANGELOG 256-259行／公式 cron ページ「Minimal context」）
- **`cron-cost-optimize` スキル**: 記録された実行履歴から script／minimal-context／full-context のどれで実行するかを推奨します。**ジョブを自分で変更することはありません**（CHANGELOG 260-262行／公式 cron ページ）
- **スケジュールどおりの発火**: 低頻度のジョブが予定の分に起動する（スキップされない）、各ジョブのスケジュールがそのジョブのタイムゾーンで表示される、persistent なジョブのタブを Schedule ページからチャットフォルダに入れられる、セキュリティゲートがツール呼び出しを拒否したジョブは成功ではなく拒否を報告する、の4点です（CHANGELOG 433-437行）

出典: CHANGELOG.md v0.7.0節（`c67c506`）、<https://kiro.dev/docs/crew/features/cron/>（Page updated 2026-09-25）。

#### タイムゾーンの既定

公式 cron ページ（Page updated 2026-09-25）は `--timezone` の既定を「global config timezone, then UTC」（グローバル設定のタイムゾーン、未設定ならUTC）と記述し、壁時計の時刻を指定するジョブには常に明示的に `--timezone` を指定するよう案内しています。2026-08-31 更新時点の同ページは「defaults to UTC」と記述していました。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | ジョブ自身のタイムゾーンがない場合 |
> |---|---|
> | 公式 cron ページ（Page updated 2026-09-25） | グローバル設定のタイムゾーン、未設定ならUTC |
> | `learn-cron-dashboard.md` 282行（`c67c506`） | 「A job without its own timezone retains the published server-timezone fallback」（サーバのタイムゾーンへのフォールバックを維持） |
>
> 「グローバル設定のタイムゾーン」と「サーバのタイムゾーン」が同じものを指すかどうかは確認できていません。

#### Persistent／Fresh セッションの既定

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | 既定とされているもの |
> |---|---|
> | 公式 cron ページ（Page updated 2026-09-25） | **Persistent**。`--persistent-session` の説明に「persistent is the stored default」、「**Persistent** (default) reuses one session…」。Fresh にするにはダッシュボードまたは MCP ツールで `persistent_session: false` を設定する |
> | 公式 cron ページ（Page updated 2026-08-31。本サイトの v0.6.0 時点の参照） | **Fresh**。`--persistent-session` の説明に「default: fresh session per run」、「**Fresh (default)** — every run starts a new session」 |
> | リポジトリ `learn-cron-dashboard.md`（`c67c506`） | `persistent_session` の既定値の明記は見つかっていません |
>
> CHANGELOG の v0.7.0〜v0.7.2 節にも、この既定の変更を説明する記載は見つかっていません。

### v0.3.0での変更（Cron・スケジュールジョブ）

- **各jobが自身の時間予算を設定できる（最大24時間）**。従来の固定30分上限を置き換えます。jobのinstructionsは50,000文字まで記述できます（CHANGELOG 184行）。**⚠️ これは job（スケジュールジョブ）の時間予算であり、[Subagent](#subagents) の1件あたりハードタイムアウトとは別項目です**（Subagent 側は v0.3.0（`21584ea`）時点では1800秒＝30分でしたが、**v0.6.0 で10800秒＝3時間に変更**されました。[04_reference/05_limits.md](../04_reference/05_limits.md)参照）
- **スケジュールジョブが毎実行ごとに再審査される**。作成時のみでなく発火ごとに現行ポリシーへ照合されるようになり、復元したバックアップが承認システムを迂回してshellコマンドを持ち込むことができなくなりました（CHANGELOG 215行）
- **ジョブのPythonソースをターミナルなしで読める**。ジョブ詳細ビューにハイライト付き・読み取り専用で表示されます（CHANGELOG 186行）

出典: CHANGELOG.md v0.3.0節（`21584ea`）。

> **Cron自体の最小間隔（v0.3.0で確認、v0.7.2で再確認）**: `docs/system-specs/modules/learn-cron-dashboard.md` の「## Cron Service (`cron.py`)」節（136行、`c67c506`）が、3種のスケジュール方式を「`every` (interval, **min 60s**), `at` (one-shot timestamp), `cron` (5-field expression)」と定義しています（173行。v0.3.0（`21584ea`）時点では59行）。これはCron Service全体の仕様記述であるため、`--every` による新規作成にも**60秒の下限が適用されます**。あわせて、他エージェントからインポートしたスケジュールにも「整数秒かつ60秒以上」の検証ルールがあります（同ファイル910-911行「Interval values must map exactly to an integer number of native seconds and remain at least 60 seconds」。`21584ea` 時点では299行）。

## Heartbeat（分類外・実在する第6の仕組み）

README の起動モード5分類には無いが、`modules/heartbeat.md` に実在する仕組みです。**分類の差として両方扱います。**

- `kiro_crew/heartbeat.py` が既定60秒間隔で周期的なバックグラウンドタスクを実行
- `~/.kiro/crew/workspace/HEARTBEAT.md` を読み、空でないタスクをエージェントに送信
- タスク1行につき1つ（複数行非対応）。`#` で始まる行・空行・HTMLコメントは無視
- エージェントの応答に `HEARTBEAT_KEEP` が含まれていれば未完了として次のtickまで保持、無ければ完了として削除
- 例外が発生したタスクは自動的に保持（再試行）
- 15tickごとにFTSインデックスを再構築（既定間隔で約15分ごと）
- 無人ターンのため、1タスクあたり1800秒（30分）のタイムアウトがCronの `_JOB_TIMEOUT_SECS` と同じ形で適用される

## Task Runner

仕様ファイルを読み、LLMでステップに分解し、各ステップをACPセッションで実行します。テストによる検証・リトライ・進捗のチェックポイント保存を伴います。

主な機能: 複数タスクの同時実行・対話的なツール承認・ステップごとのセッション分離（全メモリ注入込み）・git連携のステップコミット／リバート・実差分による独立レビュー・循環検出・再起動をまたぐディスク永続化・活動監視ベースの停滞検出・リソース枯渇を防ぐバッチ並列実行。

内部は `taskrunner.py`（オーケストレータ）＋4つのヘルパーモジュール（`task_models.py`／`task_planner.py`／`task_executor.py`／`task_reporter.py`）に分割されています。

### v0.7.0での変更（クラッシュ復旧・永続タスクキュー）

Task Runner のステップは、Subagent・Workflow の呼び出しと同じ**永続タスクキュー**に記録されるようになりました（CHANGELOG 309-313行。キューの仕組みは [Subagents の v0.7.0での変更](#v070での変更subagent永続タスクキュー適応的並行) を参照）。公式 Task Runner ページは、run と受け付けた各ステップを**実行前に記録**し、Gateway の再起動後は再試行が安全かどうかで中断した作業を照合すると記述します。

| 中断した作業 | 再起動後の扱い |
|---|---|
| git で協調している run | チェックポイントから**自動で再開**。passed／skipped のステップは完了のまま、未完了のステップには新しい試行記録が作られる |
| git worktree などの冪等性の保証がない run | 副作用が不明である旨の通知付きで **Paused** として再オープン。外部の状態を確認してから Tasks ページで再開する |
| キューにあったが開始していなかったステップ | 旧 Gateway のものとして cancelled にされる。run を再開すると、所有者のいないキュー行を実行するのではなく新しいステップ記録が受け付けられる |

run の投影は `~/.kiro/crew/tasks/` 配下に、共有のスケジューリングキューは `tasks/tasks.db` に保存されます。

出典: <https://kiro.dev/docs/crew/features/task-runner/>（Page updated 2026-09-25）「Crash recovery」、CHANGELOG.md v0.7.0節 309-313行（`c67c506`）、`taskrunner.md` 405-413行（`c67c506`）。

### v0.6.0での変更（無人 auto-run plan の時間上限）

**無人の auto-run plan は2時間で停止します。** これは v0.6.0 の破壊的変更です。

| 項目 | 内容 |
|---|---|
| 設定キー | `orchestrator.max_plan_duration_seconds`（既定 `7200` 秒＝2時間） |
| 無効化 | `0` を設定すると上限がなくなります |
| 判定タイミング | **plan 全体の実時間予算**で、**各ステージ境界でチェック**されます（ステージの途中で打ち切られません） |
| 警告 | 予算の75%に達した時点で1回だけ警告します |
| 適用外 | **stage-gated な plan は打ち切られません** |
| 関連キー | `orchestrator.stage_timeout_seconds`（ステージ単位のタイムアウト） |

出典: `docs/system-specs/modules/autopilot.md` 283行（既定2時間）・288-290行（75%の警告・`auto_run` のみに適用）・499-500行（設定キーの表）（v0.7.2で再確認、`c67c506`）。

## Subagents

`kirocrew spawn run "task"` で並行作業を委任します。

**並行数の上限（S15・出典間で食い違うため両併記）**:

- `agent.max_subagents` の既定値について、`modules/subagent.md`は「**`0`**」（＝起動時に自動サイジング）、`modules/config.md`のPython dataclass literalは「**`= 3`**」と記述しており**一致しません**。`0`の場合、下限3・上限は`agent.subagent_auto_max`で自動サイジングされます。正の値を指定すると固定キャップになります
- 自動サイジングの上限 `agent.subagent_auto_max` の既定値について、`modules/subagent.md` は「**32**」、`modules/config.md` は「**`= 16`**」と記述しており**一致しません**。別途 `SUBAGENT_AUTO_MAX_CEILING = 64`（設定ロード時のクランプ上限）が存在します
- **本サイトはこの食い違いを裁定しません**。両方の値を記録するのみです
- v0.7.2 でも同じ記述です（`subagent.md` 99行・`config.md` 1847-1848行、`c67c506`）。公式 Subagents ページ（Page updated 2026-09-30）は「Crew auto-sizes the concurrent cap from available host memory and CPU. A configured ceiling can narrow it further」と記述しています

その他の確定事項:

- **1サブエージェントあたりのハードタイムアウト: 10800秒（3時間）**。設定キーは `agent.subagent_timeout_secs`（`subagent.py` の `_TIMEOUT_SECS` がフォールバック）。**v0.5.0以前は1800秒（30分）の固定値**でした
  - ⚠️ **このキーはダッシュボードから設定できません**。`resource-protection.md` 424-427行（`c67c506`）は「config PUT の allowlist はターン予算と並行数の上限しか含まないため、subagent の期限を上げるには CLI か `config.json` の編集が必要」と述べています
  - タイムアウト時のエラー文は `Timed out after 180 minutes`（`subagent.md` 731行、`c67c506`）。`start_reaper()` が60秒間隔で期限超過のサブエージェントを強制終了します（同808行）
- 外側のキャップ: セマフォ待機＋注入の最大合計秒数 1200秒（20分。`_ON_DONE_TIMEOUT`）
- 内側のキャップ: `stream_and_collect` 1回あたり900秒（15分。`INJECTION_TIMEOUT`）
- 1サブエージェントあたりのツール呼び出し予算: **既定1000**（`_TURN_LIMIT`。`agent.subagent_max_turns` で変更可能、ロード時に `[1, 1000]` へクランプされるため既定値が上限と同じです）。**v0.6.0以前は既定100**でした（`config.md` 407行「`agent.subagent_max_turns` (100 -> 1000, #12203)」）。公式 Subagents ページも「up to 1000 tool calls」と記述します
  - 出典: `config.md` 1849行・`subagent.md` 104行・`resource-protection.md` 18行（`c67c506`）
- 下限3・入れ子不可（サブエージェントからさらにサブエージェントは起動できない）
- 空きメモリの admission gate（`spawn_min_memory_gb`）は、Linux では cgroup の余裕量、macOS と Windows ではネイティブのメモリ読み取りを使います。**ホストのメモリも有限の cgroup 上限も読み取れないときに限って fails open**（チェックをスキップして起動を許可）します（`subagent.md` 156-160行、`c67c506`）。**v0.6.0 では `/proc/meminfo` を読むため Linux のみ有効で、非Linuxでは fails open** でした（v0.6.0 `subagent.md` 52-55行、`8575209`）。本内容は v0.7.0 以降のタグの仕様書で確認したもので、CHANGELOG には記載が見つかっていません。既定値は `subagent.md`・`config.md` のいずれにも数値の記載が見つかっていません（未確認）

### v0.7.0での変更（Subagent・永続タスクキュー・適応的並行）

**永続タスクキュー（durable task queue）**

- 受け付けた Subagent の作業は、ID を返す**前に** `$KIROCREW_HOME/tasks/tasks.db` へ書き込まれます。キューにある作業は Gateway の再起動を生き残り、起動後に容量が空いた時点でスケジューリングに戻ります。復旧したエントリは保守的に照合され、副作用が不確かな作業が黙って繰り返されることはありません（公式 Subagents ページ「Durable queue」／`taskq.md` 5-12行）
- CHANGELOG は、Subagent・Task Runner のステップ・Workflow の呼び出しのすべてが永続キューの行になり、状況は **Tasks**、容量は **System** ページの **Services** タブで確認できると記述します（CHANGELOG 309-313行）
- 設定キー: `agent.task_queue_enabled`（**既定 `true`**。`false` で1リリースの間だけ従来のメモリ上のキューを使い、`tasks.db` は残したまま読まれない）、`agent.task_dispatch_window`（**既定 `64`**、`[1, 4096]`。メモリ上に保持するキュー済みエントリの上限、変更は再起動後に反映）（`config.md` 1854-1855行・`taskq.md` 1535-1536行）
- キューが有効なまま `tasks.db` を開けない場合、spawn はメモリ上のキューにフォールバックせず、`task_store_unavailable` として**すべて拒否**されます（`taskq.md` 593-599行）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | メモリが逼迫したときの spawn |
> |---|---|
> | 公式 Subagents ページ（Page updated 2026-09-30） | 「Under memory pressure, a spawn is refused as back-pressure」（back-pressure として**拒否**される。再試行すべき一時的なエラーではなく、軽い手段を選ぶ合図） |
> | `taskq.md` 9-10行・`subagent.md` 308-311行（`c67c506`） | 「Memory pressure defers a row instead of refusing it」。永続行がある場合は**延期**（行は `queued` のまま、`agent.admit_wait_secs` 後に再確認）、永続行がない場合は従来どおり拒否 |

**適応的並行（adaptive concurrency）**

- `agent.max_subagents`（または自動サイジングされた値）を**上限として書き換えずに**、その下で実効的な並行上限（effective cap）を動かします。ホストの逼迫が裏付けられると半減し、問題のない期間ごとに1段ずつ戻り、深刻な逼迫ではディスパッチを一時停止して1件の試行で再開します。**小さくなった上限に合わせて実行中の作業を止めることはありません**（`adaptive-concurrency.md` 3-11行）
- 設定キー（すべて再起動なしで反映）: `agent.adaptive_concurrency`（**既定 `true`**。`false` でユーザー設定の上限のみ）、`agent.adaptive_concurrency_mode`（**既定 `"aimd"`**。`"fixed"` で上限を固定）、`agent.adaptive_floor`（既定 `1`）、`agent.adaptive_initial`（既定 `4`、起動時の実効上限）（`adaptive-concurrency.md` 211-218行・`config.md` 1864-1865行）
- **`resource_status`**: 実際に適用中の並行上限（設定上の最大値との対比）、利用可能メモリ、CPU 負荷、現在の posture を報告します。**助言（advisory）であり、何も予約しません**。posture が `tight` または `critical` のときは並列数を減らすか重い処理を後回しにするよう公式は案内しています（公式 Subagents ページ「Limits and host capacity」／CHANGELOG 438-441行）

**委任のゲート（Delegation gate）**

- `spawn_run` は、理由を示さない**単一タスクの委任を拒否**します。別のエージェント・モデル・Crew を指定するか、次のいずれかの理由が必要です: `parent_parallel`（親が別の作業を並行して進める）／`bulk_data`（大きな入力の分離した要約）／`fresh_context`（現在の推論を引き継がない独立レビュー・再現）／`specialist`（親にない能力）／`user_requested`（ユーザーが明示的に依頼）
- モデル値 `auto` は「別モデル」の根拠になりません。理由は run の記録に**モデルの主張として**残り、認可の証明としては扱われません（公式 Subagents ページ「Delegation gate」／CHANGELOG 438-441行）

**run 操作のスコープ**

- エージェントが使う run 操作（list・inspect・steer・continue・retry・release・delete）は、**その Subagent を開始したセッション自身の run に限られます**。すべての run を操作できる所有者の画面はダッシュボードの **Activity** パネルです。セッション ID を持たない内部の呼び出し元は、親のない CLI run だけを扱えます。セッションが ID の欠落を報告した場合は `kirocrew doctor` を実行します（公式 Subagents ページ「Stopping and retrying」／`subagent.md` 672行）

出典: <https://kiro.dev/docs/crew/features/subagents/>（Page updated 2026-09-30）、CHANGELOG.md v0.7.0節（`c67c506`）、`docs/system-specs/modules/{taskq,adaptive-concurrency,config,subagent}.md`（`c67c506`）。

### v0.3.0での変更（Subagent・メモリガバナー）

- **Subagentが主エージェントと同様に承認を求める**。subagentの承認要求が trust／auto-approve／プロンプトのいずれかを通るようになり、従来のように要求がドロップされて子プロセスが固まることがなくなりました（CHANGELOG 193行）
- **メモリが致命的に少ないときの挙動が定義された**（メモリガバナー）。スケジュールジョブは延期され、新規subagentは拒否されます。ヘッダに現在の姿勢（posture）が表示されるため、重い作業が失敗する前に把握できます（CHANGELOG 181行）
- **メモリ上限が全同時エージェントの合計に適用される**。上限が同時実行中の全エージェントにまとめて適用されるようになり、小さなspawnを多数行ってホストのメモリを食い潰すことができなくなりました（CHANGELOG 218行）

出典: CHANGELOG.md v0.3.0節（`21584ea`）。

## 未確認事項

- `spawn_min_memory_gb` の既定値（数値記載なし）
- `agent.max_subagents` の真の既定値（0 vs 3の食い違いは未解消）
- `agent.subagent_auto_max` の真の既定値（32 vs 16の食い違いは未解消）
- Cron の `persistent_session` の既定値（公式 cron ページの記述が更新前後で Persistent／Fresh と逆になっており、リポジトリの仕様書に既定値の明記が見つからない。上記「[Persistent／Fresh セッションの既定](#persistentfresh-セッションの既定)」参照）
- 「入れ子不可」と v0.7.2 の仕様書の関係（`subagent.md` 106行は `_SYSTEM_PREFIX` を「spawn recursion を防ぐ」と記述する一方、同1235-1237行は spawning session が `subagent:<id>` の場合の親子リンク（S → A → B）をタスクストアが保持すると記述している。本サイトでは両者の関係を精査していない）
- メモリ逼迫時の spawn が拒否か延期か（上記のとおり公式ページとリポジトリの仕様書で記述が異なる）
- Task Runner・Workflow のキュー行の扱い（`taskq.md` 32-35行は「TaskRunner and workflows are imported as rows but not yet dispatched from them (`awaiting_adapter`)」と記述し、同1232-1234行は `TaskRunner.attach_task_admission`・`WorkflowService.attach_task_admission` が復旧アダプタを実行すると記述している。本サイトでは両者の関係を精査していない）

> **解消済み**: 「Cron自体（`--every`）の最小間隔」は、`21584ea`の`learn-cron-dashboard.md` 59行で**60秒**と確認できたため未確認事項から除きました（上記「Scheduled: Cron」節参照）。v0.7.2（`c67c506`）でも同じ記述です（173行）。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/cron/>、<https://kiro.dev/docs/crew/features/task-runner/>、<https://kiro.dev/docs/crew/features/subagents/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>
- リポジトリ（永続タスクキュー・適応的並行）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/taskq.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/adaptive-concurrency.md>
- Workflows（永続化されたワークフロー呼び出し）: [17_workflows.md](17_workflows.md)
- Chat（Autopilot）: [03_chat.md](03_chat.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

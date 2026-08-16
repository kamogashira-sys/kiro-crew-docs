# 自律実行

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: リポジトリ README「Autonomy modes」節
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**: <https://kiro.dev/docs/crew/features/cron/>・<https://kiro.dev/docs/crew/features/task-runner/>・<https://kiro.dev/docs/crew/features/subagents/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{heartbeat,taskrunner,subagent}.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

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
| `--timezone "<tz>"` | ジョブ単位のタイムゾーン（IANA名、既定UTC） |
| `--skip-dates "YYYY-MM-DD,..."` | 特定日を除外 |
| `--timeout-secs <n>` | ジョブごとのタイムアウト（既定1800秒） |
| `--agent <name>` | 実行するエージェント |

推論を伴わないCronのScript／Commandは**ACPを経由しません**。

> **Cron自体の最小間隔について**: 公式 `cli-reference` にはCronコマンド自体の最小間隔の明記がありません。確認できたのは「他エージェントからインポートしたスケジュールの検証ルール」（`learn-cron-dashboard.md`: 「Interval values must map exactly to an integer number of native seconds and remain at least 60 seconds」＝60秒以上・整数秒）のみです。Cron新規作成時にも同じ制約が適用されるかは**未確認**です。

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

## Subagents

`kirocrew spawn run "task"` で並行作業を委任します。

**並行数の上限（S15・出典間で食い違うため両併記）**:

- `agent.max_subagents` の既定は **`0`**（＝起動時に自動サイジング。下限3・上限は `agent.subagent_auto_max`）。正の値を指定すると固定キャップになります
- 自動サイジングの上限 `agent.subagent_auto_max` の既定値について、`modules/subagent.md` は「**32**」、`modules/config.md` は「**`= 16`**」と記述しており**一致しません**。別途 `SUBAGENT_AUTO_MAX_CEILING = 64`（設定ロード時のクランプ上限）が存在します
- **本サイトはこの食い違いを裁定しません**。両方の値を記録するのみです

その他の確定事項:

- 1サブエージェントあたりのハードタイムアウト: 1800秒（30分）
- 外側のキャップ: セマフォ待機＋注入の最大合計秒数 1200秒（20分）
- 下限3・入れ子不可（サブエージェントからさらにサブエージェントは起動できない）
- 空きメモリの admission gate（`spawn_min_memory_gb`）は**Linuxのみ有効**（`/proc/meminfo` を読む）。**非Linuxでは fails open**（チェックをスキップして起動を許可）。既定値は `subagent.md`・`config.md` のいずれにも数値の記載が見つかっていません（未確認）

## 未確認事項

- Cron自体（`--every`）の最小間隔（確認できたのはインポート経由の60秒下限のみ）
- `spawn_min_memory_gb` の既定値（数値記載なし）
- `agent.subagent_auto_max` の真の既定値（32 vs 16の食い違いは未解消）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/cron/>、<https://kiro.dev/docs/crew/features/task-runner/>、<https://kiro.dev/docs/crew/features/subagents/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>
- Chat（Autopilot）: [03_chat.md](03_chat.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

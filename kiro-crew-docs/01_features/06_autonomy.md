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
**出典**: <https://kiro.dev/docs/crew/features/cron/>（Page updated 2026-10-20）・<https://kiro.dev/docs/crew/features/task-runner/>（Page updated 2026-09-25）・<https://kiro.dev/docs/crew/features/subagents/>（Page updated 2026-09-30）
**出典**（v0.8.0・v0.9.0での変更・S15 の解消・Cron の既定の再確認）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{subagent,taskq,adaptive-concurrency,config,taskrunner,heartbeat,learn-cron-dashboard,cli}.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.8.0・v0.9.0での変更）: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（`agent.subagent_timeout_secs` がダッシュボードから設定できない点の再確認）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

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

> **Autopilot はこの分類には含まれません**。詳細は [03_chat.md](03_chat.md) を参照してください。
>
> - 公式ドキュメント（Sessions ページ Page updated 2026-10-20）は、Autopilot をセキュリティゲートを通過したツール呼び出しを個別の確認なしに進める、セッション単位のトグルと説明しています
> - v0.7.2 以前のリポジトリ仕様書 `modules/autopilot.md` は、Autopilot を、モデルが段階プランを提示し、承認後に Python 制御のステージループが実行する Chat の per-slot モード（`mode == "orchestrator"`）と記述していました
> - v0.9.0 のリポジトリにはこのファイルがありません。`modules/taskq.md` 464行と `modules/subagent.md` 3401-3402行は、これを「retired chat Autopilot」と呼んでいます（`99e6253`）。CHANGELOG の v0.8.0・v0.9.0 節にこの件の告知は見つかっていません
>
> v0.9.0 のリポジトリで plan／approve／stage loop としての Autopilot がどう扱われるかは確認できていません（[未確認事項](#未確認事項)）。
>
> 出典: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-10-20）、`modules/taskq.md`・`modules/subagent.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

## Scheduled: Cron

`kirocrew cron add` でスケジュールジョブを作成します。v0.8.0 以降、この CLI はエージェント・script・command・定期・ワンショットのすべてのジョブを登録できます（[v0.8.0での変更](#v080での変更cron)）。スケジュールは `--every`・`--cron`・`--at` のうちちょうど1つを指定し、`--script`・`--command`・`--agent` は同時に指定できません。

| オプション | 内容 |
|-----------|------|
| `--cron "<expr>"` | 標準cron式（`--every`・`--at` と排他） |
| `--every <secs>` | 秒単位の間隔（`--cron`・`--at` と排他） |
| `--at "<time>"` | ワンショットの実行時刻（公式 cron ページの例は `"tomorrow 9am"`）。`--cron`・`--every` と排他 |
| `--timezone "<tz>"` | ジョブ単位のタイムゾーン（IANA名）。`--cron` と `--at` に適用され、`--every` と併用すると拒否される（`modules/cli.md` 226行）。既定の記述は[下記](#タイムゾーンの既定)を参照 |
| `--skip-dates "YYYY-MM-DD,..."` | 特定日を除外 |
| `--timeout-secs <n>`（`--timeout`） | ジョブごとのタイムアウト（既定1800秒、最大24時間）。`modules/cli.md` 226行は `--timeout` と `--timeout-secs` の両方を挙げる |
| `--agent <name>` | 実行するエージェント |
| `--script FILE.py:FUNC` | script ジョブ。ファイルは事前に `~/.kiro/crew/crons/` 配下に置く必要があり、CLI はコピーしない |
| `--command "<shell>"` | command ジョブ（[制限](#command-cron-の制限)あり） |
| `--model <name>` | 実行に使うモデル（`modules/cli.md` 226行。公式 cron ページの表にはない） |
| `--[no-]persistent-session` | 実行をまたいで1つのセッションを再利用するか。既定は Persistent（[下記](#persistentfresh-セッションの既定)） |
| `--[no-]minimal-context` | 注入コンテキストを省く（[v0.7.0での変更](#v070での変更cronスケジュールジョブ)の Minimal context） |
| `--hide-in-chat` | `modules/cli.md` 226行に記載。公式 cron ページの表にはなく、挙動の説明は両方の出典に見つかっていない |
| `--silent` | ジョブが明示的に通知を送らない限り何も配信しない（公式 cron ページ） |
| `--strict-schedule` | 実行時刻のジッタを無効にする（公式 cron ページ） |
| `--managed-by <key>` | ツールがジョブを所有するためのキー（[v0.9.0での変更](#v090での変更cronスケジュールジョブ)） |

推論を伴わないCronのScript／Commandは**ACPを経由しません**。

出典: <https://kiro.dev/docs/crew/features/cron/>（Page updated 2026-10-20）、`modules/cli.md` 226行（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

### v0.9.0での変更（Cron・スケジュールジョブ）

- **`--managed-by`**: インストーラなどのツールが、所有者キー付きでジョブを登録できます。キーはストア全体で一意で、同じキーでの2回目の `cron add --managed-by` は拒否され、既存のジョブ ID が示されます。置き換え（replace in place）はなく、再インストールはキーを指定した `kirocrew cron remove --managed-by <key>` の後の再登録（新しい ID）です。`--managed-by ""`（空のキー）は拒否されます。キーの書式は ASCII の `[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,199}` です。`cron remove` はジョブ ID か `--managed-by` のどちらか一方を取ります（公式 cron ページ「Let a tool own a job」、`modules/cli.md` 226行、CHANGELOG v0.9.0節 128-129行）
- **失敗した実行の確認（Ask the agent）**: Schedule ページでジョブの **Logs** タブを開くと、各実行が **OK**／**Error**／**Timeout**／**Cancelled** のバッジ付きで並びます。Error または Timeout の実行には **Ask the agent** ボタンが表示され、新しいチャットを開いて、ジョブ ID・run ID・トリガー・開始時刻・実行の要約・実行出力の末尾4,000文字を含むレポートをコンポーザに入れます。ジョブの再実行や再開はしません（再実行は **Run Now** か `kirocrew cron trigger`）。成功とキャンセルの実行にはボタンが表示されません（公式 cron ページ「Inspect a failed run」、CHANGELOG v0.9.0節 122-125行）
- **使用量のフッター**: ダッシュボードでは、cron の実行結果の行にチャットターンと同じ使用量のフッター（経過時間・クレジット・モデル）が付きます。subagent の実行も経過時間の横にクレジットを報告します（公式 cron ページ「Where results go」、CHANGELOG v0.9.0節 116-118行）
- **Persistent の既定の確認**: `kirocrew cron add` が使う `CronService.add_job` の既定は `persistent_session=True`（`minimal_context=False`）です（`modules/cli.md` 226行）。下記「[Persistent／Fresh セッションの既定](#persistentfresh-セッションの既定)」を参照

出典: <https://kiro.dev/docs/crew/features/cron/>（Page updated 2026-10-20）、CHANGELOG.md v0.9.0節（`99e6253`）。

### v0.8.0での変更（Cron）

- **`kirocrew cron add` がすべての種類のジョブを登録する**: script・command・ワンショットのジョブが、ダッシュボードと同じオプションで登録できます（CHANGELOG v0.8.0節 491-492行）。拒否は stderr に出力されて非0で終了し、何も書き込まれません（引数の組み合わせの誤りは 2、検証・セキュリティ・ストアの拒否は 1）。`capabilities.cron` のガバナンスゲートは作成時にも適用され、無効にされた機能のもとで作ったジョブは保存されずに拒否されます（`modules/cli.md` 226行）
- **コマンド cron の実行環境（Linux・macOS）**: `/bin/sh` が Bash の Linux・macOS ホストでも command cron が動きます。CHANGELOG はその理由を、保存済みコマンドのブレース展開が代わりに拒否されるためと記述し、拒否の際は原因がプラットフォームごとに示されます（CHANGELOG v0.8.0節 702-704行）
- **ダッシュボードの cron 操作はダッシュボード所有者に限られる**: スケジュールジョブの編集・実行・確認・キャンセルのルートはダッシュボード所有者を要求し、アプリのトークンは自身のスケジュールジョブだけを管理できます（CHANGELOG v0.8.0節 696-699行）

出典: CHANGELOG.md v0.8.0節（`99e6253`）。

#### Command cron の制限

公式 cron ページ（Page updated 2026-10-20）の記述です。

- command cron は POSIX ホストで `sh -c` を通して実行され、**保存するときと各実行の前に検証**されます
- **拒否されるもの**: コマンド置換・ループ・特殊シェルパラメータ・ANSI-C クォート・ブレース展開。`grep -E '[0-9]'` のようにクォートした正規表現の間隔指定も含まれます
- これらが必要な検査には script cron を使います。基本正規表現では、ダブルクォート内のエスケープしたブレースは使えると記述されています
- 新たに拒否される形の保存済みジョブは、編集するまで実行のたびに失敗します。インポートはそのジョブをスキップして理由を報告します
- command cron は `/bin/sh` が Bash のホスト（Amazon Linux・RHEL・Fedora を含む）でも動きます

### v0.7.0での変更（Cron・スケジュールジョブ）

- **Minimal context**: エージェントジョブの作成・編集ダイアログ（Schedule ページ）の **Minimal context** トグル、または MCP ツールでの `minimal_context: true` で、保存履歴を必要としないジョブの注入コンテキストを省けます。ジョブの指示と必須のメンバー／プロジェクトのガイダンスは残り、エージェントは変わらず、Script ジョブにもなりません（CHANGELOG 256-259行／公式 cron ページ「Minimal context」）
- **`cron-cost-optimize` スキル**: 記録された実行履歴から script／minimal-context／full-context のどれで実行するかを推奨します。**ジョブを自分で変更することはありません**（CHANGELOG 260-262行／公式 cron ページ）
- **スケジュールどおりの発火**: 低頻度のジョブが予定の分に起動する（スキップされない）、各ジョブのスケジュールがそのジョブのタイムゾーンで表示される、persistent なジョブのタブを Schedule ページからチャットフォルダに入れられる、セキュリティゲートがツール呼び出しを拒否したジョブは成功ではなく拒否を報告する、の4点です（CHANGELOG 433-437行）

出典: CHANGELOG.md v0.7.0節（`c67c506`）、<https://kiro.dev/docs/crew/features/cron/>（Page updated 2026-09-25）。

#### タイムゾーンの既定

公式 cron ページ（Page updated 2026-10-20）は `--timezone` の既定を「defaults to global config timezone, then UTC」（グローバル設定のタイムゾーン、未設定ならUTC）と記述し、壁時計の時刻を指定するジョブには常に明示的に `--timezone` を指定するよう案内しています。2026-08-31 更新時点の同ページは「defaults to UTC」と記述していました。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | ジョブ自身のタイムゾーンがない場合 |
> |---|---|
> | 公式 cron ページ（Page updated 2026-10-20。v0.7.2 時点の 2026-09-25 から記述に変更なし） | グローバル設定のタイムゾーン、未設定ならUTC |
> | `learn-cron-dashboard.md` 519行（v0.9.0、`99e6253`。v0.7.2 では 282行） | 「A job without its own timezone retains the published server-timezone fallback」（サーバのタイムゾーンへのフォールバックを維持） |
> | `learn-cron-dashboard.md` 521行（v0.9.0、`99e6253`） | ワンショットの壁時計（`"9am"`・`"tomorrow 17:30"` など）は、呼び出し側がジョブのタイムゾーンを渡した場合はそのタイムゾーン、渡さない場合は「published config timezone」で解決される。夏時間でスキップされる時刻は移動されずに拒否される |
>
> 「グローバル設定のタイムゾーン」「サーバのタイムゾーン」「published config timezone」が同じものを指すかどうかは確認できていません。

#### Persistent／Fresh セッションの既定

**出典間の食い違いは v0.9.0 で解消しました。** `kirocrew cron add` が使う `CronService.add_job` の既定は `persistent_session=True` です（`modules/cli.md` 226行、`99e6253`）。公式 cron ページ（Page updated 2026-10-20）も、`--persistent-session` の説明で「persistent is the stored default」、セッションの節で「**Persistent** (default)」と記述しており、リポジトリと公式の現行の記述が一致しています。

- Fresh（実行ごとに別のセッション）にするには、ダッシュボードか MCP ツールで `persistent_session: false` を設定するか、CLI で `--no-persistent-session` を指定します
- 履歴: 2026-08-31 更新時点の公式 cron ページは Fresh を既定と記述していました。v0.7.2 時点のリポジトリ仕様書（`learn-cron-dashboard.md`）には既定の明記が見つかっていませんでした

出典: <https://kiro.dev/docs/crew/features/cron/>（Page updated 2026-10-20）、`modules/cli.md` 226行（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

### v0.3.0での変更（Cron・スケジュールジョブ）

- **各jobが自身の時間予算を設定できる（最大24時間）**。従来の固定30分上限を置き換えます。jobのinstructionsは50,000文字まで記述できます（CHANGELOG 184行）。**⚠️ これは job（スケジュールジョブ）の時間予算であり、[Subagent](#subagents) の1件あたりハードタイムアウトとは別項目です**（Subagent 側は v0.3.0（`21584ea`）時点では1800秒＝30分でしたが、**v0.6.0 で10800秒＝3時間に変更**されました。[04_reference/05_limits.md](../04_reference/05_limits.md)参照）
- **スケジュールジョブが毎実行ごとに再審査される**。作成時のみでなく発火ごとに現行ポリシーへ照合されるようになり、復元したバックアップが承認システムを迂回してshellコマンドを持ち込むことができなくなりました（CHANGELOG 215行）
- **ジョブのPythonソースをターミナルなしで読める**。ジョブ詳細ビューにハイライト付き・読み取り専用で表示されます（CHANGELOG 186行）

出典: CHANGELOG.md v0.3.0節（`21584ea`）。

> **Cron自体の最小間隔（v0.3.0で確認、v0.9.0で再確認）**: `docs/system-specs/modules/learn-cron-dashboard.md` の「## Cron Service (`cron.py`)」節（236行、v0.9.0、`99e6253`）が、3種のスケジュール方式を「`every` (interval, **min 60s**), `at` (one-shot timestamp), `cron` (5-field expression)」と定義しています（379行。v0.7.2 では 173行（`c67c506`）、v0.3.0（`21584ea`）時点では59行）。あわせて、他エージェントからインポートしたスケジュールにも「整数秒かつ60秒以上」の検証ルールがあります（同ファイル1204行。v0.7.2 では 910-911行、`21584ea` 時点では299行）。
>
> `kirocrew cron add --every` の下限そのものを明記した記述は、`modules/cli.md` 226行と公式 cron ページ（Page updated 2026-10-20）には見つかっていません。`--every` による新規作成に上記の 60秒が適用されるかの扱いは、[04_reference/05_limits.md](../04_reference/05_limits.md) の記述と整っておらず、本サイトでは確認できていません（未確認）。

## Heartbeat（分類外・実在する第6の仕組み）

README の起動モード5分類には無いが、`modules/heartbeat.md` に実在する仕組みです。**分類の差として両方扱います。**

- `kiro_crew/heartbeat.py` が既定60秒間隔で周期的なバックグラウンドタスクを実行
- `~/.kiro/crew/workspace/HEARTBEAT.md` を読み、空でないタスクをエージェントに送信
- タスク1行につき1つ（複数行非対応）。`#` で始まる行・空行・HTMLコメントは無視
- エージェントの応答に `HEARTBEAT_KEEP` が含まれていれば未完了として次のtickまで保持、無ければ完了として削除
- 例外が発生したタスクは自動的に保持（再試行）
- 15tickごとにFTSインデックスを再構築（既定間隔で約15分ごと）
- 無人ターンのため、1タスクあたり1800秒（30分）のタイムアウトがCronの `_JOB_TIMEOUT_SECS` と同じ形で適用される

### v0.9.0での変更（Heartbeat）

本内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG の v0.8.0・v0.9.0 節は説明していません。既定間隔 60 秒・FTS 再構築の 15 tick・タスクのタイムアウト 1800 秒・`HEARTBEAT_KEEP` は v0.7.2 から変わっていません（`modules/heartbeat.md` 5・10・64・147行ほか）。

- **責務の追加**: 仕様書の Responsibilities は、タスク処理・FTS 再構築のほかに、①毎日の保持期間の掃除（`_PRUNE_TICKS` ごと。`memory.history_max_days` に従う履歴の掃除と SEL の掃除）、②アイドルセッションの consolidation（毎 tick）、③回転するメモリのバックアップ（最初の beat と、以降 `_MEMORY_BACKUP_TICKS`＝1440 tick ごと。`memory.backup_enabled` が有効なときだけ実行し、`memory.backup_keep` 個を保持）を挙げています（`modules/heartbeat.md` 9-13行）
- **メモリが所有者の復旧待ちのとき**: Global memory が復旧待ち（`MemoryStartupUnavailable`）の間、beat はアイドルの consolidation とバックアップのスケジュールだけを行い、タスク処理・FTS 再構築・掃除は行いません（同 15行）
- **Heartbeat 用セッションは cycle ごとに破棄される**: cycle の終わりに、セッションがあれば毎回破棄し、次の cycle の最初のタスクが新しいセッションを開始します。コンテキスト使用率はログに残るだけです（同 90-102行）。v0.7.2 の仕様書は、コンテキスト・プロンプト回数が閾値を超えたときだけ破棄すると記述していました
- **cycle 中の追記は保持される**: HEARTBEAT.md に cycle 中に追記したタスクは、ファイルロックのもとで再読込・マージされ、アトミックに置き換えられます。cycle の snapshot にあったタスクの編集・削除だけが上書きされます（同 157行）
- **`chat-N` スロットに配送できないとき**: 解決できないスロットへの配送は破棄され、SEL に `heartbeat_prompt_deliver`（`outcome=not_found`）と警告が記録されます。Slack DM へのフォールバックはありません（同 199行）。v0.8.0 以前の仕様書は「Falls back to Slack DM if slot not found」と記述していました。使用中のスロットへの配送はキューに入ります

出典: `modules/heartbeat.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。v0.7.2 の記述は `c67c506`、v0.8.0 の記述は v0.8.0 タグ（`4d205da`）の同ファイルです。

## Task Runner

仕様ファイルを読み、LLMでステップに分解し、各ステップをACPセッションで実行します。テストによる検証・リトライ・進捗のチェックポイント保存を伴います。

主な機能: 複数タスクの同時実行・対話的なツール承認・ステップごとのセッション分離（全メモリ注入込み）・git連携のステップコミット／リバート・実差分による独立レビュー・循環検出・再起動をまたぐディスク永続化・活動監視ベースの停滞検出・リソース枯渇を防ぐバッチ並列実行。

内部は `taskrunner.py`（オーケストレータ）＋4つのヘルパーモジュール（`task_models.py`／`task_planner.py`／`task_executor.py`／`task_reporter.py`）に分割されています。

### v0.8.0での変更（並列ステップ数）

本内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG の v0.8.0・v0.9.0 節は説明していません。

- **`taskrunner.max_parallel_steps` の既定が `2` から `0`（自動）になりました**。有効な並列ステップ数は `min(taskrunner.max_parallel_steps, ホストの安全上限)` で、安全上限は `compute_memory_sized_parallel_cap` が空きメモリと1エージェントあたりの（学習済みまたは設定済みの）メモリ費用から算出します。結果は `agent.subagent_auto_max` を超えず、3 を下回りません（メモリを読み取れないときは 3）。正の値は並列数を下げる方向にだけ働き、ホストの安全上限を超えることはできません（`modules/taskrunner.md` 624-640行、`modules/config.md` 2700行、`99e6253`）
- v0.7.2 の仕様書は、上限を `compute_max_subagents(cfg)` として `min(taskrunner.max_parallel_steps, compute_max_subagents(cfg))` と記述し、既定を `2` としていました（v0.7.2 `modules/taskrunner.md` 609-616行、`modules/config.md` 1888行、`c67c506`）。v0.8.0 タグ（`4d205da`）の `modules/config.md` 2035行は既に `0`（自動）です
- 理由が仕様書に書かれています: `compute_max_subagents` は v0.9.0 では `agent.subagent_auto_max` そのものを返す天井値になり、メモリは Subagent の起動ごとの床（`agent.spawn_min_memory_gb`）が受け持つ一方、TaskRunner のステップにはそのような起動ごとの床がないため、メモリ算出を残している、と記述しています（`modules/taskrunner.md` 628-634行）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | TaskRunner の並列数 |
> |---|---|
> | 公式 Task Runner ページ（Page updated 2026-09-25。v0.7.2 時点から差分なし） | 依存関係のないタスクは「parallel batches of 3 (`_MAX_PARALLEL_TASKS`)」で並列に走り、現在のバッチが終わってから次が始まる。定数表は `_MAX_PARALLEL_TASKS`＝3（並列バッチ）、`_MAX_CONCURRENT_TASKS`＝3（同時実行 run） |
> | `modules/taskrunner.md` 624-640行・`modules/config.md` 2700行（v0.9.0、`99e6253`） | 上記の `min(taskrunner.max_parallel_steps, ホストの安全上限)`、既定 0（自動）。`_MAX_PARALLEL_TASKS` は v0.9.0 の `docs/system-specs/`・`docs/architecture/` に記述が見つからない。`_MAX_CONCURRENT_TASKS` は `modules/taskrunner.md` 400行に残り、タスク受付ゲートが run の状態を変える前に適用すると記述される（タスク受付を取り付けたときはゲートを省略し、レーンがステップを計量する） |
>
> 公式ページのバッチ実行と、`taskrunner.max_parallel_steps` の関係は確認できていません。

出典: <https://kiro.dev/docs/crew/features/task-runner/>（Page updated 2026-09-25）、`modules/taskrunner.md`・`modules/config.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

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

> **v0.9.0 時点の確認状況**: 本節の出典 `modules/autopilot.md` は v0.8.0 のリポジトリには存在しますが、v0.9.0 のリポジトリには存在しません。`orchestrator.max_plan_duration_seconds`・`orchestrator.stage_timeout_seconds` は、v0.9.0 の `modules/config.md` など `docs/system-specs/` の仕様書に記述が見つかっていません。一方、公式 Configuration ページ（Page updated 2026-10-20）は `orchestrator.max_plan_duration_seconds`（`7200`、「Whole-plan limit for unattended auto-run plans; `0` removes it」）を設定表に記載しており、CHANGELOG v0.6.0節 1409-1411行（`99e6253`）は無人の auto-run plan が2時間で停止すると記述しています。**v0.9.0 でこの上限が有効かどうかは確認できていません（未確認）。** 以下の表は v0.6.0・v0.7.2 時点の記述です。`orchestrator.stage_timeout_seconds` を記述する出典は削除された `autopilot.md` のみで、公式 Configuration ページにも記載がなく、v0.9.0 では未確認です。
>
> 出典: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）、CHANGELOG.md v0.6.0節 1409-1411行（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

**無人の auto-run plan は2時間で停止します（v0.6.0 の記述）。** これは v0.6.0 の破壊的変更です。

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

**並行数の上限（S15）— 出典間の食い違いは v0.9.0 で解消しました**:

- `agent.max_subagents` の既定は **`0`（自動）**、自動サイジングの上限 `agent.subagent_auto_max` の既定は **`32`** です。`modules/subagent.md` 112行と `modules/config.md` 2653-2654行は、いずれも v0.9.0 でこの値を記述しています（`99e6253`）
- 固定の上限（`agent.max_subagents` の正の値）は `3`〜`64` の範囲で読み込まれ、`agent.subagent_auto_max` も `3`〜`64` にクランプされます（`SUBAGENT_AUTO_MAX_CEILING` = 64。`modules/config.md` 2653-2654行・3092行）。正の値を指定すると固定キャップになります
- `max_subagents` が `0` のとき、並行数の上限は `agent.subagent_auto_max` の値そのもの（3 未満にはならない）です。`modules/subagent.md` 144-163行は、この上限をホストメモリから算出しないと記述します。メモリは起動ごとの空き容量の床（`agent.spawn_min_memory_gb`）が受け持ち、床を満たせない起動はキューで待ちます。ホストメモリを読み取れないときの自動上限は `3` です。`agent.spawn_min_memory_gb` を `0` 以下にして床を無効にした場合に限り、自動上限はホストメモリから算出されます（`compute_memory_sized_parallel_cap`）
- 履歴: v0.7.2 以前は `modules/config.md` が `agent.max_subagents` を `= 3`、`agent.subagent_auto_max` を `= 16` と記述し、`modules/subagent.md`（`0` と `32`）と一致していませんでした（v0.7.2 `config.md` 1847-1848行・`subagent.md` 99行、`c67c506`）。v0.8.0 タグ（`4d205da`）の `modules/config.md` 1993-1994行で既に一致しています。CHANGELOG の v0.8.0・v0.9.0 節にこの変更の説明は見つかっていません

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | 並行数の上限の決まり方 |
> |---|---|
> | 公式 Subagents ページ（Page updated 2026-09-30） | 「Crew auto-sizes the concurrent cap from available host memory and CPU. A configured ceiling can narrow it further」（利用可能なホストのメモリと CPU から並行数の上限を自動で決め、設定した天井がさらに狭められる） |
> | `modules/subagent.md` 144-163行（v0.9.0、`99e6253`） | 自動上限は `agent.subagent_auto_max` の値で、ホストメモリから算出しない（床を無効にしたときだけ算出）。メモリは起動ごとの床が受け持つ |

その他の確定事項:

- **1サブエージェントあたりのハードタイムアウト: 10800秒（3時間）**。設定キーは `agent.subagent_timeout_secs`（`subagent.py` の `_TIMEOUT_SECS` がフォールバック）。ロード時に `60`〜`86400` へクランプされ、`0` は既定を使います（`modules/config.md` 2656行・3094行、`modules/subagent.md` 123行、`99e6253`）。**v0.5.0以前は1800秒（30分）の固定値**でした
  - ⚠️ **このキーはダッシュボードから設定できません**。`resource-protection.md` 490-493行（v0.9.0、`99e6253`。v0.7.2 では 424-427行）は「config PUT の allowlist はターン予算と並行数の上限しか含まないため、subagent の期限を上げるには CLI か `config.json` の編集が必要」と述べています。v0.9.0 の CHANGELOG は Subagent Settings が Settings → Agent Harness に移ったと記述しますが（CHANGELOG v0.9.0節 150-153行）、移動後の画面にこのキーの項目があるかは確認できていません（未確認）
  - タイムアウト時のエラー文は `Timed out after 180 minutes`（`subagent.md` 1922行、`99e6253`）。`start_reaper()` が60秒間隔で期限超過のサブエージェントを強制終了します（同2133行）
- 外側のキャップ: セマフォ待機＋注入の最大合計秒数 1200秒（20分。`_ON_DONE_TIMEOUT`）
- 内側のキャップ: `stream_and_collect` 1回あたり900秒（15分。`INJECTION_TIMEOUT`）
- 1サブエージェントあたりのツール呼び出し予算: **既定1000**（`_TURN_LIMIT`。`agent.subagent_max_turns` で変更可能、ロード時に `[1, 1000]` へクランプされるため既定値が上限と同じです）。**v0.6.0以前は既定100**でした（`config.md` 407行「`agent.subagent_max_turns` (100 -> 1000, #12203)」）。公式 Subagents ページも「up to 1000 tool calls」と記述します
  - 出典: `config.md` 2655行・`subagent.md` 124行・`resource-protection.md` 18行（`99e6253`）
- 下限3（自動上限の下限、固定上限の下限）。**サブエージェントからさらにサブエージェントを起動できるかは確認できていません**（未確認）。`modules/subagent.md` 126行は `_SYSTEM_PREFIX` を「Injected before task text to prevent spawn recursion」と記述する一方、同 573-581行・2864行と `modules/config.md` 2672行（`agent.child_reserve`）は、ネストした起動（nested task）を前提にした記述を持ちます。両者の関係は精査できていません
- 空きメモリの admission gate（`agent.spawn_min_memory_gb`）は、Linux では cgroup の余裕量、macOS と Windows ではネイティブのメモリ読み取りを使います。**ホストのメモリも有限の cgroup 上限も読み取れないときに限って fails open**（チェックをスキップして起動を許可）します（`subagent.md` 238-242行、`99e6253`）。**v0.6.0 では `/proc/meminfo` を読むため Linux のみ有効で、非Linuxでは fails open** でした（v0.6.0 `subagent.md` 52-55行、`8575209`）。本内容は v0.7.0 以降のタグの仕様書で確認したもので、CHANGELOG には記載が見つかっていません。**`agent.spawn_min_memory_gb` の既定は `2.0`（GiB）** です（[v0.8.0での変更](#v080での変更subagentメモリ委任)）

### v0.9.0での変更（Subagent）

本節の仕様書の記述は v0.9.0 タグで確認したもので、CHANGELOG の v0.9.0 節が説明しているのは停滞した子の項目だけです（それ以外は CHANGELOG 本文は説明していません）。

- **停滞した子が親へのユーザーメッセージを保留しなくなった**: 実行中の subagent が `agent.subagent_stall_idle_secs`（既定 `120` 秒）のあいだストリームの動きがないと、実行中カードに **stalled** と表示されます。バッジが何かを終了させることはありません。v0.9.0 では、stalled の子が親のユーザーメッセージを保留しなくなり、新しい送信はそのまま処理されます（`modules/subagent.md` 125行、CHANGELOG v0.9.0節 162-164行）。1件あたり3時間の既定のハードタイムアウトは引き続き適用されます
- **一括起動の件数の上限**: `spawn_run` の `tasks` と `agents` は、それぞれ最大 **128 件**（`SPAWN_BATCH_MEMBERS_MAX`）です。上限を超える呼び出しは、状態を作る前にスキーマで拒否されます（`modules/subagent.md` 3112行・3259行）。v0.7.2・v0.8.0 タグの `subagent.md` にこの記述は見つかっていません
- **`agent.subagent_spawn_stagger_secs` の既定**: v0.9.0 の `modules/config.md` 633行は、既定が `2.0` から `0.25` に変わったと記述し、`modules/subagent.md` 810行は `0.25` を既定と記述しています。v0.8.0 タグの `modules/config.md` にこの行は見つかっていません。空いた容量は、起動を一斉に行わず、この間隔ごとに埋まります
- **Subagent Settings の移動**: CHANGELOG v0.9.0節 150-153行は、Subagent Settings と Warm Pool が Settings → Agent Harness に移ったと記述しています（画面名の変更は [Subagents](#subagents) の `agent.subagent_timeout_secs` の項を参照）

出典: `modules/subagent.md`・`modules/config.md`、CHANGELOG.md v0.9.0節（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

### v0.8.0での変更（Subagent・メモリ・委任）

CHANGELOG v0.8.0節 673-679行は、メモリが逼迫したときの subagent の扱いを次の趣旨で記述しています: 起動は「起動後に 2 GB が残る場合」に許可される（以前は 4.5 GB の空きを要求していた）、親のランタイムを共有するかどうかで価格が決まる、Mac ではカーネルがメモリ圧迫を報告している間も待つ（キューのチップが理由を示す）、負荷で切り下げられた並行上限はホストがアイドルになると戻る。以下の個別の数値と挙動は、v0.9.0 タグの仕様書で確認したもので、CHANGELOG 本文は説明していません。

**起動前の空きメモリの床（`agent.spawn_min_memory_gb`）**

- 既定は **`2.0`（GiB）** で、起動を許可した**後にも**空いていなければならないメモリ量です。`0` にすると床・予約・ホストメモリの読み取りがまとめて無効になります（`modules/subagent.md` 114行・246-248行）。`modules/config.md` 623行は旧既定を `4.0` と記述し、保存済みの `4.0` を一度だけ新しい既定へ書き換える扱い（`adopts`）の表に載せています。CHANGELOG は旧要求を 4.5 GB と記述しており、4.0 と 4.5 の違いを両ファイルは説明していません（未確認）
- 床を満たせない起動はキューで待ちます（`low_memory`）。待機は `agent.admit_wait_secs`（既定 `30` 秒、`[1, 3600]`）ごとに再確認され、`agent.subagent_queue_max_wait_secs`（既定 `1800` 秒、`[0, 86400]`、`0` は上限なし）を超えると「never started: waiting for memory」で終了します（`modules/config.md` 2664-2665行）
- 既定の設定で何も暖機・学習していないとき、起動に必要な空きメモリは、親のランタイムを共有する起動が **2.65 GiB**、最初の専用起動が **3.0 GiB**、最初の起動の暖機中に重なる専用起動が **4.0 GiB**、親のランタイムを共有する入れ子の起動が **2.0 GiB** です（`modules/subagent.md` 353-356行）
- **macOS のカーネルのメモリ圧迫ホールド**: 床が有効で、カーネルの `kern.memorystatus_vm_pressure_level` が WARN または CRITICAL を示し、このゲートウェイの専用ランタイムが実行中または暖機中のとき、ルートの起動は待ちます。キューのチップが理由を示します（`modules/subagent.md` 583-600行）。macOS のみの挙動です

**適応的並行の挙動（v0.7.2 からの変更）**

- 実効的な並行上限は、天井（`agent.max_subagents`。自動のときは `agent.subagent_auto_max`）から**始まり**、天井は書き換えません。上限を切り下げるのは**失敗が続く作業**だけで、半減し、問題のない期間ごとに1段ずつ戻ります。切り下げの信号は、プロバイダの 429、帰属できるタイムアウト、遅いまたは失敗する MCP サーバ、fd・プロセスの枯渇です（`modules/adaptive-concurrency.md` 3-13行・17-31行）
- v0.7.2 の仕様書にあった、ゲートウェイのループ遅延やメモリによる実行上限の切り下げと、メモリが臨界のときのディスパッチの一時停止は、v0.9.0 の仕様書では実行上限に使われません。メモリは起動ごとの床が受け持ちます。メモリが臨界のときの一時停止と再開（pause／probe）が残っているのは、MCP gateway の spawn gate の系列だけで、実行上限と実行中の作業には影響しません（同 17-31行・136-138行）
- 切り下げられた上限は、需要も作業の信号もない状態が 60 秒続くと1段ずつ戻ります（`DEFAULT_IDLE_RECOVERY_SECS`。同 134行）
- `agent.adaptive_initial` は保存・読み込みされますが、実行上限は天井から始まるため効果がありません（同 156-160行、`modules/config.md` 2678行）。`agent.adaptive_concurrency`（既定 `true`）・`agent.adaptive_concurrency_mode`（既定 `"aimd"`。`"fixed"` で天井に固定）・`agent.adaptive_floor`（既定 `1`）・`agent.adaptive_slow_start`（既定 `true`）は変わっていません（`modules/config.md` 2675-2679行）
- 公式 Subagents ページ（Page updated 2026-09-30）は、v0.7.2 時点から差分がなく、自動サイジングの上限を「available host memory and CPU」から決めると記述しています。`modules/subagent.md` 144-163行はホストメモリから算出しないと記述しており、[Subagents](#subagents) の表に両方を示しています

**委任の方針（Delegation policy／Delegation gate）**

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | 1タスクの委任 |
> |---|---|
> | 公式 Subagents ページ（Page updated 2026-09-30。v0.7.2 時点から差分なし） | `spawn_run` は、別のエージェント・モデル・Crew の指定か、`parent_parallel`／`bulk_data`／`fresh_context`／`specialist`／`user_requested` のいずれかの理由がない1タスクの委任を拒否する |
> | `modules/subagent.md` 3134-3146行（v0.9.0、`99e6253`） | 委任方針は prompt の指針だけで、1タスクの呼び出しを拒否する実行時のゲートはない。1タスクの呼び出しごとに、許可のみの SEL 記録 `operation="spawn.solo"` を書く。`solo_reason`／`solo_details` は検証を通過するが無視される。新しい spawn は run 記録の `delegation` を設定しない（既存の記録にあるものは保持） |
> | CHANGELOG v0.8.0節 588-590行 | 1タスクの委任に理由を要求する拒否はなくなった |

出典: CHANGELOG.md v0.8.0節、`modules/subagent.md`・`modules/adaptive-concurrency.md`・`modules/config.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）、<https://kiro.dev/docs/crew/features/subagents/>（Page updated 2026-09-30）。

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
> | 公式 Subagents ページ（Page updated 2026-09-30。v0.7.2 時点から差分なし） | 「Under memory pressure, a spawn is refused as back-pressure」（back-pressure として**拒否**される。再試行すべき一時的なエラーではなく、軽い手段を選ぶ合図） |
> | `modules/taskq.md` 9-12行・`modules/subagent.md` 252-259行（v0.9.0、`99e6253`） | 床（`agent.spawn_min_memory_gb`）を満たせない起動は、永続行の有無によらずキューで待ち（`low_memory`）、容量の判定では失敗しない。永続行がない起動（Incognito・Temporary、`agent.task_queue_enabled=false`）はメモリ上のウィンドウで待つ。待機の上限は `agent.subagent_queue_max_wait_secs`（既定 `1800` 秒）。拒否のまま残るのは、ガバナンス・cwd・メモリ識別の検査と、永続行を書けない場合（`task_store_unavailable`） |

v0.7.2 の仕様書（`taskq.md` 9-10行・`subagent.md` 308-311行、`c67c506`）は、永続行がある場合は延期し、永続行がない場合は従来どおり拒否すると記述していました。v0.9.0 の記述との関係は、[v0.8.0での変更（Subagent・メモリ・委任）](#v080での変更subagentメモリ委任)を参照してください。

**適応的並行（adaptive concurrency）**

- `agent.max_subagents`（または自動サイジングされた値）を**上限（天井）として書き換えずに**、その下で実効的な並行上限（effective cap）を動かします。**小さくなった上限に合わせて実行中の作業を止めることはありません**（`adaptive-concurrency.md` 3-11行）。v0.7.2 の仕様書は、実効上限が `min(上限, 4)` から始まり、ホストの逼迫が裏付けられると半減し、深刻な逼迫ではディスパッチを一時停止して1件の試行で再開すると記述していました。**v0.9.0 の挙動は[v0.8.0での変更](#v080での変更subagentメモリ委任)の記述に置き換わっています**
- 設定キー（すべて再起動なしで反映）: `agent.adaptive_concurrency`（**既定 `true`**。`false` でユーザー設定の上限のみ）、`agent.adaptive_concurrency_mode`（**既定 `"aimd"`**。`"fixed"` で上限を固定）、`agent.adaptive_floor`（既定 `1`）、`agent.adaptive_initial`（v0.7.2 の仕様書では既定 `4`、起動時の実効上限。**v0.9.0 の `modules/config.md` 2678行は、このキーを効果のない（inert）キーと記述しています**）（v0.7.2 の `adaptive-concurrency.md` 211-218行・`config.md` 1864-1865行、`c67c506`）
- **`resource_status`**: 実際に適用中の並行上限（設定上の最大値との対比）、利用可能メモリ、CPU 負荷、現在の posture を報告します。**助言（advisory）であり、何も予約しません**。posture が `tight` または `critical` のときは並列数を減らすか重い処理を後回しにするよう公式は案内しています（公式 Subagents ページ「Limits and host capacity」／CHANGELOG 438-441行）

**委任のゲート（Delegation gate）**

- 公式 Subagents ページ（Page updated 2026-09-30）は、`spawn_run` が理由を示さない**単一タスクの委任を拒否**すると記述しています。別のエージェント・モデル・Crew を指定するか、次のいずれかの理由が必要です: `parent_parallel`（親が別の作業を並行して進める）／`bulk_data`（大きな入力の分離した要約）／`fresh_context`（現在の推論を引き継がない独立レビュー・再現）／`specialist`（親にない能力）／`user_requested`（ユーザーが明示的に依頼）
- モデル値 `auto` は「別モデル」の根拠になりません。理由は run の記録に**モデルの主張として**残り、認可の証明としては扱われません（公式 Subagents ページ「Delegation gate」／CHANGELOG v0.7.0節 438-441行）
- v0.8.0 以降のリポジトリ側の記述は、[v0.8.0での変更（Subagent・メモリ・委任）](#v080での変更subagentメモリ委任)の「委任の方針」を参照してください

**run 操作のスコープ**

- エージェントが使う run 操作（list・inspect・steer・continue・retry・release・delete）は、**その Subagent を開始したセッション自身の run に限られます**。すべての run を操作できる所有者の画面はダッシュボードの **Activity** パネルです。セッション ID を持たない内部の呼び出し元は、親のない CLI run だけを扱えます。セッションが ID の欠落を報告した場合は `kirocrew doctor` を実行します（公式 Subagents ページ「Stopping and retrying」（Page updated 2026-09-30）、`modules/subagent.md` 1860行・1875-1876行、`99e6253`。v0.7.2 では 672行）

出典: <https://kiro.dev/docs/crew/features/subagents/>（Page updated 2026-09-30）、CHANGELOG.md v0.7.0節（`c67c506`）、`docs/system-specs/modules/{taskq,adaptive-concurrency,config,subagent}.md`（`c67c506`）。

### v0.3.0での変更（Subagent・メモリガバナー）

- **Subagentが主エージェントと同様に承認を求める**。subagentの承認要求が trust／auto-approve／プロンプトのいずれかを通るようになり、従来のように要求がドロップされて子プロセスが固まることがなくなりました（CHANGELOG 193行）
- **メモリが致命的に少ないときの挙動が定義された**（メモリガバナー）。スケジュールジョブは延期され、新規subagentは拒否されます。ヘッダに現在の姿勢（posture）が表示されるため、重い作業が失敗する前に把握できます（CHANGELOG 181行）
- **メモリ上限が全同時エージェントの合計に適用される**。上限が同時実行中の全エージェントにまとめて適用されるようになり、小さなspawnを多数行ってホストのメモリを食い潰すことができなくなりました（CHANGELOG 218行）

出典: CHANGELOG.md v0.3.0節（`21584ea`）。

## 未確認事項

- v0.9.0 のリポジトリで Autopilot（plan／approve／stage loop）がどう扱われるか（v0.9.0 の仕様書は「retired chat Autopilot」と呼ぶだけで、CHANGELOG の v0.8.0・v0.9.0 節に告知が見つかっていない。公式 docs はセッション単位のツール自動承認トグルとして記述している。[起動モード5分類](#起動モード5分類)の注記を参照）
- `orchestrator.max_plan_duration_seconds` が v0.9.0 で有効かどうか（公式 Configuration ページ（Page updated 2026-10-20）は設定表に記載しているが、v0.9.0 の仕様書に記述が見つかっていない。[v0.6.0での変更](#v060での変更無人-auto-run-plan-の時間上限)の注記を参照）と、`orchestrator.stage_timeout_seconds`（記述する出典は削除された `autopilot.md` のみ）
- `spawn_min_memory_gb` の旧既定の食い違い（`modules/config.md` 623行は `4.0`、CHANGELOG v0.8.0節 673-675行は 4.5 GB の空きを要求していたと記述。両ファイルは違いを説明していない）
- サブエージェントからさらにサブエージェントを起動できるか（上記 [Subagents](#subagents) の「下限3」の項を参照。`modules/subagent.md` の `_SYSTEM_PREFIX` の記述とネストした起動を前提にした記述の関係を精査できていない）
- 公式 Task Runner ページの並列バッチ（`_MAX_PARALLEL_TASKS`）と `taskrunner.max_parallel_steps` の関係、および `_MAX_CONCURRENT_TASKS` と同時実行 run 数の関係（[v0.8.0での変更（並列ステップ数）](#v080での変更並列ステップ数)参照）
- Cron のタイムゾーン既定（公式 cron ページとリポジトリの `learn-cron-dashboard.md` の食い違いは継続。[タイムゾーンの既定](#タイムゾーンの既定)参照）
- メモリ逼迫時の spawn が拒否か延期か（公式 Subagents ページとリポジトリの仕様書の食い違いは継続。[v0.7.0での変更（Subagent）](#v070での変更subagent永続タスクキュー適応的並行)の表を参照）
- 1タスクの委任の拒否（Delegation gate）が実行時にあるか（公式 Subagents ページとリポジトリ・CHANGELOG の食い違い。[v0.8.0での変更（Subagent・メモリ・委任）](#v080での変更subagentメモリ委任)の表を参照）
- 自動サイジングの根拠（公式 Subagents ページは「ホストのメモリと CPU から決める」、`modules/subagent.md` 144-163行は「ホストメモリから算出しない」）
- `--hide-in-chat` の挙動（`modules/cli.md` 226行に記載があるが、挙動の説明が公式 cron ページ・仕様書のいずれにも見つかっていない）
- `--every` の下限 60 秒が `kirocrew cron add` にも適用されるか（上記「Cron自体の最小間隔」の注記を参照）

> **解消済み**:
>
> - 「Cron自体（`--every`）の最小間隔」: `21584ea`の`learn-cron-dashboard.md` 59行で**60秒**と確認できたため未確認事項から除きました（上記「Scheduled: Cron」節参照）。v0.7.2（`c67c506`）・v0.9.0（`99e6253`、379行）でも同じ記述です
> - `agent.max_subagents`（`0`）・`agent.subagent_auto_max`（`32`）の既定値の食い違い（S15）: v0.9.0 の `modules/config.md` と `modules/subagent.md` が一致しました（v0.8.0 タグで既に一致）
> - `agent.spawn_min_memory_gb` の既定値: `2.0`（GiB）です（`modules/subagent.md` 114行、`modules/config.md` 623行、`99e6253`）
> - Cron の `persistent_session` の既定値: リポジトリ（`modules/cli.md` 226行）と公式 cron ページ（Page updated 2026-10-20）がいずれも Persistent を既定と記述しています（[Persistent／Fresh セッションの既定](#persistentfresh-セッションの既定)参照）
> - Task Runner・Workflow のキュー行の扱い: `modules/taskq.md` 31-40行は、TaskRunner のステップと workflow agent 呼び出しの行は共有の `RunnerAdmission` が書き、再起動後は reconciler が付ける `awaiting_adapter` を、TaskRunner／WorkflowService の採用処理（`adopt_orphaned_rows`。同 1355-1363行）が再開すると記述しています。`awaiting_adapter` は復旧の引き継ぎ用の印で、本来のディスパッチ経路ではないと記述されています（v0.7.2 の「not yet dispatched」の文言は v0.9.0 の `taskq.md` に見つかっていません）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/cron/>、<https://kiro.dev/docs/crew/features/task-runner/>、<https://kiro.dev/docs/crew/features/subagents/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>
- リポジトリ（永続タスクキュー・適応的並行）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/taskq.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/adaptive-concurrency.md>
- Workflows（永続化されたワークフロー呼び出し）: [17_workflows.md](17_workflows.md)
- Chat（Autopilot）: [03_chat.md](03_chat.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

# 上限値・既定値の一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: 各ページに記載の一次情報を集約（詳細出典は各節を参照。主要な一次情報は <https://kiro.dev/docs/crew/> と <https://github.com/kirodotdev/KiroCrew>）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [リポジトリ・公式サイト](#リポジトリ公式サイト)
- [セキュリティ](#セキュリティ)
- [メモリ](#メモリ)
- [自律実行](#自律実行)
- [App・インターフェース](#appインターフェース)
- [テレメトリ](#テレメトリ)
- [未確定（両併記）](#未確定両併記)
- [未確認事項](#未確認事項)

---

## リポジトリ・公式サイト

| 項目 | 値 |
|------|-----|
| 公式docsのcrewページ数 | **49** |
| リポジトリ`docs/`配下ファイル数 | **349**（v0.9.0タグ。v0.8.0タグは298、v0.7.2タグは281） |
| リポジトリ`docs/system-specs/`配下ファイル数 | **107**（`.md` は104。v0.7.2タグは104で、`modules/autopilot.md` が消滅し4ファイルが新規） |
| 最新安定版 | **v0.9.0** |
| 安定版リリース数 | **15**（v0.1.0〜v0.9.0） |
| 総リリース数（プレリリース含む） | **95**（プレリリース79件。版番号でない Release `ffmpeg-decoder-7.1.1-r1` が1件。2026-10-25 取得時点の GitHub Releases 実測） |
| CHANGELOG.mdの版節数 | **13** |
| ライセンス | **Apache-2.0**（本サイトはMIT） |

> **`[Unreleased]` 節について**: 固定参照時点（版 v0.9.0）の `CHANGELOG.md` に `## [Unreleased]` 節は**存在しません**（実測0件。v0.8.0・v0.7.2・v0.6.0 も0件）。`docs/build/changelog.md` 23行は「There is no `## [Unreleased]` section, and the gate refuses one.」と明記し、gateの実体は `scripts/check_changelog_history.py` です。したがって上の版節数13に `[Unreleased]` は含まれません。**節が復活した場合は出典から除外する方針を維持します**（[02_update/02_release-policy.md](../02_update/02_release-policy.md)参照）。
>
> **プレリリースの連番について**: 最大番号は件数と一致しません（例: `v0.5.0-insider.4`・`v0.6.0-insider.5` が欠番。v0.7.x 系・v0.8.0 系・v0.9.0 系にも欠番あり）。詳細は [02_update/02_release-policy.md](../02_update/02_release-policy.md) を参照してください。

## セキュリティ

| 項目 | 値 |
|------|-----|
| 拒否コマンドルール件数 | **未確認**（公式 security・hooks ページと仕様書の v0.9.0 時点の記述に、件数の記載がありません。仕様書は件数を文書に書かない方針で、実行時の `GET /api/security/posture` で導出すると記述。旧版の記載値は 137。経緯は [09_security.md](../01_features/09_security.md#8つの保護機構公式の順序)） |
| サンドボックスの値域（`agent.sandbox`） | **`auto`（既定）／`strict`／`off`**。`strict` を運用者の設定値にしたのは v0.8.0。公式 security・configuration ページ、`config.md` 2648行、`security-deep-dive.md` 96-100行が一致し、**v0.7.2 以前の3系統の食い違いは解消**。内部ティア `standard`（`auto` の解決先）と `cc` は運用者が書く値ではない。ガバナンスの `sandbox.min_level` 順序尺度は `("off", "standard", "cc", "strict")`（[09_security.md](../01_features/09_security.md)参照） |
| `strict` が隠す対象 | 出典ごとに記述が異なる（公式 security ページ、`security.md` 727行、`config.md` 2648行、`install.md` 949-959行、CHANGELOG v0.8.0節。**裁定しない**。[09_security.md](../01_features/09_security.md)の表を参照） |
| 既知のギャップ | **8点**（＋プラットフォーム依存のリソース上限）。8点目「Design Critique の capture browser におけるクロスオリジン・サブリソースの DNS rebinding」は v0.9.0 で追加（`security-deep-dive.md` 713行）。7点目「同一ユーザーによるランチャの自己汚染は受容・非防御」は v0.7.0 で追加（[09_security.md](../01_features/09_security.md)参照） |
| `mcp.honour_auto_approve` | 既定 **`true`**。変更後は Gateway の再起動が必要（`config.md` 2547行、公式 configuration ページ）。オーナーが書いた `autoApprove` 一覧のツールは承認カードと Crew のツールゲートを迂回（v0.8.0） |
| データホームのファイル権限 | ファイル `0600`・ディレクトリ `0700`（v0.9.0。既存ストアは起動時にスイープ。時間30秒・エントリ数1,000,000の上限。`security.md` 2198-2260行） |

## メモリ

| 項目 | 値 |
|------|-----|
| メモリ層数 | リポジトリ資料: **6層**（Preferences/Projects/Recent history/Semantic/Episodic/Lessons）＋横断帯（request auth / Slack owner lock / governance ceiling / SEL audit）。公式docs: **8機構**。単一の層数には裁定しない |
| コンテキストバジェット | **33,000文字**（リポジトリ `_CONTEXT_BUDGET_BASE` の固定値。v0.7.0〜。v0.6.0以前は165,000文字）。⚠️ 公式 memory ページの図は「Context Window (~55K tokens)」のままで、**出典間で食い違います**（下記「[未確定（両併記）](#未確定両併記)」） |
| Preferencesキャップ | 4,250文字（公式ページ値。v0.6.0のリポジトリでは fraction 由来の4,290文字=`int(165,000×2.6%)`） |
| Projectsキャップ | 6,400文字（公式ページ値。v0.6.0のリポジトリでは6,435文字=`int(165,000×3.9%)`） |
| Recent historyキャップ | 26,600文字（公式ページ値。v0.6.0のリポジトリでは26,400文字=`int(165,000×16%)`） |
| Semantic memoryキャップ | 12,000文字（公式ページ値。v0.6.0のリポジトリでは12,705文字=`int(165,000×7.7%)`） |
| Episodic memoryキャップ | 3,000文字・上位8件（`_EPISODIC_INJECT_CAP`。基礎キャップの`_EPISODIC_MEMORY_CAP`はSemantic memoryと同じ7.7%=12,705文字だが、実際の注入時はこの3,000文字にさらにクランプされる） |
| Lessonsキャップ | 37,250文字・最大50件（公式ページ値。最大50件は公式ページのみの記載で、仕様書での裏付けは未確認）。リポジトリでは起動時ルールブロックの上限 `_LESSONS_STARTUP_CAP` = **37,000文字**（33,000文字の割合ではない独立値）。`applies: on_topic` の lesson は別ブロック `[Learned experience]`（基準の5%）に入る |
| 1ターンの lesson 追加（`memory.inject_lessons_per_turn`） | 既定 **`false`**。有効時は最大3件・合計2,000文字（`memory-skills-hooks.md` 6130行。公式 docs と CHANGELOG に記載なし） |
| 統合1回の抽出上限 | セマンティック20件・エピソディック10件・暗黙の lesson 10件（`memory-skills-hooks.md` 386-390行） |
| メモリの書き込み・注入スイッチ（v0.8.0） | `memory.persistence_enabled`・`memory.inject_memory`・`memory.inject_lessons`・`memory.inject_activity` はいずれも既定 **`true`** |
| V1 の承認済みスナップショット | 1レコードあたり直近20件（V2 は自動の保持上限なし）。メモリ編集 API の一覧は1ページ50件（`limit` は1〜100）、`refresh` は最大500件、一括は明示指定500件／条件一致10,000件・32 MiB（`memory-skills-hooks.md` 5996-6060行） |
| ピン留めスキル本文 | 合計 **99,000 UTF-8バイト**（`PINNED_SKILL_BODIES_CAP`）。確認済みプロジェクトスキル本文は別枠の24,750文字。`skill_search` の `read` は1回99,000 UTF-8バイト |
| フォルダの Additional steering | 1フォルダ最大16件、1エントリ4,096文字（`config.md` 352-408行） |
| Knowledge の抽出プール | `knowledge.pool_idle_ttl_secs` 既定 300秒（`0` で無効）、`knowledge.extraction_effort` 既定 `high`（仕様書のみの記載） |
| observe モードの履歴（Slack） | 200件・1週間（`slack.observe_max_messages`・`slack.observe_ttl_hours` で設定可）。observe 以外は50件・5分 |
| hooks のイベント数 | 自動で発火する5＋Kiro Agent 由来のテスト専用6＝登録可能11（`memory-skills-hooks.md` 5643-5645行） |

> **v0.7.0 以降のリポジトリのキャップについて**: `memory-skills-hooks.md` 6135行（`99e6253`。v0.7.2 では 4582行）は、`_CONTEXT_BUDGET_BASE` を「a fixed 33,000-character Crew background admission allowance」と説明し、モデルのウィンドウサイズや `skills.lazy_load` で拡大しないと記述しています。lessons の予算は「22.6% of the 33,000 base」（同3377行。v0.7.2 では 2782行）です。v0.6.0 で記載していた 165,000 文字基準の fraction 由来値（4,290／6,435／26,400／12,705／37,290）は v0.7.2 以降の仕様書にはありません。公式 memory ページ（Page updated 2026-10-20。図の見出しと各キャップ値は v0.6.0 から変わっていません）のキャップ値は変わっていません。**本サイトはどちらが正かを裁定しません。**
>
> スレッド履歴の許容量は、仕様書が 200K／1M ウィンドウで 6,930／34,650文字（`memory-skills-hooks.md` 6190-6193行）、公式 memory ページが「45,000 chars」と記述しており、別の数値です。本サイトは裁定しません。

| 項目 | 値 |
|------|-----|
| 履歴減衰の段数 | **5段**（0-13日／14-60日／61-180日／181-364日／365日以降） |
| Consolidationトリガー（好み/プロジェクト） | **30メッセージ** |
| Consolidationトリガー（履歴/レッスン） | **3時間アイドル** |
| 埋め込み（Memory・Knowledge Library共有） | vendored llama-cpp-python（常時オン・in-process。`llama_cpp`固定。`get_shared_embedder()`でMemoryとKnowledge Libraryが共有）。**v0.6.0で `knowledge.md` も `InProcessEmbedder` に更新され、Ollama依存の旧記述は解消**。詳細: [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md) |

## 自律実行

| 項目 | 値 |
|------|-----|
| Cron: `--timeout-secs` 既定 | 1800秒（`1〜86400`） |
| Cron `--every` の一般下限 | **未確認**（60秒はimport取込下限およびHeartbeat間隔として確認済みだが、一般的な`--every`下限としては裁定しない） |
| Cronインポート時の最小間隔 | 60秒以上（整数秒。他エージェントからのインポート時の検証ルール） |
| **job（スケジュールジョブ）の時間予算** | **最大24時間**（v0.3.0で追加。従来の固定30分上限を置き換え。**下記「Subagent 1件あたりのハードタイムアウト」とは別項目**） |
| **job のinstructions文字数** | **50,000文字**（v0.3.0で追加） |
| TaskRunnerの構造 | オーケストレータ＋4ヘルパーモジュール |
| `taskrunner.max_parallel_steps` | 既定 **`0`（自動。ホストのメモリから算出した上限）**。正の値はその上限を下げるだけ（`config.md` 2700行。v0.7.2 以前は `2`） |
| **無人 auto-run plan の時間予算** | **7200秒（2時間）**（v0.6.0で追加。`orchestrator.max_plan_duration_seconds`）。⚠️ 根拠は CHANGELOG v0.6.0節 1409-1411行と公式 configuration ページ（Page updated 2026-10-20）101行のみで、仕様書側の根拠 `autopilot.md` は v0.9.0 に存在しません（v0.8.0 まで存在）。**v0.9.0 で有効かどうかは未確認**。「stage-gatedな planは打ち切られない」の根拠も v0.9.0 では確認できません |
| **チャット1ターンの上限** | **14400秒（4時間）**（`agent.chat_turn_timeout_secs`。v0.5.0以前は7200秒。クランプ300〜86400秒・無効化不可） |
| Subagent 1件あたりのハードタイムアウト | **10800秒（3時間）**（`agent.subagent_timeout_secs`。**v0.5.0以前は1800秒＝30分の固定値**。クランプ60〜86400秒。**ダッシュボードからは設定不可**） |
| Subagentの外側キャップ | 1200秒（20分。`_ON_DONE_TIMEOUT`） |
| Subagentの内側キャップ | 900秒（15分。`INJECTION_TIMEOUT`） |
| Subagent 1件あたりのツール呼び出し予算 | 既定 **1000**（`agent.subagent_max_turns`。**v0.7.0で100→1000**）。ロード時クランプの上限は1000（v0.5.0以前は200）。キー未設定なら自動で1000に追従し、保存済みの値は100でも保持される（[02_configuration-keys.md](02_configuration-keys.md)参照） |
| Subagent並行数（`agent.max_subagents`／`agent.subagent_auto_max`） | 既定 **`0`（自動）／`32`**。固定ピンのロード範囲・自動上限のクランプはいずれも `[3, 64]`（`config.md` 2653-2654行・3092行、`subagent.md` 112行。**v0.7.2 以前の `config.md` の値 `3`／`16` との食い違いは解消**） |
| Subagent並行数の下限 | 3 |
| `agent.spawn_min_memory_gb` | 既定 **`2.0`**（GiB。旧既定 `4.0`、CHANGELOG v0.8.0節は旧要求を 4.5 GB と記述。4.0 と 4.5 の差の説明はなし）。`0` で床・予約・ホスト読み取りを無効化（`subagent.md` 114行、`config.md` 623行） |
| 起動に必要な空きメモリ（既定・暖機なし） | 共有ランタイム **2.65** GiB／最初の専用 **3.0** GiB／暖機中に重なる専用 **4.0** GiB／入れ子で共有 **2.0** GiB（`subagent.md` 353-356行） |
| 起動待ちの上限 | `agent.subagent_queue_max_wait_secs` 既定 **1800秒**（`[0, 86400]`、`0` は上限なし）、`agent.admit_wait_secs` 既定 **30秒**（`config.md` 2664-2665行） |
| `spawn_run` の件数 | `tasks`／`agents` 各最大 **128件**（`subagent.md` 3112・3259行） |
| `agent.subagent_spawn_stagger_secs` | 既定 **`0.25`**（旧 `2.0`。`config.md` 633行） |
| `agent.adaptive_initial` | **効果なし**。実効上限は天井値から始まり、失敗する作業が続いたときだけ半減（`adaptive-concurrency.md` 17-31・157-160行） |
| `monitoring.max_runtime_secs` | 既定 **604800秒（7日）**、新規または更新する監視の上限は最大30日（公式 configuration ページ、`monitor-architecture.md` 222-246行） |
| `session.compact_wait_secs` | `0` は既定の **300秒**、設定時は **60〜3600秒**（公式 configuration ページ 44行） |
| `session.watchdog_rss_max_mb` | 既定 **`0`（無効）**。v0.7.0〜v0.8.0 は `1536`、v0.9.0 で `0` に戻った（`config.md` 634行・2696行。CHANGELOG と Release 本文に説明なし）。`0` でも内部バックグラウンドランタイムは 1536 MiB で再生成 |
| ウォッチドッグの時間 | `watchdog.stale_window_secs`／`model_silent_probe_secs`／`tool_stall_suspect_secs`／`tool_stall_hard_cap_secs` は v0.7.2 で 300／900／3600／3600秒、v0.9.0 で **600／1800／5400／7200秒**（`config.md` 637-640行、`acp-client.md` 1627-1630行） |
| ワークフロー（v0.7.2 以前から同値） | run の実時間 3600秒（`agent.workflow_run_timeout_secs`、`[60, 21600]`）、run あたり `ctx.agent()` 1000、ステップあたりツール呼び出し 200、スクリプト 262144 バイト、追跡 run 200、エージェント並行 4 固定（`workflows.md` 558-575・1438-1445行） |
| **メモリ上限の適用範囲** | **全同時エージェントの合計**（v0.3.0で変更。小さなspawnを多数行ってホストを食い潰すことができなくなった）。合計値は `resource_limits.max_total_memory_mb`／`resource_limits.max_total_processes` で上書き |
| Heartbeatの既定間隔 | 60秒 |
| Heartbeatタスクのタイムアウト | 1800秒（30分。v0.9.0でも変更なし） |
| セッション開始の待ち | 90秒。失敗し続ける開始は3回で背景の再試行を止める（CHANGELOG v0.8.0節 651-653行） |
| `kirocrew restart` の readiness 待ち | 既定60秒（`KIROCREW_RESTART_READY_TIMEOUT`。15〜180秒に丸め。`cli.md` 1606-1626行）。`kirocrew token` の応答待ちは20秒 |
| 遠隔 crew の連鎖 | 2ホップまで、親1つにつき連鎖先は最大8（公式 multi-instance ページ 142-146行）。Fargate の同時タスクは最大10（固定。CHANGELOG v0.7.0節の `fargate.max_running_tasks` との食い違いは継続） |

> **⚠️ 「24時間」と各タイムアウトを混同しないこと**: v0.3.0で追加された**最大24時間はjob（スケジュールジョブ）の時間予算**です。CHANGELOGの「replacing one fixed thirty-minute cap」はjob側の従来上限を指します。
>
> **「1800秒（30分）」は複数の別系統に登場します。v0.6.0で変わったものと変わらないものを区別してください。**
>
> | 系統 | v0.6.0での値 | 出典 |
> |---|---|---|
> | Subagent 1件あたりのハードタイムアウト | **10800秒（3時間）に変更** | `subagent.md` 14行（`_TIMEOUT_SECS`）・`resource-protection.md` 14行 |
> | Cron `--timeout-secs` 既定（`_JOB_TIMEOUT_SECS`） | 1800秒（変更なし） | `resource-protection.md` 20行 |
> | Heartbeatタスク（`HEARTBEAT_TASK_TIMEOUT_SECS`） | 1800秒（変更なし） | `heartbeat.md` 61・142行 |
> | Warm Pool の TTL（`session.pool_ttl_secs`） | 1800秒（変更なし） | `overview.md` 281行 |
>
> 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) を参照してください。

## App・インターフェース

| 項目 | 値 |
|------|-----|
| builtin App数 | **[要検証]**。`src/`解析は未承認のため、旧値を実測値として追認しない（仕様書が既定有効と記述する builtin は `projects` と `command-bar` の2件。`app-kit-platform.md` 1302-1306行） |
| メッセージングチャネル数 | v0.9.0時点: 公式docsの設定ガイドページ **7**、公式 Interfaces の一覧 **10**、公式 Quick start は7件を例示、README **10**、`messaging.md` は **10** で一貫（v0.7.2 の「eleven」は v0.9.0 に出現しない）。出典間の総数は裁定しない（[01_features/11_interfaces.md](../01_features/11_interfaces.md)参照） |
| インポート対応ソース数 | **5**（組み込み: Claude Code/Codex/Gemini/OpenClaw/Hermes。ほかにエディションが登録したソース。**本サイトは以前 MeshClaw と記載していましたが、v0.4.1 以降の仕様書は `gemini`**。[01_features/14_migration-import.md](../01_features/14_migration-import.md)参照） |
| インポートカテゴリ数 | **8** |
| Gatewayの既定ポート | **5476**（`KIROCREW_PORT`で変更可） |
| 管理対象 MCP サーバ数 | **8**（常時2・gated 1・オプトイン5。`mcp.md` 144-148・1532-1546行）。`kirocrew-debug`（読み取り専用5ツール）は v0.8.0 以降。`mcp.md` が名前を挙げるツール数は cron 9・computer 11・dashboard 31・work 5・crew-log 3・debug 5・panel 2（権威ある一覧は `build_tool_list()`。[04_mcp-tools.md](04_mcp-tools.md)参照） |
| Artifact の上限 | slug 80文字／name 200文字／description 2,000文字／tags 16個（各64コードポイント）／本文 25 MiB／保持バージョン 50／自動登録ウィジェット 200（`artifacts.md` 1109-1124行） |
| MCP App → チャットのメッセージ | 公式 apps ページ: 16,384文字・3秒に1通・1つのレンダリング済み App から20通まで。`mcp-apps.md` 119行: 総テキスト 16 KiB（単位が違うため両併記） |
| App マニフェストの件数上限 | パネルタブ 8／ファイルメニュー行 10／セッションコントロール 2／`notifications.channels` 8（`manifest-reference.md` 394-396・473・583・898行） |
| WeCom の添付 | 受信: 画像 10 MB・ファイル 20 MB・1メッセージ 10件。送信: ピクチャと音声ノート 2 MB・ファイルと動画 20 MB（公式 WeCom ページ） |
| ネイティブ `browser` ツール | セッションあたりキュー32件、操作ごとのタイムアウト15秒（`navigate`／`wait_for` は60秒）、パネル liveness 30秒（`browser.md` 29-36行） |
| Channels App | `agent.max_channels` 既定 1（1〜5）、`agent.max_channel_agents` 既定 3（1〜10）。チャネルは直近200メッセージを保持（`persistent-agent-channels.md` 45-47行） |
| App リバースプロキシ | SSE 以外の応答は合計30秒、SSE は60秒以内にイベントか `:` コメント（`api-reference.md` 842・1065行） |

## テレメトリ

**2つの別系統があります。混同しないでください**（[03_deployment/06_telemetry-and-privacy.md](../03_deployment/06_telemetry-and-privacy.md)参照）。

### ①匿名利用テレメトリ

| 項目 | 値 |
|------|-----|
| 既定状態 | オン（最初の送信は初回プライバシー開示の表示まで保留） |
| 送信フィールド数 | **5**（旧仕様は9） |
| 無効化の経路数 | 3（Settings/CLI/環境変数） |

### ②メトリクス／OTLPエクスポート

| 項目 | 値 |
|------|-----|
| 既定状態 | **オフ**（`telemetry.enabled: false`） |
| 送出先の既定 | **なし**（`telemetry.otlp_endpoint` は空。ローカルJSONLシンクのみ） |
| 送出に必要なもの | エンドポイント設定**と** OTLP エクスポータ用パッケージ（`opentelemetry-exporter-otlp-proto-http==1.44.0`）のインストールの**両方**（`pip install "kirocrew[otlp]"` はサポート対象のコマンドではない） |

## 未確定（両併記）

出典間で値が食い違うため、**本サイトは裁定しません**。

| 項目 | 出典A | 出典B |
|------|-------|-------|
| v0.9.0の日付 | CHANGELOG.md: 2026-10-09 | Release公開日: 2026-10-16 |
| v0.8.0の日付 | CHANGELOG.md: 2026-10-08（v0.9.0タグ時点）。v0.8.0タグ時点は 2026-09-27 | Release公開日: 2026-10-09 |
| v0.7.2の日付 | CHANGELOG.md: 2026-09-28 | Release公開日: 2026-09-29 |
| v0.7.1の日付 | CHANGELOG.md: 2026-09-24 | Release公開日: 2026-09-25 |
| v0.7.0の日付 | CHANGELOG.md: 2026-09-15 | Release公開日: 2026-09-24 |
| v0.6.0の日付 | CHANGELOG.md: 2026-09-05 | Release公開日: 2026-09-11 |
| v0.5.0の日付 | CHANGELOG.md: 2026-08-29 | Release公開日: 2026-09-05 |
| v0.4.1の日付 | CHANGELOG.mdの版日付 | Release公開日: 2026-08-29 |
| v0.4.0の日付 | CHANGELOG.mdの版日付 | Release公開日: 2026-08-27 |
| v0.3.0の日付 | CHANGELOG.md: 2026-08-17 | Release公開日: 2026-08-21 |
| v0.2.0の日付 | CHANGELOG.md: 2026-08-09 | Release公開日: 2026-08-10 |
| サンドボックスの呼称 | 公式docs: `auto` | README・内部ティア: `standard` |
| v0.5.0の破壊的変更の件数 | CHANGELOG.md `[0.5.0]` 節: **12件** | GitHub Release 本文: **5件**（"Five changes" と明記） |
| コンテキストバジェット | 公式 memory ページ: 図「Context Window (~55K tokens)」（v0.6.0 と同一） | `memory-skills-hooks.md` 6135行: `_CONTEXT_BUDGET_BASE` = 33,000文字の固定値（v0.7.0〜） |
| Windowsで委譲先のない経路の既定（`agent.sandbox_allow_unsandboxed_exec` 未宣言時） | 公式 `security/`・`configuration/` ページ、CHANGELOG v0.6.0節: fail-closed（既定 `false`） | `windows-install.md` 286-295行・`modules/security.md` 757・763行: **Windowsでは許可（非サンドボックス実行）**（[03_deployment/02_windows.md](../03_deployment/02_windows.md)参照。v0.9.0 の `README.md` に該当文はない） |
| Autopilot（plan／approve／stage loop） | v0.7.2・v0.8.0 の `modules/autopilot.md` と公式 configuration ページ（`orchestrator.max_plan_duration_seconds`）が存在 | v0.9.0 の `taskq.md` 464行・`subagent.md` 3402行は「retired chat Autopilot」と記述し、`autopilot.md` は存在しない。CHANGELOG に告知なし（[06_autonomy.md](../01_features/06_autonomy.md)参照） |
| 単一タスク委任の拒否（Delegation gate） | 公式 Subagents ページ（Page updated 2026-09-30）: 理由のない単一タスク委任を拒否 | `subagent.md` 3134-3146行・CHANGELOG v0.8.0節: 実行時のゲートは存在しない |
| 画面名 | CHANGELOG v0.9.0節・公式 agents ページ: **Customize** | 公式の他の capabilities ページ: **Agent Capabilities** |

> **解消した両併記**: 「埋め込み実装」（`knowledge.md` のOllama依存の旧記述）は **v0.6.0 で解消**、`session.pool_size` の既定値（0 vs 2）も v0.6.0 で `0` に一致しています。**v0.9.0 で次の3項目も解消しました**: ①「Subagent自動サイジング上限（`agent.subagent_auto_max`）」と「Subagent並行数の既定（`agent.max_subagents`）」は `config.md` が `subagent.md` と一致（0 と 32。v0.8.0 で変更）、②「Agent Backends の選択肢」は公式・CHANGELOG・仕様書が8種で一致、③「サンドボックスの値域」は `auto`／`strict`／`off` で一致。

## 未確認事項

- builtin App数（S12）: `src/`解析は、対象SHA・対象パス・解析方法を示す明示承認がないため未実施
- 拒否コマンドルール件数: 公式ページ・仕様書の記述（v0.9.0 時点）に件数の記載がない
- Autopilot の v0.9.0 での扱い、`orchestrator.stage_timeout_seconds`（出典の `autopilot.md` が v0.9.0 に存在しない）
- `session.watchdog_rss_max_mb` の既定が `0` に戻った理由（CHANGELOG と Release 本文に説明がない）
- Cron `--every` の一般下限（60秒はimport取込下限とHeartbeat間隔として確認済み）
- `-insider.N` の欠番の理由（[02_update/02_release-policy.md](../02_update/02_release-policy.md)参照）

## 関連リンク

- セキュリティ: [01_features/09_security.md](../01_features/09_security.md)
- メモリ: [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md)
- 自律実行: [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)

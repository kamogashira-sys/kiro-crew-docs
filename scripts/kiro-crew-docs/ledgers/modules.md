# `docs/system-specs/` 全107ファイル 扱う／扱わない台帳

- **取得日**: 2026-10-25
- **commit SHA**: `99e6253`（版 v0.9.0）
- **数え方**: `find docs/system-specs -type f` の**全ファイル**（Markdown 104件＋`modules/examples/workflows/*.py` 3件＝**107件**。v0.7.2 は 101＋3＝104件、v0.6.0 は 85＋3＝88件）。`.md` のみを数えると85件になるため、件数を引用する際は数え方を明示すること
- **判定基準**: 冒頭500バイトに `removed` / `no longer exist` / `legacy` / `deprecated` の断りがあるものを「出典にしない（削除済み・移行専用）」の候補とし、**ファイル全体の文脈を人手で確認**して最終判定する（機械検出だけでは `acp-client.md`・`config.md` のように内部に部分的な legacy 言及があるだけのファイルを誤って除外するため）
- **検証**: `check-coverage.py` の入力データ。合計欄が実測と一致し、判定漏れが0件であることを機械検証する

> **v0.3.0再確認（2026-08-22・`21584ea`）**: `find -type f` 実測76件（直下2・common 5・features 13・modules 56）。
>
> **v0.6.0再構築（2026-09-13・`8575209`）**: 実測**88件**（直下3・common 7・modules 74・modules/examples/workflows 4）。v0.4.1（81件）からの差分は**継続62件・`features/`→`modules/` の同名移動13件・完全新規13件・消滅6件**（`features/README.md`／`features/code-approvers.md`／`features/inline-action-buttons.md`／`modules/auto-improvement-test-plan.md`／`modules/kas-backend.md`／`modules/workflow-gates.md`）。**`features/` ディレクトリ自体が消滅**した。<br>**v0.4.1 の台帳（76件）は実体81件に対して判定漏れがあった**（`command-bar.md`・`session-control.md` など）。本再構築で全88件に判定を付与し、この乖離を解消した。
>
> **v0.7.2更新（2026-10-04・`c67c506`）**: 実測**104件**（直下3・common 7・modules 90・modules/examples/workflows 4）。v0.6.0 からの差分は**新規16件（すべて `modules/`）・消滅0件**（88＋16＝104）。新規16件の判定は「扱う」6件・「開発者向け・出典にしない」9件・「未割当・扱わない」1件（`monitor-architecture.md`）。新規16件の冒頭500バイトに `removed`／`no longer exist`／`legacy`／`deprecated` は0件。

> **v0.9.0更新（2026-10-25・`99e6253`）**: 実測**107件**（直下3・common 8・modules 92・modules/examples/workflows 4）。v0.7.2 からの差分は**新規4件・消滅1件**（104＋4−1＝107）。新規4件は `common/take-away-changes.md`・`modules/dashboard-instances.md`・`modules/dashboard-templates.md`・`modules/runtime-ownership.md`、消滅1件は `modules/autopilot.md`（v0.8.0 タグには存在し、v0.9.0 タグには存在しない）。新規4件の判定は「開発者向け・出典にしない」2件・「未割当・扱わない」2件。`modules/monitor-architecture.md` は `01_features/17_workflows.md` が引用したため「未割当」から「扱う」へ変更した。

## 直下（3ファイル）

| ファイル | 扱い | 担当ページ / 理由 |
|---------|------|------------------|
| `README.md` | 索引・出典にしない | `system-specs` の索引 |
| `oss-fork-boundaries.md` | 開発者向け・出典にしない | 実装規約・開発者向けの手順 **【v0.6.0新規】** |
| `post-launch-removals.md` | 移行専用・出典にしない | 「ローンチ後に削除予定のコード」の台帳。旧データホーム `~/.kirocrew` の記述を含むため誤記の危険がある。**唯一の例外**: 「旧パス `~/.kirocrew` は現行では使わない」の出典としてのみ `04_reference/03_directory-layout.md` で言及（S20） |

## common（8ファイル）

| ファイル | 扱い | 担当ページ / 理由 |
|---------|------|------------------|
| `common/README.md` | 索引・出典にしない | `common` の索引 |
| `common/code-style.md` | 開発者向け・出典にしない | 出典にしない（Crew 開発者のコード規約） |
| `common/error-handling.md` | 開発者向け・出典にしない | 出典にしない |
| `common/injected-messages.md` | 開発者向け・出典にしない | 出典にしない（ACP注入メッセージの内部規約） |
| `common/model-selection.md` | 開発者向け・出典にしない | 実装規約・開発者向けの手順 **【v0.6.0新規】** |
| `common/platform-compat.md` | 開発者向け・出典にしない | 実装規約・開発者向けの手順 **【v0.6.0新規】** |
| `common/testing-conventions.md` | 開発者向け・出典にしない | 出典にしない |
| `common/take-away-changes.md` | 開発者向け・出典にしない | 何かを取り除く変更のレビュー規約（Crew 開発者向け） **【v0.9.0新規】** |

## modules（92ファイル）

| ファイル | 扱い | 担当ページ / 理由 |
|---------|------|------------------|
| `modules/acp-client.md` | 扱う（機能解説の出典） | `01_architecture.md`（ACP・多重化・Warm Pool）※内部に "legacy per-session client" の言及があるが、ファイル自体は現行アーキテクチャの説明であり削除済みではない |
| `modules/adaptive-concurrency.md` | 扱う（機能解説の出典） | 適応的な並行数制御 → `01_features/06_autonomy.md` **【v0.7.x新規】** |
| `modules/agent-host-contract.md` | 開発者向け・出典にしない | 実装規約・開発者向けの手順 **【v0.6.0新規】** |
| `modules/agent-interrupt-controller.md` | 扱う（機能解説の出典） | `kiro_crew.irq`。ポーリング監視を wake-on-change 割り込みに変える → `01_features/17_workflows.md` **【v0.6.0新規】** |
| `modules/app-kit-platform.md` | 扱う（機能解説の出典） | `10_apps.md`（App SDK 基盤） |
| `modules/app-notifications.md` | 扱う（機能解説の出典） | `10_apps.md`（App 通知の仕組みとして触れる） **【v0.6.0で `features/` から移動】** |
| `modules/artifacts.md` | 扱う（機能解説の出典） | `12_artifacts.md` |
| `modules/auto-improvement.md` | 扱う（builtin App の説明として） | `04_memory-and-learning.md`（Self-evolving） |
| `modules/aws-control.md` | 扱う（機能解説の出典） | AWS Control builtin App → `01_features/16_aws-control.md` **【v0.6.0新規】** |
| `modules/babysit-pr-watch.md` | 扱う（機能解説の出典） | PR監視ループ → `01_features/17_workflows.md` **【v0.6.0で `features/` から移動】** |
| `modules/browser.md` | 扱う（機能解説の出典） | `13_computer-and-browser.md`（ブラウザ自動化。MCPでないことを明記） |
| `modules/channel-history.md` | 扱う（機能解説の出典） | `02_sessions.md`（チャネル履歴） |
| `modules/claude-code-provider.md` | 扱う（機能解説の出典） | **v0.6.0でタイトルが `# Claude Code provider — a selectable ACP harness` に変わり、削除済み機能の記録ではなく現行機能の仕様書になった** → `01_features/15_agent-backends.md` **【v0.6.0で `features/` から移動】** |
| `modules/cli.md` | 扱う（機能解説の出典） | `04_reference/01_cli-commands.md` |
| `modules/cloud.md` | 未割当・扱わない | クラウド関連の内部仕様だが、CLI・README・公式ページに `cloud` サブコマンドとして現れない。**扱わない**理由: 利用者向けの公開インターフェースとして確認できないため |
| `modules/command-bar.md` | 扱う（機能解説の出典） | Command Bar（Cmd+K）。v0.6.0で `contributes.commands` により App が行を追加できる → `01_features/10_apps.md` |
| `modules/computer-use.md` | 扱う（機能解説の出典） | `13_computer-and-browser.md`（Computer Use） |
| `modules/config.md` | 扱う（機能解説の出典） | `04_reference/02_configuration-keys.md` ※内部に "migrated from the older ... " の言及があるが、ファイル自体は現行の設定キー仕様であり削除済みではない |
| `modules/connections.md` | 扱う（機能解説の出典） | 接続の管理（Disconnect時のOAuth grant revoke を含む） → `01_features/09_security.md`・`11_interfaces.md` **【v0.6.0新規】** |
| `modules/connector-capability-manifest.md` | 開発者向け・出典にしない | コネクタ実装キャンペーンのスキーマと作業DAG（"documentation only"） **【v0.7.x新規】** |
| `modules/connector-conformance.md` | 開発者向け・出典にしない | コネクタ実装キャンペーンの適合性の責務一覧 **【v0.7.x新規】** |
| `modules/connector-github.md` | 開発者向け・出典にしない | GitHub コネクタの内部データとパース **【v0.7.x新規】** |
| `modules/connector-zoom.md` | 開発者向け・出典にしない | Zoom コネクタの契約セマンティクス（ネットワークなしの部品） **【v0.7.x新規】** |
| `modules/crew-log-core.md` | 扱う（機能解説の出典） | Crew log（`KIROCREW_CREW_LOG`・既定オフ）→ `01_features/08_mcp-integration.md`・`01_features/02_sessions.md` **【v0.7.x新規】** |
| `modules/crew-log-emitter.md` | 開発者向け・出典にしない | Crew log の書き込み側の内部実装 **【v0.7.x新規】** |
| `modules/crew-log-projection.md` | 開発者向け・出典にしない | Crew log の表示用 fold の内部実装 **【v0.7.x新規】** |
| `modules/crew-mode.md` | 扱う（機能解説の出典） | Crew Mode → `01_features/02_sessions.md` **【v0.6.0新規】** |
| `modules/dashboard-instances.md` | 未割当・扱わない | crewmate ごとのダッシュボードインスタンス（Dynamic Dashboard プレビューの内部仕様）。`01_features/12_artifacts.md` は公式ページと `artifacts.md` を出典にしており本ファイルは未引用。**【v0.9.0新規】** |
| `modules/dashboard-templates.md` | 未割当・扱わない | ダッシュボードページのテンプレート作成仕様（Dynamic Dashboard プレビューの内部仕様）。`01_features/12_artifacts.md` は本ファイルを未引用。**【v0.9.0新規】** |
| `modules/dashboard-token-auth.md` | 扱う（機能解説の出典） | `04_reference/02_configuration-keys.md`（ダッシュボードのトークン認証） **【v0.6.0で `features/` から移動】** |
| `modules/decisions.md` | 扱う（機能解説の出典） | Jev（Decisions・Preview）→ `01_features/03_chat.md` **【v0.7.x新規】** |
| `modules/dev-fleet.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「Dev Fleet」の説明として） |
| `modules/file-search.md` | 扱う（機能解説の出典） | `03_chat.md`（`@` メンション） |
| `modules/governance.md` | 扱う（機能解説の出典） | `09_security.md`（Governance） |
| `modules/harness-onboarding.md` | 扱う（機能解説の出典） | ACPハーネスの追加手順。Dormant/Selectable の区別が Agent Backends の理解に必要 → `01_features/15_agent-backends.md` **【v0.6.0新規】** |
| `modules/harness-parity.md` | 開発者向け・出典にしない | 出典にしない（内部テストハーネスの一致性） |
| `modules/harness-plugin-mapping.md` | 扱う（機能解説の出典） | 他ハーネスのプラグインモデルの対応 → `01_features/10_apps.md` **【v0.7.x新規】** |
| `modules/heartbeat.md` | 扱う（機能解説の出典） | `06_autonomy.md`（Heartbeat） |
| `modules/history.md` | 扱う（機能解説の出典） | `02_sessions.md` または `04_memory-and-learning.md`（履歴の扱いは memory-skills-hooks.md が主出典のため軽い補足として） |
| `modules/instances.md` | 扱う（機能解説の出典） | `03_deployment/03_running-24-7.md`（マルチインスタンス） |
| `modules/issue-radar.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「Issue Radar」の説明として） |
| `modules/kas-auth.md` | 扱う（機能解説の出典） | KASモードの認証 → `01_features/15_agent-backends.md` **【v0.6.0新規】** |
| `modules/knowledge.md` | 扱う（機能解説の出典） | `05_knowledge-library.md` |
| `modules/learn-cron-dashboard.md` | 扱う（機能解説の出典） | `06_autonomy.md`（Cron のインポート下限60秒等）・`10_apps.md`（学習ダッシュボードの一部）。**極めて長大なファイルのため全文解説はしない** |
| `modules/mcp-apps.md` | 扱う（機能解説の出典） | `08_mcp-integration.md` |
| `modules/mcp-gateway-backend-replacement.md` | 開発者向け・出典にしない | 実装規約・開発者向けの手順 **【v0.6.0新規】** |
| `modules/mcp-gateway-daemon-lifecycle.md` | 開発者向け・出典にしない | MCP gateway デーモンのプロセス管理の内部実装 **【v0.7.x新規】** |
| `modules/mcp-probe-quarantine.md` | 扱う（機能解説の出典） | MCPサーバのprobe失敗カウンタ（無言劣化の解消） → `01_features/08_mcp-integration.md` **【v0.6.0新規】** |
| `modules/mcp-shareability.md` | 扱う（機能解説の出典） | `08_mcp-integration.md`（MCP設定の共有範囲） |
| `modules/md-notebook.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「Notes」の説明として） |
| `modules/meetings.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「Meetings」の説明として） |
| `modules/member-event-log.md` | 開発者向け・出典にしない | Crew member のイベントログの内部実装 **【v0.7.x新規】** |
| `modules/memory-skills-hooks.md` | 扱う（機能解説の出典） | `04_memory-and-learning.md`・`07_agents-skills-steering.md`（メモリ・スキル・フックの主要出典） |
| `modules/messaging.md` | 扱う（機能解説の出典） | `11_interfaces.md`（メッセージングチャネル） |
| `modules/metrics.md` | 扱う（機能解説の出典） | `03_deployment/06_telemetry-and-privacy.md`（テレメトリ） |
| `modules/microsoft-graph-runtime.md` | 開発者向け・出典にしない | Microsoft Graph 系コネクタの共通ロジック **【v0.7.x新規】** |
| `modules/mochi.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「Mochi」の説明として） |
| `modules/model-fallback.md` | 扱う（機能解説の出典） | モデルのフォールバック → `01_features/02_sessions.md` **【v0.6.0で `features/` から移動】** |
| `modules/monitor-architecture.md` | 扱う（機能解説の出典） | 監視ループの共通設計 → `01_features/17_workflows.md`（conductor の既定パトロール・`monitoring.max_runtime_secs`）。v0.7.2 では未引用だった |
| `modules/onboarding-import.md` | 扱う（機能解説の出典） | `14_migration-import.md` |
| `modules/ops-mission-control.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「Ops Mission Control」の説明として） |
| `modules/papyrus.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「Papyrus」の説明として） |
| `modules/persistent-agent-channels.md` | 扱う（機能解説の出典） | `11_interfaces.md`（永続エージェントチャネル） |
| `modules/pipeline-conductor.md` | 扱う（機能解説の出典） | conductor（目標の分解・セッション起動・受入基準の検査） → `01_features/17_workflows.md` **【v0.6.0新規】** |
| `modules/platform-context.md` | 開発者向け・出典にしない | 出典にしない（OS判定等の内部実装） |
| `modules/plugin-import.md` | 扱う（機能解説の出典） | `kirocrew app import` → `01_features/10_apps.md` **【v0.7.x新規】** |
| `modules/pptx-maker.md` | 扱う（builtin App の説明として） | `10_apps.md`（builtin App「PPTX Maker」の説明として） |
| `modules/prompt-optimizer.md` | 扱う（機能解説の出典） | `03_chat.md`（Prompt Optimizer） **【v0.6.0で `features/` から移動】** |
| `modules/providers.md` | 扱う（機能解説の出典） | `01_architecture.md`（`agent.provider` が `acp` 固定・削除済みプロバイダ） |
| `modules/README.md` | 索引・出典にしない | `modules` の索引 |
| `modules/runtime-ownership.md` | 開発者向け・出典にしない | エージェントランタイムのプロセス所有権の設計（lease と tenancy）。実装者向けの内部設計 **【v0.9.0新規】** |
| `modules/security.md` | 扱う（機能解説の出典） | `09_security.md`・`03_deployment/04_security-hardening.md` |
| `modules/sel.md` | 扱う（機能解説の出典） | `09_security.md`（SEL・HMACチェーン） |
| `modules/session-control.md` | 扱う（機能解説の出典） | セッション制御（create/stop/send-to）。`agent.session_control` → `01_features/17_workflows.md` |
| `modules/session-storage.md` | 扱う（機能解説の出典） | `02_sessions.md` |
| `modules/session-summary.md` | 扱う（機能解説の出典） | `02_sessions.md`（セッション要約） |
| `modules/session-work-ledger.md` | 扱う（機能解説の出典） | セッションの作業台帳 → `01_features/02_sessions.md` **【v0.6.0で `features/` から移動】** |
| `modules/session.md` | 扱う（機能解説の出典） | `02_sessions.md`（`session_key` の形式を含む） |
| `modules/side.md` | 扱う（機能解説の出典） | `03_chat.md`（`/side`） |
| `modules/slack-gateway.md` | 扱う（機能解説の出典） | `11_interfaces.md`（Slack連携の詳細） |
| `modules/steering-viewer.md` | 扱う（機能解説の出典） | `07_agents-skills-steering.md`（軽く触れる） **【v0.6.0で `features/` から移動】** |
| `modules/stt-streaming.md` | 扱う（機能解説の出典） | `03_chat.md`（音声・STT） **【v0.6.0で `features/` から移動】** |
| `modules/subagent.md` | 扱う（機能解説の出典） | `06_autonomy.md`（Subagent。S15 の出典の一方） |
| `modules/task.md` | 扱う（機能解説の出典） | `06_autonomy.md`（Task の内部表現。taskrunner.md と合わせて） |
| `modules/taskq.md` | 扱う（機能解説の出典） | 永続タスクキュー → `01_features/06_autonomy.md`・`01_features/17_workflows.md` **【v0.7.x新規】** |
| `modules/taskrunner.md` | 扱う（機能解説の出典） | `06_autonomy.md`（Task Runner） |
| `modules/themes.md` | 扱う（機能解説の出典） | `03_chat.md`（テーマ） |
| `modules/turn-complete-chime.md` | UI詳細・粒度超過で出典にしない | 出典にしない（通知音の設定項目。粒度を超える） **【v0.6.0で `features/` から移動】** |
| `modules/turn-stats-footer.md` | UI詳細・粒度超過で出典にしない | 出典にしない **【v0.6.0で `features/` から移動】** |
| `modules/voice-streaming.md` | 扱う（機能解説の出典） | `03_chat.md`（音声・TTS） **【v0.6.0で `features/` から移動】** |
| `modules/workflow-chat-cards.md` | 扱う（機能解説の出典） | `06_autonomy.md`（Workflows のUI表現として軽く触れる） **【v0.6.0で `features/` から移動】** |
| `modules/workflows.md` | 扱う（builtin App の説明として） | `06_autonomy.md`・`10_apps.md`（builtin App「Workflows」） |

## modules/examples/workflows（4ファイル）

| ファイル | 扱い | 担当ページ / 理由 |
|---------|------|------------------|
| `modules/examples/workflows/01_review_changes.py` | サンプルコード・出典にしない | ワークフローのサンプルスクリプト（`docs/` 配下だが仕様記述ではない） |
| `modules/examples/workflows/02_loop_until_dry_bug_hunt.py` | サンプルコード・出典にしない | ワークフローのサンプルスクリプト（`docs/` 配下だが仕様記述ではない） |
| `modules/examples/workflows/03_scheduled_triage_native.py` | サンプルコード・出典にしない | ワークフローのサンプルスクリプト（`docs/` 配下だが仕様記述ではない） |
| `modules/examples/workflows/README.md` | 索引・出典にしない | `modules/examples/workflows/` のサンプル索引 |
## 集計

| 区分 | 件数 |
|------|------|
| 扱う（機能解説の出典） | 62 |
| 扱う（builtin App の説明として） | 10 |
| 索引・出典にしない | 4 |
| 開発者向け・出典にしない | 22 |
| UI詳細・粒度超過で出典にしない | 2 |
| サンプルコード・出典にしない | 3 |
| 移行専用・出典にしない | 1 |
| 未割当・扱わない | 3 |
| **合計** | **107**（全ファイルに判定あり。判定漏れ0件） |

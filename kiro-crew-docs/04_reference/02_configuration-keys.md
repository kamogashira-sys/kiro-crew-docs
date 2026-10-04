# 設定キー・環境変数

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（`session.pool_size`既定値の不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（`agent.max_subagents`既定値の不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（v0.5.0・v0.6.0 の新規キーと既定値の再測定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session-control.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**（v0.7.0 の既定値変更・新規キーの再測定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 表記あり）

---

## 📑 このページの内容

- [設定ファイル](#設定ファイル)
- [主な設定キー](#主な設定キー)
- [v0.7.0での変更](#v070での変更)
- [App manifest が宣言する項目（`config.json` のキーではない）](#app-manifest-が宣言する項目configjson-のキーではない)
- [環境変数](#環境変数)
- [未確認事項](#未確認事項)

---

## 設定ファイル

`~/.kiro/crew/config.json`（`config.local.json` によるオーバーレイあり）。

## 主な設定キー

`~/.kiro/crew/config.json` のキーです。**App の manifest が宣言する項目は別物**なので[後述の節](#app-manifest-が宣言する項目configjson-のキーではない)に分けています。

| キー | 既定値 | 説明 |
|------|-------|------|
| `agent.sandbox` | `auto` | サンドボックスモード。`config.md` 940行は既定 `"auto"`（Linuxはnamespace、macOSはseatbelt。macOSで有効時はkiro-cli内部のサンドボックスに委譲）、`"off"` はKiro Crewのサンドボックスをスキップ。**⚠️ 値域が出典3系統で食い違います**（`README.md` 385行は「Standard, strict, and off modes」の3モード、`security-deep-dive.md` 107-112行は内部ティア4種 `standard`／`cc`／`strict`／`off` としたうえで「運用者が `agent.sandbox` に書く値ではない」と明記）。裁定しません（[09_security.md](../01_features/09_security.md)参照） |
| `agent.provider` | `acp`（固定） | LLMプロバイダ。変更不可 |
| **`agent.acp_backend`**（v0.6.0） | `ACP_BACKEND_KIRO`（Kiro ハーネス。`harness-parity.md` 84行・`c67c506`） | セッションを動かすハーネスの選択。`acp_backends.resolve_selected_backend()` が値を正規化する。**Preview機能（Developer Mode 前提）**（[15_agent-backends.md](../01_features/15_agent-backends.md)参照） |
| **`agent.member_acp_backend`**（v0.6.0） | `kas` | Crew member のハーネス（`session-control.md` 235行） |
| `agent.max_subagents` | **食い違いあり** | Subagentの並行数上限。`subagent.md`は既定`0`（自動サイジング）、`config.md`のdataclass literalは既定`3`（両併記・裁定しない） |
| `agent.subagent_auto_max` | **食い違いあり** | 自動サイジングの上限。`subagent.md`は32、`config.md`は16と記述（両併記・裁定しない） |
| `agent.apps_allow_third_party` | `false` | サードパーティAppの実行許可スイッチ |
| `agent.sandbox_allow_unsandboxed_exec` | `false`（**Windowsでは未宣言時に許可**。下記注記） | サンドボックスバックエンド不在時の非サンドボックス実行を許可するopt-in。**v0.7.0 以降、未宣言の値はプラットフォーム依存で解決され、Windowsでは許可・それ以外ではfail-closed**（`security.md` 309行）。Windowsで拒否するには `false` を明示的に宣言する（宣言値はどちらの向きでもプラットフォーム既定に優先）。⚠️ 公式 `configuration/` ページの表は既定 `false`「only when explicitly enabled」と記載しており、プラットフォーム差に触れていません（裁定しない。[03_deployment/02_windows.md](../03_deployment/02_windows.md)参照） |
| **`agent.refusal_fallback_model`**（v0.7.0） | `""`（空＝無効） | コンテンツフィルタで拒否されたメッセージを1回だけ再試行するモデル。Settings → Chat でスロットル時のフォールバックの隣で選ぶ。次のターンでは主モデルに戻る（CHANGELOG.md v0.7.0節 356-359行、公式 `configuration/` ページ） |
| `agent.chat_turn_timeout_secs` | **`14400`（4時間）** | チャットターンの上限（ロード時クランプは300〜86400秒、無効化不可）。**v0.5.0以前は`7200`（2時間）**。`resource-protection.md` 49行は「14400 is the default, not the ceiling」と明記 |
| `agent.tool_approval_timeout_secs` | `600`（10分） | ツール承認の待機時間（ロード時クランプは30〜7200秒、かつ `chat_turn_timeout_secs` より60秒以上小さい値へ丸められる） |
| **`agent.subagent_timeout_secs`**（v0.6.0） | **`10800`（3時間）** | Subagent 1件あたりのハードタイムアウト。**v0.5.0以前は1800秒の固定値**（設定不可）。ロード時クランプは60〜86400秒、`0` は既定値を使うsentinel。**⚠️ ダッシュボードからは設定できません**（`resource-protection.md` 374-377行。CLIか`config.json`の編集が必要） |
| `agent.subagent_max_turns` | **`1000`**（**v0.6.0以前は`100`**） | Subagent 1件あたりのツール呼び出し予算。ロード時クランプは`[1, 1000]`（v0.6.0 で上限が200→1000に拡大済み）。**v0.7.0 で既定値が変わりました**（`config.md` 1849行・407行「`agent.subagent_max_turns` (100 -> 1000, #12203)」、公式 `configuration/` ページの表も `1000`）。**キーが未設定なら、更新後の既存インストールも含めて自動で1000に追従**します。**保存済みの値は100であっても保持**されます（旧既定値として書き込まれた100と、意図して選んだ100を区別できないため。`config.md` 410-416行）。保存値の確認と採用／維持は `kirocrew config defaults`（`--adopt`／`--keep`）で行います。本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません |
| **`agent.subagent_stall_idle_secs`** | `120` | ストリーム無活動が続いたときにSubagentを「停滞」表示するまでの秒数 |
| **`agent.completion_keep_chars`** | `3000` | 親セッションへ注入する完了イベントの文字数上限 |
| `agent.subagent_result_ttl_secs` | `3600` | 配送済みSubagentの`result.txt`を保持する秒数 |
| **`agent.session_control`**（v0.6.0） | **`true`** | セッション制御（外部からのcreate／stop／send-to）。`false` を明示すると403で拒否される（`session-control.md` 144行）（[17_workflows.md](../01_features/17_workflows.md)参照） |
| **`orchestrator.max_plan_duration_seconds`**（v0.6.0） | `7200`（2時間） | 無人 auto-run plan 全体の実時間予算。**ステージ境界でチェック**され、75%で1回警告。`0` で無効化。**stage-gatedな planは打ち切られない**（[06_autonomy.md](../01_features/06_autonomy.md)参照） |
| **`orchestrator.stage_timeout_seconds`**（v0.6.0） | `1800` | ステージ単位の時間予算。`0` でチェック無効（`autopilot.md` 499行・`c67c506`。v0.6.0 の同ファイル387行にも同じ記載があり、本サイトの「未確認」は確認漏れでした） |
| `session.pool_size` | `0`（無効） | Warm Poolのサイズ。**v0.6.0で`overview.md`と`config.md`が`0`で一致**（以前は`2`との食い違いを両併記していた）。ロード時クランプ上限は`POOL_SIZE_MAX = 10` |
| `session.pool_ttl_secs` | `1800` | Warm Pool内プロセスのTTL（v0.6.0でも変更なし） |
| `session.timeout_secs` | `3600`（60分） | セッションのアイドルタイムアウト |
| `session.autocompact_pct` | **`70`** | 自動圧縮のコンテキスト使用率閾値（ロード時クランプは5.0〜90.0）。**⚠️ 本サイトは以前`90`と記載していました**。`config.md` 221行は既定値の変更履歴として `90.0 -> 70.0` を挙げています |
| `session.watchdog_rss_max_mb` | **`1536`**（MiB。**v0.6.0以前は`0`＝無効**） | プロセスツリーのRSSがこのMiBを超えたセッションを再生成する。`0` で無効。**v0.7.0 で既定値が変わりました**（`config.md` 1884行「Non-zero by default so a runaway session tree is bounded out of the box」）。ターン実行中のセッションに加え、**サブエージェントが実行中・キュー待ち・結果配送中の親セッションも対象外**。本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません |
| `taskrunner.max_parallel_steps` | `2` | 並列グループ内で同時実行するステップセッションの最大数 |
| `memory.history_idle_hours` | `3.0` | 履歴統合のアイドルトリガー |
| `memory.history_max_days` | `365` | 履歴のディスク保持期間 |
| `memory.embedding_provider` | `llama_cpp`（固定。legacy値も強制コアース） | メモリシステムの埋め込みプロバイダ |
| `skills.lazy_load` | `false` | スキルのon-demandセット注入方式 |
| **`skills.max_triggered`** | `0` | 1メッセージあたりに注入する一致スキルの最大数。**`0` はトリガー注入を無効にするが、スキルの発見（短い索引と `skill_search`）は止めない**。正の整数で旧来の注入動作に戻る（CHANGELOG.md v0.7.0節 419-422行、公式 `configuration/` ページ）。⚠️ CHANGELOG は v0.7.0 の変更として「defaults to 0」と記述していますが、v0.6.0 の `config.md` 1019行も既に `max_triggered: int = 0` でした（裁定しない）。Jev（Decisions）の自動スキル選択にも `0` より大きい値が必要 |
| **`auto_update`** | `true` | ソースインストールの更新確認。**v0.7.0 から起動時に加えて12時間ごと**に確認する（公式 `configuration/` ページ、CHANGELOG.md v0.7.0節 148-150行。[03_deployment/01_installation.md](../03_deployment/01_installation.md)参照） |
| **`wakatime.enabled`**（v0.7.0） | `false` | WakaTimeのコーディング時間連携。有効にするとコーディング活動のheartbeatをWakaTimeへ送り、アカウントの統計を読む。APIキー（`WAKATIME_API_KEY`）は **Settings → Secrets** のvaultにのみ保存でき、`.env`や`config.json`からは読まれない（公式 `configuration/` ページ「Coding hours with WakaTime」、CHANGELOG.md v0.7.0節 100-103行） |
| `hooks.denied_commands.user_added` | – | インポート等で追加されたユーザー定義の拒否ルール |
| `mcp_gateway.enabled` | – | MCP Gatewayの有効化 |
| `dashboard.url` | 省略時 `localhost:5476` | ダッシュボードの到達先URL |
| **`dashboard.terminal.completion.enabled`**（v0.6.0） | **`true`** | 内蔵ターミナルの補完。`false` にすると無効化され、SEL監査イベント `terminal.complete` に `feature_disabled` が記録される。既定値は公式 `configuration/` ページの表で確認（v0.6.0 の同ページにも `true` と記載あり。本サイトは以前「未確認」としていました） |
| **`dashboard.default_memory_mode`**（v0.7.0） | `persistent` | 新しいダッシュボードチャットのメモリモード（`persistent`／`incognito`／`temporary`）。ユーザーが作るダッシュボードチャットにのみ適用（`config.md` 1963行、公式 `configuration/` ページ） |
| **`dashboard.export_include_layer_b`**（v0.7.0） | **オフ** | セッションのエクスポートに正確なモデルコンテキストを含め、インポート時にプレフィックスの再生ではなく再開できるようにする（CHANGELOG.md v0.7.0節 377-378行） |
| **`dashboard.browser_view_port`**（v0.5.0） | OSが自動割り当て | ブラウザビューの公開ポートを固定する（`browser.md` 341行） |
| **`instances.enabled`**（v0.6.0） | **`false`（既定オフ）** | Remote crews（別crewでのチャット実行）。**Preview機能**（`instances.md` 6行「Opt-in: off by default」）。v0.7.2 の公式 `features/multi-instance/` ページは「This setting applies live in 0.7」と記述（[03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)参照） |
| **`telemetry.enabled`**（v0.6.0） | **`false`** | ローカルのメトリクス収集の有効化。**これだけではネットワークへのエクスポートは行わない**（OTLP送信には `telemetry.otlp_endpoint` の設定と `kirocrew[otlp]` extra の導入が別途必要。`telemetry-otlp-export.md` 17-23行、公式 `configuration/` ページ「it does not export them」）。**匿名利用テレメトリとは別系統**（[03_deployment/06_telemetry-and-privacy.md](../03_deployment/06_telemetry-and-privacy.md)参照） |
| **`tunnel.enabled`**（v0.5.0） | 未確認 | 公開HTTPS URLでダッシュボードを露出するトンネル。`kirocrew gateway --no-tunnel` はこの設定に関わらずトンネルを張らない（`cli.md` 150行） |
| **`publish.allowed_destinations`**（v0.6.0） | default-open の allowlist | Artifact 公開先の許可リスト（`governance.md` 2200行）（[12_artifacts.md](../01_features/12_artifacts.md)参照） |
| **`slack.trusted_bot_ids`**（v0.5.0） | 未確認 | 信頼するSlack bot ID |
| **`telegram.bot_token`**（v0.3.0） | `""`（空） | **Telegramのbot token（@BotFather発行）。v0.3.0でmulti-accountが撤回され、単一トークンのみが受理されるようになった**。従来のaccount mapは**parseされ保持されるが読まれない**。**`config.md` 753行は「prefer the `TELEGRAM_BOT_TOKEN` credential」と記述しており、設定ファイルに直接書くよりも認証情報（環境変数・`.env`）経由が推奨されます**（[01_features/11_interfaces.md](../01_features/11_interfaces.md)参照） |
| **`knowledge.auto_ingest_artifacts`**（v0.3.0） | **`false`** | **Knowledge Libraryへのローカルartifact自動取り込み。v0.3.0でopt-in（既定オフ）化された**。有効にすると既存のartifactもバックフィルされる（[01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)参照） |
| **`knowledge.embed_timeout_secs`** | `10.0` | Knowledge Libraryの1リクエストあたり埋め込みタイムアウト（秒）。0・未設定は組み込みの既定値10秒になる |

## v0.7.0での変更

**既定値が変わったキー**（本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません）:

| キー | v0.6.0以前 | v0.7.0以降 | 出典 |
|---|---|---|---|
| `agent.subagent_max_turns` | `100` | `1000` | `config.md` 407・1849行 |
| `session.watchdog_rss_max_mb` | `0`（無効） | `1536` | `config.md` 1884行 |
| `agent.sandbox_allow_unsandboxed_exec`（Windowsで未宣言のとき） | 拒否（fail closed） | 許可（非サンドボックス実行） | `security.md` 309行、`windows-install.md` 285-305行 |

保存済みの設定に旧既定値が残っているかは `kirocrew config defaults` で確認できます（公式 `installation/` ページ「Check stored configuration defaults」、公式 `cli-reference` ページ）。

**新しいキー**: 上表の `agent.refusal_fallback_model`・`wakatime.enabled`・`dashboard.default_memory_mode`・`dashboard.export_include_layer_b` と、下記の Decisions（Jev）関連キー。

### Decisions（Jev）関連キー（**Preview**）

**Preview機能です。** **Settings → Developer → Feature Previews → Decisions (Jev)** を、カードに表示される送信先とデータ区分を確認したうえで有効にする必要があります。**同意は `config.json` の外に保存される**ため、エージェントが設定を編集して転送を有効にすることはできません。メインスイッチを入れても全動作が有効になるわけではなく、ターンごとのモデルの振り分けはチャットのモデルピッカーで **Auto (Jev)**、Steer-or-Queue の判断はビジー時の送信ボタンで **Auto (Jev)** を選びます。具体的なモデルを指定した場合は常に Auto (Jev) より優先され、スケジュールジョブ・サブエージェント・Appのリクエスト・remote crewのターンはそれぞれのモデル設定を使います。

| キー | 既定値 | 説明 |
|---|---|---|
| `decisions.bucket` | `100` | 対象となり得るセッションのうち、安定サンプルに含める割合（%） |
| `decisions.history_budget_chars` | `0` | 判断に添えて送る過去の会話の最大文字数。`0` は送らない |
| `decisions.model_route.simple` | `""` | Jev が simple と分類したメッセージのモデル。空なら現在のモデルのまま |
| `decisions.model_route.medium` | `""` | medium のメッセージのモデル |
| `decisions.model_route.complex` | `""` | complex のメッセージのモデル |

ガバナンスのプロファイルは `capabilities.decisions` でこのPreview全体をオフにできます（CHANGELOG.md v0.7.0節 304-305行）。

**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 表記あり）、CHANGELOG.md v0.7.0節 292-305行（`c67c506`）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## App manifest が宣言する項目（`config.json` のキーではない）

**v0.6.0 で追加されました。** 以下は App の manifest 側の宣言であり、`config.json` の設定キーではありません。混同しないよう分けて記載します。

| 項目 | 内容 |
|---|---|
| `permissions.jobs` | App がバックグラウンド処理を持つための権限宣言（CHANGELOG 125行） |
| `contributes.commands` | Cmd+K のCommand Barに行を追加する（CHANGELOG 127行） |
| `contributes.sessionControls` | コンポーザ横に**最大2つ**のライブコントロールを追加する（CHANGELOG 128行）。**表記はcamelCase**。詳細仕様は `docs/request-for-change/rfc-app-session-controls.md` にあるが、`docs/system-specs/` には見つかっていない |
| `capabilities.publish` | Artifact 公開の capability gate。`CapabilityGate` で `capability_default=False`（opt-in）（`governance.md` 2191行） |

App の権限モデル全体は [10_apps.md](../01_features/10_apps.md) を参照してください。

## 環境変数

| 変数 | 用途 |
|------|------|
| `KIROCREW_HOME` | データホームの変更（既定 `~/.kiro/crew/`） |
| `KIROCREW_PORT` | ダッシュボードポートの上書き（開発時） |
| `KIROCREW_TELEMETRY_DISABLED` | `1` で匿名テレメトリを無効化（Settings・`config.json`の設定を上書き） |
| `KIROCREW_VENV` | 仮想環境の場所の上書き |
| `KIROCREW_PROJECT_DIR` | プロジェクト単位のスキルディレクトリの参照先 |
| **`KIROCREW_CREW_LOG`**（v0.7.0） | `1` を設定して再起動すると、任意の追記専用 Crew log とセッションledgerを記録する。**既定は未設定（オフ）**、記録形式はpre-release（公式 `configuration/` ページの環境変数表、公式 `system/` ページ「Crew log (optional)」。[03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)参照） |
| `KIROCREW_ALLOW_SOURCE_BUILDS`（v0.7.0） | `1` でインストーラ・更新エンジンが事前ビルドwheelの無い依存をソースビルドすることを許可する（`install.md` 232-248行。[03_deployment/01_installation.md](../03_deployment/01_installation.md)参照） |

## 未確認事項

- `agent.max_subagents` の真の既定値（`subagent.md`は0、`config.md`は3。両併記のまま）
- `agent.subagent_auto_max` の真の既定値（32 vs 16。両併記のまま）
- `spawn_min_memory_gb` の既定値（`subagent.md`・`config.md`のいずれにも数値記載なし）
- `tunnel.enabled`・`slack.trusted_bot_ids` の既定値
- `agent.subagent_max_turns` に明示保存された `100` が、旧既定値の名残か意図した上限かの判別（`config.md` 410-416行は判別できないとして保持する。本サイトは表の既定値を `1000` とし、`kirocrew config defaults` による確認を案内する）
- `agent.sandbox_allow_unsandboxed_exec` の既定値の表記（リポジトリはWindowsで未宣言＝許可、公式 `configuration/` ページは `false`）
- `skills.max_triggered` の既定 `0` が v0.7.0 の変更か（CHANGELOG v0.7.0 は変更として記述、v0.6.0 の `config.md` も `0`）
- `agent.sandbox` が受け取る値（`auto`／`off` は確認済み）と、ガバナンスの順序尺度 `("off", "standard", "cc", "strict")` の対応関係
- `contributes.sessionControls` の仕様の確定状況（RFC（`docs/request-for-change/`）には記載があるが `docs/system-specs/` には見つかっていない）

> `session.pool_size` の食い違いは **v0.6.0 で解消**（両出典が `0`）したため、未確認事項から外しました。`dashboard.terminal.completion.enabled` の既定値は公式 `configuration/` ページの表（`true`）で確認したため外しました。

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
- ディレクトリ構造: [03_directory-layout.md](03_directory-layout.md)
- 上限値: [05_limits.md](05_limits.md)

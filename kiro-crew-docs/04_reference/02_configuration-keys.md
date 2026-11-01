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
**出典**（v0.9.0での再検証: 既定値の変更・新規キー・解消した食い違い）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.11.1での再検証: 既定ハーネスの既定値・新規キー・`dynamic_dashboard_cards`・`crewmates_onboarded`・解消した未確認事項）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-parity.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/learn-cron-dashboard.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/slack-gateway.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
**出典**（v0.11.1）: <https://kiro.dev/docs/crew/apps/manifest/>（Page updated 2026-09-25）・<https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-10-12）

---

## 📑 このページの内容

- [設定ファイル](#設定ファイル)
- [主な設定キー](#主な設定キー)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0・v0.8.0での変更](#v090v080での変更)
- [v0.7.0での変更](#v070での変更)
- [App manifest が宣言する項目（`config.json` のキーではない）](#app-manifest-が宣言する項目configjson-のキーではない)
- [環境変数](#環境変数)
- [未確認事項](#未確認事項)

---

## 設定ファイル

`~/.kiro/crew/config.json`（`config.local.json` によるオーバーレイあり）。

**v0.8.0〜v0.9.0 の読み書きの規則**（CHANGELOG.md v0.8.0節 685-691行、`modules/cli.md` 415行、`modules/config.md` 170行。いずれも `99e6253`。`kirocrew config set` の enum 検査は v0.8.0 の `cli.md` に既にあり、v0.7.2 の `cli.md` には無い記述です）:

- UTF-8 の BOM 付きで保存された `config.json`・`mcp.json`・ワークスペース設定・SKILL.md は、他のファイルと同じく読まれます。空の `mcp.json` は「サーバ無し」として読まれます。パースできない `config.json` は、テーマ・言語・オンボーディングの変更で既定値に上書きされません
- `kirocrew config set` は、enum を宣言するキーでは範囲外の値を拒否し（exit 1、選べる値を表示）、大文字小文字違いは正規形で保存します（`agent.log_level debug` → `DEBUG`）。**リスト型のキーは JSON 配列だけを受理**し、Windows PowerShell 5.1 が内側の引用符を落とした `[a,b]` は、書き込み前に exit 1 で拒否します
- `KIROCREW_HOME` は展開・解決され、ファイルシステムやドライブのルート、システムディレクトリは拒否されます（`config.md` 170行）

## 主な設定キー

`~/.kiro/crew/config.json` のキーです。**App の manifest が宣言する項目は別物**なので[後述の節](#app-manifest-が宣言する項目configjson-のキーではない)に分けています。既定値は v0.9.0 の `config.md` の dataclass（行番号は同ファイルの v0.9.0 のもの）と公式 `configuration/` ページで確認しました。`config.md` の dataclass は、公式ページの表に無いキーも載せています。**仕様書だけに記載があり公式ページの表に無いキー**は、説明の末尾にその旨を書きます。

| キー | 既定値 | 説明 |
|------|-------|------|
| `agent.sandbox` | `auto` | サンドボックスモード。**運用者が書く値は `auto`／`strict`／`off`** で、公式 `configuration/` ページ102行・公式 `security/` ページ「Sandbox modes」・`config.md` 2648行が一致します。`auto`（既定）は standard 層（Linuxはnamespace、macOSはseatbelt。macOSで有効時はkiro-cli内部のサンドボックスに委譲）で、`~/.aws`・`~/.ssh`・`~/.kube` は**見えます**。`strict`（v0.8.0〜。変更後に開始したセッションに適用）は、それらも隠すため、それらを使うツールは使えなくなります。**隠蔽対象は出典で表現が異なります**: `config.md` 2648行は `~/.aws`（`sso/cache` を含む）・`~/.ssh`（`known_hosts` を除く）・`~/.kube`・`~/.config/gh` と認証情報ファイル群（`_CC_FILES`）、CHANGELOG.md v0.8.0節 420-421行は「the cloud, ssh, kube and gh credential directories」と記述します（両併記。詳細は [09_security.md](../01_features/09_security.md)を参照）。`off` はKiro Crewのサンドボックスをスキップ。**それ以外の値は `auto` に戻ります**。`security-deep-dive.md` 108-110行の内部ティア（`standard`／`cc`）は「運用者が `agent.sandbox` に書く値ではない」と明記されています。**v0.7.2 以前は、README の3モードと内部ティア4種で値域が出典3系統に分かれて食い違っていましたが、v0.9.0 で公式・`config.md`・`security-deep-dive.md` が一致し、`README.md` からも該当文が無くなったため、解消しました** |
| `agent.provider` | `acp`（固定） | LLMプロバイダ（`config.md` 2647行）。変更不可。ハーネスの選択は `agent.acp_backend`（既定は KAS。v0.11.0〜。v0.9.0 以前は Kiro ハーネス）で行います。`overview.md` は「ACP-provider-only」、v0.9.0 の公式 `installation/` ページ19行は「the default provider path (`agent.provider = acp`)」と記述します（v0.7.2 の同ページは「the only provider」でした） |
| **`agent.acp_backend`**（v0.6.0） | **`ACP_BACKEND_KAS`（KAS）**。値が未設定または `""` は「選択なし」で、KAS が既定になる（v0.11.0〜。`harness-parity.md` 89行（H1）、`config.md` 110行、CHANGELOG.md v0.11.0節 151-153行。`fe6f5be`）。`ACP_BACKEND_KIRO` は常に選べる下限で、Kiro CLI を選ぶと保存値は `"kiro"`（実行時 id は `""`）になる。選択が保存されていない新規インストールが KAS で始まり、**明示した Kiro CLI の選択は維持される**。**v0.9.0 以前の既定は `ACP_BACKEND_KIRO`（Kiro ハーネス）でした**（`harness-parity.md` 84行・`c67c506`、`99e6253`） | セッションを動かすハーネスの選択。`acp_backends.resolve_selected_backend()` が値を正規化する。**Preview機能（Developer Mode 前提）**（v0.9.0 までの記述。v0.11.1 でも同じかは本ページでは確認しておらず、未確認です。[15_agent-backends.md](../01_features/15_agent-backends.md)参照）。⚠ 公式 `features/agent-backends/` ページ24行（Page updated 2026-10-12）は Kiro CLI を「Default backend」と記述しており、既定の記述が分かれます（裁定しない。[01_installation.md](../03_deployment/01_installation.md) の「v0.11.1での変更」を参照） |
| **`agent.member_acp_backend`**（v0.6.0） | `kas` | Crew member のハーネス（`session-control.md` 235行。v0.11.1 でも既定 `kas` で、`session-control.md` 1307行）。保存値 `"kiro"` は KAS として読まれる（`config.md` 110行） |
| **`agent.deepseek_env`**（v0.8.0） | 空 | DeepSeek Harness の環境変数名を **Settings → Secrets** の `secret://` 参照へ対応づける。DeepSeek Harness は **Developer Mode が有効なとき**に Developer ページの Agent Backend タブで選べる（ホストに `dsh` が必要。CHANGELOG.md v0.8.0節の見出しは「More backends, and hooks you can author (Preview)」）（公式 `configuration/` ページ104行） |
| `agent.max_subagents` | **`0`（auto）** | Subagentの並行数上限。`0` は `agent.subagent_auto_max` の上限まで。明示ピンはロード時 `[3, 64]`（`config.md` 2653行、`subagent.md` 112行）。**v0.7.2 の `config.md` の dataclass は `3` で、`subagent.md`（`0`）と食い違っていましたが、v0.8.0 で両者が `0` に一致し、解消しました（v0.8.0 タグの `config.md` 1993行・`subagent.md` が `0`。v0.9.0 でも同じ）** |
| `agent.subagent_auto_max` | **`32`** | 自動サイジングの上限（`[3, 64]`にロード時クランプ）（`config.md` 2654行、`subagent.md` 112行）。**v0.7.2 の `config.md` の dataclass は `16` で、`subagent.md`（`32`）と食い違っていましたが、v0.8.0 で一致し、解消しました（v0.8.0 タグの `config.md` 1994行が `32`。v0.9.0 でも同じ）** |
| `agent.spawn_min_memory_gb` | **`2.0`** | サブエージェントの起動を許可したあとにホストに残すべき空きメモリ（GiB）。`<= 0` で無効。`config.md` 623行は旧既定値 `4.0` からの変更（#15890）で、保存済みの `4.0` は自動で採用される。CHANGELOG.md v0.8.0節 673-676行は「4.5 GB free を要した」と記述しており、`4.0` との差の理由は一次情報に書かれていません（`subagent.md` 114行、`config.md` 623行）。**公式 `configuration/` ページの表には無いキー** |
| `agent.subagent_queue_max_wait_secs` | `1800` | `spawn_min_memory_gb` で保留された spawn が待つ最長時間（秒）。`[0, 86400]`、`0` は無制限（`config.md` 2665行）。**公式ページの表には無いキー** |
| `agent.session_start_concurrency`・`agent.cold_start_concurrency`・`agent.runtime_spawn_concurrency` | **`"auto"`**（v0.7.2 の `session_start_concurrency` は `2`） | ACP の `session/new` の同時数（`"auto"` は `clamp(min(cpus // 4, available_GB // 3), 2, 16)`、整数は `[1, 64]`）、バックグラウンドのコールドスタートの同時数（`"auto"` は上の幅を `[4, 16]` に丸めた値、整数は `[1, 32]`）、ACP runtime の spawn の同時数（`"auto"` は上の幅の半分を `[2, 8]` に丸めた値、整数は `[1, 32]`）。**いずれも要再起動**（`config.md` 2667・2669・2670行・641行の台帳『2 -> "auto", #17055』）。**公式ページの表には無いキー** |
| `agent.child_env_defaults` | `{}` | kiro-cli の子プロセスへ、キーが未設定の場合だけ渡す環境変数。許可リストは `TOKIO_WORKER_THREADS` と `RAYON_NUM_THREADS` だけで、値は 1〜1024 の10進文字列。それ以外は警告つきで捨てられる（`config.md` 2668行）。運用者のオプトイン。**公式ページの表には無いキー** |
| `agent.dangerously_skip_permissions` | `false` | 永続的な全 tool 承認。**要再起動**。真偽値でない値が書かれても付与にはならない（`config.md` 2651・1502行）。セキュリティ上の注意: 承認を迂回する設定です。**公式ページの表には無いキー** |
| `agent.yolo_duration` | `6h` | アドホックな自動承認の期間（`30m\|1h\|6h\|12h\|24h\|until_shutdown`。ハード上限 24h）（`config.md` 2652行、`security.md` 613行）。**v0.7.2 の `config.md` の dataclass にあった `agent.yolo`（永続的な YOLO モード）は、v0.9.0 の dataclass にありません**。`security.md` 2918行は「There is no permanent YOLO mode」と記述します。除かれた理由と移行の扱いは一次情報に書かれていません。**公式ページの表には無いキー** |
| `agent.apps_allow_third_party` | `false` | サードパーティAppの実行許可スイッチ |
| `agent.sandbox_allow_unsandboxed_exec` | `false`（**Windowsでは未宣言時に許可**。下記注記） | サンドボックスバックエンド不在時の非サンドボックス実行を許可するopt-in。**v0.7.0 以降、未宣言の値はプラットフォーム依存で解決され、Windowsでは許可・それ以外ではfail-closed**（`security.md` 763-767行。v0.7.2 のタグでは 309行）。Windowsで拒否するには `false` を明示的に宣言する（宣言値はどちらの向きでもプラットフォーム既定に優先）。**v0.11.0 以降の既定ハーネス KAS は、Windows では未宣言のプラットフォーム既定で OS による閉じ込め無しで動き、`false` を宣言すると、設定名を示して拒否されます**（Kiro CLI ハーネスは Kiro CLI のサンドボックスへ委譲。`windows-install.md` 307-315行、`fe6f5be`）。⚠️ 公式 `configuration/` ページの表（103行）は既定 `false`「only when explicitly enabled」と記載しており、プラットフォーム差に触れていません（**食い違いは継続**。裁定しない。[03_deployment/02_windows.md](../03_deployment/02_windows.md)参照。`README.md` は v0.9.0 から食い違いの当事者から外れたままです） |
| **`agent.refusal_fallback_model`**（v0.7.0） | `""`（空＝無効） | コンテンツフィルタで拒否されたメッセージを1回だけ再試行するモデル。Settings → Chat でスロットル時のフォールバックの隣で選ぶ。次のターンでは主モデルに戻る（CHANGELOG.md v0.7.0節 356-359行、公式 `configuration/` ページ） |
| `agent.chat_turn_timeout_secs` | **`14400`（4時間）** | チャットターンの上限（ロード時クランプは300〜86400秒、無効化不可）。**v0.5.0以前は`7200`（2時間）**。`resource-protection.md` 49行は「14400 is the default, not the ceiling」と明記 |
| `agent.tool_approval_timeout_secs` | `600`（10分） | ツール承認の待機時間（ロード時クランプは30〜7200秒、かつ `chat_turn_timeout_secs` より60秒以上小さい値へ丸められる） |
| **`agent.subagent_timeout_secs`**（v0.6.0） | **`10800`（3時間）** | Subagent 1件あたりのハードタイムアウト。**v0.5.0以前は1800秒の固定値**（設定不可）。ロード時クランプは60〜86400秒、`0` は既定値を使うsentinel。**⚠️ ダッシュボードからは設定できません**（`resource-protection.md` 374-377行。CLIか`config.json`の編集が必要） |
| `agent.subagent_max_turns` | **`1000`**（**v0.6.0以前は`100`**） | Subagent 1件あたりのツール呼び出し予算。ロード時クランプは`[1, 1000]`（v0.6.0 で上限が200→1000に拡大済み）。**v0.7.0 で既定値が変わりました**（`config.md` 1849行・407行「`agent.subagent_max_turns` (100 -> 1000, #12203)」、公式 `configuration/` ページの表も `1000`）。**キーが未設定なら、更新後の既存インストールも含めて自動で1000に追従**します。**保存済みの値は100であっても保持**されます（旧既定値として書き込まれた100と、意図して選んだ100を区別できないため。`config.md` 410-416行）。保存値の確認と採用／維持は `kirocrew config defaults`（`--adopt`／`--keep`）で行います。本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません |
| **`agent.subagent_stall_idle_secs`** | `120` | ストリーム無活動が続いたときにSubagentを「停滞」表示するまでの秒数 |
| **`agent.completion_keep_chars`** | `3000` | 親セッションへ注入する完了イベントの文字数上限 |
| `agent.subagent_result_ttl_secs` | `3600` | 配送済みSubagentの`result.txt`を保持する秒数 |
| **`agent.session_control`**（v0.6.0） | **`true`** | セッション制御（外部からのcreate／stop／send-to）。`false` を明示すると403で拒否される（`session-control.md` 144行）（[17_workflows.md](../01_features/17_workflows.md)参照） |
| **`orchestrator.max_plan_duration_seconds`**（v0.6.0） | `7200`（2時間） | 無人 auto-run plan 全体の実時間予算。`0` で無効化（公式 `configuration/` ページ101行「Whole-plan limit for unattended auto-run plans; `0` removes it」、CHANGELOG.md v0.6.0節。v0.9.0 のタグでは 1410行）。ステージ境界でのチェック・75%での警告・stage-gated な plan の扱いは v0.7.2 の `autopilot.md` の記述で、**`autopilot.md` は v0.9.0 に存在しません**（下の `orchestrator.stage_timeout_seconds` の行を参照。[06_autonomy.md](../01_features/06_autonomy.md)参照） |
| **`orchestrator.stage_timeout_seconds`**（v0.6.0） | **未確認** | v0.7.2・v0.8.0 の `autopilot.md`（v0.7.2 で 499行、v0.8.0 で 501行）は、既定 `1800` でステージ単位の時間予算（`0` でチェック無効）と記述していました。**`autopilot.md` は v0.9.0 のタグに存在せず**（`taskq.md` 464行が「the retired chat Autopilot」と呼ぶ記述がある）、`stage_timeout_seconds` は v0.9.0 の `docs/system-specs/`・`docs/architecture/`・公式ドキュメントのいずれにも見つかりません。削除の理由と、このキーが現在も有効かどうかは、CHANGELOG.md v0.8.0節・v0.9.0節にも記載がなく、本サイトは判断しません。既定値を断定しません。公式 `configuration/` ページは `orchestrator.max_plan_duration_seconds` を引き続き設定表に載せています |
| `session.pool_size` | `0`（無効） | Warm Poolのサイズ。**v0.6.0で`overview.md`と`config.md`が`0`で一致**（以前は`2`との食い違いを両併記していた）。ロード時クランプ上限は`POOL_SIZE_MAX = 10` |
| `session.pool_ttl_secs` | `1800` | Warm Pool内プロセスのTTL（v0.6.0でも変更なし） |
| `session.timeout_secs` | `3600`（60分） | セッションのアイドルタイムアウト |
| `session.autocompact_pct` | **`70`** | 自動圧縮のコンテキスト使用率閾値（ロード時クランプは5.0〜90.0）。**⚠️ 本サイトは以前`90`と記載していました**。`config.md` 221行は既定値の変更履歴として `90.0 -> 70.0` を挙げています |
| `session.watchdog_rss_max_mb` | **`0`（無効）**（v0.7.0〜v0.8.0は `1536`） | プロセスツリーのRSSがこのMiBを超えたセッションを再生成する。`0` で無効。**v0.9.0 で既定が `0` に戻りました**（`config.md` 2696行。634行の台帳『1536 -> 0, #16393』）。dataclass のコメントは「a fixed ceiling cannot tell a leak from a session with many MCP servers」と説明します。`0` のときも、内部のバックグラウンドランタイムは 1536 MiB（`BACKGROUND_RSS_FALLBACK_MB`）で再生成されます。ターン実行中のセッションと、サブエージェントが実行中・キュー待ち・結果配送中の親セッションは、引き続き対象外です。保存済みの `1536` は保持され、`kirocrew config defaults` で確認できます。`win` 644行（`windows-install.md`）も「default `0`, off」と記述します。**v0.7.0〜v0.8.0 の `config.md` は `1536`（v0.7.2 の 1884行「Non-zero by default so a runaway session tree is bounded out of the box」）でした。本内容は仕様書で確認したもので、CHANGELOG.md v0.8.0節・v0.9.0節/Release 本文は説明していません** |
| `taskrunner.max_parallel_steps` | **`0`（auto）**（v0.7.2 は `2`。v0.8.0 タグの `config.md` 2035行で既に `0`） | 並列グループ内で同時実行するステップセッションの最大数。`0` はホストのメモリから算出した上限、正の値はその上限を**下げるだけ**（`config.md` 2700行、`taskrunner.md` 247行）。本内容は仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。**公式ページの表には無いキー** |
| `memory.history_idle_hours` | `3.0` | 履歴統合のアイドルトリガー |
| `memory.history_max_days` | `365` | 履歴のディスク保持期間 |
| **`memory.persistence_enabled`**（v0.8.0〜） | `true` | 自動のメモリ書き込み（lessons・統合・task-runner）を有効にする全体スイッチ。`false` にすると、Gateway がセッションをメモリへ蒸留すること自体を止め、保存済みメモリ・lessons の注入も止まる（公式 `configuration/` ページ110行、`config.md` 2710行） |
| **`memory.inject_memory`／`memory.inject_lessons`／`memory.inject_activity`**（v0.8.0〜） | いずれも `true` | 新セッションの文脈へ、保存メモリ（preferences・activity index・直近セッションの抜粋）／学習した修正と USER PROFILE／直近のプロジェクト・履歴・タスク事実・過去エピソードを加える。`inject_activity` は `inject_memory` が前提（公式 `configuration/` ページ111-113行、`config.md` 2711-2714行）。`memory.inject_lessons_per_turn`（既定 `false`。続きのメッセージで、まだ見せていない一致 lesson を最大3件加える。`inject_lessons` が前提）は `config.md` 2713行のみにあり、公式ページの表には無い |
| `memory.embedding_provider` | `llama_cpp`（固定。legacy値も強制コアース） | メモリシステムの埋め込みプロバイダ |
| `skills.lazy_load` | **`true`** | スキルのon-demand注入方式。`true`（既定）は、利用順位付きの有界な索引（パスとファミリー行つき）。`false` は、短い8名の `skill_search` エントリ（`config.md` 2770行）。**本サイトは以前、既定を `false` と書いていました。これは v0.7.2 以前からの誤りでした**（v0.7.2 の `config.md` 1950行の dataclass も既に `True`）。0.6.x 以前は `false` が全スキル一覧の既定だったため、旧設定が保存した `false` は 0.7 以降では最も狭いモードを選びます（`config.md` 574-577・797-800行。632行の台帳『false -> true, #12131』） |
| **`skills.max_triggered`** | `0` | 1メッセージあたりに注入する一致スキルの最大数。**`0` はトリガー注入を無効にするが、スキルの発見（短い索引と `skill_search`）は止めない**。正の整数で旧来の注入動作に戻る（CHANGELOG.md v0.7.0節 419-422行、公式 `configuration/` ページ）。⚠️ CHANGELOG は v0.7.0 の変更として「defaults to 0」と記述していますが、v0.6.0 の `config.md` 1019行も既に `max_triggered: int = 0` でした（裁定しない）。Jev（Decisions）の自動スキル選択にも `0` より大きい値が必要 |
| **`auto_update`** | `true` | ソースインストールの更新確認。**v0.7.0 から起動時に加えて12時間ごと**に確認する（公式 `configuration/` ページ、CHANGELOG.md v0.7.0節 148-150行。[03_deployment/01_installation.md](../03_deployment/01_installation.md)参照） |
| **`wakatime.enabled`**（v0.7.0） | `false` | WakaTimeのコーディング時間連携。有効にするとコーディング活動のheartbeatをWakaTimeへ送り、アカウントの統計を読む。APIキー（`WAKATIME_API_KEY`）は **Settings → Secrets** のvaultにのみ保存でき、`.env`や`config.json`からは読まれない（公式 `configuration/` ページ「Coding hours with WakaTime」、CHANGELOG.md v0.7.0節 100-103行） |
| `hooks.denied_commands.user_added` | – | インポート等で追加されたユーザー定義の拒否ルール |
| `mcp_gateway.enabled` | – | MCP Gatewayの有効化 |
| `dashboard.url` | 省略時 `localhost:5476` | ダッシュボードの到達先URL |
| **`dashboard.terminal.completion.enabled`**（v0.6.0） | **`true`** | 内蔵ターミナルの補完。`false` にすると無効化され、SEL監査イベント `terminal.complete` に `feature_disabled` が記録される。既定値は公式 `configuration/` ページの表で確認（v0.6.0 の同ページにも `true` と記載あり。本サイトは以前「未確認」としていました） |
| **`dashboard.default_memory_mode`**（v0.7.0） | `persistent` | 新しいダッシュボードチャットのメモリモード（`persistent`／`incognito`／`temporary`）。ユーザーが作るダッシュボードチャットにのみ適用（`config.md` 1963行、公式 `configuration/` ページ） |
| **`dashboard.verbosity`** | **`answer_only`**（新規インストールのみ） | Settings → Chat → Transcript → Response Verbosity。新規インストールは Answer only で始まり、既存の config は保存済みの水準を保つ。`ultra` は廃止され、保存済みの `ultra` は `answer_only` として扱われる（公式 `configuration/` ページ43行、`config.md` 2784行） |
| **`dashboard.title_refresh_every_turns`**（v0.8.0） | `0` | 自動生成タイトルを N ターンごとに再評価し、話題が移ったら付け替える。`0` は組み込みのスケジュール。更新ごとにバックグラウンド呼び出し1回。利用者が付けたタイトルには触れない（公式 `configuration/` ページ108行、CHANGELOG.md v0.8.0節 273-278行（`99e6253`）） |
| `dashboard.dynamic_dashboard_cards` | `false` | セッション単位のイベント駆動 HTML カードを、`session_summary` なしで有効にする。ホット適用。**Settings → Developer の専用カードにある「Automatic cards for all sessions」スイッチが書き換える設定**で、ゲートウェイ全体の費用設定のため既定オフ（`learn-cron-dashboard.md` 3078-3082行、`artifacts.md` 152-154行、`config.md` 158-160行。`fe6f5be`）。Dashboard タブ自体は v0.10.0 で Feature Preview が不要になり、このスイッチが独立したカードに移った（CHANGELOG.md v0.10.0節 249-252行）。**v0.9.0 の記述（Settings → Developer → Feature Previews → Dynamic Dashboard の Preview。CHANGELOG.md v0.9.0節 30-42行）は v0.10.0 で変わりました**。画面のスイッチとキーの対応は v0.9.0 では「未確認」としていましたが、解消しました。**公式ページの表には無いキー** |
| `dashboard.folder_sort`・`dashboard.crewmates_onboarded` | `custom`・`false` | サイドバーのフォルダ順（`custom`／`name`／`created`）（`config.md` 2788行）／**廃止された Meet Mates フロー（guided create）の legacy 記録で、何も読まない**（`config.md` 3129・4115-4120行、`fe6f5be`。**v0.9.0 の説明「最初の Meet CrewMates の流れを終えたか」は現在の説明ではありません**。キー名は crewmate のまま。既定値は変わらない）。**公式ページの表には無いキー** |
| `stt.transcribe_vocabulary` | 空 | Amazon Transcribe の既存のカスタム語彙名。transcribe プロバイダのみ（`config.md` 2749行。**公式ページの表には無いキー**） |
| `session.compact_wait_secs`（v0.9.0） | `0` | Settings → Chat → Advanced → Compaction Time Limit。`0` は既定の300秒、それ以外は 60〜3,600 秒に丸められる（公式 `configuration/` ページ44行） |
| `session.idle_exempt_keys` | `[]` | アイドル期限で失効させないセッションキー。最大10キー、各512文字（`POOL_SIZE_MAX` ＝ 10）。RSS 再生成が有効なら引き続き対象。運用者のオプトイン（`config.md` 2691行。**公式ページの表には無いキー**） |
| **`mcp.honour_auto_approve`**（v0.8.0） | `true` | `mcp.json` や agent ファイルに**所有者が書いた** `autoApprove` リストを尊重する。`false` にして**Gatewayを再起動**すると、サーバが安全と宣言していない tool がすべて Crew の gate を通る。アプリ自身のリストは設定にかかわらず尊重されない（公式 `configuration/` ページ114行、`config.md` 2547行）。セキュリティ上の意味は [09_security.md](../01_features/09_security.md)を参照 |
| **`monitoring.max_runtime_secs`**（v0.8.0） | `604800`（7日） | 新規または更新する監視の運用者上限。最大30日（公式 `configuration/` ページ115行、CHANGELOG.md v0.8.0節 530-533行（`99e6253`）） |
| **`dashboard.export_include_layer_b`**（v0.7.0） | **オフ** | セッションのエクスポートに正確なモデルコンテキストを含め、インポート時にプレフィックスの再生ではなく再開できるようにする（CHANGELOG.md v0.7.0節 377-378行） |
| **`dashboard.browser_view_port`**（v0.5.0） | OSが自動割り当て | ブラウザビューの公開ポートを固定する（`browser.md` 341行） |
| **`instances.enabled`**（v0.6.0） | **`false`（既定オフ）** | Remote crews（別crewの接続・Remote crew sessions）。**Preview機能**（`instances.md` 6行「Opt-in: off by default」）。**Gateway は起動時にこの値を読むため、変更後に再起動が必要**です（v0.9.0 の公式 `features/multi-instance/` ページ35行、`config.md` 2547行）。v0.7.2 の同ページは「This setting applies live in 0.7」と記述していました（[03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)参照） |
| `instances.warm_set_cap` | `0` | 固定のwarmトンネル上限。`0` は自動サイズで、最大8（公式 `configuration/` ページ121行、同 `features/multi-instance/` ページ88行）。v0.7.2 の公式 `configuration/` ページにも既に載っていました（`config.md` 629行の台帳は『5 -> 0, #7248』） |
| **`telemetry.enabled`**（v0.6.0） | **`false`** | ローカルのメトリクス収集の有効化。**これだけではネットワークへのエクスポートは行わない**（OTLP送信には `telemetry.otlp_endpoint` の設定と `kirocrew[otlp]` extra の導入が別途必要。`telemetry-otlp-export.md` 17-23行、公式 `configuration/` ページ「it does not export them」）。**匿名利用テレメトリとは別系統**（[03_deployment/06_telemetry-and-privacy.md](../03_deployment/06_telemetry-and-privacy.md)参照） |
| **`tunnel.enabled`**（v0.5.0） | 未確認 | 公開HTTPS URLでダッシュボードを露出するトンネル。`kirocrew gateway --no-tunnel` はこの設定に関わらずトンネルを張らない（`cli.md` 150行） |
| **`publish.allowed_destinations`**（v0.6.0） | default-open の allowlist | Artifact 公開先の許可リスト（`governance.md` 2200行）（[12_artifacts.md](../01_features/12_artifacts.md)参照） |
| **`slack.trusted_bot_ids`**（v0.5.0） | **空のリスト**（すべての bot メッセージを破棄） | 信頼するSlack bot ID。挙げた `bot_id` だけが blanket の `bot_id` フィルタを通り、リストに無い bot id は拒否される（fail-closed）。`slack-gateway.md` 1786行（`fe6f5be`）。**v0.9.0 の `slack-gateway.md` 1585行（`99e6253`）にも同じ記述があり、v0.9.0 までこの既定値を「未確認」としていたのは、本サイトの見落としでした** |
| **`telegram.bot_token`**（v0.3.0） | `""`（空） | **Telegramのbot token（@BotFather発行）。v0.3.0でmulti-accountが撤回され、単一トークンのみが受理されるようになった**。従来のaccount mapは**parseされ保持されるが読まれない**。**`config.md` 753行は「prefer the `TELEGRAM_BOT_TOKEN` credential」と記述しており、設定ファイルに直接書くよりも認証情報（環境変数・`.env`）経由が推奨されます**（[01_features/11_interfaces.md](../01_features/11_interfaces.md)参照） |
| **`knowledge.auto_ingest_artifacts`**（v0.3.0） | **`false`** | **Knowledge Libraryへのローカルartifact自動取り込み。v0.3.0でopt-in（既定オフ）化された**。有効にすると既存のartifactもバックフィルされる（[01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)参照） |
| **`knowledge.embed_timeout_secs`** | `10.0` | Knowledge Libraryの1リクエストあたり埋め込みタイムアウト（秒）。0・未設定は組み込みの既定値10秒になる |

## v0.11.1での変更

v0.10.0・v0.11.0・v0.11.1 に「Before you upgrade」節はありません。呼称は v0.11.0 から UI・CHANGELOG が Mate に変わりました（v0.10.0 以前・公式ページでは crewmate。`dashboard.crewmates_onboarded` などのコード識別子・設定キー・API パスは crewmate のままです）。

**既定値が変わりました**: `agent.acp_backend` の既定が KAS になりました（v0.11.0。上の「主な設定キー」の表）。これ以外に、**既存の設定キーの既定値の変更は見つかっていません**。v0.9.0 と v0.11.1 の `config.md` の dataclass を、フィールドごとに機械的に比較した結果は、既存フィールドの既定値の変更 0 件、追加 14 フィールドでした。

**追加された設定キー**（下の表のうち、`config.md` の dataclass にあるものは v0.9.0 の dataclass にありません）。**公式 `configuration/` ページ（Page updated 2026-10-20）の表には、下のキーはどれも載っていません。** 各行の「CHANGELOG」は、CHANGELOG にそのキーまたは機能の説明があることを示します。説明が無い行は、`config.md` の差分にだけある項目です。

| キー | 既定値 | 内容 | 版・出典 |
|---|---|---|---|
| `agent.env` | `{}` | すべてのエージェント子プロセスに追加する環境変数（例 `HTTPS_PROXY`・`NODE_EXTRA_CA_CERTS`）。非機密値向け。禁止名・禁止接頭辞／接尾辞は、読み込み時に警告付きで破棄され、保存時に拒否される | v0.10.0。`config.md` 2990行、CHANGELOG.md v0.10.0節 318-319行 |
| `aws.project_profiles` | `{}` | 絶対パスのプロジェクトフォルダ → AWS プロファイルの対応。間違ったアカウントでコマンドを実行するのを防ぐための設定で、隔離ではない（エージェントは `--profile` を渡せる） | v0.10.0。`config.md` 3097・3358-3375行、CHANGELOG.md v0.10.0節 320-321行 |
| `agent.bot_name` | `""`（プロバイダの既定の名前＝Kiro） | エージェントが会話で名乗る名前（プロンプトの `{bot_name}` プレースホルダ）。NFC 正規化され、50 コードポイントを上限に、Unicode の文字などに絞られて読み込まれる | `config.md` 2968行。CHANGELOG に説明なし。`dashboard.bot_name` とは別のキー |
| `agent.model_context_tokens` | `{}` | モデル id ごとの提供コンテキスト窓（整数 1024〜10000000、先頭 64 件を読む） | v0.10.0。`config.md` 2966行、CHANGELOG.md v0.10.0節 326-328行 |
| `memory.writes_enabled` | `true` | オフにすると自動の書き込みが止まる（注入と `memory_recall` は続く） | v0.10.0。`config.md` 3035行、CHANGELOG.md v0.10.0節 334-336行 |
| `memory.lesson_extraction_enabled` | `true` | オフにすると lesson の自動抽出が止まる（他の書き込みと `learn_add` は続く） | v0.10.0。`config.md` 3036行、CHANGELOG.md v0.10.0節 334-336行 |
| `memory.embedding_idle_evict_secs` | `3600`（`0` で解放しない） | 埋め込みモデルのアイドル解放までの秒数 | v0.10.0。`memory-skills-hooks.md` 2644行、CHANGELOG.md v0.10.0節 371-372行 |
| `memory.startup_recall_timeout_secs` | `1.0`（0〜10 に丸められる） | セッション開始時の初回メッセージの埋め込みを待つ時間 | `config.md` 3041行。CHANGELOG に説明なし |
| `stt.transcribe_languages` | `[]` | Amazon Transcribe が 2〜5 言語を 1 ストリームで検出する（ライブのみ） | v0.10.0。`config.md` 3079行、CHANGELOG.md v0.10.0節 355-357行 |
| `stt.threads`・`stt.submit_on_release`・`stt.custom_model_path`・`stt.custom_model_sha256` | `0`・`false`・`""`・`""` | ローカルの STT のスレッド数、意図的な停止での送信、カスタムモデル（パスと sha256 の両方が無いと `custom` は既定に戻る） | `config.md` 3070・3072・3080-3081行。CHANGELOG に説明なし。CHANGELOG.md v0.11.0節 141-143行は「Settings → Voice → Fine-tuning で意図的に停止した dictation を送信できる」と記述するが、`stt.submit_on_release` との対応は一次情報に明記がない |
| `taskrunner.test_command`・`taskrunner.require_verification` | `[]`・`false` | 各ステップのあとに実行するテスト（シェルを使わない argv）と、テストが exit 0 のときだけステップを通す設定 | `config.md` 3024-3025行。CHANGELOG に説明なし |
| `dashboard.session_sort` | `"date-desc"` | サイドバーのセッションの並び順（`date-desc`／`date-asc`／`created-desc`／`created-asc`／`name-asc`／`name-desc`／`manual`）。ブラウザではなくゲートウェイに保存されるため、どのブラウザでもデスクトップアプリでも同じ順になる | v0.11.0。`config.md` 3125・3744-3750行、CHANGELOG.md v0.11.0節 113-116行 |
| `dashboard.github_hosts` | 既定値の記載は見つかっていない | GitHub Enterprise のホストを追加する | v0.10.0。CHANGELOG.md v0.10.0節 325-326行 |
| `dashboard.bitbucket_server_hosts` | 既定値の記載は見つかっていない | Bitbucket Server のプルリクエストの読み取り | v0.11.0。CHANGELOG.md v0.11.0節 174-175行 |
| `agent.kas_bundle` | `false`（全プラットフォームで既定オフ。シャドウテスト中） | 組み込みの KAS エンジン経路（そのために kiro-cli が要らない）。Settings → Developer → Feature Previews の「Run KAS on Kiro Crew's own engine」が同じ設定。変更後に再起動する | v0.10.0（スイッチの場所は v0.11.0 で変更）。`install.md` 595-605行、`acp-client.md` 3621行、CHANGELOG.md v0.10.0節 299-301行・v0.11.0節 154-157行 |
| `agent.kas_bundle_url` | 既定値の記載は見つかっていない | KAS エンジンの取得元（https のベース）。`kirocrew kas install` の `--url` の既定 | `cli.md` 384行、`acp-client.md` 3624行。CHANGELOG に説明なし |
| `agent.kas_persist_mcp_sign_in` | `false`（既定オフ） | KAS 上のリモート MCP のサインインをセッション間で保持する | v0.11.0。`acp-client.md` 2205行、CHANGELOG.md v0.11.0節 158-161行 |

**設定キーではない項目**: cron ジョブごとの自動停止の閾値 `auto_pause_limit`（既定 5、`0` で自動停止しない）は、`kirocrew cron add／update --auto-pause-after N` と Schedule フォームで設定します（v0.11.0。`cli.md` 343・1441行、`learn-cron-dashboard.md` 1227行、CHANGELOG.md v0.11.0節 128-137行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
出典: CHANGELOG.md v0.10.0節・v0.11.0節（`fe6f5be`）

## v0.9.0・v0.8.0での変更

v0.8.0・v0.9.0 に「Before you upgrade」節はありません。既定値が変わったキーは次のとおりです（**既定値が変わりました**）。本内容は v0.9.0 タグの仕様書・公式ページで確認したもので、CHANGELOG.md v0.8.0節・v0.9.0節/Release 本文が説明しているのは、`memory.*` の新規キーなど一部です。

| キー | v0.7.2 | v0.9.0 | 出典（`config.md`、v0.9.0） |
|---|---|---|---|
| `session.watchdog_rss_max_mb` | `1536` | `0`（無効。v0.8.0 までは `1536`） | 2696・634行 |
| `agent.max_subagents` | dataclass `3` | `0`（auto） | 2653行 |
| `agent.subagent_auto_max` | dataclass `16` | `32` | 2654行 |
| `taskrunner.max_parallel_steps` | `2` | `0`（auto） | 2700行 |
| `agent.session_start_concurrency` | `2` | `"auto"` | 2667・641行 |
| `agent.spawn_min_memory_gb` | 仕様書に数値の記載なし | `2.0`（旧既定 `4.0`） | 623行、`subagent.md` 114行 |
| `dashboard.verbosity` | dataclass `"default"`（`config.md` 1964行） | 新規インストールは `answer_only`（既存の config は保存済みの水準を保つ） | 2784行、公式 `configuration/` ページ43行 |
| `agent.sandbox` | `auto`／`off`（`strict` なし） | `strict` が追加（v0.8.0） | 2648行 |

保存済みの設定に旧既定値が残っているかは `kirocrew config defaults` で確認できます。`agent.yolo`（永続的な YOLO モード）が dataclass から無くなり、`agent.yolo_duration`・`agent.dangerously_skip_permissions` が加わったこと（上表）、`mcp.honour_auto_approve`・`memory.*`・`agent.deepseek_env` などの新規キー（上表の（v0.8.0）（v0.9.0）の行）も併せて参照してください。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.7.0での変更

**既定値が変わったキー**（本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません）:

| キー | v0.6.0以前 | v0.7.0以降 | 出典 |
|---|---|---|---|
| `agent.subagent_max_turns` | `100` | `1000` | `config.md` 407・1849行 |
| `session.watchdog_rss_max_mb` | `0`（無効） | `1536`（**v0.9.0 で `0` に戻りました**。上記「[v0.9.0・v0.8.0での変更](#v090v080での変更)」） | `config.md` 1884行（v0.7.2 のタグ） |
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
| `contributes.sessionControls` | コンポーザ横に**最大2つ**のライブコントロールを追加する（CHANGELOG 128行）。**表記はcamelCase**。各コントロールは `id`・`entryPoint`・`label`・`icon`・`statusPath` を持つ。**詳細仕様は公式 `apps/manifest/` ページ（`docs_md/apps__manifest.md` 249-267行。Page updated 2026-09-25）に記載がある**（`docs/system-specs/` には引き続き無い。v0.9.0 までこの仕様の確定状況を「未確認」としていたのは、本サイトの見落としでした。公式ページは v0.9.0 の時点で既にこの内容でした） |
| `app.json` の cron の `strict_schedule` | App の cron ジョブを、ジッターなしで分の頭に開始する（v0.11.0。CHANGELOG.md v0.11.0節 131-132行、`learn-cron-dashboard.md` 622-624行）。`config.json` のキーではない |
| `capabilities.publish` | Artifact 公開の capability gate。`CapabilityGate` で `capability_default=False`（opt-in）（`governance.md` 2191行） |

App の権限モデル全体は [10_apps.md](../01_features/10_apps.md) を参照してください。

## 環境変数

| 変数 | 用途 |
|------|------|
| `KIROCREW_HOME` | データホームの変更（既定 `~/.kiro/crew/`）。値は展開・解決され、ファイルシステムやドライブのルート、システムディレクトリは拒否される（`config.md` 170行、v0.9.0） |
| `KIROCREW_PORT` | ダッシュボードポートの上書き（開発時） |
| `KIROCREW_TELEMETRY_DISABLED` | `1` で匿名テレメトリを無効化（Settings・`config.json`の設定を上書き） |
| `KIROCREW_VENV` | 仮想環境の場所の上書き |
| `KIROCREW_PROJECT_DIR` | プロジェクト単位のスキルディレクトリの参照先 |
| **`KIROCREW_CREW_LOG`** | **未設定で有効**（v0.8.0〜）。Gateway の起動前に `0` を設定すると、Crew log とセッションledgerの記録をプロセス全体で無効にする。`0`／`false`／`no`／`off` と認識できない値で無効、未設定・空・`1`／`true`／`yes`／`on` で有効（公式 `configuration/` ページ159行「enabled when unset」、公式 `system/` ページ、`crew-log-emitter.md` 32-36行。[03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)参照）。**v0.7.2 までは既定オフで、`KIROCREW_CREW_LOG=1` と再起動が必要でした** |
| `KIROCREW_ALLOW_SOURCE_BUILDS`（v0.7.0） | `1` でインストーラ・更新エンジンが事前ビルドwheelの無い依存をソースビルドすることを許可する。**オプトインは記憶されない**。更新中にコンパイルするには、ツールチェーンが `PATH` にあるシェルから `KIROCREW_ALLOW_SOURCE_BUILDS=1 kirocrew update` を実行する（Gateway の自動更新・承認済み更新のビルド手順は信頼されたシステム `PATH` だけで動く）（`install.md` 259-268行。v0.7.2 の記述は「サービスユニット側にも設定が必要」でした）（[03_deployment/01_installation.md](../03_deployment/01_installation.md)参照） |
| `KIROCREW_KIRO_BIN` | 絶対パスなら、Kiro CLI の選択で最優先（公式 `installation/` ページ25行） |
| `KIROCREW_INSTALL_KAS` | `0` でインストーラ（`cli.sh`・`install.sh`）が KAS エンジンの取得を省く。`--no-kas` と同じ。v0.11.1〜（`install.md` 163行、`fe6f5be`。CHANGELOG には `--no-kas` だけが書かれていて、この変数の記載はありません）（[03_deployment/01_installation.md](../03_deployment/01_installation.md)参照） |
| `KIROCREW_INSTALL_PLAIN` | `1` でインストーラの進捗表示（curlの進捗バーとライブ行）を止める。パイプやログへの出力はこの状態（`install.md` 247行） |
| `KIROCREW_DISABLE_GPU` | `1` で、GPU が使えない、またはレンダリングが失敗するホストの Windows デスクトップアプリの GPU を無効にする。恒久化は `setx KIROCREW_DISABLE_GPU 1`（`windows-install.md`） |
| `KIROCREW_WORKSPACE` | ワークスペースのルートを変更する（`modules/cli.md` の環境変数表） |
| `KIROCREW_RESTART_READY_TIMEOUT` | `kirocrew restart` の readiness 期限（既定60秒。15〜180秒に丸められる）（`modules/cli.md` 1606-1626行） |
| `TELEGRAM_API_BASE_URL` | `api.telegram.org` が遮断されている環境で Bot API をリバースプロキシ経由にする。`~/.kiro/crew/.env` に `https://tg-proxy.example.com/bot{token}/{method}` の形式で設定し、Gateway を再起動する。必要なプレースホルダが無い値、または非ループバックの `http` は無視される（ログに `Ignoring TELEGRAM_API_BASE_URL`）（公式 `interfaces/telegram/` ページ。Telegram 利用時） |

## 未確認事項

- `orchestrator.stage_timeout_seconds` の既定値と、現在も有効かどうか（根拠の `autopilot.md` が v0.9.0 で削除。v0.11.1 の `docs/system-specs/`・`docs/architecture/`・`docs/guides/`・`CHANGELOG.md`・公式 `docs_md/` のいずれにも出現しない。**継続**。上記の表の注記参照）
- `tunnel.enabled` の既定値（v0.11.1 の `config.md`・`security.md` 702行・`cli.md` 335行にも既定値の記載なし。**継続**）
- `agent.subagent_max_turns` に明示保存された `100` が、旧既定値の名残か意図した上限かの判別（`config.md` 716行（`fe6f5be`）の台帳は、明示保存の100を supported な cost/turn 上限として保持する。本サイトは表の既定値を `1000` とし、`kirocrew config defaults` による確認を案内する。**継続**）
- `agent.sandbox_allow_unsandboxed_exec` の既定値の表記（リポジトリはWindowsで未宣言＝許可、公式 `configuration/` ページは `false`。**継続**。裁定しない）
- `skills.max_triggered` の既定 `0` が v0.7.0 の変更か（CHANGELOG v0.7.0 は変更として記述、v0.6.0 と v0.11.1 の `config.md` 3105行も `0`。**継続**）
- `decisions.history_budget_chars` の実効既定（公式 `configuration/` ページ136行は `0`、`config.md` 722行の台帳は『0 -> 2000, #12928』で `0` を consented ceiling を下回る supported な設定とする。`decisions.md` は「consented ceiling が 0 のあいだは履歴を送らない」と記述。**継続**。裁定しない）
- `session.watchdog_rss_max_mb` を `1536` から `0` に戻した理由、`agent.yolo` を dataclass から除いた理由（いずれも仕様書に事実はあるが、CHANGELOG/Release 本文に説明がない。`config.md` 720・3018行。`agent.yolo` は v0.11.1 の dataclass にもない。**継続**）
- `agent.acp_backend` の「Preview機能（Developer Mode 前提）」が v0.11.1 でも正しいか（v0.9.0 までの記述で、本ページでは再確認していない。[15_agent-backends.md](../01_features/15_agent-backends.md) の領域）
- Settings の「Turn Time Limit」（CHANGELOG.md v0.10.0節 286-289行）がどの設定キーか（既存の `agent.chat_turn_timeout_secs` との対応は一次情報に明記がない）
- 新規キーのうち、`agent.kas_bundle_url`・`dashboard.github_hosts`・`dashboard.bitbucket_server_hosts` の既定値（今回読んだ範囲に記載が見つからない）、`stt.submit_on_release` と CHANGELOG の「意図的に停止した dictation の送信」が同じ設定か

> 以前ここに記載していた次の項目は、v0.11.1 の再検証で**解消**として外しました。
> - **`dashboard.dynamic_dashboard_cards` と画面のスイッチの対応関係**: Settings → Developer の専用カードの「Automatic cards for all sessions」が、このキーを書き換えるスイッチです（`learn-cron-dashboard.md` 3078-3082行、`artifacts.md` 152-154行、CHANGELOG.md v0.10.0節 249-252行。v0.10.0 で変わった項目）。
> - **`slack.trusted_bot_ids` の既定値**: 空のリスト（すべての bot メッセージを破棄）。`slack-gateway.md` 1786行（`fe6f5be`）。**v0.9.0 の `slack-gateway.md` 1585行にも同じ記述があり、本サイトの見落としでした**。
> - **`contributes.sessionControls` の仕様の確定状況**: 公式 `apps/manifest/` ページ（`docs_md/apps__manifest.md` 249-267行。Page updated 2026-09-25）に仕様の記載があります。**公式ページは v0.9.0 の時点で既に同じ内容で、本サイトの見落としでした**。`docs/system-specs/` には引き続き記載がありません。
>
> v0.9.0 の再検証で解消済みとして外した項目（`agent.max_subagents`／`agent.subagent_auto_max` の真の既定値、`spawn_min_memory_gb` の既定値、`agent.sandbox` が受け取る値、`session.pool_size`、`dashboard.terminal.completion.enabled`）は、v0.11.1 でも解消のままです（`session.pool_size` は v0.6.0 で解消。両出典が `0`）。

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
- ディレクトリ構造: [03_directory-layout.md](03_directory-layout.md)
- 上限値: [05_limits.md](05_limits.md)

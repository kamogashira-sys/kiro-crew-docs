# MCP統合

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/capabilities/mcp-tools/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [MCP-firstの設計原則](#mcp-firstの設計原則)
- [管理対象のMCPサーバ](#管理対象のmcpサーバ)
- [設定ファイルの分離](#設定ファイルの分離)
- [マージの優先順位](#マージの優先順位)
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## MCP-firstの設計原則

**設計上の不変条件**: Kiro Crew はプロバイダのグローバル設定に書き込みません。`~/.kiro/settings/mcp.json` はユーザー所有で、Kiro Crew はこれを読むだけで決して変更しません。Kiro Crew 自身の追加は、完全に所有する per-agent ファイル `~/.kiro/agents/kirocrew.json` に入ります。これにより、Kiro Crew に紐づくツールがKiro Crew外の対話的なkiro-cliやKiro IDEセッションに漏れ出すことを防いでいます。

LLMが使う新機能は、Skillsのラッパーではなく**MCP Toolとして提供する**のが原則です（[07_agents-skills-steering.md](07_agents-skills-steering.md)参照）。「LLMツールの仕組み」としてMCPツールが**LLM向けの操作すべてに優先**されます。

## 管理対象のMCPサーバ

Gatewayが所有する管理対象サーバです（`agent._MANAGED_MCP_SERVERS`）。v0.7.2 タグの `architecture/mcp.md` のサーバ一覧（inventory）表は、次の**7サーバ**を「registered by `agent._MANAGED_MCP_SERVERS`」として挙げています。

| サーバ | 役割 |
|-------|------|
| `kirocrew-core` | `spawn_run`（サブエージェント起動）・`learn_add`（レッスン追加）・`task_run`（タスク実行）等 |
| `kirocrew-cron` | cronスケジューリング関連ツール |
| `kirocrew-computer` | Computer Use（デスクトップGUI自動化）のシム |
| `kirocrew-dashboard` | チャットフォルダ（`chat_folder_*`）・ボードタグ（`chat_tag_*`）・他セッションの操作（`session_*`） |
| `kirocrew-work` | conductor と worker の作業台帳（`work_brief`・`work_report`・`work_ledger_read`・`work_ledger_record`） |
| `kirocrew-crew-log` | セッションの Crew log の読み取り専用（`crew_log_*`） |
| `kirocrew-panel` | `panel_publish`・`panel_templates`（inventory 表はツール名のみを記載） |

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **3サーバとする記述**: 同じ `architecture/mcp.md` の「Managed servers」節（145-146行）は「`agent._MANAGED_MCP_SERVERS` holds the **three** servers the gateway owns end to end: `kirocrew-cron`, `kirocrew-core`, `kirocrew-computer`」と記述しています
> - **7サーバとする記述**: 同ファイルの「Server and tool inventory」表（1175-1186行）は上表の7サーバを「registered by `agent._MANAGED_MCP_SERVERS`」と記載しています。`modules/mcp-shareability.md`（46行）も「All seven managed servers」と記述しています
> - **関連する記述**: 同ファイル1411-1413行は、意図して付与する能力は `kirocrew-dashboard` と同じ形（`_MANAGED_MCP_SERVERS` で `opt_in` と印を付けた割り当て可能なセット。既定のエージェントには追加されない）にすると記述し、1908-1909行は `kirocrew-dashboard`・`kirocrew-work`・`kirocrew-crew-log`・`kirocrew-panel` を「the opt-in Crew servers」と呼んでいます
>
> v0.6.0 タグ（`8575209`）の inventory 表は、`kirocrew-dashboard`（当時は `chat_folder_*` の4ツールのみ）を加えた4サーバでした。
>
> **出典**（管理対象サーバ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
> **出典**（7サーバの記述）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/mcp-shareability.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
> **出典**（`kirocrew-work` の conductor/worker の分担）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/reference/ledger-conductor-sequence.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2。7行）

`kirocrew-crew-log` が読む Crew log は、Gateway を `KIROCREW_CREW_LOG` を有効にして動かしたときに記録されます（CHANGELOG.md v0.7.0節 316-318行）。`KIROCREW_CREW_LOG` は**既定オフ**で、`modules/crew-log-core.md`（145行）はその形式を **PRE-RELEASE**（変更される可能性あり）と明記しています。ツールの一覧は [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md) を参照してください。

`architecture/mcp.md` の「Managed servers」節（145-150行）は、`kirocrew-cron`・`kirocrew-core`・`kirocrew-computer` の各サーバが再構築のたびに `_refresh_dynamic_fields()` によって `command`/`args` を書き換えられると記述しています。**ブラウザ自動化はここに含まれません**（`browser.md` が「MCPサーバではなくシェル機能」と明記。詳細は [13_computer-and-browser.md](13_computer-and-browser.md)）。

## 設定ファイルの分離

| ファイル | 所有者 | 用途 | 読み込み元 |
|---------|-------|------|-----------|
| `~/.kiro/agents/kirocrew.json` | Kiro Crew Gateway（`agent.rebuild_agent_config`） | レンダリングされたKiroエージェント（モデル＋ツール＋マージ済み`mcpServers`） | kiro-cli（`kirocrew`エージェントとして起動時） |
| `~/.kiro/settings/mcp.json` | ユーザー | KiroのグローバルMCPサーバ | 全エージェントのkiro-cli。レンダリング時にKiro Crewのエージェントファイルにマージ |
| `~/.kiro/crew/mcp.json` | ユーザー（ダッシュボードのMCPパネル経由） | Kiro Crew固有の追加・サーバ単位のツール無効化 | Kiro Crew Gatewayのみ |

`rebuild_agent_config()` は**厳密に1つのファイル** `~/.kiro/agents/kirocrew.json` のみを書きます。他のプロバイダ向けにレンダリングされたエージェントファイルは存在しません（Kiro CrewはKiroACP専用のため）。

## マージの優先順位

Gatewayが `~/.kiro/agents/kirocrew.json` を組み立てる際のマージ順序です。

1. 管理対象サーバ（`kirocrew-core`等）は `_refresh_dynamic_fields()` が `command`/`args` を設定し、常に古いグローバルエントリで上書きされないようにする
2. `~/.kiro/settings/mcp.json`（Kiroグローバル）を `setdefault` でマージ
3. seam経由のプロバイダグローバルを `setdefault` でマージ（このビルドでは空）
4. `~/.kiro/crew/mcp.json` を既存エントリへの `update()` でマージ（Kiro Crewの `command`/`args`/`env` が勝ち、ユーザー設定の `autoApprove` 等は保持される）

Kiroグローバルはseam経由のプロバイダグローバルより優先されます（Kiro CrewがKiro CLI専用のため）。

`includeMcpJson: false` が既定です。Gatewayが既にKiroグローバルをエージェントファイルにマージしているため、`true` にするとkiro-cliがセッション開始時にグローバルを二重にマージし、重複エントリや古いパスによる新しいパスの上書きが発生します。

## v0.7.0での変更

| 変更 | 内容 | 出典 |
|------|------|:---:|
| **管理対象サーバの一覧が増えた** | v0.6.0 タグの inventory 表（4サーバ）に対し、v0.7.0 タグ以降の表は `kirocrew-work`・`kirocrew-crew-log`・`kirocrew-panel` を加えた7サーバになりました。`kirocrew-dashboard` のツールにも `chat_folder_file_self`・`chat_tag_*`・`session_*` が並びます（`session_*` は v0.6.0 タグの `modules/session-control.md` にも `kirocrew-dashboard` のツールとして記載あり）。3サーバとする記述との食い違いは「[管理対象のMCPサーバ](#管理対象のmcpサーバ)」を参照 | mcp.md 1175-1186行 |
| **読み取り専用の `kirocrew-crew-log`** | セッションごとの追記専用ログ（Crew log）を、エージェントが検証用に読める読み取り専用MCPサーバです。Crew log は `KIROCREW_CREW_LOG` を有効にしたときに記録されます（**既定オフ**） | CHANGELOG 314-318行 |
| **エージェントがボードタグ間でセッションを移せる** | `chat_tag` ツールで、タグマネージャで設定した権限の範囲内でセッションをボードタグ間で移動できます | CHANGELOG 410-414行 |
| **MCPサーバの埋め込みUIがダッシュボードのテーマを継承** | 色・フォントファミリー・角丸・影を継承し、テーマ変更時にも再継承します。対象は **Developer Mode を有効にし**、Developer → MCP Management で Gateway スタブ経由にルーティングしたサーバです | CHANGELOG 232-235行 |

`kirocrew-work`・`kirocrew-panel` の追加は v0.7.0 タグ以降の仕様書（`architecture/mcp.md` の inventory 表）で確認したもので、CHANGELOG はこの2サーバを説明していません。

出典: CHANGELOG.md v0.7.0節 232-235・314-318・410-414行（`c67c506`）。

**出典**（サーバ一覧）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## v0.3.0での変更

| 変更 | 内容 | CHANGELOG行 |
|------|------|:---:|
| **プロセス共有の可否をプローブする** | Kiro Crewが「どのMCPサーバがプロセスを安全に共有できるか」を**プローブして判定**するようになりました。**サーバ単位の選択が、従来のグローバルスイッチとその推測（guesswork）を置き換えます** | 166行 |
| **per-agent tool sets** | サーバを特定のエージェントに割り当てられるようになり、グローバル設定を編集せずに各エージェントが自分用のツール群を持てます。エージェントピッカーは、アクティブなセッションで見つかったプロジェクトローカルのエージェントも提示します | 169行 |
| **ツールの遅延提示の調整** | Tool Searchが「必要になるまでツールを隠す」度合いを設定できるようになりました（コンテキストと即応性のトレードオフ） | 172行 |
| **認証付きカスタムサーバ** | リモートMCPサーバを追加する際に**リクエストヘッダを指定**できるようになり、ファイルを手編集する必要がなくなりました | 174行 |

出典: CHANGELOG.md v0.3.0節（`21584ea`）。

## 未確認事項

- 管理対象サーバの数（`architecture/mcp.md` 内で「three」と7行の inventory 表が食い違う。本サイトは裁定せず両方を記載。「[管理対象のMCPサーバ](#管理対象のmcpサーバ)」参照）
- 上記以外の本ページの記述は `docs/architecture/mcp.md` で確認済み

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/capabilities/mcp-tools/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
- Computer Use・ブラウザ: [13_computer-and-browser.md](13_computer-and-browser.md)
- MCPツール一覧: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)

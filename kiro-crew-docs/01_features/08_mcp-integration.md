# MCP統合

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/capabilities/mcp-tools/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [MCP-firstの設計原則](#mcp-firstの設計原則)
- [管理対象のMCPサーバ](#管理対象のmcpサーバ)
- [設定ファイルの分離](#設定ファイルの分離)
- [マージの優先順位](#マージの優先順位)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## MCP-firstの設計原則

**設計上の不変条件**: Kiro Crew はプロバイダのグローバル設定に書き込みません。`~/.kiro/settings/mcp.json` はユーザー所有で、Kiro Crew はこれを読むだけで決して変更しません。Kiro Crew 自身の追加は、完全に所有する per-agent ファイル `~/.kiro/agents/kirocrew.json` に入ります。これにより、Kiro Crew に紐づくツールがKiro Crew外の対話的なkiro-cliやKiro IDEセッションに漏れ出すことを防いでいます。

LLMが使う新機能は、Skillsのラッパーではなく**MCP Toolとして提供する**のが原則です（[07_agents-skills-steering.md](07_agents-skills-steering.md)参照）。「LLMツールの仕組み」としてMCPツールが**LLM向けの操作すべてに優先**されます。

## 管理対象のMCPサーバ

Gatewayが所有する管理対象サーバです（`agent._MANAGED_MCP_SERVERS`）。v0.9.0 の `architecture/mcp.md` は、次の**8サーバ**を保持すると記述しています（144-148行。常時有効 2・条件付き（gated）1・オプトイン 5）。

| サーバ | 区分 | 役割 |
|-------|------|------|
| `kirocrew-core` | 常時有効 | `spawn_run`（サブエージェント起動）・`learn_add`（レッスン追加）・`task_run`（タスク実行）等。ブラウザの `browser` ツールもここにあります（下記） |
| `kirocrew-cron` | 常時有効 | cronスケジューリング関連ツール（9ツール） |
| `kirocrew-computer` | 条件付き（gated） | Computer Use（デスクトップGUI自動化）のシム |
| `kirocrew-dashboard` | オプトイン | チャットフォルダ（`chat_folder_*`）・ボードタグ（`chat_tag_*`）・他セッションの操作（`session_*`） |
| `kirocrew-work` | オプトイン | conductor と worker の作業台帳（`work_brief`・`work_report`・`work_ledger_read`・`work_ledger_record`・`work_ledger_rebuild`） |
| `kirocrew-crew-log` | オプトイン | セッションの Crew log の読み取り専用（`crew_log_*`） |
| `kirocrew-debug` | オプトイン | 動作中の Gateway に関する読み取り専用の 5 ツール（`debug_*`）。下記「[`kirocrew-debug`](#kirocrew-debug)」 |
| `kirocrew-panel` | オプトイン | `panel_publish`・`panel_templates`。特定の crew member の DM セッション用 |

オプトインのサーバは、既定のエージェントには追加されません。エージェントの設定が `mcpServers` のエントリと `tools` の `@<server>` 参照を持つときだけ読み込まれます（`mcp.md` 1832-1837行・1844-1850行）。`kirocrew-panel` はセッション単位の `mcpServers` エントリとして付与され、Capabilities エディタや spec からは付与できません。運用者側の上限は `agent.crew_panel` です（同 1548-1556行）。

> **解消済みの食い違い**: v0.7.2 タグの `architecture/mcp.md` は、同じファイル内で「Managed servers」節が**3サーバ**、「Server and tool inventory」表が**7サーバ**を挙げ、`modules/mcp-shareability.md` は「All seven managed servers」と記述していました。本サイトは当時、両方を併記していました。**v0.9.0 の `architecture/mcp.md` は 8 サーバで一致し**（144-148行・1532-1546行の表・2352-2354行）、`modules/mcp-shareability.md` も「All eight managed servers」と全 8 サーバを列挙しています（44行）。新規は `kirocrew-debug` です。

**出典**（管理対象サーバ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（8サーバの記述）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/mcp-shareability.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（`kirocrew-work` の conductor/worker の分担）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/reference/ledger-conductor-sequence.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。7行）

公式 `capabilities/mcp-tools`（Page updated 2026-08-31）は、管理対象サーバのうち常時有効の 2 つ（`kirocrew-core`・`kirocrew-cron`）だけを記述しています。両者は「常時有効」の 2 つで一致し、公式は条件付き・オプトインのサーバに触れていません。

### Crew log

`kirocrew-crew-log` が読む Crew log（セッションごとの追記専用ログ）は、**v0.8.0 以降、設定なしで記録されます（既定オン）**。Gateway を起動する前に `KIROCREW_CREW_LOG=0` を設定すると無効になります。`0`・`false`・`no`・`off` が無効で、認識できない値も無効として扱われ、その旨が 1 回ログに記録されます（`modules/crew-log-core.md` 160-165行・`modules/crew-log-emitter.md` 32-35行・CHANGELOG.md v0.8.0節 330-336行。公式 `configuration/`・`chat/sessions/` も同じ）。会話を削除またはゴミ箱へ移すと、その会話の Crew log も一緒に削除されます（CHANGELOG.md v0.8.0節 333-334行）。

v0.7.0〜v0.7.2 では既定オフで、`crew-log-core.md`（v0.7.2 の 145行）は形式を **PRE-RELEASE**（変更される可能性あり）と明記していました。v0.9.0 の同ファイルに PRE-RELEASE の注記はなく、追加フィールドは加算的で、既存型の形を変える変更には移行を付ける、という互換規則を記述しています。

ツールの一覧は [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md) を参照してください。

### ブラウザ

ブラウザ操作は、専用の MCP サーバではなく、`kirocrew-core` の**単一のツール `browser`** としても使えます。デスクトップアプリで Browser パネルがセッションに接続されている間、`op`（`navigate`・`snapshot`・`click`・`type`・`press_key`・`hover`・`select_option`・`screenshot`・`wait_for`・`back`・`console`）を 1 回ずつ送ります。パネルが無い場合と、`dashboard.use_builtin_browser`（既定 `true`）をオフにした場合は、ツールが `playwright-cli`（シェル）への切り替えを案内します。`navigate` が自動で扱うのは公開 HTTP(S) だけで、localhost・プライベート・リンクローカルなどは承認が必要な CLI 経路に回ります（`modules/browser.md` 3-14行・96-98行・115-123行、`mcp.md` 1803-1809行。公式 `features/browser`（Page updated 2026-09-25）も「The native Browser tool in the packaged desktop app」と記述）。

v0.7.2 以前の `browser.md` は「ブラウザは MCP サーバではなくシェル機能」と記述しており、本サイトも以前そのように記載していました（v0.8.0 タグの `browser.md` は既に単一の MCP ツールと記述）。詳細は [13_computer-and-browser.md](13_computer-and-browser.md) を参照してください。

**出典**（Crew log）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/crew-log-core.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（ブラウザ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://kiro.dev/docs/crew/features/browser/>（Page updated 2026-09-25）

`architecture/mcp.md` の「Managed servers」節（144-165行）は、管理対象サーバの各エントリが再構築のたびに `_refresh_dynamic_fields()` によって `command`/`args` を書き換えられると記述しています。

## 設定ファイルの分離

| ファイル | 所有者 | 用途 | 読み込み元 |
|---------|-------|------|-----------|
| `~/.kiro/agents/kirocrew.json` | Kiro Crew Gateway（`agent.rebuild_agent_config`） | レンダリングされたKiroエージェント（モデル＋ツール＋マージ済み`mcpServers`） | kiro-cli（`kirocrew`エージェントとして起動時） |
| `~/.kiro/settings/mcp.json` | ユーザー | KiroのグローバルMCPサーバ | 全エージェントのkiro-cli。レンダリング時にKiro Crewのエージェントファイルにマージ |
| `~/.kiro/crew/mcp.json` | ユーザー（ダッシュボードのMCPパネル経由） | Kiro Crew固有の追加・サーバ単位のツール無効化 | Kiro Crew Gatewayのみ |

`rebuild_agent_config()` は**厳密に1つのファイル** `~/.kiro/agents/kirocrew.json` のみを書きます。第2のエージェントファイルはありません。provider は ACP のみで、kiro-cli 以外の ACP ハーネスは別のエージェントファイルではなく、投影された設定を受け取ります（`mcp.md` 34-39行。v0.7.2 の同ファイルは「no agent-file renderer for any other provider: Kiro Crew is KiroACP-only」と記述）。

## マージの優先順位

`rebuild_agent_config()` が `~/.kiro/agents/kirocrew.json` を組み立てるときの順序です（`mcp.md` 63-106行）。`clean=False` のとき、既存の `kirocrew.json` がマージの**ベース**になり、ユーザーが調整したサーバ（`autoApprove` の編集・手編集・`kiro-cli mcp add --agent kirocrew` で追加したサーバ）が残ります。そのベースに次を順に適用します。

1. **App 由来のサーバ**（`{app}:{server}` のキー）を**代入**します（`setdefault` ではありません）。マニフェストが正であり、再構築のたびに導出し直すため、前回の再構築のエントリを残すと、今回取り除いた `autoApprove` の付与が残ってしまうからです
2. `~/.kiro/settings/mcp.json`（Kiroグローバル）: 無い名前は追加します。**前回の再構築が残した名前**は reconcile され、ソースが持つ `timeout`・`disabled` が上書きされ、ソースが取り除いたキーは削除されます。`autoApprove` を含む他のキーはユーザーのものとして残ります
3. seam経由のプロバイダグローバル（このビルドでは空）。手順 1・2 が既に確保した名前には触れません
4. `~/.kiro/crew/mcp.json` を既存エントリへの `update()` でマージします（Kiro Crewの `command`/`args`/`env` が勝ち、ユーザー設定の `autoApprove` 等は保持されます）

管理対象サーバは各マージループの対象外です。`command`/`args` は `_refresh_dynamic_fields()` が設定し、古いグローバルエントリで上書きされないようにします。Kiroグローバルはseam経由のプロバイダグローバルより優先されます（Kiro CrewがKiro CLI専用のため）。

> **以前の記述の訂正**: 本ページは以前、手順 2・3 を `setdefault` でマージすると記載していました。これは v0.3.0（`21584ea`）・v0.4.1・v0.6.0 の各タグの `architecture/mcp.md` の記述に基づくものです。**v0.7.0 タグ以降の同ファイルは上記の記述**（App 由来サーバの代入、reconcile）に変わっています。変更の理由は CHANGELOG に説明がありません。

コマンドが解決できないときは、同じサーバを他のソースから優先順に再試行します（kirocrew → kiro-global → provider-global）。別のソースへ切り替えた場合は、そのソースの `command`・`args`・`env` を**ひとまとまり**で採用します（`mcp.md` 97-106行）。

### `includeMcpJson` は固定

Kiro Crew は、自身が管理する全エージェント（主エージェントと App エージェント）で `includeMcpJson` を `false` に**固定**します（`mcp.md` 122-140行）。Gatewayが既にKiroグローバルをエージェントファイルにマージしているため、`true` にするとkiro-cliがセッション開始時にグローバルを二重にマージし、重複エントリや古いパスによる新しいパスの上書きが発生します。Kiro Crew の管理外の kiro-cli エージェントは、kiro-cli 自身の既定のままです。v0.7.2 以前の本ページは「`includeMcpJson: false` が既定」と記載していました。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.9.0での変更

| 変更 | 内容 | 出典 |
|------|------|:---:|
| **画面名の変更: Agent Capabilities → Customize** | CHANGELOG は「Agent Capabilities is now Customize」と記載しています。公式 `capabilities/mcp-tools`（Page updated 2026-08-31）は導線を「Agent Capabilities → Integrations (MCP)」と記述しており、公式ページの記述はこの改称を反映していません。`mcp.md`（641行）は「The Connections page's MCP panel」と記述します。呼び名が出典ごとに異なるため、本サイトは裁定せず、両方を示します | CHANGELOG 150-153行 |

出典: CHANGELOG.md v0.9.0節 150-153行（`99e6253`）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** MCP の画面の導線について、公式 `capabilities/mcp-tools`（Page updated 2026-08-31）は「Open Agent Capabilities → Integrations (MCP)」と記述します。CHANGELOG v0.9.0節 150行は「Agent Capabilities is now Customize」と記載し、`architecture/mcp.md` 641行は「The Connections page's MCP panel」と記述します。「常時有効」の 2 つのサーバ（`kirocrew-core`・`kirocrew-cron`）の記述は公式とリポジトリで一致しています。

**出典**（導線）: <https://kiro.dev/docs/crew/capabilities/mcp-tools/>（Page updated 2026-08-31）

## v0.8.0での変更

以下のうち、CHANGELOG に記載のある項目は出典の行を示します。それ以外は v0.9.0 タグの仕様書で確認したもので、**CHANGELOG/Release 本文は説明していません**（v0.8.0 タグの仕様書にも同じ記述があるものは、その旨を示します）。

### 自動承認（`autoApprove`）の扱い: `mcp.honour_auto_approve`

- **既定オン**: `mcp.json` やエージェントファイルに自分で書いた `autoApprove` のリストは保持されます。保持されたツールは kiro-cli がローカルで承認するため、Kiro Crew は許可リクエストを受け取らず、**Kiro Crew 自身のツールゲートも実行されません**（`mcp.md` 150-181行）
- **`false` にすると**、どのサーバの spec も宣言していない verb をすべて落とし、そのツールを承認カードを通る状態に戻します。管理対象サーバや edition の spec が宣言した verb は、どちらの設定でも影響を受けません。**ガバナンスの上限（ceiling）は設定にかかわらずキーを取り除きます**
- **App の `<app>:<server>` エントリのリストは、どちらの設定でも保持されません**（マニフェストが付与するもので、オーナーが選んだものではないため）
- 保持した場合は SEL に `mcp_auto_approve_honoured`、取り上げた場合は `mcp_auto_approve_withheld` が記録されます（`mcp.md` 332-349行）
- 変更には再起動が必要なキーです（`config.md` 2547行）
- CHANGELOG は「auto-approve list you wrote yourself in `mcp.json` or an agent file is now kept」と記載しています。v0.7.2 の仕様書は、ガバナンス上限に基づく取り上げ（`mcp_auto_approve_withheld`）を記述し、オーナーが書いた verb の扱いは明記していませんでした

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** `mcp.honour_auto_approve` の値が不正（真偽値でない）なときの扱い: `mcp.md` 343行は「only a real `false` there drops every verb」と記述し、`config.md` 1540行は「honour only a real `true`」と記述します。さらに `config.md` 1550行は、型の違う値は検証で取り除かれ、`load()` を通ると field default を読むと記述します。不正な値のとき保持されるかどうかは、仕様書から確認できません。

出典: CHANGELOG.md v0.8.0節 616-621行（`99e6253`）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### `kirocrew-debug`

動作中の Gateway について 5 つの問い（どのコードが動いているか、なぜ拒否されたか、インタプリタは競合しているか、ホストで何が動いているか、過ぎた時点に何が起きたか）に答える**読み取り専用**のツール群です。

| 問い | ツール |
|------|-------|
| どのコードが動いているか | `debug_gateway` |
| なぜ拒否されたか | `debug_refusals` |
| インタプリタは競合しているか、何が原因か | `debug_threads` |
| ホストで何が動いているか、何がリークしたか | `debug_processes` |
| 過ぎた時点に何が起きたか | `debug_snapshots` |

- **オプトイン**です。エージェントの `mcpServers` にエントリを追加し、`tools` に `@kirocrew-debug` を加えて付与します。コアに置くと全セッションのコンテキストを消費するため、既定のエージェントには追加されません
- ツールは 5 つに固定されています（`test/test_mcp_debug.py` が名前を固定しており、書き込みツールは追加できません）
- `debug_processes` の資源の詳細（rss・スレッド状態・fd・cwd など）は Linux のみで、macOS では pid と ppid だけです

CHANGELOG v0.8.0・v0.9.0 に `kirocrew-debug` の記述はなく、公式 `capabilities/mcp-tools` にも記載はありません。リポジトリの `docs/reference/debug/README.md`（3-30行）の説明に基づきます。v0.8.0 タグの仕様書にも同じサーバの記述があります。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/reference/debug/README.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### Tool Search と Kiro Crew 自身のサーバ（kiro-cli 2.27.0 以上）

- **Tool Search**: `agent.tool_search` は既定オンです。MCP の spec が `agent.tool_search_min_pct` または `agent.tool_search_min_tokens` の閾値を超えると、kiro は遅延提示します
- **Kiro Crew 自身のサーバ**も、起動するのが Kiro Crew が固定した kiro-cli（またはその `kiro-cli-chat`）で、かつ**バージョンが 2.27.0 以上**のときは、他のサーバと同様に必要になるまで読み込まれません。それ以外の実行ファイル（pod のバンドル、`PATH` 上の `kiro-cli`）・2.27.0 未満・バージョン不明の場合は、thinking-signature の「tools list differs」拒否を避けるため、サーバの spec を常駐させます
- 環境変数 `ASBX_KIRO_MANDATORY_MCPS`（Gateway の環境。サーバ名のカンマ区切り）が設定されていれば、それが常に優先されます（空文字も有効）
- CHANGELOG は「With kiro-cli 2.27 or later those tools load on demand under Tool Search」と記載し、デスクトップアプリは kiro-cli 2.27.1 を同梱するとしています
- v0.7.2 までの仕様書は「Crew's own servers are exempt from Tool Search deferral」（Kiro Crew 自身のサーバは遅延の対象外）と記述していました

公式 `capabilities/mcp-tools` の「Tune how aggressively Tool Search defers tools」の記述とは整合しています。

出典: CHANGELOG.md v0.8.0節 666-669行（`99e6253`）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。1811-1830行）

### 共有 MCP バックエンドの Stub レビュー（Developer Mode）

- **Developer Mode をオンにしたとき**、Developer → MCP Management でサーバの Stub スイッチをオンにすると、共有バックエンド 1 つが起動するコマンドと環境の内容を確認する画面が開き、**承認するまで何も変わりません**。承認後にコマンドが変わったサーバは「needs approval」と表示され、新しい内容を承認するまで各セッション内でそのまま動き続けます（CHANGELOG.md v0.8.0節 389-394行）
- 仕様書: 承認は `~/.kiro/crew/mcp-launch-approvals/approvals.json`（コマンドと実効環境ハッシュの対）に保存されます。承認が無い stub は、セッションごとのサンドボックス内の起動にとどまります。承認なしの `stub: true` は 409（`expected_launch_required`・`launch_display_incomplete`・`launch_changed_since_display`）で拒否され、一括の `stub: true` は 400（`batch_stub_requires_individual`）です（`mcp.md` 758-838行）
- stub の名簿（`mcp_gateway.stub_servers`）は**既定で空**で、サーバ単位のオプトインです。`mcp_gateway.stub_overrides` が MCP Management の書き込み先です。`mcp_gateway.enabled` はバックエンドの共有を決め、stub の有無とは別です（`design-notes/mcp-stub-decoupling.md` 1-40行）
- MCP Apps の描画は、stub 経由の stdio サーバが前提です（`mcp-apps.md` 3-5行）。`mcp_gateway.apps_enabled` は UI から外れ書き込まれませんが、保存済みの `false` はオプトアウトとして有効で、環境変数 `KIROCREW_MCP_APPS` も kill switch です（明示的なオフが優先）。MCP App からチャットへのメッセージ送信は [10_apps.md](10_apps.md#mcp-app-がチャットへ送るメッセージ) を参照してください

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** MCP Apps の有効化の条件について、`docs/feature-map/README.md` 81行は「gateway-stubbed servers only, behind `mcp_gateway.apps_enabled`」と記述します。`design-notes/mcp-stub-decoupling.md` 29-33行と `mcp.md` 850-855行は、`apps_enabled` は UI から外れ書き込まれず、Capability は stub の有無に従うと記述します。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### サーバのプローブと隔離

- **リモート（HTTP）プローブ**は `MCP_CLIENT_PROTOCOL_VERSION`（`2025-06-18`）を提示し、`-32602` で拒否され `data.supported` に古い版があれば 1 回だけその中の最新版で再試行します。stdio プローブは `2024-11-05` を提示します（`mcp.md` 381-392行）
- **ミュートされたサーバ**（`~/.kiro/crew/mcp.json` のエントリで `disabled` が存在し、真偽値の `false` 以外）はプローブで起動されず、`status: "disabled"` で返ります（同 388-390行）
- **プローブ失敗の隔離**: 連続して失敗したサーバは `agent.mcp_quarantine_after_failures` の閾値で `probeFailing` になり、以後のプローブ対象から外れます。チャットのセッションは引き続きそのサーバを使えます。回復は操作（`POST /api/mcp/quarantine/clear`、またはダッシュボードの Reset count）か、閾値を上げる／`0` にする（隔離と表示の両方を無効）ことです。タイマーによる自動再試行はありません（`mcp-probe-quarantine.md` 1-30行）。閾値の既定値は仕様書で確認できません（「three transient failures」という例示のみ）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/mcp-probe-quarantine.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### ツールポリシーを読めない場合

Kiro Crew 自身の MCP サーバの `tools/call` は、運用者の除外設定（ツールポリシー）を読めないとき、呼び出しを**拒否**します（fail closed）。理由は `policy_unreadable`・`identity_unattested`・`identity_unattestable`・`resolution_failed` の 4 つです。拒否は最大 60 秒の否定キャッシュの窓で限定されます。v0.7.2 の仕様書は `resolution_failed` を許可（監査のみ）と記述していました（`mcp.md` 1372-1470行）。`tools/list` は、ポリシーが解決できなくても絞り込みません。

CHANGELOG は関連する修正として、更新で以前のインストールが取り除かれた後・アプリ内再起動の後・共有 MCP バックエンドがセッション単位の実行に戻ったときも、Kiro Crew 自身のツールが使えるままになった（以前は Gateway を再起動するまですべての呼び出しが未証明として拒否された）と記載しています（CHANGELOG.md v0.8.0節 663-668行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### `mcp.extra_path_dirs`（macOS）

MCP サーバのランチャーが見つからないときに使う、絶対パスのリストの設定です。MCP の解決と MCP gateway daemon の `PATH` を拡張し、GUI アプリ全体の `PATH` は変えません。daemon が起動時に `PATH` を引き継ぐため、設定後は Gateway の再起動が必要です。エージェントのシェルコマンドには影響しないため、それらも見つからないときは launchd 側の修正を使います（`guides/macos-troubleshooting.md` 41-46行）。このキーは v0.7.2 の仕様書にありません。対象 OS は、`macos-troubleshooting.md` の文脈（macOS）以外での効果を仕様書から確認できません。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/macos-troubleshooting.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### その他

- **エージェントがユーザーのセッションに対してできること**: 別セッションが使うモデルの変更（`session_set_model`。待機中のセッションの次のターンから反映され、実行中のターンまたはサブエージェントがある間は止めるまで元のモデルのまま）、ピン留め（`chat_session_pin`）、トランスクリプトのフォーク（`session_fork`）、他セッションの採用／解放（`session_adopt`／`session_release`）。ピン留めとモデルの変更は、テンプレートが `kirocrew-dashboard` のツール群をマウントしたエージェントが必要で、メッセージングチャネルから話しているエージェントには拒否されます。ボードタグの Agent permissions（Human only／Agent: add only／Agent: add and remove）が、エージェントのタグ操作を制限します（CHANGELOG.md v0.8.0節 265-271・310-329行、`session-control.md` 16-37行）。ツールの一覧は [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md) を参照してください
- **Discord・Telegram の DM で conductor を動かせる**: チャネルのセッションは以前、完全に拒否されていました（CHANGELOG.md v0.8.0節 313-314行）
- **conductor が作業台帳を再構築できる**: Crew log の書き込み記録から台帳を再構築できます。CHANGELOG は「A conductor can rebuild its work ledger」と記載しています（CHANGELOG.md v0.8.0節 315-317行）。`kirocrew-work` の `work_ledger_rebuild` が `architecture/mcp.md` の目録（1543行）と `ledger-conductor-sequence.md`（7行）に載るのは v0.9.0 タグからです（v0.8.0 タグの `docs/` には `work_ledger_rebuild` の記述が見つかりません）

## v0.7.0での変更

| 変更 | 内容 | 出典 |
|------|------|:---:|
| **管理対象サーバの一覧が増えた** | v0.6.0 タグの inventory 表（4サーバ）に対し、v0.7.0 タグ以降の表は `kirocrew-work`・`kirocrew-crew-log`・`kirocrew-panel` を加えた7サーバになりました。`kirocrew-dashboard` のツールにも `chat_folder_file_self`・`chat_tag_*`・`session_*` が並びます（`session_*` は v0.6.0 タグの `modules/session-control.md` にも `kirocrew-dashboard` のツールとして記載あり）。v0.7.2 タグでは「Managed servers」節の3サーバとの食い違いがありましたが、v0.9.0 で8サーバ（`kirocrew-debug` を追加）に一致して解消しています（「[管理対象のMCPサーバ](#管理対象のmcpサーバ)」参照） | v0.7.2 の mcp.md 1175-1186行 |
| **読み取り専用の `kirocrew-crew-log`** | セッションごとの追記専用ログ（Crew log）を、エージェントが検証用に読める読み取り専用MCPサーバです。v0.7.0〜v0.7.2 では Crew log は `KIROCREW_CREW_LOG` を有効にしたときに記録されました（**既定オフ**）。**v0.8.0 から既定オン**です（「[Crew log](#crew-log)」参照） | CHANGELOG 314-318行 |
| **エージェントがボードタグ間でセッションを移せる** | `chat_tag` ツールで、タグマネージャで設定した権限の範囲内でセッションをボードタグ間で移動できます | CHANGELOG 410-414行 |
| **MCPサーバの埋め込みUIがダッシュボードのテーマを継承** | 色・フォントファミリー・角丸・影を継承し、テーマ変更時にも再継承します。対象は **Developer Mode を有効にし**、Developer → MCP Management で Gateway スタブ経由にルーティングしたサーバです | CHANGELOG 232-235行 |

`kirocrew-work`・`kirocrew-panel` の追加は v0.7.0 タグ以降の仕様書（`architecture/mcp.md` の inventory 表）で確認したもので、CHANGELOG はこの2サーバを説明していません。

出典: CHANGELOG.md v0.7.0節 232-235・314-318・410-414行（v0.7.2 タグのファイルの行番号、`c67c506`）。

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

- `mcp.honour_auto_approve` の値が不正なときに保持されるかどうか（`mcp.md` 343行と `config.md` 1540・1550行の記述が異なる。「[自動承認の扱い](#自動承認autoapproveの扱い-mcphonour_auto_approve)」参照）
- `agent.mcp_quarantine_after_failures` の既定値（仕様書は「three transient failures」と例示するだけで、既定値を明記する箇所を確認できない）
- `mcp.extra_path_dirs` が macOS 以外で効果を持つかどうか
- v0.7.2 の `mcp.md` の目録にあった `browse_outline`・`browse_search` は、v0.8.0 以降の `mcp.md` と全 docs・CHANGELOG に記述がなく、廃止か改名か、単に列挙から外れたのかを一次情報から確認できない（本ページでは扱わない）
- 管理対象サーバの数の食い違い（v0.7.2 時点）は v0.9.0 で解消済みです（「[管理対象のMCPサーバ](#管理対象のmcpサーバ)」参照）
- 上記以外の本ページの記述は `docs/architecture/mcp.md`（v0.9.0）で確認済みです。v0.7.0・v0.3.0 の表は、CHANGELOG の該当節が v0.7.2 の時点から変わっていないことを確認しています

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/capabilities/mcp-tools/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
- Computer Use・ブラウザ: [13_computer-and-browser.md](13_computer-and-browser.md)
- MCPツール一覧: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)

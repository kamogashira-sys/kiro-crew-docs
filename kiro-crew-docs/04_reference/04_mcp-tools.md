# MCPツール一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

---

## 📑 このページの内容

- [管理対象サーバ](#管理対象サーバ)
- [ツール一覧](#ツール一覧)
- [ブラウザのMCPツール](#ブラウザのmcpツール)
- [v0.11.1でのMCP関連の変更](#v0111でのmcp関連の変更)
- [v0.9.0でのMCP関連の変更](#v090でのmcp関連の変更)
- [v0.8.0でのMCP関連の変更](#v080でのmcp関連の変更)
- [v0.7.0でのMCP関連の変更](#v070でのmcp関連の変更)
- [v0.3.0でのMCP関連の変更](#v030でのmcp関連の変更)
- [未確認事項](#未確認事項)

---

## 管理対象サーバ

| サーバ | 区分 | 主なツール |
|-------|------|-----------|
| `kirocrew-core` | 常時有効 | `spawn_run`（サブエージェント起動）、`learn_add`（レッスン追加）、`task_run`（タスク実行）、`local_knowledge_search`（Knowledge Library検索）、`skill_search`（スキル検索）、`browser`（ブラウザ操作）ほか。一覧は下記 |
| `kirocrew-cron` | 常時有効 | `cron_add`・`cron_list`・`cron_update`・`cron_remove`・`cron_remove_all`・`cron_pause`・`cron_resume`・`cron_trigger`・`cron_secret_request`（9ツール） |
| `kirocrew-guide` | 常時有効 | `guide_list_actions`・`guide_start`・`guide_status`・`guide_cancel`・`list_change_kinds`・`find_setting`・`get_member_capabilities`・`diagnose_settings`・`propose_change`・`get_change_status`・`search_docs`・`find_ui`（12ツール） |
| `kirocrew-mate` | 常時有効 | `update_self`・`set_model`・`set_approval_mode`・`find_capabilities`・`request_capabilities`・`goal_read`・`set_goal`・`set_key_results`・`key_result_progress`・`save_goal_report`・`save_notes`（11ツール。呼び出した Mate 自身にだけ作用） |
| `kirocrew-computer` | 条件付き（gated） | Computer Use（デスクトップGUI自動化）のシム。11ツール |
| `kirocrew-dashboard` | オプトイン | フォルダ・ボードタグ・他セッションの操作。37ツール（下記。v0.9.0 は 31） |
| `kirocrew-work` | オプトイン | `work_brief`・`work_report`・`work_ledger_read`・`work_ledger_record`・`work_ledger_rebuild`（5ツール） |
| `kirocrew-crew-log` | オプトイン | `crew_log_list`・`crew_log_read`・`crew_log_projection`（3ツール） |
| `kirocrew-debug` | オプトイン | `debug_gateway`・`debug_refusals`・`debug_threads`・`debug_processes`・`debug_snapshots`（読み取り専用の5ツール） |
| `kirocrew-panel` | オプトイン | `panel_publish`・`panel_templates`・`dashboard_fields`・`dashboard_types`・`dashboard_write`・`dashboard_templates`・`dashboard_preview`・`dashboard_apply`・`dashboard_rollback`・`dashboard_snapshot`（10ツール。v0.9.0 は前の2つだけ）。Mate が自分のダッシュボードページを書くためのツール |

上表は v0.11.1 の `architecture/mcp.md` の「Server and tool inventory」表（1799-1815行。v0.9.0 では 1532-1546行）に従っています。ツール数は、この表が名前を挙げる数です。`mcp.md` は `kirocrew-core` のツールについて、**権威ある一覧は `kiro_crew.mcp_tools.build_tool_list()`**（`src/` 側）と記述しており（2403-2406行。v0.9.0 では 1620-1622行）、`src/` は解析していないため、本サイトは `kirocrew-core` のツール数を書きません。オプトインのサーバの付与方法は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md) を参照してください。

`kirocrew-dashboard` の 37 ツール（v0.11.1 タグの目録。v0.9.0 の目録は 31 ツールで、下記の `session_move_to_column`・`chat_session_pin_move`・`session_continue`・`session_rename`・`session_generate_title`・`session_history_list` の 6 つが v0.11.1 の追加です）:

- フォルダ（7）: `chat_folder_tree`・`chat_folder_create`・`chat_folder_move`・`chat_folder_update`・`chat_folder_move_session`・`chat_folder_delete`・`chat_folder_file_self`
- ボードタグ（4）: `chat_tag_list`・`chat_tag_create`・`chat_tag_update`・`chat_tag_assign`
- タグ列（4）: `chat_tag_column_list`・`chat_tag_column_create`・`chat_tag_column_move`・`session_move_to_column`（ボードの列へセッションを移す）
- ピン留め（2）: `chat_session_pin`・`chat_session_pin_move`
- 他セッションの操作（20）: `session_create`・`session_fork`・`session_stop`・`session_end_wait`・`session_retry`・`session_continue`・`session_set_model`・`session_reload`・`session_rename`・`session_generate_title`・`session_close`・`session_revive`・`session_history_list`・`session_send`・`session_broadcast`・`session_status`・`session_adopt`・`session_release`・`session_read_message`・`session_summary`

分類の件数は 7＋4＋4＋2＋20＝37 です。追加された 6 ツールのうち、`session_continue`（Continue ボタンと同じ継続）・`session_rename`（呼び出し元自身または対象のタイトルを設定）・`session_generate_title`（サイドバーの Regenerate title と同じ再生成）・`session_history_list`（復活できるアーカイブ済みセッションを新しい順に列挙）の説明は `modules/session-control.md` 26・29・30・33行の表にあります。`session_move_to_column`・`chat_session_pin_move` は名前が `mcp.md` の目録（1809行）にあり、個別の説明はこの版の `session-control.md` の表に見つかりません（`session_move_to_column` について `mcp.md` 4125行は、カードの移動はタグの書き込みでボードの書き込みではないと記述します）。

`session_*` の各ツールの説明は `modules/session-control.md` 14-37行の表に従います（例: `session_set_model` は待機中のセッションに保留中のモデル／推論 effort の選択を記録し、次のターン開始時に反映します。実行中の対象は `target_busy` で拒否されます）。

> ⚠ **出典間で記述が食い違っています。本サイトは裁定しません。** 管理対象サーバの数について、`architecture/mcp.md` 186-191行（v0.11.1）は**10サーバ**（`kirocrew-guide`・`kirocrew-mate` を常時有効に含む）と記述し、`modules/mcp-shareability.md` 44行（v0.11.1）は「All nine managed servers」として `kirocrew-mate` を挙げない**9サーバ**を列挙します。詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md#管理対象のmcpサーバ) を参照してください。
>
> 以前の本ページは、v0.7.2 時点の食い違い（`mcp.md` の「Managed servers」節が3サーバ、inventory 表が7サーバ、`mcp-shareability.md` が「All seven managed servers」）が v0.9.0 で 8 サーバに一致して解消したと記載していました。その解消は v0.11.1 では成り立ちません。v0.6.0 タグの inventory 表は、`kirocrew-dashboard`（当時は `chat_folder_*` の4ツールのみ）を加えた4サーバでした。

公式 `capabilities/mcp-tools`（Page updated 2026-08-31）は、管理対象サーバのうち常時有効の 2 つ（`kirocrew-core`・`kirocrew-cron`）だけを記述しています。仕様書が常時有効に加える `kirocrew-guide`・`kirocrew-mate` は公式にありません。

**出典**（管理対象サーバ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。186-191・1799-1815行）
**出典**（9サーバの記述）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/mcp-shareability.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。44行）
**出典**（`session_*`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/session-control.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。14-37行）

## ツール一覧

| ツール | サーバ | 用途 |
|-------|-------|------|
| `spawn_run` | `kirocrew-core` | サブエージェントを起動 |
| `learn_add` | `kirocrew-core` | レッスンを即時保存 |
| `task_run` | `kirocrew-core` | TaskRunnerでタスクを実行 |
| `local_knowledge_search` | `kirocrew-core` | Knowledge Libraryのハイブリッド検索。既定 `limit=3`、`min_score=0.012` |
| `skill_search` | `kirocrew-core` | インストール済みスキルの `search`・`list`・`read`。メタデータと本文の検索は SQLite の語索引（`skill_search_index.sqlite3`）から答え、ファイルを読みません |
| `update_message` | `kirocrew-core` | エージェントが既に送ったSlackメッセージをその場で更新（追跡中のチャンネル、またはオーナー自身のDM） |
| `pod_up` / `pod_down` / `pod_status` / `pod_ls` | `kirocrew-core` | worktree の isolated pod の操作。**Dev Fleet アプリを Apps → Library で有効にしたとき**に、エージェントが pod を起動してアドレス・ポート・短命トークンを受け取れます |
| `cron_add` / `cron_list` / `cron_update` / `cron_remove` / `cron_remove_all` / `cron_pause` / `cron_resume` / `cron_trigger` | `kirocrew-cron` | Cronジョブの作成・一覧・更新・削除・一時停止・再開・手動実行（`cron_remove_all` は全削除）。`cron_remove_all` と `cron_secret_request` には CLI の対応コマンドがないと `mcp.md` 2381-2383行（v0.9.0 では 1598-1599行）は記述します（`cron_remove_all` については公式との食い違いがあります。下記） |
| `cron_secret_request` | `kirocrew-cron` | エージェントが、cron ジョブに渡すシークレットの付与要求を保留として記録します。付与の承認・拒否は運営者側（`PUT /api/crons/{id}/secrets`。オーナーのみ）で行い、エージェントは付与できません（`learn-cron-dashboard.md` 719-734行） |
| `browser` | `kirocrew-core` | ブラウザ操作（`op` で操作を選ぶ単一ツール）。下記「[ブラウザのMCPツール](#ブラウザのmcpツール)」 |
| `knowledge_list_sources` | `kirocrew-core` | Knowledge Library のソース一覧と件数の合計。`kirocrew knowledge stats` の MCP 対応ツール（`mcp.md` 2379行。v0.9.0 では 1596行） |
| `computer_list_apps`・`computer_launch_app`・`computer_get_state`・`computer_click`・`computer_drag`・`computer_type_text`・`computer_press_key`・`computer_set_value`・`computer_scroll`・`computer_perform_action`・`computer_end_turn` | `kirocrew-computer` | Computer Useの操作（11ツール） |
| `chat_tag_list` / `chat_tag_create` / `chat_tag_update` / `chat_tag_assign` | `kirocrew-dashboard` | ボードタグの操作。エージェントはタグマネージャの **Agent permissions**（Human only／Agent: add only／Agent: add and remove）の範囲内で、セッションをタグ間で移動できます。予約されたタグは `tag_policy_denied`、ワークフロー状態タグは `status_identity_unprotected`、権限ストアが読めない場合は `tag_grants_unavailable` で失敗します（`mcp.md` 4091-4095行。v0.9.0 では 2125-2140行） |

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** `cron_remove_all` に対応する CLI について、`mcp.md` 2381-2383行（v0.11.1。v0.9.0 では 1598-1599行）は「`cron_remove_all` … have no CLI twin: `kirocrew cron remove` takes one job id」と記述し、`modules/cli.md` 343行（v0.11.1。v0.9.0 では 226行）も `kirocrew cron add/list/remove` と記述します。一方、公式 `features/cron`（Page updated 2026-10-20）72行と `interfaces/cli-reference`（Page updated 2026-10-20）176・182行は `kirocrew cron remove-all` を記述しています。v0.7.2 の `mcp.md` は `kirocrew cron remove-all` と `cron_remove_all` を対応づける行を持っていました（v0.9.0 で削除）。

> **以前の記述の訂正（`skill_search`）**: 本ページは以前、`skill_search` のサーバを「（スキル関連）」、挙動を「名前/説明→本文の順でgrep」と記載していました。サーバは v0.3.0 時点の仕様書でも `kirocrew-core` と明記されていました（誤り）。挙動は v0.6.0 タグの仕様書（memory-skills-hooks.md 995行）では grep でしたが、**v0.7.0 タグ以降の仕様書（v0.7.2 では 3216・3233-3235行、v0.9.0 では 4036・4093-4094行）は `search`・`list`・`read` をサポートし、SQLite の語索引から答えると記述しています**。この語索引は仕様書で確認したもので、CHANGELOG は説明していません。

> **以前の記述の訂正（Computer Use）**: 本ページは以前、`kirocrew-computer` のツールを「`computer_apps` / `computer_call`」と記載していました。これは誤りです。`architecture/mcp.md` の inventory 表は上記11ツール（v0.3.0 時点は `computer_launch_app` を除く10ツール）を挙げ、v0.7.2 の同ファイル1764-1771行（v0.9.0 では 2200-2208行）は `kirocrew computer call <tool>` を「**MCP twin を意図的に持たない**」人間向けのデバッグ用ハーネスとし、「do NOT add `computer_call`」と記述しています。`computer_apps` という名前のツールは仕様書に存在しません（CLI `kirocrew computer apps` の MCP twin は `computer_list_apps`）。

> **`pod_*` のトークン**: `modules/dev-fleet.md`（v0.9.0 では 361-366行。v0.7.2 では 303-307行）は、ツールの置き場所を `kirocrew-core`（`mcp_tools/apps.py`）とし、エージェントに返す pod トークンを「その pod 自身の Gateway にスコープされた2時間の資格情報」と記述しています。

**出典**（`skill_search`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。4036・4093-4094行）
**出典**（`update_message`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。1626-1633行）
**出典**（`pod_*`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/dev-fleet.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。361-366行）
出典: CHANGELOG.md v0.7.0節 127-130・170-172・410-414行（v0.7.2 タグのファイルの行番号、`c67c506`）

## ブラウザのMCPツール

v0.11.1 の `modules/browser.md` は、ブラウザ操作の経路を 2 つ記述しています（3-14行。v0.9.0 も同じ）。

- **デスクトップアプリ**: `kirocrew-core` の**単一の MCP ツール `browser`** が、Browser パネルのネイティブな埋め込み Chromium を操作します。Playwright のツール名前空間ではありません。`op` は `navigate`・`snapshot`・`click`・`type`・`press_key`・`hover`・`select_option`・`screenshot`・`wait_for`・`back`・`console` です
- **パネルが無い場合**、または `dashboard.use_builtin_browser`（既定 `true`）がオフの場合: ツールは `playwright-cli`（シェル）への切り替えを案内します

`navigate` が自動で扱うのは公開 HTTP(S) だけです。localhost・プライベート・リンクローカルなどは、承認が必要な CLI 経路に回ります（同 118-146行。v0.9.0 では 115-123行）。**例外**として、運営者が `dashboard.browser_local_origins` に書いたループバックの正確なオリジン（`localhost`・`127.0.0.1`・`[::1]` にポート必須）に一致する `navigate` は自動で扱われます。Gateway 自身の API ポートは列挙しても拒否され、エージェントは一覧を拡張できません。残るリスクとして、一覧のページを開いた後の `click`・`back` はそのページのリンクに従います（同 118-146行）。セッション開始時に検証済みのランチャーがないとき、プロンプトの `## Browser` 節は短い案内（`web_fetch`、Settings → Browser）に置き換わります（同 96-102行）。公式 `features/browser`（Page updated 2026-09-25）も「The native Browser tool in the packaged desktop app」と記述しています。詳細は [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md) を参照してください。

> **以前の記述の訂正**: 本ページは以前、「ブラウザ自動化は MCP ツールとして提供されません」「`browser.md` が『MCPサーバではなくシェル機能』と明記」と記載していました。これは v0.3.0〜v0.7.2 の `browser.md` の記述（「The browser is a shell capability, not a tool namespace」）に基づくものです。**v0.8.0 タグ以降の `browser.md` と `mcp.md` は、`kirocrew-core` の `browser` ツールを記述しています**。CHANGELOG の v0.8.0節・v0.9.0節に、このツールの記述はありません。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。3-14・96-102・118-146行）
**出典**: <https://kiro.dev/docs/crew/features/browser/>（Page updated 2026-09-25）

## v0.11.1でのMCP関連の変更

v0.10.0〜v0.11.1 の変更のうち、本ページの範囲のものです。詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md#v0111での変更) を参照してください。

- **管理対象サーバが10になった**: `kirocrew-guide`（12ツール）と `kirocrew-mate`（11ツール）が常時有効に加わりました。ただし `mcp-shareability.md` は9サーバ（`kirocrew-mate` なし）と記述し、出典間で食い違っています（上記「[管理対象サーバ](#管理対象サーバ)」）。v0.9.0 の仕様書にはなく、v0.10.0 タグの `mcp.md` で確認できます。CHANGELOG に説明はありません
- **`kirocrew-dashboard` が 31 → 37 ツール**、**`kirocrew-panel` が 2 → 10 ツール**になりました（`mcp.md` 1809・1813行）。`kirocrew-panel` の追加ツールは、Mate が自分のダッシュボードページを書く・適用する・ロールバックするためのものです（CHANGELOG.md v0.10.0節 253-255行、v0.11.0節 79-82行）。ルートセッションが自分のサイドパネルの Dashboard を書く経路も加わりました（`modules/artifacts.md`。[12_artifacts.md](../01_features/12_artifacts.md#v0111での変更)）
- **`hooks.confirm_tools`**: 運営者が指定したサーバの静的な許可を書かず、各呼び出しを PreToolUse ゲートに回します（`mcp.md` 418-475行。CHANGELOG に説明なし）
- **リモート MCP サーバのプローブが SSRF 検査を受ける**（CHANGELOG.md v0.11.0節 219-225行、`mcp.md` 516-540行）
- **KAS での MCP**: elicitation への応答、ライブセッションへのその場適用、`agent.kas_persist_mcp_sign_in`（既定オフ）（CHANGELOG.md v0.11.0節 158-161行）
- **ツールポリシーの対象**: Kiro Crew 自身のサーバだけに適用され、利用者がインストールした App が出すツールは対象外です（`mcp.md` 1626-1636行）

出典: CHANGELOG.md v0.10.0節 253-255行・v0.11.0節 79-82・158-161・219-225行（`fe6f5be`）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## v0.9.0でのMCP関連の変更

- **画面名: Agent Capabilities → Customize**（CHANGELOG.md v0.9.0節 150-153行）。公式 `capabilities/mcp-tools`（Page updated 2026-08-31）は「Agent Capabilities → Integrations (MCP)」と記述し、`architecture/mcp.md` 641行（v0.11.1 では 824行）は「The Connections page's MCP panel」と記述します。呼び名が出典ごとに異なるため、本サイトは裁定せず、両方を示します

## v0.8.0でのMCP関連の変更

- **管理対象サーバが8つに**: `kirocrew-debug` が加わりました（CHANGELOG は説明していません。`docs/reference/debug/README.md` 3-14行）
- **`kirocrew-dashboard` のツールが増えた**（v0.7.2 の目録は 14 ツール、**v0.8.0 タグの目録は 18 ツール、v0.9.0 タグの目録は 31 ツール**）: v0.9.0 タグの目録で加わったフォルダの `chat_folder_update`・`chat_folder_delete`、タグ列の `chat_tag_column_*`、`chat_session_pin`、`session_fork`・`session_end_wait`・`session_retry`・`session_set_model`・`session_reload`・`session_revive`・`session_broadcast`・`session_status`・`session_adopt`・`session_release`・`session_summary` を含みます（v0.8.0 タグの目録が新たに挙げるのは `chat_session_pin`・`session_fork`・`session_adopt`・`session_release` の4つで、`architecture/mcp.md` 1358行。v0.9.0 タグの目録は 1542行）。CHANGELOG（v0.8.0節）と v0.8.0 タグの `session-control.md` 22-26行は、これらのツールの大半（`session_set_model` を含む）を v0.8.0 で述べています。CHANGELOG は、別セッションが使うモデルの変更・ピン留め・トランスクリプトのフォーク・採用／解放を記載しています（v0.8.0節 310-329行）。ピン留めとモデルの変更は、テンプレートが dashboard ツール群をマウントしたエージェントが必要で、メッセージングチャネルから話しているエージェントには拒否されます
- **`kirocrew-work` の `work_ledger_rebuild`**: conductor が Crew log の記録から損傷した台帳を再構築できます（CHANGELOG.md v0.8.0節 315-317行に記載）。`architecture/mcp.md` の目録（1543行）と `ledger-conductor-sequence.md`（7行）に載るのは v0.9.0 タグからで、v0.8.0 タグの `docs/` には `work_ledger_rebuild` の記述が見つかりません
- **`kirocrew-cron` の `cron_secret_request`**（v0.7.2 の目録は `kirocrew-cron` を 8 ツール、`kirocrew-work` を 4 ツールとしていました）
- **自動承認の保持**: 自分で書いた `autoApprove` のリストが既定で保持されるようになりました（`mcp.honour_auto_approve`）。保持されたツールは Kiro Crew のツールゲートを通りません。詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md#自動承認autoapproveの扱い-mcphonour_auto_approve) を参照してください（CHANGELOG.md v0.8.0節 616-621行）
- **Kiro Crew 自身のツールが Tool Search で遅延提示される**（kiro-cli 2.27.0 以上）: 同ページを参照してください（CHANGELOG.md v0.8.0節 666-669行）
- **Crew log が既定オン**: `kirocrew-crew-log` が読む Crew log は、設定なしで記録されます（`KIROCREW_CREW_LOG=0` で無効。CHANGELOG.md v0.8.0節 330-336行）
- **`browser` ツール**: 上記「[ブラウザのMCPツール](#ブラウザのmcpツール)」を参照してください
- **`pod_*` ツール**は、v0.8.0 以降の `mcp.md` の目録（`kirocrew-core` の「App bridges」）に載っています（`mcp.md` 1691-1693行）。CHANGELOG の記載は v0.7.0節（下記）です

出典: CHANGELOG.md v0.8.0節 310-336・616-621・666-669行（`99e6253`）。

## v0.7.0でのMCP関連の変更

- **管理対象サーバの一覧が7サーバに**（v0.6.0 タグの inventory 表は4サーバ。v0.8.0 で8サーバ）。`kirocrew-work`・`kirocrew-crew-log`・`kirocrew-panel` が加わりました。`kirocrew-crew-log` は読み取り専用で、v0.7.0〜v0.7.2 では Crew log は `KIROCREW_CREW_LOG` 有効時に記録されました（**既定オフ**。v0.8.0 から既定オン）（314-318行）。`kirocrew-work`・`kirocrew-panel` は仕様書（inventory 表）で確認したもので、CHANGELOG は説明していません
- **`update_message`**（Slackの既投稿メッセージを更新）（170-172行）
- **`pod_*` ツール**（**Dev Fleet アプリ有効時**、エージェントが worktree の pod を起動）（127-130行）
- **`chat_tag` ツール**（ボードタグ間のセッション移動。タグマネージャで設定した権限の範囲内）（410-414行）
- **`local_knowledge_search` を1つの名前空間に絞り込める**、および **`kirocrew knowledge stats`** でライブラリのソース数・ドキュメント数・アイテム数を表示（263-267行）。`kirocrew knowledge stats` の MCP twin は `knowledge_list_sources`（`architecture/mcp.md`。v0.7.2 では 1227行、v0.9.0 では 1596行）。既定 `limit=3`・`min_score=0.012` は変わりません（`modules/knowledge.md`。v0.7.2 では 483行、v0.9.0 では 102・504行）
- **スキルの発見方法**: CHANGELOG は `skills.max_triggered` の既定が0になり、エージェントが短い索引と `skill_search` でスキルを発見するようになったと記載しています（419-422行）。設定の詳細は [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md) を参照してください

出典: CHANGELOG.md v0.7.0節 127-130・170-172・263-267・314-318・410-414・419-422行（v0.7.2 タグのファイルの行番号、`c67c506`）。

**出典**（`local_knowledge_search` の既定値）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
（`limit + 1` 行が返ることがあり、ツールは再度切り詰めません。同ファイル504行）

## v0.3.0でのMCP関連の変更

サーバ管理・ツール提示に関する変更が入っています（概念面の詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md) を参照）。

- **プロセス共有の可否をプローブ**（サーバ単位の選択がグローバルスイッチを置き換え）
- **per-agent tool sets**（サーバを特定エージェントに割り当て）
- **Tool Searchの遅延提示の度合いを設定可能**
- **認証付きカスタムサーバ**（リモートMCPサーバ追加時にリクエストヘッダを指定可）

出典: CHANGELOG.md v0.3.0節 166・169・172・174行（`21584ea`）。

## 未確認事項

- ツールの完全な一覧: `mcp.md` は `kirocrew-core` の権威ある一覧を `kiro_crew.mcp_tools.build_tool_list()`（`src/` 側）と記述しており、本ページは `src/` を解析していないため、`mcp.md` が名前を挙げるツールだけを記載します。公式 `capabilities/mcp-tools` は管理対象サーバを 2 つ（`kirocrew-core`・`kirocrew-cron`）しか記述しません
- `local_knowledge_search` を名前空間で絞り込む引数名: CHANGELOG v0.7.0節（v0.9.0 のファイルでは 977行、v0.11.1 のファイルでは 1378行）は「scoped to one namespace」と記載しています。v0.9.0 の `modules/knowledge.md` 506行が記述する絞り込みは `source_id` のみで、名前空間を指定する引数は仕様書で確認できません。公式 `features/knowledge` は「Scope a search to one source or namespace」と書きますが、引数名はありません
- v0.7.2 の `mcp.md` の目録にあった `browse_outline`・`browse_search` は、v0.8.0 以降の `mcp.md` と全 docs・CHANGELOG に記述がなく、廃止か改名か、単に列挙から外れたのかを一次情報から確認できません（本ページでは扱いません）
- `pod_*` ツールの導入版: CHANGELOG は v0.7.0節で記載していますが、`mcp.md` の目録に載るのは v0.8.0 以降です
- 管理対象サーバの数: v0.7.2 時点の食い違いは v0.9.0 で一致しましたが、v0.11.1 で `mcp.md`（10サーバ）と `mcp-shareability.md`（9サーバ）の食い違いが再発しています（上記「[管理対象サーバ](#管理対象サーバ)」参照）
- `session_move_to_column`・`chat_session_pin_move` の個別の説明: v0.11.1 の `session-control.md` の表に行がなく、`mcp.md` の目録に名前があるだけです

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
- MCP統合の概念: [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md)
- Computer Use・ブラウザ: [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)

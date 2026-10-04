# MCPツール一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [管理対象サーバ](#管理対象サーバ)
- [ツール一覧](#ツール一覧)
- [ブラウザはMCPではない](#ブラウザはmcpではない)
- [v0.7.0でのMCP関連の変更](#v070でのmcp関連の変更)
- [v0.3.0でのMCP関連の変更](#v030でのmcp関連の変更)
- [未確認事項](#未確認事項)

---

## 管理対象サーバ

| サーバ | 主なツール |
|-------|-----------|
| `kirocrew-core` | `spawn_run`（サブエージェント起動）、`learn_add`（レッスン追加）、`task_run`（タスク実行）、`local_knowledge_search`（Knowledge Library検索）、`skill_search`（スキル検索） |
| `kirocrew-cron` | cronスケジューリング関連ツール |
| `kirocrew-computer` | Computer Use（デスクトップGUI自動化）のシム |
| `kirocrew-dashboard` | `chat_folder_tree`・`chat_folder_create`・`chat_folder_move`・`chat_folder_move_session`・`chat_folder_file_self`・`chat_tag_list`・`chat_tag_create`・`chat_tag_update`・`chat_tag_assign`・`session_create`・`session_send`・`session_read_message`・`session_stop`・`session_close` |
| `kirocrew-work` | `work_brief`・`work_report`・`work_ledger_read`・`work_ledger_record` |
| `kirocrew-crew-log` | `crew_log_list`・`crew_log_read`・`crew_log_projection` |
| `kirocrew-panel` | `panel_publish`・`panel_templates` |

上表は v0.7.2 タグの `architecture/mcp.md` の inventory 表（1175-1186行）に従っています。同表は7サーバを「registered by `agent._MANAGED_MCP_SERVERS`」と記載し、`kirocrew.json` にインストールされるとしています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - 同じ `architecture/mcp.md` の145-147行は「`agent._MANAGED_MCP_SERVERS` holds the **three** servers the gateway owns end to end: `kirocrew-cron`, `kirocrew-core`, `kirocrew-computer`」とし、この3件が再構築のたびに `_refresh_dynamic_fields()` で `command`/`args` を書き換えられると記述しています
> - 同ファイルの inventory 表（1175-1186行）と `modules/mcp-shareability.md`（46行「All seven managed servers」）は7サーバとしています。同ファイル1908-1909行は後半4サーバを「the opt-in Crew servers」と呼び、1411-1413行は `opt_in` と印を付けたサーバは既定のエージェントに追加されないと記述しています
>
> 詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md) を参照してください。本ページは以前「`agent._MANAGED_MCP_SERVERS` がこの3件を所有」とだけ記載していました（v0.6.0 タグの inventory 表は `kirocrew-dashboard` を加えた4サーバ）。
>
> **出典**（管理対象サーバ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

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
| `cron_add` | `kirocrew-cron` | Cronジョブの作成 |
| `computer_list_apps`・`computer_launch_app`・`computer_get_state`・`computer_click`・`computer_drag`・`computer_type_text`・`computer_press_key`・`computer_set_value`・`computer_scroll`・`computer_perform_action`・`computer_end_turn` | `kirocrew-computer` | Computer Useの操作（11ツール） |
| `chat_tag_list` / `chat_tag_create` / `chat_tag_update` / `chat_tag_assign` | `kirocrew-dashboard` | ボードタグの操作。エージェントはタグマネージャで設定した権限の範囲内で、セッションをタグ間で移動できます |

> **以前の記述の訂正（`skill_search`）**: 本ページは以前、`skill_search` のサーバを「（スキル関連）」、挙動を「名前/説明→本文の順でgrep」と記載していました。サーバは v0.3.0 時点の仕様書でも `kirocrew-core` と明記されていました（誤り）。挙動は v0.6.0 タグの仕様書（memory-skills-hooks.md 995行）では grep でしたが、**v0.7.0 タグ以降の仕様書（v0.7.2 では 3216・3233-3235行）は `search`・`list`・`read` をサポートし、SQLite の語索引から答えると記述しています**。この語索引は仕様書で確認したもので、CHANGELOG は説明していません。

> **以前の記述の訂正（Computer Use）**: 本ページは以前、`kirocrew-computer` のツールを「`computer_apps` / `computer_call`」と記載していました。これは誤りです。`architecture/mcp.md` の inventory 表は上記11ツール（v0.3.0 時点は `computer_launch_app` を除く10ツール）を挙げ、同ファイル1764-1771行は `kirocrew computer call <tool>` を「**MCP twin を意図的に持たない**」人間向けのデバッグ用ハーネスとし、「do NOT add `computer_call`」と記述しています。`computer_apps` という名前のツールは仕様書に存在しません（CLI `kirocrew computer apps` の MCP twin は `computer_list_apps`）。

> **`pod_*` のトークン**: `modules/dev-fleet.md`（303-307行）は、ツールの置き場所を `kirocrew-core`（`mcp_tools/apps.py`）とし、エージェントに返す pod トークンを「その pod 自身の Gateway にスコープされた2時間の資格情報」と記述しています。

**出典**（`skill_search`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（`update_message`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2。1254-1260行）
**出典**（`pod_*`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/dev-fleet.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
出典: CHANGELOG.md v0.7.0節 127-130・170-172・410-414行（`c67c506`）

## ブラウザはMCPではない

**ブラウザ自動化はMCPツールとして提供されません。** `playwright-cli` をシェル機能として実行するため、登録すべきMCPサーバは存在しません。詳細は [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md) を参照してください。

> **v0.3.0でも変わりません**: v0.3.0でBrowser panel（ダッシュボードのサイドパネルをエージェントが直接操作する経路）が追加されましたが、`docs/system-specs/modules/browser.md` 10行（`21584ea`）は引き続き「The browser is a **shell capability, not a tool namespace.**」と記述しており、**MCPサーバ化されたわけではありません**。同ファイル362行も「why browsing is deliberately not an MCP」として`architecture/mcp.md`を参照しています。

## v0.7.0でのMCP関連の変更

- **管理対象サーバの一覧が7サーバに**（v0.6.0 タグの inventory 表は4サーバ）。`kirocrew-work`・`kirocrew-crew-log`・`kirocrew-panel` が加わりました。`kirocrew-crew-log` は読み取り専用で、Crew log は `KIROCREW_CREW_LOG` 有効時に記録されます（**既定オフ**）（314-318行）。`kirocrew-work`・`kirocrew-panel` は仕様書（inventory 表）で確認したもので、CHANGELOG は説明していません
- **`update_message`**（Slackの既投稿メッセージを更新）（170-172行）
- **`pod_*` ツール**（**Dev Fleet アプリ有効時**、エージェントが worktree の pod を起動）（127-130行）
- **`chat_tag` ツール**（ボードタグ間のセッション移動。タグマネージャで設定した権限の範囲内）（410-414行）
- **`local_knowledge_search` を1つの名前空間に絞り込める**、および **`kirocrew knowledge stats`** でライブラリのソース数・ドキュメント数・アイテム数を表示（263-267行）。`kirocrew knowledge stats` の MCP twin は `knowledge_list_sources`（`architecture/mcp.md` 1227行）。既定 `limit=3`・`min_score=0.012` は変わりません（`modules/knowledge.md` 483行）
- **スキルの発見方法**: CHANGELOG は `skills.max_triggered` の既定が0になり、エージェントが短い索引と `skill_search` でスキルを発見するようになったと記載しています（419-422行）。設定の詳細は [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md) を参照してください

出典: CHANGELOG.md v0.7.0節 127-130・170-172・263-267・314-318・410-414・419-422行（`c67c506`）。

**出典**（`local_knowledge_search` の既定値）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## v0.3.0でのMCP関連の変更

サーバ管理・ツール提示に関する変更が入っています（概念面の詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md) を参照）。

- **プロセス共有の可否をプローブ**（サーバ単位の選択がグローバルスイッチを置き換え）
- **per-agent tool sets**（サーバを特定エージェントに割り当て）
- **Tool Searchの遅延提示の度合いを設定可能**
- **認証付きカスタムサーバ**（リモートMCPサーバ追加時にリクエストヘッダを指定可）

出典: CHANGELOG.md v0.3.0節 166・169・172・174行（`21584ea`）。

## 未確認事項

- ツールの完全な一覧（本ページは確認できた主要ツールのみを記載。網羅的なリストは公式に見当たらない）
- 管理対象サーバの数（`architecture/mcp.md` 内で「three」と7行の inventory 表が食い違う。本サイトは裁定せず両方を記載）
- `local_knowledge_search` を名前空間で絞り込む引数名（CHANGELOG v0.7.0節 265行は「scoped to one namespace」と記載。v0.7.2 タグの `modules/knowledge.md` 484行が記述する絞り込みは `source_id` で、これは v0.6.0 タグの同ファイル 370行にも既に記載されている。名前空間を指定する引数は仕様書で確認できない）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
- MCP統合の概念: [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md)
- Computer Use・ブラウザ: [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)

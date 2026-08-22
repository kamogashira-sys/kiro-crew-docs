# MCPツール一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [3つの管理対象サーバ](#3つの管理対象サーバ)
- [ツール一覧](#ツール一覧)
- [ブラウザはMCPではない](#ブラウザはmcpではない)
- [v0.3.0でのMCP関連の変更](#v030でのmcp関連の変更)
- [未確認事項](#未確認事項)

---

## 3つの管理対象サーバ

| サーバ | 主なツール |
|-------|-----------|
| `kirocrew-core` | `spawn_run`（サブエージェント起動）、`learn_add`（レッスン追加）、`task_run`（タスク実行）、`local_knowledge_search`（Knowledge Library検索） |
| `kirocrew-cron` | cronスケジューリング関連ツール |
| `kirocrew-computer` | Computer Use（デスクトップGUI自動化）のシム |

`agent._MANAGED_MCP_SERVERS` がこの3件を両端まで所有し、再構築のたびに `command`/`args` を書き換えます。

## ツール一覧

| ツール | サーバ | 用途 |
|-------|-------|------|
| `spawn_run` | `kirocrew-core` | サブエージェントを起動 |
| `learn_add` | `kirocrew-core` | レッスンを即時保存 |
| `task_run` | `kirocrew-core` | TaskRunnerでタスクを実行 |
| `local_knowledge_search` | `kirocrew-core` | Knowledge Libraryのハイブリッド検索。既定 `limit=3`、`min_score=0.012` |
| `skill_search` | （スキル関連） | インストール済みスキルの名前/説明→本文の順でgrep |
| `cron_add` | `kirocrew-cron` | Cronジョブの作成 |
| `computer_apps` / `computer_call` | `kirocrew-computer` | Computer Useの操作 |

## ブラウザはMCPではない

**ブラウザ自動化はMCPツールとして提供されません。** `playwright-cli` をシェル機能として実行するため、登録すべきMCPサーバは存在しません。詳細は [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md) を参照してください。

> **v0.3.0でも変わりません**: v0.3.0でBrowser panel（ダッシュボードのサイドパネルをエージェントが直接操作する経路）が追加されましたが、`docs/system-specs/modules/browser.md` 10行（`21584ea`）は引き続き「The browser is a **shell capability, not a tool namespace.**」と記述しており、**MCPサーバ化されたわけではありません**。同ファイル362行も「why browsing is deliberately not an MCP」として`architecture/mcp.md`を参照しています。

## v0.3.0でのMCP関連の変更

サーバ管理・ツール提示に関する変更が入っています（概念面の詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md) を参照）。

- **プロセス共有の可否をプローブ**（サーバ単位の選択がグローバルスイッチを置き換え）
- **per-agent tool sets**（サーバを特定エージェントに割り当て）
- **Tool Searchの遅延提示の度合いを設定可能**
- **認証付きカスタムサーバ**（リモートMCPサーバ追加時にリクエストヘッダを指定可）

出典: CHANGELOG.md v0.3.0節 166・169・172・174行（`21584ea`）。

## 未確認事項

- ツールの完全な一覧（本ページは確認できた主要ツールのみを記載。網羅的なリストは公式に見当たらない）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
- MCP統合の概念: [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md)
- Computer Use・ブラウザ: [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)

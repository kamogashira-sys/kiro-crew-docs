# MCPツール一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [3つの管理対象サーバ](#3つの管理対象サーバ)
- [ツール一覧](#ツール一覧)
- [ブラウザはMCPではない](#ブラウザはmcpではない)
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

## 未確認事項

- ツールの完全な一覧（本ページは確認できた主要ツールのみを記載。網羅的なリストは公式に見当たらない）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
- MCP統合の概念: [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md)
- Computer Use・ブラウザ: [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)

# MCP統合

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/capabilities/mcp-tools/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [MCP-firstの設計原則](#mcp-firstの設計原則)
- [3つのMCPサーバ](#3つのmcpサーバ)
- [設定ファイルの分離](#設定ファイルの分離)
- [マージの優先順位](#マージの優先順位)
- [未確認事項](#未確認事項)

---

## MCP-firstの設計原則

**設計上の不変条件**: Kiro Crew はプロバイダのグローバル設定に書き込みません。`~/.kiro/settings/mcp.json` はユーザー所有で、Kiro Crew はこれを読むだけで決して変更しません。Kiro Crew 自身の追加は、完全に所有する per-agent ファイル `~/.kiro/agents/kirocrew.json` に入ります。これにより、Kiro Crew に紐づくツールがKiro Crew外の対話的なkiro-cliやKiro IDEセッションに漏れ出すことを防いでいます。

LLMが使う新機能は、Skillsのラッパーではなく**MCP Toolとして提供する**のが原則です（[07_agents-skills-steering.md](07_agents-skills-steering.md)参照）。「LLMツールの仕組み」としてMCPツールが**LLM向けの操作すべてに優先**されます。

## 3つのMCPサーバ

Gatewayが両端まで所有する3つの管理対象サーバです（`agent._MANAGED_MCP_SERVERS`）。

| サーバ | 役割 |
|-------|------|
| `kirocrew-core` | `spawn_run`（サブエージェント起動）・`learn_add`（レッスン追加）・`task_run`（タスク実行）等 |
| `kirocrew-cron` | cronスケジューリング関連ツール |
| `kirocrew-computer` | Computer Use（デスクトップGUI自動化）のシム |

各サーバは再構築のたびに `_refresh_dynamic_fields()` によって `command`/`args` が書き換えられます。**ブラウザ自動化はここに含まれません**（`browser.md` が「MCPサーバではなくシェル機能」と明記。詳細は [13_computer-and-browser.md](13_computer-and-browser.md)）。

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

## 未確認事項

- なし（本ページの記述は `docs/architecture/mcp.md` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/capabilities/mcp-tools/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
- Computer Use・ブラウザ: [13_computer-and-browser.md](13_computer-and-browser.md)
- MCPツール一覧: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)

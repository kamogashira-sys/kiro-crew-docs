# 設定キー・環境変数

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**（`session.pool_size`既定値の不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**（`agent.max_subagents`既定値の不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [設定ファイル](#設定ファイル)
- [主な設定キー](#主な設定キー)
- [環境変数](#環境変数)
- [未確認事項](#未確認事項)

---

## 設定ファイル

`~/.kiro/crew/config.json`（`config.local.json` によるオーバーレイあり）。

## 主な設定キー

| キー | 既定値 | 説明 |
|------|-------|------|
| `agent.sandbox` | `auto` | サンドボックスモード（`auto`／`strict`／`off`。[09_security.md](../01_features/09_security.md)参照） |
| `agent.provider` | `acp`（固定） | LLMプロバイダ。変更不可 |
| `agent.max_subagents` | **食い違いあり** | Subagentの並行数上限。`subagent.md`は既定`0`（自動サイジング）、`config.md`のdataclass literalは既定`3`（両併記・裁定しない） |
| `agent.subagent_auto_max` | **食い違いあり** | 自動サイジングの上限。`subagent.md`は32、`config.md`は16と記述（両併記・裁定しない） |
| `agent.apps_allow_third_party` | `false` | サードパーティAppの実行許可スイッチ |
| `agent.sandbox_allow_unsandboxed_exec` | `false` | サンドボックスバックエンド不在時の非サンドボックス実行を許可するopt-in |
| `agent.chat_turn_timeout_secs` | `7200`（2時間） | チャットターンの上限（ロード時クランプは300〜86400秒、無効化不可） |
| `agent.tool_approval_timeout_secs` | `600`（10分） | ツール承認の待機時間 |
| `session.pool_size` | **食い違いあり** | Warm Poolのサイズ。`overview.md`は既定`0`（オフ）、`config.md`のdataclass literalは既定`2`（両併記・裁定しない） |
| `session.pool_ttl_secs` | `1800` | Warm Pool内プロセスのTTL |
| `session.timeout_secs` | `3600` | セッションのアイドルタイムアウト |
| `session.autocompact_pct` | `90` | 自動圧縮のコンテキスト使用率閾値 |
| `memory.history_idle_hours` | `3.0` | 履歴統合のアイドルトリガー |
| `memory.history_max_days` | `365` | 履歴のディスク保持期間 |
| `memory.embedding_provider` | `llama_cpp`（固定。legacy値も強制コアース） | メモリシステムの埋め込みプロバイダ |
| `skills.lazy_load` | `false` | スキルのon-demandセット注入方式 |
| `hooks.denied_commands.user_added` | – | インポート等で追加されたユーザー定義の拒否ルール |
| `mcp_gateway.enabled` | – | MCP Gatewayの有効化 |
| `dashboard.url` | 省略時 `localhost:5476` | ダッシュボードの到達先URL |

## 環境変数

| 変数 | 用途 |
|------|------|
| `KIROCREW_HOME` | データホームの変更（既定 `~/.kiro/crew/`） |
| `KIROCREW_PORT` | ダッシュボードポートの上書き（開発時） |
| `KIROCREW_TELEMETRY_DISABLED` | `1` で匿名テレメトリを無効化（Settings・`config.json`の設定を上書き） |
| `KIROCREW_VENV` | 仮想環境の場所の上書き |
| `KIROCREW_PROJECT_DIR` | プロジェクト単位のスキルディレクトリの参照先 |

## 未確認事項

- `agent.max_subagents` の真の既定値（`subagent.md`は0、`config.md`は3。両併記のまま）
- `agent.subagent_auto_max` の真の既定値（32 vs 16。両併記のまま）
- `session.pool_size` の真の既定値（`overview.md`は0、`config.md`は2。両併記のまま）
- `spawn_min_memory_gb` の既定値（`subagent.md`・`config.md`のいずれにも数値記載なし）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
- ディレクトリ構造: [03_directory-layout.md](03_directory-layout.md)
- 上限値: [05_limits.md](05_limits.md)

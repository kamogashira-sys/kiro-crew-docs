# 既存設定の引き継ぎ

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [2つの引き継ぎ経路](#2つの引き継ぎ経路)
- [3フェーズ](#3フェーズ)
- [8カテゴリ](#8カテゴリ)
- [移行されないもの（明示的な非対象）](#移行されないもの明示的な非対象)
- [未確認事項](#未確認事項)

---

## 2つの引き継ぎ経路

1. **`.kiro` はランタイムがネイティブに読む**（移行不要）: Kiro CLIの設定はKiro Crewがそのまま利用します
2. **他エージェントからは一度きりのインポート**: 組み込みの**5ソース**（Codex・Claude Code・Gemini・OpenClaw・Hermes）に加え、エディションが `ImportSourceProvider`（CPPシーム）で登録したソースから、`onboarding_import.py` が設定を移行します

> **以前の記述の訂正**: 本ページは以前、5ソースの1つを「MeshClaw」と記載していました。これは v0.3.0（`21584ea`）の `modules/onboarding-import.md`（26行: `codex`, `claude_code`, `meshclaw`, `openclaw`, `hermes`）に基づくもので、**v0.4.1・v0.6.0・v0.7.0・v0.7.2 の各タグの同ファイルでは `meshclaw` に代わって `gemini` が並び、「plus any an edition registers through the `ImportSourceProvider` CPP seam」が付記されています**。CHANGELOG v0.4.0節（1420行）は「First-run setup imports from Gemini CLI and Antigravity, including their MCP servers and workspaces」と記載しています。MeshClaw が対象から外れたことは CHANGELOG に記載がありません。
>
> `gemini` は Google の端末エージェントの系譜を1つのIDでまとめたソースです。Antigravity CLI が独自のディレクトリを持たず `~/.gemini` を再利用するため、1つのルートに Gemini CLI の設定と Antigravity のインストールの両方が入ります（同ファイル26-30行）。
>
> **出典**（ソース一覧）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2。22-30行）
> 出典: CHANGELOG.md v0.4.0節 1420行（`c67c506`）

このモジュールは**投影（projection）であり、ミラーではありません**。他エージェントのレイアウトを読み、Kiro Crew自身のコンテナにKiro Crew自身のAPI経由でのみ書き込みます。独自のストレージ形式を発明したり、Kiro Crewが読まないファイルを書いたり、他エージェントのストアをそのまま複製することはありません。

初回起動時のオンボーディングフロー（Kiro CLIの前提条件チェックの後、テーマツアーの前）、およびSettingsからオンデマンドで実行できます。

## 3フェーズ

常にこの順序で実行されます。

| フェーズ | エントリポイント | 書き込みするか |
|---------|--------------|--------------|
| Detect（検出） | `detect_sources()` | しない |
| Dry run（プレビュー） | `preview_import()` | **しない — ディスクに一切触れない** |
| Apply（適用） | `apply_import()` | する（マージのみ） |

## 8カテゴリ

| カテゴリ | 理由 | 移送先 |
|---------|------|-------|
| `instructions` | ユーザーが書いたルール。最も再現不可能な資産 | メモリ階層 |
| `memories` | プレーンMarkdownの知識。エージェント間で意味的に安定 | メモリ階層 |
| `skills` | 自己完結型ディレクトリ＋`SKILL.md`。ほぼ同一の形式 | `skills/imported/<source>/<name>/` |
| `mcp_servers` | 事実上の標準形式（`mcpServers` / `[mcp_servers.*]`） | `mcp.json` → `mcpServers` |
| **`denied_commands`** | 手作業で調整された拒否ルール。再作成は手間がかかりミスしやすい | `config.json` → `hooks.denied_commands.user_added` |
| `settings` | 曖昧さのないスカラーのみ（タイムゾーン・テーマモード・テーマ色） | `config.json` |
| `workspaces` | プロジェクトディレクトリ（明示的な設定からのみ） | `config.json` → `workspaces` |
| `schedules` | 移植可能なcron/interval仕様 | `CronService`。**必ず `enabled=False`** |

衝突方針は既定でskip（既存を維持）ですが、`instructions`・`memories` は**merge-onlyのため衝突しません**。

## 移行されないもの（明示的な非対象）

いずれも意図的な除外です。ギャップに見えても「復元」してはいけません。

| 除外対象 | 理由 |
|---------|------|
| **セッション／会話の文字起こし** | 業界的な慣行ではない（調査対象のどのエージェントも文字起こしを移行しない）。文字起こしは別のモデル・別のシステムプロンプトの会話の記録であり、Kiro Crewに再生すると誤解を招くコンテキストになる |
| **ペルソナ／`SOUL.md`をペルソナとして** | Kiro Crewのペルソナサーフェスはテーマパックのペルソナ（`capabilities.theme_persona`が管理）。ファイルの**指示的な内容**はメモリとして移行されるが、ペルソナとしての役割は落とされる |
| **いかなる認証情報も** | `~/.claude/.credentials.json`・`~/.codex/auth.json`・`.env`・`auth-profiles.json`・Gatewayトークン・プロバイダAPIキー。決して読まれない |
| **ランタイム状態** | サブエージェントの記録・ツール結果・チェックポイント・フック状態・実行中のタスク状態 |
| **アーキテクチャ固有の設定** | プラグイン／フック／バインディング／エージェントリストの設定、メモリバックエンドの選択、プロバイダとモデルのマッピング（Kiro CrewはKiroACP専用のため移送先がない） |
| **不透明なバイナリストア** | 他エージェントのSQLiteメモリストアは `unsupported_memory_database` として報告されるのみで解析されない |
| **許可リスト（拒否リストとは逆）** | 他エージェントの `permissions.allow` はセキュリティ境界を**広げる**ため、インポートしない（拒否ルールのみ対象） |

## 未確認事項

- なし（本ページの記述は `modules/onboarding-import.md` で確認済み）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
- メモリシステム: [04_memory-and-learning.md](04_memory-and-learning.md)
- セキュリティ: [09_security.md](09_security.md)

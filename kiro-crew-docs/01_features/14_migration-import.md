# 既存設定の引き継ぎ

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [2つの引き継ぎ経路](#2つの引き継ぎ経路)
- [3フェーズ](#3フェーズ)
- [8カテゴリ](#8カテゴリ)
- [衝突方針](#衝突方針)
- [移行されないもの（明示的な非対象）](#移行されないもの明示的な非対象)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
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

衝突方針は既定でskip（既存を維持）ですが、`instructions`・`memories` は**merge-onlyのため衝突しません**。詳細は次節「[衝突方針](#衝突方針)」を参照してください。

**出典**（ソース・フェーズ・カテゴリ）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。5-30行・166-175行）

## 衝突方針

移行先に同名の項目が既にあるときは、ハード失敗ではなく**ユーザーが決める事項**として扱われます。適用リクエストが方針を持ち、既定は最も安全な `skip` です（364-383行）。

| 方針 | 動作 |
|------|------|
| `skip`（**既定**） | Kiro Crew の既存の項目に触れず、取り込み側を `conflict` として報告 |
| `rename` | 派生した重複しない名前で並べて取り込む |
| `overwrite` | 復元用のコピーを書いたうえで、既存の項目を置き換える |

カテゴリごとの適用範囲と `rename` の名前の作り方:

| カテゴリ | 使える方針 | `rename` の名前 |
|---------|-----------|----------------|
| `skills` | skip・rename・overwrite | `<name>-<source>`、次に `<name>-<fingerprint[:8]>`（v0.8.0 以前は `<name>-imported-<source>`） |
| `mcp_servers` | skip・rename・overwrite | `<name>-<source>`、次に `<name>-<fingerprint[:8]>` |
| `workspaces` | skip・rename | `base-<source>`、次に `base-<fp[:8]>`（`skip` は衝突を報告するだけで、接尾辞は `rename` のときだけ作られる） |
| `instructions`・`memories` | 適用なし（merge-only） | — |
| `denied_commands`・`settings` | 適用なし（不足分だけ追加） | — |
| `schedules` | skip のみ（重複するスケジュールは `_same_schedule` で照合） | — |

`skills` の `rename` の名前が `<name>-imported-<source>` から `<name>-<source>` に変わった点は、v0.8.0 タグ（347行）と v0.9.0 タグ（379行）の仕様書の差分で確認したもので、CHANGELOG/Release 本文は説明していません。

**出典**（衝突方針）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。364-383行）

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

## v0.9.0での変更

本節は、v0.9.0 タグの `onboarding-import.md` を v0.8.0 タグの同ファイルと比べて確認したものです。**CHANGELOG/Release 本文は、このうち設定のエクスポートを除いて説明していません**。

- **設定のエクスポートに永続チャット履歴を含められる**: Settings → Import / Export で、エクスポートに永続チャット履歴を含められます（CHANGELOG.md v0.9.0節 129-130行）。`docs/feature-map/README.md` 202行の「Portability」は、メモリ・設定のバンドル全体のエクスポートとインポートで、永続チャット履歴を任意で含められ（インポート側は追加のみ）、crew agent template がバンドルに含まれない場合は両端で警告すると記述しています。**これは Kiro Crew 自身のバンドルのエクスポート／インポートで、本ページが扱う他エージェントからの一度きりのインポートとは別の機能です**
- **ペルソナ識別のガードが見出し行も検査する**: 取り込む指示の段落に「You are …」のような識別の行があると、その段落ごと除外されます。v0.9.0 の仕様書は、ガードが段落の**すべての行**（見出しを含む）を、見出し・リスト・引用・強調の記号を取り除いたうえで検査し、`# You are Aria` も段落を除外すると記述しています（250-253行）。v0.8.0 タグの仕様書は「every non-heading line」（見出し以外のすべての行）でした
- **スキルの `rename` の名前**: 上記「[衝突方針](#衝突方針)」を参照
- **診断名の変更**: 読み取れないソースを報告する診断名が `scanner_failed` から `source_unreadable`（unsupported の診断）になりました。読み取れないソースの部分的な結果は破棄され、他のソースの取り込みには影響しません（590-594行）
- **`PUT /api/onboarding/import/state` の失敗コード**: `invalid_request`（400）、`config_unreadable`（500。`config.json` が解析できず、再試行しても解消しない）、`state_failed`（500）。完了の保存に失敗したとき、初回の Import ステップは「保存せずに離れる」ローカルの出口を出します（670行）。v0.8.0 タグの仕様書は `{completed: bool}` だけを記述していました
- **内部構造の記述**: 仕様書の「Structure and ownership」節は v0.8.0 タグで加わったもので（v0.7.2 には無し。v0.8.0 タグでは32-128行）、v0.9.0 タグでも同じ位置にあります（v0.9.0 タグでは32-158行）。エンジンの内部構成の記述で、利用者の操作は変わりません

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.9.0節 129-130行（`99e6253`）。

## v0.8.0での変更

- **初回の Import 設定ステップが保存できないとき、「Close setup for now」が出る**: 解析できない `config.json` は、テーマ・言語・オンボーディングの変更でも既定値で上書きされなくなりました（CHANGELOG.md v0.8.0節 685-694行）
- **オンボーディングの完了を保存するリクエストが POST から PUT に変わった**: v0.7.2 タグの仕様書は `POST /api/onboarding/import/state`、v0.8.0 タグ以降は `PUT` と記述しています（v0.7.2 の 540行、v0.8.0 の 637行）。CHANGELOG はこの変更を説明していません

出典: CHANGELOG.md v0.8.0節 685-694行（`99e6253`）。

## 未確認事項

- なし（本ページの記述は `modules/onboarding-import.md` の v0.9.0 タグで確認済み。ただし、v0.9.0 の `onboarding-import.md` の記述と、各ソース（Codex・Claude Code・Gemini・OpenClaw・Hermes）の実際のレイアウトとの一致は `src/` を解析していないため未確認）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/onboarding-import.md>
- メモリシステム: [04_memory-and-learning.md](04_memory-and-learning.md)
- セキュリティ: [09_security.md](09_security.md)

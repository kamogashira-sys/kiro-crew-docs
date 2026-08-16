# エージェント・スキル・Steering

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/capabilities/>（agents/agent-templates/skills/steering/hooks/prompts配下、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [エージェント設定](#エージェント設定)
- [エージェントの切り替え](#エージェントの切り替え)
- [スキル](#スキル)
- [`skill://` によるIDE/CLIとの往復](#skill-によるidecliとの往復)
- [Hooks](#hooks)
- [未確認事項](#未確認事項)

---

## エージェント設定

エージェント設定は `~/.kiro/agents/*.json` に置かれるJSONファイルで、kiro-cliに「どう振る舞うか」（システムプロンプト・有効なツール・MCPサーバ）を指示します。詳細は [01_architecture.md](01_architecture.md) を参照してください。

## エージェントの切り替え

Slackでは `!agent <name>` または `!agent off` というowner専用コマンドでアクティブなエージェントを切り替えられます（全新規セッションに適用）。エージェント解決の優先順位は「スレッド上書き（`!agent`）→チャネル単位の上書き→設定された既定値→標準の `kirocrew` フォールバック」の順です。

## スキル

Markdownファイル（`~/.kiro/crew/skills/{name}/SKILL.md`）で、任意のYAML frontmatter（`name`・`description`・`always`）を持ちます。ネストしたディレクトリもサポートされます（例: `skills/utils/tiny-url/SKILL.md`）。

**ソース優先順位**（プロジェクトレベルが勝つ）: `$KIROCREW_PROJECT_DIR/skills/` → `builtin_skills/`（バンドル済み）。初回起動時に `~/.kiro/crew/skills/` へ自動コピーされます。

### 読み込み方式

1. **Always-on**（常時オン）: `always: true` のスキルは新しいセッションごとに全文が注入されます
2. **On-demand**（オンデマンド）: スキルの要約（名前＋説明＋ディレクトリパス）がセッションコンテキストに入り、LLMが必要に応じて `cat` でファイルを読めます

**Lazy-load**（`skills.lazy_load`、既定false）は on-demand セットの注入方法を制御します。OFFなら全件をランク付けなしで生の165kバジェット内にダンプし、ONなら常時オンのスキルを全文注入＋使用頻度でランク付けした上位K件をバジェット内に収めます。

**トリガー式**（README等で言及される「Triggered」）は `max_triggered`（既定0）を有効にすることで、メッセージのキーワードに一致するスキルを都度読み込む仕組みです。既定では無効です。

### 用途の区別

「LLMツールの仕組み」として、MCPツール（`kirocrew-cron`・`kirocrew-core`のようなネイティブツール）が**LLM向けの操作すべてに優先されます**。スキルは**オンデマンドの知識のためだけ**にあり、CLIコマンドのラッパーとしては使いません（MCPツールを使う）。

## `skill://` によるIDE/CLIとの往復

エージェント設定は `skill://` というグロブパターンでスキルを参照でき、これによりCrew・Kiro IDE・Kiro CLI 間でスキルの往復ができます。この仕組みは `annotate_skills_with_agents` がエージェントJSONを解析し、`skill://` グロブを事前展開して各スキルと照合する形で実装されています。

## Hooks

`hooks.py` がconfig駆動のフック機構を提供します（PreToolUseゲート等）。詳細はセキュリティ節（[09_security.md](09_security.md)）で扱います。

## 未確認事項

- なし（本ページの記述は公式 `capabilities/` 配下と `memory-skills-hooks.md` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/capabilities/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
- アーキテクチャ: [01_architecture.md](01_architecture.md)
- セキュリティ: [09_security.md](09_security.md)

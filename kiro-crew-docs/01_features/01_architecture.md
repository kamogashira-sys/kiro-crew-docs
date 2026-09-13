# アーキテクチャ

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/providers.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [3層構造](#3層構造)
- [Kiro CLI との差分](#kiro-cli-との差分)
- [プロバイダは acp 固定](#プロバイダは-acp-固定)
- [メッセージフロー](#メッセージフロー)
- [データの置き場所](#データの置き場所)
- [未確認事項](#未確認事項)

---

## 3層構造

Kiro Crew は次の3層の上に成り立っています。

1. **kiro-cli** — エージェントの**ランタイム**（エージェント本体ではない）。LLM 接続・ツール実行（bash・ファイル読み書き・grep・glob）・MCP サーバ管理・セッション永続化・コンテキスト圧縮、そして **ACP**（Agent Client Protocol。任意のオーケストレータが操作できる JSON-RPC 2.0 の stdio インターフェース）を持ちます。
2. **エージェント設定**（`~/.kiro/agents/` 配下、またはプロジェクト固有の `<project>/.kiro/agents/` の JSON）— kiro-cli に「どう振る舞うか」を指示します（システムプロンプト・有効なツール・MCP サーバ）。すべてのエージェントは `kiro-cli acp --agent <name>` として動作し、`--agent` フラグが設定を選ぶだけで、ランタイムは常に kiro-cli です。Kiro Crew は自身の `kirocrew.json` をここに生成・更新します。
3. **Kiro Crew** — **Gateway**。複数のサーフェス（CLI・チャネル・ダッシュボード・デスクトップアプリ）をこのランタイムに多重化し、ランタイムが意図的に持たない機能（スケジューリング・記憶・複数セッションなど）を追加する**単一の asyncio プロセス**です。

## Kiro CLI との差分

公式が整理する比較表です。

| 機能 | kiro-cli 単体 | Kiro Crew を使うと |
|------|-------------|-------------------|
| セッション | 端末ごとに1つ | 多数同時（チャネルスレッド・ダッシュボードスロット・cronジョブ・subagent・タスクステップ） |
| サーフェス | 端末のみ | CLI・Web ダッシュボード・Electron デスクトップ・7種のメッセージングチャネル |
| 永続化 | ディレクトリごとの文字起こし | セッション横断のメモリ（好み・プロジェクト・日次履歴・レッスン） |
| セッション間の認識 | なし | セッションがメモリを共有し、一方が学んだことを他方も見られる |
| スケジューリング | なし | Cron ジョブ（`every`／`at`／cron式）＋プロセス横断のファイルロック |
| 自律タスク | なし | TaskRunner: 仕様化・分解・実行・再試行・再計画・チェックポイント |
| 自己学習 | なし | 修正から抽出したレッスンを後続セッションに注入 |
| ツールの制御 | エージェント設定単位 | 独立した PreToolUse ゲート＋エージェントが弱めることができない2階層のガバナンス上限 |
| コンテキスト管理 | 手動の圧縮 | 設定可能な閾値での自動圧縮・バジェット意識のコンテキスト組み立て・減衰するメモリ |
| プロセスの耐障害性 | 手動再起動 | Warm pool・サーキットブレーカー・クラッシュ復旧・アイドル時クリーンアップ・孤立PID追跡 |

> **本サイトでの扱い**: 表の右列（Kiro Crew を使うと追加される機能）が本サイトの主眼です。Kiro CLI 単体の機能（モデル選択・CLI コマンド体系など）は解説しません。[q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs) を参照してください。

### なぜエージェントをオーケストレーションするのか（公式の説明）

- **無人での作業**: Cron ジョブ・TaskRunner の仕様・subagent は、人がコマンドを打たずに動きます
- **専門化**: 異なるサーフェスやジョブがそれぞれ別のエージェント設定を同時に実行できます
- **積み重ね**: 会話が共有メモリに反映され、レッスンが永続するため、後続のセッションは前のセッションが学んだ内容から始まります

### エージェントの階層

`kirocrew` 自体も他と同じ階層にある1つのエージェント設定です。これが調整役になっているのは、Gateway の既定値がこれであり、他のエージェントとのセッションを開くよう Gateway に依頼する MCP ツール（`spawn_run`・`cron_add`・`task_run`）をこれが保持しているためです。Gateway のコード自体はエージェントに依存しない設計で、調整の振る舞いはエージェント設定側にあります。

## プロバイダは acp 固定

**Kiro Crew は KiroACP 専用です**: `agent.provider` は `acp` に固定され、kiro-cli が必須要件です。`LLMProvider` という抽象インターフェースは薄い接点として残されていますが、**実在する具体プロバイダは1つだけ**（`AcpProvider`）です。

> **削除された機能**（重要な事実として明記）: **Bedrock プロバイダ**は「de-Amazoning」の過程で、設定フィールドとマルチプロバイダ振り分けファクトリごと**削除されました**。

> **⚠️ v0.6.0 で状況が変わりました**。かつて「スタンドアロンプロバイダは削除された」と記録していた仕様書 `docs/system-specs/features/claude-code-provider.md`（タイトル `# Standalone provider — removed`）は、**v0.6.0 では `docs/system-specs/modules/claude-code-provider.md` に移動し、タイトルが `# Claude Code provider — a selectable ACP harness` に変わりました**。すなわち**削除済み機能の記録ではなく、現行機能（選択可能なACPハーネス）の仕様書**です。
>
> v0.6.0 では `agent.acp_backend` によってハーネスを選択でき、`acp_backends.BASELINE_SELECTABLE_BACKENDS` は `ACP_BACKEND_KIRO`（空文字列）・`ACP_BACKEND_CLAUDE`・`ACP_BACKEND_KAS` を含みます。ただし**これは Preview 機能で、Developer Mode を有効にしないと選択できません**。したがって「`kiro-cli` が唯一のバックエンド」という記述は v0.5.0 以前の状態です。詳細と出典間の食い違いは [15_agent-backends.md](15_agent-backends.md) を参照してください。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/claude-code-provider.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## メッセージフロー

ユーザーのメッセージは hook を通り、セッションにルーティングされ、コンテキストで補強され、ACP 経由で kiro-cli に転送され、結果がストリームで返されます。

```
User → Surface（Channel/Dashboard/CLI） → Gateway
     → HookManager（auto-reply/transform/inject/deny）
     → SessionManager（get_or_create）
     → ContextBuilder（memory + skills + lessons + history を組み立て）
     → kiro-cli（ACP, JSON-RPC）→ LLM
     ← ストリーム応答
     → ConversationLog（JSONL）に追記
     → メモリ統合を非同期トリガー
```

**重要**: ツール呼び出しは単純に通過するわけではありません。kiro-cli が実行を許可される前に、**すべての呼び出しが Kiro Crew 自身の PreToolUse ゲートで評価されます**（詳細は [09_security.md](09_security.md)）。

## データの置き場所

永続状態は `~/.kiro/crew/`（`KIROCREW_HOME` で上書き可能）に置かれます。このルートは kiro-cli 自身の `~/.kiro/` の下にネストしており、Kiro ファミリーの各アプリが1つのディレクトリを共有して保護できるようになっています。**旧パス `~/.kirocrew` は自動的に移行されます**（現行では使いません）。ディレクトリ構造の詳細は [04_reference/03_directory-layout.md](../04_reference/03_directory-layout.md) を参照してください。

生成された kiro-cli 用のエージェント JSON は、ここではなく `~/.kiro/agents/`（kiro-cli がエージェント仕様を読む場所）に書かれます。

## 未確認事項

- なし（本ページの記述はすべて `docs/architecture/overview.md` と `docs/system-specs/modules/providers.md` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
- 値の一覧: [04_reference/03_directory-layout.md](../04_reference/03_directory-layout.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

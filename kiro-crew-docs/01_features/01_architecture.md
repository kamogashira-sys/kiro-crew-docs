# アーキテクチャ

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/providers.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**（既定ハーネス）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-parity.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

---

## 📑 このページの内容

- [v0.11.1 での変更](#v0111-での変更)
- [3層構造](#3層構造)
- [Kiro CLI との差分](#kiro-cli-との差分)
- [プロバイダは acp 固定](#プロバイダは-acp-固定)
- [メッセージフロー](#メッセージフロー)
- [データの置き場所](#データの置き場所)
- [未確認事項](#未確認事項)

---

## v0.11.1 での変更

### 既定のハーネスが KAS になった（v0.11.0 以降。出典間で食い違い）

v0.11.0 以降、**ハーネスの選択を保存していない新規インストールの既定は KAS** です。KAS は Kiro CLI より前に並び、各ハーネスのロゴ付きで「Kiro Agent」と表示されます。Kiro CLI を明示的に選んだ場合は、その選択が保たれます（CHANGELOG.md v0.11.0節 151-153行）。`harness-parity.md` 89行（H1）も、`agent.acp_backend` が未設定または空文字のときは選択なしとして KAS が既定で、`kiro-cli` は無条件に選べる最低ラインと記述します（テスト名は v0.9.0 の `test_kiro_is_the_default_backend` から `test_kas_is_the_default_backend` に変わっています）。同 H3 は、KAS が使えないとき選択なしは Kiro CLI に黙って落ちると記述します。

> ⚠ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **KAS が既定**: CHANGELOG.md v0.11.0節 151-153行、`harness-parity.md` 89行（H1）。いずれも v0.11.1 のファイル
> - **Kiro CLI が既定**: `architecture/overview.md` 19-20行は「`kiro-cli` is the default and baseline harness」、35-37行は「`kiro-cli` as the required baseline and default」と記述します（v0.11.1 のファイル。v0.9.0 と同文）。公式 `features/agent-backends`（Page updated 2026-10-12）24行は Kiro CLI を「Default backend」と記述します

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-parity.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。89行）
出典: CHANGELOG.md v0.11.0節 151-153行（`fe6f5be`）
**出典**: <https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-10-12）

以降の本文では「既定」と書かず、`kiro-cli` を「ベースライン（常に選べる最低ライン）」と書き分けます。

### 内蔵 KAS エンジン（Feature Preview）

- **v0.10.0**: Settings → Agent Harness の「Use the built-in KAS engine」（既定オフ）で、この版に固定した KAS エンジンをインストールして実行します。KAS のために kiro-cli をインストールしておく必要がなくなります（CHANGELOG.md v0.10.0節 299-301行）
- **v0.11.0**: デスクトップアプリは固定版の KAS エンジンを同梱し、kiro-cli の同梱をやめて、利用者自身のインストールを検出します。エンジンのスイッチは Settings → Developer → Feature Previews に移りました（CHANGELOG.md v0.11.0節 154-157行）。設定キーは `agent.kas_bundle` で、スイッチ名は「Run KAS on Kiro Crew's own engine」です（`guides/install.md` 598-604行）
- **v0.11.1**: ワンライナーと `install.sh` は、固定版の KAS エンジンを既定でダウンロードします（`--no-kas` で省略。ダウンロードに失敗してもインストールは成功します）（CHANGELOG.md v0.11.1節 45-47行、`guides/install.md` 158-168行）
- **スイッチの既定**: `guides/install.md` 594-598行は、内蔵エンジンは「shadow testing」にあり、スイッチは全プラットフォームで既定オフで、利用者が入れるまで有効にならないと記述します。「ハーネスの選択の既定が KAS」と「内蔵エンジンのスイッチの既定がオフ」は別の設定です。両者の関係（スイッチがオフのときの KAS の動き）を、この版の一次情報から断定しません。公式 `features/agent-backends` 26行は、KAS を「Kiro CLI の ACP リレー経由で Kiro のエージェントハーネスを動かす」と記述します

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。158-168・594-604行）
出典: CHANGELOG.md v0.10.0節 299-301行・v0.11.0節 154-157行・v0.11.1節 45-47行（`fe6f5be`）

### Coder ワークスペース（Session Environments。開発者向け Feature Preview。v0.11.0）

チャットは、Coder のワークスペース上でワークスペースを動かせます。エージェントのエンジンは Gateway に残り、ファイル・ターミナル・Settings のカード・composer のチップが加わります（CHANGELOG.md v0.11.0節 171-173行）。

- `providers.md` 75-82行は、Session Environments を開発者向けの Feature Preview と記述し、セッションのワークスペースツールをどこで実行するかを選ぶ機能で、Coder がワークスペースの提供元だと説明します。`agent.provider` の値は増えず、モデルも選びません。設定は Settings > Session Environments にあり、Coder の URL と名前付きプロファイルを持ち、認証情報は持ちません
- 会話・メモリ・レッスン・スキル・承認・ツールゲート・監査ログ・エンジンは Gateway に残り、ゲストが持つのはワークスペースとそのツールサーバーだけで、モデルの認証情報は持ちません（同 98-101行）
- ホストのツール許可リストがワイヤーを越えて届くのは KAS だけで、他のバックエンドはワークスペースに触れる前に `check_remote_workspace_supported` が拒否します（同 129-133行）。`kirocrew-core` のうち `LOCAL_ONLY_CORE_TOOLS` に載るツールは許可から外され、`LOCAL_ONLY_SERVERS`（Computer Use と、ジョブが Gateway 側で動く cron）はゲストに送られません（同 134-138行）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/providers.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。75-138行）
出典: CHANGELOG.md v0.11.0節 171-173行（`fe6f5be`）

## 3層構造

Kiro Crew は次の3層の上に成り立っています。

1. **ACP ハーネス** — エージェントの**ランタイム**（エージェント本体ではない）。`kiro-cli` はベースラインのハーネスです（既定は v0.11.0 以降、出典間で食い違います。[v0.11.1 での変更](#v0111-での変更)）。LLM 接続・ツール実行（bash・ファイル読み書き・grep・glob）・MCP サーバ管理・セッション永続化・コンテキスト圧縮、そして **ACP**（Agent Client Protocol。任意のオーケストレータが操作できる JSON-RPC 2.0 の stdio インターフェース）を持ちます。選択できる他のハーネスも同じトランスポートを実装し、差分は capability で区別されます（`overview.md` 19-24行）。
2. **エージェント設定**（`~/.kiro/agents/` 配下、またはプロジェクト固有の `<project>/.kiro/agents/` の JSON）— ハーネスに「どう振る舞うか」を指示します（システムプロンプト・有効なツール・MCP サーバ）。`overview.md` が「既定のバックエンド」と書く `kiro-cli` では `kiro-cli acp --agent <name>` として動作し、Kiro Crew は自身の `kirocrew.json` をここに生成・更新します。他のハーネスには、ACP プロバイダの seam を通じて同等の投影が渡されます（同 25-29行）。
3. **Kiro Crew** — **Gateway**。複数のサーフェス（CLI・チャネル・ダッシュボード・デスクトップアプリ）を、選択されたハーネスに多重化し、ランタイムが意図的に持たない機能（スケジューリング・記憶・複数セッションなど）を追加する**単一の asyncio プロセス**です。

> **以前の記述の訂正**: 本ページは以前、層 1 を「kiro-cli」、層 2 を「ランタイムは常に kiro-cli」と記載していました。これは v0.7.2 以前の `overview.md` の記述（「the runtime is always kiro-cli」）に基づくもので、**v0.9.0 以降の同ファイルは「ACP harness」を層 1 とし、kiro-cli を既定でベースラインのハーネスと記述しています（v0.11.1 の `overview.md` も同文です。既定については [v0.11.1 での変更](#v0111-での変更) の食い違いを参照）**。選択できるハーネスの一覧と Preview・Developer Mode の扱いは「[プロバイダは acp 固定](#プロバイダは-acp-固定)」と [15_agent-backends.md](15_agent-backends.md) を参照してください。

## Kiro CLI との差分

リポジトリの `overview.md` が整理する比較表です（v0.11.1 の記述に合わせています。表の内容は v0.9.0 から変わっていません）。サーフェスの行は、v0.3.0（`21584ea`）の `overview.md` では「seven messaging channels」と件数を書いていましたが、v0.7.2・v0.9.0 の同行は件数を書いていません。公式トップ（Page updated 2026-10-20）は Slack・Discord・Telegram・Teams・Webex・WeCom・WeChat を挙げ、`modules/cli.md` 339行（v0.9.0 では 222行）は WhatsApp を `kirocrew setup --whatsapp` で有効にするオプトインとして記述しています。件数は出典ごとに異なるため、本サイトは裁定せず件数を書きません。

| 機能 | kiro-cli 単体 | Kiro Crew を使うと |
|------|-------------|-------------------|
| セッション | 端末ごとに1つ | 多数同時（チャネルスレッド・ダッシュボードスロット・cronジョブ・subagent・タスクステップ） |
| サーフェス | 端末のみ | CLI・Web ダッシュボード・Electron デスクトップ・メッセージングチャネル（`overview.md` 43行: Slack・Discord・Telegram・Teams・WeChat ほか） |
| 永続化 | ディレクトリごとの文字起こし | セッション横断のメモリ（好み・プロジェクト・日次履歴・レッスン） |
| セッション間の認識 | なし | 同じ Global V1 ストアまたは同じメンバー専用 V2 ストアに紐づくセッションは学習を共有する。別のメンバーのストア同士は交わらない（`overview.md` 45行） |
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
- **積み重ね**: 会話は、そのセッションに紐づくメモリストアに反映され、レッスンが永続するため、同じストアの後続のセッションは前のセッションが学んだ内容から始まります（`overview.md` 59-61行）

### エージェントの階層

`kirocrew` 自体も他と同じ階層にある1つのエージェント設定です。これが調整役になっているのは、Gateway の既定値がこれであり、他のエージェントとのセッションを開くよう Gateway に依頼する MCP ツール（`spawn_run`・`cron_add`・`task_run`）をこれが保持しているためです。Gateway のコード自体はエージェントに依存しない設計で、調整の振る舞いはエージェント設定側にあります。

## プロバイダは acp 固定

**Kiro Crew は ACP プロバイダ専用です**: `agent.provider` は `acp` に固定されます。ハーネスの選択は別の設定 `agent.acp_backend` です。`overview.md` 35-37行は `kiro-cli` を必須のベースラインかつ既定と記述し、`harness-parity.md` 89行（v0.11.0 以降）は `kiro-cli` を無条件に選べる最低ラインとし、選択なしの既定を KAS と記述します（食い違いは [v0.11.1 での変更](#v0111-での変更)）。`LLMProvider` という抽象インターフェースは薄い接点として残されており、factory が選ぶ具体プロバイダは `AcpProvider` だけです。共有ランタイム用の `AcpSessionProvider` が 2 つ目の具象サブクラスとして存在します（`providers.md` 3-6行）。

> v0.7.2 以前の本ページは「KiroACP 専用」「実在する具体プロバイダは1つだけ」と記載していました。v0.9.0 以降の `providers.md`（v0.11.1 でも同文）は上記のとおり `AcpSessionProvider` に言及し、`agent.provider` はハーネスの選択子ではないと明記しています（5・8-9行）。

> **削除された機能**（重要な事実として明記）: **Bedrock プロバイダ**は「de-Amazoning」の過程で、設定フィールドとマルチプロバイダ振り分けファクトリごと**削除されました**。v0.11.1 の `providers.md`（66-70行。v0.9.0 も同位置）も、Bedrock やスタンドアロンのプロバイダは無く、マルチプロバイダの振り分け factory も無いと記述しています。

> **⚠️ v0.6.0 で状況が変わりました**。かつて「スタンドアロンプロバイダは削除された」と記録していた仕様書 `docs/system-specs/features/claude-code-provider.md`（タイトル `# Standalone provider — removed`）は、**v0.6.0 では `docs/system-specs/modules/claude-code-provider.md` に移動し、タイトルが `# Claude Code provider — a selectable ACP harness` に変わりました**。すなわち**削除済み機能の記録ではなく、現行機能（選択可能なACPハーネス）の仕様書**です。
>
> v0.6.0 では `agent.acp_backend` によってハーネスを選択でき、`acp_backends.BASELINE_SELECTABLE_BACKENDS` は `ACP_BACKEND_KIRO`（空文字列）・`ACP_BACKEND_CLAUDE`・`ACP_BACKEND_KAS` を含みました。したがって「`kiro-cli` が唯一のバックエンド」という記述は v0.5.0 以前の状態です。
>
> **v0.9.0 以降の選択肢**: v0.9.0 の `claude-code-provider.md` は、公開ビルドの選択可能なハーネスを kiro-cli・Claude・KAS・Codex・OpenCode・Pi・goose・DeepSeek の **8 つ**（`ACP_BACKENDS_KNOWN` の全 id）と記述しています（5-12行。v0.11.1 の同ファイルも同じ 8 つです）。v0.7.2 の同ファイルは 3 つ（kiro-cli・Claude・KAS）でした。DeepSeek は v0.8.0 で加わり、CHANGELOG は Developer Mode をオンにして選ぶと説明しています（CHANGELOG.md v0.8.0節 407-410行）。公式 `features/agent-backends`（Page updated 2026-10-12）は、この機能を **Preview** で **Developer Mode の背後**にあると記述します。
>
> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** 公開範囲について、公式 `features/agent-backends` は Preview・Developer Mode が必要と記述し、`providers.md` 12行（v0.11.1 でも同文）は「Several are selectable on a plain public build」と記述しています（v0.7.2 の同ファイルも同文）。詳細は [15_agent-backends.md](15_agent-backends.md) を参照してください。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/claude-code-provider.md>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。5-12行）
> **出典**（v0.6.0 時点の注記）: 同ファイル（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## メッセージフロー

ユーザーのメッセージは hook を通り、セッションにルーティングされ、コンテキストで補強され、ACP 経由で選択されたハーネスに転送され、結果がストリームで返されます。

```
User → Surface（Channel/Dashboard/CLI） → Gateway
     → HookManager（auto-reply/transform/inject/deny）
     → SessionManager（get_or_create）
     → ContextBuilder（memory + skills + lessons + history を組み立て）
     → ACP ハーネス（選択されたもの。ACP, JSON-RPC）→ LLM
     ← ストリーム応答
     → ConversationLog（JSONL）に追記
     → メモリ統合を非同期トリガー
```

**重要**: ツール呼び出しは単純に通過するわけではありません。ハーネスが実行を許可される前に、**すべての呼び出しが Kiro Crew 自身の PreToolUse ゲートで評価されます**（詳細は [09_security.md](09_security.md)）。

## データの置き場所

永続状態は `~/.kiro/crew/`（`KIROCREW_HOME` で上書き可能）に置かれます。このルートは kiro-cli 自身の `~/.kiro/` の下にネストしており、Kiro ファミリーの各アプリが1つのディレクトリを共有して保護できるようになっています。**旧パス `~/.kirocrew` は完全に非推奨で、自動移行されません**（現行では使いません）。旧パスが残っているのは、機密パスの拒否リスト（sensitive-path deny lists）の中だけです。ディレクトリ構造の詳細は [04_reference/03_directory-layout.md](../04_reference/03_directory-layout.md) を参照してください。

> **以前の記述の訂正**: 本ページは以前「旧パス `~/.kirocrew` は自動的に移行される」と記載していました。これは v0.3.0（`21584ea`）・v0.4.1 の `architecture/overview.md` の記述（「a legacy `~/.kirocrew` is migrated automatically」）に基づくもので、**v0.6.0 タグ以降の同ファイルは「fully deprecated and does not auto-migrate」と記述しています**。v0.7.2 タグでも同文です。変更の理由は CHANGELOG に説明がありません。
>
> **出典**（旧パスの扱い）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2。628-629行）
>
> v0.9.0 の同ファイルも同じ記述です（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。656-659行）。v0.11.1 では同じ記述が 661-662行にあります（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）。

v0.11.1 の `overview.md`（676-679行。v0.9.0 では 673-676行で同内容）のデータホーム一覧には、`members/`（crew member の固定 ID と brief）と `memory_stores/`（member／named の SQLite メモリとレッスン）が載っています。`lessons.jsonl` は「Global V1 learned corrections」と記述されています。メンバーに紐づく V2 メモリが使えないときは、Global V1 へフォールバックせず明示的に失敗します（同 355-358行）。

生成された kiro-cli 用のエージェント JSON は、ここではなく `~/.kiro/agents/`（kiro-cli がエージェント仕様を読む場所）に書かれます（`overview.md` 692-695行）。

**出典**（データホーム・生成エージェント JSON）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。355-358・661-662・676-679・692-695行）

## 未確認事項

- メッセージングチャネルの件数: 出典ごとに異なります（リポジトリ `overview.md` は件数なし、公式トップは 7 つの名前、`modules/cli.md` は WhatsApp のオプトイン）。本サイトは裁定せず件数を書きません（上記「Kiro CLI との差分」参照）
- エージェントバックエンド選択の公開範囲: 公式（Preview・Developer Mode）と `providers.md`（plain public build で選択可能）で記述が食い違っています（上記「プロバイダは acp 固定」参照）
- 既定のハーネス: v0.11.0 以降、CHANGELOG・`harness-parity.md` は KAS、`overview.md`・公式 `features/agent-backends` は Kiro CLI と記述が食い違っています（上記「[v0.11.1 での変更](#v0111-での変更)」参照）
- 内蔵 KAS エンジンのスイッチ（`agent.kas_bundle`、既定オフ）がオフのときの KAS の動作は、この版の一次情報から断定していません
- 上記以外の本ページの記述は `docs/architecture/overview.md` と `docs/system-specs/modules/providers.md`（v0.11.1）で確認済みです

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
- 値の一覧: [04_reference/03_directory-layout.md](../04_reference/03_directory-layout.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

# エージェント・スキル・Steering

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/capabilities/>（agents/agent-templates/skills/steering/hooks/prompts配下）
- agents: Page updated 2026-10-20
- agent-templates: Page updated 2026-10-12
- steering: Page updated 2026-10-12
- hooks: Page updated 2026-10-12
- skills: Page updated 2026-09-25
- prompts: Page updated 2026-09-12

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/steering-viewer.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/context-management.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.7.0での変更）: <https://kiro.dev/docs/crew/capabilities/skills/>（Page updated 2026-09-25）、<https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）、<https://kiro.dev/docs/crew/capabilities/agent-templates/>（Page updated 2026-10-12）

---

## 📑 このページの内容

- [画面名: Customize（旧 Agent Capabilities）](#画面名-customize旧-agent-capabilities)
- [エージェント設定](#エージェント設定)
- [エージェントの切り替え](#エージェントの切り替え)
- [スキル](#スキル)
- [`skill://` によるIDE/CLIとの往復](#skill-によるidecliとの往復)
- [Hooks](#hooks)
- [Steering](#steering)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## 画面名: Customize（旧 Agent Capabilities）

v0.9.0 の CHANGELOG は「Agent Capabilities is now Customize」と記載しています（CHANGELOG v0.9.0節 150-152行）。公式 agents ページ（Page updated 2026-10-20）は導線を「Customize → Agents」と記載しています。一方、公式 agent-templates・skills・steering・hooks の各ページ（Page updated 2026-09-25〜2026-10-12）は「Agent Capabilities →」のままです。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - CHANGELOG v0.9.0節と公式 agents ページ（Page updated 2026-10-20）: 画面名は **Customize**
> - 公式 agent-templates（2026-10-12）・steering（2026-10-12）・hooks（2026-10-12）・skills（2026-09-25）ページ: 画面名は **Agent Capabilities**
>
> v0.9.0 の仕様書 `steering-viewer.md` 3行は「The Steering tab under Customize」と記載しています。

本ページでは、導線を「Customize（旧 Agent Capabilities）→ …」の形で示します。

**出典**: CHANGELOG.md v0.9.0節 150-152行（`99e6253`）
**出典**: <https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）、<https://kiro.dev/docs/crew/capabilities/hooks/>（Page updated 2026-10-12）
（仕様書: `steering-viewer.md` 3行。参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## エージェント設定

エージェント設定は `~/.kiro/agents/` に置かれるファイル（`*.json`。v0.7.0 からは YAML frontmatter 付きの Markdown ファイル単体も可。「[v0.7.0での変更](#v070での変更)」参照）で、kiro-cliに「どう振る舞うか」（システムプロンプト・有効なツール・MCPサーバ）を指示します。詳細は [01_architecture.md](01_architecture.md) を参照してください。

## エージェントの切り替え

Slackでは `!agent <name>` または `!agent off` というowner専用コマンドでアクティブなエージェントを切り替えられます（全新規セッションに適用）。エージェント解決の優先順位は「スレッド上書き（`!agent`）→チャネル単位の上書き→設定された既定値→標準の `kirocrew` フォールバック」の順です。

## スキル

Markdownファイル（`~/.kiro/crew/skills/{name}/SKILL.md`）で、任意のYAML frontmatter（`name`・`description`・`always`）を持ちます。ネストしたディレクトリもサポートされます（例: `skills/utils/tiny-url/SKILL.md`）。

**ソース優先順位**（プロジェクトレベルが勝つ）: `$KIROCREW_PROJECT_DIR/skills/` → `builtin_skills/`（バンドル済み）。初回起動時に `~/.kiro/crew/skills/` へ自動コピーされます。

**プロジェクトスキル（`<project>/.kiro/skills`）**: 上記の `$KIROCREW_PROJECT_DIR/skills/`（`~/.kiro/crew/skills/` にコピーされる同期元）とは別のソースです。そのプロジェクトに結び付いたセッションで、コピーせずにその場で discovery され、ソースは `kiro-workspace` と表示されます。読み込むにはディレクトリ単位の明示的な許可（consent）が必要で、`skills.project_skills_enabled`（既定 true）を false にすると、許可の有無にかかわらず何も読み込みません（`memory-skills-hooks.md` v0.9.0 3571-3575行・3620-3622行。v0.7.2 では 2902-2952行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### 読み込み方式

公式 skills ページ（Page updated 2026-09-25）は次の3モードを示しています。

| モード | 動作 |
|-------|------|
| **Always-on** | `always: true` のスキルは、対象となるセッションごとに全文が注入されます |
| **On-demand**（既定） | エージェントは使用頻度でランク付けしたインデックス（各スキルの名前・説明・パス）を受け取り、直接読むか `skill_search` で他のスキルを探します |
| **Triggered** | `skills.max_triggered` が0より大きいとき、メッセージに一致したスキルが注入されます |

`skills.max_triggered` の既定は `0` で、メッセージごとのトリガー注入は無効ですが、on-demand の読み込みと `skill_search` は無効になりません。正の整数を設定すると、メッセージごとに最大その数のトリガー一致スキルを注入します。frontmatter の `triggers` は `max_triggered` が正のときだけ意味を持ちます（公式 skills ページ）。v0.6.0 時点の公式ページは On-demand スキルを「loaded only when your message matches the skill's trigger keywords」と説明していましたが、v0.7.2 時点以降の記述は上表に改められています（公式 skills ページは Page updated 2026-09-25 のまま、v0.9.0 の取得時点でも同じ記述です）。

> v0.7.0 の CHANGELOG 419-422行は「`skills.max_triggered` defaults to 0 … (set a positive integer to restore the old behaviour)」を v0.7.0 の変更として記載しています。一方、v0.6.0 の仕様書（`memory-skills-hooks.md` 1373行、`config.md` 1019行）も既定を0と記載しています。

**Discovery（`skills.lazy_load`、既定 true）**: **既定値が変わりました（v0.6.0以前は false）**。v0.9.0 の仕様書は、on-demand セットの提示方法を次のように記載します（`config.md` 3813-3821行、`memory-skills-hooks.md` 3912-3916行）。

- **true（既定）**: 使用頻度でランク付けした上限付きのインデックス（各スキルのパスと、省いたファミリーを示す1行）
- **false**: より短いエントリ（最大8件の名前と短い用途、短いキーワードで `skill_search` を使う案内）。8件のうち最大6件はユーザー自身のスキル、残りは使用頻度順で上位の残りのスキルです（`config.md` 3817-3820行）
- どちらの値でも、Crew が背景情報に充てる基準値（固定 33,000文字）は拡大しません（`memory-skills-hooks.md` 6135行）
- `always: true` の必須の本文は、合計で `PINNED_SKILL_BODIES_CAP`（99,000 UTF-8バイト）を共有します。超過したときは黙って切り捨てず、`SkillContextCapacityError` になります（`memory-skills-hooks.md` 3937-3940行）

v0.6.0 の仕様書では、`skills.lazy_load` は「OFFなら全件をランク付けなしで当時の基準値165,000文字の中にダンプ、ONなら常時オンのスキルを全文注入＋使用頻度で上位K件」という切り替えでした（`memory-skills-hooks.md` v0.6.0 989-990行）。

`skills.lazy_load` の既定値の変更と上記の挙動: 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません。v0.9.0 タグの仕様書でも同じ内容を確認しています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - `config.md` 3813-3821行: 既定（`lazy_load=true`）のエントリは使用頻度順のインデックスで、最大8件の名前を並べる短いエントリは `lazy_load=false` のとき。`memory-skills-hooks.md` 3912-3916行も、既定を「the usage-ranked index with a family hint」、false を「a shorter search pointer」と記載
> - `memory-skills-hooks.md` 6197-6200行: 「The default discovery entry lists up to eight names and short purposes」と記載し、既定のエントリが最大8件の名前を並べるとしている
>
> この食い違いは v0.7.2 の仕様書にも同じ形でありました（v0.7.2 では `memory-skills-hooks.md` 4637-4638行）。v0.9.0 でも継続しています。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### 用途の区別

「LLMツールの仕組み」として、MCPツール（`kirocrew-cron`・`kirocrew-core`のようなネイティブツール）が**LLM向けの操作すべてに優先されます**。スキルは**オンデマンドの知識のためだけ**にあり、CLIコマンドのラッパーとしては使いません（MCPツールを使う）。

## `skill://` によるIDE/CLIとの往復

エージェント設定は `skill://` というグロブパターンでスキルを参照でき、これによりCrew・Kiro IDE・Kiro CLI 間でスキルの往復ができます。この仕組みは `annotate_skills_with_agents` がエージェントJSONを解析し、`skill://` グロブを事前展開して各スキルと照合する形で実装されています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> エージェントが独自の `skill://` マッピングを持つときのスキル本文の扱いについて、v0.9.0 の仕様書2ファイルの記述が異なります。
>
> - `memory-skills-hooks.md` 3927-3928行: 「A `skill://` mapping restricts availability, not eager body delivery」（マッピングは利用できる範囲を絞るもので、本文を先に配るものではない）
> - `config.md` 3820-3821行: 「An agent with its own `skill://` mapping gets neither -- those skills arrive as complete instructions」（どちらのエントリも受け取らず、スキルは完全な指示として届く）
>
> この食い違いは v0.7.2 の仕様書にも同じ形でありました（v0.7.2 では `memory-skills-hooks.md` 3189-3190行、`config.md` 2730-2731行）。v0.9.0 でも継続しています。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## Hooks

Kiro Crew には、本ページの出典上、2種類のフック設定が登場します。両者の関係（どちらが他方を置き換えるか等）は一次情報で確認できません。

- **`config.json` の `hooks` 節**: `hooks.py` がconfig駆動のフック機構を提供します（`auto_approve_tools`・`auto_deny_tools`・`auto_replies`・`transforms`・`context_rules`。PreToolUseゲート等）。deny が approve に優先します（`memory-skills-hooks.md` 5400-5406行）。詳細はセキュリティ節（[09_security.md](09_security.md)）で扱います
- **Hooks ページで管理するフック**（下記）: 公式 hooks ページ（Page updated 2026-10-12）が記載する、トリガー・マッチャー・アクションを持つフックです

公式 hooks ページは Page updated 2026-10-12 で全面的に書き換えられています（v0.7.2 時点の公式ページは `~/.kiro/crew/hooks/`（または `.kiro/hooks/`）の JSON ファイルと `SessionStart`・`PostFileSave` などのイベント名を記載していました。v0.9.0 の取得時点のページと v0.9.0 の仕様書は、保存先を `~/.kiro/crew/hooks.json` と記載しており、一致しています）。

### 管理と構造

- **ダッシュボード**: Customize（旧 Agent Capabilities）→ Hooks で、フックの表示・作成・編集・削除ができます。各フックはトリガー・アクション・任意のマッチャーを示します
- **保存先**: `~/.kiro/crew/hooks.json`。プロバイダ所有のフックはダッシュボードで読み取り専用で、プロバイダの設定に残ります（公式 hooks ページ。仕様書 `memory-skills-hooks.md` 5551行も `hooks.json` と記載）
- **構造**: **トリガー**（いつ実行するか）、**マッチャー**（任意。どのイベントで実行するかを絞る）、**アクション**（シェルコマンド1つ、または選んだ Skills をコンテキストに読み込む）の3つです

### 自動で発火する5つのイベント

| トリガー | 発火するとき |
|---------|-------------|
| `AgentSpawn` | 新しいエージェントセッションが始まるとき |
| `UserPromptSubmit` | エージェントにメッセージが送られるとき |
| `PreToolUse` | ツールが始まる前 |
| `PostToolUse` | ツールが終わった後 |
| `Stop` | エージェントのターンが終わるとき |

**マッチャー**: `PreToolUse`・`PostToolUse` はツール名に対するグロブ（完全一致・`prefix*`・`*suffix`・`*text*`・`*`）です。`AgentSpawn`・`UserPromptSubmit`・`Stop` はメッセージまたは最終返信のテキストに対して、グロブ、大文字小文字を区別しない正規表現、パイプ区切りの contains のいずれかを使います。

### テスト専用の Kiro Agent の6イベント

Hooks の編集画面は、Kiro Agent（KAS バックエンド）由来の6つのイベント名も保存できます。公式 hooks ページは、このうちどれも Crew 0.8 では自動で発火せず、**Test** がこれらのフックを実行する唯一の方法で、各フックは無効の状態で保存されると記載しています。マッチャーは取りません。

| トリガー | 想定される場面 | 行の状態 |
|---------|---------------|---------|
| `PreTaskExecution` | spec タスクが始まる前 | `not fired yet` |
| `PostTaskExecution` | spec タスクが完了した後 | `not fired yet` |
| `FileCreated` | Kiro Agent がファイルを作った後 | `never fires` |
| `FileEdited` | Kiro Agent がファイルを保存した後 | `never fires` |
| `FileDeleted` | Kiro Agent がファイルを削除した後 | `never fires` |
| `UserTriggered` | フックを手動で実行したとき | `never fires` |

仕様書も、`ALLOWED_HOOK_EVENTS` は11件（自動で発火する5件と、`hooks.HOOK_EVENTS_KAS_ONLY` の6件）で、後者の6件は「registrable but fired by nothing」（登録できるがどこからも発火されない）と記載しています（`memory-skills-hooks.md` 5643-5645行。この記述は別イベント `SessionLaneChanged` の節の中にあり、その節自体は未実装の仕様を扱うと断っていますが、3つのイベント集合の現状は同じ箇所に書かれています）。CHANGELOG v0.8.0節 411-413行は、イベントピッカーが11個の Kiro Agent トリガーのフックを書けるようにし、Test でいつでも実行できると記載しています（公式 hooks ページの「自動5件＋テスト専用6件」と合わせると11件です）。公式ページの「None fires automatically in Crew 0.8」は版が「0.8」のまま、Page updated 2026-10-12 のページに残っています。v0.9.0 の仕様書にも矛盾する記述はありません。

### アクション

**コマンドアクション**: シェルコマンドを1つ実行します。環境変数 `KIROCREW_HOOK_EVENT` と `KIROCREW_HOOK_CONTEXT` が渡され、標準入力にイベントの JSON が入ります。シェルは POSIX では `/bin/sh`、Windows では `%ComSpec%` で、フックはプラットフォーム間で移植できないため、必要ならプラットフォームごとにコマンドを書きます（`memory-skills-hooks.md` 5548-5560行）。

フックには Gateway の環境がそのまま渡りません。渡るのは `PATH`・ホームと一時ディレクトリ・ロケール・TLS の信頼設定・`KIROCREW_HOME` だけです。`AWS_PROFILE` や `VIRTUAL_ENV` のような値は、コマンドの中で設定するか、絶対パスを使います（公式 hooks ページ。仕様書 `memory-skills-hooks.md` 5585-5593行は、許可リスト `_HOOK_BASE_ENV_KEYS` に含まれない環境変数を持ち込めない旨を記載しています）。

終了コードの意味は次のとおりです。

- `0`: `PreToolUse` を許可します。`AgentSpawn` と `UserPromptSubmit` では、標準出力がモデルのコンテキストに入ります
- `2`: `PreToolUse` の呼び出しを拒否し、標準エラー出力をモデルに返します
- それ以外の終了、タイムアウト、クラッシュ: `PreToolUse` をブロックします（fail closed）
- ほかのイベントでは、0 以外の終了は警告を記録し、ターンは続きます

`Stop` のフックは、もう1ターンを要求できます。終了コード `0` で、標準出力が `{"decision": "block", "reason": "<text>"}` の形のとき、理由を注入してエージェントを続行させます。それ以外の標準出力は無視されます。この JSON の形は、公式 hooks ページの HTML で確認したものです（`.md` companion では該当箇所が空文字になっています）。

`PreToolUse` のフックが止められるのは、Gateway が承認を握っているときだけです。Kiro CLI が既に承認した呼び出しは、フックがイベントを報告するだけで止められません。

**Skills アクション**: コマンドを空にして Skills を選ぶと、サブプロセスを起動せずに選んだ Skills をコンテキストに読み込みます。`AgentSpawn` または `UserPromptSubmit` でだけ使えます。ほかのトリガーとアクションの組み合わせは、効果のない状態で保存されず、拒否されます。

### ダッシュボードからの作成

1. Customize（旧 Agent Capabilities）→ Hooks を開く
2. **New Hook** を選び、名前を付けてイベントを選ぶ
3. ツールイベントにはグロブのマッチャー、メッセージイベントにはグロブ・正規表現・contains を選ぶ
4. コマンドを1つ追加する。`AgentSpawn` と `UserPromptSubmit` では、空にして Skills を選ぶこともできる
5. 保存する。自動イベントのフックは保存時に有効になり、Kiro Agent の6イベントのフックは無効で保存される
6. **Test** で保存したフックを実行し、終了コード・標準出力・標準エラー出力を確認する

新しい自動イベントのフックは、テストする前に発火することがあります。コマンドがまだライブの呼び出しをゲートする準備ができていないときは、先に `PreToolUse` のフックを無効にします。Gateway の再起動は不要です（公式 hooks ページ）。

### Preview・Developer Mode の扱い

CHANGELOG v0.8.0節 405行の見出しは「More backends, and hooks you can author (Preview)」です。同節で「with Developer Mode on」という条件が付くのは DeepSeek Harness の項目（406-409行）だけで、フックの項目（410-413行）に条件の記載はありません。公式 hooks ページにも Preview・Developer Mode の語はありません。**フックの編集画面が Preview 扱いかどうかは、一次情報で確認できません。**

**出典**: <https://kiro.dev/docs/crew/capabilities/hooks/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.8.0節 405-413行（`99e6253`）。

## Steering

公式 steering ページ（Page updated 2026-10-12）は、Steering ファイルを、ワークスペースから起動したすべてのセッションに適用される Markdown のルールと説明しています。

- **置き場所**: プロジェクトの `.kiro/steering/*.md`。Gateway がそのワークスペースから起動したとき（またはアクティブなプロジェクトをそのディレクトリにしたとき）、すべてのセッションがこれらのファイルの内容を継承し、エージェントは永続的な指示として受け取ります。変更は次のセッションから有効で、再起動は不要です
- **ダッシュボード**: Customize（旧 Agent Capabilities）→ Steering で、Steering ファイルの表示・編集・追加ができます。一覧は各ファイルの inclusion モードも表示し、管理するファイルではそのモードを設定できます
- **inclusion モード**: 仕様書 `steering-viewer.md` 16-24行は、`always`・`fileMatch`・`manual`・`auto` の4種を記載し、宣言が無いか認識できない値のときは `always` として報告すると記載しています

### フォルダの Additional steering（v0.8.0 で追加）

フォルダの設定で **Additional steering** のディレクトリを追加できます（公式 steering ページ。CHANGELOG v0.8.0節 249-253行）。

- 各エントリは、存在する絶対パスか、`~` で始まるパスです。1フォルダに最大16件まで追加できます。ネットワークパス、機微なパス、存在しないフォルダ、実体が重複するパスは拒否されます
- チャットは、自分のフォルダと祖先フォルダの一覧を引き継ぎます。これらは、既存のプロジェクト・エージェント・crewmate の Steering に、どのエージェントバックエンドでも加わります
- チャットを移動すると次のターンからフォルダの Steering が変わり、実行中のターンは開始時のコンテキストを保ちます
- 追加できるのはダッシュボードの owner だけです

仕様書 `config.md` 352-408行は、公式ページにない次の詳細を記載しています。

- 読み込まれるのは各ディレクトリの `**/*.md` のうち inclusion が `always` または未指定のものです。`manual`・`auto`・`fileMatch` のファイルは読み込まれません
- 1エントリは4096文字までです。検証に失敗すると 400 `steering_dirs_invalid` になります
- アプリまたは crew-member の権限による追加は 403 `steering_dirs_forbidden` で拒否されます。空のリストへの更新（クリア）はすべての呼び出し元に許可されます
- 解決は祖先から累積します（根の祖先が先、子孫が後）。実体が同じパスは、最初の1件だけを残します

仕様書 `steering-viewer.md` 91行は、Steering タブの作成・更新・削除について、incognito・temporary・ゲストのセッションからは読み取りのみで、さらにダッシュボードの owner を要求し、owner でない呼び出しは 403 `owner_only` になると記載しています。読み取りは owner に限られません。

**出典**: <https://kiro.dev/docs/crew/capabilities/steering/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/steering-viewer.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.8.0節 249-253行（`99e6253`）。

## v0.9.0での変更

v0.9.0 の CHANGELOG（v0.9.0節）で、本ページの範囲に関わる変更です。v0.8.0・v0.9.0 の CHANGELOG に「Before you upgrade」節はありません。

- **画面名の改称**: Agent Capabilities は Customize になりました（CHANGELOG v0.9.0節 150-152行）。公式ページの表記の違いは「[画面名: Customize（旧 Agent Capabilities）](#画面名-customize旧-agent-capabilities)」を参照してください
- **信頼できないチェックアウトの agent spec のフック**: 信頼できないチェックアウトの agent spec にあるフックは、ターンループに届かなくなりました（CHANGELOG v0.9.0節 176-178行の「Security and access」の段落）
- **crewmate の呼称**: v0.8.0 の CHANGELOG は Preview を「the Crew Members preview」と呼び（CHANGELOG v0.8.0節 338行）、v0.9.0 時点の公式 agents ページ（Page updated 2026-10-20）は同じ Preview を Settings → Developer → Feature Previews → **Crewmates** と呼んでいます。本サイトは裁定せず、両方の呼称を示します

公式 agents ページ（Page updated 2026-10-20）は、Preview の Crewmates 機能で、各 crewmate が表示名・プライベートメモリ・ワークスペース・agent template・既定モデル・任意のトリガーを持つと記載しています。**Preview の機能です**（Settings → Developer → Feature Previews → Crewmates を有効にします）。crewmate のメモリは [04_memory-and-learning.md](04_memory-and-learning.md) の「Crewmate のプライベートメモリ（Preview）」を参照してください。

### スキル（仕様書だけで確認した項目）

次の3件は v0.9.0 タグの仕様書で確認したもので、v0.8.0 タグ・v0.7.2 タグの仕様書には記載がありません。CHANGELOG（v0.8.0節・v0.9.0節）と公式ドキュメントは説明していません。

- **`skills.lazy_load` の書き換え（アップグレード時に1回）**: 0.6.x 以前の Kiro Crew は `skills.lazy_load: false` を `config.json` に書き出しており、当時の `false` は全件の一覧を意味していました。v0.7.0 以降は `false` が短いエントリを選びます。仕様書 `config.md` 797-862行は、`meta.lastTouchedVersion` が 0.6.x 以前などの条件を満たす設定からこの値を、アップグレード時に1回だけ削除し（既定の `true` が適用されます）、WARNING を1行出すと記載しています。条件を満たさない設定と、その後に `kirocrew config set skills.lazy_load false` で選んだ値はそのまま残ります。**この項目は仕様書だけに記載があり、公式ドキュメントと CHANGELOG には記載がありません**
- **トリガーしたスキルの本文は、セッション内で最初に一致したときだけ**: `skills.max_triggered` を正の整数にしてトリガー注入を有効にしたとき、仕様書は、一致したスキルの本文がプロバイダセッションで最初に一致したときだけ全文で入り、同じセッションでの2回目以降の一致は 1 行のポインタ（`[Relevant skills for this message]`）に切り替わると記載しています。新しいセッション、compaction 後の最初のターン、エージェントの変更で記録がリセットされます。確認済みのプロジェクトスキルは一致のたびに本文が入ります。記録はセッション512件、1セッションあたり64スキルの LRU で上限が決まっています（`context-management.md` 243-256行・270-295行）。`skills.max_triggered` の既定は 0 なので、既定ではこの挙動は働きません。**この項目は仕様書だけに記載があり、公式ドキュメントと CHANGELOG には記載がありません**。v0.7.2 と v0.8.0 の同ファイルは、一致したスキルの本文を既定で全文注入すると記載していました（v0.8.0 の `context-management.md` 217-218行）
- **`skill_search` の読み取りの上限**: `action="read"` の1回の読み取りは最大 `SKILL_READ_CAPACITY`（99,000 UTF-8バイト）です。本文がこれに収まらないとき、`offset`・`limit` を渡さない読み取りは拒否され、本文のサイズ・上限・ページングのパラメータが示されます。`offset`・`limit` を渡すと行単位でページングされ、次の `offset` がヘッダに入ります（`memory-skills-hooks.md` 4047-4066行）。**この項目は仕様書だけに記載があります**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/context-management.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

出典: CHANGELOG.md v0.9.0節 150-152行・176-178行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）

## v0.8.0での変更

v0.8.0 の CHANGELOG（v0.8.0節）、公式 agents／agent-templates ページ、v0.9.0 タグの仕様書で確認できる変更です。（スキルのうち、v0.8.0 タグの仕様書に記載がなく v0.9.0 タグで初めて確認できた3件は「[v0.9.0での変更](#v090での変更)」の「スキル（仕様書だけで確認した項目）」に置いています）

### エージェントテンプレートと crewmate

- **Agent templates タブ**: Customize（旧 Agent Capabilities）→ Agent templates で、インストール済みのテンプレートが origin 別に並びます。自分のテンプレートは作成・複製・編集・削除でき、package と built-in のテンプレートは読み取り専用です（編集可能なコピーは **Duplicate** で作ります）（公式 agent-templates ページ。CHANGELOG v0.8.0節 294-300行）
- **テンプレートからの開始**: **Chat with this template** は共有の既定メモリを使う1回限りのセッションです。**Enroll as crewmate** は専用メモリを持つ名前付きの crewmate を作ります。登録済みのテンプレートには **Already enrolled as a crewmate** と表示されます
- **Schedule ページ**: Agent の一覧は **Crewmates** と **Agent templates** に分かれます。crewmate のジョブはその crewmate のワークスペースとメモリで動きます。Agent template のジョブは既定 crewmate のワークスペースとメモリで動き、crewmate を新たに作りません
- **crewmate の表示名**: Customize（旧 Agent Capabilities）→ Agents の crew フォームの **Display name** は、ダッシュボード全体での表示名です。id は引き続きスケジュールと CLI を決めます（CHANGELOG v0.8.0節 301-303行。公式 agents ページ）
- **同名スキルの区別**: 2つのパッケージが同じ名前のスキルを持つとき、エージェントエディタのスキルピッカーとチップが、それぞれの場所を表示します。スキルカタログの読み込みに失敗したときは、理由を表示します（CHANGELOG v0.8.0節 304-306行）
- **継承の既定**: Kiro CLI の設定で継承する既定値をオフにした crewmate は、グローバルの Steering を受け取らなくなりました（CHANGELOG v0.8.0節 570-571行）

crewmate は Preview の機能です（Settings → Developer → Feature Previews → Crewmates。CHANGELOG v0.8.0節は同じ Preview を「Crew Members preview」と呼んでいます）。テンプレートの継承（Follow the parent template）は Kiro バックエンドのみです（「[v0.7.0での変更](#v070での変更)」参照）。

### スキル

- **always-on スキルが収まらない場合**: 信頼されたプロジェクトの `always: true` スキルは、`PINNED_SKILL_BODIES_CAP` の共有枠に数えず、別の枠で扱います。収まらないスキル、または読めないスキルは、セッション全体を失敗させずにスキップします。確認済みのプロジェクトスキル本文の別枠は 24,750文字です（`memory-skills-hooks.md` 3941-3946行・6195-6196行）。CHANGELOG v0.8.0節は、プロジェクトの always-on スキルが収まらないとき、または SKILL.md が UTF-8 でないときは、警告を出してスキップすると記載しています（669-670行）
- **ファイルの文字コード**: BOM 付き（UTF-8）の `config.json`・`mcp.json`・SKILL.md は、ほかのファイルと同じように読まれます（CHANGELOG v0.8.0節 686-688行）。仕様書は、UTF-16 の SKILL.md と、本文が `<!doctype` または `<html` で始まる SKILL.md はスキルとして扱わず、警告を出してその行だけを外すと記載しています（`memory-skills-hooks.md` 3722-3745行）
- **スキルの承認と再インストール**: Skills の承認待ちは、承認が拒否された理由を表示し、クリックの前に失敗する候補に印を付けます（CHANGELOG v0.8.0節 561-563行）。スキルの再インストールで新しいコピーを書けなかったときは、手元のコピーを保ちます（CHANGELOG v0.8.0節 568行）

### フック

- **KAS バックエンドでの agent spec のフック**: agent spec のフックと権限が、KAS バックエンドで有効になりました（CHANGELOG v0.8.0節 558-559行）
- **Hooks ページ**: Kiro Agent の11個のトリガーでフックを書けるようになりました（CHANGELOG v0.8.0節 411-413行）。詳細は上記「[Hooks](#hooks)」を参照してください

出典: CHANGELOG.md v0.8.0節 294-306行・558-563行・568行・570-571行・669-670行・686-688行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/capabilities/agent-templates/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/context-management.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.7.0での変更

v0.7.0 の CHANGELOG と、公式 skills／agents／agent-templates ページ（v0.9.0 の取得時点の Page updated は skills 2026-09-25・agents 2026-10-20・agent-templates 2026-10-12）で確認できる変更です。スキルの読み込みモードの説明と `skills.lazy_load` の既定値は「[読み込み方式](#読み込み方式)」を参照してください。

- **エージェントを Markdown 1ファイルで書ける**: `~/.kiro/agents` に YAML frontmatter 付きの Markdown で書いたエージェントは、対になる JSON なしで一覧に表示され、使えます。エージェントピッカーはテンプレートを crew member と並べて表示します（member としては登録しません）。エージェントは、tag manager で設定した権限のもとで `chat_tag` ツールを使い、セッションをボードのタグ間で移動できます（CHANGELOG 410-414行）
- **親テンプレートの継承（Kiro バックエンド）**: Customize（旧 Agent Capabilities）→ Agents → エージェントの **Capabilities** ペインで **Follow the parent template** をオンにし、能力ごとに次を選びます。親テンプレートが変わると、取り込む差分を確認してから適用します（公式 agent-templates ページ「Follow a parent template」／CHANGELOG 239-243行）
  - **Inherited**: 親の現在値を使い、親の変更に自動で追従します
  - **Override**: 親の変更にかかわらず、エージェント自身の値を保ちます
  - **Removed**: その能力をこのエージェントでは抑止します（後の親の変更も含みます）。選択を変えるまで続きます
- **テンプレートの編集とフォーク**: エージェントの **Agent Template** ペインで、親テンプレートに従っていないエージェントのモデルとスキルをその場で編集できます。最初の編集で共有テンプレートを変えずに私的コピーをフォークし、**Customized** マーカー、テンプレートと異なるフィールド数のライブ表示、保存内容のプレビュー、**Save as new template** を表示します（公式 agent-templates ページ／CHANGELOG 244-248行）。フォークしたコピーには親テンプレートの変更が流れ込みません（公式 agent-templates ページ「Fork a private copy」）
- **リポジトリからスキルをインポート**: **Settings → Skills → Discover** で、公開 GitHub リポジトリの1スキルまたは全スキルを取り込めます。アドレスは `owner/repo`・`owner/repo@ref`・`owner/repo:path`・`owner/repo@ref:path` の形式で、インストール時に解決したコミットに固定されます。インポートはスナップショットで、購読ではありません。新しいリビジョンは同じアドレスを再インポートして確認・適用します。エージェントは `skill_fetch` でレジストリのスキルを確認できますが、インストールはダッシュボードでの操作です（公式 skills ページ「Import from a repository」／CHANGELOG 422-423行）

出典: CHANGELOG.md v0.7.0節 239-248行・410-414行・419-425行（`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/capabilities/skills/>（Page updated 2026-09-25）、<https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）、<https://kiro.dev/docs/crew/capabilities/agent-templates/>（Page updated 2026-10-12）

## 未確認事項

- 本ページの記述は公式 `capabilities/` 配下と `memory-skills-hooks.md`・`config.md` で確認済み。ただし v0.9.0 の仕様書2ファイルの間で、次の2点の記述が食い違っており、本サイトは裁定していません（どちらも v0.7.2 から継続）
  - `skills.lazy_load` の既定（true）のときに提示されるエントリの形（「[読み込み方式](#読み込み方式)」参照）
  - 独自の `skill://` マッピングを持つエージェントでのスキル本文の扱い（「[`skill://` によるIDE/CLIとの往復](#skill-によるidecliとの往復)」参照）
- 画面名は、CHANGELOG v0.9.0節・公式 agents ページ（Customize）と、公式の他の capabilities ページ（Agent Capabilities）で表記が異なります（「[画面名: Customize（旧 Agent Capabilities）](#画面名-customize旧-agent-capabilities)」参照）。本サイトは裁定していません
- Hooks の編集画面が Preview 扱いかどうかは、一次情報で確認できません（「[Preview・Developer Mode の扱い](#previewdeveloper-mode-の扱い)」参照）
- 公式 hooks ページの「None fires automatically in Crew 0.8」は版が「0.8」のままの記述です。v0.9.0 の仕様書に矛盾する記述はありませんが、Page updated 2026-10-12 より後の公式ページ側の更新は確認できません
- `config.json` の `hooks` 節と `hooks.json` のフックの関係は、一次情報で確認できません
- 仕様書だけに記載があり、公式ドキュメントと CHANGELOG に記載がない項目: `skills.lazy_load` の書き換え、トリガーしたスキルの本文の重複排除、`skill_search` の1回の読み取りの上限、フォルダの Additional steering の詳細（4096文字・403/400 のコード）
- Memory V2・`src/` 由来の値（builtin App 数など）は `src/` の解析が必要なため、本ページでは扱いません

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/capabilities/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
- アーキテクチャ: [01_architecture.md](01_architecture.md)
- セキュリティ: [09_security.md](09_security.md)
- メモリと学習: [04_memory-and-learning.md](04_memory-and-learning.md)

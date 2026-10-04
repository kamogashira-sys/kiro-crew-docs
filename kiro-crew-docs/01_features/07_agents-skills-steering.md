# エージェント・スキル・Steering

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/capabilities/>（agents/agent-templates/skills/steering/hooks/prompts配下、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（v0.7.0での変更・`skills.lazy_load` の既定値・プロジェクトスキル）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.7.0での変更）: <https://kiro.dev/docs/crew/capabilities/skills/>、<https://kiro.dev/docs/crew/capabilities/agents/>、<https://kiro.dev/docs/crew/capabilities/agent-templates/>（いずれも Page updated 2026-09-25）

---

## 📑 このページの内容

- [エージェント設定](#エージェント設定)
- [エージェントの切り替え](#エージェントの切り替え)
- [スキル](#スキル)
- [`skill://` によるIDE/CLIとの往復](#skill-によるidecliとの往復)
- [Hooks](#hooks)
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## エージェント設定

エージェント設定は `~/.kiro/agents/` に置かれるファイル（`*.json`。v0.7.0 からは YAML frontmatter 付きの Markdown ファイル単体も可。「[v0.7.0での変更](#v070での変更)」参照）で、kiro-cliに「どう振る舞うか」（システムプロンプト・有効なツール・MCPサーバ）を指示します。詳細は [01_architecture.md](01_architecture.md) を参照してください。

## エージェントの切り替え

Slackでは `!agent <name>` または `!agent off` というowner専用コマンドでアクティブなエージェントを切り替えられます（全新規セッションに適用）。エージェント解決の優先順位は「スレッド上書き（`!agent`）→チャネル単位の上書き→設定された既定値→標準の `kirocrew` フォールバック」の順です。

## スキル

Markdownファイル（`~/.kiro/crew/skills/{name}/SKILL.md`）で、任意のYAML frontmatter（`name`・`description`・`always`）を持ちます。ネストしたディレクトリもサポートされます（例: `skills/utils/tiny-url/SKILL.md`）。

**ソース優先順位**（プロジェクトレベルが勝つ）: `$KIROCREW_PROJECT_DIR/skills/` → `builtin_skills/`（バンドル済み）。初回起動時に `~/.kiro/crew/skills/` へ自動コピーされます。

**プロジェクトスキル（`<project>/.kiro/skills`）**: 上記の `$KIROCREW_PROJECT_DIR/skills/`（`~/.kiro/crew/skills/` にコピーされる同期元）とは別のソースです。そのプロジェクトに結び付いたセッションで、コピーせずにその場で discovery され、ソースは `kiro-workspace` と表示されます。読み込むにはディレクトリ単位の明示的な許可（consent）が必要で、`skills.project_skills_enabled`（既定 true）を false にすると、許可の有無にかかわらず何も読み込みません（`memory-skills-hooks.md` v0.7.2 2902-2952行。v0.6.0 の同ファイルにも記載あり）。

### 読み込み方式

公式 skills ページ（Page updated 2026-09-25）は次の3モードを示しています。

| モード | 動作 |
|-------|------|
| **Always-on** | `always: true` のスキルは、対象となるセッションごとに全文が注入されます |
| **On-demand**（既定） | エージェントは使用頻度でランク付けしたインデックス（各スキルの名前・説明・パス）を受け取り、直接読むか `skill_search` で他のスキルを探します |
| **Triggered** | `skills.max_triggered` が0より大きいとき、メッセージに一致したスキルが注入されます |

`skills.max_triggered` の既定は `0` で、メッセージごとのトリガー注入は無効ですが、on-demand の読み込みと `skill_search` は無効になりません。正の整数を設定すると、メッセージごとに最大その数のトリガー一致スキルを注入します。frontmatter の `triggers` は `max_triggered` が正のときだけ意味を持ちます（公式 skills ページ）。v0.6.0 時点の公式ページは On-demand スキルを「loaded only when your message matches the skill's trigger keywords」と説明していましたが、v0.7.2 時点の記述は上表に改められています。

> v0.7.0 の CHANGELOG 419-422行は「`skills.max_triggered` defaults to 0 … (set a positive integer to restore the old behaviour)」を v0.7.0 の変更として記載しています。一方、v0.6.0 の仕様書（`memory-skills-hooks.md` 1373行、`config.md` 1019行）も既定を0と記載しています。

**Discovery（`skills.lazy_load`、既定 true）**: **既定値が変わりました（v0.6.0以前は false）**。v0.7.2 の仕様書は、on-demand セットの提示方法を次のように記載します（`config.md` 1950行・2727-2730行、`memory-skills-hooks.md` 3187-3189行）。

- **true（既定）**: 使用頻度でランク付けした上限付きのインデックス（各スキルのパスと、省いたファミリーを示す1行）
- **false**: より短いエントリ（使用頻度順で最大8件の名前と短い用途、短いキーワードで `skill_search` を使う案内）
- どちらの値でも、Crew が背景情報に充てる基準値（固定 33,000文字）は拡大しません（`memory-skills-hooks.md` 4582行）
- `always: true` の必須の本文は、合計で `PINNED_SKILL_BODIES_CAP`（99,000 UTF-8バイト）を共有します。超過したときは黙って切り捨てず、`SkillContextCapacityError` になります（`memory-skills-hooks.md` 3199-3201行）

v0.6.0 の仕様書では、`skills.lazy_load` は「OFFなら全件をランク付けなしで当時の基準値165,000文字の中にダンプ、ONなら常時オンのスキルを全文注入＋使用頻度で上位K件」という切り替えでした（`memory-skills-hooks.md` v0.6.0 989-990行）。

`skills.lazy_load` の既定値の変更と上記の挙動: 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - `config.md` 2727-2730行: 既定（`lazy_load=true`）のエントリは使用頻度順のインデックスで、最大8件の名前を並べる短いエントリは `lazy_load=false` のとき。`memory-skills-hooks.md` 3187-3189行も、既定を「the usage-ranked index with a family hint」、false を「a shorter search pointer」と記載
> - `memory-skills-hooks.md` 4637-4638行: 「The default discovery entry lists up to eight usage-ranked names and short purposes and requests short keywords」（既定のエントリが最大8件の名前を並べる）
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

### 用途の区別

「LLMツールの仕組み」として、MCPツール（`kirocrew-cron`・`kirocrew-core`のようなネイティブツール）が**LLM向けの操作すべてに優先されます**。スキルは**オンデマンドの知識のためだけ**にあり、CLIコマンドのラッパーとしては使いません（MCPツールを使う）。

## `skill://` によるIDE/CLIとの往復

エージェント設定は `skill://` というグロブパターンでスキルを参照でき、これによりCrew・Kiro IDE・Kiro CLI 間でスキルの往復ができます。この仕組みは `annotate_skills_with_agents` がエージェントJSONを解析し、`skill://` グロブを事前展開して各スキルと照合する形で実装されています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> エージェントが独自の `skill://` マッピングを持つときのスキル本文の扱いについて、v0.7.2 の仕様書2ファイルの記述が異なります。
>
> - `memory-skills-hooks.md` 3189-3190行: 「A `skill://` mapping restricts availability, not eager body delivery」（マッピングは利用できる範囲を絞るもので、本文を先に配るものではない）
> - `config.md` 2730-2731行: 「An agent with its own `skill://` mapping gets neither -- those skills arrive as complete instructions」（どちらのエントリも受け取らず、スキルは完全な指示として届く）
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## Hooks

`hooks.py` がconfig駆動のフック機構を提供します（PreToolUseゲート等）。詳細はセキュリティ節（[09_security.md](09_security.md)）で扱います。

## v0.7.0での変更

v0.7.0 の CHANGELOG と、公式 skills／agents／agent-templates ページ（いずれも Page updated 2026-09-25）で確認できる変更です。スキルの読み込みモードの説明と `skills.lazy_load` の既定値は「[読み込み方式](#読み込み方式)」を参照してください。

- **エージェントを Markdown 1ファイルで書ける**: `~/.kiro/agents` に YAML frontmatter 付きの Markdown で書いたエージェントは、対になる JSON なしで一覧に表示され、使えます。エージェントピッカーはテンプレートを crew member と並べて表示します（member としては登録しません）。エージェントは、tag manager で設定した権限のもとで `chat_tag` ツールを使い、セッションをボードのタグ間で移動できます（CHANGELOG 410-414行）
- **親テンプレートの継承（Kiro バックエンド）**: Agent Capabilities → Agents → エージェントの **Capabilities** ペインで **Follow the parent template** をオンにし、能力ごとに次を選びます。親テンプレートが変わると、取り込む差分を確認してから適用します（公式 agent-templates ページ「Follow a parent template」／CHANGELOG 239-243行）
  - **Inherited**: 親の現在値を使い、親の変更に自動で追従します
  - **Override**: 親の変更にかかわらず、エージェント自身の値を保ちます
  - **Removed**: その能力をこのエージェントでは抑止します（後の親の変更も含みます）。選択を変えるまで続きます
- **テンプレートの編集とフォーク**: エージェントの **Agent Template** ペインで、親テンプレートに従っていないエージェントのモデルとスキルをその場で編集できます。最初の編集で共有テンプレートを変えずに私的コピーをフォークし、**Customized** マーカー、テンプレートと異なるフィールド数のライブ表示、保存内容のプレビュー、**Save as new template** を表示します（公式 agent-templates ページ／CHANGELOG 244-248行）。フォークしたコピーには親テンプレートの変更が流れ込みません（公式 agent-templates ページ「Fork a private copy」）
- **リポジトリからスキルをインポート**: **Settings → Skills → Discover** で、公開 GitHub リポジトリの1スキルまたは全スキルを取り込めます。アドレスは `owner/repo`・`owner/repo@ref`・`owner/repo:path`・`owner/repo@ref:path` の形式で、インストール時に解決したコミットに固定されます。インポートはスナップショットで、購読ではありません。新しいリビジョンは同じアドレスを再インポートして確認・適用します。エージェントは `skill_fetch` でレジストリのスキルを確認できますが、インストールはダッシュボードでの操作です（公式 skills ページ「Import from a repository」／CHANGELOG 422-423行）

出典: CHANGELOG.md v0.7.0節 239-248行・410-414行・419-425行（`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/capabilities/skills/>、<https://kiro.dev/docs/crew/capabilities/agents/>、<https://kiro.dev/docs/crew/capabilities/agent-templates/>（いずれも Page updated 2026-09-25）

## 未確認事項

- 本ページの記述は公式 `capabilities/` 配下と `memory-skills-hooks.md`・`config.md` で確認済み。ただし v0.7.2 の仕様書2ファイルの間で、次の2点の記述が食い違っており、本サイトは裁定していません
  - `skills.lazy_load` の既定（true）のときに提示されるエントリの形（「[読み込み方式](#読み込み方式)」参照）
  - 独自の `skill://` マッピングを持つエージェントでのスキル本文の扱い（「[`skill://` によるIDE/CLIとの往復](#skill-によるidecliとの往復)」参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/capabilities/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
- アーキテクチャ: [01_architecture.md](01_architecture.md)
- セキュリティ: [09_security.md](09_security.md)

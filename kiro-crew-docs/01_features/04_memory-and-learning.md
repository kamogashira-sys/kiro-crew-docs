# メモリと学習

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-10-20）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（埋め込み共有機構の裏付け）: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 2026-09-25）
**出典**（同上）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.9.0・v0.8.0での変更）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.7.0での変更。仕様書の行番号は v0.7.2 のもの）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

---

## 📑 このページの内容

- [6層メモリ](#6層メモリ)
- [記憶がどう作られるか](#記憶がどう作られるか)
- [減衰の3機構](#減衰の3機構)
- [競合解決の優先順位](#競合解決の優先順位)
- [メモリモード](#メモリモード)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [メモリ編集の保護（v0.3.0で追加）](#メモリ編集の保護v030で追加)
- [チャネルごとの記録](#チャネルごとの記録)
- [埋め込みの実行方式](#埋め込みの実行方式)
- [Self-evolving（Auto-Improvement）](#self-evolvingauto-improvement)
- [未確認事項](#未確認事項)

---

## 6層メモリ

Kiro Crew は新しいセッションでも、以前のセッションから好み・プロジェクト状況・学んだ修正内容を引き継ぎます。会話をトークン単位で再生するのではなく、**6つの独立したメモリ層**で実現しています。

> **入れ子の意味に関する重要な注意**: 一次情報は「以下のネストは**source-of-truth ordering**（後の層が前の層を上書きできる順序）であり、ストレージ階層ではない」と明記しています。層1〜3はワークスペースの Markdown ファイル、層4〜6は `memory.db`（共有 `VectorMemoryStore`）の行です。

| 層 | 名前 | 保存先 | 上限（キャップ） |
|----|------|-------|----------------|
| 1 | **Preferences**（好み） | `preferences.md` | 4,250文字 |
| 2 | **Projects**（プロジェクト） | `projects.md` | 6,400文字 |
| 3 | **Recent history**（直近履歴） | `history/{date}.md` | 26,600文字 |
| 4 | **Semantic memory**（構造化キーバリュー） | SQLite `semantic_memory` テーブル＋任意のFAISSインデックス | 12,000文字 |
| 5 | **Episodic memory**（過去の出来事） | SQLite `episodic_memories` テーブル＋任意のFAISSインデックス | 3,000文字・クエリごと上位8件 |
| 6 | **Lessons**（学習した修正） | `lesson.<md5hash>` セマンティックエントリ（confidence 1.0） | 37,250文字・最大50件 |

> **注記**: 上記の上限値は公式ページ（Page updated 2026-10-20）の記述です。公式ページは 2026-10-20 時点で3つの節（Control memory writes and context・Editing saved memories・Named memory stores）が加わっていますが、図と上限値の行は v0.7.2 時点の公式ページ（Page updated 2026-08-04）と同一です。v0.6.0 のリポジトリ `memory-skills-hooks.md` は、全キャップを `int(165,000 × fraction)` という fraction 由来の値として定義しており（fractionが真実源）、公式値とは全項目でわずかに異なっていました（例: Preferences 4,290文字、Projects 6,435文字、Recent history 26,400文字、Semantic memory 12,705文字、Lessons 37,290文字）。v0.7.0 以降の同ファイルでは基準値が固定 33,000文字に変わり、これら165,000由来の値は記載されていません（下記の食い違いを参照）。詳細な対応表は [04_reference/05_limits.md](../04_reference/05_limits.md) を参照してください。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **公式 memory ページ**（Page updated 2026-10-20）: 図の見出しを「Context Window (~55K tokens)」とし、上表の各キャップ（Lessons 37,250文字など）を掲載しています。図の見出しと各キャップの値は、v0.6.0 時点・v0.7.2 時点の公式ページから変わっていません
> - **リポジトリ `memory-skills-hooks.md`（v0.9.0）6135行**: 「`_CONTEXT_BUDGET_BASE` is a fixed 33,000-character Crew background admission allowance, reused from the former smallest-window tier. Model window size and `skills.lazy_load` cannot enlarge it」と記載します。基準値は固定 33,000文字で、モデルのウィンドウサイズで拡大しません（v0.6.0 の同ファイル15行は「reference budget 165,000 chars, ~55k tokens」と記載していました）
> - **同ファイル 3377行（Lessons）**: `lessons` バジェットは「22.6% of the 33,000 base」です。一方、起動時に注入するルール層は `caps.lessons_startup`（`_LESSONS_STARTUP_CAP` = 37,000文字）という別枠で制限され、「deliberately NOT a share of the 33,000 base」（基準値の取り分ではない）と明記されています。37,000文字はモデルのウィンドウに比例しません
>
> 行番号は v0.9.0 のもので、v0.7.2 では 4582行・2782行でした。基準値の固定 33,000文字と、起動時のルール層の 37,000文字は、どちらも v0.7.2 と同じです。`config.md` 3825-3829行も、オプションの内容に充てる枠を固定 33,000文字と記載しています。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
> **出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-10-20）

### Preferences（好み）

ユーザーの習慣・ツールの好み・コミュニケーションスタイル。**30メッセージごとに Consolidator によって全面的に置き換えられます**（追記ではありません）。新しいセッションのたびに注入されます。

### Projects（プロジェクト）

進行中の作業状況（CR・パッケージ・ブランチ・状態）。Preferences と同じライフサイクルです。

### Recent history（直近履歴）

日次要約を段階的に減衰させて保持します（詳細は[減衰の3機構](#減衰の3機構)）。3時間アイドル時に更新され、heartbeat サービスにより日次で刈り込まれます。

### Semantic memory（構造化キーバリュー）

SQLite に保存される構造化された事実。キーの接頭辞は `pref.*` / `project.*` / `user.*`（ユーザー定義の追加キーも可）。**常時オン**で、埋め込みモデルがダウンロードされ次第自動的に有効化されます。検索はハイブリッド（`0.6 × ベクトルスコア + 0.4 × キーワードスコア`。埋め込みモデル未ダウンロード時はキーワードのみにフォールバック）。

**confidence gating**（確信度ゲート）によりハルシネーションによる書き込みを防ぎます。LLM による書き込みは確信度0.8以上が必要。ユーザーが明示した書き込みは確信度に関わらず常に勝ちます。競合時は確信度が高い方が勝ち、同確信度なら新しい方が勝ちます。

### Episodic memory（過去の出来事）

「zoomのバグをCSSカスタムプロパティの追加で修正した」のような、特定の過去の出来事を捉えた短いテキストの断片です。過去の会話への検索可能なブックマークと考えられます。1エントリ10〜2,000文字。FAISS コサイン類似度0.88超は重複として拒否されます。最大10,000件（超過時は重要度最低・最古のものから刈り込み）。

検索には**時間減衰スコアリング**と**MMR多様性リランキング**（Jaccardベース、λ=0.6）を使い、冗長な結果を避けます。

### Lessons（学習した修正）

デフォルトの振る舞いを上書きする、ユーザーが教えたルールです。「常にXをして」と言ったとき、または会話中に修正パターンが検出されたときに作成されます。重複排除は部分文字列一致＋トピック重複（50%超のキーワード重複→新しい方に置換）。**global（グローバル）とworkspace（ワークスペース）のスコープ**があります。v0.4.0 CHANGELOGは、scope optionが以前は機能していなかったが、この版で動作するようになったと記載します（一次情報: `memory-skills-hooks.md`「`[Learned corrections]`（global + workspace）」）。`[Learned corrections]` という独立したブロックとして注入されます（公式ページの記述）。v0.9.0 のリポジトリ仕様書では、lesson が宣言する `applies` によって注入先が2つのブロックに分かれると記載されています（「[v0.7.0での変更](#v070での変更)」参照）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **lesson のスコープ**: 公式 CLI リファレンス（Page updated 2026-10-20）は `kirocrew learn add --scope workspace` を載せ、Scopes を `global`（既定）と `workspace` としています。仕様書 `memory-skills-hooks.md` 6250行は `lessons` グループの内容を「`[Learned corrections]`（global + workspace）」と記載します。一方、`memory-skills-hooks.md` 3216行は lesson を1つのリポジトリに限る `repo_scope` を記載し、`docs/architecture/context-management.md` 114-117行は「The legacy `scope="workspace"` tier never reaches a prompt」と記載しています
> - **トピック重複の基準**: 公式 memory ページは「topic overlap (>50% keyword → replace)」と記載します。仕様書 `memory-skills-hooks.md` 3236行は「shared keywords ≥ 50% of the LARGER keyword set → newer wins」と記載します
>
> どちらの食い違いも v0.7.2 の一次情報に同じ記述があり、v0.9.0 でも継続しています。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
> **出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-10-20）、<https://kiro.dev/docs/crew/interfaces/cli-reference/>（Page updated 2026-10-20）

## 記憶がどう作られるか

```
ユーザーメッセージ
    ├──► learn_add MCPツール ──► write_lesson() ──► 即時レッスン保存
    │    （ユーザーが「Xを覚えて」と言う、またはエージェントが修正される）
    │
    ├──► 30メッセージ ──► HistoryConsolidator（好み経路）
    │                    ├── preferences.md を更新（全面置換）
    │                    ├── projects.md を更新（全面置換）
    │                    └── セマンティックエントリを抽出（最大20件）
    │
    ├──► 3時間アイドル ──► HistoryConsolidator（履歴経路）
    │                     ├── history/{date}.md に追記
    │                     ├── エピソディックエントリを抽出（最大10件）
    │                     └── 暗黙のレッスンを抽出（「覚えて」と言わない修正）
```

**2つの独立した統合（Consolidation）経路**があります。

| 経路 | トリガー | 更新対象 | オフセット管理 |
|------|---------|---------|--------------|
| 好み／プロジェクト | **30メッセージ**（セッション単位、`_CONSOLIDATION_THRESHOLD`） | `preferences.md`・`projects.md`・セマンティックエントリ | メモリ内の `_prefs_offset` 辞書 |
| 履歴＋レッスン | **3時間アイドル**（セッション単位、`history_idle_hours` = 3.0） | `history/{date}.md`・エピソディックエントリ・`lessons.jsonl`（またはベクトルストアの `lesson.*`） | JSONLメタデータ内の永続化された `last_consolidated` |

好み経路は永続化された `last_consolidated` マーカーを進めません（履歴経路のみが進めます）。これにより、好み統合が先に走っても履歴統合が全メッセージを必ずカバーします。

統合1回あたりの抽出上限は、セマンティック20件、エピソディック10件、暗黙の lesson 10件です（`memory-skills-hooks.md` 386-390行、v0.9.0）。`memory-skills-hooks.md` 2381行は、減衰の3機構（下記）を含むこれらの仕組みが V1 にだけ適用され、V2 は全履歴とエピソディックの内容を、年齢による順位下げや容量による自動削除なしで保持すると記載しています。本ページは V1 を前提とした記述です。

### 明示的レッスン vs 暗黙的レッスン

- **明示的**: ユーザーが「pytest-asyncio strict modeを常に使うことを覚えて」と言う → `learn_add` で即時保存
- **暗黙的**: ユーザーが「覚えて」と言わずにエージェントを訂正する（例:「いや、それをキャッシュしないで — 値はリクエストごとに変わる」） → 履歴統合の際に抽出される

## 減衰の3機構

古いメモリがコンテキストを消費し続けないよう、3つの独立した減衰機構があります。

### 1. 履歴の時間段階的減衰

| 経過期間 | 保持内容 |
|---------|---------|
| 0〜13日 | タイムスタンプ付きの全エントリ |
| 14〜60日 | 日ごとの最初のエントリ＋件数 |
| 61〜180日 | 日付＋件数のみ |
| 181〜364日 | コンテキストには読み込まれない（ディスクには保持） |
| 365日以降 | ディスクから削除 |

古い履歴は段階的に詳細さを失い、「何かが起きた」というマーカーになり、やがてコンテキストから外れるがディスクには残り、最終的に365日で完全に削除されます。

### 2. エピソディックの指数時間減衰スコアリング

```
score = cosine_sim × (0.7 + 0.3 × importance) × exp(-0.03 × days_old)
```

約23日で50%、約77日で10%まで減衰します。

### 3. エピソディック上限の強制

10,000件に達すると、重要度最低かつ最古のものから刈り込まれます。

## 競合解決の優先順位

複数の記憶が競合したとき、以下の順で優先されます（公式ページの明示的な優先順位）。

```
1. Lessons（ユーザー明示、confidence 1.0）
2. Semantic memory（ユーザー明示の書き込み）
3. Semantic memory（LLMの書き込み、confidence 0.8以上）
4. Preferences / Projects（統合により生成）
5. Episodic memory（関連度スコアリングされた断片）
6. History（時間減衰した要約）
```

Lessons が最優先されるのは、「常にこれに従う。デフォルトの振る舞いを上書きする」と明記された独立ブロック `[Learned corrections]` で注入されるためです（公式ページの記述。v0.9.0 のリポジトリ仕様書でのブロック分割は「[v0.7.0での変更](#v070での変更)」参照）。

## メモリモード

Crew のセッションには `memory_mode` があり、値は **`persistent`（永続・既定）・`incognito`（匿名）・`temporary`（一時）** の3種です（`history.py` の `INCOGNITO_MEMORY_MODES` として実装。`session-summary.md` にも同様の記述あり）。

| モード | 記憶を読む | 記憶に書く |
|-------|-----------|-----------|
| **Persistent**（既定） | はい | はい |
| **Incognito** | はい | いいえ |
| **Temporary** | いいえ | いいえ |

上表は公式 sessions ページ（Page updated 2026-10-20）の記述です。Incognito は好み・lesson・履歴を使えますが、会話は何も書き戻しません。Temporary は記憶を読みも書きもしません。仕様書も、Incognito は読み取りを許可して学習の書き込みをすべて拒否し、Temporary は lesson を含めて記憶を読みも書きもしないと記載しています（`memory-skills-hooks.md` 51-52行）。`incognito`・`temporary` のセッションは「restricted（制限）」として扱われ、統合（consolidation）とレッスン抽出がブロックされます。メモリコンテキストの読み取りのブロックは Temporary にあたります。どちらのモードでも、セッションのJSONL自体（タブ復旧・Gateway再起動時の復元のため）は書き込まれます（`learn-cron-dashboard.md` 218行）。

新規のダッシュボードチャットの既定モードは、Settings → Chat → Default Memory Mode（`dashboard.default_memory_mode`。既定 `persistent`）で選びます。新規チャットのフローで明示的に選んだモードが常に優先されます（公式 sessions ページ、`config.md` 2783行）。

> v0.7.2 以前の本ページは、`incognito` と `temporary` の両方でメモリコンテキストの注入がブロックされると記載していました。これは誤りでした。Incognito は記憶を読みます。

**出典**: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-10-20）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/learn-cron-dashboard.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.9.0での変更

v0.9.0 の CHANGELOG（v0.9.0節 125-127行）、公式 memory ページ（Page updated 2026-10-20）、v0.9.0 タグの仕様書で確認できる、メモリに関わる変更です。v0.8.0・v0.9.0 の CHANGELOG に「Before you upgrade」節はありません。

### 保存済みメモリの編集と復元

Settings → Overview の **Memory** カードで **Edit saved memories** を開くと、既定ストアのレコードエディタが開きます。レコードを開くと、値・由来（provenance）・**Revision history** を読めます。

- **Restore an earlier version**: Revision history の中で、値が現在と異なる以前の承認済みバージョンに **Restore "…"** ボタンが出ます。押すと **Restore an earlier version** ダイアログが開き、**Now**（いまの値）と **After restoring**（復元後の値）の2列でプレビューします
- 確定すると、その値が **Restored version** と印の付いた新しいバージョンとして保存されます。以前のバージョンは履歴に残るため、復元そのものも元に戻せます

仕様書 `memory-skills-hooks.md` は、公式ページにない次の内容を記載しています（Memory V2 は同ファイル5行で「development-stage」と記載されており、本サイトは V2 を機能として扱いません）。

- 履歴として自動で保持される承認済みスナップショットは、V1 では1レコードあたり直近20件です。V2 の承認済みスナップショットと、どちらの版でも提案（proposal）には自動の保持上限がありません（6013-6015行）。保持から外れたスナップショットを指定した復元は 404 `memory_revision_missing` で拒否されます（6030-6037行）
- レコード一覧 API は `limit` を 1〜100 で受け付け（5987-5988行）、エディタは1ページ50件を描画します（1458行）。`refresh` は最大500件の識別子を解決します（5996行）。一括操作は、識別子の明示指定が最大500件、条件に一致するすべてを選ぶ場合は最大10,000件・32 MiB です（6054-6060行）

### 名前付きメモリストアの作成

`config.json` の `memory_stores` に宣言した名前付きストアのディレクトリは、初回利用時に作られません。ディレクトリが削除されたストアは、作り直すまで欠けたままです。作り直すには `kirocrew memory create-store <name>` を使います（CHANGELOG v0.9.0節 125-127行）。

- 成功すると `Created memory store '<name>' at <path>.` を出力します。ディレクトリが既に存在するときは、何も変更せずその旨を報告します
- 既定ストア（作成手順が不要）、`memory_stores` に宣言のない名前、crewmate のストア（crewmate の作成と同時に作られる）を指定すると、stderr に1行を出して終了コード 1 で拒否します

仕様書 `cli.md` 423行は、このコマンドの対象を「`memory_stores` に宣言した名前付きの V1 ストア」と記載し、V2 のメンバーストアは「メンバーと同時に用意される」ため拒否すると記載しています。`kirocrew memory` のほかの動詞（`list`・`search`・`show`・`stats`・`audit`・`export`・`migrate`・`backup`・`backups`・`restore`・`carve`・`retired`・`import`）は、公式 CLI リファレンス（Page updated 2026-10-20）に載っています。コマンドの一覧は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) を参照してください。

### Crewmate のプライベートメモリ（Preview）

公式 agents ページ（Page updated 2026-10-20）は、Settings → Developer → Feature Previews → Crewmates を有効にした Preview 機能として、各 crewmate が表示名・プライベートメモリ・ワークスペース・agent template・既定モデル・任意のトリガーを持つと記載しています。仕様書は、新規の Crew Member の作成で V2 のメモリストアが1つ割り当てられ、V2 は development-stage であると記載しています（`memory-skills-hooks.md` 5行、`config.md` 410-417行）。V2 の内部仕様は本サイトでは扱いません。

> 呼称について: v0.8.0 の CHANGELOG は Preview を「the Crew Members preview」と呼び、v0.9.0 時点の公式 agents ページは同じ Preview を「Crewmates」と呼んでいます。本サイトは裁定せず、両方の呼称を示します。

### Auto-Improvement の書き込みルートは owner 限定

v0.9.0 の CHANGELOG は、すべての built-in App の書き込みルートがダッシュボードの owner だけを受け付けるようになったと記載しています（v0.9.0節 174-175行）。Auto-Improvement について、仕様書 `auto-improvement.md` は次のように記載しています。

- `/api/apps/auto-improvement/` のルートのうち17本は owner 限定で、owner でないダッシュボードのユーザーとアプリ token は 403 `owner_only` になります。許可された呼び出しは SEL に記録されます
- アプリを無効にすると、実行中の watcher とランも止まります（28-40行）

Auto-Improvement は既定で無効の built-in App です（[10_apps.md](10_apps.md)）。

### 仕様書だけに記載がある項目

次の項目は、公式ドキュメントと CHANGELOG（v0.8.0・v0.9.0）に記載がなく、v0.9.0 タグのリポジトリ仕様書だけが記載しています。v0.8.0 の仕様書には記載がありません。

- **`memory.inject_lessons_per_turn`（既定 `false`、既定オフ）**: 有効にすると、フォローアップのメッセージごとに、そのセッションにまだ見せていない一致 lesson を最大3件・lesson の行の合計が最大2,000文字（ヘッダとフッタは数えない）まで、`[Learned corrections — relevant to this message …]` として追加します。`memory.inject_lessons` が有効なことが前提で、Temporary のターンと最小コンテキストのターンには入りません（`memory-skills-hooks.md` 6130行、`config.md` 2713行）

**出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-10-20）
**出典**: <https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）、<https://kiro.dev/docs/crew/interfaces/cli-reference/>（Page updated 2026-10-20）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.9.0節 125-127行・174-175行（`99e6253`）。

## v0.8.0での変更

v0.8.0 の CHANGELOG（v0.8.0節）、公式 memory ページ（Page updated 2026-10-20）、v0.9.0 タグの仕様書で確認できる変更です。

### メモリの書き込みと注入を切り替える設定

`config.json` の次の4キーで、Gateway が何を記録し、新しいターンに何を渡すかを切り替えられます（CHANGELOG v0.8.0節 364-370行、公式 memory ページ「Control memory writes and context」）。4つとも既定は `true` です。

| 設定 | `false` にしたときの効果 |
|------|----------------------|
| `memory.persistence_enabled` | 自動のメモリ書き込みと統合が止まります。保存済みのメモリや lesson も新しいセッションに加えません |
| `memory.inject_memory` | 保存済みメモリを新しいセッションのコンテキストから省きます |
| `memory.inject_lessons` | 学習した修正（`[Learned corrections]`）とユーザープロファイル（`[USER PROFILE]`）のブロックを省きます |
| `memory.inject_activity` | 最近のプロジェクト・履歴・タスク事実・過去のエピソードを省きます。`memory.inject_memory` が `false` のときは効果がありません |

- これらは Gateway 全体（プロセス全体）の設定で、1つの会話にだけ効く Persistent／Incognito／Temporary のセッションモードの代わりにはなりません。1つの会話にはセッションモードを使い、Gateway が全セッションの記憶の扱いを変えるべきときにこれらの設定を使います（公式 memory ページ）
- 仕様書は、これらの設定を `build_session_context()` の中で評価し、`memory` グループとの交差で決めると記載しています（`memory-skills-hooks.md` 288-310行）
- Developer Mode を有効にすると、コンテキストの内訳に **Facts recalled for this task** の行が加わります（CHANGELOG v0.8.0節 371-373行。公式 memory ページには記載がありません）

### 新しいセッションの初期注入（v0.7.0 の変更の更新）

`memory.inject_activity`（既定 `true`）が有効なとき、仕様書は、新しいセッションの最初のターンに、予算付きの `[Memory activity]` ブロックが加わると記載しています。ブロックの中身は、プロジェクト、日次履歴（14日分は全文、それ以降は要約と件数で180日目まで）、タスク事実、リクエストに関連するエピソードです（`memory-skills-hooks.md` 34-37行・132-137行・294-300行・1430-1440行・6128行）。`false` にすると、これらは `memory_recall` で取得する構成に戻り、起動時にクエリの埋め込みも行いません（同ファイル 1430-1440行）。公式 memory ページ（Page updated 2026-10-20）も `memory.inject_activity` を同じ意味で記載しています。v0.7.0〜v0.7.2 の仕様書にこのスイッチの記載はなく、v0.8.0 の仕様書に記載があります。v0.8.0 と v0.9.0 の CHANGELOG は、v0.7.0 の「初期注入が減った」記述を変更する旨を説明していません。

これにより、v0.7.x で公式 memory ページと仕様書の間にあった「新しいセッションの初期注入」の食い違いは、v0.9.0 の一次情報では解消しています（下記「[v0.7.0での変更](#v070での変更)」参照）。

### 統合で抽出される lesson も `applies` を宣言する

v0.7.2 の仕様書は、統合（consolidation）で抽出された lesson は `applies` を持たないと記載していました。v0.8.0 以降の仕様書は、履歴統合の抽出プロンプトが抽出した項目ごとに同じ指示を持ち、正規化した区分を書き込み経路に渡すと記載します。値が空・綴りの誤りの場合は「unstated」として書かれ、破棄されません。タスクランナー自身の lesson 抽出（`source="task_runner"`）と、CLI の直接の `write_lesson` は、現在も区分を宣言せず、unstated のままです（`memory-skills-hooks.md` 3377行）。本内容は仕様書で確認したもので、CHANGELOG の v0.8.0節・v0.9.0節は説明していません。

### observe モードのバッファ設定

observe モードのバッファの既定（200件・1週間）は、`slack.observe_max_messages` と `slack.observe_ttl_hours` で設定します。仕様書 `channel-history.md` 48行は、observe チャネルの履歴を `<data-home>/history` の JSONL に追記し、起動時に読み込むと記載しています。observe 以外のモードは、下記「[チャネルごとの記録](#チャネルごとの記録)」の表のとおりです。本内容は仕様書で確認したもので、CHANGELOG は説明していません。

**出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-10-20）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/channel-history.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.8.0節 364-373行（`99e6253`）。

## v0.7.0での変更

v0.7.0 の CHANGELOG と v0.7.2 タグのリポジトリ仕様書 `memory-skills-hooks.md` で確認できる、メモリと学習に関わる変更です。v0.7.x の CHANGELOG に「Before you upgrade」節はありません。

- **lesson が `applies` を宣言する**: 保存する lesson が「standing rule（常に従うルール）」か「past finding（過去の知見）」かを `applies`: `always` / `on_topic` で宣言します（CHANGELOG 422-425行）。仕様書（v0.9.0 の 3377行。v0.7.2 では 2782行）の記載は次のとおりです
  - 起動時の注入は2ブロックに分かれます。`always` は `[Learned corrections]`（`lessons` バジェット）、`on_topic` は `[Learned experience]`（別枠の `lesson_experience` バジェット、5%）に入ります。2つのバジェットは合算されず、モデルのウィンドウが広くても拡大しません
  - `applies` を持たない lesson（この項目ができる前に書かれたものすべてを含む）は「unstated」として扱われ、ルールのブロック（`[Learned corrections]`）に入ります。同じブロック内では `always` と明示された行が unstated の行より前に並びます
  - `applies` を指定できる書き込み経路は `learn_add` MCPツール・`POST /api/lessons`・そのルートを使う CLI です。v0.7.2 の仕様書では、統合（consolidation）で抽出された lesson は `applies` を持たず、ルールのブロックに入ると記載していました。v0.8.0 以降の仕様書は、統合の抽出も `applies` を宣言すると記載しています（「[v0.8.0での変更](#v080での変更)」参照）
  - `applies` は write-once です。区分を変えるには削除して追加し直します
  - リクエストがどの `on_topic` の lesson にも一致しないときは、`[Learned experience]` の中身を注入せず、保留した件数と `memory_recall`／`learn_list` を示す通知だけを表示します。バジェット超過で省いた lesson も件数付きで通知され、黙って省かれることはありません
- **新しいセッションの初期注入が減った（v0.7.0〜v0.7.2）**: 新しいセッションは日次履歴と古いプロジェクトノートを注入しなくなりました（CHANGELOG 476-477行）。v0.7.2 の仕様書（33-36行）は、最初のターンに安定した好みと該当するルールを保持し、それ以前の活動（日次履歴・プロジェクトノート・古いタスクの事実・エピソード）は `memory_recall` で明示的に取得すると記載し、これは Global V1 と named V1 にも適用されるとしています。起動時には最大1,800文字の activity index（プロジェクトの見出し／先頭エントリと、直近3日分の見出し／先頭行）が入ります（4584-4592行）。**v0.8.0 以降は既定が変わっています。** `memory.inject_activity`（既定 `true`）が有効なとき、最初のターンに日次履歴・プロジェクト・タスク事実・関連エピソードが予算付きの `[Memory activity]` ブロックとして入ります。activity index（最大1,800文字）は v0.9.0 の仕様書にも残っています（6139行）。詳細は「[v0.8.0での変更](#v080での変更)」を参照してください
- **参照バジェットの基準値**: リポジトリの基準値 `_CONTEXT_BUDGET_BASE` が固定 33,000文字になりました（v0.6.0以前は165,000文字）。公式 memory ページの記述（~55K tokens）との食い違いは「[6層メモリ](#6層メモリ)」の注記を参照してください

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **公式 memory ページ**（Page updated 2026-10-20）: 「Injected as a distinct `[Learned corrections]` block」と、Lessons を1つのブロックとして説明しています
> - **v0.7.0 の CHANGELOG と v0.9.0 の `memory-skills-hooks.md`**: 上記のとおり、Lessons は `applies` によって2ブロックに分かれます（`memory-skills-hooks.md` 3377行）
>
> v0.7.x にあった、新しいセッションの初期注入（Recent history を含むかどうか）の食い違いは、v0.8.0 の `memory.inject_activity` により、v0.9.0 の一次情報では解消しています（「[v0.8.0での変更](#v080での変更)」参照）。

> **注記**: `memory-skills-hooks.md` 5行（v0.7.2 も v0.9.0 も）は「Memory V2 is a development-stage replacement」（開発段階の置き換え）と記載していますが、公式 memory ページは Memory V2 を記載していません。本サイトは Memory V2 を機能として扱いません。

出典: CHANGELOG.md v0.7.0節 422-425行・476-477行（`c67c506`）。
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2。`applies` の記載は 2026-10-25 / commit `99e6253` / 版 v0.9.0 の 3377行で再確認）
**出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-10-20）

## メモリ編集の保護（v0.3.0で追加）

**メモリの編集には「認識済みのセッション」が必要になりました。** 偽造されたキーで保存済みメモリを削除できる経路が閉じられています。

出典: CHANGELOG.md v0.3.0節 226行（`21584ea`）「**Memory edits require a recognised session**, closing a path where a forged key could delete stored memory」。セキュリティ全体の文脈は [09_security.md](09_security.md) を参照してください。

## チャネルごとの記録

同一のメモリストアはすべてのチャネルで共有されますが、記録の振る舞いはチャネルによって異なります（公式ページの表）。

| チャネル | 起動条件 | 履歴バッファ | メモリ統合 |
|---------|---------|-------------|-----------|
| DM | `always`（常時） | セッションベース（ACPネイティブ） | ✅ あり |
| グループチャネル | `mention`（メンション時） | 50メッセージ・5分TTL・メモリ内 | ✅ メンション時のみ |
| グループチャネル | `observe`（観察） | 200メッセージ・1週間TTL・ディスク永続 | ✅ メンション時のみ |
| グループチャネル | `off`（無効） | なし | ❌ なし |
| ダッシュボードタブ | 該当なし | セッションベース（ACPネイティブ） | ✅ あり |

**observe モードでのセキュリティ**: 認可されたユーザー（owner＋許可リスト）からのメッセージのみが記録されます。認可されていないメッセージはプロンプトインジェクションを防ぐため黙って破棄されます。

## 埋め込みの実行方式

**Memory と Knowledge Library は同じ埋め込み機構を共有します。**

Memory（本ページの6層メモリ）と [Knowledge Library](05_knowledge-library.md) は、vendored された `llama-cpp-python` による**常時オン・in-processの共有シングルトン埋め込み器**（`get_shared_embedder()`）を使います。`memory.embedding_provider` は `llama_cpp` のみを受理し、legacy値 `"ollama"`／`"none"` も**強制的に `llama_cpp` にコアース**されます。外部デーモンは不要・設定で無効化できません。

公式ドキュメント `features/knowledge/` も「Knowledge items are embedded for semantic search using **the same in-process embedding runtime as Memory**」と明記しており、両者が同一機構を共有することを確認できます。Ollamaは、埋め込みモデルのCDNダウンロードが失敗した場合の**任意のフォールバック手段**（`ollama pull qwen3-embedding:0.6b` を手動実行）として`troubleshooting.md`に案内されているのみで、既定の実装ではありません。

> **リポジトリ内の記述の不整合は v0.6.0 で解消しました**。v0.4.1 時点では `docs/system-specs/modules/knowledge.md` に「Knowledge Library が `OllamaEmbedder`（`knowledge/embedder.py`）経由で Ollama に依存する」という上記と異なる記述が残っていましたが、**v0.6.0 では同ファイルが `InProcessEmbedder` —「in-process via the vendored llama-cpp runtime, no server and no HTTP hop」に更新され、`Ollama` の語が0件になりました**（`knowledge.md` 106行）。v0.9.0 の同ファイルでも `Ollama` の語は0件で、`InProcessEmbedder` は122行に記載されています。これで公式ドキュメントおよび `memory-skills-hooks.md`／`install.md`／`overview.md`／`config.md` と一致します。詳細は [05_knowledge-library.md](05_knowledge-library.md) を参照してください。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0。v0.9.0 での再確認は 2026-10-25 / commit `99e6253` / 版 v0.9.0）

埋め込みモデルがまだダウンロード中／未取得の間は、メモリはキーワード・FTS検索に緩やかに縮退し、モデルが用意できた時点で自動的に埋め込みが有効になります（再起動不要）。

## Self-evolving（Auto-Improvement）

`auto-improvement.md` が定義する自己改善の仕組みです。**measurement-first**（まず測定してから改善する）の自己改善ループで、メトリクスを校正し既知の改善を検出できることを証明してから keep-or-revert を回し、決定論的なゲートとA/B測定を通った候補のみをドラフトPRにします。

設計原則: **「あらゆる判断は決定論的なPython、あらゆる提案はエージェント。エージェントは自分の成果を採点しない」**。opt-in の builtin App（`auto_improvement`。表示名「Auto-Improvement」）として提供されます。既定では無効です。詳細は [10_apps.md](10_apps.md) を参照してください。owner 限定のルートについては「[v0.9.0での変更](#v090での変更)」の「Auto-Improvement の書き込みルートは owner 限定」を参照してください。

## 未確認事項

- 公式 memory ページ（Page updated 2026-10-20）とリポジトリ `memory-skills-hooks.md`（v0.9.0）の間で、参照バジェットの基準値（~55K tokens と固定 33,000文字）と、Lessons の注入ブロック（1つと2つ）の記述が食い違っています。本サイトは裁定していません（「[6層メモリ](#6層メモリ)」「[v0.7.0での変更](#v070での変更)」参照）。このほかに、lesson のスコープとトピック重複の基準にも食い違いがあります（「[Lessons（学習した修正）](#lessons学習した修正)」参照）。新しいセッションの初期注入（Recent history を含むかどうか）の食い違いは、v0.9.0 の一次情報では解消しています
- メモリモード用語（persistent/incognito/temporary）は当初 Zenn 記事由来の記述として要検証扱いだったが、`history.py` の `INCOGNITO_MEMORY_MODES` および `session-summary.md` 249行で実在を確認済み。各モードの意味は公式 sessions ページの表と仕様書（51-52行）で確認済み
- 「Lessons 最大50件」は、公式 memory ページだけの記載です。仕様書で lesson 数の上限として確認できたのは、インポートが寄与する lesson の最大50件（`memory-skills-hooks.md` 3166行）だけで、起動時に注入する lesson 数の上限としての根拠は一次情報で確認できません
- 公式 memory ページのキャップ値（Preferences 4,250文字など）と、リポジトリの各ブロックの割合（Preferences 2.6% など）の対応は、どちらの資料も文字数で対応表を載せておらず、確認できません。`context-management.md` は割合と定数名だけを記載しています
- 公式 memory ページの「Thread conversation history 45,000 chars (LLM-compressed)」と、仕様書のスレッド履歴の許容量（`memory-skills-hooks.md` 6188-6193行）は、別の数値です。両者の関係は一次情報で確認できないため、本サイトは裁定していません
- Memory V2 の挙動は、仕様書が development-stage と記載し、公式 memory ページが触れていません。本サイトは V2 を機能として扱わず、仕様書の範囲を超える内容は確認していません
- 仕様書 `memory-skills-hooks.md` 3383行は、lesson のランキングを評価するベンチ `lesson-recall` を記載しています。このベンチは公式 CLI リファレンスに載っていません。利用者向けのコマンドかどうかは確認できないため、本サイトは扱いません
- Knowledge Libraryの埋め込み機構は、公式ドキュメント `features/knowledge/` および `memory-skills-hooks.md`／`install.md`／`overview.md`／`config.md`で「Memoryと共有するin-process機構」と確認済み。**v0.4.1 まで食い違っていた `docs/system-specs/modules/knowledge.md` も v0.6.0 で `InProcessEmbedder` に更新され、不整合は解消した**（上記「埋め込みの実行方式」参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/memory/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
- Knowledge Library: [05_knowledge-library.md](05_knowledge-library.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

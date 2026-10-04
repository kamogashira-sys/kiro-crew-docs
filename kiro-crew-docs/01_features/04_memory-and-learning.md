# メモリと学習

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（埋め込み共有機構の裏付け）: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 表記あり）
**出典**（同上）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（v0.7.0での変更・参照バジェットの基準値・Lessons の2ブロック化）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（キャップ値と「~55K tokens」が不変であることの確認）: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-08-04）

---

## 📑 このページの内容

- [6層メモリ](#6層メモリ)
- [記憶がどう作られるか](#記憶がどう作られるか)
- [減衰の3機構](#減衰の3機構)
- [競合解決の優先順位](#競合解決の優先順位)
- [メモリモード](#メモリモード)
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

> **注記**: 上記の上限値は公式ページ（Page updated 2026-08-04。v0.6.0 時点の内容とバイト単位で同一）の記述です。v0.6.0 のリポジトリ `memory-skills-hooks.md` は、全キャップを `int(165,000 × fraction)` という fraction 由来の値として定義しており（fractionが真実源）、公式値とは全項目でわずかに異なっていました（例: Preferences 4,290文字、Projects 6,435文字、Recent history 26,400文字、Semantic memory 12,705文字、Lessons 37,290文字）。v0.7.2 の同ファイルでは基準値が固定 33,000文字に変わり、これら165,000由来の値は記載されていません（下記の食い違いを参照）。詳細な対応表は [04_reference/05_limits.md](../04_reference/05_limits.md) を参照してください。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **公式 memory ページ**（Page updated 2026-08-04）: 図の見出しを「Context Window (~55K tokens)」とし、上表の各キャップ（Lessons 37,250文字など）を掲載しています。v0.6.0 時点から内容は変わっていません
> - **リポジトリ `memory-skills-hooks.md`（v0.7.2）4582行**: 「`_CONTEXT_BUDGET_BASE` is a fixed 33,000-character Crew background admission allowance, reused from the former smallest-window tier. Model window size and `skills.lazy_load` cannot enlarge it」と記載します。基準値は固定 33,000文字で、モデルのウィンドウサイズで拡大しません（v0.6.0 の同ファイル15行は「reference budget 165,000 chars, ~55k tokens」と記載していました）
> - **同ファイル 2782行（Lessons）**: `lessons` バジェットは「22.6% of the 33,000 base」です。一方、起動時に注入するルール層は `caps.lessons_startup`（`_LESSONS_STARTUP_CAP` = 37,000文字）という別枠で制限され、「deliberately NOT a share of the 33,000 base」（基準値の取り分ではない）と明記されています。37,000文字はモデルのウィンドウに比例しません
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

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

デフォルトの振る舞いを上書きする、ユーザーが教えたルールです。「常にXをして」と言ったとき、または会話中に修正パターンが検出されたときに作成されます。重複排除は部分文字列一致＋トピック重複（50%超のキーワード重複→新しい方に置換）。**global（グローバル）とworkspace（ワークスペース）のスコープ**があります。v0.4.0 CHANGELOGは、scope optionが以前は機能していなかったが、この版で動作するようになったと記載します（一次情報: `memory-skills-hooks.md`「`[Learned corrections]`（global + workspace）」）。`[Learned corrections]` という独立したブロックとして注入されます（公式ページの記述）。v0.7.2 のリポジトリ仕様書では、lesson が宣言する `applies` によって注入先が2つのブロックに分かれると記載されています（「[v0.7.0での変更](#v070での変更)」参照）。

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

Lessons が最優先されるのは、「常にこれに従う。デフォルトの振る舞いを上書きする」と明記された独立ブロック `[Learned corrections]` で注入されるためです（公式ページの記述。v0.7.2 のリポジトリ仕様書でのブロック分割は「[v0.7.0での変更](#v070での変更)」参照）。

## メモリモード

Crew のセッションには `memory_mode` があり、値は **`persistent`（永続）・`incognito`（匿名）・`temporary`（一時）** の3種です（`history.py` の `INCOGNITO_MEMORY_MODES` として実装。`session-summary.md` にも同様の記述あり）。`incognito`・`temporary` のセッションは「restricted（制限）」として扱われ、統合（consolidation）・レッスン抽出・メモリコンテキストの注入がブロックされます。ただしセッションのJSONL自体（タブ復旧・Gateway再起動時の復元のため）は書き込まれます。

## v0.7.0での変更

v0.7.0 の CHANGELOG と v0.7.2 タグのリポジトリ仕様書 `memory-skills-hooks.md` で確認できる、メモリと学習に関わる変更です。v0.7.x の CHANGELOG に「Before you upgrade」節はありません。

- **lesson が `applies` を宣言する**: 保存する lesson が「standing rule（常に従うルール）」か「past finding（過去の知見）」かを `applies`: `always` / `on_topic` で宣言します（CHANGELOG 422-425行）。仕様書（2782行）の記載は次のとおりです
  - 起動時の注入は2ブロックに分かれます。`always` は `[Learned corrections]`（`lessons` バジェット）、`on_topic` は `[Learned experience]`（別枠の `lesson_experience` バジェット、5%）に入ります。2つのバジェットは合算されず、モデルのウィンドウが広くても拡大しません
  - `applies` を持たない lesson（この項目ができる前に書かれたものすべてを含む）は「unstated」として扱われ、ルールのブロック（`[Learned corrections]`）に入ります。同じブロック内では `always` と明示された行が unstated の行より前に並びます
  - `applies` を指定できる書き込み経路は `learn_add` MCPツール・`POST /api/lessons`・そのルートを使う CLI です。統合（consolidation）で抽出された lesson は `applies` を持たず、ルールのブロックに入ります
  - `applies` は write-once です。区分を変えるには削除して追加し直します
  - リクエストがどの `on_topic` の lesson にも一致しないときは、`[Learned experience]` の中身を注入せず、保留した件数と `memory_recall`／`learn_list` を示す通知だけを表示します。バジェット超過で省いた lesson も件数付きで通知され、黙って省かれることはありません
- **新しいセッションの初期注入が減った**: 新しいセッションは日次履歴と古いプロジェクトノートを注入しなくなりました（CHANGELOG 476-477行）。仕様書（33-36行）は、最初のターンに安定した好みと該当するルールを保持し、それ以前の活動（日次履歴・プロジェクトノート・古いタスクの事実・エピソード）は `memory_recall` で明示的に取得すると記載し、これは Global V1 と named V1 にも適用されるとしています。起動時には最大1,800文字の activity index（プロジェクトの見出し／先頭エントリと、直近3日分の見出し／先頭行）が入ります（4584-4592行）
- **参照バジェットの基準値**: リポジトリの基準値 `_CONTEXT_BUDGET_BASE` が固定 33,000文字になりました（v0.6.0以前は165,000文字）。公式 memory ページの記述（~55K tokens）との食い違いは「[6層メモリ](#6層メモリ)」の注記を参照してください

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> - **公式 memory ページ**（Page updated 2026-08-04）: 「Injected as a distinct `[Learned corrections]` block」と、Lessons を1つのブロックとして説明しています。「Context assembly」節の「At session start」の表には、Projects 6,400文字・Recent history 26,600文字が含まれています
> - **v0.7.0 の CHANGELOG と v0.7.2 の `memory-skills-hooks.md`**: 上記のとおり、Lessons は `applies` によって2ブロックに分かれ、新しいセッションは日次履歴と古いプロジェクトノートを注入しません

> **注記**: v0.7.2 の `memory-skills-hooks.md` 5行は「Memory V2 is a development-stage replacement」（開発段階の置き換え）と記載していますが、公式 memory ページは Memory V2 を記載していません。本サイトは Memory V2 を機能として扱いません。

出典: CHANGELOG.md v0.7.0節 422-425行・476-477行（`c67c506`）。
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 2026-08-04）

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

> **リポジトリ内の記述の不整合は v0.6.0 で解消しました**。v0.4.1 時点では `docs/system-specs/modules/knowledge.md` に「Knowledge Library が `OllamaEmbedder`（`knowledge/embedder.py`）経由で Ollama に依存する」という上記と異なる記述が残っていましたが、**v0.6.0 では同ファイルが `InProcessEmbedder` —「in-process via the vendored llama-cpp runtime, no server and no HTTP hop」に更新され、`Ollama` の語が0件になりました**（`knowledge.md` 106行）。これで公式ドキュメントおよび `memory-skills-hooks.md`／`install.md`／`overview.md`／`config.md` と一致します。詳細は [05_knowledge-library.md](05_knowledge-library.md) を参照してください。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

埋め込みモデルがまだダウンロード中／未取得の間は、メモリはキーワード・FTS検索に緩やかに縮退し、モデルが用意できた時点で自動的に埋め込みが有効になります（再起動不要）。

## Self-evolving（Auto-Improvement）

`auto-improvement.md` が定義する自己改善の仕組みです。**measurement-first**（まず測定してから改善する）の自己改善ループで、メトリクスを校正し既知の改善を検出できることを証明してから keep-or-revert を回し、決定論的なゲートとA/B測定を通った候補のみをドラフトPRにします。

設計原則: **「あらゆる判断は決定論的なPython、あらゆる提案はエージェント。エージェントは自分の成果を採点しない」**。opt-in の builtin App（`auto_improvement`。表示名「Auto-Improvement」）として提供されます。既定では無効です。詳細は [10_apps.md](10_apps.md) を参照してください。

## 未確認事項

- 公式 memory ページ（Page updated 2026-08-04）とリポジトリ `memory-skills-hooks.md`（v0.7.2）の間で、参照バジェットの基準値（~55K tokens と固定 33,000文字）、Lessons の注入ブロック（1つと2つ）、新しいセッションの初期注入（Recent history を含むかどうか）の記述が食い違っています。本サイトは裁定していません（「[6層メモリ](#6層メモリ)」「[v0.7.0での変更](#v070での変更)」参照）
- メモリモード用語（persistent/incognito/temporary）は当初 Zenn 記事由来の記述として要検証扱いだったが、`history.py` の `INCOGNITO_MEMORY_MODES` および `session-summary.md` L188 で実在を確認済み
- Knowledge Libraryの埋め込み機構は、公式ドキュメント `features/knowledge/` および `memory-skills-hooks.md`／`install.md`／`overview.md`／`config.md`で「Memoryと共有するin-process機構」と確認済み。**v0.4.1 まで食い違っていた `docs/system-specs/modules/knowledge.md` も v0.6.0 で `InProcessEmbedder` に更新され、不整合は解消した**（上記「埋め込みの実行方式」参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/memory/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
- Knowledge Library: [05_knowledge-library.md](05_knowledge-library.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

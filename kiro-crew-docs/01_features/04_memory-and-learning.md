# メモリと学習

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/features/memory/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [6層メモリ](#6層メモリ)
- [記憶がどう作られるか](#記憶がどう作られるか)
- [減衰の3機構](#減衰の3機構)
- [競合解決の優先順位](#競合解決の優先順位)
- [メモリモード](#メモリモード)
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

コンテキストウィンドウ全体の参照バジェットは**約55,000トークン**です。

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

デフォルトの振る舞いを上書きする、ユーザーが教えたルールです。「常にXをして」と言ったとき、または会話中に修正パターンが検出されたときに作成されます。重複排除は部分文字列一致＋トピック重複（50%超のキーワード重複→新しい方に置換）。**global（グローバル）とworkspace（ワークスペース）のスコープ**があります（一次情報: `memory-skills-hooks.md`「`[Learned corrections]`（global + workspace）」）。`[Learned corrections]` という独立したブロックとして注入されます。

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

Lessons が最優先されるのは、「常にこれに従う。デフォルトの振る舞いを上書きする」と明記された独立ブロック `[Learned corrections]` で注入されるためです。

## メモリモード

Crew のセッションには `memory_mode` があり、値は **`persistent`（永続）・`incognito`（匿名）・`temporary`（一時）** の3種です（`history.py` の `INCOGNITO_MEMORY_MODES` として実装。`session-summary.md` にも同様の記述あり）。`incognito`・`temporary` のセッションは「restricted（制限）」として扱われ、統合（consolidation）・レッスン抽出・メモリコンテキストの注入がブロックされます。ただしセッションのJSONL自体（タブ復旧・Gateway再起動時の復元のため）は書き込まれます。

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

**Crew には2つの独立した埋め込み機構があり、対象範囲が異なります。**

| 対象 | 実行方式 |
|------|---------|
| **Memory システム全体**（本ページの6層メモリ）＋アーキテクチャ全般 | **常時オン・in-process**。vendored された `llama-cpp-python` を使用。`memory.embedding_provider` は `llama_cpp` のみを受理し、legacy値 `"ollama"`／`"none"` も**強制的に `llama_cpp` にコアース**されます。外部デーモンは不要・設定で無効化できません |
| **Knowledge Library のみ**（[05_knowledge-library.md](05_knowledge-library.md)） | ローカルの **Ollama** 経由（別の仕組み。詳細は次ページ） |

埋め込みモデルがまだダウンロード中／未取得の間は、メモリはキーワード・FTS検索に緩やかに縮退し、モデルが用意できた時点で自動的に埋め込みが有効になります（再起動不要）。

## Self-evolving（Auto-Improvement）

`auto-improvement.md` が定義する自己改善の仕組みです。**measurement-first**（まず測定してから改善する）の自己改善ループで、メトリクスを校正し既知の改善を検出できることを証明してから keep-or-revert を回し、決定論的なゲートとA/B測定を通った候補のみをドラフトPRにします。

設計原則: **「あらゆる判断は決定論的なPython、あらゆる提案はエージェント。エージェントは自分の成果を採点しない」**。opt-in の builtin App（`auto_improvement`。表示名「Auto-Improvement」）として提供されます。既定では無効です。詳細は [10_apps.md](10_apps.md) を参照してください。

## 未確認事項

- なし。メモリモード用語（persistent/incognito/temporary）は当初 Zenn 記事由来の記述として要検証扱いだったが、`history.py` の `INCOGNITO_MEMORY_MODES` および `session-summary.md` L188 で実在を確認済み

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/memory/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
- Knowledge Library: [05_knowledge-library.md](05_knowledge-library.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

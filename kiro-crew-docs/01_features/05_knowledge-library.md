# Knowledge Library

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（v0.7.0での変更・エージェントの書き込み経路・SELイベント・タイムアウトの扱い）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.7.0での変更）: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 2026-09-25）

---

## 📑 このページの内容

- [概要](#概要)
- [取り込みパイプライン](#取り込みパイプライン)
- [ハイブリッド検索](#ハイブリッド検索)
- [埋め込みは共有in-process機構](#埋め込みは共有in-process機構)
- [重複排除](#重複排除)
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## 概要

Knowledge Library は Kiro Crew 独自のパーソナルナレッジグラフです。ローカルの SQLite バックエンドのコーパスで、ドキュメント（フォルダ・アップロード・artifact・取得したURL）を取り込み、有界のLLMワーカープールでチャンク分割・エンティティ抽出を行い、`local_knowledge_search` MCP tool 経由でハイブリッド検索（FTS5キーワード＋グラフ探索＋任意のベクトル）をLLMに提供します。

**すべての取り込みと検索はホスト内で完結します。** 外部呼び出しは、抽出／URL取得ワーカーのACP LLMターンのみです（埋め込みはMemoryと共有するin-process機構で行われ、外部エンドポイントを呼び出しません。詳細は下記「埋め込みは共有in-process機構」参照）。

[04_memory-and-learning.md](04_memory-and-learning.md) の6層メモリとは**別の仕組み**です。公式ページも「automatic memory layers とは区別される、外部コンテンツのための厳選ドキュメントストア」と明記しています。ダッシュボードのサイドバーにある**組み込みサーフェス**であり、App Store の app ではありません。

## 取り込みパイプライン

```
files / uploads / artifacts / URLs
   → FileReader（読み込み＋テキスト抽出）
   → HeadingAwareChunker（チャンク分割）
   → エンティティ抽出（LLMワーカープール）
   → KnowledgeStore（SQLite: items / entities / graph, FTS5同期）
```

主なコンポーネント:

| コンポーネント | 役割 |
|--------------|------|
| `knowledge/chunker.py` | `HeadingAwareChunker` — テキスト/Markdown/コード/スライドのチャンク分割 |
| `knowledge/embedder.py` | `InProcessEmbedder` — vendored された llama-cpp ランタイムによるin-process埋め込み。**サーバもHTTPホップも介しません**（`knowledge.md` 106行） |
| `knowledge/store.py` | `KnowledgeStore` — SQLiteスキーマ、items/entities/graph、FTS5同期 |
| `knowledge/retrieval.py` | `HybridRetriever` — FTS5＋グラフ＋ベクトル検索をRRFで融合 |
| `knowledge/ingestion.py` | `IngestionPipeline` — 読み込み→チャンク分割→抽出→保存のオーケストレーション |
| `knowledge/dedup.py` | ソース横断の重複排除 |

**エージェントによる書き込み経路（既定オフ）**: エージェントは `knowledge_add_document` MCPツールでドキュメントを追加できます。この経路は**既定で無効**で、`knowledge.auto_add_documents` で有効化します。追加されたドキュメントは「Auto-added」という名前の `agent://` ソースに集約されます。`knowledge.md` は「Nothing registers a file or folder on its own」と記載し、フォルダはユーザーが追加して確認したときだけライブラリに入るとしています（`knowledge.md` v0.7.2 214-234行「§2b」）。artifact の自動取り込みは別の opt-in 設定です（「[v0.3.0での変更](#v030での変更)」参照）。

## ハイブリッド検索

FTS5（キーワード）＋グラフ探索＋任意のベクトル検索を **RRF**（Reciprocal Rank Fusion）で融合します。埋め込みが未取得の場合はベクトル検索の脚が縮退し、キーワード＋グラフのみで動作します。

`local_knowledge_search` MCP tool 経由でLLMに提供され、既定の `limit` は3件、`min_score = 0.012` 未満の結果は除外されます。出力は `redact_exfiltration_urls()` と `redact_credentials()` を通してから返され、呼び出しごとにSELの監査イベント（`success`／`no_results`／`not_configured`／`unknown_source`）が発生します。`unknown_source` は、存在しない `source_id` を指定したときに例外ではなく `knowledge_list_sources` を案内するメッセージを返す場合のイベントです（`knowledge.md` v0.7.2 483-484行）。本サイトの従来の記述は3種のみを挙げていましたが、v0.6.0 の同ファイルにも4種が記載されています。

## 埋め込みは共有in-process機構

> **一次情報内の不整合は v0.6.0 で解消しました。**
>
> v0.6.0 の `docs/system-specs/modules/knowledge.md` は 106行で `InProcessEmbedder` を「embedding **in-process** via the vendored llama-cpp runtime, **no server and no HTTP hop**」と記述し、**同ファイル内に `Ollama` の語は1件も存在しません**（実測0件）。以下4箇所の記述と一致しました。
>
> - `docs/system-specs/modules/memory-skills-hooks.md`: `get_shared_embedder()` は「process-wide singleton, **shared by vector memory AND the knowledge library**」と明記。
> - `docs/guides/install.md`: `memory.embedding_provider` は `llama_cpp` のみを受理し、旧設定値は起動時に強制変換される。
> - `docs/architecture/overview.md`: 「Embeddings are always-on and in-process, computed by vendored llama-cpp-python … there is no external embedding daemon to install or configure」。
> - `config.md` の `KnowledgeConfig`: 「Embedding/retrieval settings live under MemoryConfig (shared via `create_embedder_from_config`)」。
>
> したがって **[04_memory-and-learning.md](04_memory-and-learning.md) の6層メモリと同じ、vendored `llama-cpp-python` による常時オン・in-processの共有シングルトン埋め込み器**（`get_shared_embedder()`）を使います。既定モデルは `qwen3-embedding:0.6b`（`knowledge.md` 132行）で、**モデル名は `名前:タグ` 形式ですが、Ollamaサーバを介するわけではありません**。
>
> **経緯**: v0.4.1 時点では `knowledge.md` 104行が `OllamaEmbedder` —「local embedding via Ollama」と記述し（同ファイル内に `Ollama` が4件）、他の一次情報と食い違っていたため、本サイトは両方を記載していました。v0.6.0 で `knowledge.md` 側が更新され解消しています。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

外部Ollamaデーモンへの依存が実際にない場合、埋め込みが未取得（モデルのバックグラウンドダウンロード中など）の間はベクトル検索の脚が縮退し、キーワード＋グラフのみで動作する点は変わりません。

| 項目 | 値 |
|------|-----|
| 埋め込みモデル（共有GGUF） | `qwen3-embedding-0.6b-q8_0.gguf`（Memoryと共有。`memory-skills-hooks.md`の`ModelDownloadManager`が管理） |
| リクエストごとのタイムアウト | 10秒（`knowledge.embed_timeout_secs` で上書き可）。v0.7.2 の `knowledge.md` 135行は、この値を「Retained for config compatibility」（設定の互換性のために残す）とし、in-process ランタイムにはこの値が制限するリクエスト単位の呼び出しがないと記載しています（v0.6.0 の同ファイル133行は「Per-request embed timeout (s)」と記載） |
| チャンクオーバーラップ | 200 |
| ベクトルRRFの重み | 2.0 |

Knowledge Library の初回検索時には、共有embedderのバックグラウンドGGUFロードがまだ完了していない場合があります。ロードが完了する前は、プローブが即座に `None` を返すため、検索はキーワード＋グラフのみで数ミリ秒で応答します。

## 重複排除

「1つのドキュメント・複数の場所」の原則で管理されます。2つのソースが同じドキュメントを持つ場合、1つの保存済みコピーと `source_locations` 行で管理され、片方が消えても別のソースが保持していれば削除されません。完全一致（ハッシュ）の重複は取り込み時にゲートされ、あいまい一致（埋め込みベース）は事後の掃き掃除で処理されます。

## v0.7.0での変更

v0.7.0 の CHANGELOG と公式 Knowledge ページ（Page updated 2026-09-25）で確認できる変更です。

- **コードの対応拡張子が4言語増えた**: フォルダのスキャンが、これまでスキップしていた **C#（`.cs`）・Kotlin（`.kt`・`.kts`）・Swift（`.swift`）・Scala（`.scala`）** を取り込むようになりました（CHANGELOG 263-264行／公式ページ「Code and document coverage」「Crew 0.7 adds …」）。公式ページは、無視されたファイル・設定したバジェットを超えたファイル・読み込みに失敗したファイルを、成功として数えずに報告すると記載しています
- **検索をソース／namespace に絞れる**: `local_knowledge_search` を1つのソースまたは namespace にスコープできます。公式ページは、識別子を推測せず先にソース一覧で安定した識別子を確認するよう案内し、スコープはキーワードとベクトルの起点の結果を絞るもので、グラフ探索はソースをまたぐ関係を引き続き使えると記載しています（公式ページ／CHANGELOG 265行は「scoped to one namespace」と記載）。仕様書では `source_id` 引数がこれにあたり、ソースの一覧と `source_id` は `knowledge_list_sources` ツールで得られます（`knowledge.md` 484-485行）
- **ライブラリ統計 `kirocrew knowledge stats`**: マイグレーションや修復を実行せずに、ライブラリのソース数・ドキュメント数・アイテム数とソースごとの件数を表示します。`--json` でJSON出力になります（公式ページ「Library statistics」／CHANGELOG 265-267行）。仕様書は読み取り専用であることを境界として明記し、flush・rebuild・repair・reindex のコマンドは並べていません（`knowledge.md` 532-580行）
- **検索結果が `limit` より1件多くなることがある**: キーワード検索で1位の結果は切り捨てから保護されるため、`local_knowledge_search` は `limit + 1` 件を返すことがあり、ツール側で切り詰め直しません（`knowledge.md` 483行）
- **埋め込みのタイムアウト設定の扱い**: 上記「[埋め込みは共有in-process機構](#埋め込みは共有in-process機構)」の表のとおり、`knowledge.embed_timeout_secs` は設定の互換性のために残す値と記載されるようになりました（`knowledge.md` 135行）

> 「検索結果が `limit` より1件多くなることがある」「埋め込みのタイムアウト設定の扱い」の2項目: 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません。

出典: CHANGELOG.md v0.7.0節 263-267行（`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 2026-09-25）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## v0.3.0での変更

### 自動取り込みがopt-in（既定オフ）になった

**Knowledge の自動取り込み（auto-ingest）は既定で無効になりました。** 新規インストールは、ユーザーが明示的に有効化するまで**何も取り込まず、抽出にコストを一切かけません**。設定キーは `knowledge.auto_ingest_artifacts` です（[04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)参照）。

出典: CHANGELOG.md v0.3.0節 24行（`21584ea`）「**Knowledge auto-ingest is opt-in.** A fresh install ingests nothing, and spends nothing on extraction, until you switch it on」。`src/kiro_crew/knowledge/artifact_ingest.py` のdocstringにも「Off by default, opt in with ...」と記載されています。

### 支出に上限が設けられた

Knowledge Libraryの支出（LLM抽出のコスト）が境界づけられました。CHANGELOG（202行）が挙げるのは以下です。

- **sweep budget**（掃き掃除の予算）
- **per-source rate limits and caps**（ソース単位のレート制限と上限）
- **設定可能な抽出モデル**
- **ソース単位のコストの可視化**
- **抽出に失敗したファイルの表示**
- 受け付ける形式に **JSON Lines・NDJSON・Org Mode** が追加

あわせて **lessons が関連度で浮上する**ようになりました（199行）。ライブラリが大きくなっても、該当する古い修正がコンテキストから減衰して消えることがなくなり、lesson は「not this」句を独立したフィールドとして保持します（lessonsの仕組みは [04_memory-and-learning.md](04_memory-and-learning.md) を参照）。

## 未確認事項

- なし。Knowledge Libraryの埋め込み機構は、公式ドキュメント `features/knowledge/`（「Knowledge items are embedded … using the same in-process embedding runtime as Memory」）および `memory-skills-hooks.md`／`install.md`／`overview.md`／`config.md`で「Memoryと共有するin-process機構」と確認済み。v0.4.1 までOllama依存の記述を残していたリポジトリの`docs/system-specs/modules/knowledge.md`（本ページの主要出典）も v0.6.0 で更新され、v0.7.2 の同ファイルでも `Ollama` の語は0件、`InProcessEmbedder` は「no server and no HTTP hop」と記載されている（108行。上記「埋め込みは共有in-process機構」参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/knowledge/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
- メモリシステム: [04_memory-and-learning.md](04_memory-and-learning.md)
- MCPツール一覧: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)

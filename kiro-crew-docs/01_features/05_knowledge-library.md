# Knowledge Library

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [概要](#概要)
- [取り込みパイプライン](#取り込みパイプライン)
- [ハイブリッド検索](#ハイブリッド検索)
- [埋め込みは共有in-process機構](#埋め込みは共有in-process機構)
- [重複排除](#重複排除)
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
| `knowledge/embedder.py` | `OllamaEmbedder` — Ollama経由のローカル埋め込み（下記「埋め込みは共有in-process機構」の注記参照。他の一次情報とは記述が一致しません） |
| `knowledge/store.py` | `KnowledgeStore` — SQLiteスキーマ、items/entities/graph、FTS5同期 |
| `knowledge/retrieval.py` | `HybridRetriever` — FTS5＋グラフ＋ベクトル検索をRRFで融合 |
| `knowledge/ingestion.py` | `IngestionPipeline` — 読み込み→チャンク分割→抽出→保存のオーケストレーション |
| `knowledge/dedup.py` | ソース横断の重複排除 |

## ハイブリッド検索

FTS5（キーワード）＋グラフ探索＋任意のベクトル検索を **RRF**（Reciprocal Rank Fusion）で融合します。埋め込みが未取得の場合はベクトル検索の脚が縮退し、キーワード＋グラフのみで動作します。

`local_knowledge_search` MCP tool 経由でLLMに提供され、既定の `limit` は3件、`min_score = 0.012` 未満の結果は除外されます。出力は `redact_exfiltration_urls()` と `redact_credentials()` を通してから返され、呼び出しごとにSELの監査イベント（`success`／`no_results`／`not_configured`）が発生します。

## 埋め込みは共有in-process機構

> **一次情報内に不整合があります（未解消）。**
>
> - `docs/system-specs/modules/knowledge.md`（本ページの主要出典）は、Knowledge Libraryが「ローカルのOllama埋め込みエンドポイント」を使う `OllamaEmbedder`（`knowledge/embedder.py`）に依存すると記述しています（既定モデル: `qwen3-embedding:0.6b`）。
> - 一方、以下4箇所は揃って「Memory と Knowledge Library は同じ埋め込み機構を共有する」と記述しています。
>   - `docs/system-specs/modules/memory-skills-hooks.md`: `get_shared_embedder()` は「process-wide singleton, **shared by vector memory AND the knowledge library**」と明記。
>   - `docs/guides/install.md`: `memory.embedding_provider` は `llama_cpp` のみを受理し、旧設定値は起動時に強制変換される。
>   - `docs/architecture/overview.md`: 「Embeddings are always-on and in-process, computed by vendored llama-cpp-python … there is no external embedding daemon to install or configure」。
>   - `config.md` の `KnowledgeConfig`: 「Embedding/retrieval settings live under MemoryConfig (shared via `create_embedder_from_config`)」。
>
> 本サイトは、多数一致し新設計（Ollama依存の削除）を裏付ける後者4箇所を採用します。すなわち、**[04_memory-and-learning.md](04_memory-and-learning.md) の6層メモリと同じ、vendored `llama-cpp-python` による常時オン・in-processの共有シングルトン埋め込み器**（`get_shared_embedder()`）を使うと理解しています。`knowledge.md`のOllama記述は、リポジトリ内で更新が反映されていない可能性がありますが、確定はできません。

外部Ollamaデーモンへの依存が実際にない場合、埋め込みが未取得（モデルのバックグラウンドダウンロード中など）の間はベクトル検索の脚が縮退し、キーワード＋グラフのみで動作する点は変わりません。

| 項目 | 値 |
|------|-----|
| 埋め込みモデル（共有GGUF） | `qwen3-embedding-0.6b-q8_0.gguf`（Memoryと共有。`memory-skills-hooks.md`の`ModelDownloadManager`が管理） |
| リクエストごとのタイムアウト | 10秒（`knowledge.embed_timeout_secs` で上書き可） |
| チャンクオーバーラップ | 200 |
| ベクトルRRFの重み | 2.0 |

Knowledge Library の初回検索時には、共有embedderのバックグラウンドGGUFロードがまだ完了していない場合があります。ロードが完了する前は、プローブが即座に `None` を返すため、検索はキーワード＋グラフのみで数ミリ秒で応答します。

## 重複排除

「1つのドキュメント・複数の場所」の原則で管理されます。2つのソースが同じドキュメントを持つ場合、1つの保存済みコピーと `source_locations` 行で管理され、片方が消えても別のソースが保持していれば削除されません。完全一致（ハッシュ）の重複は取り込み時にゲートされ、あいまい一致（埋め込みベース）は事後の掃き掃除で処理されます。

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

- なし。Knowledge Libraryの埋め込み機構は、公式ドキュメント `features/knowledge/`（「Knowledge items are embedded … using the same in-process embedding runtime as Memory」）および `memory-skills-hooks.md`／`install.md`／`overview.md`／`config.md`で「Memoryと共有するin-process機構」と確認済み。リポジトリの`docs/system-specs/modules/knowledge.md`（本ページの主要出典）のみ、更新が反映されていないOllama依存の記述を残す（上記「埋め込みは共有in-process機構」参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/knowledge/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
- メモリシステム: [04_memory-and-learning.md](04_memory-and-learning.md)
- MCPツール一覧: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)

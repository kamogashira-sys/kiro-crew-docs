# Knowledge Library

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [概要](#概要)
- [取り込みパイプライン](#取り込みパイプライン)
- [ハイブリッド検索](#ハイブリッド検索)
- [埋め込みはOllama経由](#埋め込みはollama経由)
- [重複排除](#重複排除)
- [未確認事項](#未確認事項)

---

## 概要

Knowledge Library は Kiro Crew 独自のパーソナルナレッジグラフです。ローカルの SQLite バックエンドのコーパスで、ドキュメント（フォルダ・アップロード・artifact・取得したURL）を取り込み、有界のLLMワーカープールでチャンク分割・エンティティ抽出を行い、`local_knowledge_search` MCP tool 経由でハイブリッド検索（FTS5キーワード＋グラフ探索＋任意のベクトル）をLLMに提供します。

**すべての取り込みと検索はホスト内で完結します。** 外部呼び出しは、抽出／URL取得ワーカーのACP LLMターンと、ローカルのOllama埋め込みエンドポイントのみです。

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
| `knowledge/embedder.py` | `OllamaEmbedder` — Ollama経由のローカル埋め込み |
| `knowledge/store.py` | `KnowledgeStore` — SQLiteスキーマ、items/entities/graph、FTS5同期 |
| `knowledge/retrieval.py` | `HybridRetriever` — FTS5＋グラフ＋ベクトル検索をRRFで融合 |
| `knowledge/ingestion.py` | `IngestionPipeline` — 読み込み→チャンク分割→抽出→保存のオーケストレーション |
| `knowledge/dedup.py` | ソース横断の重複排除 |

## ハイブリッド検索

FTS5（キーワード）＋グラフ探索＋任意のベクトル検索を **RRF**（Reciprocal Rank Fusion）で融合します。埋め込みが未取得の場合はベクトル検索の脚が縮退し、キーワード＋グラフのみで動作します。

`local_knowledge_search` MCP tool 経由でLLMに提供され、既定の `limit` は3件、`min_score = 0.012` 未満の結果は除外されます。出力は `redact_exfiltration_urls()` と `redact_credentials()` を通してから返され、呼び出しごとにSELの監査イベント（`success`／`no_results`／`not_configured`）が発生します。

## 埋め込みはOllama経由

> **重要: メモリシステムとは異なる埋め込み機構です。**
>
> [04_memory-and-learning.md](04_memory-and-learning.md) の6層メモリは vendored `llama-cpp-python` による常時オン・in-process の埋め込みですが、**Knowledge Library のみ、ローカルのOllamaエンドポイントを使う `OllamaEmbedder` に委譲します**（既定モデル: `qwen3-embedding:0.6b`）。

| 項目 | 値 |
|------|-----|
| 埋め込みモデル | `qwen3-embedding:0.6b`（`DEFAULT_MODEL`） |
| リクエストごとのタイムアウト | 10秒（`knowledge.embed_timeout_secs` で上書き可） |
| チャンクトークンサイズ・オーバーラップ | チャンクオーバーラップ200 |
| ベクトルRRFの重み | 2.0 |

Knowledge Library の可用性確認プローブは、初回検索時にバックグラウンドでGGUFロードをトリガーします（Ollamaの可用性確認）。プローブが即座に `None` を返す間は、検索はキーワードのみで数ミリ秒で応答します。

## 重複排除

「1つのドキュメント・複数の場所」の原則で管理されます。2つのソースが同じドキュメントを持つ場合、1つの保存済みコピーと `source_locations` 行で管理され、片方が消えても別のソースが保持していれば削除されません。完全一致（ハッシュ）の重複は取り込み時にゲートされ、あいまい一致（埋め込みベース）は事後の掃き掃除で処理されます。

## 未確認事項

- なし（本ページの記述は公式 `features/knowledge/` と `modules/knowledge.md` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/knowledge/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
- メモリシステム: [04_memory-and-learning.md](04_memory-and-learning.md)
- MCPツール一覧: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)

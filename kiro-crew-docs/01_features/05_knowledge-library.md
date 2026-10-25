# Knowledge Library

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 2026-09-25）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.9.0・v0.8.0での変更）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.7.0での変更・エージェントの書き込み経路・SELイベント・タイムアウトの扱い）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。v0.7.0 当時の行番号は v0.7.2 / commit `c67c506`）
**出典**（v0.7.0での変更）: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 2026-09-25）

---

## 📑 このページの内容

- [概要](#概要)
- [取り込みパイプライン](#取り込みパイプライン)
- [ハイブリッド検索](#ハイブリッド検索)
- [埋め込みは共有in-process機構](#埋め込みは共有in-process機構)
- [重複排除](#重複排除)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
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
| `knowledge/embedder.py` | `InProcessEmbedder` — vendored された llama-cpp ランタイムによるin-process埋め込み。**サーバもHTTPホップも介しません**（`knowledge.md` 122行。v0.6.0 では106行） |
| `knowledge/store.py` | `KnowledgeStore` — SQLiteスキーマ、items/entities/graph、FTS5同期 |
| `knowledge/retrieval.py` | `HybridRetriever` — FTS5＋グラフ＋ベクトル検索をRRFで融合 |
| `knowledge/ingestion.py` | `IngestionPipeline` — 読み込み→チャンク分割→抽出→保存のオーケストレーション |
| `knowledge/dedup.py` | ソース横断の重複排除 |

**エージェントによる書き込み経路（既定オフ）**: エージェントは `knowledge_add_document` MCPツールでドキュメントを追加できます。この経路は**既定で無効**で、`knowledge.auto_add_documents` で有効化します。追加されたドキュメントは「Auto-added」という名前の `agent://` ソースに集約されます。`knowledge.md` は「Nothing registers a file or folder on its own」と記載し、フォルダはユーザーが追加して確認したときだけライブラリに入るとしています（`knowledge.md` 235-262行「§2b」。v0.7.2 では214-234行）。artifact の自動取り込みは別の opt-in 設定です（「[v0.3.0での変更](#v030での変更)」参照）。

## ハイブリッド検索

FTS5（キーワード）＋グラフ探索＋任意のベクトル検索を **RRF**（Reciprocal Rank Fusion）で融合します。埋め込みが未取得の場合はベクトル検索の脚が縮退し、キーワード＋グラフのみで動作します。

`local_knowledge_search` MCP tool 経由でLLMに提供され、既定の `limit` は3件、`min_score = 0.012` 未満の結果は除外されます。出力は `redact_exfiltration_urls()` と `redact_credentials()` を通してから返され、呼び出しごとにSELの監査イベント（`success`／`no_results`／`not_configured`／`unknown_source`）が発生します。`unknown_source` は、存在しない `source_id` を指定したときに例外ではなく `knowledge_list_sources` を案内するメッセージを返す場合のイベントです（`knowledge.md` 504行。v0.7.2 では483-484行）。本サイトの従来の記述は3種のみを挙げていましたが、v0.6.0 の同ファイルにも4種が記載されています。

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
> したがって **[04_memory-and-learning.md](04_memory-and-learning.md) の6層メモリと同じ、vendored `llama-cpp-python` による常時オン・in-processの共有シングルトン埋め込み器**（`get_shared_embedder()`）を使います。既定モデルは `qwen3-embedding:0.6b`（`knowledge.md` 149行。v0.6.0 では132行）で、**モデル名は `名前:タグ` 形式ですが、Ollamaサーバを介するわけではありません**。
>
> **経緯**: v0.4.1 時点では `knowledge.md` 104行が `OllamaEmbedder` —「local embedding via Ollama」と記述し（同ファイル内に `Ollama` が4件）、他の一次情報と食い違っていたため、本サイトは両方を記載していました。v0.6.0 で `knowledge.md` 側が更新され解消しています。
>
> **v0.9.0 での再確認**: v0.9.0 の `knowledge.md` でも `Ollama` の語は0件です。`InProcessEmbedder` は122行に記載されています。`config.md` の `KnowledgeConfig` は、埋め込みと検索の設定が `MemoryConfig` の下にあり、`create_embedder_from_config` で共有されると記載しています（2717-2719行）。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0。v0.9.0 の再確認は 2026-10-25 / commit `99e6253` / 版 v0.9.0）

外部Ollamaデーモンへの依存が実際にない場合、埋め込みが未取得（モデルのバックグラウンドダウンロード中など）の間はベクトル検索の脚が縮退し、キーワード＋グラフのみで動作する点は変わりません。

| 項目 | 値 |
|------|-----|
| 埋め込みモデル（共有GGUF） | `qwen3-embedding-0.6b-q8_0.gguf`（Memoryと共有。`memory-skills-hooks.md`の`ModelDownloadManager`が管理） |
| リクエストごとのタイムアウト | 10秒（`knowledge.embed_timeout_secs` で上書き可）。v0.9.0 の `knowledge.md` 150行は、この値を「Retained for config compatibility」（設定の互換性のために残す）とし、in-process ランタイムにはこの値が制限するリクエスト単位の呼び出しがないと記載しています（v0.7.2 では135行、v0.6.0 の同ファイル133行は「Per-request embed timeout (s)」と記載） |
| チャンクオーバーラップ | 200 |
| ベクトルRRFの重み | 2.0 |

Knowledge Library の初回検索時には、共有embedderのバックグラウンドGGUFロードがまだ完了していない場合があります。ロードが完了する前は、プローブが即座に `None` を返すため、検索はキーワード＋グラフのみで数ミリ秒で応答します。

## 重複排除

「1つのドキュメント・複数の場所」の原則で管理されます。2つのソースが同じドキュメントを持つ場合、1つの保存済みコピーと `source_locations` 行で管理され、片方が消えても別のソースが保持していれば削除されません。完全一致（ハッシュ）の重複は取り込み時にゲートされ、あいまい一致（埋め込みベース）は事後の掃き掃除で処理されます。

## v0.9.0での変更

v0.9.0 の CHANGELOG（v0.9.0節）は Knowledge Library の変更を説明していません。公式 Knowledge ページ（Page updated 2026-09-25）も v0.7.2 時点から変わっていません。次の項目は、本内容が v0.9.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。次のうち、`knowledge.extraction_effort`・ダッシュボードの設定コントロール・`knowledge.pool_idle_ttl_secs`・ベクトル検索不可時の注記・変更系ルートの owner 確認は、v0.8.0 タグの仕様書に記載がなく、v0.9.0 タグで確認したものです。`knowledge.extraction_pool_size` と、抽出の effort が `agent.role_efforts.background` から独立しているという方針（v0.8.0 では `high` 固定）は、v0.8.0 タグの仕様書（`knowledge.md` 19-27行）にも記載があります。いずれも公式ドキュメントには記載がありません。

### 抽出の effort とワーカープール

- **`knowledge.extraction_effort`**: エンティティ抽出ワーカーの推論 effort を選びます。未設定・空文字・無効な値は、従来どおり `high`（`DEFAULT_EXTRACTION_EFFORT`）です。この値は `agent.role_efforts.background` とは独立しています（独立の方針は v0.8.0 タグの仕様書にもあり、そこでは `high` 固定でした。v0.9.0 でキーによる選択になりました）。URL 取得プール（ワーカー1つ）は effort を明示せず、プロバイダの既定のままです（`knowledge.md` 17-49行）
- **ダッシュボードからの変更**: Knowledge タブの設定で、モデル・extraction effort・プールサイズを変更できます。effort の変更はワーカーの再起動で反映され、プールサイズは次のアイドル境界で反映されます（`knowledge.md` 17-49行）。`config.md` 2534-2545行は、`knowledge.extraction_effort` を、再起動が必要なキーの一覧（`requires_restart()` から生成）に載せています
- **`knowledge.extraction_pool_size`**（v0.8.0 タグの仕様書にも記載あり）: 抽出プールだけの大きさを決めます。URL 取得プールと auto_research のプールは変わりません。仕様書の定数表は、プールのワーカー数の既定値（`DEFAULT_POOL_SIZE`）を3としています（`knowledge.md` 138行）。`knowledge.extraction_pool_size` 自体の既定値を明記した行は確認できません
- **`knowledge.pool_idle_ttl_secs`**（既定 300秒、`0` で無効）: ワーカーが1つも使われない状態がこの秒数続くと、プールをゼロまで縮小し、次の取得で再び起動します。設定の書き込みは `reconfigure()` を通じて稼働中のプールに届き、新しい TTL はすぐに、新しいプールサイズは次のアイドル境界で反映されます（`knowledge.md` 426行）

### 検索の出力と権限

- **ベクトル検索が使えないとき**: `local_knowledge_search` の出力は、結果なしのメッセージも含めて末尾に ` (vector path unavailable; keyword results only)` が付きます。埋め込み器が使えないという判定はキャッシュされ、`NEGATIVE_CACHE_TTL`（300秒）の後に再確認されます（`knowledge.md` 505行）
- **変更系ルートの owner 確認**: `/api/knowledge` の変更系ルート17本は、呼び出しがダッシュボードのユーザーからのときに、ダッシュボードの owner であることを確認します。それ以外の呼び出し元（アプリ token、`X-Internal-Secret` を持つ loopback の呼び出し）はこの確認を通り、それぞれ既存の制御（アプリ token はマニフェストで宣言したパスへの制限）の下に置かれます（`knowledge.md` 519-524行）

出典: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.8.0での変更

v0.8.0 の CHANGELOG（v0.8.0節）と v0.9.0 タグの仕様書で確認できる、取り込みの変更です。公式 Knowledge ページ（Page updated 2026-09-25）には記載がありません。

- **AsciiDoc が取り込み対象に加わった**: `.adoc` と `.asciidoc` を読みます。`.asc` は PGP armor の拡張子でもあるため除外されています（CHANGELOG v0.8.0節 577-578行、`knowledge.md` 164-170行）
- **Word 文書の表**: Word 文書（`.docx`）は本文に加えて、表のセル、入れ子の表、content-control の包みの中身を文書順に取り込みます。表のセルにだけ書かれた事実も検索で見つかります（CHANGELOG v0.8.0節 578行、`knowledge.md` 188行）
- **PDF の読み取り**: PDF は、メモリ（`RLIMIT_AS` 1 GiB）と CPU 時間（`RLIMIT_CPU` 60秒）を制限した子プロセス（`kiro_crew.pdf_extract`）で読みます。文字数・ページ数・実時間に上限があり、上限で切り詰めたときは `truncated: True` になります（`knowledge.md` 179-183行）
- **PDF が検索できない不具合の修正**: CHANGELOG v0.8.0節は、ファイルブラウザと Knowledge の取り込みの両方で PDF が再び検索できるようになったと記載しています（636-637行）。また Linux では、Gateway 自身のメモリが1 GB を超えたことがあると、抽出ワーカーの watchdog が Gateway のピーク値を測っていたため、すべての PDF が読めなくなっていました。これも修正されています（640-642行）

出典: CHANGELOG.md v0.8.0節 577-578行・636-642行（`99e6253`）。
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.7.0での変更

v0.7.0 の CHANGELOG と公式 Knowledge ページ（Page updated 2026-09-25）で確認できる変更です。

- **コードの対応拡張子が4言語増えた**: フォルダのスキャンが、これまでスキップしていた **C#（`.cs`）・Kotlin（`.kt`・`.kts`）・Swift（`.swift`）・Scala（`.scala`）** を取り込むようになりました（CHANGELOG 263-264行／公式ページ「Code and document coverage」「Crew 0.7 adds …」）。公式ページは、無視されたファイル・設定したバジェットを超えたファイル・読み込みに失敗したファイルを、成功として数えずに報告すると記載しています
- **検索をソース／namespace に絞れる**: `local_knowledge_search` を1つのソースまたは namespace にスコープできます。公式ページは、識別子を推測せず先にソース一覧で安定した識別子を確認するよう案内し、スコープはキーワードとベクトルの起点の結果を絞るもので、グラフ探索はソースをまたぐ関係を引き続き使えると記載しています（公式ページ／CHANGELOG 265行は「scoped to one namespace」と記載）。仕様書では `source_id` 引数がこれにあたり、ソースの一覧と `source_id` は `knowledge_list_sources` ツールで得られます（`knowledge.md` 506-507行。v0.7.2 では484-485行）
- **ライブラリ統計 `kirocrew knowledge stats`**: マイグレーションや修復を実行せずに、ライブラリのソース数・ドキュメント数・アイテム数とソースごとの件数を表示します。`--json` でJSON出力になります（公式ページ「Library statistics」／CHANGELOG 265-267行）。仕様書は読み取り専用であることを境界として明記し、flush・rebuild・repair・reindex のコマンドは並べていません（`knowledge.md` 508行・561-620行。v0.7.2 では532-580行）
- **検索結果が `limit` より1件多くなることがある**: キーワード検索で1位の結果は切り捨てから保護されるため、`local_knowledge_search` は `limit + 1` 件を返すことがあり、ツール側で切り詰め直しません（`knowledge.md` 504行。v0.7.2 では483行）
- **埋め込みのタイムアウト設定の扱い**: 上記「[埋め込みは共有in-process機構](#埋め込みは共有in-process機構)」の表のとおり、`knowledge.embed_timeout_secs` は設定の互換性のために残す値と記載されるようになりました（`knowledge.md` 150行。v0.7.2 では135行）

> 「検索結果が `limit` より1件多くなることがある」「埋め込みのタイムアウト設定の扱い」の2項目: 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません。

出典: CHANGELOG.md v0.7.0節 263-267行（`c67c506`）。
**出典**: <https://kiro.dev/docs/crew/features/knowledge/>（Page updated 2026-09-25）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

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

- `knowledge.extraction_effort`・`knowledge.pool_idle_ttl_secs` は、公式 Knowledge ページと CHANGELOG（v0.8.0・v0.9.0）に記載がなく、v0.9.0 タグの仕様書だけが記載しています。`knowledge.extraction_pool_size` の既定値は仕様書で確認できません（「[v0.9.0での変更](#v090での変更)」参照）
- Knowledge Library の埋め込み機構について、一次情報の食い違いはありません。Knowledgeの埋め込み機構は、公式ドキュメント `features/knowledge/`（「Knowledge items are embedded … using the same in-process embedding runtime as Memory」）および `memory-skills-hooks.md`／`install.md`／`overview.md`／`config.md`で「Memoryと共有するin-process機構」と確認済み。v0.4.1 までOllama依存の記述を残していたリポジトリの`docs/system-specs/modules/knowledge.md`（本ページの主要出典）も v0.6.0 で更新され、v0.9.0 の同ファイルでも `Ollama` の語は0件、`InProcessEmbedder` は「no server and no HTTP hop」と記載されている（122行。v0.7.2 では108行。上記「埋め込みは共有in-process機構」参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/knowledge/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/knowledge.md>
- メモリシステム: [04_memory-and-learning.md](04_memory-and-learning.md)
- MCPツール一覧: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)

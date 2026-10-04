# 上限値・既定値の一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: 各ページに記載の一次情報を集約（詳細出典は各節を参照。主要な一次情報は <https://kiro.dev/docs/crew/> と <https://github.com/kirodotdev/KiroCrew>）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

---

## 📑 このページの内容

- [リポジトリ・公式サイト](#リポジトリ公式サイト)
- [セキュリティ](#セキュリティ)
- [メモリ](#メモリ)
- [自律実行](#自律実行)
- [App・インターフェース](#appインターフェース)
- [テレメトリ](#テレメトリ)
- [未確定（両併記）](#未確定両併記)
- [未確認事項](#未確認事項)

---

## リポジトリ・公式サイト

| 項目 | 値 |
|------|-----|
| 公式docsのcrewページ数 | **49** |
| リポジトリ`docs/`配下ファイル数 | **281**（v0.7.2タグ。v0.6.0タグは230） |
| リポジトリ`docs/system-specs/`配下ファイル数 | **104**（`.md` は101。v0.6.0タグは88） |
| 最新安定版 | **v0.7.2** |
| 安定版リリース数 | **13** |
| 総リリース数（プレリリース含む） | **77**（プレリリース64件。2026-10-04 取得時点の GitHub Releases 実測） |
| CHANGELOG.mdの版節数 | **11** |
| ライセンス | **Apache-2.0**（本サイトはMIT） |

> **`[Unreleased]` 節について**: 固定参照時点（版 v0.7.2）の `CHANGELOG.md` に `## [Unreleased]` 節は**存在しません**（実測0件）。`docs/build/changelog.md` 23行は「There is no `## [Unreleased]` section, and the gate refuses one.」と明記し、gateの実体は `scripts/check_changelog_history.py` です。したがって上の版節数11に `[Unreleased]` は含まれません。**節が復活した場合は出典から除外する方針を維持します**（[02_update/02_release-policy.md](../02_update/02_release-policy.md)参照）。
>
> **プレリリースの連番について**: 最大番号は件数と一致しません（例: `v0.5.0-insider.4`・`v0.6.0-insider.5` が欠番。v0.7.x 系にも欠番あり）。詳細は [02_update/02_release-policy.md](../02_update/02_release-policy.md) を参照してください。

## セキュリティ

| 項目 | 値 |
|------|-----|
| 拒否コマンドルール件数 | **137** |
| サンドボックス: 出典3系統で値域が食い違う（裁定しない） | ① `README.md` 385行: **3モード**（Standard / strict / off）／② `config.md` 940行: `agent.sandbox` は既定 **`auto`**・**`off`** でスキップ（`strict` の記載なし）／③ `security-deep-dive.md` 107-112行: 内部ティアは **`standard`（`auto`の解決先）／`cc`／`strict`／`off` の4種**で「**運用者が `agent.sandbox` に書く値ではない**」と明記。ガバナンスの `sandbox.min_level` 順序尺度は `("off", "standard", "cc", "strict")` で要求モードを**上へ**クランプ（[09_security.md](../01_features/09_security.md)参照） |
| 既知のギャップ | **7点**（＋プラットフォーム依存のリソース上限。7点目「同一ユーザーによるランチャの自己汚染は受容・非防御」は v0.7.0 で追加。[09_security.md](../01_features/09_security.md)参照） |

## メモリ

| 項目 | 値 |
|------|-----|
| メモリ層数 | リポジトリ資料: **6層**（Preferences/Projects/Recent history/Semantic/Episodic/Lessons）＋横断帯（request auth / Slack owner lock / governance ceiling / SEL audit）。公式docs: **8機構**。単一の層数には裁定しない |
| コンテキストバジェット | **33,000文字**（リポジトリ `_CONTEXT_BUDGET_BASE` の固定値。v0.7.0〜。v0.6.0以前は165,000文字）。⚠️ 公式 memory ページの図は「Context Window (~55K tokens)」のままで、**出典間で食い違います**（下記「[未確定（両併記）](#未確定両併記)」） |
| Preferencesキャップ | 4,250文字（公式ページ値。v0.6.0のリポジトリでは fraction 由来の4,290文字=`int(165,000×2.6%)`） |
| Projectsキャップ | 6,400文字（公式ページ値。v0.6.0のリポジトリでは6,435文字=`int(165,000×3.9%)`） |
| Recent historyキャップ | 26,600文字（公式ページ値。v0.6.0のリポジトリでは26,400文字=`int(165,000×16%)`） |
| Semantic memoryキャップ | 12,000文字（公式ページ値。v0.6.0のリポジトリでは12,705文字=`int(165,000×7.7%)`） |
| Episodic memoryキャップ | 3,000文字・上位8件（`_EPISODIC_INJECT_CAP`。基礎キャップの`_EPISODIC_MEMORY_CAP`はSemantic memoryと同じ7.7%=12,705文字だが、実際の注入時はこの3,000文字にさらにクランプされる） |
| Lessonsキャップ | 37,250文字・最大50件（公式ページ値）。v0.7.2のリポジトリでは起動時ルールブロックの上限 `_LESSONS_STARTUP_CAP` = **37,000文字**（33,000文字の割合ではない独立値。「165,000 × 0.226 = 37,290」の水準を戻したと明記）。`applies: on_topic` の lesson は別ブロック `[Learned experience]`（基準の5%）に入る |

> **v0.7.0 以降のリポジトリのキャップについて**: `memory-skills-hooks.md` 4582行（`c67c506`）は、`_CONTEXT_BUDGET_BASE` を「a fixed 33,000-character Crew background admission allowance」と説明し、モデルのウィンドウサイズや `skills.lazy_load` で拡大しないと記述しています。lessons の予算は「22.6% of the 33,000 base」（同2782行）です。v0.6.0 で記載していた 165,000 文字基準の fraction 由来値（4,290／6,435／26,400／12,705／37,290）は v0.7.2 の仕様書にはありません。公式 memory ページ（Page updated 2026-08-04、v0.6.0 とバイト同一）のキャップ値は変わっていません。**本サイトはどちらが正かを裁定しません。**
| 履歴減衰の段数 | **5段**（0-13日／14-60日／61-180日／181-364日／365日以降） |
| Consolidationトリガー（好み/プロジェクト） | **30メッセージ** |
| Consolidationトリガー（履歴/レッスン） | **3時間アイドル** |
| 埋め込み（Memory・Knowledge Library共有） | vendored llama-cpp-python（常時オン・in-process。`llama_cpp`固定。`get_shared_embedder()`でMemoryとKnowledge Libraryが共有）。**v0.6.0で `knowledge.md` も `InProcessEmbedder` に更新され、Ollama依存の旧記述は解消**。詳細: [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md) |

## 自律実行

| 項目 | 値 |
|------|-----|
| Cron: `--timeout-secs` 既定 | 1800秒 |
| Cron `--every` の一般下限 | **未確認**（60秒はimport取込下限およびHeartbeat間隔として確認済みだが、一般的な`--every`下限としては裁定しない） |
| Cronインポート時の最小間隔 | 60秒以上（整数秒。同ファイル299行。他エージェントからのインポート時の検証ルール） |
| **job（スケジュールジョブ）の時間予算** | **最大24時間**（v0.3.0で追加。従来の固定30分上限を置き換え。**下記「Subagent 1件あたりのハードタイムアウト」とは別項目**） |
| **job のinstructions文字数** | **50,000文字**（v0.3.0で追加） |
| TaskRunnerの構造 | オーケストレータ＋4ヘルパーモジュール |
| **無人 auto-run plan の時間予算** | **7200秒（2時間）**（v0.6.0で追加。`orchestrator.max_plan_duration_seconds`。ステージ境界でチェック・75%で1回警告・`0`で無効化。**stage-gatedな planは打ち切られない**） |
| **チャット1ターンの上限** | **14400秒（4時間）**（`agent.chat_turn_timeout_secs`。v0.5.0以前は7200秒。クランプ300〜86400秒・無効化不可） |
| Subagent 1件あたりのハードタイムアウト | **10800秒（3時間）**（`agent.subagent_timeout_secs`。**v0.5.0以前は1800秒＝30分の固定値**。クランプ60〜86400秒。**ダッシュボードからは設定不可**） |
| Subagentの外側キャップ | 1200秒（20分。`_ON_DONE_TIMEOUT`） |
| Subagentの内側キャップ | 900秒（15分。`INJECTION_TIMEOUT`） |
| Subagent 1件あたりのツール呼び出し予算 | 既定 **1000**（`agent.subagent_max_turns`。**v0.7.0で100→1000**、`config.md` 407・1849行）。ロード時クランプの上限は1000（v0.5.0以前は200）。キー未設定なら自動で1000に追従し、保存済みの値は100でも保持される（[02_configuration-keys.md](02_configuration-keys.md)参照） |
| Subagent並行数の下限 | 3 |
| **メモリ上限の適用範囲** | **全同時エージェントの合計**（v0.3.0で変更。小さなspawnを多数行ってホストを食い潰すことができなくなった）。合計値は `resource_limits.max_total_memory_mb`／`resource_limits.max_total_processes` で上書き |
| Heartbeatの既定間隔 | 60秒 |
| Heartbeatタスクのタイムアウト | 1800秒（30分。v0.6.0でも変更なし） |

> **⚠️ 「24時間」と各タイムアウトを混同しないこと**: v0.3.0で追加された**最大24時間はjob（スケジュールジョブ）の時間予算**です。CHANGELOGの「replacing one fixed thirty-minute cap」はjob側の従来上限を指します。
>
> **「1800秒（30分）」は複数の別系統に登場します。v0.6.0で変わったものと変わらないものを区別してください。**
>
> | 系統 | v0.6.0での値 | 出典 |
> |---|---|---|
> | Subagent 1件あたりのハードタイムアウト | **10800秒（3時間）に変更** | `subagent.md` 14行（`_TIMEOUT_SECS`）・`resource-protection.md` 14行 |
> | Cron `--timeout-secs` 既定（`_JOB_TIMEOUT_SECS`） | 1800秒（変更なし） | `resource-protection.md` 20行 |
> | Heartbeatタスク（`HEARTBEAT_TASK_TIMEOUT_SECS`） | 1800秒（変更なし） | `heartbeat.md` 61・142行 |
> | Warm Pool の TTL（`session.pool_ttl_secs`） | 1800秒（変更なし） | `overview.md` 281行 |
>
> 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) を参照してください。

## App・インターフェース

| 項目 | 値 |
|------|-----|
| builtin App数 | **[要検証]**。v0.4.1の`src/`解析は未承認のため、旧値を実測値として追認しない |
| メッセージングチャネル数 | v0.7.2時点: 公式docsの設定ガイドページ **7**（一覧は10件）、README **10**、`messaging.md` は同一ファイル内で「eleven」「ten」「nine of ten」が混在。出典間の総数は裁定しない（[01_features/11_interfaces.md](../01_features/11_interfaces.md)参照） |
| インポート対応ソース数 | **5**（組み込み: Claude Code/Codex/Gemini/OpenClaw/Hermes。ほかにエディションが登録したソース。**本サイトは以前 MeshClaw と記載していましたが、v0.4.1 以降の仕様書は `gemini`**。[01_features/14_migration-import.md](../01_features/14_migration-import.md)参照） |
| インポートカテゴリ数 | **8** |
| Gatewayの既定ポート | **5476**（`KIROCREW_PORT`で変更可） |

## テレメトリ

**2つの別系統があります。混同しないでください**（[03_deployment/06_telemetry-and-privacy.md](../03_deployment/06_telemetry-and-privacy.md)参照）。

### ①匿名利用テレメトリ

| 項目 | 値 |
|------|-----|
| 既定状態 | オン |
| 送信フィールド数 | **5**（旧仕様は9） |
| 無効化の経路数 | 3（Settings/CLI/環境変数） |

### ②メトリクス／OTLPエクスポート

| 項目 | 値 |
|------|-----|
| 既定状態 | **オフ**（`telemetry.enabled: false`） |
| 送出先の既定 | **なし**（`telemetry.otlp_endpoint` は空。ローカルJSONLシンクのみ） |
| 送出に必要なもの | エンドポイント設定**と** `kirocrew[otlp]` extra のインストールの**両方** |

## 未確定（両併記）

出典間で値が食い違うため、**本サイトは裁定しません**。

| 項目 | 出典A | 出典B |
|------|-------|-------|
| v0.7.2の日付 | CHANGELOG.md: 2026-09-28 | Release公開日: 2026-09-29 |
| v0.7.1の日付 | CHANGELOG.md: 2026-09-24 | Release公開日: 2026-09-25 |
| v0.7.0の日付 | CHANGELOG.md: 2026-09-15 | Release公開日: 2026-09-24 |
| v0.6.0の日付 | CHANGELOG.md: 2026-09-05 | Release公開日: 2026-09-11 |
| v0.5.0の日付 | CHANGELOG.md: 2026-08-29 | Release公開日: 2026-09-05 |
| v0.4.1の日付 | CHANGELOG.mdの版日付 | Release公開日: 2026-08-29 |
| v0.4.0の日付 | CHANGELOG.mdの版日付 | Release公開日: 2026-08-27 |
| v0.3.0の日付 | CHANGELOG.md: 2026-08-17 | Release公開日: 2026-08-21 |
| v0.2.0の日付 | CHANGELOG.md: 2026-08-09 | Release公開日: 2026-08-10 |
| Subagent自動サイジング上限（`agent.subagent_auto_max`） | `subagent.md`: 32 | `config.md`: 16 |
| Subagent並行数の既定（`agent.max_subagents`） | `subagent.md`: 0（自動サイジング） | `config.md`: 3 |
| サンドボックスの呼称 | 公式docs: `auto` | README・内部ティア: `standard` |
| v0.5.0の破壊的変更の件数 | CHANGELOG.md `[0.5.0]` 節: **12件** | GitHub Release 本文: **5件**（"Five changes" と明記） |
| コンテキストバジェット | 公式 memory ページ: 図「Context Window (~55K tokens)」（v0.6.0 と同一） | `memory-skills-hooks.md` 4582行: `_CONTEXT_BUDGET_BASE` = 33,000文字の固定値（v0.7.0〜） |
| Agent Backends の選択肢 | 公式ページ: **7種**（Kiro CLI/Claude Code/KAS/Codex/OpenCode/Pi/goose。v0.6.0時点は4種） | `claude-code-provider.md`: `BASELINE_SELECTABLE_BACKENDS` は3件（KIRO/CLAUDE/KAS。v0.7.2でも同じ） |
| Windowsで委譲先のない経路の既定（`agent.sandbox_allow_unsandboxed_exec` 未宣言時） | 公式 `security/`・`configuration/` ページ、`README.md`: fail-closed（既定 `false`） | `windows-install.md` 285-290行・`modules/security.md` 309行: **Windowsでは許可（非サンドボックス実行）**（v0.7.0〜。[03_deployment/02_windows.md](../03_deployment/02_windows.md)参照） |

> **解消した両併記**: 「埋め込み実装」（`knowledge.md` のOllama依存の旧記述）は **v0.6.0 で解消**したため表から外しました。`session.pool_size` の既定値（0 vs 2）も v0.6.0 で `0` に一致しています。

## 未確認事項

- builtin App数（S12）: `src/`解析は、対象SHA・対象パス・解析方法を示す明示承認がないため未実施
- `spawn_min_memory_gb` の既定値（性質は v0.7.0 以降、Linux は cgroup の空き、macOS・Windows はネイティブのメモリ読み取りで判定し、どちらも読めない場合のみ fail open。`subagent.md` 156-160行・`c67c506`。v0.6.0 までは「Linuxのみ有効・非Linuxは fail open」と記載していた）
- Cron `--every` の一般下限（60秒はimport取込下限とHeartbeat間隔として確認済み）
- `-insider.N` の欠番の理由（[02_update/02_release-policy.md](../02_update/02_release-policy.md)参照）

## 関連リンク

- セキュリティ: [01_features/09_security.md](../01_features/09_security.md)
- メモリ: [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md)
- 自律実行: [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)

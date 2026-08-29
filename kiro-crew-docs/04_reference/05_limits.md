# 上限値・既定値の一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: 各ページに記載の一次情報を集約（詳細出典は各節を参照。主要な一次情報は <https://kiro.dev/docs/crew/> と <https://github.com/kirodotdev/KiroCrew>）
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

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
| 公式docsのcrewページ数 | **43** |
| リポジトリ`docs/`配下ファイル数 | **225** |
| 最新安定版 | **v0.4.1** |
| 安定版リリース数 | **8** |
| 総リリース数（プレリリース含む） | **43**（プレリリース35件） |
| CHANGELOG.mdの版節数 | **6**（＋`[Unreleased]`） |
| ライセンス | **Apache-2.0**（本サイトはMIT） |

## セキュリティ

| 項目 | 値 |
|------|-----|
| 拒否コマンドルール件数 | **137** |
| サンドボックスモード数 | **3**（`auto`＝既定／`strict`／`off`） |
| 既知のギャップ | **6点**（＋プラットフォーム依存のリソース上限。[09_security.md](../01_features/09_security.md)参照） |

## メモリ

| 項目 | 値 |
|------|-----|
| メモリ層数 | リポジトリ資料: **6層**（Preferences/Projects/Recent history/Semantic/Episodic/Lessons）＋横断帯（request auth / Slack owner lock / governance ceiling / SEL audit）。公式docs: **8機構**。単一の層数には裁定しない |
| コンテキストバジェット | **165,000文字**（約55,000トークン） |
| Preferencesキャップ | 4,250文字（公式ページ値。リポジトリのfraction由来値は4,290文字=`int(165,000×2.6%)`） |
| Projectsキャップ | 6,400文字（公式ページ値。リポジトリのfraction由来値は6,435文字=`int(165,000×3.9%)`） |
| Recent historyキャップ | 26,600文字（公式ページ値。リポジトリのfraction由来値は26,400文字=`int(165,000×16%)`。リポジトリの`_MEMORY_HISTORY_CAP`は"Daily history"表記） |
| Semantic memoryキャップ | 12,000文字（公式ページ値。リポジトリのfraction由来値は12,705文字=`int(165,000×7.7%)`） |
| Episodic memoryキャップ | 3,000文字・上位8件（`_EPISODIC_INJECT_CAP`。基礎キャップの`_EPISODIC_MEMORY_CAP`はSemantic memoryと同じ7.7%=12,705文字だが、実際の注入時はこの3,000文字にさらにクランプされる） |
| Lessonsキャップ | 37,250文字・最大50件（公式ページ値。リポジトリのfraction由来値は37,290文字=`int(165,000×22.6%)`） |
| 履歴減衰の段数 | **5段**（0-13日／14-60日／61-180日／181-364日／365日以降） |
| Consolidationトリガー（好み/プロジェクト） | **30メッセージ** |
| Consolidationトリガー（履歴/レッスン） | **3時間アイドル** |
| 埋め込み（Memory・Knowledge Library共有） | vendored llama-cpp-python（常時オン・in-process。`llama_cpp`固定。`get_shared_embedder()`でMemoryとKnowledge Libraryが共有）。※`knowledge.md`のみOllama依存の古い記述が残る。詳細: [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md) |

## 自律実行

| 項目 | 値 |
|------|-----|
| Cron: `--timeout-secs` 既定 | 1800秒 |
| Cron `--every` の一般下限 | **未確認**（60秒はimport取込下限およびHeartbeat間隔として確認済みだが、一般的な`--every`下限としては裁定しない） |
| Cronインポート時の最小間隔 | 60秒以上（整数秒。同ファイル299行。他エージェントからのインポート時の検証ルール） |
| **job（スケジュールジョブ）の時間予算** | **最大24時間**（v0.3.0で追加。従来の固定30分上限を置き換え。**下記「Subagent 1件あたりのハードタイムアウト」とは別項目**） |
| **job のinstructions文字数** | **50,000文字**（v0.3.0で追加） |
| TaskRunnerの構造 | オーケストレータ＋4ヘルパーモジュール |
| Subagent 1件あたりのハードタイムアウト | 1800秒（30分） |
| Subagentの外側キャップ | 1200秒（20分） |
| Subagent並行数の下限 | 3 |
| **メモリ上限の適用範囲** | **全同時エージェントの合計**（v0.3.0で変更。小さなspawnを多数行ってホストを食い潰すことができなくなった） |
| Heartbeatの既定間隔 | 60秒 |
| Heartbeatタスクのタイムアウト | 1800秒（30分） |

> **⚠️ 「24時間」と「1800秒」を混同しないこと**: v0.3.0で追加された**最大24時間はjob（スケジュールジョブ）の時間予算**です。**Subagent 1件あたりのハードタイムアウト1800秒（30分）は別項目で、`21584ea`でも変更されていません**（`docs/system-specs/modules/subagent.md` 14行の`_TIMEOUT_SECS`で確認）。CHANGELOGの「replacing one fixed thirty-minute cap」はjob側の従来上限を指します。詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) を参照してください。

## App・インターフェース

| 項目 | 値 |
|------|-----|
| builtin App数 | **[要検証]**。v0.4.1の`src/`解析は未承認のため、旧値を実測値として追認しない |
| メッセージングチャネル数 | 公式docs **7**、README **8**、messaging仕様 **10**。v0.4.0でWhatsApp/iMessage/Feishu追加。出典間の総数は裁定しない |
| インポート対応ソース数 | **5**（Claude Code/Codex/OpenClaw/Hermes/MeshClaw） |
| インポートカテゴリ数 | **8** |
| Gatewayの既定ポート | **5476**（`KIROCREW_PORT`で変更可） |

## テレメトリ

| 項目 | 値 |
|------|-----|
| 既定状態 | オン |
| 送信フィールド数 | **5**（旧仕様は9） |
| 無効化の経路数 | 3（Settings/CLI/環境変数） |

## 未確定（両併記）

出典間で値が食い違うため、**本サイトは裁定しません**。

| 項目 | 出典A | 出典B |
|------|-------|-------|
| v0.4.1の日付 | CHANGELOG.mdの版日付 | Release公開日: 2026-08-29 |
| v0.4.0の日付 | CHANGELOG.mdの版日付 | Release公開日: 2026-08-27 |
| v0.3.0の日付 | CHANGELOG.md: 2026-08-17 | Release公開日: 2026-08-21 |
| v0.2.0の日付 | CHANGELOG.md: 2026-08-09 | Release公開日: 2026-08-10 |
| Subagent自動サイジング上限（`agent.subagent_auto_max`） | `subagent.md`: 32 | `config.md`: 16 |
| サンドボックスの呼称 | 公式docs: `auto` | README・内部ティア: `standard` |
| 埋め込み実装 | Memory/Knowledge Library: shared in-process / vendored llama-cpp-python | `knowledge.md`: Ollama依存の旧記述。裁定しない |

## 未確認事項

- builtin App数（S12）: v0.4.1の`src/`解析は、対象SHA・対象パス・解析方法を示す明示承認がないため未実施
- `spawn_min_memory_gb` の既定値（Linuxのみ有効・非Linuxはfails openという性質のみ確認）
- Cron `--every` の一般下限（60秒はimport取込下限とHeartbeat間隔として確認済み）

## 関連リンク

- セキュリティ: [01_features/09_security.md](../01_features/09_security.md)
- メモリ: [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md)
- 自律実行: [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)

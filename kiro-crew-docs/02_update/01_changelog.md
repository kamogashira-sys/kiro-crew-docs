# 更新履歴

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/releases>
（参照: 2026-08-16）

---

## 📑 このページの内容

- [v0.2.0](#v020)
- [v0.1.3](#v013)
- [v0.1.2](#v012)
- [v0.1.0・v0.1.1](#v010v011)
- [未確認事項](#未確認事項)

---

> このページは **v0.1.2〜v0.2.0** をCHANGELOG.mdに版節があるものから要約しています。CHANGELOG.mdは開発者向けの詳細記述（PR番号付き・1項目10行超）のため、そのまま転記せず、利用者に影響する変更に絞っています。

### v0.2.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-09 |
| GitHub Release 公開日 | 2026-08-10 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.2.0>

主な変更（利用者に影響するもの・抜粋）:

- **Persistent Browser Mode** — Settingsのスイッチ1つでエージェントが永続ブラウザセッションを使えるようになった
- **Spec Builder** — 仕様駆動開発のサーフェス（[01_features/10_apps.md](../01_features/10_apps.md)のbuiltin App参照）
- **Ops Mission Control** — インシデントタイムライン付きの自律的な運用初動対応者
- **Crew Companion** — エージェントの動きを反映するデスクコンパニオン
- **Auto-Improvement** — measurement-firstの自己改善（[01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md)参照）

### v0.1.3

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-07 |
| GitHub Release 公開日 | 2026-08-05 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.3>

model entitlementのhot patch: モデルピッカーがアカウントが利用可能なモデルにスコープを限定し、アカウントが利用できないモデルは送信されなくなりました。利用不可のモデルは、容量エラーや生のJSON-RPCダンプではなく、アクセス問題として報告されます（箇条書き項目はなく、CHANGELOG.md本文の概要記述が出典）。

### v0.1.2

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-07-30 |
| GitHub Release 公開日 | 2026-08-04 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.2>

主な変更（利用者に影響するもの・抜粋）:

- **One agent, ten ways in** — Webダッシュボード・ネイティブデスクトップアプリ・ターミナル等、複数のサーフェスからアクセス可能に
- **長時間セッション向けのダッシュボード** — 複数の並行チャットに対応
- **音声入出力** — WebSocket経由のライブストリーミングSTT
- **10言語対応** — インターフェースの多言語化
- **無人のマルチステップタスク** — 仕様を渡すと分解・実行する（TaskRunner。[01_features/06_autonomy.md](../01_features/06_autonomy.md)参照）

### v0.1.0・v0.1.1

CHANGELOG.mdに版節が存在しません（**最古の節はv0.1.2**）。Release本文のみが出典です。

- v0.1.0（<https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.0>） — 2026-07-22公開
- v0.1.1（<https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.1>） — 2026-07-28公開

## 未確認事項

- v0.1.0・v0.1.1のRelease本文の詳細な要約（本ページでは版とリンクのみを記載）

## 関連リンク

- CHANGELOG: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
- Releases: <https://github.com/kirodotdev/KiroCrew/releases>
- リリース方針: [02_release-policy.md](02_release-policy.md)

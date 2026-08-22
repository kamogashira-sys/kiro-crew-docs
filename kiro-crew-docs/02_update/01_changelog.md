# 更新履歴

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/releases>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [v0.3.0](#v030)
- [v0.2.0](#v020)
- [v0.1.3](#v013)
- [v0.1.2](#v012)
- [v0.1.0・v0.1.1](#v010v011)
- [未確認事項](#未確認事項)

---

> このページは **v0.1.2〜v0.3.0** をCHANGELOG.mdに版節があるものから要約しています。CHANGELOG.mdは開発者向けの詳細記述（PR番号付き・1項目10行超）のため、そのまま転記せず、利用者に影響する変更に絞っています。

### v0.3.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-17 |
| GitHub Release 公開日 | 2026-08-21 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.3.0>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

#### Before you upgrade（破壊的変更・5件）

- **Node.js 22が最小要件**（24 LTS推奨）。Node 20のインストールは拒否される
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **Multi-account Telegramが撤回**。単一bot tokenのみ受理し`telegram.bot_token`へ移行
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md)
- **`kirocrew logout`がrefresh tokenも失効**させる（access tokenに加えて）
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)
- **terminal出力のcredentialスキャンに関する記述**。**⚠️ 同一v0.3.0節内に「スキャンしない」（Before you upgrade）と「ライブストリームでscrubする」（Security and governance）という矛盾する記述があり、本サイトは裁定せず両方を記載しています**
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **Knowledge auto-ingestがopt-in化**（既定オフ）。設定キー`knowledge.auto_ingest_artifacts`
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)

#### 新機能（利用者に影響するもの・抜粋）

- **Crew Mode** — 前のメッセージを待たずに次を送信でき、並列サブセッションで処理される
- **Session summaries** — サイドパネルタブが各スレッドの意図と着地点を示す（opt-in）
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md)
- **Browser panel** — エージェントがダッシュボードのサイドパネルを直接操作。Playwright CLIはリモートセッション用に残る
  → 詳細は [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)
- **Git panel** — サイドパネルにリポジトリ状態とコミットログ
- **Linux ARM64・Windowsのfirst-class build**
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **`kirocrew tailnet up`によるtailnet公開**・ダッシュボードからのcloud crew起動
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)
- **Personal Shopper・Issue Radar Crews**（CHANGELOGは「2つの新App」と表現）・App Store刷新。**⚠️ 両Appの実装自体は既存**（`personal_shopper`はv0.2.0以前から、`issue_radar`はv0.1.2から存在）で、CHANGELOGの表現と実装年代が一致しません。本サイトは両方を記載しています
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **Computer Useの提示方法が変更**（動作する環境にのみ提示）。**プラットフォームは引き続きmacOSのみ**
  → 詳細は [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)
- **各jobが自身の時間予算を設定可能**（最大24時間）
  → 詳細は [04_reference/05_limits.md](../04_reference/05_limits.md)
- **メモリガバナー**（メモリ枯渇時にスケジュールジョブを延期・新規subagentを拒否）
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **`kirocrew policy show`が拒否コマンドカタログをカテゴリ別に要約**
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)
- **MCPサーバの共有可否をプローブ**・per-agent tool sets・認証付きカスタムサーバ
  → 詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md)
- **Subagentが主エージェントと同様に承認を要求**
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **Knowledge支出に上限**・lessonsが関連度で浮上
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)
- **画像がartifactとして保持**・push to talk
  → 詳細は [01_features/12_artifacts.md](../01_features/12_artifacts.md)
- **Telegramに実際のコマンドメニュー**
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md)
- **パフォーマンス改善**（初回メッセージのレイテンシ短縮・コールド読込の転送量削減・ディクテーション高速化・ストリーミング改善）

#### Security and governance（セキュリティ・ガバナンス・7件）

- Appは自身のイベントのみ参照可能に
- スケジュールジョブが毎実行ごとに再審査される
- メモリ上限が全同時エージェント合計に適用
- ライブストリームでcredentialがscrubされる（**Before you upgradeの記述と矛盾。上記参照**）
- ピン留めされたポリシー下限をローカルで引き下げ不可
- メモリ編集に認識済みセッションが必要
- 独自のIDプロバイダを持ち込み可能
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)・[03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)

#### 開発者向け変更（C-L3・件数のみ）

- Notable fixes（Chat and composer／Sessions and stopping／Apps and settings／Channels and notifications／Desktop, install, and CLI／Security and resources／Everywhere else）: **7カテゴリ**（v0.2.0以前のCHANGELOG節に前例がないため件数のみ記載。個別項目は展開しません）

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

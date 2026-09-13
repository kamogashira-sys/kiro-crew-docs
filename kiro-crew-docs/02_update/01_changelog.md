# 更新履歴

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/releases>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

---

## 📑 このページの内容

- [v0.6.0](#v060)
- [v0.5.0](#v050)
- [v0.4.1](#v041)
- [v0.4.0](#v040)
- [v0.3.0](#v030)
- [v0.2.0](#v020)
- [v0.1.3](#v013)
- [v0.1.2](#v012)
- [v0.1.0・v0.1.1](#v010v011)
- [未確認事項](#未確認事項)

---

> このページは **v0.1.2〜v0.6.0** をCHANGELOG.mdに版節があるものから要約しています。CHANGELOG.mdは開発者向けの詳細記述（PR番号付き・1項目10行超）のため、そのまま転記せず、利用者に影響する変更に絞っています。

### v0.6.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-09-05 |
| GitHub Release 公開日 | 2026-09-11 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.6.0>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

#### Before you upgrade（破壊的変更・4件）

- **Python 3.12 が下限**になりました。3.10・3.11 のホストはインストール・更新の前に上げる必要があります。システムのパッケージマネージャに 3.12 がない場合は、各インストーラが自分で 3.12 を用意します
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **インストーラが自前の Python を持ち込む**ようになりました。`curl -fsSL https://download.crew.kiro.dev/cli.sh | sh` はシステムの Python ではなく**ピン留めされた CPython** を用意します。意図してシステム側に対してビルドする場合は `--system-python` を渡します
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **コマンドゲートがコマンド文字列を読んで credential パスを塞ぐ方式をやめました**。今後は**サンドボックスの bind mask が境界**です。この文字列ゲートに依存していた場合は、`config.json` の `agent.sandbox` が `off` になっていないか確認が必要です
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **無人の auto-run plan が2時間で停止**します。`config.json` の `orchestrator.max_plan_duration_seconds` で引き上げるか、`0` で上限を外します。**stage-gated な plan は打ち切られません**
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) / [04_reference/05_limits.md](../04_reference/05_limits.md)

#### 新機能（利用者に影響するもの・抜粋）

- **ハーネスの選択（Preview）** — Claude Code・Codex・KAS を選べます。Settings → Developer で Developer Mode をオン（既定オフ）にしてから Developer → Agent Backend で選択します。**Claude 自身の設定で事前承認されたツール呼び出しは Crew の承認パスに到達せず、拒否ルールと監査ログがその呼び出しを見ません**
  → 詳細は [01_features/15_agent-backends.md](../01_features/15_agent-backends.md)
- **Remote crews（Preview）** — `instances.enabled` で、接続済みの別 crew 上でチャットを実行できます。別所で動くセッションには server badge と crew 名が付きます
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- **長時間の作業** — チャットの1ターンが最大4時間（`agent.chat_turn_timeout_secs`）、サブエージェントは3時間・最大1000ツール呼び出しになりました
  → 詳細は [04_reference/05_limits.md](../04_reference/05_limits.md) / [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)
- **エージェントが自分の監視ループを制御** — 開始・変更・停止をエージェント自身が行えます。goal chip にサイクル上限が表示されます。`agent.session_control` は既定 true で、`false` で無効化します
  → 詳細は [01_features/17_workflows.md](../01_features/17_workflows.md)
- **AWS Control が Overview で開く** — アカウント・キーの健全性・ドライブ使用量・共有リンク・バックアップスケジュールを1画面に表示します。Files ペインはその場でプレビュー・リネームします
  → 詳細は [01_features/16_aws-control.md](../01_features/16_aws-control.md)
- **Apps に Launchpad** — Apps → Library がグリッド表示になり、アプリはバックグラウンド処理・Command Bar の行・埋め込みチャットを持てます
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **Crew members に顔（Preview）** — ghost avatar を組み立てられます。**Developer Mode 前提の Preview opt-in** です
- **ゲートが理由を説明する** — ブロックされたツール呼び出しが次の手を示します。拒否ルールは綴り替えに耐えるようになり、通常の作業が誤って拒否されることが減りました。**サンドボックスできないホスト（armv7l・riscv64 など）はエージェントの実行を拒否します**
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **承認の形を変えられる** — サンドボックス内のコマンドが自分の上限を書き換えられなくなりました。再起動時に auto-approve grant を落としたことを通知します
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **計測** — cron・heartbeat を含むすべてのターンがトークン・支出・レイテンシを報告します
  → 詳細は [03_deployment/06_telemetry-and-privacy.md](../03_deployment/06_telemetry-and-privacy.md)
- **Artifact の公開** — 自分の AWS アカウント上の公開 HTTPS URL へ artifact を公開できます（`publish.allowed_destinations`）
  → 詳細は [01_features/12_artifacts.md](../01_features/12_artifacts.md)
- **自動 Knowledge フォルダの廃止** — フォルダは明示的に追加したときだけ Library に入ります
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)

### v0.5.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-29 |
| GitHub Release 公開日 | 2026-09-05 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.5.0>
（参照: 2026-09-13 / commit `e683282` / 版 v0.5.0）

#### Before you upgrade（破壊的変更・12件）

> **⚠️ 出典間で件数が食い違っています。本サイトは裁定せず両方を示します。**
> CHANGELOG.md の `[0.5.0]` 節の "Before you upgrade" は **12項目**ですが、GitHub Release 本文は **5項目**のみを挙げ、本文中で "Five changes" と明記しています。本サイトは**CHANGELOG.md の12件を根拠**とし、Release 本文には5件しか記載がないことを注記します。どちらが正しいかは判断しません。

- **Dictation provider が単一の `local` provider に統合**されました
- **Snapshot-to-S3 が廃止**されました。`kirocrew snapshot --to s3://…`・`--aws-profile`・`s3://` からの fetch が削除され、クラウドバックアップは AWS Control app に移りました。引き換えにスナップショットは live state への restore を獲得しています
  → 詳細は [01_features/16_aws-control.md](../01_features/16_aws-control.md)
- **App の実行信頼が、同意したコードに束縛**されました。grant は同意した時点のコードに紐づきます
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **黙って実行されていた一部のコマンドが確認を求める**ようになりました
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **Kiro CLI へは published relay 経由で到達**するようになりました（bundle-path 系の環境変数2件が削除）
- **security-policy の `sandbox` キーの綴り誤りが検証エラーになりました**（従来は黙って無視）。`publish` が malformed な場合は publish を拒否します
- **リリースが最小サポート版を宣言できる**ようになりました。下回るインストールには snooze・skip・dismiss ができない更新プロンプトが出ます
  → 詳細は [02_release-policy.md](02_release-policy.md)
- **Knowledge が Agent Capabilities 配下へ移動**しました（単独の Knowledge ページは廃止）
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)
- **単独の Auto-Triage Pipeline app が廃止**され、そのボードは他所へ移りました
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **Disconnect が本当に切断する**ようになりました。接続の削除は OAuth grant の revoke も行います
- **Malformed な agent spec が明示的に失敗**するようになりました（従来は黙って読み飛ばし）
- **`kirocrew gateway --no-tunnel`** — 新フラグで起動した gateway はトンネルを張りません
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

> **注**: 上記のうち、Release 本文に記載があるのは「Dictation provider の統合」「Snapshot-to-S3 の廃止」「App 実行信頼の束縛」「確認を求めるコマンド」と、Knowledge 移動と Auto-Triage 廃止を1項目に統合したものです。残りは CHANGELOG.md にのみ記載されています。

#### 新機能（利用者に影響するもの・抜粋）

- **AWS Control（builtin App・既定オフ）** — 接続済み AWS アカウントの健全性・プライベート S3 ドライブ・クラウドバックアップ・費用を1画面で扱います。**Apps > Library で有効化**します
  → 詳細は [01_features/16_aws-control.md](../01_features/16_aws-control.md)
- **セキュリティポリシーの中央配布** — `security_policy.json` を URL で配布し、各ホストが fetch します
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **セッションがタブになる** — ダッシュボードのセッション表示がタブ形式になりました
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md)
- **エージェントが他のエージェントを動かす** — `session_send` が他セッションへ次のターンとしてメッセージを配送します。conductor エージェントがこの上に構築されています
  → 詳細は [01_features/17_workflows.md](../01_features/17_workflows.md)
- **承認を誘導できる** — 承認の挙動を設定で方向づけられます
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **Secrets の適用範囲拡大**・**MCP サーバの無言劣化の解消**・**スマートフォンとタッチ対応**・**Meetings の自動翻訳**（対象言語を選ぶと逐行で翻訳）
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md) / [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)
- **どこからでも自己更新**・**Issue Radar と Dev Fleet の強化**・**高速化と軽量化**
- **多言語化の拡充** — CHANGELOG は「Counted labels, confirmation dialogs and sign-in guidance are fully translated in all 12 languages」と記述しています（**v0.1.2 節の「10言語対応」から増加**）。破壊的プロンプトはその言語の引用符で資源名を囲み、5つのメニューがキーボード操作・フォーカス復帰・スクリーンリーダー通知に対応しました
- **`tunnel.enabled`・`dashboard.browser_view_port`・`slack.trusted_bot_ids`** の設定キーが追加されました
  → 詳細は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

### v0.4.1

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-28 |
| GitHub Release 公開日 | 2026-08-29 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.4.1>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

安定チャネルの表示修正です。About、Settings footer、更新ポップアップは、内部のrelease-candidate stampではなく、インストール済み・利用可能な**正式リリース番号**を表示します。更新の仕組み、skip、snoozeの動作は変わりません。

### v0.4.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-25 |
| GitHub Release 公開日 | 2026-08-27 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.4.0>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

主な変更（利用者に影響するもの・抜粋）:

- **WindowsとLinuxの導入** — Windowsは署名済みinstallerとin-app auto-updateをstable配布。Linux desktopは`.deb`/`.rpm`（glibc 2.34以上）を提供し、旧ディストリビューション向けに`--managed-python`がある
- **Windows Computer Use** — UI AutomationでWindowsネイティブアプリを読み取り・操作でき、Windows agent treeにはJob objectのprocess/memory ceilingが追加
- **チャネル** — WhatsApp、iMessage、Feishuが追加。Teams/Telegram/WebexがSlackとの機能パリティへ近づき、Discordにはコマンドメニュー等が追加
- **Secrets** — config fileではなく暗号化vaultに保存し、MCP環境で`secret://NAME`参照を使える。値はSettings → Secretsでマスクされ、ブラウザへ送られない
- **ダッシュボード/セッション** — inline編集・diff・file tree、複数Gateway横断のセッション検索、Session hand-off、Reloadなどを追加
- **Memory / Skills** — repository scopeのLessonが有効化、tag別episodic decay、project-local skills、hooksのmatcher/injectionを追加

暗号方式、設定キー、保存先、およびbuiltin App数は、このCHANGELOG記述だけでは確定しないため補完しません。詳細は各機能ページを参照してください。

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

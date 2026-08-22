# CLIコマンド一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://kiro.dev/docs/crew/interfaces/cli-reference/>（Page updated 表記あり）
**出典**: リポジトリ README
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（`cloud`サブコマンド完全一覧・`eval`/`telemetry`掲載漏れの指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [コマンド一覧](#コマンド一覧)
- [v0.3.0での変更](#v030での変更)
- [クラウド・Pod（見落としやすいコマンド群）](#クラウドpod見落としやすいコマンド群)
- [`token`の出力ストリーム契約](#tokenの出力ストリーム契約)
- [未確認事項](#未確認事項)

---

> **方針の訂正**: 当初このページは公式 `cli-reference` とREADMEの2系統のみを突合して作成していましたが、**リポジトリのモジュール仕様（`docs/system-specs/modules/cli.md`）に、公式ページより遥かに完全なコマンド一覧が存在する**ことが判明したため全面改訂しました。一次情報ヒエラルキーの順位1（リポジトリのモジュール仕様）を最優先する本サイトの原則に従い、本ページは`modules/cli.md`を主たる出典とします。

## コマンド一覧

`docs/system-specs/modules/cli.md`「## Commands」節の実測（一部説明を要約）。

| コマンド | 説明 |
|---------|------|
| `kirocrew chat [-m "msg"] [--model X]` | チャット。対話モード／単発メッセージ／モデル上書き |
| `kirocrew gateway [--slack-only] [--no-crons]` | Gateway起動（ダッシュボード＋メッセージングチャネル） |
| `kirocrew setup [--agent-only] [--slack]` | エージェント設定インストール・プロジェクトディレクトリ保存・認証情報設定 |
| `kirocrew doctor` | kiro-cliの導入・設定の妥当性検証 |
| `kirocrew cron add/list/remove` | Cronジョブ管理 |
| `kirocrew spawn run/list` | サブエージェント管理 |
| `kirocrew app install/list/enable/disable/uninstall[--purge-data]/dev` | App Kit管理 |
| `kirocrew learn add/list/remove` | 学習した修正の管理 |
| `kirocrew run TASK.md` | 仕様ファイルから自律タスクを実行 |
| `kirocrew token` | 認証トークン付きダッシュボードURLを出力 |
| `kirocrew logout` | 全アクティブダッシュボードセッションを無効化（リフレッシュチェーン含む）。**⚠️ v0.3.0のCHANGELOGはこれを新規変更として記載しているが、この記述は`64060f3`時点で既に存在した。下記「[`kirocrew logout` の変更に関する食い違い](#kirocrew-logout-の変更に関する食い違い裁定しない)」参照** |
| `kirocrew manifest` | ユーザーエイリアス自動入力済みのSlackマニフェスト生成 |
| `kirocrew update` | 最新版へ更新（git pull＋再ビルド） |
| `kirocrew status` | 実行中Gatewayの統計を表示 |
| `kirocrew stop [--port N]` | Gateway停止（サービス認識。稼働中ならsystemd/launchdサービスを停止） |
| `kirocrew restart [--port N]` | Gateway再起動 |
| `kirocrew service install/uninstall/status` | システムレベルのサービス化（systemd/launchd） |
| `kirocrew logs [-f]` | ログ表示（追従可） |
| `kirocrew cloud launch/list/status/connect/tunnel/login/stop/start/destroy/iam-policy/iam-boundary/doctor` | 自分のAWSアカウント内のEC2インスタンスのプロビジョニング・接続・管理（サブコマンド一覧は`modules/cloud.md`準拠。`modules/cli.md`は`tunnel`・`login`・`iam-boundary`を含まない9コマンドのみを列挙） |
| `kirocrew security events [-n N]` | 最近のSEL監査イベント表示 |
| `kirocrew security verify` | SEL HMACチェーンの整合性検証 |
| `kirocrew snapshot [--keep N] [--list]` | 全状態のスナップショット作成（既定7件保持） |
| `kirocrew restore <file> [--mode replace\|merge] [--components X,Y] [--dry-run]` | スナップショット復元 |
| `kirocrew config get [key]` / `set <key> <val>` / `edit` | 設定操作 |
| `kirocrew memory list/search/stats/audit` / `export/import/migrate` | ベクトルメモリの検査・移行 |
| `kirocrew policy show/validate/explain/profile` | 実効セキュリティポリシーの検査 |
| `kirocrew pod up/down/ls/status/token/url/logs/exec/install/provision` | 孤立ワークツリーのテストGateway（**Linux `systemd --user`限定**。macOS/Windowsでは1行メッセージで拒否） |
| `kirocrew knowledge dedup [--apply]` | ソース横断の重複ナレッジ文書を統合（dry-run既定） |
| `kirocrew cron preview <script>` | Scriptのcronをローカルで実MCPツール付きで実行（通知はキャプチャして表示） |
| `kirocrew workspace create/update --dir <name>` | ワークスペース管理（`--dir`はデータホームの厳密な子孫のみ許可） |
| `kirocrew computer doctor [--json]` | Computer Useの利用可否レポート |
| `kirocrew computer apps` | 操作可能な画面上アプリの一覧 |
| `kirocrew computer call <tool> [k=v ...]` | Computer Useツールを1件実行（デバッグ・再現用） |
| `kirocrew mcp-cron` / `mcp-core` / `mcp-computer` | kiro-cliが起動する内部MCPサーバ（`mcp-computer`は`argparse.SUPPRESS`で隠される） |
| `kirocrew --version` | 版表示 |
| `kirocrew eval [--all] [--scenario <name>]` | マルチセッション評価ハーネス実行（`kirocrew gateway --test-mode`を別シェルで起動している必要あり）。**`modules/cli.md`には記載がなく、公式`cli-reference`ページのみに記載** |
| `kirocrew telemetry disable` / `status` | 匿名テレメトリの無効化・送信内容の確認。**`modules/cli.md`には記載がなく、リポジトリREADMEのみに記載** |
| **`kirocrew tailnet up`** | ダッシュボードをTailscaleネットワークに公開する。**⚠️ `modules/cli.md`（本ページの主出典）に記載がありません**。実在は`docs/guides/remote-and-mobile.md` 286・290・294行（`tailscale serve`を実行、443でHTTPS、印字されるURLはセッションを含まない）と`docs/system-specs/modules/governance.md` 1310行（`capabilities.tailnet_origin`）で確認できます（`21584ea`）。**リポジトリ内には未確定の将来仕様を扱うディレクトリにもこのコマンドへの言及がありますが、本サイトはそれを出典として使いません** |

> **注記**: `eval`と`telemetry`は、本ページの主出典`modules/cli.md`「## Commands」節には記載がありません。しかし`eval`は公式`interfaces/cli-reference/`ページに、`telemetry`はリポジトリREADMEに明確に存在するコマンドとして記載されているため、掲載漏れを避けるためここに追加しています。**`tailnet`（v0.3.0で追加）はさらに事情が異なり、CLIコマンド台帳の4系統（①公式cli-referenceページ ②リポジトリREADME ③`--help` ④`modules/cli.md`）すべてに記載がありません**。実在は上表に示した別系統（ガイド・governance仕様）で確認しています。`modules/cli.md`を主出典としても、他の一次情報だけに存在するコマンドを見落とさないよう、複数系統を横断確認する必要があります。

## v0.3.0での変更

### `kirocrew policy show` の詳細

`show`は拒否コマンドカタログを**カテゴリ別のグループ件数として要約**し、**`--ids`** を付けると各カテゴリのrule idを列挙します。**エンタープライズポリシーが有効かどうかに関わらず、全インストールで利用可能**です。

出典: `docs/system-specs/modules/cli.md` 135行（`21584ea`）／CHANGELOG.md v0.3.0節 176行「**`kirocrew policy show` lists the denied-command catalog**, so you can read what is blocked without going to the source」。拒否ルールの件数（137）は [01_features/09_security.md](../01_features/09_security.md)、ポリシーの配置は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

### `kirocrew logout` の変更に関する食い違い（裁定しない）

CHANGELOGはv0.3.0の破壊的変更として「**`kirocrew logout` now revokes refresh tokens**, not just access tokens（access tokenだけでなくrefresh tokenも失効させる）」を挙げています（19行）。**しかし本ページの主出典`modules/cli.md` 107行は、本サイトがv0.2.0として固定している`64060f3`の時点で既に「Revoke all active dashboard sessions, refresh chains included」と記述していました**（`21584ea`でも同一文）。

つまり**CHANGELOGはこれをv0.3.0の新規変更として記載しているが、モジュール仕様は`64060f3`時点で既に同じ内容を記述していた**という状態です。**どちらが実際の変更時期を示すか・なぜ食い違うのかは公式に説明がないため、本サイトは推測せず両方を記載します。**

出典: CHANGELOG.md v0.3.0節 19行（`21584ea`）／`docs/system-specs/modules/cli.md` 107行（`64060f3`・`21584ea`の両方で同一文であることを実測）。

## クラウド・Pod（見落としやすいコマンド群）

`kirocrew cloud` と `kirocrew pod` は**公式 `cli-reference` ページには独立した見出しがありません**が、リポジトリのモジュール仕様には完全なサブコマンド一覧が明記されており、**実在するコマンドです**。

- **`kirocrew cloud`**: 自分のAWSアカウントにKiroCrewのEC2インスタンスをプロビジョニングして管理する、人間向けのインストーラ／コントロールプレーン。`launch`は6段階のウィザード。`tunnel`はSSMポートフォワードでダッシュボードを開く、`login`はSSM経由で`kiro-cli`のデバイスコード／ソーシャルサインインを実行、`iam-boundary`はimmutableなインスタンス権限バウンダリを事前作成するワンタイムの管理者操作（`modules/cloud.md:13-16`）
- **`kirocrew pod`**: 孤立したワークツリーのテスト用Gateway。**Linuxの`systemd --user`のみで動作**し、macOS/Windowsではsystemdに触れるすべての動詞が1行メッセージで拒否されます

## `token`の出力ストリーム契約

`kirocrew token` は**機械可読なstdout契約**を持ちます。stdoutにはダッシュボードURLのみが流れ、すべての失敗理由（無効なTTL・Gateway未起動・Gateway到達不可・空トークン）はstderrに出力されます。この契約は、リモートでの`kirocrew token`実行結果をSSH経由でパースする`mint_remote_token`が、stdoutからJWTを正規表現抽出するために必要とされています。

## 未確認事項

- `kirocrew --help` による実機での突合（未実施）
- `eval`・`telemetry`が`modules/cli.md`から脱落している理由（意図的な非対象外か、ドキュメント更新漏れかは不明）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)
- 上限値: [05_limits.md](05_limits.md)

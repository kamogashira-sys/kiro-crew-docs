# CLI サブコマンド突合表（当初の3系統 → **4系統に訂正**）

- **取得日**: 2026-08-16
- **commit SHA**: `64060f3ffecdf4aebeb764b4e3108e7375249ad8`
- **出典**: ① 公式 `kiro.dev/docs/crew/interfaces/cli-reference/`（`.md` companion）② リポジトリ `README.md` ③ `kirocrew --help`（**実機なしのため未実施。注記する**）④ **`docs/system-specs/modules/cli.md`（リポジトリのモジュール仕様。当初の突合の後に追加。最も完全で正確な一次情報）**

> **v0.3.0再確認（2026-08-22・v0.3.0タグ`21584ea`）**: 系統④の全コマンドの実在を`21584ea`のfull cloneで再確認済み（変化なし・70行）。`tailnet`を追加、`policy show`の詳細を反映。（v0.3.0 対応。コミット `aaaefa9`）

> **重要な訂正（2026-08-16）**: 当初①②③の3系統に限定したが、**一次情報ヒエラルキー順位1のリポジトリモジュール仕様（`modules/cli.md`）を検索対象に含めていなかった**ことが判明した。`modules/cli.md`には`cloud`・`pod`を含む、公式cli-referenceより遥かに完全なコマンド一覧が存在する。以下は訂正後の内容。

> **v0.6.0再測定（2026-09-13・`8575209`）**: 系統④（`modules/cli.md`）の表形式コマンド一覧を機械抽出して再測定した。
>
> | 版 | `modules/cli.md` の表に載るサブコマンド数 |
> |---|---|
> | v0.4.1（`bba3f19`） | **32件** |
> | v0.6.0（`8575209`） | **39件** |
>
> **新規7件**: `agent`／`artifact`／`consolidate`／`eval`／`sandbox`／`tailnet`／`telemetry`（`tailnet` は v0.3.0 で既に台帳へ追加済み）。**消滅0件**。
>
> **⚠️ 一次情報間の差（裁定しない）**: **`kirocrew secrets import` は `modules/cli.md` の表に載っていません**が、`docs/guides/secrets-env.md` 54・58・84行と CHANGELOG の `[0.5.0]` 節507行（「**`kirocrew secrets import`** — Move plaintext credentials out of `.env`」）に実在します。`modules/cli.md` の表が網羅的でない可能性がありますが、公式の説明がないため本サイトは裁定せず、両方の事実を記録します。`check-notation.py` の `ALLOWED_CLI_COMMANDS` には `secrets` と `artifact` の両方を登録済み。
>
> 抽出方法: `^\|\s*` + 「`kirocrew <sub>`」で始まる表セルのみを対象にした（本文の散発的な言及を拾わないため）。
>
> **v0.7.2再測定（2026-10-04・`c67c506`）**: 同じ抽出方法で **40件**（新規1件: `ledger-sweep`（221-222行）。消滅0件）。
>
> | 版 | `modules/cli.md` の表に載るサブコマンド数 |
> |---|---|
> | v0.7.2（`c67c506`） | **40件** |
>
> **⚠️ 表に無いが実在するもの（裁定しない）**: `kirocrew file-delivery approve` は `modules/cli.md` の表・README・公式 cli-reference のいずれにも無く、CHANGELOG v0.7.0節 445-448行・`docs/feature-map/README.md`・公式 `security/` ページで確認できる。`kirocrew secrets import` は引き続き表に無い（`modules/cli.md` の「Secrets Command」節 662-681行には記載）。公式 cli-reference ページの `kirocrew` サブコマンドは26語（`app`〜`update`）。`check-notation.py` の `ALLOWED_CLI_COMMANDS` に `ledger-sweep`・`file-delivery` を追加した。表にある `agent`／`consolidate`／`sandbox` は公開文書で未使用のため許可リスト未登録のまま。

## 系統①: 公式 cli-reference の H2/H3 構造（確定）

| H2 グループ | コマンド |
|-----------|---------|
| Global flags | （フラグのみ） |
| Gateway lifecycle | `setup` / `doctor` / `gateway` / `stop` / `restart` / `logs` / `service` / `update` / `token` |
| Chat | `chat` |
| Task runner | `run` / `run status` / `run cancel` |
| Cron | `cron add` / `cron list` / `remove` / `remove-all` / `pause` / `resume` / `trigger` / `update` |
| Subagents | `spawn run` / `spawn list` |
| Learning | `learn add` / `learn list` / `remove` |
| Snapshot & restore | `snapshot` / `restore` |
| Config | `config get` / `set` / `edit` |
| Apps | `app dev` |
| MCP | `manifest` |
| Status and metrics | `status` |
| Eval harness | `eval` |
| Computer use | `computer apps` / `computer call` |
| Docker helpers | （個別コマンド見出しなし） |
| Auth | `logout` |

**本文中にのみ言及があるコマンド**（H3 見出しはないが `kirocrew X` として出現）: `chown`／`kiro-cli`（サブコマンドではなくエイリアス言及）

## 系統②: README 中の `kirocrew X` 全出現

`chat` / `config` / `cron` / `doctor` / `gateway` / `logs` / **`policy`** / `run` / `service` / `setup` / `spawn` / **`security`** / **`telemetry`**

## 系統③: `kirocrew --help`

**未実施**（実機の Kiro Crew インストールが本環境に存在しないため）。実機確認が可能になれば追加する。それまでは①②のみで判定する。

## 突合結果

| コマンド | ①公式ページ | ②README | ③--help | 判定 |
|---------|:---:|:---:|:---:|------|
| `setup`〜`token`（Gateway lifecycle 9件） | ○ | 一部○ | 未確認 | 記載する |
| `chat` | ○ | ○ | 未確認 | 記載する |
| `run` / `run status` / `run cancel` | ○ | 一部○ | 未確認 | 記載する |
| `cron add`〜`update`（8件） | ○ | 一部○ | 未確認 | 記載する |
| `spawn run` / `spawn list` | ○ | 一部○ | 未確認 | 記載する |
| `learn add` / `learn list` / `remove` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `snapshot` / `restore` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `config get/set/edit` | ○ | ○ | 未確認 | 記載する |
| `app dev` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `manifest` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `status` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `eval` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `computer apps` / `computer call` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `logout` | ○ | – | 未確認 | 記載する（公式ページのみ） |
| `chown` | ○（本文のみ・H3なし） | – | 未確認 | 記載する（本文中の言及として） |
| **`telemetry`** | **×** | ○ | 未確認 | **記載する。「公式ページに独立見出しはないが README に実在」と注記** |
| **`security`** | **×** | ○ | 未確認 | 同上 |
| **`policy`** | **×** | ○ | 未確認 | 同上 |
| **`cloud`** | **×** | **×** | 未確認 | **記載しない**（いずれの系統にも出現しない） |
| **`pod`** | **×** | **×** | 未確認 | **記載しない**（`modules/security.md` に言及があるとされていたが、README・公式ページのいずれにも出現しないため見送り） |

## 確定事項（`cloud` の当初の判定 → 撤回・訂正）

**当初の判定「`kirocrew cloud`はいずれの系統にも出現しないため記載しない」は誤りだった。** `docs/system-specs/modules/cli.md`「## Commands」節に完全なサブコマンド一覧が存在し、`cloud`・`pod`ともに実在するコマンドである。

## 系統④: `docs/system-specs/modules/cli.md` の完全なコマンド一覧（訂正版で正とする）

| コマンド | 説明 |
|---------|------|
| `kirocrew chat [-m "msg"] [--model X]` | チャット（対話モード・単発メッセージ・モデル上書き） |
| `kirocrew gateway [--slack-only] [--no-crons]` | サーバ起動 |
| `kirocrew setup [--agent-only] [--slack]` | エージェント設定インストール |
| `kirocrew doctor` | ヘルスチェック |
| `kirocrew cron add/list/remove` | Cronジョブ管理 |
| `kirocrew spawn run/list` | サブエージェント管理 |
| `kirocrew app install/list/enable/disable/uninstall/dev` | App Kit管理 |
| `kirocrew learn add/list/remove` | レッスン管理 |
| `kirocrew run TASK.md` | 自律タスク実行 |
| `kirocrew token` | ダッシュボードアクセスURL発行 |
| `kirocrew logout` | 全ダッシュボードセッションの無効化 |
| `kirocrew manifest` | Slackマニフェスト生成 |
| `kirocrew update` | 最新版へ更新 |
| `kirocrew status` | 実行中Gatewayの統計表示 |
| `kirocrew stop` / `restart` | Gateway停止・再起動 |
| `kirocrew service install/uninstall/status` | システムサービス化 |
| `kirocrew logs [-f]` | ログ表示 |
| **`kirocrew cloud launch/list/status/connect/stop/start/destroy/iam-policy/doctor`** | **AWSアカウント内のEC2インスタンスのプロビジョニング・接続・管理**（実在確認済み） |
| `kirocrew security events/verify` | SEL監査イベント表示・整合性検証 |
| `kirocrew snapshot [--keep N] [--list]` | スナップショット作成 |
| `kirocrew restore <file> [--mode] [--components] [--dry-run]` | スナップショット復元 |
| `kirocrew config get/set/edit` | 設定操作 |
| `kirocrew memory list/search/stats/audit/export/import/migrate` | ベクトルメモリ検査 |
| `kirocrew policy show/validate/explain/profile` | 実効セキュリティポリシー検査。**`show`はカテゴリ別グループ件数で拒否コマンドカタログを要約、`--ids`で各カテゴリのrule idを列挙。エンタープライズポリシー無効でも利用可**（`modules/cli.md` 135行・v0.3.0タグ`21584ea`で確認） |
| `kirocrew pod up/down/ls/status/token/url/logs/exec/install/provision` | 孤立ワークツリーのテストGateway（Linux `systemd --user`限定。実在確認済み） |
| `kirocrew knowledge dedup [--apply]` | Knowledge Library重複排除 |
| `kirocrew cron preview <script>` | Cronスクリプトのローカル実行プレビュー |
| `kirocrew workspace create/update --dir <name>` | ワークスペース管理 |
| `kirocrew computer doctor/apps/call` | Computer Use操作 |
| `kirocrew mcp-cron`/`mcp-core`/`mcp-computer` | kiro-cliが起動する内部MCPサーバ（`argparse.SUPPRESS`で隠されている場合あり） |
| `kirocrew --version` | 版表示 |
| **`kirocrew tailnet up`** | **⚠️ `modules/cli.md`に記載なし（系統④に不在）。CHANGELOG v0.3.0節122行に記述があり、実体は`docs/guides/remote-and-mobile.md` 286・290・294行（`tailscale serve`実行・443でHTTPS・印字URLはセッション非含有）と`docs/system-specs/modules/governance.md` 1310行（`capabilities.tailnet_origin`）で確認できる（v0.3.0タグ`21584ea`）。`docs/request-for-change/rfc-tailnet-dashboard-access.md`にも記載があるが、RFCは出典として使用しない** |

## 反映方針（v0.3.0タグ`21584ea`再確認済み・2026-08-22）

`04_reference/01_cli-commands.md`は本表（系統④）を主軸に全面改訂する。`cloud`・`pod`は実在コマンドとして記載する。**`tailnet`は系統④に不在のため、出典を`guides/remote-and-mobile.md`・`modules/governance.md`と明示した上で記載する**（系統④の一覧に依拠していると誤解させる書き方をしない）。`policy show`は上記の詳細（カテゴリ別グループ件数・`--ids`・エンタープライズ無効でも利用可）を反映する。

# CLIコマンド一覧

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://kiro.dev/docs/crew/interfaces/cli-reference/>（Page updated 表記あり）
**出典**: リポジトリ README
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（`cloud`サブコマンド完全一覧・`eval`/`telemetry`掲載漏れの指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（v0.7.0の新規コマンド・pod の対応プラットフォーム・`token`の403・`eval`/`telemetry`/`tailnet`の再測定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cloud.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

---

## 📑 このページの内容

- [コマンド一覧](#コマンド一覧)
- [v0.7.0での変更](#v070での変更)
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
| **`kirocrew ledger-sweep`**（v0.7.0） | 終了済みに見えるsessionとconductor-workのledgerを一覧表示（種別・保存先ディレクトリ・ledgerキー・フェーズ／項目数・経過時間・該当理由）。**dry-runで、何も削除しない** |
| **`kirocrew ledger-sweep --purge [--older-than-days N] [--purge-unreadable]`**（v0.7.0） | dry-runが列挙したledgerを削除する。**取り消し不可・明示実行のみで、自動では動かない**（Gatewayのフック・履歴削除経路・MCPツールのいずれからも到達しない）。各削除は保存先のロック下で再判定され、ledgerが再び使われ始めていれば拒否される。**既定のアイドル期間は30日**（有限の非負数のみ。`nan`・`inf`は拒否）。読めない記録は`--purge-unreadable`を付けない限り残す |
| `kirocrew cron add/list/remove` | Cronジョブ管理 |
| `kirocrew spawn run/list` | サブエージェント管理 |
| `kirocrew app install/list/enable/disable/uninstall[--purge-data]/dev` | App Kit管理 |
| **`kirocrew app import <package-dir> [--out DIR] [--name NAME] [--install]`**（v0.7.0） | 他のエージェントハーネス向けのプラグインパッケージをAppディレクトリに変換し、対応先の無い要素をすべて報告する。**読み取りとコピーのみで、パッケージ内のものは何も実行しない** |
| `kirocrew learn add/list/remove` | 学習した修正の管理 |
| `kirocrew run TASK.md` | 仕様ファイルから自律タスクを実行 |
| `kirocrew token` | 認証トークン付きダッシュボードURLを出力 |
| `kirocrew logout` | 全アクティブダッシュボードセッションを無効化（リフレッシュチェーン含む）。**⚠️ v0.3.0のCHANGELOGはこれを新規変更として記載しているが、この記述は`64060f3`時点で既に存在した。下記「[`kirocrew logout` の変更に関する食い違い](#kirocrew-logout-の変更に関する食い違い裁定しない)」参照** |
| `kirocrew manifest` | ユーザーエイリアス自動入力済みのSlackマニフェスト生成 |
| `kirocrew update` | 最新版へ更新（git fetch→上流コミットをピン留め→**この venv が `requires-python` を満たさないリビジョンは拒否**（v0.7.0）→ピン留めしたコミットへhard reset＋再ビルド。分岐したチェックアウトは拒否され、`--force`でローカルコミットを破棄） |
| `kirocrew status` | 実行中Gatewayの統計を表示 |
| `kirocrew stop [--port N]` | Gateway停止（サービス認識。稼働中ならsystemd/launchdサービスを停止） |
| `kirocrew restart [--port N]` | Gateway再起動 |
| `kirocrew service install/uninstall/status` | システムレベルのサービス化（systemd/launchd） |
| `kirocrew logs [-f]` | ログ表示（追従可） |
| `kirocrew cloud launch/list/status/connect/tunnel/login/logout/stop/start/destroy/iam-policy/iam-boundary/doctor` | 自分のAWSアカウント内のEC2インスタンスのプロビジョニング・接続・管理（サブコマンド一覧は`modules/cloud.md` 13行準拠の13件。`modules/cli.md` 243行は`tunnel`・`login`・`logout`・`iam-boundary`を含まない9コマンドのみを列挙）。**本サイトは以前 `logout` を載せていませんでしたが、v0.6.0 の `cloud.md` の一覧にも既に含まれていました** |
| `kirocrew security events [-n N]` | 最近のSEL監査イベント表示 |
| `kirocrew security verify` | SEL HMACチェーンの整合性検証 |
| `kirocrew secrets import [--apply]` | データホームの `.env` にある平文の認証情報を暗号化secrets vaultへ移す。**既定はdry-run**、`--apply`で保存し `.env` の該当行を `secret://KEY` 参照に書き換える。移すのは vault 対応の Jira 認証キー（`JIRA_API_TOKEN`・ホスト別 `JIRA_TOKEN_<HEX>`）のみ。`--file`オプションは無く、データホームの`.env`だけを読む。**`modules/cli.md` の「## Commands」表には無く、同ファイルの別節「## Secrets Command」（662-681行）・`docs/guides/secrets-env.md` 72-92行・`docs/system-specs/modules/security.md` 255行に記載**（v0.6.0 の `secrets-env.md` にも既に記載あり）。vault の保存・一覧・削除はダッシュボードの **Settings → Secrets**（CLIは移行のみ。保存値を読み戻すコマンドは意図的に無い） |
| **`kirocrew file-delivery approve`**（v0.7.0） | 認証情報らしい内容を検出して`file_send`が配送を拒否したファイルについて、ダッシュボード所有者が **Settings → Security** で承認を準備したあと、**Gatewayホスト上で直接実行**して1回限りの承認を完了する。エージェント自身はこの手順を完了できず、Computer Use有効時は拒否される。**`modules/cli.md` には記載がなく、公式 `security/` ページ「Approve a flagged file delivery」節（`docs_md/security.md` 176-185行）・`docs/feature-map/README.md` 298-330行・CHANGELOG.md v0.7.0節 445-448行に記載**。ネイティブWindowsでは承認は拒否される（[03_deployment/02_windows.md](../03_deployment/02_windows.md)参照） |
| `kirocrew snapshot [--keep N] [--list]` | 全状態のスナップショット作成（既定7件保持） |
| `kirocrew restore <file> [--mode replace\|merge] [--components X,Y] [--dry-run]` | スナップショット復元 |
| `kirocrew config get [key]` / `set <key> <val>` / `edit` | 設定操作 |
| `kirocrew config defaults [--adopt \| --keep <key>]` | 保存済みの値のうち、置き換えられた旧既定値のままのものを一覧表示する。`--adopt`で現在の既定値を採用、`--keep`で保存値を意図的なものとして記録する（公式`cli-reference`「`kirocrew config defaults`」節。v0.6.0の公式ページにも記載あり。`modules/cli.md`の表には記載なし） |
| `kirocrew memory list/search/stats/audit` / `export/import/migrate` | ベクトルメモリの検査・移行 |
| **`kirocrew memory backup/backups/restore`**（v0.7.0） | Global・宣言済みの名前付きV1・所有中のV2ストアのホットコピーを取る（`--keep <n>`）／ストアのコピーを新しい順に一覧（`--store`）／復元をステージする（`--store`・`--from <file>`。既定はそのストアの最新）。**V1・V2とも復元はGateway再起動時に有効化**される |
| **`kirocrew memory retired`**（v0.7.0） | セマンティックな書き込みで置き換えられたエピソードを一覧し、1件を復元する（`--restore <id>`・`--limit`）。既定ストアのみ |
| **`kirocrew memory carve --store <name>`**（v0.7.0） | crewストアの行をcarveファセットで絞り込み・集計する。ファセットはcrewのメモリストアにのみ存在する |
| `kirocrew policy show/validate/explain/profile` | 実効セキュリティポリシーの検査 |
| `kirocrew pod up/down/ls/status/token/url/scenarios/api/logs/exec/install/provision` | 孤立ワークツリーのテストGateway。**v0.7.0で3プラットフォーム対応**: ユーザー単位・非昇格のバックエンドとして Linux `systemd --user`・macOS `launchd`・Windows Task Scheduler（`schtasks.exe`）を使う。いずれも無いホストではサービスマネージャに触れる動詞が1行メッセージで拒否される。**`pod api` は Linux＋macOS のみ**（AF_UNIXソケットが必要なため）。**v0.6.0までは Linux `systemd --user` 限定**（macOS/Windowsでは拒否）だった |
| **`kirocrew pod prune --dry-run`**（v0.7.0） | 孤立したpodホームの一括削除をプレビューする（公式`cli-reference`「Isolated pods」節、CHANGELOG.md v0.7.0節 122-124行。`modules/cli.md`の表には記載なし） |
| **`kirocrew pod up --no-embeddings`**／**`--wait-secs <SECS>`**（v0.7.0） | 埋め込みモデルなしでpodを起動する（podの環境のみに `KIROCREW_SKIP_MODEL_DOWNLOAD=1`。メモリ・ナレッジ検索はキーワード検索にフォールバック）／`pod up` のヘルス待ち時間（既定90秒。5〜3600秒にクランプ。`KIROCREW_POD_HEALTH_SECS` でも指定可） |
| `kirocrew knowledge dedup [--apply]` | ソース横断の重複ナレッジ文書を統合（dry-run既定） |
| **`kirocrew knowledge stats [--json]`**（v0.7.0） | ナレッジライブラリのソース・文書・項目を合計とソース別に数える。**読み取り専用**（SQLite `mode=ro` で開き、スキーマ移行や孤立データの掃除は走らない） |
| `kirocrew cron preview <script>` | Scriptのcronをローカルで実MCPツール付きで実行（通知はキャプチャして表示） |
| `kirocrew workspace create/update --dir <name>` | ワークスペース管理（`--dir`はデータホームの厳密な子孫のみ許可） |
| `kirocrew computer doctor [--json]` | Computer Useの利用可否レポート |
| `kirocrew computer apps` | 操作可能な画面上アプリの一覧 |
| `kirocrew computer call <tool> [k=v ...]` | Computer Useツールを1件実行（デバッグ・再現用） |
| `kirocrew mcp-cron` / `mcp-core` / `mcp-computer` | kiro-cliが起動する内部MCPサーバ（`mcp-computer`は`argparse.SUPPRESS`で隠される） |
| `kirocrew --version` | 版表示 |
| `kirocrew eval [--all] [--scenario <name>]` | マルチセッション評価ハーネス実行（`kirocrew gateway --test-mode`を別シェルで起動している必要あり）。公式`cli-reference`ページの記載。`modules/cli.md` 259行は `kirocrew eval [scenarios…] [--all] [--judge]`（引数なしは約30秒のsmoke test）と記載 |
| `kirocrew telemetry status/disable/enable` | 匿名テレメトリの送信内容の確認・無効化・有効化（`modules/cli.md` 262行。リポジトリREADMEにも記載） |
| **`kirocrew tailnet status/up/down`** | ダッシュボードをTailscaleネットワークに公開してそのoriginを信頼する／公開をやめる（`modules/cli.md` 261行）。`up`の詳細は`docs/guides/remote-and-mobile.md` 286・290・294行（`tailscale serve`を実行、443でHTTPS、印字されるURLはセッションを含まない）と`docs/system-specs/modules/governance.md` 1310行（`capabilities.tailnet_origin`）（いずれも`21584ea`時点の行番号） |

> **注記（v0.7.2 で訂正）**: 本ページは以前、`eval`・`telemetry`・`tailnet` は主出典 `modules/cli.md`「## Commands」節に記載が無いと注記していました。これは `21584ea`（v0.3.0）時点の `modules/cli.md` に基づく記述で、**v0.6.0 の `modules/cli.md`（191・193・194行）には既に3つとも記載されていました**（v0.7.2 では 259・261・262行）。本サイトの注記が追随していませんでした。`modules/cli.md` を主出典としても、他の一次情報だけに存在するコマンドを見落とさないよう、複数系統を横断確認する方針は変わりません（`config defaults`・`pod prune`・`file-delivery`・`secrets import` は `modules/cli.md` の表に無く、公式ページや別節・ガイドで確認しています）。
>
> `modules/cli.md` の表には、本サイトの表記規約上のCLIサブコマンド許可リストに未登録のコマンド群も記載されています（エージェント定義・履歴統合・AppArmorプロファイル管理など）。本ページはこれらを掲載していません。

## v0.7.0での変更

- **新規コマンド**: `kirocrew ledger-sweep`（`--purge`）・`kirocrew app import`・`kirocrew knowledge stats`・`kirocrew memory backup/backups/restore/retired/carve`・`kirocrew file-delivery approve`・`kirocrew pod prune`・`kirocrew pod up --no-embeddings/--wait-secs`（上表の「（v0.7.0）」の行）
- **`kirocrew pod` が macOS（launchd）・Windows（Task Scheduler）でも動作**（CHANGELOG.md v0.7.0節 122-126行。下記「[クラウド・Pod](#クラウドpod見落としやすいコマンド群)」参照）
- **`kirocrew update` が `requires-python` を満たさないリビジョンを拒否**（CHANGELOG.md v0.7.0節 151-153行）
- **`kirocrew token` の失敗理由に「Gatewayが拒否した（HTTP 403）」が加わりました**（下記「[`token`の出力ストリーム契約](#tokenの出力ストリーム契約)」参照）

`kirocrew ledger-sweep`・`kirocrew memory backup/backups/restore/retired/carve`・`kirocrew pod up --no-embeddings/--wait-secs`・`token` の403の扱い: 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません（`modules/cli.md` 221-222・334-336・342-343・362-370行。いずれも v0.6.0 の `modules/cli.md` には無い記述です）。`app import`（CHANGELOG.md v0.7.0節 400-402行）・`knowledge stats`（同 263-267行）・`file-delivery approve`（同 445-448行）は CHANGELOG に記載があります。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/interfaces/cli-reference/>・<https://kiro.dev/docs/crew/security/>（Page updated 表記あり）

## v0.3.0での変更

### `kirocrew policy show` の詳細

`show`は拒否コマンドカタログを**カテゴリ別のグループ件数として要約**し、**`--ids`** を付けると各カテゴリのrule idを列挙します。**エンタープライズポリシーが有効かどうかに関わらず、全インストールで利用可能**です。

出典: `docs/system-specs/modules/cli.md` 135行（`21584ea`）／CHANGELOG.md v0.3.0節 176行「**`kirocrew policy show` lists the denied-command catalog**, so you can read what is blocked without going to the source」。拒否ルールの件数（137）は [01_features/09_security.md](../01_features/09_security.md)、ポリシーの配置は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

### `kirocrew logout` の変更に関する食い違い（裁定しない）

CHANGELOGはv0.3.0の破壊的変更として「**`kirocrew logout` now revokes refresh tokens**, not just access tokens（access tokenだけでなくrefresh tokenも失効させる）」を挙げています（19行）。**しかし本ページの主出典`modules/cli.md` 107行は、本サイトがv0.2.0として固定している`64060f3`の時点で既に「Revoke all active dashboard sessions, refresh chains included」と記述していました**（`21584ea`でも同一文）。

つまり**CHANGELOGはこれをv0.3.0の新規変更として記載しているが、モジュール仕様は`64060f3`時点で既に同じ内容を記述していた**という状態です。**どちらが実際の変更時期を示すか・なぜ食い違うのかは公式に説明がないため、本サイトは推測せず両方を記載します。**

出典: CHANGELOG.md v0.3.0節 19行（`21584ea`）／`docs/system-specs/modules/cli.md` 107行（`64060f3`・`21584ea`の両方で同一文であることを実測）。

## クラウド・Pod（見落としやすいコマンド群）

`kirocrew cloud` は**公式 `cli-reference` ページには独立した見出しがありません**が、リポジトリのモジュール仕様には完全なサブコマンド一覧が明記されており、**実在するコマンドです**。`kirocrew pod` は **v0.7.2 の公式 `cli-reference` ページに「Isolated pods」節が新設**されています（v0.6.0 の同ページには無し）。

- **`kirocrew cloud`**: 自分のAWSアカウントにKiroCrewのEC2インスタンスをプロビジョニングして管理する、人間向けのインストーラ／コントロールプレーン。`launch`は6段階のウィザード。`tunnel`はSSMポートフォワードでダッシュボードを開く、`login`はSSM経由で`kiro-cli`のデバイスコード／ソーシャルサインインを実行、`iam-boundary`はimmutableなインスタンス権限バウンダリを事前作成するワンタイムの管理者操作（`modules/cloud.md:13-16`）
- **`kirocrew pod`**: 孤立したワークツリーのテスト用Gateway（ソースworktreeを、専用のGateway・データホーム・ポート・プロセス境界で動かす）。**v0.7.0 で Linux `systemd --user`・macOS `launchd`・Windows Task Scheduler の3つのユーザー単位サービスマネージャに対応**しました。Windowsでは現在のユーザーがスケジュールタスクを作成できる必要があり、**`pod api` はWindowsで使えません**（Unixドメインソケットが必要。代わりに `pod token` と印字されるURLを自前のHTTPクライアントで使う）。メモリ／CPUの上限とクラッシュ時の再起動の2つは systemd だけが強制します（`modules/cli.md` 338行）。**v0.6.0 までは Linux の `systemd --user` のみで動作**し、macOS/Windowsではsystemdに触れるすべての動詞が1行メッセージで拒否されていました

出典（pod）: `docs/system-specs/modules/cli.md` 338行（`c67c506`）、公式 `cli-reference` ページ「Isolated pods」節、CHANGELOG.md v0.7.0節 122-126行。

## `token`の出力ストリーム契約

`kirocrew token` は**機械可読なstdout契約**を持ちます。stdoutにはダッシュボードURLのみが流れ、すべての失敗理由（無効なTTL・Gateway未起動・Gateway到達不可・**Gatewayによる拒否**・空トークン）はstderrに出力されます。この契約は、リモートでの`kirocrew token`実行結果をSSH経由でパースする`mint_remote_token`が、stdoutからJWTを正規表現抽出するために必要とされています。

**Gatewayによる拒否（v0.7.0）**: GatewayがHTTPエラーで応答した場合は、`Could not reach gateway` ではなく、Gateway自身の理由を伴う拒否（`Gateway refused the token request (HTTP 403): <error body>`）として報告されます。`/api/token/local` は、呼び出し元のホスト由来を証明できない場合（サンドボックス内の呼び出し元・解決できないピアpid・Linuxで別のnamespaceなど）に403を返し、本文に対処方法を示します。これをネットワーク障害として報告すると、運用者を誤った対処に導いていたためです（`modules/cli.md` 362-370行）。

出典: `docs/system-specs/modules/cli.md` 358-377行（`c67c506`）。

## 未確認事項

- `kirocrew --help` による実機での突合（未実施）

> 以前ここに記載していた「`eval`・`telemetry`が`modules/cli.md`から脱落している理由」は、v0.6.0 以降の `modules/cli.md` に両方とも記載されていることを確認したため外しました（上記「コマンド一覧」の注記参照）。

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)
- 上限値: [05_limits.md](05_limits.md)

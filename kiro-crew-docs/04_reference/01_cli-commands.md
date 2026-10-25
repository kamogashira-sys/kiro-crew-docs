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
**出典**（v0.9.0での再検証: コマンド一覧の突合・`cloud`の13サブコマンド・`cron add`・`memory create-store`・`snapshot --strict`・`desktop`・`token`の応答待ち）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.9.0）: <https://kiro.dev/docs/crew/interfaces/cli-reference/>（Page updated 2026-10-20）

---

## 📑 このページの内容

- [コマンド一覧](#コマンド一覧)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [クラウド・Pod（見落としやすいコマンド群）](#クラウドpod見落としやすいコマンド群)
- [`token`の出力ストリーム契約](#tokenの出力ストリーム契約)
- [未確認事項](#未確認事項)

---

> **方針の訂正**: 当初このページは公式 `cli-reference` とREADMEの2系統のみを突合して作成していましたが、**リポジトリのモジュール仕様（`docs/system-specs/modules/cli.md`）に、公式ページより遥かに完全なコマンド一覧が存在する**ことが判明したため全面改訂しました。一次情報ヒエラルキーの順位1（リポジトリのモジュール仕様）を最優先する本サイトの原則に従い、本ページは`modules/cli.md`を主たる出典とします。

## コマンド一覧

`docs/system-specs/modules/cli.md`「## Commands」節の実測（一部説明を要約）。行番号は v0.9.0（`99e6253`）のものです。v0.7.2 の再測定からの差分は、下の「[v0.9.0での変更](#v090での変更)」にまとめています。

| コマンド | 説明 |
|---------|------|
| `kirocrew chat [-m "msg"] [--model X]` | チャット。対話モード／単発メッセージ／モデル上書き |
| `kirocrew gateway [--slack-only] [--no-crons]` | Gateway起動（ダッシュボード＋メッセージングチャネル） |
| `kirocrew setup [--agent-only] [--slack]` | エージェント設定インストール・プロジェクトディレクトリ保存・認証情報設定 |
| `kirocrew doctor` | kiro-cliの導入・設定の妥当性検証 |
| **`kirocrew ledger-sweep`**（v0.7.0） | 終了済みに見えるsessionとconductor-workのledgerを一覧表示（種別・保存先ディレクトリ・ledgerキー・フェーズ／項目数・経過時間・該当理由）。**dry-runで、何も削除しない** |
| **`kirocrew ledger-sweep --purge [--older-than-days N] [--purge-unreadable]`**（v0.7.0） | dry-runが列挙したledgerを削除する。**取り消し不可・明示実行のみで、自動では動かない**（Gatewayのフック・履歴削除経路・MCPツールのいずれからも到達しない）。各削除は保存先のロック下で再判定され、ledgerが再び使われ始めていれば拒否される。**既定のアイドル期間は30日**（有限の非負数のみ。`nan`・`inf`は拒否）。読めない記録は`--purge-unreadable`を付けない限り残す |
| `kirocrew cron add/list/remove` | Cronジョブ管理。`add` は、エージェントのprompt／`--script FILE.py:FUNC`（`<config_dir>/crons/` に既にあるPython関数。CLIは登録するだけでコピーしない）／`--command SHELL` のいずれかを、`--every`／`--cron`／1回限りの `--at` のちょうど1つで登録する（v0.8.0）。`--timezone` は `--cron`・`--at` に効き、`--every` とは併用不可（既定は設定のグローバルタイムゾーン、無ければ UTC）。ほかに `--timeout-secs`（1〜86400、既定1800）、`--model`、`--[no-]persistent-session`、`--[no-]minimal-context`、`--hide-in-chat`。拒否は stderr に出て非0で終わる（argparse のフラグ組み合わせは2、検証・セキュリティ・ストアの拒否は1）。**`--managed-by KEY`**（v0.9.0）: 外部インストーラの provenance キー（ASCII `[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,199}`）をジョブに記録する。キーはストア全体で一意で、同じキーでの2回目の `add` は拒否される。再インストールは `cron remove --managed-by KEY` のあと `add`（新しい id が付く）。`remove` は id か `--managed-by` のどちらか一方（`modules/cli.md` 226行、公式 `cli-reference` ページ） |
| **`kirocrew cron pause/resume/trigger <id>`** | 一時停止／再開／即時実行。`pause`・`resume` は未知の id で exit 1（`Job not found`）、`trigger` は実行中のGatewayへの要求が失敗または拒否されたとき exit 1（`modules/cli.md` 436行） |
| `kirocrew spawn run/list` | サブエージェント管理。`list` は、未開始の accepted spawn（🕒と待ち理由）と再開待ちも表示する（`modules/cli.md` 227行） |
| `kirocrew app install/list/enable/disable/uninstall[--purge-data]/dev` | App Kit管理 |
| **`kirocrew app import <package-dir> [--out DIR] [--name NAME] [--install]`**（v0.7.0） | 他のエージェントハーネス向けのプラグインパッケージをAppディレクトリに変換し、対応先の無い要素をすべて報告する。**読み取りとコピーのみで、パッケージ内のものは何も実行しない** |
| `kirocrew learn add/list/remove` | 学習した修正の管理 |
| `kirocrew run TASK.md` | 仕様ファイルから自律タスクを実行 |
| `kirocrew token` | 認証トークン付きダッシュボードURLを出力 |
| `kirocrew logout` | 全アクティブダッシュボードセッションを無効化（リフレッシュチェーン含む）。**⚠️ v0.3.0のCHANGELOGはこれを新規変更として記載しているが、この記述は`64060f3`時点で既に存在した。下記「[`kirocrew logout` の変更に関する食い違い](#kirocrew-logout-の変更に関する食い違い裁定しない)」参照** |
| `kirocrew manifest` | ユーザーエイリアス自動入力済みのSlackマニフェスト生成 |
| `kirocrew update` | 最新版へ更新（git fetch→上流コミットをピン留め→**この venv が `requires-python` を満たさないリビジョンは拒否**（v0.7.0）→ピン留めしたコミットへhard reset＋再ビルド。分岐したチェックアウトは拒否され、`--force`でローカルコミットを破棄）。**wheel インストール（gitチェックアウト無し）は導入形態で分岐**する（v0.9.0 の仕様書）: 管理対象 venv は自前のエンジンで更新し、pipx はインストーラを再実行する（Windows 非対応）。利用者が管理する素の `pip install` 環境は exit 1 で拒否し、その場の upgrade コマンドと Gateway 再起動コマンドを示す（署名付きの upgrade コマンドを示せないときはその旨を示す）。更新後、実行中のGatewayが自分のポートを所有し local secret を持つ場合に限り `POST /api/update/revalidate` で更新バッジの再確認を依頼する（失敗しても exit code は変わらない）（`modules/cli.md` 1222-1294行） |
| `kirocrew status` | 実行中Gatewayの統計を表示 |
| `kirocrew stop [--port N]` | Gateway停止（サービス認識。稼働中ならsystemd/launchdサービスを停止）。`--port` を渡すとサービスの短絡を迂回する。**`--port PORT --expect-pid PID`**（v0.9.0 の仕様書）は、呼び出し側（デスクトップアプリの固まったGateway再起動）がGatewayを特定済みのときの絞った停止で、`os.pidfd_open` と `signal.pidfd_send_signal` が無いホスト（macOS・Windows）では signal を送らず exit 1（`modules/cli.md` 1404-1420行） |
| `kirocrew restart [--port N]` | Gateway再起動。detached fork の経路は、`/api/ready` が応答し run marker の pid が前のGatewayと異なるまで待ってから成功を表示する（v0.9.0 の仕様書）。置き換えが即死したら終了ステータスを示して exit 1、期限（既定60秒）内に ready にならなければ exit 1。期限は環境変数 `KIROCREW_RESTART_READY_TIMEOUT` で指定でき、15〜180秒に丸められる（`modules/cli.md` 1606-1626行） |
| `kirocrew service install/uninstall/status` | システムレベルのサービス化（systemd/launchd）。Linux の `status` は system／user の両スコープを表示し、いずれかが UP のときだけ exit 0。`uninstall` は自分が入れたユニットだけを消す（`sudo` で実行しない）（`modules/cli.md` 239-244行。詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)） |
| `kirocrew logs [-f]` | ログ表示（追従可） |
| `kirocrew cloud launch/list/status/connect/tunnel/login/logout/stop/start/destroy/iam-policy/iam-boundary/doctor` | 自分のAWSアカウント内のEC2インスタンスのプロビジョニング・接続・管理（サブコマンドは13件。**v0.9.0 では `modules/cli.md` 246行・公式 `cli-reference` ページ「Cloud」節（Page updated 2026-10-20）・`modules/cloud.md` 13行のいずれも13件すべてを列挙しています**。v0.7.2 の `modules/cli.md` は`tunnel`・`login`・`logout`・`iam-boundary`を含まない9コマンドのみを列挙していました。13件の列挙は v0.8.0 タグの `modules/cli.md` 243行で既に揃っており、その差は v0.8.0 で解消しています）。**本サイトは以前 `logout` を載せていませんでしたが、v0.6.0 の `cloud.md` の一覧にも既に含まれていました**。`launch` のフラグは下記「[クラウド・Pod](#クラウドpod見落としやすいコマンド群)」参照 |
| `kirocrew security events [-n N]` | 最近のSEL監査イベント表示 |
| `kirocrew security verify` | SEL HMACチェーンの整合性検証 |
| `kirocrew secrets import [--apply]` | データホームの `.env` にある平文の認証情報を暗号化secrets vaultへ移す。**既定はdry-run**、`--apply`で保存し `.env` の該当行を `secret://KEY` 参照に書き換える。移すのは vault 対応の Jira 認証キー（`JIRA_API_TOKEN`・ホスト別 `JIRA_TOKEN_<HEX>`）のみ。`--file`オプションは無く、データホームの`.env`だけを読む。**`modules/cli.md` の「## Commands」表には無く、同ファイルの別節「## Secrets Command」（761-775行）・`docs/guides/secrets-env.md` 94-98行・`docs/system-specs/modules/security.md` 656行に記載**（v0.9.0。v0.6.0 の `secrets-env.md` にも既に記載あり。v0.9.0 の表にも無いままです）。vault の保存・一覧・削除はダッシュボードの **Settings → Secrets**（CLIは移行のみ。保存値を読み戻すコマンドは意図的に無い） |
| **`kirocrew file-delivery approve`**（v0.7.0） | 認証情報らしい内容を検出して`file_send`が配送を拒否したファイルについて、ダッシュボード所有者が **Settings → Security** で承認を準備したあと、**Gatewayホスト上で直接実行**して1回限りの承認を完了する。エージェント自身はこの手順を完了できず、Computer Use有効時は拒否される。**`modules/cli.md` には記載がなく、公式 `security/` ページ「Approve a flagged file delivery」節（`docs_md/security.md` 198-205行。Page updated 2026-10-12）・`docs/feature-map/README.md` 327-345行・CHANGELOG.md v0.7.0節 1157-1160行（`99e6253`。v0.7.2 のタグでは 445-448行）に記載**（v0.9.0 の `modules/cli.md` の表にも無いままです）。ネイティブWindowsでは承認は拒否される（[03_deployment/02_windows.md](../03_deployment/02_windows.md)参照） |
| `kirocrew snapshot [--keep N] [--list] [--strict]` | 全状態のスナップショット作成（既定7件保持）。**`--strict`**（v0.9.0 の仕様書）: 書き出した bundle が要求したエントリを省いたとき exit 3（既定は、不完全でも bundle を書いたなら exit 0）。bundle は残り prune は保留される。exit 1 は「使える bundle が作れなかった」の意味のまま（`modules/cli.md` 251・312-318行）。`--allow-unpinned-staging` は、ディレクトリを descriptor で固定できないプラットフォームでパス名ベースのステージングを許可する（同 258-259行。`restore` にもある） |
| `kirocrew restore <file> [--mode replace\|merge] [--components X,Y] [--dry-run]` | スナップショット復元 |
| `kirocrew config get [key]` / `set <key> <val>` / `edit` | 設定操作 |
| `kirocrew config defaults [--adopt \| --keep <key>]` | 保存済みの値のうち、置き換えられた旧既定値のままのものを一覧表示する。`--adopt`で現在の既定値を採用、`--keep`で保存値を意図的なものとして記録する（公式`cli-reference`「`kirocrew config defaults`」節。v0.6.0の公式ページにも記載あり。`modules/cli.md`の表には記載なし） |
| `kirocrew memory list/search/stats/audit` / `export/import/migrate` | ベクトルメモリの検査・移行。`export`・`import` は `--store <name>`（既定は既定ストア）を取る。`--include-markdown` は既定ストア専用（`modules/cli.md` 418-420行）。公式 `cli-reference` ページが挙げる `memory` の動詞は `list`・`search`・`show`・`stats`・`audit`・`export`・`migrate`・`backup`・`backups`・`restore`・`carve`・`retired`・`import` |
| **`kirocrew memory create-store <name>`**（v0.9.0） | `config.json` の `memory_stores` に宣言した名前付きV1ストアのディレクトリを作る。宣言したストアは使用時には作られないため、ディレクトリを消したストアは、このコマンドを実行するまで欠けたままになる。既定ストア・宣言されていない名前・crewmateのストア（crewmate と一緒に作られる）は拒否される（stderr に1行、exit 1）。既にディレクトリがあれば何も変えない（`modules/cli.md` 423行、公式 `cli-reference` ページ） |
| **`kirocrew memory backup/backups/restore`**（v0.7.0） | Global・宣言済みの名前付きV1・所有中のV2ストアのホットコピーを取る（`--keep <n>`）／ストアのコピーを新しい順に一覧（`--store`）／復元をステージする（`--store`・`--from <file>`。既定はそのストアの最新）。**V1・V2とも復元はGateway再起動時に有効化**される |
| **`kirocrew memory retired`**（v0.7.0） | セマンティックな書き込みで置き換えられたエピソードを一覧し、1件を復元する（`--restore <id>`・`--limit`）。既定ストアのみ |
| **`kirocrew memory carve --store <name>`**（v0.7.0） | crewストアの行をcarveファセットで絞り込み・集計する。ファセットはcrewのメモリストアにのみ存在する |
| `kirocrew policy show/validate/explain/profile` | 実効セキュリティポリシーの検査 |
| `kirocrew pod up/down/ls/prune/status/token/url/scenarios/api/logs/exec/install/provision` | 孤立ワークツリーのテストGateway。**v0.7.0で3プラットフォーム対応**: ユーザー単位・非昇格のバックエンドとして Linux `systemd --user`・macOS `launchd`・Windows Task Scheduler（`schtasks.exe`）を使う。いずれも無いホストではサービスマネージャに触れる動詞が1行メッセージで拒否される。**`pod api` は Linux＋macOS のみ**（AF_UNIXソケットが必要なため）。**v0.6.0までは Linux `systemd --user` 限定**（macOS/Windowsでは拒否）だった |
| **`kirocrew pod prune [--older-than D] [--all] [--dry-run] [--json]`**（v0.7.0） | 孤立したpodホームを一括で回収する。`--older-than` の既定は `3d`。`--dry-run` はプレビュー。**`modules/cli.md` の表には v0.9.0 の 426行で載りました**（v0.7.2 の表には無く、公式`cli-reference`「Isolated pods」節とCHANGELOG.md v0.7.0節で確認していました） |
| **`kirocrew pod up --no-token`**（v0.9.0 の仕様書） | メンバートークンを作らずにpodを起動する。`pod.token` の監査行は `skipped`（`reason=no-token`）、`--json` は空のトークンを返す（`modules/cli.md` 430行） |
| **`kirocrew pod up --no-embeddings`**／**`--wait-secs <SECS>`**（v0.7.0） | 埋め込みモデルなしでpodを起動する（podの環境のみに `KIROCREW_SKIP_MODEL_DOWNLOAD=1`。メモリ・ナレッジ検索はキーワード検索にフォールバック）／`pod up` のヘルス待ち時間（既定90秒。5〜3600秒にクランプ。`KIROCREW_POD_HEALTH_SECS` でも指定可） |
| `kirocrew knowledge dedup [--apply]` | ソース横断の重複ナレッジ文書を統合（dry-run既定） |
| **`kirocrew knowledge stats [--json]`**（v0.7.0） | ナレッジライブラリのソース・文書・項目を合計とソース別に数える。**読み取り専用**（SQLite `mode=ro` で開き、スキーマ移行や孤立データの掃除は走らない） |
| `kirocrew cron preview <script>` | Scriptのcronをローカルで実MCPツール付きで実行（通知はキャプチャして表示） |
| `kirocrew workspace create/update --dir <name>` | ワークスペース管理（`--dir`はデータホームの厳密な子孫のみ許可） |
| `kirocrew computer doctor [--json]` | Computer Useの利用可否レポート |
| `kirocrew computer apps` | 操作可能な画面上アプリの一覧 |
| `kirocrew computer call <tool> [k=v ...]` | Computer Useツールを1件実行（デバッグ・再現用） |
| **`kirocrew desktop metrics/tunnel`**（v0.9.0 の仕様書） | デスクトップアプリ向けの補助コマンド。`metrics` はアプリが記録したプロセスごとの CPU・メモリを表示する（`--json`、`--top`）。`tunnel` は（`--host`・`--local-port`・`--remote-port` を指定して）アプリが remote crew へ張る SSH フォワードをクライアント専用モードで維持する。アプリが起動し、拒否されたホストやポートで exit 2、SIGTERM・SIGINT・stdin の EOF で exit 0。Windows では提供されない（`modules/cli.md` 435行、`instances.md` の tunnel_keeper の節） |
| `kirocrew mcp-cron` / `mcp-core` / `mcp-computer` | kiro-cliが起動する内部MCPサーバ（`mcp-computer`は`argparse.SUPPRESS`で隠される） |
| `kirocrew --version` | 版表示 |
| `kirocrew eval [--all] [--scenario <name>]` | マルチセッション評価ハーネス実行（`kirocrew gateway --test-mode`を別シェルで起動している必要あり）。公式`cli-reference`ページの記載。`modules/cli.md` 263行は `kirocrew eval [scenarios…] [--all] [--judge]`（引数なしは約30秒のsmoke test）と記載 |
| `kirocrew telemetry status/disable/enable` | 匿名テレメトリの送信内容の確認・無効化・有効化（`modules/cli.md` 266行。リポジトリREADMEにも記載） |
| **`kirocrew tailnet status/up/down`** | ダッシュボードをTailscaleネットワークに公開してそのoriginを信頼する／公開をやめる（`modules/cli.md` 265行）。`up`の詳細は`docs/guides/remote-and-mobile.md` 286・290・294行（`tailscale serve`を実行、443でHTTPS、印字されるURLはセッションを含まない）と`docs/system-specs/modules/governance.md` 1310行（`capabilities.tailnet_origin`）（いずれも`21584ea`時点の行番号） |

> **注記（v0.7.2 で訂正）**: 本ページは以前、`eval`・`telemetry`・`tailnet` は主出典 `modules/cli.md`「## Commands」節に記載が無いと注記していました。これは `21584ea`（v0.3.0）時点の `modules/cli.md` に基づく記述で、**v0.6.0 の `modules/cli.md`（191・193・194行）には既に3つとも記載されていました**（v0.7.2 では 259・261・262行、v0.9.0 では 263・265・266行）。本サイトの注記が追随していませんでした。`modules/cli.md` を主出典としても、他の一次情報だけに存在するコマンドを見落とさないよう、複数系統を横断確認する方針は変わりません（`config defaults`・`pod prune`・`file-delivery`・`secrets import` は `modules/cli.md` の表に無く、公式ページや別節・ガイドで確認しています）。
>
> `modules/cli.md` の表には、本サイトの表記規約上のCLIサブコマンド許可リストに未登録のコマンド群も記載されています（エージェント定義・履歴統合・AppArmorプロファイル管理など）。本ページはこれらを掲載していません。

## v0.9.0での変更

v0.9.0 に「Before you upgrade」節はありません。CHANGELOG.md v0.9.0節が CLI の変更として説明するのは `kirocrew memory create-store`・`kirocrew cron add --managed-by`・`kirocrew cloud launch` の `--ami`／`--extra-packages` の3点です（同 125-130行）。それ以外は **v0.9.0 タグの `modules/cli.md` で確認した内容で、CHANGELOG/Release 本文は説明していません**（`cloud` を除く各項目は、v0.8.0 タグの `modules/cli.md` に無いことを確認済み。`cloud` の13サブコマンドは v0.8.0 タグの `modules/cli.md` 243行に既にあり、下記のとおり v0.9.0 での新規ではありません）。

- **新しいサブコマンド語 `kirocrew desktop`**（`metrics`・`tunnel`）。`modules/cli.md` の表のセルが `kirocrew <語>` で始まるサブコマンド語は、v0.7.2・v0.8.0 の 40 語から v0.9.0 で 41 語になりました（新規は `desktop` のみ。消えた語はありません）
- **公式 `cli-reference` ページに「Cloud」節が新設されました**（v0.7.2 の取得内容には独立した見出しがなく、v0.9.0 の取得内容にある。Page updated 2026-10-20）。同じ13件を列挙しています。13サブコマンドが `modules/cli.md` に揃ったのは v0.8.0 で、v0.8.0 タグの `modules/cli.md` 243行が13件を列挙しています（v0.7.2 の同行は9件。v0.9.0 では246行）。`launch` のフラグは下記「[クラウド・Pod](#クラウドpod見落としやすいコマンド群)」を参照してください
- `kirocrew memory create-store`、`kirocrew cron add --managed-by`（`cron remove --managed-by`）、`kirocrew snapshot --strict`、`kirocrew pod up --no-token`、`kirocrew pod prune` の表への掲載（上の表の各行）
- `kirocrew update` の wheel インストールでの導入形態別の挙動、`kirocrew stop --port PORT --expect-pid PID`、`kirocrew restart` の readiness 待ち（上の表の各行）
- `kirocrew token` の「Gatewayが20秒以内に応答しない場合」の扱い（下記「[`token`の出力ストリーム契約](#tokenの出力ストリーム契約)」）
- `kirocrew spawn list` が未開始の accepted spawn を表示する、履歴統合を強制するコマンドは有界のパスで進むため、大きなバックログは `partially consolidated, N message(s) remain` で終わることがあり、その場合は再実行する。`spawn list` の表示については `modules/cli.md` 227行、統合のコマンドは同 262行

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>、<https://kiro.dev/docs/crew/interfaces/cli-reference/>（Page updated 2026-10-20）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.9.0節 125-130行（`99e6253`）

## v0.8.0での変更

- **`kirocrew cron add` が、すべての種類のジョブを登録できるようになりました**: script・command・1回限りのジョブが、ダッシュボードと同じオプションを取ります（CHANGELOG.md v0.8.0節 491-492行）
- **`kirocrew doctor` が、ビルドとずれたスキルを報告します**: skill-view の別名の滞留数も数えます（同 493-494行）。`doctor` の現在のチェック項目は [03_deployment/05_troubleshooting.md](../03_deployment/05_troubleshooting.md) を参照してください

出典: CHANGELOG.md v0.8.0節 489-495行（`99e6253`）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.7.0での変更

- **新規コマンド**: `kirocrew ledger-sweep`（`--purge`）・`kirocrew app import`・`kirocrew knowledge stats`・`kirocrew memory backup/backups/restore/retired/carve`・`kirocrew file-delivery approve`・`kirocrew pod prune`・`kirocrew pod up --no-embeddings/--wait-secs`（上表の「（v0.7.0）」の行）
- **`kirocrew pod` が macOS（launchd）・Windows（Task Scheduler）でも動作**（CHANGELOG.md v0.7.0節 122-126行。下記「[クラウド・Pod](#クラウドpod見落としやすいコマンド群)」参照）
- **`kirocrew update` が `requires-python` を満たさないリビジョンを拒否**（CHANGELOG.md v0.7.0節 151-153行）
- **`kirocrew token` の失敗理由に「Gatewayが拒否した（HTTP 403）」が加わりました**（下記「[`token`の出力ストリーム契約](#tokenの出力ストリーム契約)」参照）

`kirocrew ledger-sweep`・`kirocrew memory backup/backups/restore/retired/carve`・`kirocrew pod up --no-embeddings/--wait-secs`・`token` の403の扱い: 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません（`modules/cli.md` の v0.7.2 のタグでの行番号は 221-222・334-336・342-343・362-370行。v0.9.0 のタグでは 224-225・418-424・431-432・449-461行）。いずれも v0.6.0 の `modules/cli.md` には無い記述です。`app import`（CHANGELOG.md v0.7.0節。v0.7.2 のタグでは 400-402行）・`knowledge stats`（同 263-267行）・`file-delivery approve`（同 445-448行）は CHANGELOG に記載があります。

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

**v0.9.0 でも継続しています**: CHANGELOG.md v0.3.0節（v0.9.0 のタグでは 2255-2256行）は同じ記述で、`modules/cli.md` 235行（`99e6253`）は「Revoke all active dashboard sessions, refresh chains included」と記述しています（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

## クラウド・Pod（見落としやすいコマンド群）

`kirocrew cloud` は、**v0.7.2 の公式 `cli-reference` ページには独立した見出しがありませんでした**が、リポジトリのモジュール仕様には完全なサブコマンド一覧が明記されており、**実在するコマンドです**。**v0.9.0 の公式 `cli-reference` ページには「Cloud」節が新設され**、13サブコマンドを列挙し、`launch` のフラグを説明しています（Page updated 2026-10-20）。`kirocrew pod` は **v0.7.2 の公式 `cli-reference` ページに「Isolated pods」節が新設**されています（v0.6.0 の同ページには無し）。

- **`kirocrew cloud`**: 自分のAWSアカウントにKiroCrewのEC2インスタンスをプロビジョニングして管理する、人間向けのインストーラ／コントロールプレーン。`launch`は6段階のウィザード。`tunnel`はSSMポートフォワードでダッシュボードを開く、`login`はSSM経由で`kiro-cli`のデバイスコード／ソーシャルサインインを実行、`iam-boundary`はimmutableなインスタンス権限バウンダリを事前作成するワンタイムの管理者操作（`modules/cloud.md:13-16`）
- **`kirocrew cloud launch` のフラグ**（公式 `cli-reference` ページ「Cloud」節、`modules/cloud.md` 171-181行）:
  - `--size <tier>`: インスタンスのサイズ階層（既定は balanced、または対話ピッカー）
  - `--subnet <SUBNET_ID>`: ネットワーク自動検出の代わりに、その正確なサブネットへ起動する。インターネットへの出口が必要
  - `--ami <AMI_ID>`（v0.9.0）: 最新の Amazon Linux 2023 の代わりに、自分の AMI から起動する。サイズ階層のアーキテクチャに一致し、AL2023 互換であること
  - `--extra-packages <PKGS>`（v0.9.0）: インスタンスに追加で入れる dnf パッケージ（カンマ区切り。例 `gh,jq`）。dnf が見つけられない名前は警告付きで飛ばされる（`/var/log/kirocrew-setup.log`）。名前は英数字と `. _ + -` で先頭は英数字、全体で256文字以内、重複は除かれる
  - `--new`: 保存済みのインスタンスを再開せず、別の新しいインスタンスを作る
  - `-y`, `--yes`: 既定を受け入れ、プロンプトなし
  - `--ami`・`--extra-packages` は**新しい箱にだけ**効く。既存スタックを再開する場合、対話では警告、`--yes` では失敗する（`--new` を使う）。ランチャはイメージを事前検査しない: アーキテクチャ違いはスタック作成時に失敗し、`dnf` や `cfn-signal` が無いイメージはブートストラップで失敗またはタイムアウトする（`modules/cloud.md` 171-181行、`docs/guides/cloud-instance-ssm-vs-ssh.md` 103-112行）
- **`kirocrew pod`**: 孤立したワークツリーのテスト用Gateway（ソースworktreeを、専用のGateway・データホーム・ポート・プロセス境界で動かす）。**v0.7.0 で Linux `systemd --user`・macOS `launchd`・Windows Task Scheduler の3つのユーザー単位サービスマネージャに対応**しました。Windowsでは現在のユーザーがスケジュールタスクを作成できる必要があり、**`pod api` はWindowsで使えません**（Unixドメインソケットが必要。代わりに `pod token` と印字されるURLを自前のHTTPクライアントで使う）。メモリ／CPUの上限とクラッシュ時の再起動の2つは systemd だけが強制します（`modules/cli.md` 338行）。**v0.6.0 までは Linux の `systemd --user` のみで動作**し、macOS/Windowsではsystemdに触れるすべての動詞が1行メッセージで拒否されていました

出典（pod）: `docs/system-specs/modules/cli.md` 426-432行（`99e6253`。v0.7.2 のタグでは 338行）、公式 `cli-reference` ページ「Isolated pods」節、CHANGELOG.md v0.7.0節（v0.7.2 のタグでは 122-126行）。

## `token`の出力ストリーム契約

`kirocrew token` は**機械可読なstdout契約**を持ちます。stdoutにはダッシュボードURLのみが流れ、すべての失敗理由（無効なTTL・Gateway未起動・Gateway到達不可・**Gatewayによる拒否**・空トークン）はstderrに出力されます。この契約は、リモートでの`kirocrew token`実行結果をSSH経由でパースする`mint_remote_token`が、stdoutからJWTを正規表現抽出するために必要とされています。

**Gatewayによる拒否（v0.7.0）**: GatewayがHTTPエラーで応答した場合は、`Could not reach gateway` ではなく、Gateway自身の理由を伴う拒否（`Gateway refused the token request (HTTP 403): <error body>`）として報告されます。`/api/token/local` は、呼び出し元のホスト由来を証明できない場合（サンドボックス内の呼び出し元・解決できないピアpid・Linuxで別のnamespaceなど）に403を返し、本文に対処方法を示します。これをネットワーク障害として報告すると、運用者を誤った対処に導いていたためです（`modules/cli.md` 362-370行）。

**応答待ち（v0.9.0 の仕様書）**: Gateway が要求を受け付けても 20秒の予算（`_TOKEN_REQUEST_TIMEOUT`）内に応答しない場合は、「Gateway on port N is up but did not answer within 20 s (busy)」と報告され、「Could not reach gateway」にはなりません。読み取りタイムアウトと、タイムアウトを包んだ `URLError` は busy として数え、接続拒否は「Could not reach gateway」のままです。負荷のかかった healthy な Gateway が 12〜14秒で応答することがあり、それを到達不能と呼ぶと、動いている Gateway を再起動する誤った対処に導くため、と仕様書は説明しています（`modules/cli.md` 463-470行）。本内容は CHANGELOG/Release 本文では確認していません。

出典: `docs/system-specs/modules/cli.md` 358-377行（`c67c506`。v0.9.0 のタグでは 449-470行）、463-470行（`99e6253`）。

## 未確認事項

- `kirocrew --help` による実機での突合（未実施）
- `kirocrew logout` の変更時期（上記「[`kirocrew logout` の変更に関する食い違い](#kirocrew-logout-の変更に関する食い違い裁定しない)」。**継続**。裁定しない）

> 以前ここに記載していた「`eval`・`telemetry`が`modules/cli.md`から脱落している理由」は、v0.6.0 以降の `modules/cli.md` に両方とも記載されていることを確認したため外しました（上記「コマンド一覧」の注記参照）。

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>
- 設定キー: [02_configuration-keys.md](02_configuration-keys.md)
- 上限値: [05_limits.md](05_limits.md)

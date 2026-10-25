# 匿名利用テレメトリ

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew>（README「Anonymous usage telemetry」節 243-325行）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [2つの信号（既定オン）](#2つの信号既定オン)
- [送信される5フィールド](#送信される5フィールド)
- [App インストールレシート](#appインストールレシート)
- [旧仕様との差分](#旧仕様との差分)
- [無効化の3経路（ローカル設定）](#無効化の3経路ローカル設定)
- [ローカル設定を上書きする2つの経路](#ローカル設定を上書きする2つの経路)
- [メトリクス／OTLPエクスポート（別系統・既定オフ）](#メトリクスotlpエクスポート別系統既定オフ)
- [アプリ内 session-pulse アンケート](#アプリ内-session-pulse-アンケート)
- [送られないもの](#送られないもの)
- [未確認事項](#未確認事項)

---

## 2つの信号（既定オン）

Kiro Crewは**匿名の1日1回のハートビート**を送信します。これにより開発者はどれだけのコピーが稼働中か、どのリリース・Python マイナー版・インストール経路のサポートが必要かを把握できます。

公式カタログからのインストール・更新成功後には、**匿名のApp単位のレシート**も送信されます。**両方の信号が既定でオンで、同じ制御方法を使います。** ただし**最初の送信は、初回起動時のプライバシー開示（Privacy 章）が表示されるまで保留されます**。

仕様書（`metrics.md` 1732-1745行）は、最初のハートビートが Privacy 章の確認（`dashboard.privacy_acked`）まで保留されると記述しています。`kirocrew telemetry enable|disable` も、ヘッドレスホスト向けにこのフラグを立てます。ゲートは**初回送信だけ**に掛かり（`beacon.is_first_send()`）、送信済みのインストールは再度ゲートされません。`dashboard.privacy_acked` は `dashboard.onboarded` にフォールバックするため、Privacy 章が存在する前に初回起動を終えた利用者が再びゲートされることはありません。インストールレシートも同じ判定でゲートされます。

（v0.7.2 以前の本ページは「両方の信号が既定でオン」とだけ記載していました。初回送信の保留に関する README の文は、v0.7.2 の README にはなく、v0.8.0 の README から存在します。）

## 送信される5フィールド

**正確に以下の5フィールドのみが、1日最大1回送信されます。**

| フィールド | 例 | 理由 |
|-----------|-----|------|
| ランダムなインスタンスID | `9c75560d…`（UUID4） | 稼働中のコピー数を数えるため。初回起動時に一度生成され、ホスト名・ユーザー名・MAC・IP・アカウントとは無関係。インストールされたコピーを識別するが人を識別しない |
| アプリ版番号 | `0.1.2` | 使われているリリースの把握。**リリース番号のみ**（`-nightly.20260731t065756`のようなビルドスタンプは送信前に除去される。ビルドごとのタイムスタンプはほぼユニークで特定のマシンを識別する助けになるため） |
| Pythonマイナー版 | `3.12` | 最小要件をいつ上げられるか判断するため |
| インストール経路（Install path） | `dmg` | 実際に使われている配布形式の把握 |
| 初回送信フラグ（First-send flag） | `1` / `0` | 初めて送信に成功したインストールか、既存のインストールか |

> **項目名の修正**: 本サイトは v0.7.2 以前、これらを「インストールチャネル」「初回起動フラグ」と記載していました。README の項目名は **Install path** と **First-send flag** で、理由欄も上記の内容です（README 273-274行）。送信されるのが5フィールドであること、各フィールドの例は変わっていません。

## Appインストールレシート

公式カタログからのインストール・更新成功後に、同じテレメトリホストへ `/b/1/install/<app-slug>?t=<token>&k=<fresh|update>&v=<release>` へのGETが1回送信されます。`t` は、ローカルに保存される**レシート専用の秘密値**（receipt secret。ハートビートのインスタンスIDとは独立）をキーとした、`app-install:<slug>` に対する HMAC-SHA256 の先頭32桁の16進文字列です。この秘密値はマシンの外へ送信されず、異なる App のトークン同士も、ハートビートのインスタンスIDともリンクできません。そのため、インストール済みAppのプロファイルを組み立てることはできません。秘密値を永続化できない場合、レシートは送信されません。

仕様書（`metrics.md` 1786-1792行）は、秘密値を 64桁の16進のランダム値で、初回使用時に生成し、データホームに `app_receipt_secret` として owner-only で保存すると記述しています。ハートビートのインスタンスIDから独立させる理由として、収集側がハートビートからインスタンスIDを既に保持しているため、同じ鍵だと公開スラッグに対するトークンを再計算し、1つのインストールのレシートを App 間でリンクできてしまうことを挙げています。

（v0.7.2 以前の本ページは「`t` はローカルのbeaconインストールIDをキーとしたHMAC-SHA256」「生のインストールIDは決して送信されません」と記載していました。v0.8.0 で改訂された README の記述に合わせて修正しました。）

レシートはバンドル済みまたはエディション提供の公式カタログエントリに限られます。ユーザー設定のレジストリ・ローカルディレクトリインストール・自己登録されたAppからは何も送信されないため、プライベートなApp名がマシンから出ることはありません。

## 旧仕様との差分

**以前は9フィールドでした。** リリースチャネル・OS・CPUアーキテクチャ・ガバナンス姿勢は**削除されました**。それぞれ単体では粗い情報でしたが、インスタンスIDが安定しているため、これらの属性がすべて同じコピーを描写し、組み合わせることでどの単一フィールドが示すよりも狭いグループに絞り込めてしまうためです。

Kiro Crewは独自のアカウントシステムを持たず、`kiro-cli`がモデルアクセスに使うKiroサインインは決して読み取られたり送信されたりしません。1人が3台のマシンでKiro Crewを動かせば3つのCrewとして数えられます（「ユーザー」ではなく「**Daily Active Crews**」として報告）。

## 無効化の3経路（ローカル設定）

1. ダッシュボードの **Settings → Privacy → Send anonymous usage heartbeat**（初回起動オンボーディングの最終ステップにも同じスイッチがある）
2. `kirocrew telemetry disable`（`config.json`に永続化）
3. `KIROCREW_TELEMETRY_DISABLED=1`（環境変数。前2者を上書きする）

```bash
kirocrew telemetry disable        # config.jsonに永続化
export KIROCREW_TELEMETRY_DISABLED=1   # シェル・コンテナ単位
kirocrew telemetry status         # 送信内容を正確に表示
```

ダッシュボードのトグルと`kirocrew telemetry disable`は同じ設定を書くため、いずれか一方が再起動・アップグレードを跨いで有効です。`KIROCREW_TELEMETRY_DISABLED`は両方を上書きします（設定時はダッシュボードのトグルが無効化されその旨が表示されます）。

## ローカル設定を上書きする2つの経路

上記の3経路はいずれもローカルのユーザー設定です。以下の2条件はローカル設定にかかわらずテレメトリを無効化します。

1. **CI環境、または`KIROCREW_HOME`が`~/.kiro/crew`以外を指す場合**: 自動的にオフになります（開発用インスタンスやpodは決してカウントされません）
2. **Enterprise administratorによる強制無効化**: セキュリティポリシーの`capabilities.telemetry`エントリで、ローカル設定にかかわらず両方の送信信号をブロックできます。設定されている場合、ダッシュボードのトグルは変更不可であることを表示します

```json
{"version": 1, "boot": {"fail_closed": true},
 "capabilities": {"telemetry": {"enabled": false}}}
```

> **policy層のみで有効**: `docs/system-specs/modules/governance.md` は、この強制無効化を「**POLICY LAYER ONLY**」と明記しています。判定は `layer == "policy"` を要求するため、**Level-2 profile** に `capabilities.telemetry.enabled: false` を書いてもビーコンは抑止されません（読み取り専用ビューアがその行を `profile` 由来の governed として表示する場合でも同じです）。同じ記述は v0.6.0 タグの同ファイルにもあり、v0.7.x 以降での変更ではありません（本サイトが v0.7.2 以前は記載していなかった事項です）。
>
> `capabilities.telemetry` が統制するのは、ハートビート・インストールレシートに加え、アプリ内 session-pulse アンケート（下記）の3つです。3つは同じ `beacon.telemetry_permitted` の判定を通り、仕様書はこれらを「the repo's only default-on egress family」と記述しています（`governance.md` 2707-2718行）。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/governance.md>（2707-2718行・2773-2776行）
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## メトリクス／OTLPエクスポート（別系統・既定オフ）

> **⚠️ 本ページのここまでの内容とは別の仕組みです。混同しないでください。**
>
> - **①匿名利用テレメトリ**（本ページの上記すべて）: **既定オン**。`kirocrew telemetry enable/disable/status` で操作します
> - **②メトリクス／OTLPエクスポート**（この節）: **既定オフ**。`telemetry.enabled` で操作します
>
> 名前が似ていますが、設定キー・既定値・送信先・目的がいずれも異なります。

**v0.6.0 でメトリクスの計測範囲が広がりました。** CHANGELOG は「Every turn reports its tokens, spend and latency across cron, heartbeat, …」と記述しています。

`docs/system-specs/modules/metrics.md` は、これを OpenTelemetry SDK（Apache-2.0 / CNCF）上に構築された **local-first** のメトリクステレメトリと説明し、**Default OFF**（`telemetry.enabled: false`）と明記しています。無効時は「all metric call sites are cheap no-ops and nothing is written or exported, **byte-identical to no telemetry**」であり、`mcp_gateway.enabled`／`skills.lazy_load` と同じ opt-in 規約に従います。

### 収集と送出は別のスイッチ

`docs/guides/telemetry-otlp-export.md` は「Collection and egress are deliberately separate switches」と明記しています。**収集を有効にしてもデータはどこにも送られません。**

| 設定 | 既定 | 意味 |
|---|---|---|
| `telemetry.enabled` | **`false`** | 何も記録されません。メトリクスの呼び出し箇所は安価な no-op になります |
| `telemetry.otlp_endpoint` | **`""`（空）** | **マシンから何も出ません。** ローカルの JSONL シンクのみ |
| OTLP エクスポータ用パッケージ（`opentelemetry-exporter-otlp-proto-http`） | **未インストール** | 別途インストールするまで、OTLP エクスポータはインポートできません |

送出（egress）にはエンドポイントの設定**と** OTLP エクスポータ用パッケージのインストールの**両方**が必要です。ローカルシンクは OTLP に置き換わるのではなく**追加**されるため、エンドポイントを設定してもダッシュボードは動き続けます。エンドポイントを設定していてもパッケージが無い場合、Kiro Crew は警告を記録してローカルのみのまま動きます（起動に失敗しません）。

**エクスポータのインストール方法**（`telemetry-otlp-export.md` 33-49行）:

- ソースチェックアウトからは、editable な Kiro Crew のインストールを置き換えずに、宣言されている extra を入れます: `pip install -e ".[otlp]"`
- 既存のインストールには、extra が固定している配布物を直接入れます: `pip install "opentelemetry-exporter-otlp-proto-http==1.44.0"`
- このプロジェクトは既定のパッケージインデックスで公開されていないため、`pip install "kirocrew[otlp]"` は**サポート対象のコマンドではありません**（ガイドの記述）。エクスポータは OTLP over HTTP のみで、gRPC はありません

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** `docs/system-specs/modules/metrics.md`（470行・1332行）は、この仕組みを `kirocrew[otlp]` extra として表現しています。`docs/guides/telemetry-otlp-export.md`（45-48行）は `pip install "kirocrew[otlp]"` がサポート対象のコマンドではないと記述し、ソースチェックアウトでは `pip install -e ".[otlp]"` を示しています。

環境変数 `KIROCREW_TELEMETRY` は、`1`・`true`・`yes`・`on` で収集を有効にし、`0`・`false`・`no`・`off` で強制的に無効にします。設定フラグより優先されますが、制御するのは**ローカル収集だけ**で、ネットワーク送出を有効にすることはありません。`telemetry.enabled` が `false` で `KIROCREW_TELEMETRY` も未設定のときは何も記録されません。

### `telemetry.enabled` の切り替え方

`telemetry.enabled` は、`config.json` の `"telemetry": {"enabled": true}`、`kirocrew config set telemetry.enabled true`、ダッシュボードの Settings → Privacy にある recording switch、環境変数のいずれでも切り替えられます。いずれも Gateway の再起動は不要です（仕様書によると 30 秒ごとに同意状態を再判定します）。

- recording switch は、`telemetry.otlp_endpoint` が設定されているとき、`true` への切り替えが HTTP 409 で拒否されます。ローカル専用の切り替えとして提示されたスイッチが送出を始めてしまうのを防ぐためです。`false` への切り替えは常に許可されます
- 環境変数・`config.local.json` のオーバーレイ・OTLP エンドポイントがある場合、スイッチは無効表示になります
- この recording switch は、上記①の匿名ハートビートのトグルとは独立した別のスイッチです

### OTLP のリソース属性とゲージ

- `service.instance.id` は、永続化された匿名のインストール ID（仕様書は `beacon.install_id` と記述）で、再起動をまたいで同一です。Crew が明示的に設定し、ホスト名やユーザー名から導出しません。`process.pid` は別の属性です。ほかに `os.type`・`host.arch`・`process.runtime.name`・`process.runtime.version`・`host.cpu.logical_count`・`service.version`（リリース番号のみ）があります（`metrics.md` 322-345行）。データホームに書き込めずインストール ID を作れない場合、Kiro Crew は明示的な ID を省き、SDK が per-process の識別子に戻ることがあります（ガイドの記述）
- v0.7.2 のガイド `telemetry-otlp-export.md` は、309-312行で `service.instance.id` を SDK の検出器が生成するプロセスごとの新しい値と記述し（gateway の再起動のたびに系列が新しくなる）、157行では同じ属性がインストールを識別するものでプロセスを識別するものではないとも記述しており、ガイド内で記述が分かれていました。v0.9.0 のガイドは、永続化されたインストール識別子に統一されています（320行）。CHANGELOG に対応する記述は見当たりません
- 累積系の5つの instrument は、単調増加の sum ではなく、プロセス開始からの合計値を保持するゲージとしてエクスポートされます。`rate()`・`increase()` のようなカウンタ用の関数は適用せず、連続するサンプルの差を取ります（ガイドの記述）

> ⚠️ **`telemetry.enabled` の説明は、出典によって異なります。本サイトは裁定しません。** 公式 configuration ページ（Page updated 2026-10-20）は、`telemetry.enabled` を「Enables local latency and fault-rate metrics; it does not export them」と記載し、README（323-325行）は `telemetry.enabled` を「local-only performance metrics that never leave your machine」と記述しています。一方、`metrics.md`（144行・153-157行）と `telemetry-otlp-export.md`（19-23行）は、`telemetry.otlp_endpoint` を設定し、OTLP エクスポータ用パッケージをインストールした場合に、集約メトリクスが OTLP で送出されると記述しています。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/metrics.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/telemetry-otlp-export.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）

## アプリ内 session-pulse アンケート

`capabilities.telemetry` の統制対象には、ハートビート・インストールレシートに加えて、アプリ内の session-pulse アンケート（`dashboard/handlers/feedback.py`）があります。ハートビートとレシートは固定の匿名ペイロードを送りますが、アンケートは**利用者自身が送信した回答と、匿名の per-install ID**（`beacon.install_id`）を送ります。送信は、同じ判定（初回プライバシー開示を含む）が許可した後に限られます（`governance.md` 2707-2718行）。

- ダッシュボードのバックエンドが、同期プロキシとして AWS Aperture の session-pulse アンケート（form `KiroCrew`/`SessionFeedback`/`1.0.1`）に転送します
- 再表示の判定は、フロントエンドの30日の `localStorage` クールダウンと、サーバー側の per-user dedup の二重です
- 本内容は v0.7.2 の仕様書にも同じ記述があり、本サイトが未掲載だったものです
- アンケートが利用者に表示される条件と画面上の位置は、一次情報で**未確認**です

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/learn-cron-dashboard.md>（3466行）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## 送られないもの

プロンプト・モデルの応答・ファイル内容・ファイルパス・リポジトリ／ブランチ名・認証情報・環境変数・ホスト名・ユーザー名・IPアドレスは**決して送信されません**。受信側のCDNは**クライアントIPアドレスをログに記録しない**設定になっており、ログ配信にそのフィールドが含まれないため、IPは一切保存されません。

## 未確認事項

- アンケートが利用者に表示される条件と画面上の位置（「アプリ内 session-pulse アンケート」）
- 公式 configuration ページ・README（`telemetry.enabled` はローカルのみ）と、仕様書・ガイド（エンドポイント設定時は OTLP で送出できる）の記述の食い違いは、裁定していません
- 本ページの匿名ハートビートの記述は、v0.9.0 タグ（`99e6253`）の README「Anonymous usage telemetry」節で確認済みです。この節は v0.8.0 で改訂されており（Install path・First-send flag の項目名、receipt secret、初回送信の保留）、v0.7.2 以前の本ページはその改訂前の記述でした

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew>（README「Anonymous usage telemetry」節）
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

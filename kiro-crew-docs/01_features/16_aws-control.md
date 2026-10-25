# AWS Control（builtin App）

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://kiro.dev/docs/crew/apps/aws-control/>（Page updated 2026-09-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/aws-control.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**（v0.8.0・v0.9.0 での確認。Access boundary・Backup・Dashboard surface の節）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/aws-control.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [概要](#概要)
- [有効化](#有効化)
- [ビューの構成](#ビューの構成)
- [アカウントの接続と切断](#アカウントの接続と切断)
- [Drive（S3ドライブ）](#drives3ドライブ)
- [Backup（クラウドバックアップ）](#backupクラウドバックアップ)
- [Bill（費用）](#bill費用)
- [安全性モデル](#安全性モデル)
- [Snapshot-to-S3 の廃止との関係](#snapshot-to-s3-の廃止との関係)
- [v0.8.0での変更](#v080での変更)
- [v0.9.0での確認事項](#v090での確認事項)
- [未確認事項](#未確認事項)

---

## 概要

**v0.5.0 で追加され、v0.6.0 で Overview が加わった builtin App です。既定では無効です。**

公式ページは「接続済みの AWS アカウントを1つのサーフェスにまとめる builtin Crew app」と説明し、**4領域**を扱うと記述します。

1. アカウントの健全性の確認
2. プライベートな S3 ドライブ内のファイル閲覧・管理
3. クラウドバックアップの実行
4. 請求費用の確認

公式ページは「Every paid service asks for your confirmation before its first use per account, and every change is on the record」と記述しています（課金が発生するサービスはアカウントごとに初回利用前に確認を求め、変更はすべて記録される）。

## 有効化

**このアプリは無効な状態で出荷されます（"It ships disabled by default"）。**

1. **Apps → Library** を開く
2. **AWS Control** を見つけて **Enable** をクリック

## ビューの構成

AWS Control は **Overview** で開きます。公式ページは、Overview に接続済みアカウント・キーの健全性・ドライブ使用量・月初からの支出・共有リンク・バックアップスケジュールが表示されると記述します。`modules/aws-control.md` 1653-1660行（v0.9.0）は、この6つが指標カード（metric card）の並びで、その下に Accounts カードと Cloud drive カードが横に並び、さらに Paid services カードがあると記述します。Overview 自体は、課金サービスの2つの同意ゲートのほかに変更操作を持ちません。

**⚠️ ビューの呼称が出典間で食い違っています。本サイトは裁定せず両方を記載します。**

| 出典 | rail から開けるビューの呼称 |
|---|---|
| 公式ページ `apps/aws-control/` | **Files** / **Artifact library** / **Backup** / **Share links** |
| CHANGELOG v0.6.0 節（"Your cloud drive, inside the app"） | **Files** / **Library** / **Backup** / **Access** |
| `modules/aws-control.md` 4-5行（v0.9.0、`99e6253`） | 「Drive, Library, Backup, cost, share, and IAM-policy views」（Drive／Library／Backup／費用／共有／IAM ポリシーのビュー）。ダッシュボード面の記述（1653行以降）は Overview・Accounts・Usage の各ペインに言及する |

各ペインは独自の URL を持つため、同じビューへ直接戻れます。

## アカウントの接続と切断

Crew は **deploy engine が保守する AWS プロファイルレジストリ**を使います。接続済みの各アカウントには、設定されたプロファイルが生きた ID に解決されるかどうかに基づく健全性インジケータ（**ok** / **degraded** / **unknown**）が表示されます。

アカウントを削除するには、そのアカウント行のオーバーフローメニューから **Remove from AWS Control** を選びます。

> **⚠️ 削除の範囲**: 公式ページは「This removes only the local registry entry and its consent grants. It does not modify accounts, resources, or data in AWS」と明記しています。**ローカルのレジストリエントリと同意grantのみを削除し、AWS 側のアカウント・リソース・データには一切触れません。**

## Drive（S3ドライブ）

Drive ビューは**アカウントにスコープされた、プライベート・バージョニング有効・所有者限定の S3 バケット**です。公式ページは「It is not a general S3 browser」（汎用の S3 ブラウザではない）と明記しています。

バケットは**確認後にのみ作成**され、作成時に次のハードニングが適用されます。

- ブロックパブリックアクセス
- AES-256 サーバーサイド暗号化
- バケット所有者の強制（bucket owner enforced）
- バージョニング有効

バケットは3つのセクションを別々のキープレフィックスで持ちます。

| セクション | プレフィックス | 内容 |
|---|---|---|
| **Files** | `drive/` | 一般のドライブファイル。画像・動画・音声・PDF・テキストをダウンロードせずプレビューダイアログで開ける。ファイル名・パスでの検索、メニューからの **Rename**、ドラッグでの移動、ドロップでのアップロード、インライン確認付きの削除が可能 |
| **Artifact library** | `artifacts/` | クラウドの Artifact ライブラリ。保存または公開したレポート・出力・ファイル |
| **Backup** | `backup/` | Crew インストールのクラウドスナップショット |

**共有リンクは常に期限切れになります。明示的に共有を作成しない限り、何も公開されません。**

## Backup（クラウドバックアップ）

対応する2種類のバックアップがあります。

| 種類 | 内容 | プレフィックス |
|---|---|---|
| **Snapshot** | 標準の Crew スナップショット（memory・crons・config・skills・workspace・notifications・security コンポーネント） | `backup/snapshots/` |
| **Sessions archive** | セッションのトランスクリプト履歴の全量（公式ページの記述。内訳は[v0.8.0での変更](#v080での変更)を参照） | `backup/sessions/` |

**作成**: Backup ビューで **Back up now** をクリックします。ページから離れてもバックアップは継続し、**Backup** に戻れば現在の状態が見られます。

**復元**: 公式ページは「A restore downloads the archive to the `/restore/` directory on the gateway host and gives you the local path. **It does not hot-swap live state directly**」と記述します。復元を適用するには、ダウンロードしたパスを指定して `kirocrew restore` を実行します。

```bash
kirocrew restore ~/.kiro/crew/restore/<snapshot-file>.tar.gz
```

これはローカルスナップショットと同じ replace / merge の復元フローに従います。詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md) と [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) を参照してください。

**夜間バックアップ**: アカウントごとに夜間バックアップのトグルがあります。夜間ループはバックグラウンドで動き、設定したトグルによって認可されます。夜間バックアップの既定、スキップ、失敗時の再試行、保持の仕様は[v0.9.0での確認事項](#v090での確認事項)を参照してください。

## Bill（費用）

Bill ビューは月初からの支出と当月の予測合計を AWS サービス別に表示します。

- データは **Cost Explorer** から取得し、**日次でキャッシュ**される（CE のデータは約24時間遅延）
- キャッシュの経過時間が数値と並べて表示される
- **予測はローカルでの算術**（月初からの実績を1か月に外挿）であり、**AWS Budgets リソースは作成されない**
- アカウントで Cost Explorer が有効になっている必要がある

## 安全性モデル

公式ページが挙げる5原則です。

| 原則 | 内容 |
|---|---|
| **課金サービスの同意ゲート** | AWS 課金が発生するすべてのサービスは、アカウントごとに初回利用前に確認を求める |
| **監査証跡** | すべての mutation が Crew の監査ログに記録される |
| **所有者限定ドライブ** | S3 バケットはプライベートで、プロビジョニングしたアカウントに限定される。共有リンクは期限切れになり、既定では何も公開されない |
| **読み取り専用の請求** | Bill ビューは Cost Explorer データを読むだけで、請求設定を変更しない |
| **切断はローカルのみ** | アカウント削除はローカルのレジストリエントリと同意grantのみを削除し、AWS リソースには触れない |

監査ログ（SEL）全体の仕組みは [09_security.md](09_security.md) を参照してください。

リポジトリの仕様書（`modules/aws-control.md` 10-23行、v0.9.0、`99e6253`）は、上記に加えてルートの境界を次のように記述しています。

- AWS Control のすべてのルートは、アプリが無効な場合と、ダッシュボード所有者でない呼び出しを拒否し、どちらの拒否も SEL に記録します
- 変更を伴うルートは、制限付きセッションからの呼び出しも拒否し、成功・拒否・`AWSError` のいずれも SEL に記録します
- アカウントを対象とする操作は、登録済みプロファイルを解決したあとに実際の ID を再確認します。別のアカウントに付け替えられたプロファイルは、URL が示すアカウントのためには使われず拒否されます

## Snapshot-to-S3 の廃止との関係

**v0.5.0 で `kirocrew snapshot --to s3://…`・`--aws-profile`・`s3://` fetch パスが削除され、クラウドバックアップは AWS Control app に移りました**（CHANGELOG v0.5.0 節 Before you upgrade 2番目）。引き換えにスナップショットは live state への restore（replace / merge・rollback ledger 付き）を獲得しています。

CLI からの S3 連携は使えません。詳細は [02_update/01_changelog.md](../02_update/01_changelog.md) の v0.5.0 節を参照してください。

## v0.8.0での変更

公式 AWS Control ページ（Page updated 2026-09-12）は v0.7.2 時点から差分がなく、CHANGELOG の v0.8.0・v0.9.0 節には AWS Control の項目が見つかっていません。次の内容は v0.8.0 以降の仕様書で確認したもので、CHANGELOG と公式ページは説明していません（v0.7.2 の `modules/aws-control.md` に `Layer B`・`conversations/`・`sessionsIncludeLayerB` の記述は見つかっていません）。

**Sessions archive の中身（`modules/aws-control.md` 895-945行、v0.9.0、`99e6253`）**

- **crew 側**（データホーム配下の表示用トランスクリプト）は常にアーカイブされます
- **kiro-cli 側**（Layer B。モデルのコンテキストウィンドウをバイト単位で写した、編集されていないもの）は、**運用者がそのアカウントについて許可した場合にだけ**アーカイブされます。既定は含めません（withhold）。保存値が読めない場合や真偽値でない場合も含めません
- 許可すると、アーカイブに `conversations/` ルートも加わります。kiro-cli の端末会話を、その CLI 自身の SQLite ストアから、テーブルの許可リスト（allowlist）に従って行単位でコピーしたものです。ストア本体はトークンを含むためアーカイブされません。各テキストセルはエグレス編集（egress redaction）を受けます。ストアにはこの製品と無関係の kiro-cli の利用も記録されます
- 実行記録には `layer_b` が残り、実際にアーカイブに入ったものを示します。書き出しが保持しているものより少ないときは、`conversations_skipped` に理由が残ります
- 許可はアカウントごとに、アプリの状態ファイル `backup.json` の `sessionsIncludeLayerB` として保存され、`config.json` のキーではありません（963-966行）
- 公式ページは Sessions archive を「your full sessions transcript history」と記述しています。この「full」と、上記の許可による内訳の関係は確認できていません

## v0.9.0での確認事項

次の内容は v0.9.0 の `modules/aws-control.md` で確認したもので、v0.7.2 の仕様書にも同じ項目の記述があります（本ページは従来、公式ページを主な出典としていたため掲載していませんでした）。公式ページと CHANGELOG はこれらを説明していません。

- **夜間バックアップは既定でオフ**: 仕様書は「`nightly` ships off」と記述します（570行）。**夜間のセッションアーカイブは別の許可**（`backup.nightly_sessions_enabled`）で、キーがなければ偽として読まれます。夜間スナップショットを有効にしても、トランスクリプトについては何も許可したことになりません（1534-1541行）。スナップショットとセッションの2種は、それぞれ別の呼び出し・別の監査対象で実行されます（1545-1550行）
- **変更がなければアップロードしない**: 前回のアーカイブが、記録されたキー・長さ・バージョンでドライブに残っていると確認できたときだけ、アップロードせずに `unchanged` として記録します。確認できない場合はすべてアップロードします（516-552行）。成功したスキップでは、ラベルの公開も保持の掃引も行いません
- **失敗した夜間実行の再試行**: 夜間ループの半時間ごとの wake は due の確認間隔で、再試行間隔ではありません。連続して失敗すると、待ち時間は 0・1時間・2時間・4時間・8時間・以降は12時間になります（`NIGHTLY_RETRY_BACKOFF_SECS`。1405-1406行・1436-1438行）
- **保持（古いアーカイブの削除）は既定でオフ**: アカウントの `backup.json` に整数のカウントがあるときだけ有効になります。既定のカウントはありません。`POST /backup/{account}/retention` でカウントを設定し、`null` で解除します。bool と範囲外の値は拒否されます。保持の掃引は、会話の書き出しの欠落（conversation-export gap）を報告した実行の最後には走りません（559-571行・625-640行）。ダッシュボードにこの設定の操作はなく、HTTP だけで設定・確認します（同 640-642行）
- **夜間バックアップの実行時刻**: 仕様書から、実行時刻の値は確認できていません（未確認）

出典: `modules/aws-control.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

## 未確認事項

- 健全性インジケータ 3値（ok / degraded / unknown）の判定条件の詳細（公式ページは「設定されたプロファイルが生きた ID に解決されるか」に基づくと記述する。仕様書 1687-1689行は、健全性が点とバッジの語で表現され、色だけで示されないと記述するが、3値の判定条件は確認できていない）
- 夜間バックアップの実行時刻と、タイムゾーンの扱い
- `docs/system-specs/modules/aws-control.md` の本文（2591行）のうち、本ページは Access boundary・Backup・Dashboard surface の節だけを確認している。Credentials and paid-service consent・Drive and destructive operations・Publishing and sharing の節と、公式ページにも CHANGELOG の AWS Control の項目にも説明がない "The crew bundle builder"（1826行以降）・"The crew container runtime"（1923行以降）は確認できていない
- Sessions archive の「full sessions transcript history」（公式ページ）と、許可による内訳（仕様書）の関係
- builtin App の総数（S12）— `src/` の解析が未承認のため未確認。詳細は [04_reference/05_limits.md](../04_reference/05_limits.md) を参照

> **解消済み**: 「Overview に表示される項目の完全な一覧」は、`modules/aws-control.md` 1653-1660行（`99e6253`）が、6つの指標カード（accounts・keys healthy of total・drive used・month-to-date spend・live share links・backup schedule）と Accounts・Cloud drive・Paid services の各カードを記述しているため、未確認事項から除きました（上記「ビューの構成」参照）。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/apps/aws-control/>
- 公式（Snapshot & restore）: <https://kiro.dev/docs/crew/features/snapshot/>
- Apps: [10_apps.md](10_apps.md)
- Artifact: [12_artifacts.md](12_artifacts.md)
- セキュリティ: [09_security.md](09_security.md)
- 常時運用とスナップショット: [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

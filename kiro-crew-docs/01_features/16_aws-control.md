# AWS Control（builtin App）

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://kiro.dev/docs/crew/apps/aws-control/>
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/aws-control.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

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

AWS Control は **Overview** で開きます。Overview には接続済みアカウント・キーの健全性・ドライブ使用量・月初からの支出・共有リンク・バックアップスケジュールが表示されます。

**⚠️ ビューの呼称が出典間で食い違っています。本サイトは裁定せず両方を記載します。**

| 出典 | rail から開けるビューの呼称 |
|---|---|
| 公式ページ `apps/aws-control/` | **Files** / **Artifact library** / **Backup** / **Share links** |
| CHANGELOG v0.6.0 節（"Your cloud drive, inside the app"） | **Files** / **Library** / **Backup** / **Access** |

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
| **Sessions archive** | セッションのトランスクリプト履歴の全量 | `backup/sessions/` |

**作成**: Backup ビューで **Back up now** をクリックします。ページから離れてもバックアップは継続し、**Backup** に戻れば現在の状態が見られます。

**復元**: 公式ページは「A restore downloads the archive to the `/restore/` directory on the gateway host and gives you the local path. **It does not hot-swap live state directly**」と記述します。復元を適用するには、ダウンロードしたパスを指定して `kirocrew restore` を実行します。

```bash
kirocrew restore ~/.kiro/crew/restore/<snapshot-file>.tar.gz
```

これはローカルスナップショットと同じ replace / merge の復元フローに従います。詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md) と [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) を参照してください。

**夜間バックアップ**: アカウントごとに夜間バックアップのトグルがあります。夜間ループはバックグラウンドで動き、設定したトグルによって認可されます。

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

## Snapshot-to-S3 の廃止との関係

**v0.5.0 で `kirocrew snapshot --to s3://…`・`--aws-profile`・`s3://` fetch パスが削除され、クラウドバックアップは AWS Control app に移りました**（CHANGELOG v0.5.0 節 Before you upgrade 2番目）。引き換えにスナップショットは live state への restore（replace / merge・rollback ledger 付き）を獲得しています。

CLI からの S3 連携は使えません。詳細は [02_update/01_changelog.md](../02_update/01_changelog.md) の v0.5.0 節を参照してください。

## 未確認事項

- Overview に表示される項目の完全な一覧（公式ページは接続済みアカウント・キーの健全性・ドライブ使用量・月初からの支出・共有リンク・バックアップスケジュールを挙げるが、網羅かは不明）
- 健全性インジケータ 3値（ok / degraded / unknown）の判定条件の詳細
- 夜間バックアップの実行時刻と、タイムゾーンの扱い
- `docs/system-specs/modules/aws-control.md` の本文（本サイトでは未精読。公式ページを主な出典としている）
- builtin App の総数（S12）— `src/` の解析が未承認のため未確認。詳細は [04_reference/05_limits.md](../04_reference/05_limits.md) を参照

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/apps/aws-control/>
- 公式（Snapshot & restore）: <https://kiro.dev/docs/crew/features/snapshot/>
- Apps: [10_apps.md](10_apps.md)
- Artifact: [12_artifacts.md](12_artifacts.md)
- セキュリティ: [09_security.md](09_security.md)
- 常時運用とスナップショット: [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

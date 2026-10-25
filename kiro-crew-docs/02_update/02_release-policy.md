# リリース方針

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/build/release.md>（「The three channels」節ほか）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://github.com/kirodotdev/KiroCrew>（README「Release channels」節）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [版番号の付け方](#版番号の付け方)
- [プレリリースの系統](#プレリリースの系統)
- [配布チャネル](#配布チャネル)
- [強制更新の下限（最小サポート版）](#強制更新の下限最小サポート版)
- [`[Unreleased]`を出典にしない理由](#unreleasedを出典にしない理由)
- [日付の食い違い](#日付の食い違い)
- [未確認事項](#未確認事項)

---

## 版番号の付け方

`vX.Y.Z` 形式です。実在する安定版は固定参照時点（2026-10-25）で **v0.1.0／v0.1.1／v0.1.2／v0.1.3／v0.2.0／v0.3.0／v0.4.0／v0.4.1／v0.5.0／v0.6.0／v0.7.0／v0.7.1／v0.7.2／v0.8.0／v0.9.0** の15件です（GitHub Releases実測、全95 Release中。プレリリースは79件。ほかに、版番号ではない Release `ffmpeg-decoder-7.1.1-r1`（2026-10-23公開、`prerelease` は false）が1件あります。プレリリースの件数は取得時点の値で、次期版の公開に伴って増えます）。

`ffmpeg-decoder-7.1.1-r1` の Release 本文は、Kiro Crew のデスクトップアプリとソースインストールのデコーダストアが使う、音声専用の最小構成の ffmpeg 7.1.1 デコーダと説明しています。`vX.Y.Z` 形式ではなく、安定版の15件には含めません。全95件には含まれます。

本サイトは安定版のみを扱う方針のため、プレリリースは本文の解説対象にしていません。

## プレリリースの系統

取得時点（2026-10-25）のプレリリース79件のうち、**v0.9.0 までの版の系統は74件**です。残る5件（`-insider.N` 4件・`-rc.N` 1件）は v0.9.0 より新しい版のプレリリース（取得時点の GitHub Releases では、同じ新しい base version の `-rc.N` 1件と `-insider.N` 4件）のため、本サイトは扱いません。以下は v0.9.0 までの版の74件の内訳で、サフィックスは**2系統**あり、版によって使い分けられています。

| サフィックス | 対象 | 件数 |
|---|---|---|
| `-rc.N` | **v0.2.0系のみ**（例: `v0.2.0-rc.1`） | 8件 |
| `-insider.N` | v0.1.0／v0.1.1／v0.1.2／v0.1.3／v0.4.0／v0.4.1／v0.5.0／v0.6.0／v0.7.0／v0.7.1／v0.7.2／v0.8.0／v0.9.0 系（例: `v0.1.3-insider.2`） | 66件 |

v0.8.0 系（9件）と v0.9.0 系（6件）は、安定版（v0.8.0・v0.9.0）が公開済みの系統です。

**v0.3.0系のプレリリースはGitHub Releases実測で0件**です（`v0.3.0` 本体のみで `-rc.N`・`-insider.N` いずれも存在しません）。

> **⚠️ 連番の最大値は件数ではありません。** 実測で欠番があります。
>
> | 系統 | 存在する番号 | 件数 | 欠番 |
> |---|---|---|---|
> | `v0.5.0-insider.N` | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11 | **10件** | `-insider.4` |
> | `v0.6.0-insider.N` | 1, 2, 3, 4, 6, 7 | **6件** | `-insider.5` |
> | `v0.7.0-insider.N` | 2, 3, 4, 5, 6, 8, 9 | **7件** | `-insider.1`・`-insider.7` |
> | `v0.7.1-insider.N` | 2 | **1件** | `-insider.1` |
> | `v0.7.2-insider.N` | 1, 2 | **2件** | なし |
> | `v0.8.0-insider.N` | 1, 4, 7, 8, 10, 11, 12, 14, 16 | **9件** | `-insider.2`・`-insider.3`・`-insider.5`・`-insider.6`・`-insider.9`・`-insider.13`・`-insider.15` |
> | `v0.9.0-insider.N` | 3, 4, 5, 6, 7, 9 | **6件** | `-insider.1`・`-insider.2`・`-insider.8` |
>
> 最大番号（11・7・9・16・9）を件数として扱うと誤りになります。欠番の理由は公式に説明がなく**未確認**です。

## 配布チャネル

Kiro Crew には Stable・Insider・Nightly の3チャネルがあります。リリース運用文書（`docs/build/release.md` 16-22行「The three channels」節）が、チャネルごとのトリガーと版の形を定めています。

| チャネル | 対象（`docs/guides/install.md` 166-168行） | トリガー（`docs/build/release.md` 18-22行） | 頻度 |
|---------|------|---------|------|
| **Stable** | 全員（既定） | 素の版タグ（例: `v0.2.0`）の push。その時点で候補として確認済みのコミットから、素の版番号で**再ビルド**する。候補の成果物をバイト単位で再公開するのは、`vars.STABLE_PROMOTE_BYTES` がその版を指定した場合だけ | 版タグの push 時。`release.md` 1383行は「Insider は stable と判断されるまで寝かせる。暦上の固定周期は無い」と記述 |
| **Insider** | パワーユーザー（機能を日〜週単位で早く受け取り、新しい不具合も受け入れる人） | プレリリースタグの push | タグの push ごと |
| **Nightly** | 開発チームとコントリビューター向けの、未テストの `main` HEAD | `main` HEAD から `nightly.yml`（cron `0 6 * * *`＝06:00 UTC）と手動実行 | 日次（06:00 UTC） |

> **⚠️ 出典の変更**: v0.7.2 までの README「Release channels」節にあった4列の表（対象・ビルド元・頻度）は、v0.9.0 の README（64-69行）には存在しません。v0.9.0 の README は同節を、Stable が既定・Insider がリリース候補・Nightly が `main` に従うという案内に縮め、現行のトリガー・版の形・昇格の挙動・頻度・更新レーンの意味は `docs/build/release.md` が定めると書いています。本ページの表は `release.md` と `install.md` から作り直しました。表の「対象」列の文言は `install.md` の記述に基づく本サイトの要約です。
>
> **出典間の参照切れ**: `docs/guides/install.md` 169行と `docs/guides/docker.md` 35行は、README の「Release channels」の表を参照していますが、v0.9.0 の README にその表はありません。
>
> **Insider のタグ形と実際の Releases**: `release.md` 21行は Insider の版の形を `<x.y.z>-rc.N` と記述し、643-645行は同じ base version では `-rc.N` に揃えるよう定めています。実際の GitHub Releases は `-insider.N` が主系統です（[プレリリースの系統](#プレリリースの系統)）。この経緯は公式に説明が見つかっていません（[未確認事項](#未確認事項)）。

各チャネルへの切替方法（出典はいずれも v0.9.0）:

- **CLI**: インストーラの `--channel` で指定する（`docs/guides/install.md` 159-170行）
- **Docker**: タグ `stable`／`latest`・`insider`・`nightly` で選ぶ（`docs/guides/docker.md` 25-29行）
- **デスクトップアプリ**: About から切り替えられ、更新後に Gateway がその場で再起動する。**v0.3.0で追加された切替手段で、3チャネルの構成自体は変わっていません**（v0.9.0タグの CHANGELOG 2357-2358行「Change release channel without reinstalling」）

v0.7.2 の README は「すべての導入経路（デスクトップアプリ・CLI・Docker イメージ）が同じ3チャネルを提供する」と記述していました。この文は v0.9.0 の README にありません。

手順の詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md) を参照してください。

## 強制更新の下限（最小サポート版）

**v0.5.0 で追加されました。** CHANGELOG は「A release can declare a minimum supported version — An install below the floor gets an update prompt that cannot be snoozed, skipped or dismissed」と記述します（v0.9.0タグの CHANGELOG 1736-1737行、`[0.5.0]` 節）。

`docs/build/release.md` 778行以降（v0.9.0。v0.7.2 では 728行以降）は仕組みをより詳しく説明しています。古いクライアントを動かし続けさせてはならないリリース（feed schema の破壊・プロトコルの破壊・後方互換のないデータ移行）が対象です。

| 要素 | 内容 |
|---|---|
| 宣言場所 | `packaging/MIN_VERSION` に**1行1つのリリース版**を記述（コメントと空行は無視。値の行が2つ以上あると publish が失敗する） |
| 伝搬 | その値を持つコミットから publish された CLI feed manifest が、任意項目の**署名付き `min_version` フィールド**として埋め込む |
| Gateway の挙動 | feed の定期チェック（normal feed check）時に下限と自分の版を比較する。**インストーラと同じピン留め鍵で manifest の署名を検証したあと**に比較する（`platform/feed_trust.py`）。版はまずチャネル単位で畳み込まれる（プロモートされた stable ビルドの `0.3.0rc13` スタンプは `0.3.0` リリースと同一とみなす） |
| 下限未満のとき | status frame と `GET /api/update/check` の `update_required` が true になり、ダッシュボードの更新モーダルが **snooze・skip・Escape を失う**（更新するまでプロンプトが出続ける）。**Gateway 自体は動作を続けます** |
| 失敗時 | 検証や解析の失敗は**ordinary な（dismiss 可能な）プロンプトに劣化**する。仕様書はこれを「the floor fails toward freedom, never toward coercion」と表現しています |
| インストーラ | フィールドの書式を検証するだけで、あとは無視する（常に署名された版をインストールする） |
| 企業ガバナンスのピン | `security_policy.json` の `updates.min_version` は**独立**しており、feed の下限と **OR** で結合される（`release.md` 805-807行は、どちらか一方だけでも更新が必須になると記述）。必須更新が実際に適用されるかどうかはインストール形態で異なる（下表） |

**政策側 `min_version` を下回ったときの扱い**（`docs/system-specs/modules/governance.md` 251-283行。v0.9.0。インストール形態ごとの区分は v0.7.2 の同文書にはありませんでした）: 政策（`security_policy.json`）を使う企業環境が前提で、`updates` キーを含むポリシーを使わないインストールには関係しません。仕様書は、更新を自動で取り込む形態では、下限を下回るホストはユーザーの `auto_update=false` を上書きして**必須更新**を取ると記述します。ただし起動そのものは拒否せず、解析できない下限は無視されます。

| インストール形態 | 下限未満のときの挙動 |
|---|---|
| ポリシープロバイダ（`check_command`） | チェックが版を報告するたびに適用する |
| git checkout | 主ブランチで、現在より新しい版を取り込める場合だけ適用する。下限未満でも新しい版が無い場合や、チェックアウトが分岐している場合は、通知とバッジの更新にとどまる。主ブランチ以外では適用しない |
| `cli.sh` の managed venv | feed に新しいビルドがあり、`source`（政策の取得元ピン）が許す場合にインストーラを再実行する。新しいビルドが無ければログを1行書くだけで再インストールしない |
| pip・pipx | 更新バッジを点灯するだけ |
| Docker・デスクトップアプリ同梱の Gateway（プロバイダ無し） | バックエンドからは適用しない（コンテナは新しいイメージが必要）。アプリ側の更新スイッチがオフなら「更新が見つかった」プロンプトを閉じられなくするだけで、オン（既定）なら下限は効果を持たない |

必須更新もアイドルを待って適用され、強制はされません。`release.md`（either alone makes the update mandatory という一文）と `governance.md`（形態ごとの区分）は記述の粒度が異なります。本サイトはどちらかを正とする裁定をせず、両方を示します。

## `[Unreleased]`を出典にしない理由

`CHANGELOG.md` 冒頭の `## [Unreleased]` 節は**未リリース**の項目であり、リリース済みの機能として扱うと誤情報になります。本サイトは常にこの節を出典から除外します。

> **⚠️ 現在この節は存在しません。** 固定参照時点（2026-10-25 / 版 v0.9.0）の `CHANGELOG.md` に `## [Unreleased]` 節はありません（実測0件。v0.8.0・v0.6.0 時点も0件）。リポジトリの開発方針文書は「**There is no `## [Unreleased]` section, and the gate refuses one.**」と明記し、保留中の内容を見るには `git log --oneline <last-tag>..HEAD` を読むよう指示しています（`docs/build/changelog.md` 23行）。
>
> gateの実体は `scripts/check_changelog_history.py` です。`docs/build/release.md` 1356-1358行（v0.9.0。v0.7.2 では 1275-1277行）は「There is no `## [Unreleased]` section to accumulate into and no in-progress prerelease heading to rename later — `scripts/check_changelog_history.py` refuses both」と記述し、**節を作ることも、進行中のプレリリース見出しを後で改名することも拒否される**としています。その結果、changelog の差分は新しい節をちょうど1つ足す形になります。`docs/build/changelog.md` 24-28行（v0.9.0）は、最新の系列のリリースは先頭に足し、旧い系列のパッチリリースは版順に `main` へミラーされて新しい系列の節の下に置かれる（リリースブランチ上の節とバイト単位で同一）と記述します。
>
> したがって現時点では除外すべき対象がありません。**節が復活した場合に備えて、除外方針そのものは維持します。**
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/build/changelog.md>
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
>
> v0.9.0 タグの `docs/build/changelog.md` 23行は v0.6.0・v0.7.2 タグと同じ文です。24-28行は上記のとおり改訂されています。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/build/release.md>
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
>
> 参考として、過去には存在していました（2026-08-16 時点の取得で約390行）。**この方針を述べた文の所在も版で移動しています**（v0.4.1 では `AGENTS.md` 254行、v0.6.0 では `docs/build/changelog.md` 23行）。

## 日付の食い違い

CHANGELOG.mdの日付とGitHub Releaseの公開日は**一致しません**（実測でCHANGELOGに版節を持つ13版すべてで食い違い。v0.1.0・v0.1.1 は CHANGELOG に版節がないため表に載せません）。CHANGELOG の日付は v0.9.0 タグの `CHANGELOG.md` の見出し、Release公開日は GitHub Releases の公開日時の日付部分です（タイムゾーン変換はしていません）。

| 版 | CHANGELOG.mdの日付 | Release公開日 |
|----|-------------------|-------------|
| v0.9.0 | 2026-10-09 | 2026-10-16 |
| v0.8.0 | 2026-10-08（v0.9.0 タグ時点。v0.8.0 タグ時点は 2026-09-27） | 2026-10-09 |
| v0.7.2 | 2026-09-28 | 2026-09-29 |
| v0.7.1 | 2026-09-24 | 2026-09-25 |
| v0.7.0 | 2026-09-15 | 2026-09-24 |
| v0.6.0 | 2026-09-05 | 2026-09-11 |
| v0.5.0 | 2026-08-29 | 2026-09-05 |
| v0.4.1 | 2026-08-28 | 2026-08-29 |
| v0.4.0 | 2026-08-25 | 2026-08-27 |
| v0.3.0 | 2026-08-17 | 2026-08-21 |
| v0.2.0 | 2026-08-09 | 2026-08-10 |
| v0.1.3 | 2026-08-07 | 2026-08-05 |
| v0.1.2 | 2026-07-30 | 2026-08-04 |

**本サイトはこれを裁定せず、両方を記載します**（[01_changelog.md](01_changelog.md)参照）。

公式（`docs/build/changelog.md` 38-39行。v0.9.0）は、CHANGELOG の見出しの日付を「節を書いた日で、リリース候補を切る時点。安定版タグを切るときに書き換えない」と定義しています。この定義の文は v0.7.2 タグの同ファイルにはありません。一方、表のとおり13版すべてで両者の日付が一致しません。

> **同じ版節の日付がタグによって異なる例**: `[0.8.0]` 節の見出しの日付は、v0.8.0 タグの CHANGELOG（5行）では 2026-09-27、v0.9.0 タグの CHANGELOG（187行）では 2026-10-08 です。節の本文は2つのタグで同一です（差分は見出し1行のみ）。Release 公開日は 2026-10-09。日付が変わった理由は公式に説明が見つかっていません（未確認）。また、v0.8.0 タグの CHANGELOG には `[0.7.2]` 節がなく、v0.9.0 タグの CHANGELOG では `[0.8.0]` 節の下（717行）にあります。
>
> **出典**: CHANGELOG.md v0.9.0節 5行・v0.8.0節 187行（`99e6253`）。v0.8.0 タグ（`4d205da`）の CHANGELOG.md 5行
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## 未確認事項

- 日付が食い違う個別の理由（公式は CHANGELOG の日付を「節を書いた日＝リリース候補を切る時点で、安定版タグを切るときに書き換えない」と定義している［`docs/build/changelog.md` 38-39行］が、13版すべてで食い違う理由と、`[0.8.0]` 節の日付が v0.8.0 タグ時点と v0.9.0 タグ時点で異なる理由は、公式に説明が見つかっていない。理由は未確認）
- v0.8.0 タグの CHANGELOG に `[0.7.2]` 節がない理由
- `-insider.N` の欠番（`v0.5.0-insider.4`・`v0.6.0-insider.5`・`v0.7.0-insider.1`・`v0.7.0-insider.7`・`v0.7.1-insider.1`、および v0.8.0 系の7件・v0.9.0 系の3件）の理由
- `packaging/MIN_VERSION` の現在の値（`src/`・`packaging/` はスナップショット取得対象外のため未確認）
- `-rc.N` から `-insider.N` へ切り替わった経緯（v0.2.0系のみ `-rc.N` である理由は公式に説明が見つかっていない。公式の運用文書 `docs/build/release.md` 21行・643-645行は Insider のタグ形を `-rc.N` と記述しており、GitHub Releases の実タグ［`-insider.N` が主系統］との食い違いの経緯も説明が見つかっていない）

## 関連リンク

- Releases: <https://github.com/kirodotdev/KiroCrew/releases>
- 更新履歴: [01_changelog.md](01_changelog.md)
- 導入経路: [03_deployment/01_installation.md](../03_deployment/01_installation.md)

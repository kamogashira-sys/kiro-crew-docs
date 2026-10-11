# Kiro Crew ドキュメント 更新手順書

本書は kiro-crew-docs の版更新（Kiro Crew の新しい安定版への追随）の手順の正本です。ローカルで作業する場合も、Kiro Web のクラウドセッション・Workflow で作業する場合も、本書に従います。

> **本書には版番号・件数などの値を書きません。** 値は版ごとに変わり、書き換え漏れの原因になるためです。値の正本は次のとおりです。
>
> - 正準値（SSoT）: 検証器の定数（§7.3 の許可定数）と [`scripts/kiro-crew-docs/ledgers/ssot-status.md`](../scripts/kiro-crew-docs/ledgers/ssot-status.md)
> - 固定参照時点（対象版・commit）: ルート [`README.md`](../README.md) の「更新範囲と参照時点」
> - 台帳: [`scripts/kiro-crew-docs/ledgers/`](../scripts/kiro-crew-docs/ledgers/)

## 目次

- §1 概要 / §2 重要な原則 / §3 一次情報ヒエラルキー / §4 正規化ルール
- §5 差分列挙と一次情報の取得 / §6 記述粒度 / §7 SSoT / §8 スコープ境界
- §9 Kiro Crew 固有の制約 / §10 ライセンス・再配布 / §11 作業フロー / §12 監視項目
- §13 クラウド版の工程表 / §14 SSoT 定義表 / §15 PR 本文の定型7節 / §16 監査ページ群
- §17 ページ編集の共通ルール / §18 版更新ごとの必須検査 / §19 禁止事項
- 付録A changelog エントリの書式 / 付録B 機能解説ページの書式

---

## 1. 概要

### 1.1 目的

Kiro Crew（OSS）の公式サイト・リポジトリの更新に、推測ゼロで追随するための手順を定めます。

### 1.2 Kiro Crew のリリース特性

- **OSS** であり、一次情報がリポジトリ（GitHub `kirodotdev/KiroCrew`）と公式サイト（`kiro.dev/docs/crew/`）の二重構造
- 版番号あり（`vX.Y.Z`）
- 版ごとの変更点の一次情報は GitHub の `CHANGELOG.md` と Releases。kiro.dev の `changelog/crew/` の扱いは §3.2 の確認方法に従う
- main ブランチが日次で動く
- 提供形態が複数ある（デスクトップアプリ／ワンライナー／Docker／ソース）
- OS で機能差がある（Windows に `not yet` の項目がある）

## 2. 重要な原則

1. **推測禁止**。公式・リポジトリに書かれていないことを書かない
2. **理由も推測しない**。公式が理由を明記していない限り「〜のため」を書かない
3. **未確認は明示**。確認できない事項は「未確認事項」節に置く
4. **値はリポジトリの実体から取る**。二次情報（Zenn 記事等）のみに依拠した数値を断定形で書かない
5. **各コミット前に機械検証**（§11.3）
6. **食い違いは裁定しない**。出典間で値が異なる場合は両方を記載する
7. **ローカル絶対パスを書かない**

### 2.1 食い違いの3類型

| # | 類型 | 例（SSoT の ID。§14） |
|---|------|------|
| ① | 同じものの値が違う | S3a: CHANGELOG 日付と Release 公開日。版ごとの実測値の正本は公開文書 [02_update/02_release-policy.md](../kiro-crew-docs/02_update/02_release-policy.md) の「日付の食い違い」表 |
| ② | 同一リポジトリ内の仕様書同士が食い違う | S15: Subagent 自動サイジング上限（`modules/subagent.md` と `modules/config.md`）。値は [04_reference/05_limits.md](../kiro-crew-docs/04_reference/05_limits.md) |
| ③ | 同じものを別の名前で呼ぶ | S22: サンドボックスモードの呼称（公式 docs と、README・内部ティア） |

いずれも両併記し、裁定しません。両併記が必須の項目は `check-consistency.py` の `DUAL_NOTATION` が対称性を検査します。

## 3. 一次情報ヒエラルキー（8順位）

| 順位 | 情報源 | 何に使うか | 注意 |
|-----|-------|-----------|------|
| 1 | リポジトリのソース／モジュール仕様（`docs/system-specs/`・`docs/architecture/`） | 仕様の最終根拠 | main ブランチは日次で動く。**参照時は commit SHA を記録** |
| 2 | リポジトリの README／ガイド | 導入・運用手順 | 同上 |
| 3 | 公式ドキュメント（`kiro.dev/docs/crew/` 配下。ページ数は sitemap の `docs/crew/` 全件） | 機能の公式な言い方 | 末尾スラッシュ必須。UA 必須 |
| 4 | CHANGELOG.md ＋ GitHub Releases | 版ごとの変更点 | 両者の日付が食い違う。両併記 |
| 5 | 公式ブログ | 設計意図・背景 | 発表時点の記述 |
| 6 | AWS 公式ブログ（日本語） | 日本語の公式用語 | 原文優先 |
| 7 | AWS Japan 社員の Zenn 記事 | 日本語の解釈・検証済み手順 | 「個人の見解」注記あり。仕様の根拠にしない |
| 8 | 実機確認 | 1〜7 で確定しない挙動 | 本サイトでは必須にしない |

### 3.1 適用原則

順位1・2（リポジトリ）が最も正確です。ただし、CLI サブコマンドの突合で `docs/system-specs/modules/cli.md` を検索対象に含めていなかった実例があります。リポジトリを調査する際は `docs/system-specs/` 全体を横断的に検索します。

### 3.2 出典にしないもの

- `docs/request-for-change/`（RFC・未確定）
- `docs/ci/`・`docs/build/`（開発者向け。**ただしリリース手順・changelog 運用の一次情報としては `docs/build/release.md`・`docs/build/changelog.md` を参照する**）
- 削除済み・移行専用の仕様書（`post-launch-removals.md` 等。冒頭に `removed`／`no longer exist`／`legacy`／`deprecated` の断りがあるもの）。版によって同名ファイルの性質が変わるため、固定版の本文で断りの有無を確認する。現行の判定はモジュール台帳 [`ledgers/modules.md`](../scripts/kiro-crew-docs/ledgers/modules.md)
- `## [Unreleased]`（固定版に節があるかを毎回確認する。復活した場合に備えて除外方針は維持する）
- プレリリース（`-insider.N`・`-rc.N`）

> 公開文書側の正本は [00_information/03_information-sources.md](../kiro-crew-docs/00_information/03_information-sources.md) の「出典にしないもの」表です。本節と食い違ったら公開文書側を実測で再確認し、両方を同期します。

**kiro.dev の `llms.txt` と `changelog/crew/` は、前提を置かずに毎回確認します。** 一次情報ヒエラルキーのどこに置くかは未決定（人の判断事項）です。

```bash
# kiro.dev changelog/crew の有無（HTTP ステータス）と、系列ページの有無
curl -sS -o /dev/null -w '%{http_code}\n' -A "Mozilla/5.0" "https://kiro.dev/changelog/crew/"
# llms.txt に crew の言及があるか（行番号付き）
curl -sS -A "Mozilla/5.0" "https://kiro.dev/llms.txt" | grep -n -i 'crew'
```

公開文書の一部と `.github/WORKFLOW.md` には、これらについての前提を書いた箇所があります。確認結果が前提と異なる場合は PR 本文⑥（§15）に書き、前提の修正は版更新とは別の PR で行います（版更新 PR の差分を版更新に限定するため）。

### 3.3 Zenn 記事の位置づけ

「個人の見解であり所属組織の公式見解ではない」旨の Publication 注記があるため、仕様の根拠にはせず、日本語表現・検証済み手順の出典として併記します。**0.1.2 時点の記事の値を、固定参照時点の最新安定版の値として書きません。**（固定版はルート `README.md` の「更新範囲と参照時点」表が正本です）

### 3.4 実機確認の位置づけ

1〜7 で確定しない挙動にだけ使います。本サイトでは実機確認を必須にしません。

## 4. 日付・版番号・SHA・名称の正規化ルール

- 日付は **ISO `YYYY-MM-DD`**。TZ 変換なし
- **CHANGELOG 日付と Release 日付は2列で併記**
- 版番号は `vX.Y.Z`（プレリリースは扱わない）
- **commit SHA は短縮7桁で記録**。取得日は本文に書かず出典行に書く
- **機能名は公式ナビの表示名を優先**し、URL スラッグは出典としてのみ使う（例: `features/cron` → 表示名「Scheduling」、`features/artifact-deploy` → 表示名「Artifacts」）
- **同じものを別の名前で呼ぶ出典がある場合は両併記**（例: S22 のサンドボックスの呼称）

## 5. 差分列挙と一次情報の取得

### 5.1 更新検知の4系統

```bash
# ① GitHub Releases
curl -s "https://api.github.com/repos/kirodotdev/KiroCrew/releases?per_page=100"
# ② CHANGELOG.md のハッシュ変化
curl -s "https://raw.githubusercontent.com/kirodotdev/KiroCrew/main/CHANGELOG.md" | sha256sum
# ③ 公式 sitemap の crew ページ数変化
curl -s -A "Mozilla/5.0" "https://kiro.dev/sitemap.xml"
# ④ GitHub Tree API の docs/ ファイル数変化
curl -s "https://api.github.com/repos/kirodotdev/KiroCrew/git/trees/main?recursive=1"
```

機械検知は `make check-kiro-crew-freshness`（4系統）で行います。クラウドの版更新では `make check-kiro-crew-cloud-freshness`（`--strict --release-only`）を使い、出力の `freshness-result: rc=<n>` 行で判定します（0＝更新なし、1＝更新検知、3＝未検証＝1系統以上の取得失敗）。make はレシピの非0をすべて exit 2 で返すため、make の終了コードでは判定しません。

### 5.2 末尾スラッシュと UA の罠

kiro.dev は末尾スラッシュ必須（無しは301）。`-A "Mozilla/5.0"` 必須（空 UA は403）。

### 5.3 レート制限への対処

GitHub API は未認証の上限が 60 req/h です。Tree API・Releases API は1回ずつに抑えます。`fetch-snapshot.sh` と `check-freshness.py` は、環境変数 `GITHUB_TOKEN` があれば api.github.com への要求にだけ `Authorization` ヘッダを付けます（値は出力しません）。Kiro Web の Secrets にはトークンを置きません。CI（`validate-kiro-crew-docs.yml` の網羅性の実測と更新検知のステップ）は Actions の `GITHUB_TOKEN` を渡します。

### 5.4 スナップショット取得手順

一次情報（対象版のスナップショット・前回版と経由版のリポジトリ）は、リポジトリの追跡対象に書かずに取得します。

```bash
make fetch-kiro-crew-primary VERSION=vX.Y.Z PREV=vA.B.C
```

| 変数 | 既定値 | 内容 |
|---|---|---|
| `CLOUD_ROOT` | `/tmp/kiro-crew-primary` | 対象版のスナップショット（`<YYYYMMDD>_vX.Y.Z/`。repo・meta・releases・docs_md・`PIN.json`） |
| `CLOUD_PREV_ROOT` | `/tmp/kiro-crew-primary-prev` | 前回版のリポジトリ（`vA.B.C/repo`） |
| `CLOUD_VIA_ROOT` | `/tmp/kiro-crew-primary-via` | 経由版（前回版と対象版の間の安定版）のリポジトリ。`fetch-snapshot.sh` が `releases.json` から列挙する |

- **冪等**: 同じ `VERSION` の `PIN.json` があれば取得しません。`PREV` を指定した場合、既存の `PIN.json` の `base` が `PREV` と異なれば `base mismatch` で exit 1 になります
- `CLOUD_ROOT` 直下のスナップショットが1件でなければ `snapshot count mismatch` で exit 1 になります（別の版の混在を検出）
- `PIN.json` には、対象版の `ref`・`tag_object_sha`・`commit_sha`・`commit_short`・`release_published_at`・`prerelease`・`changelog_date`・`reference_date`・`sitemap_crew_count`・`official_page_updated`（公式ページごとの Page updated）・`official_md_sha256`（公式ページの `.md` companion の sha256。内容は保存しない）・`base`・`via`（経由版の配列）が入ります。PR 本文②（§15）はこの値を転記します
- `.md` companion の取得ごとの安定性は sha256 の比較で確かめています。取得ごとに値が変わるページがあると偽の差分が出るため、`--page-updated-diff` の差分は人が `.md` を確認してから扱います
- Kiro Web の Workflow では、run ごとに分けた置き場所を `CLOUD_ROOT`・`CLOUD_PREV_ROOT`・`CLOUD_VIA_ROOT` に渡します。Kiro Web のクラウドセッションでは `/tmp` がコマンド呼び出しをまたいで残らず、ワークスペースのファイルは残ります。このため、置き場所はリポジトリのルートからの相対パス `.kiro/cloud-runs/<run_id>/primary` とし、`CLOUD_ROOT` に渡します。前回版・経由版・`src/` の clone は `-prev`・`-via`・`-src` を付けた名前（`.kiro/cloud-runs/<run_id>/primary-prev`・`.kiro/cloud-runs/<run_id>/primary-via`・`.kiro/cloud-runs/<run_id>/primary-src`）にし、前の2つを `CLOUD_PREV_ROOT`・`CLOUD_VIA_ROOT` に渡します。make はリポジトリのルートで実行します。`.kiro/` は `.gitignore` の対象です。ローカル管理領域（§19）には置きません。`.gitignore` の `.kiro/` を部分的に除外する場合は `.kiro/*` と `!.kiro/workflows/` の形にし、`.kiro/cloud-runs/` を ignore のまま保ちます（`make check-kiro-crew-ignore` が確かめます）。run の起動前に、置き場所が空であることを次で確かめます（2行とも `0` であること）

```bash
CLOUD_ROOT='<cloud_root の値>'; ls -d "$CLOUD_ROOT"/*/ 2>/dev/null | wc -l; ls -d "$CLOUD_ROOT-prev" "$CLOUD_ROOT-via" "$CLOUD_ROOT-src" 2>/dev/null | wc -l
```

- **`KCD_GIT_ISOLATE=1`**: 指定すると `fetch-snapshot.sh` は KiroCrew へのリモート git 操作（`git clone`・`git ls-remote`）だけを、git のグローバル設定・システム設定を読まない環境（`HOME`・`XDG_CONFIG_HOME` を作業用の空のディレクトリにし、`GIT_CONFIG_NOSYSTEM=1` を付け、`GIT_CONFIG_GLOBAL` を外す）で実行します。git のグローバル設定が `https://github.com/` の URL を書き換えて KiroCrew の clone が失敗する環境（Kiro Web のクラウドセッション）で使います。`make fetch-kiro-crew-primary VERSION=vX.Y.Z PREV=vA.B.C KCD_GIT_ISOLATE=1 CLOUD_ROOT=.kiro/cloud-runs/<run_id>/primary CLOUD_PREV_ROOT=.kiro/cloud-runs/<run_id>/primary-prev CLOUD_VIA_ROOT=.kiro/cloud-runs/<run_id>/primary-via` の形で渡せます。既定は無効で、ローカルの動作は変わりません。`1`・`0`・未設定（空を含む）以外の値は exit 1 です。git の設定の値は出力しません。`api.github.com` への要求（curl。§5.3）と、`src/` の clone（§13 W-4。`fetch-snapshot.sh` を通らない）は対象外です

引数なしの `make fetch-kiro-crew-snapshot` は、ローカル管理領域へ保存する従来の動作です。クラウドでは使いません。

### 5.5 検証スクリプト

`scripts/kiro-crew-docs/` の `check-*` 全件と、関連するスクリプトです。

| スクリプト | 内容 | 呼び出し |
|-----------|------|---------|
| `check-links.py` | 内部リンク・アンカー・URL 書式 | `check-kiro-crew-all` |
| `check-structure.py` | 構成・H1・出典・公開境界 | 同 |
| `check-counts.py` | 件数系 SSoT・ページ数3者一致・builtin App 台帳 | 同 |
| `check-consistency.py` | 値系 SSoT の水平展開・両併記の対称性 | 同 |
| `check-notation.py` | 表記規約 (a)〜(i) | 同 |
| `check-coverage.py` | 公式ページ台帳とモジュール台帳の網羅性 | 同（スナップショットが無いとスキップ）。`--strict` は `check-kiro-crew-cloud` |
| `check-changelog.py` | changelog 構造 | `check-kiro-crew-all` |
| `check-scope.py` | スコープ境界 | 同 |
| `check-source-pin.py` | 参照時点記録・削除済み仕様書 | 同 |
| `check-ignore.sh` | 公開範囲（ローカル管理対象・絶対パス・トークン書式・スナップショット由来ファイル） | `check-kiro-crew-ignore` |
| `check-urls.sh` | 外部 URL 到達性（★外部依存） | `check-kiro-crew-urls`・`check-kiro-crew-urls-important` |
| `check-freshness.py` | 更新検知4系統（★外部依存） | `check-kiro-crew-freshness`・`check-kiro-crew-cloud-freshness` |
| `check-audit-groups.py` | 監査ページ群（§16）の割当漏れ・重複・存在しないファイル | `check-kiro-crew-cloud` |
| `check-peripheral-values.py` | `.github/`・`Makefile` に版依存の値が無いこと | `check-kiro-crew-peripheral-values`・`check-kiro-crew-cloud` |
| `check-pr-scope.py` | PR の変更範囲（`PROFILE=version-update`／`infra`） | `check-kiro-crew-pr-scope` |
| `check-pr-body.sh` | 公開される PR 本文の公開前検査 | `check-kiro-crew-pr-body` |
| `check-release-note.sh` | リリースノートの版の4者一致（ファイル名・H1・README の固定版・changelog 先頭）。`--print-readme-version` で README の固定版を出力 | `check-kiro-crew-release-note`（validate CI の PR 実行・Release ワークフローのゲート） |
| `measure-ssot.py` | 機械測定できる SSoT と検証器定数の比較・公式ページ台帳と `PIN.json` の比較 | `check-kiro-crew-cloud`・`check-kiro-crew-ledger-current` |
| `clean-room.sh` | 公開されるファイルだけの複製で make を実行 | `check-kiro-crew-cleanroom` |
| `fetch-snapshot.sh` | 一次情報の取得 | `fetch-kiro-crew-primary` |

### 5.6 表記規約 (a)〜(i)

(a) 他製品コマンドの混入 (b) 製品名表記の揺れ (c) 非 ISO 日付 (d) 存在しない版番号 (e) 取得日の混入 (f) autolink 事故 (g) 推測表現 (h) 存在しない CLI サブコマンド (i) 存在しない層数・件数の創作

## 6. 記述粒度

- **C-L1**: 新機能 → `01_features` に新ページ
- **C-L2**: 既存機能の仕様変更 → 該当ページと `04_reference` の値を更新
- **C-L3**: 利用者に影響しない開発者向け変更 → `02_update/01_changelog.md` に件数のみ

判定基準: CHANGELOG の項目が利用者の操作・設定・挙動に影響するか。

C-L1 で公開ページを新設した場合は、同じ PR で `check-structure.py` の `SECTION_FILES`・`check-counts.py` の `SECTIONS`・`TOTAL_PAGES`（定数コミット）と、§16 の監査ページ群への割当を行います。

## 7. SSoT（正準値）の定義と検証

### 7.1 状態区分

- **確定**: 固定参照時点の安定版タグの一次情報で直接取得済み
- **`[要検証]`**: 一次情報から再測定が必要。`src/` を出典とする値は、`fetch-snapshot.sh` が `src/` を取得しないため、依頼者の承認（G1。§13）を得て別に測るまで `[要検証]` のままにする（`.github/WORKFLOW.md`「厳密な仕様調査での `src/` 解析確認」）
- **未確定（両併記）**: 出典間で食い違い、裁定しない。**解消済みの食い違いを併記し続けない**（§18）
- **別項目と判明したもの**: 同じ名前で呼ばれるが別系統と判明したもの。同一項目として値を比較しない

版ごとの状態（基準点、`[要検証]` の ID と理由、未確定（両併記）の ID、解消済みの記録、§12 の監視値）は [`ssot-status.md`](../scripts/kiro-crew-docs/ledgers/ssot-status.md) に書きます。各 ID の定義と測り方は §14 です。

### 7.2 SSoT にしないもの

Star 数・Fork 数・コントリビューター数（日々変動）／コミット頻度（継続検証不可）／`[Unreleased]` の項目数／社内採用実績（発表時点の数値）

### 7.3 値変更時の更新箇所と順序

版更新では次の順に編集・コミットします。

1. **検証器の定数**（専用コミット `chore(scripts): 検証器の正準値を Kiro Crew vX.Y.Z 実測へ更新`）。版更新 PR（`PROFILE=version-update`）で変更してよい定数は次の17件だけです
   - `check-changelog.py`: `VALID_STABLE_VERSIONS`
   - `check-notation.py`: `VALID_STABLE_VERSIONS`・`ALLOWED_CLI_COMMANDS`・`DENIED_CLI_COMMANDS`
   - `check-counts.py`: `SSOT`・`SECTIONS`・`TOTAL_PAGES`
   - `check-coverage.py`: `EXPECTED_OFFICIAL_PAGES`・`EXPECTED_MODULES`
   - `check-freshness.py`: `KNOWN_LATEST_STABLE`・`KNOWN_STABLE_COUNT`・`KNOWN_CREW_PAGES`・`KNOWN_DOCS_FILES`
   - `check-consistency.py`: `DUAL_NOTATION`・`SSOT`
   - `check-structure.py`: `SECTION_FILES`
   - `check-source-pin.py`: `REMOVED_SPEC_FILES`
2. **台帳4本**（`scripts/kiro-crew-docs/ledgers/` の `official-pages.md`・`modules.md`・`builtin-apps.md`・`cli-commands.md`）。公式ページ台帳の「公式 Page updated（固定時点）」「`.md` sha256（固定時点）」列は `PIN.json` の値で更新する。builtin App 台帳は `src/` の実測値がある場合だけ更新する
3. **本文**（C-L1／C-L2／C-L3）
4. **`kiro-crew-docs/04_reference/05_limits.md`**（集約表）
5. **`scripts/kiro-crew-docs/ledgers/ssot-status.md`**（版ごとの状態）
6. **README 群**（ルート `README.md` の固定値、`kiro-crew-docs/README.md`、各セクション README）
7. **リリースノート**（`.github/release-notes/vX.Y.Z.md`。Release の自動化を導入した後に使う。導入前は `.github/WORKFLOW.md` §8 に従い人が Release を作る）

②〜⑦はコミット `docs: …` にします。正規表現定数や関数など、上の17件以外の変更は検証ロジックの変更であり、版更新 PR ではなく `PROFILE=infra` の別 PR で扱います。

## 8. スコープ境界

| 区分 | 扱い |
|------|------|
| Crew Gateway 自身の機能 | 解説する |
| Kiro CLI への依存点（ACP 等） | 解説する |
| Kiro CLI 単体の機能 | 解説しない。q-cli-docs へリンク |
| `docs/reference/kiro-cli/` の内容 | 出典として使わない（Kiro CLI のリファレンス） |

## 9. Kiro Crew 固有の制約（C-1〜C-7）

1. 一次情報が「公式サイト」ではなく「OSS リポジトリ」
2. kiro.dev の `changelog/crew/` の扱いが未決定（§3.2 の確認方法で毎回確認する）
3. 版番号の日付が2系統で食い違う
4. リポジトリに Kiro CLI のリファレンスが同梱されている（スコープ境界必須）
5. main ブランチが日次で動く（参照時点の記録必須）
6. 提供形態が複数あり、OS で機能差がある
7. セキュリティが導入判断に直結する（既知ギャップ（S10）を必ず記載）

## 10. ライセンス・再配布の扱い

本サイト（解説文書）は **MIT**。Kiro Crew 本体は **Apache-2.0**。一次情報のスナップショット（リポジトリの clone・公式ページの複製）はリポジトリに追跡させず、再配布しません。

## 11. 作業フロー

### 11.1 書式と記録の置き場

- changelog の版節と機能解説ページの書式は付録A・付録B
- 計画・調査・作業記録は PR 本文の定型7節（§15）に書く。PR 本文が一次記録になる

### 11.2 流れ

情報収集 → 出典記録 → 記述 → 自己検証 → コミット前検証 → コミット → PR → 人のレビューとマージ

### 11.3 コミット前検証（必須）

1. 対象ファイルを**名前で指定して** `git add`（`git add .` は使わない）
2. `make check-kiro-crew-ignore`（公開範囲。exit 0 必須）
3. `make check-kiro-crew-all`（exit 0 必須）
4. `.github/` または `Makefile` を変更した場合は `make check-kiro-crew-peripheral-values`（exit 0 必須）
5. コミット

執筆中の確認には `make check-kiro-crew-quick`（links／structure のみ）を使えます。版更新の完了条件は `make check-kiro-crew-cloud`（スキップを合格にしない全検証）の exit 0 です。公開されるファイルだけで検証が通ることは `make check-kiro-crew-cleanroom TARGETS="check-kiro-crew-ignore check-kiro-crew-all"` で確かめます。

### 11.4 ネガティブテスト手順（スクリプト新規作成・改修時）

1. 壊す前に `sha256sum` を記録
2. 規則1本だけ発火するように壊す
3. exit 1 とメッセージを確認
4. 復元
5. `diff` ＋ `sha256sum -c` で復元を検証
6. 再実行して exit 0 を確認
7. 結果を PR 本文⑤に書く

### 11.5 検証器の「検出強度」を取り違えない

- `check-notation.py` の `ALLOWED_CLI_COMMANDS` 未登録（(h)）は、オプション無しでは列挙されるだけで終了コードを変えません。`check-kiro-crew-cloud` は `--strict` で errors にします。`DENIED_CLI_COMMANDS` に登録が無い間は、CLI サブコマンド名の誤りはオプション無しでは止まりません
- `check-structure.py` の `SECTION_FILES` 欠落は「未執筆ファイル」注記どまりです。同じ欠落は `check-counts.py`（実ファイル数と計画値の不一致）と `check-links.py`（導線リンク切れ）が捕捉するので、3本を併せて実行すれば多層防御として成立します
- `check-kiro-crew-all` の網羅性チェックは、一次情報スナップショットが無いとスキップして成功扱いになります（出力に「未検証です」と表示）。クラウドでは `check-kiro-crew-cloud` の `--strict` で失敗にします
- エラーとして確実に止まることを確認済みなのは、changelog の版節欠落・実在しない版番号・削除済み仕様書 URL・セクションページ数の増減・台帳の件数不一致・freshness の4系統です

### 11.6 コミットの形式

`.github/WORKFLOW.md` §7 の形式（`<type>: <subject>`、本文、末尾に `出典: <source>（参照: <date> / commit <sha> / 版 <version>）`）。参照日・commit・版は `PIN.json` の `reference_date`・`commit_short`・対象版でそろえます。

### 11.7 公開後の表示確認（G3）

マージ後に、GitHub 上の公開ページで表示を確認します（アンカーの `user-content-` プレフィックス・表のセル数）。人が行います。

## 12. 監視項目

値は書きません（現在値は `ssot-status.md` と検証器定数）。

| 項目 | 頻度 | リスク |
|------|------|-------|
| 新安定版のリリース | nightly | 中 |
| CHANGELOG.md の変化 | nightly | 中 |
| 公式 crew ページ数の増減（S1） | nightly | 低 |
| `docs/` 構成の変化 | nightly | 低 |
| Windows パリティの `not yet` 解消 | 月次 | 低 |
| 既知ギャップ（S10）の増減・解消 | 月次 | 中 |
| 拒否ルール件数（S11）の変化 | nightly | **高**（安全機構の変化） |
| builtin App 数（S12）と `defaultEnabled` の変化 | nightly | **高** |
| サンドボックス既定モード（S22）の変化 | nightly | **高** |
| S23① 匿名利用テレメトリ（`kirocrew telemetry`）の送信フィールド数と既定状態の変化 | 月次 | 中 |
| S23② メトリクス／OTLP エクスポート（`telemetry.enabled`・`KIROCREW_TELEMETRY`）の既定状態と送信先・項目の変化。**①と別系統なので混同しない** | 月次 | 中 |
| 出典間で食い違っている値（S15・S24・Agent Backends の選択肢数・Windows の非サンドボックス実行の既定）が解消されたか | 月次 | 低（Windows の既定は**高**） |
| **本サイトが「食い違い」「未確認」と書いている項目が上流で解消していないか**（§18） | **版更新ごと（必須）** | **高**（解消済みの食い違いを併記し続けると誤りになる） |

月次の項目は版更新の Workflow の対象外です。nightly と「版更新ごと（必須）」の項目は版更新の調査（§13 `investigate`）で扱います。

## 13. クラウド版の工程表

版更新の工程（W-1〜W-19）を、Workflow のステップと人のゲートに対応づけます。Workflow 定義（recipe）を導入する前にクラウドセッションで手作業で行う場合も、同じ順序とゲートに従います。

| # | 工程 | ステップ／ゲート | 内容 |
|---|---|---|---|
| W-1 | 更新検知 | `detect` | `make check-kiro-crew-cloud-freshness` の `freshness-result` 行。対象版が安定版（`releases/tags/<版>` の `prerelease` が false）で、kiro-crew-docs に同名タグが無いことも確認する |
| W-2 | 対象版・基準点の確定 | `detect`・`fetch` | 前回版がルート `README.md` の固定版と一致すること。`PIN.json` の `ref`・`commit_sha`・`base`・`via` |
| W-3 | 計画 | `plan-gate`（**G1: 計画承認**） | PR 本文ドラフトの①②③⑥⑦（§15）を書き、人の承認を得る |
| W-4 | `src/` 解析の可否 | **G1** ＋ `src-measure` | 人の返答に `SRC_ANALYSIS: APPROVED` または `SRC_ANALYSIS: DENIED` の1行を求める。APPROVED の場合だけ、対象版のタグを別に clone して測る |
| W-5 | スナップショット取得 | `fetch` | `make fetch-kiro-crew-primary`（§5.4） |
| W-6 | 調査 | `investigate` | 経由版の一覧、SSoT の再測定（`measure-ssot.py` と §14 の手動項目）、§18 の解消判定 |
| W-7 | 差分抽出 | `investigate` | タグ間の `docs/` 差分（`diff -rq`）、タグ版 CHANGELOG の版節、公式ページの差分（`measure-ssot.py --page-updated-diff`） |
| W-8 | 台帳の再確認 | `investigate` | 公式ページ割当・モジュール扱い・builtin App・CLI 突合の4系統 |
| W-9 | 監査 | `audit`（群 A〜G の並列。§16） | 読み取り専用。群ごとの監査レポートを書く |
| W-10 | 本文更新 | `implement` ③ | §17 のルール、付録A・B の書式 |
| W-11 | 正準値の更新 | `implement` ① | §7.3 の17件 |
| W-12 | ネガティブテスト | `converge`（verify-fix） | 検証規則を改修した場合だけ（版更新 PR では規則を改修しない） |
| W-13 | 台帳・状態の更新 | `implement` ②⑤ | §7.3 |
| W-14 | インデックス同期 | `implement` ⑥ | README 群 |
| W-15 | 検証 | `converge`（verify-fix・review） | `check-kiro-crew-cloud`・`check-kiro-crew-ledger-current`・`check-kiro-crew-cloud-freshness`・`check-kiro-crew-pr-scope PROFILE=version-update`・`check-kiro-crew-pr-body` |
| W-16 | コミット・push・PR | `implement`・`pr`（**G2: PR レビューとマージ**） | feature branch `docs/kiro-crew-vX.Y.Z`。マージは人が行う |
| W-17 | GitHub Release | **G3** | マージ後に Release を作る（自動化の導入前は人が `.github/WORKFLOW.md` §8 に従う） |
| W-18 | 公開後の表示確認 | **G3**（人） | §11.7 |
| W-19 | 作業記録 | PR 本文（§15） | PR 本文を一次記録にする |

- 同時に2本以上の run を起動しません（同じチェックアウトを編集し合うため）
- `run_id` は未使用の値にします（前の run の判定ファイルを今回のものとして扱わないため）

## 14. SSoT 定義表

値は書きません。値の正本は検証器定数と `ssot-status.md` です。「機械測定」は `measure-ssot.py --snapshot <dir> --expect-constants` が測る項目、「手動」はこの表の測定方法に従って人またはエージェントが測る項目です。

| ID | 項目 | 測定方法 | 出典（一次情報の種別とパス） | 検証器 |
|---|---|---|---|---|
| S1 | 公式 crew ページ数 | sitemap の `docs/crew/` の URL 件数。URL の集合も公式ページ台帳と照合する | 公式 `kiro.dev/sitemap.xml` | 機械測定。`check-counts.py` `SSOT`・`check-consistency.py` `SSOT`・`check-freshness.py` `KNOWN_CREW_PAGES`・`check-coverage.py` `EXPECTED_OFFICIAL_PAGES` |
| S2 | リポジトリ `docs/` のファイル数 | タグの `docs/` を `find -type f` で数える（全ファイル） | KiroCrew タグの `docs/` | 機械測定。`check-counts.py`・`check-consistency.py` の `SSOT` |
| S3 | 最新安定版 | Releases の `prerelease == false` で、対象版の `published_at` 以前の最新の `tag_name` | GitHub Releases API | 機械測定。`check-consistency.py` `SSOT`・`check-freshness.py` `KNOWN_LATEST_STABLE`・`VALID_STABLE_VERSIONS`（2本）の最大値 |
| S3a | 版の日付（2系統） | タグ版 CHANGELOG の `## [X.Y.Z] - YYYY-MM-DD` と Release の `published_at` の日付部分 | タグの `CHANGELOG.md` ＋ Releases API（`PIN.json` の `changelog_date`・`release_published_at`・`via`） | 手動。`check-consistency.py` `DUAL_NOTATION`（両併記） |
| S4 | 安定版リリース数 | 最新安定版と同じ条件で数えた安定版の件数と版番号の集合 | GitHub Releases API | 機械測定。`check-counts.py`・`check-consistency.py` の `SSOT`・`check-freshness.py` `KNOWN_STABLE_COUNT`・`VALID_STABLE_VERSIONS`（2本） |
| S5 | 総リリース数（取得時点） | `releases.json` の全件数 | GitHub Releases API | 取得時点で変わるため測定値と比較しない。`check-counts.py`・`check-consistency.py` の `SSOT` |
| S6 | CHANGELOG の版節数 | タグ版 CHANGELOG の `## [X.Y.Z]` 見出し数（`## [Unreleased]` の有無も記録） | タグの `CHANGELOG.md` | 機械測定。`check-consistency.py` `SSOT` |
| S7 | ライセンス | `LICENSE` と README の記載 | タグの `LICENSE`・`README.md` | 手動 |
| S8 | Gateway の待ち受けポート | 仕様書と公式 docs の記載 | `docs/system-specs/modules/config.md` ほか・公式 `configuration/` | 手動。`check-consistency.py` `SSOT` |
| S9 | メモリ層の内訳 | Memory 仕様書の層構成 | `docs/system-specs/modules/memory-skills-hooks.md` | 手動 |
| S10 | セキュリティ層と既知ギャップ | 層の構成と Known gaps の項目数（公式 security ページと区別する） | `docs/architecture/security-deep-dive.md`・公式 `security/` | 手動 |
| S11 | 拒否ルール件数 | 拒否コマンドカタログの件数 | `docs/system-specs/modules/security.md` | 手動。`check-counts.py`・`check-consistency.py` の `SSOT` |
| S12 | builtin App 数と `defaultEnabled` | `src/kiro_crew/apps/builtins/*/` のディレクトリ数と各 `app.json` の `displayName`・`defaultEnabled` | ソース `src/`（G1 で承認された場合だけ解析） | 手動（`src-measure`）。`check-counts.py` `SSOT`（builtin App 台帳との一致） |
| S13 | メッセージングチャネル数 | 公式 Interfaces ページ・README・仕様書の列挙を別々に数える（両併記） | 公式 `interfaces/`・`README.md`・`docs/system-specs/modules/messaging.md` | 手動。`check-counts.py` `SSOT` |
| S14 | インポートのソース数・カテゴリ数 | Import 仕様書の列挙 | `docs/system-specs/modules/onboarding-import.md` | 手動。`check-counts.py` `SSOT` |
| S15 | Subagent 自動サイジング上限（`max_subagents` の既定を含む） | 2つの仕様書を個別に確認（両併記） | `docs/system-specs/modules/subagent.md`・`docs/system-specs/modules/config.md` | 手動。`check-consistency.py` `DUAL_NOTATION` |
| S16 | 履歴減衰 | Memory 仕様書の段の記述 | `docs/system-specs/modules/memory-skills-hooks.md` | 手動。`check-consistency.py` `SSOT` |
| S17 | Cron 最小間隔 | Cron の仕様書と公式ページの記述 | `docs/system-specs/modules/` の Cron 関連仕様書・公式 `features/cron/` | 手動 |
| S18 | 埋め込みモデル・方式 | 仕様書と公式 docs を分けて確認 | `docs/system-specs/modules/knowledge.md`・`memory-skills-hooks.md`・公式 `features/memory/`・`features/knowledge/` | 手動 |
| S19 | Consolidation の閾値 | Memory 仕様書の記述 | `docs/system-specs/modules/memory-skills-hooks.md` | 手動。`check-consistency.py` `SSOT` |
| S20 | 状態ディレクトリ | README・仕様書の記述 | `README.md`・`docs/` | 手動。`check-source-pin.py`（旧データホームの検出） |
| S21 | 公式カテゴリ構成 | sitemap の URL 集合からカテゴリ・索引・単独ページを数える | 公式 `kiro.dev/sitemap.xml` | 手動 |
| S22 | サンドボックス（モード・既定・呼称） | README・仕様書・アーキテクチャ資料と公式 security ページを両併記 | `README.md`・`docs/system-specs/modules/config.md`・`docs/architecture/security-deep-dive.md`・公式 `security/` | 手動。`check-consistency.py` `DUAL_NOTATION` |
| S23 | テレメトリ（①匿名利用 ②メトリクス／OTLP） | ①と②を別系統として確認 | ① `README.md` の該当節 ② `docs/system-specs/modules/metrics.md` | 手動 |
| S24 | コンテキストバジェット | 公式 memory ページの記述とリポジトリの `_CONTEXT_BUDGET_BASE` を両併記 | 公式 `features/memory/`・`docs/system-specs/modules/memory-skills-hooks.md` | 手動。`check-consistency.py` `SSOT`・`DUAL_NOTATION` |
| S25 | チャットターン上限 | 設定キーの既定と範囲 | `docs/system-specs/modules/config.md` | 手動 |
| S26 | Subagent タイムアウト | 設定キーの既定 | `docs/system-specs/modules/config.md` ほか | 手動 |
| S27 | `agent.subagent_max_turns` の既定 | 設定キーの既定と上限 | `docs/system-specs/modules/config.md` | 手動 |
| S28 | `docs/system-specs/` のファイル数 | `find -type f` の全ファイル（`.md` のみの件数も併記） | KiroCrew タグの `docs/system-specs/` | 機械測定。`check-coverage.py` `EXPECTED_MODULES`・モジュール台帳の合計 |
| S29 | auto-run plan の上限 | 仕様書の記述 | `docs/system-specs/modules/autopilot.md` | 手動 |
| CLI | `modules/cli.md` の表のサブコマンド | 表のセルが `kirocrew <sub>` で始まるものだけを数える（本文の散発的な言及は数えない） | `docs/system-specs/modules/cli.md`・README・公式 `interfaces/cli-reference/` | 手動。CLI 台帳・`check-notation.py` `ALLOWED_CLI_COMMANDS` |

## 15. PR 本文の定型7節

PR 本文を一次記録にします（作業記録の代わり）。公開リポジトリで公開されるため、作成前に `make check-kiro-crew-pr-body PR_BODY=<file> CLOUD_ROOT=<dir>` が exit 0 であることを確かめます（ローカル絶対パス・トークン・秘密鍵の書式・上流文書の連続5行以上の転記を検出します）。

| 節 | 書くこと |
|---|---|
| ① 更新計画 | 対象版・経由版・基準点、粒度（C-L1〜C-L3）の判定 |
| ② 一次情報の固定 | `PIN.json` の値の表（ref・commit・CHANGELOG 日付・Release 公開日・参照日・sitemap 件数・経由版） |
| ③ SSoT 変更点 | ID・前回値（更新前の定数）・新値・測定コマンド・出典（パスと行）を全件 |
| ④ 実施内容 | ファイル別の変更点（`git log --oneline origin/main..HEAD` と `git diff --stat origin/main...HEAD` から作る） |
| ⑤ 検証結果 | 実行した全コマンドと exit code、`check-kiro-crew-cloud` の要約行の数値、ネガティブテストの exit code |
| ⑥ 未確認・据え置き | §18 の解消判定表（必須）。対象版より新しい版を検知した場合はその版も |
| ⑦ 人の判断事項 | G1 の人の返答を逐語で記録（`SRC_ANALYSIS:` の行を含む）。正準値の変更・公式間の食い違いの扱い・公開方針 |

## 16. 監査ページ群

公開ページ（`kiro-crew-docs/0[0-4]_*`）は、次の群 A〜G のいずれか1つ、または「`implement` が直接更新」に割り当てます。版更新で公開ページを新設した場合は、同じ PR でこの表に割り当てます。割当漏れ・重複・存在しないファイルは `scripts/kiro-crew-docs/check-audit-groups.py` が検出します（`check-kiro-crew-cloud` に含まれます）。ルート `README.md` と `kiro-crew-docs/README.md` は `implement` ⑥で更新します。

| 群 | 対象ファイル（`kiro-crew-docs/` 配下） | 主に関わる SSoT・台帳 |
|---|---|---|
| A メモリ・Knowledge・スキル | `01_features/04_memory-and-learning.md`・`01_features/05_knowledge-library.md`・`01_features/07_agents-skills-steering.md` | S9・S16・S18・S19・S24 |
| B セキュリティ | `01_features/09_security.md`・`03_deployment/04_security-hardening.md`・`03_deployment/06_telemetry-and-privacy.md` | S10・S11・S22・S23 |
| C チャット・セッション・インターフェース | `01_features/02_sessions.md`・`01_features/03_chat.md`・`01_features/11_interfaces.md`・`01_features/13_computer-and-browser.md` | S13・S29 |
| D 自律実行・Agent Backends・AWS Control・Workflows | `01_features/06_autonomy.md`・`01_features/15_agent-backends.md`・`01_features/16_aws-control.md`・`01_features/17_workflows.md` | S15・S17・S26・S27 |
| E Apps・MCP・Artifacts・移行・アーキテクチャ | `01_features/01_architecture.md`・`01_features/08_mcp-integration.md`・`01_features/10_apps.md`・`01_features/12_artifacts.md`・`01_features/14_migration-import.md`・`04_reference/04_mcp-tools.md` | S12・S14・builtin App 台帳 |
| F デプロイ・リファレンス | `03_deployment/01_installation.md`・`03_deployment/02_windows.md`・`03_deployment/03_running-24-7.md`・`03_deployment/05_troubleshooting.md`・`04_reference/01_cli-commands.md`・`04_reference/02_configuration-keys.md`・`04_reference/03_directory-layout.md` | S8・S20・S25・CLI 台帳 |
| G 情報源・リリース方針 | `00_information/01_repository-structure.md`・`00_information/02_official-docs-structure.md`・`00_information/03_information-sources.md`・`02_update/02_release-policy.md` | S1・S2・S3・S3a・S4・S5・S21・S28・§3.2 の確認 |
| （`implement` が直接更新） | `00_information/README.md`・`01_features/README.md`・`02_update/README.md`・`02_update/01_changelog.md`・`03_deployment/README.md`・`04_reference/README.md`・`04_reference/05_limits.md` | 集約表・README 群・changelog |

監査の観点（全群共通）: 前回版と対象版の一次情報（タグ間の差分・タグ版 CHANGELOG の版節・公式ページの差分）に照らして、担当ページの記述が対象版でも正しいかを確かめます。各群の監査は他の群の出力を参照しません。

監査レポートの書式:

- 冒頭: 対象公開ページ、一次情報（対象版と前回版の ref・commit）
- §1 既存記述の修正が必要（根拠のファイル:行）
- §2 追記候補（根拠のファイル:行）
- §3 変化なしを確認した主要記述
- §4 判断できなかった事項（未確認として扱う）

## 17. ページ編集の共通ルール

### 17.1 Scope

- 監査（`audit`）は読み取り専用。編集は `implement` だけが行う
- 版更新 PR で編集するのは、公開ページ・README 群・リリースノート・本書・台帳と、§7.3 の許可定数だけ

### 17.2 Inputs

監査レポート（§16）、一次情報（§5.4 の対象版・前回版・経由版）、`PIN.json`。

### 17.3 Verification

- 変更を書く前に、引用元の行を自分で開いて確認する。監査レポートの主張どおりに書かれていなければ適用せず、理由を記録する
- 一次情報に書かれていないことを足さない。理由を創作しない（「〜のため」は出典が書いている場合だけ）

### 17.4 Style

- 各ページの既存の日本語の文体と構成に合わせる
- 禁止表現（推測表現）を使わない（一覧は `check-notation.py` の規約 (g)）
- Kiro Crew（製品名）／KiroCrew（GitHub リポジトリ名）／`kirocrew`（CLI コマンド）を書き分ける。日付は ISO `YYYY-MM-DD`。ローカル絶対パスを書かない
- プレリリース（`-insider`・`-rc`）、固定参照時点より新しい版、`[Unreleased]`、`docs/request-for-change/`、`docs/task-specs/` を事実として書かない

### 17.5 Citations

- 変更しない内容の既存の出典行は残す
- 追加・修正した内容には、ページの既存の形式で出典行を書く
  - GitHub: `**出典**（<対象>）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/xxx.md>` の次の行に `（参照: YYYY-MM-DD / commit `xxxxxxx` / 版 vX.Y.Z）`
  - CHANGELOG: `出典: CHANGELOG.md vX.Y.Z節 N行（`xxxxxxx`）`
  - 公式ページ: `**出典**: <https://kiro.dev/docs/crew/<path>/>（Page updated 表記あり）`。kiro.dev の URL は末尾 `/`
- commit・参照日・版は `PIN.json` の `commit_short`・`reference_date`・対象版で常に組にする。行番号は対象版のファイルの行番号

### 17.6 Structure

- 追記は `## vX.Y.Z での変更`（ページの既存の型に合わせて `###` でもよい）として、古い版の節より上に置く
- タグ間の仕様書の差分にだけあり CHANGELOG・Release 本文に説明が無い項目は、その旨を注記する
- CHANGELOG に「Before you upgrade」節が無い版の変更を「破壊的変更」と呼ばない。既定値の変更は「既定値が変わりました」と書く
- 値の訂正はその場で書き換え、旧値と版を注記する（例: 「（vA.B.C 以前は N）」）。前の版から既にあった誤りは、誤りだったことを明記して直す
- Preview・Developer Mode・Feature Preview・既定オフは必ず明記する
- 食い違いは裁定しない。`> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**` の後に両方の記述と出典を書く。解消を確認した食い違いは解消済みとして書き直し、未確認事項から外す

### 17.7 Canonical values

本文に正準値を書く場合は、検証器定数（§7.3）と `ssot-status.md` の値に一致させます。`[要検証]` の項目には数を書きません。両併記の項目は両方を書きます。`check-consistency.py` の `SSOT` のパターン（文脈語＋数値）に一致する書き方で旧値を書くと水平展開検証が失敗するため、版節内の当時の値は文脈語を変えて書きます。

### 17.8 CLI

`kirocrew <sub>` は `check-notation.py` の `ALLOWED_CLI_COMMANDS` にある語だけを使います。新しい語が必要な場合は CLI 台帳（`ledgers/cli-commands.md`）で突合し、定数コミットで追加します。

### 17.9 Links

相対パスで書き、アンカーの実在を確かめます（GitHub の slug: 小文字化、空白は `-`、記号の多くは除去、日本語は残る）。見出しを変えた場合は `kiro-crew-docs/` 全体を grep して参照元を直します。

### 17.10 Checks

`make check-kiro-crew-all` と `make check-kiro-crew-cloud` を実行し、失敗は自分の編集で直します。監査群の担当外のファイルが原因の失敗は、直さずに報告します。

### 17.11 Priority

監査レポート §1 の修正はすべて行います。§2 の追記候補は、利用者の操作・設定・既定値・セキュリティに影響するものを優先します。小さな UI の項目は1つの箇条にまとめてよい。

### 17.12 Output

ファイルごとの変更（節・内容・根拠のファイル:行）、適用しなかった監査項目と理由、調整が必要な事項、検査結果（exit code）をまとめ、要旨を PR 本文④⑥に書きます。

## 18. 版更新ごとの必須検査

本サイトが「食い違い」「未確認」「要検証」と書いている項目が、対象版の一次情報で解消していないかを毎回確かめます（§12 最終行）。

1. 次で公開ページの該当行を全件列挙する（`make list-kiro-crew-open-items` と同じ。最終行が `open-items: N`。0件なら非0で終わる）

```bash
out=$(grep -rnE '食い違い|未確認|要検証' kiro-crew-docs/0[0-4]_*); printf '%s\n' "$out"; n=$(printf '%s\n' "$out" | grep -c .); echo "open-items: $n"; test "$n" -ge 1
```

2. 各行を対象版の一次情報で「解消／継続／判定不能」に判定し、根拠を書く
3. 結果を PR 本文⑥に次の表で書く（行数が `open-items: N` の N と一致すること）

| ファイル:行 | 項目 | 判定（解消／継続／判定不能） | 根拠（一次情報のファイル:行） |
|---|---|---|---|

解消と判定した項目は、本文を解消済みとして書き直します（§17.6）。

## 19. 禁止事項

- main への直接コミット・push（feature branch と PR を使う。マージは人が行う）
- タグの作成・Release の公開（マージ後の自動化、または人が行う）
- ローカル管理領域（`work_plans/`・`work_records/`・`05_meta/`・`06_embedded-docs/`）への書き込みとコミット、一次情報スナップショットの追跡・再配布
- 承認の無い `src/` の解析（G1 の返答に `SRC_ANALYSIS: APPROVED` がある場合だけ解析する）
- 版更新 PR での `.github/`（`release-notes/` と本書を除く）・`Makefile`・`.gitignore`・検証ロジックの変更（`make check-kiro-crew-pr-scope PROFILE=version-update` で検査する）。改訂が必要と判断したら、版更新 PR では変更せずに人に判断を求める
- `.github/`・`Makefile` への版依存の値（件数・版番号）の記載（`make check-kiro-crew-peripheral-values` で検査する）
- トークン・秘密鍵・ローカル絶対パスをファイルや PR 本文に書くこと
- 上流文書の長文の転記（出典のパスと行番号で参照する）
- 推測で書くこと

---

## 付録A changelog エントリの書式

新しい安定版がリリースされたとき、CHANGELOG.md の該当版節を要約して書きます。**正準キーは版番号（`vX.Y.Z`）**。CHANGELOG 日付と Release 公開日は**2列で併記**します（食い違うため）。粒度は §6（C-L1／C-L2／C-L3）。CHANGELOG は開発者向けの詳細記述（PR 番号付き・長い項目）のため、そのまま転記しません。

```markdown
### vX.Y.Z

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | YYYY-MM-DD |
| GitHub Release 公開日 | YYYY-MM-DD |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/vX.Y.Z>
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md#xyz>

#### 利用者に影響する変更（C-L1/C-L2）

- **（機能名）**: （要約。CHANGELOGの記述を圧縮する形に限定し、書かれていない理由を足さない）
  → 詳細は [01_features/NN_xxx.md](../01_features/NN_xxx.md)

#### 開発者向け変更（C-L3・件数のみ）

- 内部テスト・リファクタリング等: N件
```

| # | 記入時の確認 |
|---|------|
| 1 | 版番号は `vX.Y.Z` 形式か（プレリリース `-rc.N` は扱わない） |
| 2 | **CHANGELOG 日付と Release 公開日の2列が両方あるか**（食い違いを裁定していないか） |
| 3 | `## [Unreleased]` を出典にしていないか（固定版に節があるかを確認する。`docs/build/changelog.md` が changelog の gate の規則を説明している） |
| 4 | C-L1／C-L2 は該当ページへリンクし、changelog に詳細を重複させていないか |
| 5 | C-L3 は件数のみで、個別項目を転記していないか |
| 6 | 公式に書かれていない**理由・因果**を足していないか |

## 付録B 機能解説ページの書式

`01_features/` に新ページを作るときに使います。Kiro Crew の一次情報だけで書き、Kiro CLI／IDE／Web の記述を根拠にしません（別製品）。

```markdown
# （機能名）

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://kiro.dev/docs/crew/（パス）/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/（module）.md>
（参照: YYYY-MM-DD / commit `xxxxxxx` / 版 vX.Y.Z）

---

## 概要

（公式の説明。「公式は〜と説明しています」の形で引用元を示す）

## 使い方

（手順。公式の手順どおり。順序を勝手に変えない）

## 設定

（設定項目。値は 04_reference にリンクし本文に重複させない）

## 制限事項

（公式に明記されている制限のみ。書かれていない制限を推測しない）

## Kiro CLI との違い

（**Crew Gateway 自身の機能**と**Kiro CLI への依存点**を区別して書く。Kiro CLI 単体機能は書かず q-cli-docs へリンクする）

## 未確認事項

（一次情報で確認できなかったことを明示。空なら節を削除）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/（パス）/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/（module）.md>
- 値の一覧: [04_reference/NN_xxx.md](../04_reference/NN_xxx.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)
```

| # | 記入時の確認 |
|---|------|
| 1 | 冒頭に「**Kiro Crew（OSS）**の仕様」と明記したか |
| 2 | 出典が2形式（kiro.dev＋Page updated ／ GitHub＋参照日・SHA・版）のいずれかで揃っているか |
| 3 | GitHub 出典に**参照日・commit SHA・版**が揃っているか |
| 4 | 値を `04_reference/` と二重に書いていないか（リンクで済ませる） |
| 5 | Kiro CLI 単体の機能が混入していないか（q-cli-docs の領域） |
| 6 | 公式に書かれていない**理由・因果・意図**を足していないか |
| 7 | Zenn 記事（0.1.2 時点）の値を固定参照時点の最新安定版の値として書いていないか（版差があれば注記） |
| 8 | SSoT（§14）と数値が一致しているか |

---

**関連ドキュメント**: [WORKFLOW.md](WORKFLOW.md) / [COMMIT_CHECKLIST.md](COMMIT_CHECKLIST.md)

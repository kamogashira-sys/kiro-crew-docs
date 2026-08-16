# ドキュメント作成ワークフロー

Kiro Crew は **OSS であり、一次情報がリポジトリ（GitHub `kirodotdev/KiroCrew`）と公式サイト（`kiro.dev/docs/crew/`）の二重構造**である。main ブランチは日次で動き（週100コミット超）、リリースも約2週間ペースで進む。したがって「取得時点の記録」が兄弟サイト以上に重要になる。

## 📋 作業フロー

1. 情報収集（① リポジトリのソース・モジュール仕様 ② README・ガイド ③ 公式 docs ④ CHANGELOG・Releases ⑤ 公式ブログ ⑥ AWS公式ブログ ⑦ Zenn記事 ⑧ 実機確認）
2. 一次情報の特定（差分検知・出典の絞り込み）
3. 出典の記録（参照日・commit SHA・版を必ず残す）
4. 記述（推測ゼロ・理由の創作禁止・スコープ境界の遵守）
5. 自己検証
6. コミット前検証（機械チェック）
7. コミット

---

## 1️⃣ 情報収集

### 一次情報の優先順位（8順位）

| 順位 | 情報源 | 何に使うか |
|-----|-------|-----------|
| 1 | リポジトリのソース／モジュール仕様（`docs/system-specs/`・`docs/architecture/`） | 仕様の最終根拠。設定キー名・既定値・制約 |
| 2 | リポジトリの README／ガイド（`docs/guides/`・`docs/app-kit/`） | 導入手順・運用手順・App SDK |
| 3 | 公式ドキュメント（`kiro.dev/docs/crew/` 配下43ページ） | 機能の公式な言い方・ユーザー向け説明 |
| 4 | CHANGELOG.md + GitHub Releases | 版ごとの変更点（**両者の日付が食い違う**。両併記） |
| 5 | 公式ブログ（`kiro.dev/blog/introducing-kiro-crew/`） | 設計意図・背景・採用実績 |
| 6 | AWS公式ブログ（日本語） | 日本語の公式用語 |
| 7 | AWS Japan 社員の Zenn 記事（3本） | 日本語の解釈・検証済み手順・図解（**「個人の見解」注記あり。仕様の根拠にはしない**） |
| 8 | 実機確認 | 1〜7 で確定しない挙動（本サイトでは必須にしない） |

### 情報収集の原則

- **リポジトリを出典にする記述には commit SHA（短縮7桁）と参照日を必ず記録する**
- Zenn 記事（0.1.2 時点）の値をそのまま最新版の値として書かない。**v0.2.0 の一次情報で再確認する**
- `docs/request-for-change/`（RFC）・`[Unreleased]`・プレリリースを実装済みとして書かない
- **削除済み・移行専用の仕様書を出典にしない**（`features/claude-code-provider.md`・`post-launch-removals.md` 等。冒頭に `removed`／`no longer exists`／`legacy` の断りがあるもの）

### 出典にしないもの

| 対象 | 理由 |
|------|------|
| `docs/request-for-change/`（20件） | 未確定の将来仕様 |
| `docs/ci/`・`docs/build/` | Crew 開発者向け |
| 削除済み・移行専用の仕様書 | v0.2.0で既に存在しない機能の記録 |
| `## [Unreleased]` | 未リリース |
| プレリリース（`-rc.N`） | 安定版のみを版番号として扱う |
| `kiro.dev/llms.txt` | crew の言及が0件（URL網羅には使えない） |

### 公式 docs 取得時の注意

- **末尾スラッシュ必須**。無いと301
- `-A "Mozilla/5.0"` 必須。空UAは403
- `.md` companion が存在する（末尾スラッシュを除去して `.md` を付与。`content-type: text/markdown` で確認できる）

### GitHub 取得時の注意

- Tree API・Releases API は未認証 60 req/h。1回ずつに抑える
- `git clone --depth 1` 後は `git rev-parse HEAD` で commit SHA を記録

---

## 2️⃣ 一次情報の特定

### 更新検知（4系統）

```bash
# ① GitHub Releases（新しい安定版）
curl -s "https://api.github.com/repos/kirodotdev/KiroCrew/releases?per_page=100"

# ② CHANGELOG.md のハッシュ変化
curl -s "https://raw.githubusercontent.com/kirodotdev/KiroCrew/main/CHANGELOG.md" | sha256sum

# ③ 公式 sitemap の crew ページ数変化
curl -s -A "Mozilla/5.0" "https://kiro.dev/sitemap.xml"

# ④ GitHub Tree API の docs/ ファイル数変化
curl -s "https://api.github.com/repos/kirodotdev/KiroCrew/git/trees/main?recursive=1"
```

### スコープ境界の確認（Crew 固有）

リポジトリに `docs/reference/kiro-cli/`（23ファイル）が同梱されているが、これは **q-cli-docs の領域**。Crew Gateway 自身の機能とKiro CLIへの依存点（ACP・`agent.provider=acp`）は解説するが、Kiro CLI 単体の機能は解説しない。

---

## 3️⃣ 出典の記録

### 方法1: GitHub 出典（インライン）

```
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
```

### 方法2: 公式 docs 出典（インライン）

```
**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
```

### 方法3: 未確認事項の明示

一次情報で確認できない事項は「未確認」と明示する。数値を推測で埋めない。

### 方法4: 出典間の食い違いの明示

CHANGELOG日付とRelease公開日、Subagent上限（`subagent.md`と`config.md`）、サンドボックスの呼称（`auto`と`standard`）のように**出典間で値が食い違う場合は両併記し裁定しない**。

---

## 4️⃣ 記述

### 記述の原則

- 公式に書かれていない理由・因果を書かない
- `01_features` は概念と挙動を扱い、具体的な値は `04_reference` に置いて相互リンクする
- 各ページ冒頭に製品スコープ注記（`> **本ページは Kiro Crew（OSS）の仕様です。**`）を置く

### 禁止表現

「最低〜以上」（根拠なし）／「一般的に」（曖昧）／「通常」「おそらく」「たぶん」（推測）／未確認の層数・件数の創作（例:「公式8層」）

### Kiro Crew / KiroCrew / kirocrew の書き分け

| 表記 | 用途 |
|------|------|
| **Kiro Crew** | 製品名 |
| **KiroCrew** | GitHubリポジトリ名 |
| **`kirocrew`** | CLIコマンド名 |

### Kiro CLI との書き分け

Crew はランタイムとして Kiro CLI に依存する（ACP経由）。この依存関係は解説するが、Kiro CLI 単体の機能（モデル選択・CLIコマンド体系）は q-cli-docs の領域として扱い、混同しない。

### 日付・版番号・名称の表記

- **ISO形式 `YYYY-MM-DD`**。TZ変換なし
- 版番号は `vX.Y.Z`（プレリリースは扱わない）
- CHANGELOG日付とRelease公開日は**2列で併記**
- **機能名は公式ナビの表示名を優先**し、URLスラッグは出典としてのみ使う（例: `features/cron` → 表示名「Scheduling」）

---

## 5️⃣ 自己検証

### 出典の確認

- [ ] 全ての技術的記述に出典がある
- [ ] GitHub出典に参照日・commit SHA・版が揃っている
- [ ] 出典が一次情報（順位1〜4）である
- [ ] 各ページに出典日がある

### 値の確認

- [ ] 表の値・件数を実測（HTML／JSON）から取った
- [ ] SSoT（S1〜S24）と一致している
- [ ] 出典間で食い違う値は両併記した（裁定していない）

### 表現の確認

- [ ] 推測表現を使用していない
- [ ] 理由・因果を勝手に補っていない
- [ ] Kiro Crew / KiroCrew / kirocrew の表記を混同していない
- [ ] Kiro CLI 単体の機能を Crew の機能として書いていない

### リンクの確認

- [ ] 内部リンクが有効（相対パス）
- [ ] 外部リンクが有効・kiro.devは末尾スラッシュ付き
- [ ] 姉妹サイトへのリンクに「別製品」と明記

---

## 6️⃣ コミット前検証

```bash
cd <リポジトリのルート>

# 執筆中の常用（links / structure のみ。全チェックではありません）
make check-kiro-crew-quick

# 公開範囲の機械確認（ローカル管理対象が除外されているか。exit 0 必須）
make check-kiro-crew-ignore

# コミット前・公開前（exit 0 必須）
make check-kiro-crew-all

git status --short
```

> ⚠️ **`all` の exit 0 は「全部を検証した」ではありません。** 網羅性チェックは
> 一次情報のスナップショット（`06_embedded-docs/YYYYMMDD/repo/docs/`）が無いと
> **スキップして成功扱い**になります。スキップ時は「**未検証です**」と表示されるので
> 出力を読んでください。

> 利用可能なターゲットは `make`（引数なし）で確認できます。

### ⚠️ 検証スクリプトを新規作成・改修したときはネガティブテストを行う

**規則ごとに独立して**壊し、検出されることを確認します。

| 手順 | 内容 |
|------|------|
| 1 | 壊す前にハッシュを取る（`sha256sum <file> > /tmp/x.sha`） |
| 2 | **規則1本だけ**が発火するように壊す |
| 3 | **exit 1** と**該当メッセージ**を確認 |
| 4 | 復元する |
| 5 | **`diff` ＋ `sha256sum -c` で復元を検証** |
| 6 | 復元後に再実行して **exit 0** を確認 |
| 7 | 実施記録を作業記録に残す |

[コミット前チェックリスト](COMMIT_CHECKLIST.md)も確認してください。

---

## 7️⃣ コミット

```
<type>: <subject>

<body>

出典: <source>（参照: <date> / commit <sha> / 版 <version>）
```

### 例

```
docs: 01_features/09_security.md を執筆

- サンドボックス3モード（auto/strict/off）を記述
- Owner lock を追加

出典: https://kiro.dev/docs/crew/security/（参照: 2026-08-16）
出典: https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md
（参照: 2026-08-16 / commit 64060f3 / 版 v0.2.0）
```

---

## 🔄 問題発見時の対応

| 問題 | 対応 |
|------|------|
| **出典不明の記述** | 一次情報を特定 → 出典を追加。検証不可能なら削除 |
| **推測表現** | 一次情報で確認 → 確認できれば断定表現へ、できなければ「未確認」明示または削除 |
| **理由・因果が書かれている** | 公式にその理由が明記されているか確認 → なければ**削除** |
| **Kiro Crew / Kiro CLI の混同** | スコープ境界（§8）で確認 → Crew の一次情報で書き直すか、q-cli-docs へリンク |
| **出典間で値が食い違う** | **裁定しない**。両方を併記し「食い違いあり」と明示 |
| **存在しない値の創作**（例: 公式8層） | 一次情報の該当箇所を正規表現等で再検査。無ければ削除 |
| **削除済み仕様書を出典にしていた** | 該当記述を削除するか「削除済み」の事実として書き直す |

---

## 📊 品質指標

### 目標

- 出典不明の記述: **0件**
- 公式に根拠のない理由・因果の記述: **0件**
- 推測表現: **0件**
- リンク切れ: **0件**
- SSoT（正準値）の不一致: **0件**
- 存在しない値の創作: **0件**

### 測定方法

```bash
make check-kiro-crew-all
```

---

## 🔗 関連ドキュメント

- [コミット前チェックリスト](COMMIT_CHECKLIST.md)
- [サイト本体 README](../kiro-crew-docs/README.md)
- [更新手順書](../kiro-crew-docs/05_meta/10_update-guide.md)（ローカル管理）

---

**最終更新**: 2026-08-16

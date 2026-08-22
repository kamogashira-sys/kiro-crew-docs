# コミット前チェックリスト

このチェックリストは、ドキュメントの品質を保証するために、コミット前に必ず確認してください。

> **Kiro Crew は OSS であり一次情報がリポジトリと公式サイトの二重構造です。** main ブランチは
> 日次で動くため、リポジトリを出典にした記述には**参照日・commit SHA・版**の記録が必須です
> （[ワークフロー](WORKFLOW.md)参照）。

---

## 🚫 必須確認事項

### 1. 出典の確認

- [ ] 全ての技術的記述に一次情報の出典がある
- [ ] **GitHub 出典に参照日・commit SHA・版が揃っている**
- [ ] 機能仕様・設定値は公式ドキュメント（<https://kiro.dev/docs/crew/>）またはリポジトリの `docs/system-specs/` に基づく
- [ ] 各ページに**出典日**を記載している
- [ ] 公式に確認できない事項は「未確認」と明示している（推測で断定していない）
- [ ] **0.1.2 時点の Zenn 記事の値を最新版（現在 v0.3.0）の値として書いていないか**（本サイトで実際に発生した誤りの主因）

### 2. 表現の確認

- [ ] 推測表現（「おそらく」「と思われる」等）を使用していない
- [ ] 断定的な記述には必ず根拠がある
- [ ] **公式に書かれていない理由・因果・意図を書いていない**
- [ ] **Kiro Crew / KiroCrew / kirocrew の表記を混同していないか**（製品名／リポジトリ名／CLIコマンド名）
- [ ] **Kiro CLI 単体の機能を Crew の機能として書いていないか**（`docs/reference/kiro-cli/` は出典にしない）
- [ ] `docs/request-for-change/`・`[Unreleased]`・削除済み仕様書（`claude-code-provider.md` 等）を出典にしていないか

### 3. 値の取得元の確認

- [ ] 表の値・件数を実測（HTML・JSON API のレスポンス）から取った
- [ ] SSoT（S1〜S24）の値と一致している
- [ ] **出典間で値が食い違う場合は両併記し裁定していない**（S3a版の日付／S15 Subagent上限／S22サンドボックス呼称）
- [ ] 存在しない層数・件数を「公式の表記」として書いていない（例:「公式8層」は現行公式に存在しない）

### 4. リンクの確認

- [ ] 全ての内部リンクが有効である（相対パス）
- [ ] 全ての外部リンクが有効である
- [ ] **kiro.dev の URL は末尾スラッシュ付き**（スラッシュなしは301）
- [ ] GitHub の blob URL は `blob/main/` 形式（末尾スラッシュを付けない）
- [ ] 姉妹サイト（IDE/CLI/Web版）へのリンクに「**別製品**」であることを明記している

### 5. 公開範囲の確認

- [ ] ローカル管理対象（`work_plans/`・`05_meta/`・`06_embedded-docs/`・`work_records/`）がコミットに含まれていない
- [ ] **ローカル絶対パス・ユーザー名が公開ファイルに含まれていない**（`check-ignore.sh` が機械検出します）

---

## 📋 参照時点記録の確認（main が日次で動くため）

### GitHub 出典の正しい記録形式

```
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/overview.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
```

### 公式 docs 出典の確認

```bash
# 末尾スラッシュ必須。空 UA は 403
curl -sS -A "Mozilla/5.0" -o /tmp/crew-page.html "https://kiro.dev/docs/crew/security/"

# .md companion（末尾スラッシュ除去 + .md）
curl -sS -A "Mozilla/5.0" -o /tmp/crew-page.md "https://kiro.dev/docs/crew/security.md"
```

### スコープ境界の確認

- [ ] `docs/reference/kiro-cli/`（23ファイル）を出典として引用していない
- [ ] Kiro CLI 単体機能の解説が混入していない
- [ ] Crew Gateway 自身の機能と、Kiro CLI への依存点（ACP・`agent.provider=acp`）を区別して書いている

---

## 🔍 検証方法

### 自動検証

```bash
cd <リポジトリのルート>
make check-kiro-crew-quick    # 執筆中の常用（links / structure のみ）
make check-kiro-crew-ignore   # 公開範囲の機械確認（コミット前に必須・exit 0 必須）
make check-kiro-crew-all      # コミット前・公開前
```

> **`check-kiro-crew-quick` は全チェックではありません**（links / structure のみ）。
> 執筆中の素早い確認用です。**コミット前には `check-kiro-crew-all` を実行してください**
> （利用可能なターゲットは `make` で確認できます）。

> ⚠️ **`check-kiro-crew-all` の exit 0 は「全部を検証した」を意味しません**。
> 網羅性チェック（`check-kiro-crew-coverage`）は**一次情報のスナップショットが無いと
> スキップして成功扱い**になります（clone 直後・CI）。スキップ時は出力に
> 「**未検証です**」と表示されるので、必ず出力を読んでください。
>
> 外部情報源に依存する検証（外部URLの到達性・更新検知）は `all` には含めません
> （ネットワーク障害やレート制限で CI が赤くなるのを避けるため）。

### 手動検証

1. **出典の確認** — 技術的記述に出典リンクと参照日（GitHubはSHAも）があるか／リンクが有効か
2. **版・SHAの確認** — 公式Releases・CHANGELOG、またはclone時のSHAと一致するか
3. **推測表現の確認** — 「おそらく」「と思われる」等がないか／**理由を勝手に補っていないか**
4. **表記の区別** — Kiro Crew / KiroCrew / kirocrew を混同していないか／Kiro CLI 単体の機能が混入していないか

---

## ✅ コミット前の最終確認

- [ ] 全てのチェック項目を確認した
- [ ] **`make check-kiro-crew-all` を実行した（exit 0）** — `quick` では代用できません
- [ ] `make check-kiro-crew-ignore` を実行した（exit 0）
- [ ] 検証スクリプトを新規作成・改修した場合、**規則ごとにネガティブテスト**を行い、`diff` で復元を検証した
- [ ] 公開範囲の確認を実施した（`git status` ＋ `git check-ignore`）
- [ ] コミットメッセージが明確である

---

## 📝 コミットメッセージガイドライン

### フォーマット

```
<type>: <subject>

<body>

<footer>
```

### Type

- `docs`: ドキュメント変更
- `chore(scripts)`: 検証スクリプト変更
- `chore(ci)`: CI 設定変更
- `fix`: 誤記・リンク切れ等の修正
- `chore`: その他のツール・設定変更

### 例

```
docs: 01_features/09_security.md を執筆

- サンドボックス3モード（auto/strict/off）を記述
- Owner lock を追加

出典: https://kiro.dev/docs/crew/security/（参照: 2026-08-22）
出典: https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md
（参照: 2026-08-22 / commit 21584ea / 版 v0.3.0）
```

---

## 🔗 関連ドキュメント

- [ドキュメント作成ワークフロー](WORKFLOW.md)
- [サイト本体 README](../kiro-crew-docs/README.md)

---

**最終更新**: 2026-08-22（v0.3.0対応で出典記法の例を更新）

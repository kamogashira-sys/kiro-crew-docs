# Pull Request

## Description

Brief description of the changes in this PR.

## Type of Change

Please delete options that are not relevant.

- [ ] 🐛 Bug fix (typo, wrong value, broken link)
- [ ] ✨ New documentation (new page or section)
- [ ] 💥 Breaking change (section restructure, file rename/move)
- [ ] 📚 Documentation update (existing page updated for a new Kiro Crew release or docs update)
- [ ] 🔧 Maintenance (scripts, CI, templates)

## Changes Made

- [ ] Updated documentation files
- [ ] Added new documentation
- [ ] Fixed typos or errors
- [ ] Improved formatting or structure
- [ ] Updated examples or code snippets
- [ ] Other: _______________

## Sections Updated

- [ ] `kiro-crew-docs/00_information/` (リポジトリ・公式サイトの構造・情報源)
- [ ] `kiro-crew-docs/01_features/` (機能解説。本サイトの主眼)
- [ ] `kiro-crew-docs/02_update/` (changelog・リリース方針)
- [ ] `kiro-crew-docs/03_deployment/` (導入・運用・セキュリティ・テレメトリ)
- [ ] `kiro-crew-docs/04_reference/` (CLI・設定キー・ディレクトリ構造・上限値)
- [ ] `scripts/` / `Makefile` / CI
- [ ] Other: _______________

## Kiro Crew version / commit

**Kiro Crew is OSS with version numbers (vX.Y.Z) and a main branch that moves daily.**
If this change concerns a specific release, give the version (e.g., `v0.2.0`).
If this change is based on the repository directly, give the **commit SHA (short, 7 chars)** you referenced.

## Checklist

- [ ] I have read the [documentation workflow](WORKFLOW.md) and [commit checklist](COMMIT_CHECKLIST.md)
- [ ] Every technical statement cites a primary source (GitHub repository or kiro.dev/docs/crew/)
- [ ] GitHub-sourced statements record **reference date + commit SHA + version**
- [ ] Statements that cannot be verified officially are explicitly marked 未確認
- [ ] **No reasons/causality are asserted unless officially stated** (facts and inference are kept separate)
- [ ] I have performed a self-review of my own changes
- [ ] I have checked for typos and grammatical errors
- [ ] My changes are consistent with existing documentation structure
- [ ] Dates use ISO format (`YYYY-MM-DD`)
- [ ] Kiro Crew / KiroCrew / kirocrew notation is not mixed (product name / repo name / CLI command)
- [ ] Kiro CLI single-product features are not described as Kiro Crew features (links to q-cli-docs instead)
- [ ] `docs/request-for-change/`, `[Unreleased]`, prerelease tags, and removed/legacy spec files are not cited as sources
- [ ] kiro.dev URLs end with a trailing slash and use `-A "Mozilla/5.0"` when fetched

## Testing

- [ ] `make check-kiro-crew-all` passes locally (exit 0)
- [ ] `make check-kiro-crew-ignore` passes locally (exit 0)
- [ ] If I created or modified a validation script, I ran a **negative test per rule** and verified restoration with `diff`
- [ ] I have verified that all links work correctly
- [ ] I have checked that tables render properly (if applicable)

## 版更新（クラウド）

Kiro Crew の新しい安定版への追随（版更新）の PR では、次の7節を書きます（Kiro Web のクラウドセッション・Workflow で作業した場合も、ローカルで作業した場合も同じ）。PR 本文が作業記録の一次記録になります。書き方は [更新手順書](UPDATE_GUIDE.md) §15、作成前に `make check-kiro-crew-pr-body PR_BODY=<file> CLOUD_ROOT=<dir>` が exit 0 であることを確かめます。版更新以外の PR ではこの節を削除してください。

### ① 更新計画

対象版・経由版・基準点、粒度（C-L1〜C-L3）の判定。

### ② 一次情報の固定

`PIN.json` の値の表（ref・commit・CHANGELOG 日付・Release 公開日・参照日・sitemap 件数・経由版）。

### ③ SSoT 変更点

ID・前回値（更新前の定数）・新値・測定コマンド・出典（パスと行）を全件。

### ④ 実施内容

ファイル別の変更点（`git log --oneline origin/main..HEAD` と `git diff --stat origin/main...HEAD` から作る）。

### ⑤ 検証結果

実行した全コマンドと exit code（`check-kiro-crew-cloud`・`check-kiro-crew-ledger-current`・`check-kiro-crew-cloud-freshness` の `freshness-result` 行・`check-kiro-crew-pr-scope PROFILE=version-update`・`check-kiro-crew-pr-body`）、`check-kiro-crew-cloud` の要約行の数値、ネガティブテストの exit code。

### ⑥ 未確認・据え置き

更新手順書 §18 の解消判定表（必須。行数は `make list-kiro-crew-open-items` の `open-items: N` と一致させる）。対象版より新しい版を検知した場合はその版も。

### ⑦ 人の判断事項

計画承認（G1）での人の返答を逐語で記録（`SRC_ANALYSIS: APPROVED` または `SRC_ANALYSIS: DENIED` の行を含む）。正準値の変更・公式間の食い違いの扱い・公開方針。

## Related Issues

Closes #(issue number)

## Additional Notes

Add any additional notes or context about the PR here.

---

**Important**: This is an unofficial documentation project. By submitting this PR, you acknowledge that
this project is not affiliated with the Kiro Crew maintainers, Kiro, or Amazon Web Services, Inc.
Kiro Crew itself is licensed under Apache-2.0; this documentation project is licensed under MIT.

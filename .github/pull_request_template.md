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

## Related Issues

Closes #(issue number)

## Additional Notes

Add any additional notes or context about the PR here.

---

**Important**: This is an unofficial documentation project. By submitting this PR, you acknowledge that
this project is not affiliated with the Kiro Crew maintainers, Kiro, or Amazon Web Services, Inc.
Kiro Crew itself is licensed under Apache-2.0; this documentation project is licensed under MIT.

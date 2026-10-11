# kiro-crew-docs 作業規約（エージェント向け）

## 適用範囲

本ファイルは、リポジトリ `kamogashira-sys/kiro-crew-docs`（Kiro Crew の非公式日本語解説サイト）での作業にだけ適用します。成果物は公開されます。

## 品質優先

- 一次情報（Kiro Crew のリポジトリ `kirodotdev/KiroCrew` と公式サイト `kiro.dev/docs/crew/`）で確認できたことだけを書く。確認できないことは「未確認」と書く
- 速さより正確さを優先し、検証工程を省略しない
- 推測表現を使わない（一覧は `scripts/kiro-crew-docs/check-notation.py` の規約 (g) と [.github/WORKFLOW.md](.github/WORKFLOW.md) の「禁止表現」）
- 出典間の食い違いは裁定せず両方を書く

## 版更新（Kiro Crew の新しい安定版への追随）

版更新は次の手順書に従います。

#[[file:.github/UPDATE_GUIDE.md]]

- 完了条件は `make check-kiro-crew-cloud` の exit 0（スキップを合格にしない全検証）
- 作業は feature branch で行い、PR を作る。main への直接 push、タグの作成、Release の公開はしない
- 禁止事項は手順書の §19

## コミット前の順序

1. 対象ファイルを名前で指定して `git add`（`git add .` は使わない）
2. `make check-kiro-crew-ignore`（exit 0）
3. `make check-kiro-crew-all`（exit 0）
4. `.github/` または `Makefile` を変更した場合は `make check-kiro-crew-peripheral-values`（exit 0）
5. コミット（形式は [.github/WORKFLOW.md](.github/WORKFLOW.md) §7）

PR 本文は公開前に `make check-kiro-crew-pr-body` で検査します（手順書 §15）。

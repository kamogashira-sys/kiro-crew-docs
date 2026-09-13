# Makefile - kiro-crew-docs 検証ツール一括実行
#
# 使用方法:
#   make                          # ヘルプを表示
#   make check-kiro-crew-quick    # 執筆中の常用（links / structure のみ）
#   make check-kiro-crew-all      # コミット前・公開前（ネットワーク不要のもの全部）
#   make check-kiro-crew-ignore   # 公開範囲チェック（コミット前に必須・exit 0 必須）
#
# ⚠️ 「exit 0」は「検証して合格した」を必ずしも意味しません:
#   - 網羅性チェックは一次情報スナップショットが無いとスキップして成功扱いになります
#     （clone 直後・CI では未検証。出力に「未検証です」と表示します）
#   - 外部依存のターゲット（-urls / -freshness）は all に含まれません
#   検証スクリプトを新規作成・改修したときは、意図的に文書を壊して検出されることを
#   確認してください（ネガティブテスト）。手順は .github/WORKFLOW.md §6 を参照。
#
# Kiro Crew は OSS であり一次情報がリポジトリ（GitHub）と公式 docs（kiro.dev）の
# 二重構造である。main ブランチは日次で動くため、リポジトリを出典にした記述には
# 参照時点（取得日・commit SHA・版）の記録が必須（05_meta/10_update-guide.md §4）。

.DEFAULT_GOAL := help

.PHONY: help \
        check-kiro-crew-all check-kiro-crew-quick check-kiro-crew-ignore \
        check-kiro-crew-links check-kiro-crew-structure check-kiro-crew-counts \
        check-kiro-crew-consistency check-kiro-crew-notation check-kiro-crew-coverage \
        check-kiro-crew-changelog check-kiro-crew-scope check-kiro-crew-source-pin \
        check-kiro-crew-urls check-kiro-crew-urls-important check-kiro-crew-freshness \
        fetch-kiro-crew-snapshot extract-kiro-crew-changelog extract-kiro-crew-doc-index

SCRIPTS := ./scripts/kiro-crew-docs

# 一次情報スナップショットの置き場（日付ディレクトリ配下の入れ子。§7.4）。
# 未指定・不在ならチェックはスキップする（ネットワークに依存させない）。
SNAPSHOT_ROOT ?= kiro-crew-docs/06_embedded-docs
REPO_DIR  ?= $(shell ls -d $(SNAPSHOT_ROOT)/*/repo     2>/dev/null | sort | tail -1)
DOCS_DIR  ?= $(shell ls -d $(SNAPSHOT_ROOT)/*/repo/docs 2>/dev/null | sort | tail -1)
META_DIR  ?= $(shell ls -d $(SNAPSHOT_ROOT)/*/meta     2>/dev/null | sort | tail -1)
REL_DIR   ?= $(shell ls -d $(SNAPSHOT_ROOT)/*/releases 2>/dev/null | sort | tail -1)

# ------------------------------------------------------------
# ヘルプ
# ------------------------------------------------------------
help:
	@echo "=== kiro-crew-docs 検証ツール ==="
	@echo ""
	@echo "まとめて実行:"
	@echo "  make check-kiro-crew-all       # 全チェック（ネットワーク不要のもの全部）"
	@echo "  make check-kiro-crew-quick     # 高速チェック（links / structure のみ。執筆中の確認用）"
	@echo "  make check-kiro-crew-ignore    # 公開範囲チェック（コミット前に必須）"
	@echo ""
	@echo "個別に実行（ネットワーク不要）:"
	@echo "  make check-kiro-crew-links       # 内部リンク・アンカー・kiro.dev/GitHub URL 書式"
	@echo "  make check-kiro-crew-structure   # 構成・H1・出典2形式・公開境界"
	@echo "  make check-kiro-crew-counts      # 件数系 SSoT・ページ数3者一致"
	@echo "  make check-kiro-crew-consistency # 値系 SSoT・両併記の対称性（S3a/S15/S22）"
	@echo "  make check-kiro-crew-notation    # 表記規約 (a)〜(i)"
	@echo "  make check-kiro-crew-coverage    # 公式49ページ台帳・未割当検出"
	@echo "  make check-kiro-crew-changelog   # changelog 構造・日付2列"
	@echo "  make check-kiro-crew-scope       # スコープ境界（Kiro CLI 混入検出）"
	@echo "  make check-kiro-crew-source-pin  # 参照時点記録・削除済み仕様書の出典検出"
	@echo ""
	@echo "個別に実行（★外部サイトに依存。all / CI（PR）には含めない）:"
	@echo "  make check-kiro-crew-urls           # 公開文書の外部 URL 到達性"
	@echo "  make check-kiro-crew-urls-important # 重要 URL のみ"
	@echo "  make check-kiro-crew-freshness      # 更新検知（4系統）。OFFLINE=<dir> で検証可"
	@echo ""
	@echo "保守用:"
	@echo "  make fetch-kiro-crew-snapshot        # 一次情報スナップショットの取得"
	@echo "  make extract-kiro-crew-changelog     # CHANGELOG.md から版節・日付・項目を抽出"
	@echo "  make extract-kiro-crew-doc-index     # Tree API JSON から docs/ の内訳を生成"

# ------------------------------------------------------------
# まとめて実行
# ------------------------------------------------------------
check-kiro-crew-all: check-kiro-crew-links check-kiro-crew-structure check-kiro-crew-counts \
                     check-kiro-crew-consistency check-kiro-crew-notation check-kiro-crew-coverage \
                     check-kiro-crew-changelog check-kiro-crew-scope check-kiro-crew-source-pin
	@echo ""
	@echo "✅ kiro-crew-docs 全チェックが完了しました"
	@echo "   （外部 URL の到達性と更新検知は別ターゲットです）"

check-kiro-crew-quick: check-kiro-crew-links check-kiro-crew-structure
	@echo ""
	@echo "✅ kiro-crew-docs 高速チェックが完了しました"
	@echo "   （これは全チェックではありません。コミット前に make check-kiro-crew-all を実行してください）"

check-kiro-crew-ignore:
	@$(SCRIPTS)/check-ignore.sh

# ------------------------------------------------------------
# 個別ターゲット（ネットワーク不要）
# ------------------------------------------------------------
check-kiro-crew-links:
	@$(SCRIPTS)/check-links.py --check-anchors

check-kiro-crew-structure:
	@$(SCRIPTS)/check-structure.py

check-kiro-crew-counts:
	@if [ -n "$(DOCS_DIR)" ] && [ -d "$(DOCS_DIR)" ]; then \
	    $(SCRIPTS)/check-counts.py --docs-dir "$(DOCS_DIR)" --meta-dir "$(META_DIR)"; \
	else \
	    $(SCRIPTS)/check-counts.py; \
	fi

check-kiro-crew-consistency:
	@$(SCRIPTS)/check-consistency.py

check-kiro-crew-notation:
	@$(SCRIPTS)/check-notation.py

check-kiro-crew-coverage:
	@if [ -n "$(REPO_DIR)" ] && [ -d "$(REPO_DIR)" ]; then \
	    $(SCRIPTS)/check-coverage.py --repo-dir "$(REPO_DIR)"; \
	else \
	    echo "⚠️  網羅性チェックをスキップ: $(SNAPSHOT_ROOT) に一次情報のスナップショットがありません"; \
	    echo "   → これは「検証して合格した」ではありません（**未検証**です）"; \
	fi

check-kiro-crew-changelog:
	@if [ -n "$(REPO_DIR)" ] && [ -d "$(REPO_DIR)" ]; then \
	    $(SCRIPTS)/check-changelog.py --repo-dir "$(REPO_DIR)"; \
	else \
	    $(SCRIPTS)/check-changelog.py; \
	fi

check-kiro-crew-scope:
	@$(SCRIPTS)/check-scope.py

check-kiro-crew-source-pin:
	@$(SCRIPTS)/check-source-pin.py

# ------------------------------------------------------------
# 個別ターゲット（★外部サイトに依存。all / CI（PR）には含めない）
# ------------------------------------------------------------
check-kiro-crew-urls:
	@$(SCRIPTS)/check-urls.sh

check-kiro-crew-urls-important:
	@$(SCRIPTS)/check-urls.sh --important

OFFLINE ?=
check-kiro-crew-freshness:
	@if [ -n "$(OFFLINE)" ]; then \
	    $(SCRIPTS)/check-freshness.py --offline "$(OFFLINE)"; \
	else \
	    $(SCRIPTS)/check-freshness.py; \
	fi

# ------------------------------------------------------------
# 保守用（check-*-all には含めない）
# ------------------------------------------------------------
fetch-kiro-crew-snapshot:
	@$(SCRIPTS)/fetch-snapshot.sh

INDEX ?=
ENTRY ?=
ARGS ?=
extract-kiro-crew-changelog:
	@$(SCRIPTS)/extract-changelog.py $(ARGS)

extract-kiro-crew-doc-index:
	@$(SCRIPTS)/extract-doc-index.py $(ARGS)

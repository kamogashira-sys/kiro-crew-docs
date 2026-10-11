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
        fetch-kiro-crew-snapshot extract-kiro-crew-changelog extract-kiro-crew-doc-index \
        check-kiro-crew-cleanroom fetch-kiro-crew-primary check-kiro-crew-cloud \
        check-kiro-crew-ledger-current check-kiro-crew-cloud-freshness check-kiro-crew-pr-scope \
        check-kiro-crew-pr-body list-kiro-crew-open-items

SCRIPTS := ./scripts/kiro-crew-docs

# 一次情報スナップショットの置き場（日付ディレクトリ配下の入れ子。05_meta/10_update-guide.md §5.4）。
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
	@echo "  make check-kiro-crew-freshness      # 更新検知（4系統）。OFFLINE=<dir> で検証可。FRESHNESS_ARGS で追加引数"
	@echo "  make fetch-kiro-crew-primary VERSION=<版> [PREV=<前回版>]"
	@echo "                                      # 一次情報を CLOUD_ROOT（既定 /tmp/kiro-crew-primary）へ取得（冪等）"
	@echo "  make check-kiro-crew-cloud          # クラウド入口: スキップを合格にしない全検証（--strict）＋要約行"
	@echo "  make check-kiro-crew-ledger-current # 公式ページ台帳の Page updated・sha256 列が PIN.json と一致するか"
	@echo "  make check-kiro-crew-cloud-freshness"
	@echo "                                      # 更新検知（--strict --release-only）。freshness-result: rc=<n> を出す"
	@echo ""
	@echo "クラウド・PR 用（ネットワーク不要）:"
	@echo "  make check-kiro-crew-cleanroom TARGETS=\"...\" [ARGS=\"...\"]"
	@echo "                                      # 公開されるファイルだけの複製（/tmp）で TARGETS を実行"
	@echo "  make check-kiro-crew-pr-scope PROFILE=version-update|infra [BASE=origin/main] [HEAD_REV=<rev>]"
	@echo "                                      # PR の変更範囲が許可パス・許可行に収まるか"
	@echo "  make check-kiro-crew-pr-body PR_BODY=<file>|RUN_DIR=<dir> [CLOUD_ROOT=<dir>]"
	@echo "                                      # 公開される PR 本文の公開前検査（PIN.json のあるスナップショット1件が必須）"
	@echo "  make list-kiro-crew-open-items      # 公開ページの「食い違い」「未確認」「要検証」の全行と件数"
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

# 公開されるファイルだけの複製（/tmp/kcd-cleanroom.XXXX）で TARGETS を実行する。
# クラウドセッションの clone 直後と同じ条件（ローカル管理領域が無い）の再現。追加の変数は ARGS で渡す
TARGETS ?=
check-kiro-crew-cleanroom:
	@if [ -z "$(TARGETS)" ]; then echo "❌ TARGETS を指定してください（例: TARGETS=\"check-kiro-crew-all\"）"; exit 1; fi
	@$(SCRIPTS)/clean-room.sh $(TARGETS) $(ARGS)

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
FRESHNESS_ARGS ?=
check-kiro-crew-freshness:
	@if [ -n "$(OFFLINE)" ]; then \
	    $(SCRIPTS)/check-freshness.py --offline "$(OFFLINE)" $(FRESHNESS_ARGS); \
	else \
	    $(SCRIPTS)/check-freshness.py $(FRESHNESS_ARGS); \
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

# ------------------------------------------------------------
# クラウド（Kiro Web）・PR 用（check-*-all には含めない）
# ------------------------------------------------------------
# 一次情報の置き場（リポジトリの追跡対象には書かない）。Kiro Web では run ごとの cloud_root を渡す
VERSION ?=
PREV ?=
CLOUD_ROOT ?= /tmp/kiro-crew-primary
CLOUD_PREV_ROOT ?= /tmp/kiro-crew-primary-prev
CLOUD_VIA_ROOT ?= /tmp/kiro-crew-primary-via
CLOUD_SNAP = $(shell ls -d $(CLOUD_ROOT)/*/ 2>/dev/null)

# 冪等: $(CLOUD_ROOT)/*_$(VERSION)/PIN.json があれば target を取得しない。
# 検査の順序: ① PREV 指定時の base 一致（ほかの取得・検査より先） ② 前回版・経由版の有無と commit 照合
# ③ $(CLOUD_ROOT) 直下のスナップショットが1件であること
fetch-kiro-crew-primary:
	@if [ -z "$(VERSION)" ]; then echo "❌ VERSION を指定してください（例: VERSION=vX.Y.Z PREV=vA.B.C）"; exit 1; fi
	@set -e; pin=$$(ls $(CLOUD_ROOT)/*_$(VERSION)/PIN.json 2>/dev/null | head -1); \
	if [ -n "$$pin" ]; then \
	    if [ -n "$(PREV)" ]; then \
	        base=$$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("base") or "null")' "$$pin"); \
	        if [ "$$base" != "$(PREV)" ]; then echo "base mismatch: PIN=$$base PREV=$(PREV)"; exit 1; fi; \
	    fi; \
	    echo "=== 取得済み（取得を省略）: $$pin ==="; cat "$$pin"; echo ""; \
	else \
	    date=$$(TZ=Asia/Tokyo date +%Y%m%d); \
	    if [ -n "$(PREV)" ]; then \
	        $(SCRIPTS)/fetch-snapshot.sh --out-root "$(CLOUD_ROOT)" --base "$(PREV)" --via-root "$(CLOUD_VIA_ROOT)" "$${date}_$(VERSION)" "$(VERSION)"; \
	    else \
	        $(SCRIPTS)/fetch-snapshot.sh --out-root "$(CLOUD_ROOT)" "$${date}_$(VERSION)" "$(VERSION)"; \
	    fi; \
	    pin=$$(ls $(CLOUD_ROOT)/*_$(VERSION)/PIN.json | head -1); \
	fi; \
	if [ -n "$(PREV)" ]; then \
	    if [ -f "$(CLOUD_PREV_ROOT)/$(PREV)/repo/COMMIT_SHA" ]; then \
	        echo "前回版 $(PREV): 取得済み（$(CLOUD_PREV_ROOT)/$(PREV)）"; \
	    else \
	        $(SCRIPTS)/fetch-snapshot.sh --repo-only --out-root "$(CLOUD_PREV_ROOT)" "$(PREV)" "$(PREV)"; \
	    fi; \
	fi; \
	python3 -c 'import json,sys; [print(v["ref"]+"\t"+v["commit_sha"]) for v in json.load(open(sys.argv[1])).get("via", [])]' "$$pin" \
	| while IFS="$$(printf '\t')" read -r vref vsha; do \
	    if [ ! -f "$(CLOUD_VIA_ROOT)/$$vref/repo/COMMIT_SHA" ]; then \
	        echo "経由版 $$vref: $(CLOUD_VIA_ROOT)/$$vref が無いため取り直します"; \
	        $(SCRIPTS)/fetch-snapshot.sh --repo-only --out-root "$(CLOUD_VIA_ROOT)" "$$vref" "$$vref" || exit 1; \
	    fi; \
	    got=$$(cat "$(CLOUD_VIA_ROOT)/$$vref/repo/COMMIT_SHA"); \
	    if [ "$$got" != "$$vsha" ]; then echo "via commit mismatch: $$vref PIN=$$vsha $(CLOUD_VIA_ROOT)=$$got"; exit 1; fi; \
	    echo "経由版 $$vref: COMMIT_SHA が PIN.json の via と一致（$$got）"; \
	done; \
	n=$$(ls -d $(CLOUD_ROOT)/*/ 2>/dev/null | wc -l); \
	if [ "$$n" -ne 1 ]; then echo "snapshot count mismatch: $$n under CLOUD_ROOT (expected 1)"; exit 1; fi; \
	echo "✅ 一次情報: $(CLOUD_ROOT) 直下のスナップショット 1 件"

# クラウド入口。スキップを合格にしない（--strict）。1つでも失敗したら非0。末尾に PR 本文へ転記する要約行を出す
check-kiro-crew-cloud:
	@snap="$(CLOUD_SNAP)"; set -- $$snap; \
	if [ "$$#" -ne 1 ]; then echo "❌ $(CLOUD_ROOT) 直下のスナップショットが $$# 件です（1件である必要があります）。検査を行いませんでした"; \
	    echo "   → make fetch-kiro-crew-primary VERSION=<版> PREV=<前回版> CLOUD_ROOT=$(CLOUD_ROOT)"; exit 1; fi; \
	snap=$${1%/}; log=$$(mktemp -d /tmp/kcd-cloud.XXXX); fail=0; : > "$$log/rc.txt"; \
	run() { name="$$1"; shift; echo ""; echo "######## $$name ########"; \
	    "$$@" > "$$log/$$name.txt" 2>&1; rc=$$?; cat "$$log/$$name.txt"; \
	    echo "######## $$name: exit $$rc"; echo "$$name: exit $$rc" >> "$$log/rc.txt"; \
	    [ "$$rc" -eq 0 ] || fail=1; }; \
	run 01-ignore $(MAKE) --no-print-directory check-kiro-crew-ignore; \
	run 02-all $(MAKE) --no-print-directory check-kiro-crew-all SNAPSHOT_ROOT="$(CLOUD_ROOT)"; \
	run 03-coverage-strict $(SCRIPTS)/check-coverage.py --strict --repo-dir "$$snap/repo"; \
	run 04-counts-strict $(SCRIPTS)/check-counts.py --strict --docs-dir "$$snap/repo/docs" --meta-dir "$$snap/meta"; \
	run 05-changelog-strict $(SCRIPTS)/check-changelog.py --strict --repo-dir "$$snap/repo"; \
	run 06-notation-strict $(SCRIPTS)/check-notation.py --strict; \
	run 07-measure-ssot $(SCRIPTS)/measure-ssot.py --snapshot "$$snap" --expect-constants; \
	run 08-urls-important $(MAKE) --no-print-directory check-kiro-crew-urls-important; \
	echo ""; echo "=== check-kiro-crew-cloud 要約（PR 本文⑤へ転記）==="; \
	echo "一次情報: $$snap"; cat "$$log/rc.txt"; \
	grep -h '^KCD-SUMMARY:' "$$log"/0*.txt | sed 's/^KCD-SUMMARY: /要約: /'; \
	rm -rf "$$log"; \
	if [ "$$fail" -ne 0 ]; then echo "❌ check-kiro-crew-cloud: 失敗あり"; exit 1; fi; \
	echo "✅ check-kiro-crew-cloud: すべて exit 0"

# 公式ページ台帳の Page updated・.md sha256 列が PIN.json と1件でも異なれば exit 1（版更新 PR でだけ使う）
check-kiro-crew-ledger-current:
	@snap="$(CLOUD_SNAP)"; set -- $$snap; \
	if [ "$$#" -ne 1 ]; then echo "❌ $(CLOUD_ROOT) 直下のスナップショットが $$# 件です（1件である必要があります）。検査を行いませんでした"; exit 1; fi; \
	$(SCRIPTS)/measure-ssot.py --snapshot "$${1%/}" --expect-ledger-current

# make はレシピの非0をすべて exit 2 にするため、スクリプトの終了コードを freshness-result 行で出す
check-kiro-crew-cloud-freshness:
	@$(SCRIPTS)/check-freshness.py --strict --release-only; rc=$$?; \
	echo "freshness-result: rc=$$rc"; exit $$rc

BASE ?= origin/main
HEAD_REV ?=
PROFILE ?=
check-kiro-crew-pr-scope:
	@if [ -z "$(PROFILE)" ]; then echo "❌ PROFILE を指定してください（version-update または infra）"; exit 1; fi
	@$(SCRIPTS)/check-pr-scope.py --base "$(BASE)" $(if $(HEAD_REV),--head "$(HEAD_REV)") --profile "$(PROFILE)"

RUN_DIR ?=
PR_BODY ?= $(RUN_DIR)/pr-body.md
SNAPSHOT ?= $(shell ls -d $(CLOUD_ROOT)/*/ 2>/dev/null)
check-kiro-crew-pr-body:
	@set -- $(SNAPSHOT); \
	if [ "$$#" -ne 1 ]; then echo "❌ SNAPSHOT が $$# 件です（CLOUD_ROOT=$(CLOUD_ROOT) 直下に1件である必要があります）。検査を行いませんでした"; exit 1; fi; \
	if [ ! -f "$(PR_BODY)" ]; then echo "❌ PR 本文 $(PR_BODY) がありません。検査を行いませんでした"; exit 1; fi; \
	if [ ! -f "$${1%/}/PIN.json" ]; then echo "❌ SNAPSHOT $${1%/} に PIN.json がありません（取得が完了していません）。検査を行いませんでした"; \
	    echo "   → make fetch-kiro-crew-primary VERSION=<版> PREV=<前回版> CLOUD_ROOT=$(CLOUD_ROOT)"; exit 1; fi; \
	$(SCRIPTS)/check-pr-body.sh "$(PR_BODY)" --snapshot "$${1%/}"

# 公開ページの「食い違い」「未確認」「要検証」を全行列挙し、最終行に件数を出す。0件なら exit 1（検索の空振りを合格にしない）
OPEN_ITEMS_PATHS ?= kiro-crew-docs/0[0-4]_*
list-kiro-crew-open-items:
	@out=$$(grep -rnE '食い違い|未確認|要検証' $(OPEN_ITEMS_PATHS)); printf '%s\n' "$$out"; n=$$(printf '%s\n' "$$out" | grep -c .); echo "open-items: $$n"; test "$$n" -ge 1

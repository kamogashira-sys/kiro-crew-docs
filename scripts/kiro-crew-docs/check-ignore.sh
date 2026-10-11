#!/usr/bin/env bash
# 公開範囲の機械検証（作業計画書 Phase 1-5 / 4-1 / 5-3）
#
# ローカル管理対象が .gitignore で除外されていること、および
# 公開対象が誤って除外されていないことを機械確認する。
#
# 使い方: make check-kiro-crew-ignore  または  scripts/kiro-crew-docs/check-ignore.sh
#
# 走査対象（ローカル絶対パス・トークン・秘密鍵・スナップショット由来ファイル）は
# git ls-files -co --exclude-standard（追跡＋未追跡かつ非除外）。git add 前の未追跡ファイルの漏えいも検出する。
# トークン・秘密鍵の書式は一致箇所のファイル名と行番号だけを表示し、値を出力しない。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT" || exit 1

fail=0

# ローカル管理対象（GitHub 非公開）: ignore されていなければ NG
LOCAL_ONLY=(
  "kiro-crew-docs/work_plans/x_plan.md"
  "kiro-crew-docs/05_meta/10_update-guide.md"
  "kiro-crew-docs/05_meta/templates/worklog.md"
  "kiro-crew-docs/05_meta/ledger-builtin-apps.md"
  "kiro-crew-docs/06_embedded-docs/x.md"
  "kiro-crew-docs/06_embedded-docs/20260816/repo/README.md"
  "work_records/20260816/x_worklog.md"
  "x_update_plan.md"
  "x_review_report.md"
  "x_investigation.md"
  "x_worklog.md"
  ".claude/settings.local.json"
  ".kiro/settings/mcp.json"
  ".kiro/steering/x.md"
  ".kiro/agents/x.json"
  ".kiro/hooks/x.kiro.hook"
  ".kiro/specs/x/requirements.md"
  "kiro-crew-docs/work_plans/cloud-runs/r/x.md"
  ".kiro/cloud-runs/r/primary/x/PIN.json"
  ".kiro/cloud-runs/r/primary-prev/x/repo/COMMIT_SHA"
  ".kiro/cloud-runs/r/primary-via/x/repo/COMMIT_SHA"
  ".kiro/cloud-runs/r/primary-src/x"
)

# 公開対象: ignore されていたら NG
PUBLIC=(
  "README.md"
  "AGENTS.md"
  "LICENSE"
  "CODE_OF_CONDUCT.md"
  ".github/ISSUE_TEMPLATE/bug_report.yml"
  ".github/WORKFLOW.md"
  ".github/COMMIT_CHECKLIST.md"
  ".github/pull_request_template.md"
  ".github/workflows/validate-kiro-crew-docs.yml"
  ".github/workflows/release-kiro-crew-docs.yml"
  ".github/UPDATE_GUIDE.md"
  "kiro-crew-docs/README.md"
  "kiro-crew-docs/00_information/README.md"
  "kiro-crew-docs/01_features/README.md"
  "kiro-crew-docs/02_update/README.md"
  "kiro-crew-docs/03_deployment/README.md"
  "kiro-crew-docs/04_reference/README.md"
  "scripts/kiro-crew-docs/check-ignore.sh"
  "scripts/kiro-crew-docs/check-audit-groups.py"
  "scripts/kiro-crew-docs/check-peripheral-values.py"
  "scripts/kiro-crew-docs/ledgers/official-pages.md"
  "scripts/kiro-crew-docs/ledgers/modules.md"
  "scripts/kiro-crew-docs/ledgers/builtin-apps.md"
  "scripts/kiro-crew-docs/ledgers/cli-commands.md"
  "scripts/kiro-crew-docs/ledgers/ssot-status.md"
  "Makefile"
)

echo "=== ローカル管理対象が除外されていることを確認 ==="
for p in "${LOCAL_ONLY[@]}"; do
  if git check-ignore -q "$p"; then
    echo "  OK   ignored: $p"
  else
    echo "  FAIL not ignored: $p"
    fail=1
  fi
done

echo "=== 公開対象が除外されていないことを確認 ==="
for p in "${PUBLIC[@]}"; do
  if git check-ignore -q "$p"; then
    echo "  FAIL wrongly ignored: $p"
    fail=1
  else
    echo "  OK   publishable: $p"
  fi
done

echo "=== コミット済みツリーにローカル管理対象が含まれていないことを確認 ==="
tracked=$(git ls-files | grep -E "work_plans/|05_meta/|06_embedded-docs/|work_records/|_plan\.md$|_review_report\.md$|_investigation\.md$|_worklog\.md$" || true)
if [ -n "$tracked" ]; then
  echo "  FAIL 以下がトラックされています:"
  echo "$tracked" | sed 's/^/    /'
  fail=1
else
  echo "  OK   local-only files are not tracked"
fi

echo "=== 公開ファイルにローカル絶対パス・ユーザー名が含まれていないことを確認 ==="
# 対象は公開されうるファイル（追跡＋未追跡かつ非除外）。バイナリは除外。
# `/home/kirocrew` はDockerコンテナ内のホームディレクトリを指す一次情報由来の記述
# （公式 running-24-7.md の Docker 実行例 `-v kirocrew-home:/home/kirocrew` と同一）であり、
# レビュアーのローカル環境のユーザー名ではない。本スクリプト自身の説明コメントも除外する。
leak=$(git ls-files -co --exclude-standard -z | xargs -0 -r grep -n -I -E '/home/[a-z_][a-z0-9_-]*|/Users/[A-Za-z0-9_-]+' 2>/dev/null \
  | grep -v -E '(^|[^a-z0-9_-])home/kirocrew([^a-z0-9_-]|$)' || true)
if [ -n "$leak" ]; then
  echo "  FAIL ローカル絶対パスらしい記述があります:"
  echo "$leak" | sed 's/^/    /'
  fail=1
else
  echo "  OK   no local absolute paths in tracked or untracked (non-ignored) files"
fi

echo "=== 公開ファイルにトークン・秘密鍵の書式が含まれていないことを確認 ==="
# 書式: GitHub トークンの接頭辞（gh + p/o/s + "_"、github + "_pat_"）と PEM 秘密鍵の見出し。
# 本スクリプト自身が一致しないよう、正規表現は文字クラスで書く。値は出力せず「ファイル:行」だけを表示する。
secret=$(git ls-files -co --exclude-standard -z | xargs -0 -r grep -n -I -E 'gh[pos]_|github[_]pat_|-----BEGIN [A-Z ]*PRIVATE[ ]KEY-----' 2>/dev/null \
  | cut -d: -f1,2 || true)
if [ -n "$secret" ]; then
  echo "  FAIL トークン・秘密鍵の書式に一致する行があります（値は表示しません）:"
  echo "$secret" | sed 's/^/    /'
  fail=1
else
  echo "  OK   no token / private key formats"
fi

echo "=== スナップショット由来のファイルが公開されうる位置に無いことを確認 ==="
# 一次情報スナップショット（fetch-snapshot.sh の出力）は /tmp、Kiro Web ではワークスペースの .kiro/cloud-runs/、
# またはローカル管理領域にだけ置く
snap=$(git ls-files -co --exclude-standard \
  | grep -E '(^|/)(COMMIT_SHA|PIN\.json|releases\.json|tree\.json|sitemap\.xml)$|(^|/)docs_md/' || true)
if [ -n "$snap" ]; then
  echo "  FAIL スナップショット由来らしいファイルがあります:"
  echo "$snap" | sed 's/^/    /'
  fail=1
else
  echo "  OK   no snapshot-derived files"
fi

if [ "$fail" -eq 0 ]; then
  echo "=== 結果: すべて OK ==="
else
  echo "=== 結果: 失敗あり（公開してはいけない状態） ==="
fi
exit "$fail"

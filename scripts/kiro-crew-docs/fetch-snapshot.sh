#!/usr/bin/env bash
# fetch-snapshot.sh - 一次情報スナップショットの取得（保守用。check-*-all には含めない）
#
# 使用方法:
#   scripts/kiro-crew-docs/fetch-snapshot.sh [YYYYMMDD]
#
# 取得内容:
#   - GitHub: KiroCrew を --depth 1 で clone（docs/ とルート .md）。COMMIT_SHA を記録
#   - 公式docs: kiro.dev/docs/crew/ 配下43ページのHTML + .md companion
#   - meta: sitemap.xml・Tree API JSON
#   - releases: Releases API JSON
#
# 保存先: kiro-crew-docs/06_embedded-docs/<日付>/
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

DATE="${1:-$(date +%Y%m%d)}"
SNAP="kiro-crew-docs/06_embedded-docs/${DATE}"
UA="Mozilla/5.0"

mkdir -p "$SNAP/repo" "$SNAP/docs" "$SNAP/docs_md" "$SNAP/releases" "$SNAP/meta"

echo "=== 1. GitHubリポジトリのclone ==="
TMP_CLONE=$(mktemp -d)
git clone --depth 1 https://github.com/kirodotdev/KiroCrew.git "$TMP_CLONE"
git -C "$TMP_CLONE" rev-parse HEAD > "$SNAP/repo/COMMIT_SHA"
cp -r "$TMP_CLONE/docs" "$SNAP/repo/"
cp "$TMP_CLONE"/*.md "$SNAP/repo/" 2>/dev/null || true
cp "$TMP_CLONE/LICENSE" "$TMP_CLONE/NOTICE" "$SNAP/repo/" 2>/dev/null || true
rm -rf "$TMP_CLONE"
echo "COMMIT_SHA: $(cat "$SNAP/repo/COMMIT_SHA")"

echo "=== 2. Releases / sitemap / Tree API ==="
curl -s "https://api.github.com/repos/kirodotdev/KiroCrew/releases?per_page=100" -o "$SNAP/releases/releases.json"
curl -s "https://api.github.com/repos/kirodotdev/KiroCrew/git/trees/main?recursive=1" -o "$SNAP/meta/tree.json"
curl -s -A "$UA" "https://kiro.dev/sitemap.xml" -o "$SNAP/meta/sitemap.xml"
curl -s "https://api.github.com/repos/kirodotdev/KiroCrew" -o "$SNAP/meta/repo_info.json"

echo "=== 3. 公式43ページのHTML + .md companion ==="
python3 - "$SNAP/meta/sitemap.xml" > /tmp/crew_urls_fetch.txt <<'PY'
import sys, re
s = open(sys.argv[1], encoding="utf-8").read()
urls = re.findall(r"<loc>(https://kiro\.dev/docs/crew/[^<]*)</loc>", s)
for u in urls:
    print(u)
PY

cd "$SNAP/docs"
while IFS= read -r url; do
  slug=$(echo "$url" | sed -e 's#https://kiro.dev/docs/crew/##' -e 's#/$##' -e 's#/#__#g')
  [ -z "$slug" ] && slug="index"
  curl -s -A "$UA" "$url" -o "${slug}.html"
done < /tmp/crew_urls_fetch.txt
cd - > /dev/null

cd "$SNAP/docs_md"
while IFS= read -r url; do
  slug=$(echo "$url" | sed -e 's#https://kiro.dev/docs/crew/##' -e 's#/$##' -e 's#/#__#g')
  [ -z "$slug" ] && slug="index"
  mdurl="${url%/}.md"
  curl -s -A "$UA" "$mdurl" -o "${slug}.md"
done < /tmp/crew_urls_fetch.txt
cd - > /dev/null

echo ""
echo "=== 完了 ==="
echo "保存先: $SNAP"
echo "docs/ HTML: $(find "$SNAP/docs" -name '*.html' | wc -l) 件"
echo "docs_md/ MD: $(find "$SNAP/docs_md" -name '*.md' | wc -l) 件"
echo "docs/配下ファイル数: $(find "$SNAP/repo/docs" -type f | wc -l) 件"

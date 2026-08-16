#!/usr/bin/env bash
# check-urls.sh - 公開文書に載せた外部 URL の到達性チェック（★外部サイトに依存）
#
# 使用方法:
#   scripts/kiro-crew-docs/check-urls.sh              # 全件
#   scripts/kiro-crew-docs/check-urls.sh --important  # 重要 URL のみ（切り分け用）
#
# ⚠️ **本スクリプトは外部サイトにアクセスします。**
#    レート制限・一時障害で失敗しうるため `make check-kiro-crew-all` には**含めません**。
#
# 作法:
#   - kiro.dev の docs/crew/blog URL は末尾スラッシュ必須（無しは301）
#   - GitHub の blob URL は末尾スラッシュを付けない
#   - User-Agent 必須（空文字の明示指定は403）
#   - GitHub API は未認証60 req/hのレート制限に注意
#
# 除外: プレースホルダURL・ローカル管理領域
#
# fail-safe:
#   - ネットワークそのものが不通なら exit 0 ＋ 案内
#   - 到達性の失敗（404・予期しないリダイレクト等）は exit 1

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT" || exit 1

UA="Mozilla/5.0"
IMPORTANT_ONLY=0
[ "${1:-}" = "--important" ] && IMPORTANT_ONLY=1

IMPORTANT=(
  "https://kiro.dev/docs/crew/"
  "https://kiro.dev/crew/"
  "https://github.com/kirodotdev/KiroCrew"
  "https://kiro.dev/sitemap.xml"
)

echo "=== kiro-crew-docs 外部 URL 到達性チェック ==="
echo ""

if ! curl -sS --max-time 15 -A "$UA" -o /dev/null "https://kiro.dev/"; then
  echo "⚠️  ネットワークに到達できませんでした（**未検証**です）"
  echo "   → これは「URL が有効であることを検証した」ではありません"
  exit 0
fi

if [ "$IMPORTANT_ONLY" -eq 1 ]; then
  printf '%s\n' "${IMPORTANT[@]}" > /tmp/kc_urls.txt
  echo "重要 URL のみを検査します（${#IMPORTANT[@]} 件）"
else
  python3 - > /tmp/kc_urls.txt <<'PY'
import glob, os, re

EXCLUDE = ("05_meta", "06_embedded-docs", "work_plans", "work_records")
PLACEHOLDER = re.compile(r"[<>{}]|（|\((?:パス|module|スラッグ|slug|path)\)")
REGEX_FRAGMENT = re.compile(r"\\\.|\[\^|\.\*|\[0-9\]|\\d")
THIRD_PARTY = re.compile(
    r"^https?://(?!(?:kiro\.dev|app\.kiro\.dev|github\.com/kamogashira-sys|"
    r"github\.com/kirodotdev|raw\.githubusercontent\.com/kirodotdev|discord\.gg))")

files = sorted(glob.glob("kiro-crew-docs/**/*.md", recursive=True))
files = [f for f in files if not any(x in f for x in EXCLUDE)]
files += ["README.md"] + sorted(glob.glob(".github/*.md"))

urls = set()
for f in files:
    if not os.path.isfile(f):
        continue
    for m in re.finditer(r"https?://[^\s<>()\[\]\"'`|]+", open(f, encoding="utf-8").read()):
        u = m.group(0).rstrip(".,;:)")
        if PLACEHOLDER.search(u) or REGEX_FRAGMENT.search(u) or THIRD_PARTY.match(u):
            continue
        urls.add(u)

for u in sorted(urls):
    print(u)
PY
  echo "公開文書から $(wc -l < /tmp/kc_urls.txt) 件の URL を抽出しました"
fi

echo ""

fail=0
ok=0
declare -a failures=()

while IFS= read -r url; do
  [ -z "$url" ] && continue
  code=$(curl -sS --max-time 20 -o /dev/null -w '%{http_code}' -A "$UA" "$url" 2>/dev/null || echo "000")
  case "$code" in
    200|204)
      ok=$((ok + 1))
      ;;
    301|302|307|308)
      case "$url" in
        https://kiro.dev/docs/*|https://kiro.dev/crew/*)
          failures+=("$code $url  → リダイレクトされました（末尾スラッシュの有無を確認してください）")
          fail=1
          ;;
        *)
          # GitHub は正常なリダイレクトがあり得る（例: デフォルトブランチ解決）
          ok=$((ok + 1))
          ;;
      esac
      ;;
    000)
      failures+=("--- $url  → 接続できませんでした（一時障害・レート制限の可能性）")
      fail=1
      ;;
    403)
      case "$url" in
        https://api.github.com/*)
          failures+=("403 $url  → GitHub APIレート制限の可能性（未認証60 req/h）")
          ;;
        *)
          failures+=("403 $url")
          ;;
      esac
      fail=1
      ;;
    *)
      failures+=("$code $url")
      fail=1
      ;;
  esac
done < /tmp/kc_urls.txt

echo "到達 OK: $ok 件"
if [ ${#failures[@]} -gt 0 ]; then
  echo ""
  echo "❌ 到達できなかった URL: ${#failures[@]} 件"
  for x in "${failures[@]}"; do
    echo "   - $x"
  done
  echo ""
  echo "❌ URL 到達性チェックに失敗しました"
  exit 1
fi

echo ""
echo "✅ すべての外部 URL に到達できました"
exit 0

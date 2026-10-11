#!/usr/bin/env bash
# fetch-snapshot.sh - 一次情報スナップショットの取得（保守用。check-*-all には含めない）
#
# 使用方法:
#   scripts/kiro-crew-docs/fetch-snapshot.sh [オプション] [YYYYMMDD] [REF]
#
#   YYYYMMDD: 保存先ディレクトリ名（既定: 当日）。タグ基準で取得する場合は
#             `20260822_v0.3.0` のように版を含めた名前を推奨する
#             （Makefile は `sort | tail -1` で最新1件を選ぶため、
#               同日の main HEAD スナップショットより後にソートされる名前にする）
#   REF:      取得する git ref（タグ・ブランチ）。既定: main
#             リリース版のSSoTを測る場合は必ずタグを指定する
#             例: scripts/kiro-crew-docs/fetch-snapshot.sh 20260822_v0.3.0 v0.3.0
#
# オプション:
#   --out-root <dir>   保存先のルート（既定: kiro-crew-docs/06_embedded-docs。従来どおり）。
#                      リポジトリ外（/tmp 等）に取得する場合に使う。既に中身のある保存先には取得しない
#   --repo-only        GitHub の clone（docs/ とルート .md）と COMMIT_SHA・REF だけを取得する（前回版・経由版用）
#   --base <版>        前回版。releases.json から経由版（base より後・REF より前に公開された安定版）を列挙する
#   --via-root <dir>   経由版の保存先のルート（--base と併用。<dir>/<版>/repo に --repo-only と同じ内容を置く）
#   --extra-url <URL>  公式ページの取得対象に URL を1件足す（ネガティブテスト用。繰り返し指定可）
#   -h, --help         使い方と、この引数での保存先を表示して終了する（取得しない）
#
# 環境変数:
#   KCD_RELEASES_PER_PAGE  Releases API の1ページの件数（既定 100）。Link ヘッダの rel="next" がある間だけ次ページを取得する
#   GITHUB_TOKEN           あれば api.github.com への要求に Authorization ヘッダを付ける（値は出力しない）
#
# 取得内容:
#   - GitHub: KiroCrew を --depth 1 で clone（docs/ とルート .md）。COMMIT_SHA・REF を記録
#   - 公式docs: sitemap.xml の kiro.dev/docs/crew/ 配下の全ページの HTML + .md companion（件数は sitemap の実測）
#   - meta: sitemap.xml・Tree API JSON・repo 情報
#   - releases: Releases API JSON（全ページを1つの配列にまとめる）
#   - PIN.json: 一次情報の固定値（ref・commit・Release 公開日・CHANGELOG 日付・参照日・
#     公式ページの Page updated と .md の sha256・前回版・経由版）
#
# 失敗の扱い:
#   すべての HTTP 取得で 200 以外・0バイトを失敗（exit 1）にする。.md companion の 404 も失敗。
#   sitemap の crew URL が0件、取得した HTML・.md の件数が sitemap の件数と一致しない、
#   Page updated が抽出できないページがある、--base の版が releases.json に無い、のいずれも exit 1。
#   途中で失敗した場合（中断を含む）は、この実行で新しく作った保存先（<out-root>/<YYYYMMDD>・経由版の
#   <via-root>/<版>、およびこの実行で作ったルート）を削除する。実行前から中身のあった保存先は削除しない。
#   取得失敗の残骸が「取得済み」「保存先が空ではない」と扱われて、再実行・Retry が止まるのを防ぐため。
#
# 制約:
#   - **src/ は取得しない**（docs/ とルート .md のみ）。builtin App数など src/ 由来の
#     SSoT を測る場合は別途 full clone が必要:
#       git clone https://github.com/kirodotdev/KiroCrew.git <dir> && git -C <dir> checkout <REF>
#   - 公式docs（kiro.dev）は REF に連動しない。常に取得時点の内容になる
#
# 保存先: <out-root>/<YYYYMMDD>/（既定 kiro-crew-docs/06_embedded-docs/<日付>/）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

GH_REPO_URL="https://github.com/kirodotdev/KiroCrew.git"
API="https://api.github.com/repos/kirodotdev/KiroCrew"
UA="Mozilla/5.0"
DEFAULT_OUT_ROOT="kiro-crew-docs/06_embedded-docs"

OUT_ROOT="$DEFAULT_OUT_ROOT"
OUT_ROOT_GIVEN=0
REPO_ONLY=0
BASE=""
VIA_ROOT=""
EXTRA_URLS=()
SHOW_HELP=0
POSITIONAL=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --out-root)  OUT_ROOT="${2:?--out-root には値が必要です}"; OUT_ROOT_GIVEN=1; shift 2 ;;
    --repo-only) REPO_ONLY=1; shift ;;
    --base)      BASE="${2:?--base には値が必要です}"; shift 2 ;;
    --via-root)  VIA_ROOT="${2:?--via-root には値が必要です}"; shift 2 ;;
    --extra-url) EXTRA_URLS+=("${2:?--extra-url には値が必要です}"); shift 2 ;;
    -h|--help)   SHOW_HELP=1; shift ;;
    --) shift; POSITIONAL+=("$@"); break ;;
    -*) echo "❌ 不明なオプション: $1" >&2; exit 1 ;;
    *)  POSITIONAL+=("$1"); shift ;;
  esac
done

DATE="${POSITIONAL[0]:-$(date +%Y%m%d)}"
REF="${POSITIONAL[1]:-main}"
SNAP="${OUT_ROOT%/}/${DATE}"
PER_PAGE="${KCD_RELEASES_PER_PAGE:-100}"

if [ "$SHOW_HELP" -eq 1 ]; then
  sed -n '2,/^set -euo/p' "${BASH_SOURCE[0]}" | sed -e '$d' -e 's/^# \{0,1\}//'
  echo "この引数での保存先: $SNAP（REF: $REF）"
  echo "既定の保存先ルート: $DEFAULT_OUT_ROOT"
  exit 0
fi

if [ -n "$BASE" ] && [ -z "$VIA_ROOT" ]; then
  echo "❌ --base には --via-root の指定が必要です" >&2
  exit 1
fi
if [ "$REPO_ONLY" -eq 1 ] && { [ -n "$BASE" ] || [ "${#EXTRA_URLS[@]}" -gt 0 ]; }; then
  echo "❌ --repo-only は --base・--extra-url と併用できません" >&2
  exit 1
fi

# --out-root を明示したときは、既に中身のある保存先に上書きしない（古いファイルの混在による偽の件数一致を防ぐ）
if [ "$OUT_ROOT_GIVEN" -eq 1 ] && [ -d "$SNAP" ] && [ -n "$(ls -A "$SNAP" 2>/dev/null)" ]; then
  echo "❌ 保存先が既に存在し空ではありません: $SNAP" >&2
  exit 1
fi

AUTH_HEADER=()
if [ -n "${GITHUB_TOKEN:-}" ]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${GITHUB_TOKEN}")
  echo "（GITHUB_TOKEN が設定されているため api.github.com に認証ヘッダを付けます。値は表示しません）"
fi

WORK=$(mktemp -d /tmp/kcd-fetch.XXXX)

# 失敗時に片付ける保存先（この実行で作ったものだけ）。NEW_DIRS は実行前に存在しなかったディレクトリ
# （失敗時に丸ごと削除）、EMPTIED_DIRS は実行前に空だったディレクトリ（失敗時に中身だけ削除）
NEW_DIRS=()
EMPTIED_DIRS=()
mark_new() {
  if [ ! -e "$1" ]; then
    NEW_DIRS+=("$1")
  elif [ -d "$1" ] && [ -z "$(ls -A "$1" 2>/dev/null)" ]; then
    EMPTIED_DIRS+=("$1")
  fi
}
cleanup() {
  local rc=$? i d
  rm -rf "$WORK"
  [ "$rc" -eq 0 ] && return 0
  # 作った順の逆（経由版 → 保存先 → ルート）に片付ける
  for ((i = ${#EMPTIED_DIRS[@]} - 1; i >= 0; i--)); do
    d="${EMPTIED_DIRS[$i]}"
    if [ -d "$d" ] && [ -n "$(ls -A "$d" 2>/dev/null)" ]; then
      find "$d" -mindepth 1 -delete
      echo "（失敗したため、この実行で書き込んだ中身を削除しました: $d）" >&2
    fi
  done
  for ((i = ${#NEW_DIRS[@]} - 1; i >= 0; i--)); do
    d="${NEW_DIRS[$i]}"
    if [ -e "$d" ]; then
      rm -rf "$d"
      echo "（失敗したため、この実行で作った保存先を削除しました: $d）" >&2
    fi
  done
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

mark_new "${OUT_ROOT%/}"
mark_new "$SNAP"
if [ -n "$VIA_ROOT" ]; then
  mark_new "${VIA_ROOT%/}"
fi

# http_get <url> <out> [curl の追加引数...]: 200 以外・0バイトなら失敗（return 1）
http_get() {
  local url="$1" out="$2" code
  shift 2
  if ! code=$(curl -sS -L -A "$UA" -w '%{http_code}' -o "$out" "$@" "$url"); then
    echo "❌ 取得失敗（curl エラー）: $url" >&2
    return 1
  fi
  if [ "$code" != "200" ]; then
    echo "❌ 取得失敗（HTTP $code）: $url" >&2
    return 1
  fi
  if [ ! -s "$out" ]; then
    echo "❌ 取得失敗（0バイト）: $url" >&2
    return 1
  fi
}

# clone_repo <ref> <snapdir>: --depth 1 で clone し docs/ とルート .md・LICENSE・NOTICE と COMMIT_SHA・REF を保存
# 保存先の repo/ は clone に成功してから作り、COMMIT_SHA は最後に書く（途中の失敗で「取得済み」に見せない）
clone_repo() {
  local ref="$1" dir="$2" tmp
  tmp=$(mktemp -d "$WORK/clone.XXXX")
  if ! git -c advice.detachedHead=false clone -q --depth 1 --branch "$ref" "$GH_REPO_URL" "$tmp/r"; then
    echo "❌ clone に失敗しました（ref: $ref。存在しないタグ・ネットワーク不通の可能性）" >&2
    exit 1
  fi
  mkdir -p "$dir/repo"
  printf '%s\n' "$ref" > "$dir/repo/REF"
  cp -r "$tmp/r/docs" "$dir/repo/"
  cp "$tmp/r"/*.md "$dir/repo/" 2>/dev/null || true
  cp "$tmp/r/LICENSE" "$tmp/r/NOTICE" "$dir/repo/" 2>/dev/null || true
  git -C "$tmp/r" rev-parse HEAD > "$dir/repo/COMMIT_SHA"
  rm -rf "$tmp"
}

echo "=== 1. GitHubリポジトリのclone（ref: $REF）==="
clone_repo "$REF" "$SNAP"
echo "REF: $REF"
echo "COMMIT_SHA: $(cat "$SNAP/repo/COMMIT_SHA")"

if [ "$REPO_ONLY" -eq 1 ]; then
  echo ""
  echo "=== 完了（--repo-only）==="
  echo "保存先: $SNAP"
  echo "REF: $REF / COMMIT_SHA: $(cat "$SNAP/repo/COMMIT_SHA")"
  exit 0
fi

mkdir -p "$SNAP/docs" "$SNAP/docs_md" "$SNAP/releases" "$SNAP/meta"

echo "=== 2. sitemap と公式ページの URL 抽出 ==="
http_get "https://kiro.dev/sitemap.xml" "$SNAP/meta/sitemap.xml"
python3 - "$SNAP/meta/sitemap.xml" > "$WORK/sitemap_urls.txt" <<'PY'
import sys, re
s = open(sys.argv[1], encoding="utf-8").read()
for u in re.findall(r"<loc>(https://kiro\.dev/docs/crew/[^<]*)</loc>", s):
    print(u)
PY
SITEMAP_COUNT=$(grep -c . "$WORK/sitemap_urls.txt" || true)
echo "sitemap の docs/crew/ URL: ${SITEMAP_COUNT} 件"
if [ "$SITEMAP_COUNT" -eq 0 ]; then
  echo "❌ sitemap から docs/crew/ の URL を1件も抽出できませんでした" >&2
  exit 1
fi
cp "$WORK/sitemap_urls.txt" "$WORK/fetch_urls.txt"
for u in "${EXTRA_URLS[@]+"${EXTRA_URLS[@]}"}"; do
  printf '%s\n' "$u" >> "$WORK/fetch_urls.txt"
  echo "（--extra-url で取得対象に追加: $u）"
done

slug_of() {
  local s
  s=$(printf '%s' "$1" | sed -e 's#https://kiro.dev/docs/crew/##' -e 's#/$##' -e 's#/#__#g')
  [ -z "$s" ] && s="index"
  printf '%s' "$s"
}

echo "=== 3. 公式ページ（sitemap の ${SITEMAP_COUNT} 件）の HTML + .md companion ==="
while IFS= read -r url; do
  slug=$(slug_of "$url")
  http_get "$url" "$SNAP/docs/${slug}.html"
  http_get "${url%/}.md" "$SNAP/docs_md/${slug}.md"
done < "$WORK/fetch_urls.txt"

HTML_COUNT=$(find "$SNAP/docs" -name '*.html' | wc -l)
MD_COUNT=$(find "$SNAP/docs_md" -name '*.md' | wc -l)
echo "HTML: ${HTML_COUNT} 件 / .md: ${MD_COUNT} 件 / sitemap: ${SITEMAP_COUNT} 件"
if [ "$HTML_COUNT" -ne "$SITEMAP_COUNT" ] || [ "$MD_COUNT" -ne "$SITEMAP_COUNT" ]; then
  echo "❌ 取得した HTML・.md の件数が sitemap の件数と一致しません" >&2
  exit 1
fi

echo "=== 4. Releases / Tree / repo 情報 / releases/tags（GitHub API）==="
# Releases API: Link ヘッダに rel="next" がある間だけ次ページを取りにいく
url="${API}/releases?per_page=${PER_PAGE}"
page=0
while [ -n "$url" ]; do
  page=$((page + 1))
  http_get "$url" "$WORK/releases_page_${page}.json" -D "$WORK/releases_head_${page}.txt" \
    -H "Accept: application/vnd.github+json" "${AUTH_HEADER[@]+"${AUTH_HEADER[@]}"}"
  url=$(python3 - "$WORK/releases_head_${page}.txt" <<'PY'
import re, sys
link = ""
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    if line.lower().startswith("link:"):
        link = line.split(":", 1)[1]
m = re.search(r'<([^>]+)>\s*;\s*rel="next"', link)
print(m.group(1) if m else "")
PY
)
done
echo "Releases API: ${page} ページ取得（per_page=${PER_PAGE}）"
python3 - "$SNAP/releases/releases.json" "$WORK"/releases_page_*.json <<'PY'
import json, sys
out, pages = sys.argv[1], sys.argv[2:]
pages.sort(key=lambda p: int(p.rsplit("_", 1)[1].split(".")[0]))
merged = []
for p in pages:
    data = json.load(open(p, encoding="utf-8"))
    if not isinstance(data, list):
        sys.exit(f"❌ Releases API の応答が配列ではありません: {p}")
    merged.extend(data)
json.dump(merged, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"releases.json: {len(merged)} 件")
PY

http_get "${API}/git/trees/${REF}?recursive=1" "$SNAP/meta/tree.json" "${AUTH_HEADER[@]+"${AUTH_HEADER[@]}"}"
http_get "${API}" "$SNAP/meta/repo_info.json" "${AUTH_HEADER[@]+"${AUTH_HEADER[@]}"}"

# REF がタグなら tag object と ^{} の commit を記録し、releases/tags/<REF> を取得する
git ls-remote --tags "$GH_REPO_URL" "refs/tags/${REF}" "refs/tags/${REF}^{}" > "$WORK/ls_remote.txt"
IS_TAG=0
if [ -s "$WORK/ls_remote.txt" ]; then
  IS_TAG=1
  http_get "${API}/releases/tags/${REF}" "$WORK/release_tag.json" "${AUTH_HEADER[@]+"${AUTH_HEADER[@]}"}"
else
  echo "（REF $REF はタグではないため、tag_object_sha・release_published_at・prerelease は null にします）"
  : > "$WORK/release_tag.json"
fi
if [ -n "$BASE" ] && [ "$IS_TAG" -ne 1 ]; then
  echo "❌ --base は REF がタグのときだけ指定できます" >&2
  exit 1
fi

echo "=== 5. 経由版の列挙と取得 ==="
: > "$WORK/via_list.txt"
if [ -n "$BASE" ]; then
  python3 - "$SNAP/releases/releases.json" "$BASE" "$WORK/release_tag.json" > "$WORK/via_list.txt" <<'PY'
import json, sys
rels = json.load(open(sys.argv[1], encoding="utf-8"))
base = sys.argv[2]
target = json.load(open(sys.argv[3], encoding="utf-8"))
by_tag = {r["tag_name"]: r for r in rels}
if base not in by_tag:
    sys.exit(f"❌ --base の版 {base} が releases.json にありません")
lo, hi = by_tag[base]["published_at"], target["published_at"]
via = [r for r in rels if not r.get("prerelease") and lo < r["published_at"] < hi]
via.sort(key=lambda r: r["published_at"])
for r in via:
    print(f'{r["tag_name"]}\t{r["published_at"]}')
PY
  if [ ! -s "$WORK/via_list.txt" ]; then
    echo "経由版: なし（${BASE} と ${REF} の間に公開された安定版はありません）"
  fi
  while IFS=$'\t' read -r vref _published; do
    [ -z "$vref" ] && continue
    vdir="${VIA_ROOT%/}/${vref}"
    if [ -f "$vdir/repo/COMMIT_SHA" ]; then
      echo "経由版 ${vref}: 取得済み（${vdir}）。COMMIT_SHA を読みます"
    else
      echo "経由版 ${vref}: ${vdir} に取得します（--repo-only と同じ内容）"
      mark_new "$vdir"
      clone_repo "$vref" "$vdir"
    fi
    echo "  COMMIT_SHA: $(cat "$vdir/repo/COMMIT_SHA")"
  done < "$WORK/via_list.txt"
else
  echo "（--base 未指定のため経由版は列挙しません。PIN.json の base は null、via は空配列）"
fi

echo "=== 6. PIN.json（一次情報の固定値）==="
REFERENCE_DATE=$(TZ=Asia/Tokyo date +%F)
python3 - "$SNAP" "$REF" "$WORK/ls_remote.txt" "$WORK/release_tag.json" "$REFERENCE_DATE" \
  "$WORK/sitemap_urls.txt" "$BASE" "${VIA_ROOT:-}" "$WORK/via_list.txt" <<'PY'
import datetime, hashlib, json, os, re, sys
snap, ref, ls_remote, release_tag, reference_date, urls_file, base, via_root, via_list = sys.argv[1:10]

def slug_of(url):
    s = url.replace("https://kiro.dev/docs/crew/", "").rstrip("/").replace("/", "__")
    return s or "index"

def changelog_date(changelog_path, ref):
    ver = ref[1:] if ref.startswith("v") else ref
    if not os.path.isfile(changelog_path):
        return None
    m = re.search(r"(?m)^## \[" + re.escape(ver) + r"\] - (\d{4}-\d{2}-\d{2})", open(changelog_path, encoding="utf-8").read())
    return m.group(1) if m else None

commit_sha = open(os.path.join(snap, "repo", "COMMIT_SHA"), encoding="utf-8").read().strip()
tag_object_sha, peeled = None, None
for line in open(ls_remote, encoding="utf-8"):
    sha, name = line.split()
    if name.endswith("^{}"):
        peeled = sha
    else:
        tag_object_sha = sha
if tag_object_sha is not None:
    expected = peeled or tag_object_sha  # 軽量タグは ^{} 行が無く、タグ自体が commit を指す
    if expected != commit_sha:
        sys.exit(f"❌ clone の commit {commit_sha} が git ls-remote のタグ commit {expected} と一致しません")

rel = {}
if os.path.getsize(release_tag) > 0:
    rel = json.load(open(release_tag, encoding="utf-8"))

page_updated, md_sha = {}, {}
missing = []
for url in [u.strip() for u in open(urls_file, encoding="utf-8") if u.strip()]:
    slug = slug_of(url)
    html = open(os.path.join(snap, "docs", slug + ".html"), encoding="utf-8", errors="replace").read()
    m = re.search(r"Page updated:<!-- --> <!-- -->([^<]+)", html)
    raw = m.group(1).strip() if m else ""
    if not raw:
        missing.append(url)
        continue
    try:
        page_updated[url] = datetime.datetime.strptime(raw, "%B %d, %Y").date().isoformat()
    except ValueError:
        sys.exit(f"❌ Page updated の表示 {raw!r} を日付として解釈できません: {url}（抽出パターンの陳腐化を疑ってください）")
    md_sha[url] = hashlib.sha256(open(os.path.join(snap, "docs_md", slug + ".md"), "rb").read()).hexdigest()
if missing:
    sys.exit(f"❌ Page updated を抽出できないページが {len(missing)} 件あります（抽出パターンの陳腐化を疑ってください）: {missing}")

via = []
if base:
    rels = {r["tag_name"]: r for r in json.load(open(os.path.join(snap, "releases", "releases.json"), encoding="utf-8"))}
    for line in open(via_list, encoding="utf-8"):
        if not line.strip():
            continue
        vref, published = line.rstrip("\n").split("\t")
        vdir = os.path.join(via_root, vref)
        vdate = changelog_date(os.path.join(vdir, "repo", "CHANGELOG.md"), vref)
        if vdate is None:
            print(f"⚠️  経由版 {vref} のタグの CHANGELOG に自版の節がありません（changelog_date を null にします。未確認として扱ってください）")
        via.append({
            "ref": vref,
            "commit_sha": open(os.path.join(vdir, "repo", "COMMIT_SHA"), encoding="utf-8").read().strip(),
            "changelog_date": vdate,
            "release_published_at": rels[vref]["published_at"],
        })

target_date = changelog_date(os.path.join(snap, "repo", "CHANGELOG.md"), ref)
if target_date is None:
    print(f"⚠️  {ref} の CHANGELOG に自版の節がありません（changelog_date を null にします）")

pin = {
    "ref": ref,
    "tag_object_sha": tag_object_sha,
    "commit_sha": commit_sha,
    "commit_short": commit_sha[:7],
    "release_published_at": rel.get("published_at"),
    "prerelease": rel.get("prerelease"),
    "changelog_date": target_date,
    "reference_date": reference_date,
    "sitemap_crew_count": len(page_updated),
    "official_page_updated": page_updated,
    "official_md_sha256": md_sha,
    "base": base or None,
    "via": via,
}
json.dump(pin, open(os.path.join(snap, "PIN.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
summary = {k: v for k, v in pin.items() if k not in ("official_page_updated", "official_md_sha256")}
print(json.dumps(summary, ensure_ascii=False, indent=2))
print(f"official_page_updated: {len(page_updated)} 件 / official_md_sha256: {len(md_sha)} 件")
PY

echo ""
echo "=== 完了 ==="
echo "保存先: $SNAP"
echo "REF: $REF / COMMIT_SHA: $(cat "$SNAP/repo/COMMIT_SHA")"
echo "sitemap の docs/crew/ URL: ${SITEMAP_COUNT} 件"
echo "docs/ HTML: ${HTML_COUNT} 件"
echo "docs_md/ MD: ${MD_COUNT} 件"
echo "docs/配下ファイル数: $(find "$SNAP/repo/docs" -type f | wc -l) 件"
echo "※ src/ は取得していません。src/ 由来のSSoT（builtin App数など）は full clone で測定してください"

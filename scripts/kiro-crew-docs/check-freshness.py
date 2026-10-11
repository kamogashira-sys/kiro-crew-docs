#!/usr/bin/env python3
"""check-freshness.py - kiro-crew-docs 更新検知（★外部サイトに依存・4系統）

使用方法:
    ./scripts/kiro-crew-docs/check-freshness.py
    ./scripts/kiro-crew-docs/check-freshness.py --offline <snapshot-dir>
        # ネットワークを使わず、指定したスナップショットで検証する

4系統（Crew固有の設計。兄弟サイトはchangelog索引+sitemapの2系統だが、
Crewはリポジトリ側3系統+公式サイト1系統）:
    ① GitHub Releases（新しい安定版の検知）
    ② CHANGELOG.md のハッシュ変化
    ③ 公式sitemapのcrewページ数変化
    ④ GitHub Tree APIのdocs/ファイル数変化

fail-safe:
    ネットワーク不通・レート制限時はexit 0＋警告（CIを赤くしない）。
    実際に更新を検知した場合はexit 1（「文書のバグ」ではなく「更新作業が必要」の合図）。

オプション（既定はオフで、上の挙動を変えない）:
    --strict        ①〜④のうち1系統でも取得に失敗したら exit 3（未検証）。クラウド入口から呼ぶ
    --release-only  ④（main の docs/ 件数）の変化を errors ではなく notes に入れる（版が出ていなくても動くため）

Releases のページング（オプションに関係なく適用）:
    1ページの件数は環境変数 KCD_RELEASES_PER_PAGE（既定 100）。応答の Link ヘッダに rel="next" が
    無くなるまで取得して連結し、取得したページ数を notes に出す。
参考表示（⑤。終了コードに影響しない）:
    kiro.dev の changelog/crew/0-N/（既知の最新安定版の系列と次の系列）の HTTP ステータス
"""
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

RELEASES_URL = "https://api.github.com/repos/kirodotdev/KiroCrew/releases?per_page=100"
CREW_CHANGELOG_SERIES_URL = "https://kiro.dev/changelog/crew/{series}/"
CHANGELOG_URL = "https://raw.githubusercontent.com/kirodotdev/KiroCrew/main/CHANGELOG.md"
SITEMAP_URL = "https://kiro.dev/sitemap.xml"
TREE_URL = "https://api.github.com/repos/kirodotdev/KiroCrew/git/trees/main?recursive=1"

KNOWN_LATEST_STABLE = "v0.7.2"
KNOWN_STABLE_COUNT = 13
KNOWN_CREW_PAGES = 49
KNOWN_DOCS_FILES = 331
# ⚠️ ④系統は `trees/main`（＝main HEAD）を測る更新検知であり、SSoT S2（v0.7.2タグの281件）とは
#    別の値である。331 は 2026-10-04 の main 実測値。main は日次で動くため、この値の変化は
#    「文書のバグ」ではなく「上流が動いた」の合図。offline モードではタグ版tree.json（281）を
#    読むため差分が報告されるが、これは想定どおり。

UA = "Mozilla/5.0"


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_with_headers(url):
    """本文と応答ヘッダを返す（Link ヘッダによるページングのため）。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace"), r.headers


def releases_first_url():
    per_page = os.environ.get("KCD_RELEASES_PER_PAGE") or "100"
    return RELEASES_URL.replace("per_page=100", f"per_page={per_page}")


def fetch_all_releases(notes):
    """Link ヘッダに rel="next" が無くなるまでページを取得して連結する。"""
    url = releases_first_url()
    data, pages = [], 0
    while url:
        body, headers = fetch_with_headers(url)
        pages += 1
        data.extend(json.loads(body))
        m = re.search(r'<([^>]+)>\s*;\s*rel="next"', headers.get("Link", "") or "")
        url = m.group(1) if m else None
    notes.append(f"① Releases: {pages} ページ取得（{url_per_page(releases_first_url())}）")
    return data


def url_per_page(url):
    m = re.search(r"per_page=(\d+)", url)
    return f"per_page={m.group(1)}" if m else "per_page=?"


def check_releases(notes, errors, offline_dir):
    try:
        if offline_dir:
            path = os.path.join(offline_dir, "releases", "releases.json")
            if not os.path.isfile(path):
                notes.append("① Releases: オフラインスナップショットに releases.json がありません")
                return
            data = json.load(open(path, encoding="utf-8"))
        else:
            data = fetch_all_releases(notes)
        stable = [r for r in data if not r.get("prerelease")]
        stable.sort(key=lambda r: r["published_at"], reverse=True)
        latest = stable[0]["tag_name"] if stable else None
        notes.append(f"① Releases: 最新安定版 {latest} / 安定版数 {len(stable)}")
        if latest and latest != KNOWN_LATEST_STABLE:
            errors.append(f"① 新しい安定版を検知しました: {latest}（既知: {KNOWN_LATEST_STABLE}）")
        if len(stable) != KNOWN_STABLE_COUNT:
            errors.append(f"① 安定版リリース数が {len(stable)} 件に変化しました（既知: {KNOWN_STABLE_COUNT}）")
    except Exception as e:
        notes.append(f"① Releases: 取得失敗（{e}）。ネットワーク不通・レート制限の可能性")


def check_changelog_hash(notes, errors, offline_dir):
    try:
        if offline_dir:
            path = os.path.join(offline_dir, "repo", "CHANGELOG.md")
            if not os.path.isfile(path):
                notes.append("② CHANGELOG: オフラインスナップショットにCHANGELOG.mdがありません")
                return
            txt = open(path, encoding="utf-8").read()
        else:
            txt = fetch(CHANGELOG_URL)
        h = hashlib.sha256(txt.encode()).hexdigest()
        notes.append(f"② CHANGELOG.md: sha256={h[:16]}...")
        versions = re.findall(r"(?m)^## \[(\d+\.\d+\.\d+)\]", txt)
        notes.append(f"② CHANGELOG.md: 版節 {versions}")
    except Exception as e:
        notes.append(f"② CHANGELOG: 取得失敗（{e}）")


def check_sitemap(notes, errors, offline_dir):
    try:
        if offline_dir:
            path = os.path.join(offline_dir, "meta", "sitemap.xml")
            if not os.path.isfile(path):
                notes.append("③ sitemap: オフラインスナップショットにsitemap.xmlがありません")
                return
            txt = open(path, encoding="utf-8").read()
        else:
            txt = fetch(SITEMAP_URL)
        urls = re.findall(r"<loc>(https://kiro\.dev/docs/crew/[^<]*)</loc>", txt)
        notes.append(f"③ sitemap: crewページ {len(urls)} 件")
        if len(urls) != KNOWN_CREW_PAGES:
            errors.append(f"③ 公式crewページ数が {len(urls)} 件に変化しました（既知: {KNOWN_CREW_PAGES}）")
    except Exception as e:
        notes.append(f"③ sitemap: 取得失敗（{e}）")


def check_tree(notes, errors, offline_dir, release_only=False):
    try:
        if offline_dir:
            path = os.path.join(offline_dir, "meta", "tree.json")
            if not os.path.isfile(path):
                notes.append("④ Tree API: オフラインスナップショットにtree.jsonがありません")
                return
            data = json.load(open(path, encoding="utf-8"))
        else:
            data = json.loads(fetch(TREE_URL))
        if data.get("truncated"):
            notes.append("④ Tree API: truncated=true（全量取得できていない可能性）")
        docs_files = [t for t in data.get("tree", []) if t["path"].startswith("docs/") and t["type"] == "blob"]
        notes.append(f"④ Tree API: docs/配下 {len(docs_files)} ファイル")
        if len(docs_files) != KNOWN_DOCS_FILES:
            msg = f"④ docs/配下のファイル数が {len(docs_files)} 件に変化しました（既知: {KNOWN_DOCS_FILES}）"
            if release_only:
                notes.append(msg + "（--release-only のため更新検知に数えない）")
            else:
                errors.append(msg)
    except Exception as e:
        notes.append(f"④ Tree API: 取得失敗（{e}）")


def check_crew_changelog_series(notes):
    """⑤ kiro.dev changelog/crew/0-N/ の HTTP ステータスを参考表示する（終了コードに影響しない）。"""
    m = re.match(r"v(\d+)\.(\d+)\.", KNOWN_LATEST_STABLE)
    if not m:
        return
    major, minor = int(m.group(1)), int(m.group(2))
    for series in (f"{major}-{minor}", f"{major}-{minor + 1}"):
        url = CREW_CHANGELOG_SERIES_URL.format(series=series)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception as e:
            notes.append(f"⑤ kiro.dev {url}: 到達不可（{e}）。参考表示のみ")
            continue
        notes.append(f"⑤ kiro.dev {url}: HTTP {status}（参考表示。版の正本にはしない）")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", help="オフラインスナップショットのディレクトリ")
    ap.add_argument("--strict", action="store_true",
                    help="1系統でも取得に失敗したら exit 3（未検証）にする")
    ap.add_argument("--release-only", action="store_true",
                    help="④ main の docs/ 件数の変化を更新検知に数えない（notes に表示する）")
    args = ap.parse_args()
    os.chdir(repo_root())

    print("=== kiro-crew-docs 更新検知（4系統） ===")
    print("")

    notes, errors = [], []
    fetch_failed = 0

    print("🔍 ① GitHub Releases を確認中...")
    check_releases(notes, errors, args.offline)

    print("🔍 ② CHANGELOG.md のハッシュを確認中...")
    check_changelog_hash(notes, errors, args.offline)

    print("🔍 ③ 公式sitemapのcrewページ数を確認中...")
    check_sitemap(notes, errors, args.offline)

    print("🔍 ④ GitHub Tree APIのdocs/ファイル数を確認中...")
    check_tree(notes, errors, args.offline, args.release_only)

    if not args.offline:
        print("🔍 ⑤ kiro.dev changelog/crew の系列ページを確認中（参考表示）...")
        check_crew_changelog_series(notes)

    print("")
    print("=== 結果 ===")
    for n in notes:
        print(f"   - {n}")
        if "取得失敗" in n:
            fetch_failed += 1
    print("")

    if args.strict and fetch_failed >= 1:
        print(f"⚠️  {fetch_failed} 系統で取得に失敗しました（--strict）")
        print("   → これは「更新なしを確認した」ではありません（**未検証**です）")
        for e in errors:
            print(f"   - （参考）{e}")
        return 3

    if fetch_failed >= 4 and not args.offline:
        print("⚠️  すべての系統で取得に失敗しました。ネットワーク不通の可能性があります")
        print("   → これは「更新なしを確認した」ではありません（**未検証**です）")
        return 0

    if errors:
        print(f"🔔 更新を検知しました（{len(errors)} 件）:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("🔔 これは「文書のバグ」ではなく「更新作業が必要」の合図です")
        return 1

    print("✅ 既知の状態から変化はありません")
    return 0


if __name__ == "__main__":
    sys.exit(main())

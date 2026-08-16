#!/usr/bin/env python3
"""check-links.py - kiro-crew-docs 内部リンク整合チェック

使用方法:
    ./scripts/kiro-crew-docs/check-links.py
    ./scripts/kiro-crew-docs/check-links.py --check-anchors   # アンカー(見出し)実在も検査(日本語含む)
    ./scripts/kiro-crew-docs/check-links.py --check-anchors --paths <file...>

機能:
    - kiro-crew-docs/**/*.md ＋ ルート README.md ＋ .github/*.md の
      相対 Markdown リンクを抽出し、リンク先ファイルの実在を検証
    - 同一ファイル内アンカー（`#...`）と他ファイルのアンカーの実在を検証
    - 外部リンクの書式を検証（Crew 固有: kiro.dev と GitHub の2種類の分岐）:
        - kiro.dev の docs URL は末尾スラッシュ必須（無しは301）
        - GitHub の blob URL（.../blob/main/...）は末尾スラッシュを**付けない**
          （kiro.dev とは逆の規則。両方を同じ正規表現で検査すると誤検知する）
        - 姉妹製品（IDE / CLI / Web）のページへのリンクは「別製品」明示を促す（検出のみ）
    - 上記以外の http(s)/mailto/tel は到達性を検証しない（check-urls.sh の担当）

除外（スコープ外・ローカル管理のため）:
    - kiro-crew-docs/06_embedded-docs/**
    - kiro-crew-docs/05_meta/**
    - kiro-crew-docs/work_plans/**
    - work_records/**
    - *_plan.md / *_review_report.md / *_investigation.md / *_worklog.md
"""
import glob
import os
import re
import sys

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
BARE_URL_RE = re.compile(r'<?(https://(?:kiro\.dev|github\.com|raw\.githubusercontent\.com)/[^\s>)"\']*)>?')
HEADING_RE = re.compile(r'^#{1,6}\s+(.*?)\s*$')
HTML_ANCHOR_RE = re.compile(r'<a\s+(?:id|name)=["\']([^"\']+)["\']')

EXCLUDE_SUBSTR = (
    "kiro-crew-docs/06_embedded-docs/",
    "kiro-crew-docs/05_meta",
    "kiro-crew-docs/work_plans",
    "work_records/",
    "_plan.md",
    "_review_report.md",
    "_investigation.md",
    "_worklog.md",
)
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:")

GITHUB_RELATIVE_RE = re.compile(
    r"^(?:\.\./)+(?:issues|pulls|discussions|wiki)(?:/\d+)?$"
)

# プレースホルダを含む URL は書式検証の対象外（テンプレート等の雛形）
PLACEHOLDER_RE = re.compile(r"[<>{}]|\((?:パス|module|スラッグ|path)\)|（")

# kiro.dev の docs URL は末尾スラッシュ必須（無しは301）
KIRO_DEV_SLASH_REQUIRED_RE = re.compile(r'^https://kiro\.dev/(?:docs|crew|blog)(?:/|$)')

# GitHub の blob URL は末尾スラッシュを付けない（付けると404になる）
GITHUB_BLOB_TRAILING_SLASH_RE = re.compile(r'^https://github\.com/[^/]+/[^/]+/blob/[^\s]+/$')

# 姉妹製品（IDE/CLI/Web）ドキュメントへのリンク検出。
# kiro.dev/docs/{ide,cli,web}/ 形式に加え、実際に使われている姉妹サイトの
# GitHubリポジトリ形式（github.com/kamogashira-sys/{kiro-web-docs,kiro-ide-docs,q-cli-docs}）
# も検出する（V-06: 旧パターンはkiro.dev形式のみで、実際のリンクを検出できていなかった）。
SIBLING_DOCS_RE = re.compile(
    r'^https://kiro\.dev/docs/(?:ide/|cli/|web/)'
    r'|^https://github\.com/kamogashira-sys/(?:kiro-web-docs|kiro-ide-docs|q-cli-docs)\b'
)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_excluded(path):
    norm = path.replace(os.sep, "/")
    return any(sub in norm for sub in EXCLUDE_SUBSTR)


def slugify(heading):
    s = heading.strip().lower()
    s = s.replace("`", "")
    s = re.sub(r"[^\w\s\-ぁ-んァ-ヶ一-龠ー]", "", s)
    return re.sub(r"\s", "-", s)


def strip_code(txt):
    out = []
    in_fence = False
    for line in txt.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(re.sub(r"`[^`\n]*`", "", line))
    return "".join(out)


def collect_headings(filepath):
    slugs = set()
    in_fence = False
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for m in HTML_ANCHOR_RE.finditer(line):
                    slugs.add(m.group(1).lower())
                m = HEADING_RE.match(line)
                if m:
                    slugs.add(slugify(m.group(1)))
    except OSError:
        pass
    return slugs


def check_url(url):
    """外部 URL の書式を検証し、問題があれば理由を返す（なければ None）。"""
    if PLACEHOLDER_RE.search(url):
        return None
    if os.path.splitext(url)[1] and not url.endswith((".md", ".json", ".xml")):
        return None
    if KIRO_DEV_SLASH_REQUIRED_RE.match(url) and not url.endswith("/") and not url.endswith((".md", ".xml")):
        return "kiro.dev の docs/crew/blog URL は末尾スラッシュが必須（スラッシュなしは301）"
    if GITHUB_BLOB_TRAILING_SLASH_RE.match(url):
        return "GitHub の blob URL は末尾スラッシュを付けない（kiro.dev とは逆の規則）"
    return None


def main():
    args = sys.argv[1:]
    check_anchors = "--check-anchors" in args
    paths_mode = "--paths" in args
    target_paths = []
    if paths_mode:
        target_paths = args[args.index("--paths") + 1:]
        if not target_paths:
            print("❌ --paths にファイルを 1 つ以上指定してください")
            sys.exit(2)
    os.chdir(repo_root())

    if paths_mode:
        missing = [p for p in target_paths if not os.path.isfile(p)]
        if missing:
            for p in missing:
                print(f"❌ --paths 指定ファイルが存在しません: {p}")
            sys.exit(2)
        files = sorted(target_paths)
    else:
        files = (sorted(glob.glob("kiro-crew-docs/**/*.md", recursive=True))
                 + ["README.md"]
                 + sorted(glob.glob(".github/*.md")))

    checked = 0
    url_checked = 0
    broken = []
    anchor_broken = []
    bad_urls = []
    sibling_links = []
    heading_cache = {}

    for f in files:
        if not paths_mode and (is_excluded(f) or f.endswith(".bak")):
            continue
        base = os.path.dirname(f)
        try:
            txt = open(f, encoding="utf-8").read()
        except OSError:
            continue
        txt = strip_code(txt)

        seen_urls = set()
        for m in BARE_URL_RE.finditer(txt):
            url = m.group(1).rstrip(".,)")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            url_checked += 1
            reason = check_url(url)
            if reason:
                bad_urls.append((f, url, reason))
            if SIBLING_DOCS_RE.match(url) and not PLACEHOLDER_RE.search(url):
                sibling_links.append((f, url))

        for m in LINK_RE.finditer(txt):
            target = m.group(2).strip()
            if target.startswith("#"):
                if check_anchors:
                    anchor = target[1:]
                    checked += 1
                    if f not in heading_cache:
                        heading_cache[f] = collect_headings(f)
                    if anchor.lower() not in heading_cache[f]:
                        anchor_broken.append((f, target, anchor))
                continue
            if target.startswith(SKIP_PREFIX):
                continue
            if GITHUB_RELATIVE_RE.match(target.rstrip("/")):
                continue
            path, _, anchor = target.partition("#")
            if not path:
                continue
            resolved = os.path.normpath(os.path.join(base, path))
            if not paths_mode and is_excluded(resolved):
                continue
            checked += 1
            if not os.path.exists(resolved):
                broken.append((f, target, resolved))
                continue
            if check_anchors and anchor and resolved.endswith(".md"):
                if resolved not in heading_cache:
                    heading_cache[resolved] = collect_headings(resolved)
                if anchor.lower() not in heading_cache[resolved]:
                    anchor_broken.append((f, target, anchor))

    print("=== kiro-crew-docs 内部リンク整合チェック ===")
    print("")
    print(f"チェックした相対リンク数: {checked}")
    print(f"リンク切れ: {len(broken)} 件")
    for f, t, r in broken:
        print(f"  ❌ {f}: '{t}' -> {r}")

    print("")
    print(f"外部URLの書式チェック: {url_checked} 件中 {len(bad_urls)} 件が不正")
    for f, u, reason in bad_urls:
        print(f"  ❌ {f}: {u}")
        print(f"      → {reason}")

    if check_anchors:
        print("")
        print(f"アンカー検査: 切れ {len(anchor_broken)} 件（日本語アンカーも検査対象）")
        for f, t, a in anchor_broken:
            print(f"  ⚠️  {f}: '{t}'（見出し '#{a}' が見つからない）")

    print("")
    print(f"姉妹製品（IDE / CLI / Web）ドキュメントへのリンク: {len(sibling_links)} 件")
    if sibling_links:
        print("   → 「別製品」であることを本文で明示しているか確認してください")
        for f, u in sibling_links:
            print(f"      {f}: {u}")

    print("")
    total_errors = len(broken) + len(bad_urls) + (len(anchor_broken) if check_anchors else 0)
    if total_errors > 0:
        print("❌ リンクチェックに失敗しました")
        sys.exit(1)
    print("✅ すべての内部リンクと外部URLの書式が有効です")
    sys.exit(0)


if __name__ == "__main__":
    main()

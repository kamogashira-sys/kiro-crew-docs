#!/usr/bin/env python3
"""check-audit-groups.py - 監査ページ群（.github/UPDATE_GUIDE.md §16）の網羅性を検証する

使用方法:
    ./scripts/kiro-crew-docs/check-audit-groups.py
    ./scripts/kiro-crew-docs/check-audit-groups.py --files-from <file> --guide <file>
        # テスト用: 公開ページの一覧（1行1パス）と手順書を差し替える

目的:
    版更新の監査（群 A〜G の並列）が、どの群にも入らない公開ページを見落とさないようにする。
    公開ページを新設したのに群へ割り当てていない・同じページを2つの群に書いた・
    存在しないページを書いた、のいずれも失敗にする。

検証内容:
    手順書の「監査ページ群」を見出しに含む `## ` 節の最初の表から、2列目の `*.md`
    （`kiro-crew-docs/` からの相対パス）を行ごとに抽出し、公開ページの一覧
    （既定 `git ls-files 'kiro-crew-docs/0[0-4]_*'`）と突き合わせる。
    1. 割当漏れ: 一覧にあり表に無い
    2. 重複: 表の2行以上（または同じ行に2回）に書かれている
    3. 存在しない: 表にあり一覧に無い
    1件でもあれば exit 1。要約行「監査群 割当 N/N・重複 N」を `KCD-SUMMARY:` 付きで出す。
"""
import argparse
import os
import re
import subprocess
import sys

DOC_ROOT = "kiro-crew-docs"
GUIDE = ".github/UPDATE_GUIDE.md"
SECTION_RE = re.compile(r"^##\s+.*監査ページ群")
FILE_RE = re.compile(r"`([^`]+\.md)`")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def public_pages(files_from):
    if files_from:
        lines = open(files_from, encoding="utf-8").read().splitlines()
    else:
        out = subprocess.run(["git", "ls-files", f"{DOC_ROOT}/0[0-4]_*"],
                             capture_output=True, text=True, check=True).stdout
        lines = out.splitlines()
    return sorted({ln.strip() for ln in lines if ln.strip()})


def parse_groups(guide):
    """節の最初の表を読み、(群のラベル, [ファイル]) の一覧を返す。表が見つからなければ None。"""
    lines = open(guide, encoding="utf-8").read().splitlines()
    start = next((i for i, ln in enumerate(lines) if SECTION_RE.match(ln)), None)
    if start is None:
        return None
    rows, in_table = [], False
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        if ln.startswith("|"):
            in_table = True
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 2 or set(cells[0]) <= set("-: ") or cells[0] == "群":
                continue  # 区切り行・見出し行
            files = [f"{DOC_ROOT}/{f}" for f in FILE_RE.findall(cells[1])]
            rows.append((cells[0], files))
        elif in_table:
            break
    return rows if rows else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--files-from", help="公開ページの一覧（1行1パス。既定は git ls-files）")
    ap.add_argument("--guide", help=f"手順書（既定 {GUIDE}）")
    args = ap.parse_args()
    files_from = os.path.abspath(args.files_from) if args.files_from else None
    guide = os.path.abspath(args.guide) if args.guide else None
    os.chdir(repo_root())
    guide = guide or GUIDE

    print("=== kiro-crew-docs 監査ページ群の網羅性チェック ===")
    print("")
    if not os.path.isfile(guide):
        print(f"❌ {guide} がありません。検査を行いませんでした")
        return 1
    rows = parse_groups(guide)
    if rows is None:
        print(f"❌ {guide} に「監査ページ群」の節の表が見つかりません。検査を行いませんでした")
        return 1
    pages = public_pages(files_from)
    if not pages:
        print("❌ 公開ページの一覧が0件です。検査を行いませんでした")
        return 1

    where = {}
    for label, files in rows:
        for f in files:
            where.setdefault(f, []).append(label)
    page_set = set(pages)
    unassigned = [p for p in pages if p not in where]
    duplicated = {f: labels for f, labels in where.items() if len(labels) > 1}
    missing = sorted(f for f in where if f not in page_set)
    assigned = len([p for p in pages if p in where])

    print(f"手順書: {guide}（群 {len(rows)} 行）")
    print(f"公開ページ: {len(pages)} 件（{'--files-from ' + args.files_from if files_from else 'git ls-files'}）")
    print("")
    errors = []
    if unassigned:
        errors.append(f"割当漏れ {len(unassigned)} 件（どの群にもありません）: {unassigned}")
    for f, labels in sorted(duplicated.items()):
        errors.append(f"重複: {f} が {len(labels)} 回書かれています（{labels}）")
    if missing:
        errors.append(f"存在しないファイル {len(missing)} 件（公開ページの一覧にありません）: {missing}")

    print(f"KCD-SUMMARY: 監査群 割当 {assigned}/{len(pages)}・重複 {len(duplicated)}")
    print("")
    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        return 1
    print("✅ すべての公開ページがちょうど1つの群に割り当てられています")
    return 0


if __name__ == "__main__":
    sys.exit(main())

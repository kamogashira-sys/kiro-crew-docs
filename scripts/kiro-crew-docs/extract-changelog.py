#!/usr/bin/env python3
"""extract-changelog.py - CHANGELOG.md から版節・日付・項目を抽出する（保守用）

使用方法:
    ./scripts/kiro-crew-docs/extract-changelog.py [--path <CHANGELOG.md>] [--text]

デフォルトのpath: kiro-crew-docs/06_embedded-docs/<最新日付>/repo/CHANGELOG.md

出力:
    版節ごとの日付・項目一覧（JSON、--textで人が読む形式）
"""
import argparse
import glob
import json
import os
import re
import sys

VERSION_HEAD_RE = re.compile(r"(?m)^## \[(\d+\.\d+\.\d+|Unreleased)\]\s*(?:—|-)?\s*(\d{4}-\d{2}-\d{2})?")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def find_default_path():
    candidates = sorted(glob.glob("kiro-crew-docs/06_embedded-docs/*/repo/CHANGELOG.md"))
    return candidates[-1] if candidates else None


def extract(text):
    sections = []
    matches = list(VERSION_HEAD_RE.finditer(text))
    for i, m in enumerate(matches):
        version, date = m.group(1), m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        items = re.findall(r"(?m)^-\s+(.+)$", body)
        sections.append({"version": version, "date": date, "item_count": len(items), "items": items[:5]})
    return sections


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--path", help="CHANGELOG.md のパス")
    ap.add_argument("--text", action="store_true", help="人が読む形式で出力")
    args = ap.parse_args()
    os.chdir(repo_root())

    path = args.path or find_default_path()
    if not path or not os.path.isfile(path):
        print("❌ CHANGELOG.md が見つかりません。--path で指定するか "
              "fetch-snapshot.sh を先に実行してください", file=sys.stderr)
        return 2

    text = open(path, encoding="utf-8").read()
    sections = extract(text)

    if args.text:
        print(f"=== {path} ===")
        for s in sections:
            print(f"\n[{s['version']}] {s['date'] or '(日付なし)'} — 項目数: {s['item_count']}")
            for it in s["items"]:
                print(f"  - {it[:80]}")
    else:
        print(json.dumps(sections, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

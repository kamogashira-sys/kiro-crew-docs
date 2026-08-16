#!/usr/bin/env python3
"""extract-doc-index.py - Tree API の JSON から docs/ のカテゴリ別内訳を生成する（保守用）

使用方法:
    ./scripts/kiro-crew-docs/extract-doc-index.py [--path <tree.json>] [--text]

デフォルトのpath: kiro-crew-docs/06_embedded-docs/<最新日付>/meta/tree.json

出力:
    docs/配下のカテゴリ別ファイル数（計画書 §2.6 の表を機械生成する）
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def find_default_path():
    candidates = sorted(glob.glob("kiro-crew-docs/06_embedded-docs/*/meta/tree.json"))
    return candidates[-1] if candidates else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--path", help="tree.json のパス")
    ap.add_argument("--text", action="store_true", help="人が読む形式で出力")
    args = ap.parse_args()
    os.chdir(repo_root())

    path = args.path or find_default_path()
    if not path or not os.path.isfile(path):
        print("❌ tree.json が見つかりません。--path で指定するか "
              "fetch-snapshot.sh を先に実行してください", file=sys.stderr)
        return 2

    data = json.load(open(path, encoding="utf-8"))
    if data.get("truncated"):
        print("⚠️  truncated=true（全量取得できていません。結果は不完全です）", file=sys.stderr)

    docs_files = [t for t in data.get("tree", []) if t["path"].startswith("docs/") and t["type"] == "blob"]

    category = Counter()
    ext = Counter()
    for f in docs_files:
        parts = f["path"].split("/")
        # docs/<category>/... の形。docs/直下ファイルは "(root)"
        cat = parts[1] if len(parts) > 2 else "(root)"
        category[cat] += 1
        _, e = os.path.splitext(f["path"])
        ext[e or "(no ext)"] += 1

    result = {
        "total": len(docs_files),
        "by_category": dict(sorted(category.items(), key=lambda x: -x[1])),
        "by_extension": dict(sorted(ext.items(), key=lambda x: -x[1])),
    }

    if args.text:
        print(f"docs/配下 合計: {result['total']} ファイル")
        print("\nカテゴリ別:")
        for k, v in result["by_category"].items():
            print(f"  {k:30} {v:4}")
        print("\n拡張子別:")
        for k, v in result["by_extension"].items():
            print(f"  {k:10} {v:4}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

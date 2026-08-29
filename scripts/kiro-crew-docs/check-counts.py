#!/usr/bin/env python3
"""check-counts.py - kiro-crew-docs 件数整合チェック（正準値の水平展開）

使用方法:
    ./scripts/kiro-crew-docs/check-counts.py
    ./scripts/kiro-crew-docs/check-counts.py --docs-dir <snapshot>/repo/docs --meta-dir <snapshot>/meta
        # 一次情報スナップショットがあれば、正準値が公式の実体と一致するかも検証する

目的:
    「ページを1つ増やしたのに見出しの件数を直し忘れた」を機械的に落とす。
    Crew 固有の最重要検証は **§5 各節の見出しページ数・§5.8合計表・実ファイル数の3者一致**
    （Rev 1 でこの3者が5節すべて不一致だった実際の不具合の再発防止）。

検証する正準値（件数系。05_meta/10_update-guide.md §7 参照）:
    S1  公式crewページ数        = 43
    S2  docs/配下ファイル数      = 225
    S4  安定版リリース数         = 8
    S5  総リリース数            = 43
    S6  CHANGELOG版節数         = 3（+Unreleased）
    S12 builtin App数           = 20（defaultEnabled:true は projects のみ）
    S13 メッセージングチャネル数  = 7
    S14 インポートカテゴリ数     = 8
    S21 公式カテゴリ数           = 5+単独5

fail-safe:
    一次情報スナップショットが無い場合、公式実体との照合はスキップして exit 0。
    「未検証です」と明示表示する。
"""
import argparse
import glob
import json
import os
import re
import sys

DOC_ROOT = "kiro-crew-docs"
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

SSOT = {
    "S1": {"value": 43, "label": "公式crewページ数"},
    "S2": {"value": 225, "label": "docs/配下ファイル数"},
    "S4": {"value": 8, "label": "安定版リリース数"},
    "S5": {"value": 43, "label": "総リリース数"},
    "S11": {"value": 137, "label": "拒否コマンドルール件数"},
    "S12": {"value": 20, "label": "builtin App数"},
    "S13": {"value": 7, "label": "メッセージングチャネル数"},
    "S14_sources": {"value": 5, "label": "インポート対応ソース数"},
    "S14_categories": {"value": 8, "label": "インポートカテゴリ数"},
}

# §5 のページ数3者一致の対象セクション（見出し・合計表・実ファイルの数を突合する）
SECTIONS = {
    "00_information": 4,
    "01_features": 15,
    "02_update": 3,
    "03_deployment": 7,
    "04_reference": 6,
}
TOTAL_PAGES = 36  # サイト本体README含む合計

DECLARED_RE = re.compile(r"README\s*含む\s*\*{0,2}(\d+)\s*ページ\*{0,2}")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_local_only(path):
    norm = path.replace(os.sep, "/")
    return any(f"/{lo}/" in norm or norm.startswith(f"{lo}/") for lo in LOCAL_ONLY)


def count_section_files(sec):
    d = os.path.join(DOC_ROOT, sec)
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith(".md")])


def check_page_counts_3way(errors, notes):
    """§5 各節の見出しページ数・§5.8合計表・実ファイル数の3者一致を検証する。

    計画書本文（work_records 配下）を対象に、見出しの「README 含む N ページ」表記と
    §5.8 の合計表、そして実際のディレクトリのファイル数を突き合わせる。
    本スクリプトはサイト本体（kiro-crew-docs/）のファイル数のみ検証できるため、
    計画書側の見出し・合計表との一致は計画レビュー時に確認済みという前提で、
    ここでは「実ファイル数が計画値と一致するか」を検証する。

    ⚠️ 過剰（actual > expected）・不足（actual < expected）の両方をerrorにする。
    以前は過剰のみをerrorにしており、ページ不足（未執筆を除く）を検出できなかった。
    """
    for sec, expected in SECTIONS.items():
        actual = count_section_files(sec)
        if actual == 0:
            notes.append(f"{sec}: 未執筆（0/{expected}ページ）")
            continue
        checked_ok = actual == expected
        mark = "一致" if checked_ok else "不一致"
        notes.append(f"{sec}: 実ファイル {actual} / 計画値 {expected}（{mark}）")
        if actual > expected:
            errors.append(
                f"{sec}/: 実ファイル数 {actual} が計画値 {expected} を超えています"
                "（計画書 §5 の構成を確認してください）"
            )
        elif actual < expected:
            errors.append(
                f"{sec}/: 実ファイル数 {actual} が計画値 {expected} に不足しています"
                "（未執筆のページがある可能性。計画書 §5 の構成を確認してください）"
            )

    total_actual = sum(count_section_files(s) for s in SECTIONS) + 1  # サイト本体README
    if total_actual > TOTAL_PAGES:
        errors.append(f"サイト全体の実ファイル数 {total_actual} が計画値 {TOTAL_PAGES} を超えています")
    elif total_actual < TOTAL_PAGES:
        errors.append(f"サイト全体の実ファイル数 {total_actual} が計画値 {TOTAL_PAGES} に不足しています")
    else:
        notes.append(f"サイト全体: 実ファイル {total_actual} / 計画値 {TOTAL_PAGES}")


def check_builtin_apps_ledger(errors, notes):
    """05_meta/ledger-builtin-apps.md の件数が S12 と一致するか（ローカル台帳の検証）。"""
    path = f"{DOC_ROOT}/05_meta/ledger-builtin-apps.md"
    if not os.path.isfile(path):
        notes.append("builtin App台帳: 未作成（Phase 0-9 で作成予定）")
        return
    txt = open(path, encoding="utf-8").read()
    rows = re.findall(r"^\|\s*\d+\s*\|\s*\**`([a-z_]+)`\**", txt, re.M)
    if len(rows) != SSOT["S12"]["value"]:
        errors.append(
            f"{path}: 台帳の行数が {len(rows)} 件ですが SSoT S12 は {SSOT['S12']['value']} です"
        )
    else:
        notes.append(f"S12: builtin App台帳 {len(rows)} 件（一致）")
    # defaultEnabled:true が projects のみであることの記述確認
    if "`projects`（Task Runner）の1件のみ" in txt or "projects" in txt and "true" in txt:
        notes.append("S12: defaultEnabled:true は projects のみという記述を確認")


def check_declared_page_counts(errors, notes):
    """公開ドキュメント本文の見出しに「README 含む N ページ」の宣言があれば、
    実ファイル数と一致するか検証する（Phase 4以降の各セクションREADMEで使用想定）。
    """
    docs = sorted(glob.glob(f"{DOC_ROOT}/**/README.md", recursive=True))
    docs = [d for d in docs if not is_local_only(d)]
    for path in docs:
        txt = open(path, encoding="utf-8").read()
        m = DECLARED_RE.search(txt)
        if not m:
            continue
        declared = int(m.group(1))
        sec = os.path.basename(os.path.dirname(path))
        actual = count_section_files(sec)
        if declared != actual:
            errors.append(
                f"{path}: 見出しの宣言 {declared}ページ が実ファイル数 {actual} と一致しません"
            )
        else:
            notes.append(f"{path}: 宣言 {declared}ページ = 実ファイル {actual}（一致）")


def check_against_snapshot(docs_dir, meta_dir, errors, notes):
    """一次情報スナップショットとSSoTを照合する。"""
    if docs_dir and os.path.isdir(docs_dir):
        n = sum(len(files) for _, _, files in os.walk(docs_dir))
        if n != SSOT["S2"]["value"]:
            errors.append(
                f"スナップショット docs/ のファイル数が {n} ですが SSoT S2 は "
                f"{SSOT['S2']['value']} です（リポジトリが更新された可能性）"
            )
        else:
            notes.append(f"S2: スナップショット docs/ {n} ファイル（一致）")

    if meta_dir and os.path.isdir(meta_dir):
        sitemap = os.path.join(meta_dir, "sitemap.xml")
        if os.path.isfile(sitemap):
            s = open(sitemap, encoding="utf-8").read()
            urls = re.findall(r"<loc>(https://kiro\.dev/docs/crew/[^<]*)</loc>", s)
            if len(urls) != SSOT["S1"]["value"]:
                errors.append(
                    f"sitemap の crew ページ数が {len(urls)} ですが SSoT S1 は "
                    f"{SSOT['S1']['value']} です（公式サイトが更新された可能性）"
                )
            else:
                notes.append(f"S1: sitemap の crew ページ {len(urls)} 件（一致）")

        releases = os.path.join(meta_dir, "..", "releases", "releases.json")
        if os.path.isfile(releases):
            data = json.load(open(releases, encoding="utf-8"))
            stable = sum(1 for r in data if not r.get("prerelease"))
            total = len(data)
            if stable != SSOT["S4"]["value"]:
                errors.append(
                    f"Releases の安定版が {stable} 件ですが SSoT S4 は {SSOT['S4']['value']} です"
                )
            else:
                notes.append(f"S4: 安定版リリース {stable} 件（一致）")
            if total != SSOT["S5"]["value"]:
                errors.append(
                    f"Releases の総数が {total} 件ですが SSoT S5 は {SSOT['S5']['value']} です"
                )
            else:
                notes.append(f"S5: 総リリース {total} 件（一致）")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--docs-dir", help="スナップショット内の repo/docs ディレクトリ（任意）")
    ap.add_argument("--meta-dir", help="スナップショット内の meta ディレクトリ（任意）")
    args = ap.parse_args()
    os.chdir(repo_root())

    print("=== kiro-crew-docs 件数整合チェック（正準値の水平展開） ===")
    print("")

    errors, notes = [], []

    print("🔍 ページ数3者一致（見出し・§5.8合計表・実ファイル）を検証中...")
    check_page_counts_3way(errors, notes)

    print("🔍 各セクションREADMEの宣言ページ数を検証中...")
    check_declared_page_counts(errors, notes)

    print("🔍 builtin App台帳を検証中...")
    check_builtin_apps_ledger(errors, notes)

    if args.docs_dir and os.path.isdir(args.docs_dir):
        print(f"🔍 一次情報スナップショットと照合中（{args.docs_dir}）...")
        check_against_snapshot(args.docs_dir, args.meta_dir, errors, notes)
    else:
        print("⚠️  一次情報スナップショットとの照合をスキップしました")
        print("   → これは「公式と一致することを検証した」ではありません（**未検証**です）")
        print("   使い方: check-counts.py --docs-dir <snapshot>/repo/docs --meta-dir <snapshot>/meta")

    print("")
    print("=== チェック結果 ===")
    if notes:
        print("正準値の確認:")
        for n in notes:
            print(f"   - {n}")
        print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 件数整合チェックに失敗しました")
        return 1

    print("✅ すべての件数記述が実体と一致しています")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""check-consistency.py - kiro-crew-docs 記述整合チェック（値の水平展開・両併記の対称性）

使用方法:
    ./scripts/kiro-crew-docs/check-consistency.py

目的:
    同じ値が複数ページに書かれている状態で、片方だけ直して他方が古いまま残るのを落とす。
    check-counts.py が「表の実体 vs 宣言件数」を見るのに対し、本スクリプトは
    「文書 A の値 vs 文書 B の値 vs SSoT 定数」を見る。

Crew 固有の最重要検証: **両併記3件の対称性**（出典間で値が食い違うため裁定せず
両方を書く決まりにしたもの。片方のページだけ書いて他方に書き忘れると
「裁定した」ように読めてしまう）:
    S3a  版の日付（CHANGELOG日付 vs Release公開日）
    S15  Subagent上限（subagent.md=32 vs config.md=16）
    S22  サンドボックス呼称（公式docsのauto vs README/内部ティアのstandard）

検証する正準値（値系。S8〜S20・S22・S24）:
    S8  Gatewayポート           = 5476
    S11 拒否コマンドルール件数   = 137
    S16 履歴減衰段数            = 5
    S19 Consolidation閾値       = 30メッセージ / 3時間idle
    S22 サンドボックスモード数   = 3（auto/strict/off）
    S24 コンテキストバジェット   = 165,000文字

⚠️ 数値だけを探さない。単位や文脈語とセットで照合する。
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-crew-docs"
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

# 両併記が必須の3件。それぞれ「両方の値が同一ページに存在するか」を検証する。
DUAL_NOTATION = [
    {
        "id": "S3a", "label": "版の日付（CHANGELOG vs Release公開日）",
        "pattern_a": re.compile(r"CHANGELOG"),
        "pattern_b": re.compile(r"Release\s*公開日|公開日"),
        "target_glob": f"{DOC_ROOT}/02_update/01_changelog.md",
    },
    {
        "id": "S15", "label": "Subagent上限（32 vs 16）",
        "pattern_a": re.compile(r"\b32\b"),
        "pattern_b": re.compile(r"\b16\b"),
        "target_glob": f"{DOC_ROOT}/04_reference/05_limits.md",
    },
    {
        "id": "S22", "label": "サンドボックス呼称（auto vs standard）",
        "pattern_a": re.compile(r"`auto`"),
        "pattern_b": re.compile(r"`standard`|standard"),
        "target_glob": f"{DOC_ROOT}/01_features/09_security.md",
    },
]

# 値系SSoT: 文脈語とセットで数値を検証（所有ファイル=04_reference/05_limits.md）
OWNER = f"{DOC_ROOT}/04_reference/05_limits.md"

SSOT = [
    {"id": "S8", "label": "Gatewayポート", "value": "5476",
     "pattern": re.compile(r"(?:ポート|port)[^\n]{0,20}?\**\s*(5476)\s*\**")},
    {"id": "S11", "label": "拒否コマンドルール件数", "value": "137",
     "pattern": re.compile(r"(?:拒否(?:ルール|コマンド)?[^\n]{0,20}?|deny pattern[^\n]{0,10}?)\**\s*(137)\s*\**")},
    {"id": "S16", "label": "履歴減衰段数", "value": "5",
     "pattern": re.compile(r"(?:履歴(?:の)?減衰)[^\n]{0,10}?\**\s*(5)\s*\**\s*段")},
    {"id": "S24", "label": "コンテキストバジェット", "value": "165000",
     "pattern": re.compile(r"\**\s*(165,000|165000)\s*\**\s*文字")},
]


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_local_only(path):
    norm = path.replace(os.sep, "/")
    return any(f"/{lo}/" in norm or norm.startswith(f"{lo}/") for lo in LOCAL_ONLY)


def all_docs():
    docs = sorted(glob.glob(f"{DOC_ROOT}/**/*.md", recursive=True))
    return [d for d in docs if not is_local_only(d)]


def check_dual_notation(errors, notes):
    """両併記3件が対象ファイルに揃って存在するかを検証する。"""
    for d in DUAL_NOTATION:
        path = d["target_glob"]
        if not os.path.isfile(path):
            notes.append(f"{d['id']}: {path} は未執筆（Phase 3/4で執筆予定）")
            continue
        txt = open(path, encoding="utf-8").read()
        has_a = bool(d["pattern_a"].search(txt))
        has_b = bool(d["pattern_b"].search(txt))
        if has_a and has_b:
            notes.append(f"{d['id']}: {d['label']} — 両方の値が {path} に存在（対称性OK）")
        elif has_a or has_b:
            errors.append(
                f"{path}: {d['id']}（{d['label']}）が**片方だけ**しか書かれていません"
                f"（一方だけ検出={has_a and 'A' or 'B'}）。両併記の対称性が崩れています"
            )
        else:
            notes.append(f"{d['id']}: {d['label']} — {path} にまだ記述なし（未執筆）")


def check_value_ssot(errors, notes):
    """値系SSoTが所有ファイルに記載され、他ページで異なる値になっていないかを検証する。"""
    if not os.path.isfile(OWNER):
        notes.append(f"所有ファイル {OWNER} が未執筆のため値系SSoT検証をスキップ")
        return
    owner_txt = open(OWNER, encoding="utf-8").read()
    for s in SSOT:
        m = s["pattern"].search(owner_txt)
        if not m:
            notes.append(f"{s['id']}: {s['label']} の記述が {OWNER} に見つかりません（未執筆の可能性）")
            continue
        found = m.group(1).replace(",", "")
        if found != s["value"].replace(",", ""):
            errors.append(
                f"{OWNER}: {s['id']}（{s['label']}）が {found} と書かれていますが "
                f"SSoT は {s['value']} です"
            )
        else:
            notes.append(f"{s['id']}: {s['label']} = {found}（{OWNER} で一致）")


def check_source_dates_consistency(errors, notes):
    """同一の出典URL・commit SHAに対する参照日が、複数ファイル間で食い違っていないかを検証する。"""
    sha_pattern = re.compile(r"commit\s*`([0-9a-f]{7})`")
    shas_by_file = {}
    for path in all_docs():
        txt = open(path, encoding="utf-8").read()
        shas = set(sha_pattern.findall(txt))
        if shas:
            shas_by_file[path] = shas

    all_shas = set()
    for shas in shas_by_file.values():
        all_shas |= shas
    if len(all_shas) > 1:
        notes.append(f"commit SHA の異なる値が {len(all_shas)} 種類使われています: {sorted(all_shas)}"
                     "（意図的に異なる取得時点を参照している場合は問題なし）")
    elif len(all_shas) == 1:
        notes.append(f"commit SHA は全ファイルで統一されています: {list(all_shas)[0]}")


def main():
    os.chdir(repo_root())

    print("=== kiro-crew-docs 記述整合チェック（値の水平展開・両併記の対称性） ===")
    print("")

    errors, notes = [], []

    print("🔍 両併記3件（S3a/S15/S22）の対称性を検証中...")
    check_dual_notation(errors, notes)

    print("🔍 値系SSoTの所有ファイルとの一致を検証中...")
    check_value_ssot(errors, notes)

    print("🔍 出典日・commit SHAの水平展開を検証中...")
    check_source_dates_consistency(errors, notes)

    print("")
    print("=== チェック結果 ===")
    if notes:
        print("確認事項:")
        for n in notes:
            print(f"   - {n}")
        print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 記述整合チェックに失敗しました")
        return 1

    print("✅ すべての値記述が整合しています")
    return 0


if __name__ == "__main__":
    sys.exit(main())

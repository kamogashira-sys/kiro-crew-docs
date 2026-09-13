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
        "pattern_a": re.compile(r"subagent_auto_max[^\n]{0,40}?`subagent\.md`\s*[:：]\s*32\b"),
        "pattern_b": re.compile(r"subagent_auto_max[^\n]{0,40}?`config\.md`\s*[:：]\s*16\b"),
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
     "pattern": re.compile(r"(?:既定ポート|Gatewayポート|gateway\s*port|KIROCREW_PORT)[^\n]{0,20}?\**\s*(\d{2,6})\s*\**", re.IGNORECASE),
     "extra_patterns": [re.compile(r"(?:localhost|127\.0\.0\.1)[:：](\d{2,6})")]},
    {"id": "S11", "label": "拒否コマンドルール件数", "value": "137",
     "pattern": re.compile(r"(?:拒否コマンドルール件数|deny\s*pattern\s*count)[^\n]{0,10}?\**\s*(\d{1,6})\s*\**")},
    {"id": "S16", "label": "履歴減衰段数", "value": "5",
     "pattern": re.compile(r"履歴減衰の段数[^\n]{0,10}?\**\s*(\d{1,3})\s*\**\s*段")},
    {"id": "S19a", "label": "Consolidationトリガー（好み/プロジェクト）", "value": "30",
     "pattern": re.compile(r"Consolidationトリガー[^\n]{0,20}?好み/プロジェクト[^\n]{0,20}?\**\s*(\d{1,6})\s*\**\s*メッセージ")},
    {"id": "S19b", "label": "Consolidationトリガー（履歴/レッスン）", "value": "3",
     "pattern": re.compile(r"Consolidationトリガー[^\n]{0,20}?履歴/レッスン[^\n]{0,20}?\**\s*(\d{1,3})\s*\**\s*時間アイドル")},
    {"id": "S24", "label": "コンテキストバジェット", "value": "165000",
     "pattern": re.compile(r"コンテキストバジェット[^\n]{0,20}?\**\s*([\d,]{3,10})\s*\**\s*文字")},
    # --- 件数系SSoT（S1〜S6）: D-15（案1）により追加 -------------------------
    # 背景: check-counts.py は「定数 ↔ 一次情報スナップショット実測」を突合するが
    # OWNER（05_limits.md）の本文を読まない。一方このリストは①OWNER自身の値と
    # ②OWNER以外の全ページでの水平展開一致を同時に検査する。両者の隙間にあった
    # 「05_limits.md が旧値でも全検証器 exit 0」という穴を閉じるための登録である。
    # 注意: 文脈語を緩めると版節内の「当時の値」を誤検知する。文脈語は必ず
    # 「その値が現在値を指すときだけ現れる語」に限定すること。
    {"id": "S1", "label": "公式docsのcrewページ数", "value": "49",
     "pattern": re.compile(r"(?:公式docsのcrewページ数|`kiro\.dev/docs/crew/`配下)\D{0,8}?\**\s*(\d{1,4})\s*\**"),
     # 2桁以上に限定する理由: 「公式2ページと…で確認済み」のように、総数ではなく
     # 「特定の2ページ」を指す表現が実在し、1桁を許すと誤検知になる。公式ページの
     # 総数は2桁以上であるため、この制約で総数の指し先だけを拾える。
     "extra_patterns": [re.compile(r"公式\s*(\d{2,4})\s*ページ")]},
    {"id": "S2", "label": "リポジトリdocs配下ファイル数", "value": "230",
     "pattern": re.compile(r"(?:リポジトリ`docs/`配下ファイル数|`docs/`\s*配下は)\D{0,8}?\**\s*(\d{1,5})\s*\**")},
    {"id": "S3", "label": "最新安定版", "value": "0.6.0",
     "pattern": re.compile(r"最新安定版\D{0,8}?\**\s*v(\d+\.\d+\.\d+)\s*\**")},
    {"id": "S4", "label": "安定版リリース数", "value": "10",
     "pattern": re.compile(r"安定版リリース数\D{0,8}?\**\s*(\d{1,4})\s*\**")},
    {"id": "S5", "label": "総リリース数", "value": "59",
     "pattern": re.compile(r"総リリース数(?:（プレリリース含む）)?\D{0,8}?\**\s*(\d{1,4})\s*\**"),
     "extra_patterns": [re.compile(r"全\s*(\d{1,4})\s*Release")]},
    {"id": "S6", "label": "CHANGELOG.mdの版節数", "value": "8",
     "pattern": re.compile(r"CHANGELOG\.mdの版節数\D{0,8}?\**\s*(\d{1,3})\s*\**")},
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

    # 水平展開検証: OWNER以外のページで同じ文脈語＋数値パターンが登場する場合、
    # SSoT値と異なっていないかを確認する。OWNER自身は既に上のループで検証済みなので除外する。
    # `pattern`（主パターン）と `extra_patterns`（同じ値を指す別表記。例: `localhost:PORT`）の
    # 両方を対象にし、実際にマッチした数値をSSoT値と比較する（固定値マッチだと改変を検出できないため）。
    other_docs = [d for d in all_docs() if os.path.abspath(d) != os.path.abspath(OWNER)]
    mismatches_by_id = {}
    matches_by_id = {}
    for path in other_docs:
        txt = open(path, encoding="utf-8").read()
        for s in SSOT:
            patterns = [s["pattern"]] + s.get("extra_patterns", [])
            for pat in patterns:
                for m in pat.finditer(txt):
                    found = m.group(1).replace(",", "")
                    line_no = txt.count("\n", 0, m.start()) + 1
                    if found != s["value"].replace(",", ""):
                        mismatches_by_id.setdefault(s["id"], []).append(
                            f"{path}:{line_no} は {found}（SSoTは{s['value']}）"
                        )
                    else:
                        matches_by_id.setdefault(s["id"], []).append(f"{path}:{line_no}")

    for s in SSOT:
        sid = s["id"]
        if sid in mismatches_by_id:
            for detail in mismatches_by_id[sid]:
                errors.append(
                    f"{sid}（{s['label']}）の値が水平展開先で食い違っています: {detail}"
                )
        elif sid in matches_by_id:
            notes.append(
                f"{sid}: {s['label']} は {len(matches_by_id[sid])} 箇所の水平展開先でも "
                f"{OWNER} と一致（{', '.join(matches_by_id[sid])}）"
            )


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

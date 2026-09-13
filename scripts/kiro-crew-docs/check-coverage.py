#!/usr/bin/env python3
"""check-coverage.py - 公式ページ台帳の網羅性を検証する

使用方法:
    ./scripts/kiro-crew-docs/check-coverage.py
    ./scripts/kiro-crew-docs/check-coverage.py --repo-dir <snapshot>/repo
        # 一次情報スナップショットがあれば sitemap 実測との突き合わせも行う

Crew 版の設計（Rev 1 からの再設計理由）:
    兄弟サイトは「changelog エントリの網羅性」を検証するが、Crew は changelog が
    GitHub のため、それに相当する検証対象が無い。代わりに **「公式ページのどれを
    扱い、どれを意図的に扱わないか」の台帳（05_meta/ledger-official-pages.md）**を
    検証対象にする。

    ⚠️ **Rev 1 はこの検証を設計しながら台帳自体を成果物にしておらず、実際に
    `features/artifact-deploy` が未割当のまま残っていた**。本スクリプトは
    台帳の各行に「担当ページ」または「不扱い理由」が明記されているかを検証する。

検証内容:
    1. 台帳（ledger-official-pages.md）が EXPECTED_OFFICIAL_PAGES 行（README分含む）持っていること
    2. 各行に担当ページ（`01_features/NN_xxx.md` 等）が記載されていること
       （未割当が0件であること）
    3. 台帳が指す担当ページが実際に公開対象ディレクトリに存在すること
       （ファイル名だけの記載は`01_features/`配下、`/`を含む記載はフルパスとして解決する）
    4. モジュール台帳（ledger-modules.md）が EXPECTED_MODULES 件すべてに判定を持つこと

fail-safe:
    台帳ファイルが無い場合は exit 0＋警告（Phase 0 未実施の場合はスキップ）。
"""
import argparse
import glob
import os
import re
import sys

LEDGER_PAGES = "kiro-crew-docs/05_meta/ledger-official-pages.md"
LEDGER_MODULES = "kiro-crew-docs/05_meta/ledger-modules.md"
EXPECTED_OFFICIAL_PAGES = 49
EXPECTED_MODULES = 88  # v0.6.0タグ実測（直下3/common7/modules78）。v0.3.0時点の76から更新

ROW_RE = re.compile(r'^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|', re.M)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def check_official_pages_ledger(errors, notes):
    if not os.path.isfile(LEDGER_PAGES):
        notes.append(f"{LEDGER_PAGES} が未作成（Phase 0-7 で作成予定）")
        return
    txt = open(LEDGER_PAGES, encoding="utf-8").read()
    rows = ROW_RE.findall(txt)
    if len(rows) != EXPECTED_OFFICIAL_PAGES:
        errors.append(
            f"{LEDGER_PAGES}: 台帳の行数が {len(rows)} 件ですが公式{EXPECTED_OFFICIAL_PAGES}ページと一致しません"
        )
    else:
        notes.append(f"公式ページ台帳: {len(rows)} 件（{EXPECTED_OFFICIAL_PAGES}件と一致）")

    unassigned = []
    missing_files = []
    for num, url, assignment in rows:
        # 「担当ページ」列が空、または「未割当」等の語を含む場合は未割当とみなす
        if not assignment.strip() or re.search(r"未割当|TBD|未定", assignment):
            unassigned.append((num, url))
            continue
        # 担当ページが実際に公開対象に存在するかを検証する。
        # 列の形式は次の3パターン: `01_architecture.md`（01_features/配下は省略）、
        # `03_deployment/01_installation.md`（フルパス）、
        # `09_security.md` ＋ `03_deployment/04_security-hardening.md`（複数ファイルを＋で連結）。
        for raw_name in re.findall(r"`([^`]+\.md)`", assignment):
            candidates = [raw_name] if "/" in raw_name else [f"01_features/{raw_name}", raw_name]
            resolved = [c for c in candidates if os.path.isfile(f"kiro-crew-docs/{c}")]
            if not resolved:
                missing_files.append((num, url, raw_name))
    if unassigned:
        errors.append(
            f"{LEDGER_PAGES}: 未割当が {len(unassigned)} 件あります: "
            f"{[f'#{n} {u}' for n, u in unassigned]}"
        )
    else:
        notes.append("公式ページ台帳: 未割当0件")

    if missing_files:
        errors.append(
            f"{LEDGER_PAGES}: 担当ページが実在しない行が {len(missing_files)} 件あります: "
            f"{[f'#{n} {u} -> {f}' for n, u, f in missing_files]}"
        )
    else:
        notes.append(f"公式ページ台帳: 担当ページの実在確認 {len(rows)} 件すべてOK")


def check_modules_ledger(errors, notes):
    if not os.path.isfile(LEDGER_MODULES):
        notes.append(f"{LEDGER_MODULES} が未作成（Phase 0-8 で作成予定）")
        return
    txt = open(LEDGER_MODULES, encoding="utf-8").read()
    m = re.search(r"\*\*合計\*\*\s*\|\s*\*\*(\d+)\*\*", txt)
    if m:
        total = int(m.group(1))
        if total != EXPECTED_MODULES:
            errors.append(
                f"{LEDGER_MODULES}: 集計の合計が {total} 件ですが実測{EXPECTED_MODULES}件と一致しません"
            )
        else:
            notes.append(f"モジュール台帳: 合計 {total} 件（{EXPECTED_MODULES}件と一致）")
    else:
        notes.append(f"{LEDGER_MODULES}: 合計欄が見つかりません（形式が変わった可能性）")


def check_against_sitemap(repo_dir, errors, notes):
    """スナップショットのsitemapと台帳の件数が一致するかを検証する（任意）。"""
    sitemap = os.path.join(repo_dir, "..", "meta", "sitemap.xml")
    if not os.path.isfile(sitemap):
        return
    s = open(sitemap, encoding="utf-8").read()
    urls = re.findall(r"<loc>(https://kiro\.dev/docs/crew/[^<]*)</loc>", s)
    if len(urls) != EXPECTED_OFFICIAL_PAGES:
        errors.append(
            f"sitemap実測の公式crewページが {len(urls)} 件ですが台帳の前提{EXPECTED_OFFICIAL_PAGES}件と一致しません"
            "（公式サイトが更新された可能性。台帳の再作成が必要）"
        )
    else:
        notes.append(f"sitemap実測: {len(urls)} 件（台帳の前提と一致）")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo-dir", help="スナップショット内の repo ディレクトリ（任意）")
    args = ap.parse_args()
    os.chdir(repo_root())

    print("=== kiro-crew-docs 公式ページ網羅性チェック ===")
    print("")

    errors, notes = [], []

    print(f"🔍 公式{EXPECTED_OFFICIAL_PAGES}ページ台帳の未割当を検証中...")
    check_official_pages_ledger(errors, notes)

    print(f"🔍 モジュール{EXPECTED_MODULES}ファイル台帳の判定漏れを検証中...")
    check_modules_ledger(errors, notes)

    if args.repo_dir and os.path.isdir(args.repo_dir):
        print(f"🔍 sitemap実測との突き合わせ中（{args.repo_dir}）...")
        check_against_sitemap(args.repo_dir, errors, notes)
    else:
        print("⚠️  一次情報スナップショットとの照合をスキップしました（未検証です）")

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
        print("❌ 網羅性チェックに失敗しました")
        return 1

    print("✅ 網羅性に問題はありません")
    return 0


if __name__ == "__main__":
    sys.exit(main())

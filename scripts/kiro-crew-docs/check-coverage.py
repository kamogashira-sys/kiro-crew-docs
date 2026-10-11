#!/usr/bin/env python3
"""check-coverage.py - 公式ページ台帳の網羅性を検証する

使用方法:
    ./scripts/kiro-crew-docs/check-coverage.py
    ./scripts/kiro-crew-docs/check-coverage.py --repo-dir <snapshot>/repo
        # 一次情報スナップショットがあれば sitemap 実測との突き合わせも行う

Crew 版の設計（Rev 1 からの再設計理由）:
    兄弟サイトは「changelog エントリの網羅性」を検証するが、Crew は changelog が
    GitHub のため、それに相当する検証対象が無い。代わりに **「公式ページのどれを
    扱い、どれを意図的に扱わないか」の台帳（scripts/kiro-crew-docs/ledgers/official-pages.md）**を
    検証対象にする。

    ⚠️ **Rev 1 はこの検証を設計しながら台帳自体を成果物にしておらず、実際に
    `features/artifact-deploy` が未割当のまま残っていた**。本スクリプトは
    台帳の各行に「担当ページ」または「不扱い理由」が明記されているかを検証する。

検証内容:
    1. 台帳（official-pages.md）が EXPECTED_OFFICIAL_PAGES 行（README分含む）持っていること
    2. 各行に担当ページ（`01_features/NN_xxx.md` 等）が記載されていること
       （未割当が0件であること）
    3. 台帳が指す担当ページが実際に公開対象ディレクトリに存在すること
       （ファイル名だけの記載は`01_features/`配下、`/`を含む記載はフルパスとして解決する）
    4. モジュール台帳（modules.md）が EXPECTED_MODULES 件すべてに判定を持つこと

fail-safe:
    台帳ファイルが無い場合は exit 0＋警告（Phase 0 未実施の場合はスキップ）。

--strict（クラウド入口 check-kiro-crew-cloud から呼ぶ。既定はオフで、上の挙動を変えない）:
    スキップを合格にしない。台帳不在・--repo-dir 不在・sitemap 不在・合計欄の欠落をエラーにし、
    sitemap 実測の URL 集合と台帳の URL 列の集合が一致することも検査する。
    末尾に `KCD-SUMMARY:` で始まる要約行（公式ページ台帳 N/N・モジュール台帳 N/N・sitemap 実測 N）を出す。

環境変数:
    KCD_LEDGER_DIR  台帳のディレクトリ（既定 scripts/kiro-crew-docs/ledgers）。ネガティブテストで /tmp の複製に差し替える
"""
import argparse
import glob
import os
import re
import sys

LEDGER_DIR = os.environ.get("KCD_LEDGER_DIR") or "scripts/kiro-crew-docs/ledgers"
LEDGER_PAGES = os.path.join(LEDGER_DIR, "official-pages.md")
LEDGER_MODULES = os.path.join(LEDGER_DIR, "modules.md")
EXPECTED_OFFICIAL_PAGES = 49
EXPECTED_MODULES = 104  # v0.7.2タグ実測（直下3/common7/modules94。.mdのみは101）。v0.6.0タグは88

ROW_RE = re.compile(r'^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|', re.M)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def check_official_pages_ledger(errors, notes, strict=False, summary=None):
    if not os.path.isfile(LEDGER_PAGES):
        if strict:
            errors.append(f"{LEDGER_PAGES} がありません（--strict では台帳不在を合格にしません）")
        else:
            notes.append(f"{LEDGER_PAGES} が未作成（Phase 0-7 で作成予定）")
        return
    txt = open(LEDGER_PAGES, encoding="utf-8").read()
    rows = ROW_RE.findall(txt)
    if summary is not None:
        summary["ledger_urls"] = [url for _num, url, _assignment in rows]
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


def check_modules_ledger(errors, notes, strict=False, summary=None):
    if not os.path.isfile(LEDGER_MODULES):
        if strict:
            errors.append(f"{LEDGER_MODULES} がありません（--strict では台帳不在を合格にしません）")
        else:
            notes.append(f"{LEDGER_MODULES} が未作成（Phase 0-8 で作成予定）")
        return
    txt = open(LEDGER_MODULES, encoding="utf-8").read()
    m = re.search(r"\*\*合計\*\*\s*\|\s*\*\*(\d+)\*\*", txt)
    if m:
        total = int(m.group(1))
        if summary is not None:
            summary["modules_total"] = total
        if total != EXPECTED_MODULES:
            errors.append(
                f"{LEDGER_MODULES}: 集計の合計が {total} 件ですが実測{EXPECTED_MODULES}件と一致しません"
            )
        else:
            notes.append(f"モジュール台帳: 合計 {total} 件（{EXPECTED_MODULES}件と一致）")
    elif strict:
        errors.append(f"{LEDGER_MODULES}: 合計欄が見つかりません（形式が変わった可能性。--strict ではエラー）")
    else:
        notes.append(f"{LEDGER_MODULES}: 合計欄が見つかりません（形式が変わった可能性）")


def check_against_sitemap(repo_dir, errors, notes, strict=False, summary=None):
    """スナップショットのsitemapと台帳の件数が一致するかを検証する（任意）。"""
    sitemap = os.path.join(repo_dir, "..", "meta", "sitemap.xml")
    if not os.path.isfile(sitemap):
        if strict:
            errors.append(f"{sitemap} がありません（--strict では sitemap 照合のスキップを合格にしません）")
        return
    s = open(sitemap, encoding="utf-8").read()
    urls = re.findall(r"<loc>(https://kiro\.dev/docs/crew/[^<]*)</loc>", s)
    if summary is not None:
        summary["sitemap_urls"] = urls
    if len(urls) != EXPECTED_OFFICIAL_PAGES:
        errors.append(
            f"sitemap実測の公式crewページが {len(urls)} 件ですが台帳の前提{EXPECTED_OFFICIAL_PAGES}件と一致しません"
            "（公式サイトが更新された可能性。台帳の再作成が必要）"
        )
    else:
        notes.append(f"sitemap実測: {len(urls)} 件（台帳の前提と一致）")


def check_url_sets(errors, notes, summary):
    """--strict: sitemap 実測の URL 集合と台帳の URL 列の集合が一致するかを検証する。"""
    if "sitemap_urls" not in summary or "ledger_urls" not in summary:
        return  # 台帳不在・sitemap 不在は呼び出し元でエラー済み
    sitemap_set = {u.replace("https://kiro.dev", "", 1) for u in summary["sitemap_urls"]}
    ledger_set = set(summary["ledger_urls"])
    only_sitemap = sorted(sitemap_set - ledger_set)
    only_ledger = sorted(ledger_set - sitemap_set)
    summary["matched"] = len(sitemap_set & ledger_set)
    if only_sitemap or only_ledger:
        errors.append(
            f"sitemap 実測と台帳の URL 集合が一致しません: sitemap のみ {only_sitemap} / 台帳のみ {only_ledger}"
        )
    else:
        notes.append(f"sitemap 実測と台帳の URL 集合が一致（{len(sitemap_set)} 件）")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo-dir", help="スナップショット内の repo ディレクトリ（任意）")
    ap.add_argument("--strict", action="store_true",
                    help="スキップを合格にしない（台帳不在・--repo-dir 不在をエラーにし、URL 集合の一致も検査する）")
    args = ap.parse_args()
    os.chdir(repo_root())

    print("=== kiro-crew-docs 公式ページ網羅性チェック ===")
    print("")

    errors, notes = [], []
    summary = {} if args.strict else None

    print(f"🔍 公式{EXPECTED_OFFICIAL_PAGES}ページ台帳の未割当を検証中...")
    check_official_pages_ledger(errors, notes, args.strict, summary)

    print(f"🔍 モジュール{EXPECTED_MODULES}ファイル台帳の判定漏れを検証中...")
    check_modules_ledger(errors, notes, args.strict, summary)

    if args.repo_dir and os.path.isdir(args.repo_dir):
        print(f"🔍 sitemap実測との突き合わせ中（{args.repo_dir}）...")
        check_against_sitemap(args.repo_dir, errors, notes, args.strict, summary)
        if args.strict:
            print("🔍 sitemap実測と台帳の URL 集合を照合中（--strict）...")
            check_url_sets(errors, notes, summary)
    elif args.strict:
        errors.append(f"--repo-dir {args.repo_dir!r} がありません（--strict では一次情報との照合のスキップを合格にしません）")
    else:
        print("⚠️  一次情報スナップショットとの照合をスキップしました（未検証です）")

    print("")
    print("=== チェック結果 ===")
    if notes:
        print("確認事項:")
        for n in notes:
            print(f"   - {n}")
        print("")

    if args.strict:
        sitemap_n = len(summary["sitemap_urls"]) if "sitemap_urls" in summary else "未測定"
        matched = summary.get("matched", "未測定")
        modules = summary.get("modules_total", "未測定")
        print(f"KCD-SUMMARY: 公式ページ台帳 {matched}/{sitemap_n}")
        print(f"KCD-SUMMARY: モジュール台帳 {modules}/{EXPECTED_MODULES}")
        print(f"KCD-SUMMARY: sitemap 実測 {sitemap_n}")
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

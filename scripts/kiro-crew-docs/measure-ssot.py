#!/usr/bin/env python3
"""measure-ssot.py - 一次情報スナップショットから機械測定できる SSoT を測り、検証器の定数と比べる

使用方法:
    ./scripts/kiro-crew-docs/measure-ssot.py --snapshot <dir>
        # 測定値と各検証器の定数を Markdown の表で表示する（exit 0）
    ./scripts/kiro-crew-docs/measure-ssot.py --snapshot <dir> --expect-constants
        # 測定値と定数が1つでも不一致、または同じ ID の定数どうしが1つでも不一致なら exit 1
    ./scripts/kiro-crew-docs/measure-ssot.py --snapshot <dir> --page-updated-diff
        # 公式ページ台帳の「公式 Page updated（固定時点）」「.md sha256（固定時点）」列と PIN.json を
        # URL ごとに比べ、どちらかが異なるページの一覧を表示する（exit 0）
    ./scripts/kiro-crew-docs/measure-ssot.py --snapshot <dir> --expect-ledger-current
        # 同じ比較で差分が1件でもあれば exit 1

    <dir> は fetch-snapshot.sh の保存先（例: /tmp/kiro-crew-primary/20261011_v0.7.2。PIN.json がある形式）。

目的:
    前回値の正本（ローカルの作業記録）が無いクラウドで、検証器定数と一次情報の実測値を機械比較する。
    同じ値が複数の検証器に重複して定義されているため（S1: 4箇所、S3: 4箇所、S4: 5箇所 など）、
    一部だけ更新する漏れも検出する。

測定方法（数え方は ledger-modules.md の「数え方」と同じく `find -type f` 相当の全ファイル）:
    S1  meta/sitemap.xml の docs/crew/ URL 件数
    S2  repo/docs 配下のファイル数
    S3  releases.json の安定版のうち published_at が PIN.release_published_at 以前で最新の tag_name
    S4  同条件の安定版の件数と版番号の集合
    S6  タグ版 repo/CHANGELOG.md の `## [X.Y.Z]` 見出し数
    S28 repo/docs/system-specs 配下のファイル数
    S5  releases.json の総件数（取得時点の値。測定値とは比較せず、定数どうしの一致だけを見る）
    版番号は先頭の v を除いて比較し、check-consistency.py の SSOT の値（文字列）は数値に正規化する。

--page-updated-diff / --expect-ledger-current:
    台帳が無い、または2列が無い場合は比較できないため、どちらのオプションでも exit 1（未検証を合格にしない）。

環境変数:
    KCD_LEDGER_DIR  公式ページ台帳のディレクトリ（既定 kiro-crew-docs/05_meta）
"""
import argparse
import json
import os
import re
import sys
import types

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
KIRO_DEV = "https://kiro.dev"
CHECKERS = {
    "counts": "check-counts.py",
    "consistency": "check-consistency.py",
    "freshness": "check-freshness.py",
    "coverage": "check-coverage.py",
    "changelog": "check-changelog.py",
    "notation": "check-notation.py",
}


def repo_root():
    return os.path.abspath(os.path.join(SCRIPTS_DIR, "..", ".."))


def load_checker(key):
    """ファイル名にハイフンがあるため、ファイルパスを指定して読み込む。

    __pycache__ のバイトコードは使わない（ソースの mtime が秒単位で同じ・サイズが同じ編集だと
    古いバイトコードが読まれ、定数の変更を取りこぼすため。ネガティブテストで実測）。
    """
    path = os.path.join(SCRIPTS_DIR, CHECKERS[key])
    mod = types.ModuleType(f"kcd_{key}")
    mod.__file__ = path
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), mod.__dict__)
    return mod


def ver_key(v):
    return tuple(int(x) for x in str(v).lstrip("v").split("."))


def norm(v):
    """比較用の正規化: 版番号は v を除き、数値の文字列は int にする。"""
    if isinstance(v, str):
        s = v.lstrip("v").replace(",", "")
        return int(s) if s.isdigit() else s
    return v


def count_files(path):
    n = 0
    for dirpath, _dirs, files in os.walk(path):
        n += sum(1 for f in files if os.path.isfile(os.path.join(dirpath, f))
                 and not os.path.islink(os.path.join(dirpath, f)))
    return n


def measure(snapshot):
    pin_path = os.path.join(snapshot, "PIN.json")
    if not os.path.isfile(pin_path):
        sys.exit(f"❌ {pin_path} がありません（fetch-snapshot.sh で取得したスナップショットを指定してください）")
    pin = json.load(open(pin_path, encoding="utf-8"))
    cutoff = pin.get("release_published_at")
    if not cutoff:
        sys.exit("❌ PIN.json の release_published_at がありません（タグで取得したスナップショットが必要です）")

    sitemap = open(os.path.join(snapshot, "meta", "sitemap.xml"), encoding="utf-8").read()
    s1 = len(re.findall(r"<loc>(https://kiro\.dev/docs/crew/[^<]*)</loc>", sitemap))
    s2 = count_files(os.path.join(snapshot, "repo", "docs"))
    releases = json.load(open(os.path.join(snapshot, "releases", "releases.json"), encoding="utf-8"))
    stable = [r for r in releases if not r.get("prerelease") and r["published_at"] <= cutoff]
    stable.sort(key=lambda r: r["published_at"])
    s3 = stable[-1]["tag_name"].lstrip("v") if stable else None
    s4_set = {r["tag_name"].lstrip("v") for r in stable}
    changelog = open(os.path.join(snapshot, "repo", "CHANGELOG.md"), encoding="utf-8").read()
    s6 = len(re.findall(r"(?m)^## \[\d+\.\d+\.\d+\]", changelog))
    s28 = count_files(os.path.join(snapshot, "repo", "docs", "system-specs"))
    return pin, {"S1": s1, "S2": s2, "S3": s3, "S4": len(s4_set), "S4_set": s4_set,
                 "S5": len(releases), "S6": s6, "S28": s28}


def consistency_value(mod, sid):
    for s in mod.SSOT:
        if s["id"] == sid:
            return s["value"]
    return None


def constants(mods):
    """ID ごとに（定義箇所, 値）の一覧を返す。"""
    c, k, f, cov, cl, nt = (mods[x] for x in ("counts", "consistency", "freshness", "coverage", "changelog", "notation"))
    return {
        "S1": [("check-counts.py SSOT['S1']", c.SSOT["S1"]["value"]),
               ("check-consistency.py SSOT id=S1", consistency_value(k, "S1")),
               ("check-freshness.py KNOWN_CREW_PAGES", f.KNOWN_CREW_PAGES),
               ("check-coverage.py EXPECTED_OFFICIAL_PAGES", cov.EXPECTED_OFFICIAL_PAGES)],
        "S2": [("check-counts.py SSOT['S2']", c.SSOT["S2"]["value"]),
               ("check-consistency.py SSOT id=S2", consistency_value(k, "S2"))],
        "S3": [("check-consistency.py SSOT id=S3", consistency_value(k, "S3")),
               ("check-freshness.py KNOWN_LATEST_STABLE", f.KNOWN_LATEST_STABLE),
               ("max(check-changelog.py VALID_STABLE_VERSIONS)", max(cl.VALID_STABLE_VERSIONS, key=ver_key)),
               ("max(check-notation.py VALID_STABLE_VERSIONS)", max(nt.VALID_STABLE_VERSIONS, key=ver_key))],
        "S4": [("check-counts.py SSOT['S4']", c.SSOT["S4"]["value"]),
               ("check-consistency.py SSOT id=S4", consistency_value(k, "S4")),
               ("check-freshness.py KNOWN_STABLE_COUNT", f.KNOWN_STABLE_COUNT),
               ("len(check-changelog.py VALID_STABLE_VERSIONS)", len(cl.VALID_STABLE_VERSIONS)),
               ("len(check-notation.py VALID_STABLE_VERSIONS)", len(nt.VALID_STABLE_VERSIONS))],
        "S4_set": [("check-changelog.py VALID_STABLE_VERSIONS", set(cl.VALID_STABLE_VERSIONS)),
                   ("check-notation.py VALID_STABLE_VERSIONS", set(nt.VALID_STABLE_VERSIONS))],
        "S5": [("check-counts.py SSOT['S5']", c.SSOT["S5"]["value"]),
               ("check-consistency.py SSOT id=S5", consistency_value(k, "S5"))],
        "S6": [("check-consistency.py SSOT id=S6", consistency_value(k, "S6"))],
        "S28": [("check-coverage.py EXPECTED_MODULES", cov.EXPECTED_MODULES)],
    }


def fmt(v):
    if isinstance(v, set):
        return "{" + ", ".join(sorted(v, key=ver_key)) + "}"
    return str(v)


def compare_constants(measured, consts):
    """表の行と、不一致（測定値と定数・定数どうし）の一覧を返す。"""
    rows, mismatches = [], []
    matched = compared = 0
    for sid in ("S1", "S2", "S3", "S4", "S4_set", "S6", "S28", "S5"):
        values = consts[sid]
        for where, value in values:
            if sid == "S5":
                rows.append((sid, f"{measured['S5']}（取得時点。比較しない）", where, fmt(value), "—"))
                continue
            if sid == "S4_set":
                ok = set(norm(x) for x in value) == measured["S4_set"]
            else:
                ok = norm(value) == norm(measured[sid])
            compared += 1
            matched += ok
            rows.append((sid, fmt(measured[sid]), where, fmt(value), "✅" if ok else "❌"))
            if not ok:
                mismatches.append(f"{sid}: 測定値 {fmt(measured[sid])} と {where} = {fmt(value)} が一致しません")
        normalized = {fmt(set(norm(x) for x in v)) if sid == "S4_set" else norm(v) for _w, v in values}
        if len(normalized) > 1:
            mismatches.append(
                f"{sid}: 重複定義どうしが一致しません（"
                + " / ".join(f"{w} = {fmt(v)}" for w, v in values) + "）")
    return rows, mismatches, matched, compared


def parse_ledger(path):
    """公式ページ台帳から URL→(Page updated, sha256) を読む。列が無ければ None を返す。"""
    lines = open(path, encoding="utf-8").read().split("\n")
    header_idx = None
    for i, line in enumerate(lines):
        if line.startswith("|") and "公式URL" in line:
            header_idx = i
            break
    if header_idx is None:
        return None, "公式URL の列を持つ表が見つかりません"
    headers = [h.strip() for h in lines[header_idx].strip().strip("|").split("|")]
    try:
        url_col = next(i for i, h in enumerate(headers) if "公式URL" in h)
        pu_col = next(i for i, h in enumerate(headers) if "Page updated" in h)
        sha_col = next(i for i, h in enumerate(headers) if "sha256" in h)
    except StopIteration:
        return None, "「公式 Page updated（固定時点）」列または「.md sha256（固定時点）」列がありません"
    result = {}
    for line in lines[header_idx + 2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) <= max(url_col, pu_col, sha_col):
            continue
        url = cells[url_col].strip("`")
        result[KIRO_DEV + url if url.startswith("/") else url] = (cells[pu_col].strip("`"), cells[sha_col].strip("`"))
    return result, None


def page_updated_diff(pin, ledger_dir):
    path = os.path.join(ledger_dir, "ledger-official-pages.md")
    if not os.path.isfile(path):
        return None, f"{path} がありません"
    ledger, err = parse_ledger(path)
    if ledger is None:
        return None, f"{path}: {err}"
    pu, sha = pin.get("official_page_updated", {}), pin.get("official_md_sha256", {})
    diffs = []
    for url in sorted(set(ledger) | set(pu)):
        if url not in ledger:
            diffs.append((url, "（台帳に無い）", f"{pu.get(url)} / {sha.get(url)}", "台帳に行が無い"))
            continue
        if url not in pu:
            diffs.append((url, " / ".join(ledger[url]), "（PIN に無い）", "PIN に無い（公式から消えた可能性）"))
            continue
        lp, ls = ledger[url]
        changed = []
        if lp != pu[url]:
            changed.append("Page updated")
        if ls != sha.get(url):
            changed.append(".md sha256")
        if changed:
            diffs.append((url, f"{lp} / {ls}", f"{pu[url]} / {sha.get(url)}", "・".join(changed)))
    return diffs, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--snapshot", required=True, help="fetch-snapshot.sh の保存先（PIN.json を含むディレクトリ）")
    ap.add_argument("--expect-constants", action="store_true", help="測定値・定数どうしの不一致で exit 1")
    ap.add_argument("--page-updated-diff", action="store_true", help="台帳と PIN.json の Page updated・sha256 の差分を表示")
    ap.add_argument("--expect-ledger-current", action="store_true", help="台帳と PIN.json の差分が1件でもあれば exit 1")
    args = ap.parse_args()
    os.chdir(repo_root())
    ledger_dir = os.environ.get("KCD_LEDGER_DIR") or "kiro-crew-docs/05_meta"

    pin, measured = measure(args.snapshot)
    mods = {k: load_checker(k) for k in CHECKERS}
    rows, mismatches, matched, compared = compare_constants(measured, constants(mods))

    print("=== kiro-crew-docs SSoT 機械測定 ===")
    print("")
    print(f"スナップショット: {args.snapshot}（ref {pin.get('ref')} / commit {pin.get('commit_short')} / "
          f"参照日 {pin.get('reference_date')}）")
    print("数え方: ファイル数は find -type f 相当の全ファイル（.md 以外も含む）")
    print("")
    print("| ID | 測定値 | 定数 | 定数の値 | 一致 |")
    print("|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    print("")

    rc = 0
    if mismatches:
        print(f"❌ 不一致 {len(mismatches)} 件:")
        for m in mismatches:
            print(f"   - {m}")
        print("")
        if args.expect_constants:
            rc = 1
    else:
        print("✅ 測定値と定数、定数どうしはすべて一致しています")
        print("")
    if args.expect_constants:
        print(f"KCD-SUMMARY: SSoT 一致 {matched}/{compared}")
        print("")

    if args.page_updated_diff or args.expect_ledger_current:
        print("=== 公式ページ台帳と PIN.json の比較（Page updated・.md sha256）===")
        diffs, err = page_updated_diff(pin, ledger_dir)
        if diffs is None:
            print(f"❌ 比較できません（未検証です）: {err}")
            return 1
        print(f"差分: {len(diffs)} 件")
        if diffs:
            print("")
            print("| URL | 台帳（Page updated / sha256） | PIN（Page updated / sha256） | 変化 |")
            print("|---|---|---|---|")
            for d in diffs:
                print("| " + " | ".join(d) + " |")
        print("")
        if args.expect_ledger_current and diffs:
            print("❌ 台帳が PIN.json と一致しません（--expect-ledger-current）")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())

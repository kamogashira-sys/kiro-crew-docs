#!/usr/bin/env python3
"""check-changelog.py - kiro-crew-docs changelog 構造チェック

使用方法:
    ./scripts/kiro-crew-docs/check-changelog.py
    ./scripts/kiro-crew-docs/check-changelog.py --repo-dir <snapshot>/repo
        # CHANGELOG.md / Releases と突き合わせる（任意）

検証内容:
    1. 版見出しの書式（`### vX.Y.Z`）
    2. 版番号が実在する安定版のみであること（プレリリース・Unreleasedを含まない）
    3. **各版にCHANGELOG日付とRelease公開日の2列が両方あること**（Crew固有。
       両者は食い違うため、片方だけの記載は「裁定した」ように読めてしまう）
    4. 目次の降順（新しい版が先）

fail-safe: スナップショットが無い場合は実体との突き合わせをスキップしexit 0。
"""
import argparse
import glob
import os
import re
import sys

DOC_FILE = "kiro-crew-docs/02_update/01_changelog.md"
VALID_STABLE_VERSIONS = ["0.1.0", "0.1.1", "0.1.2", "0.1.3", "0.2.0"]

VERSION_HEAD_RE = re.compile(r'(?m)^### v(\d+\.\d+\.\d+)\s*$')
DATE_ROW_RE = re.compile(r'\|\s*(CHANGELOG\.md|GitHub Release\s*公開日)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|')


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo-dir", help="スナップショット内の repo ディレクトリ（任意）")
    args = ap.parse_args()
    os.chdir(repo_root())

    print("=== kiro-crew-docs changelog 構造チェック ===")
    print("")

    errors, notes = [], []

    if not os.path.isfile(DOC_FILE):
        print(f"⚠️  {DOC_FILE} が未執筆です（Phase 4 で執筆予定）")
        print("✅ 検証対象が無いため exit 0")
        return 0

    txt = open(DOC_FILE, encoding="utf-8").read()

    print("🔍 版見出しの書式と実在性を検証中...")
    versions = VERSION_HEAD_RE.findall(txt)
    for v in versions:
        if v not in VALID_STABLE_VERSIONS:
            errors.append(f"{DOC_FILE}: 存在しない版番号です: v{v}")
    notes.append(f"検出した版見出し: {['v'+v for v in versions]}")

    print("🔍 目次の降順を検証中...")
    order_ok = all(
        VALID_STABLE_VERSIONS.index(versions[i]) > VALID_STABLE_VERSIONS.index(versions[i+1])
        for i in range(len(versions) - 1)
        if versions[i] in VALID_STABLE_VERSIONS and versions[i+1] in VALID_STABLE_VERSIONS
    )
    if versions and not order_ok:
        errors.append(f"{DOC_FILE}: 版見出しが降順（新しい版が先）になっていません: {versions}")
    elif versions:
        notes.append("版見出しは降順（新しい版が先）")

    print("🔍 各版のCHANGELOG日付・Release公開日の2列を検証中...")
    # 版節ごとにスコープを切って両方の日付行があるか確認
    sections = re.split(r'(?m)^### v\d+\.\d+\.\d+\s*$', txt)[1:]  # 先頭は見出し前の文章
    for v, sec in zip(versions, sections):
        # 次の版見出しまでを対象にする（末尾は次のsplitで自動的に切られている）
        rows = DATE_ROW_RE.findall(sec[:500])  # 版節冒頭付近のみ見る
        kinds = {r[0] for r in rows}
        if "CHANGELOG.md" in kinds and "GitHub Release\u3000公開日" in kinds:
            pass  # 両方揃っている（全角スペースの可能性を吸収するため下で再確認）
        has_changelog = bool(re.search(r'CHANGELOG\.md\s*\|\s*\d{4}-\d{2}-\d{2}', sec[:500]))
        has_release = bool(re.search(r'公開日\s*\|\s*\d{4}-\d{2}-\d{2}', sec[:500]))
        if has_changelog and has_release:
            notes.append(f"v{v}: CHANGELOG日付・Release公開日の両方を確認")
        elif has_changelog or has_release:
            errors.append(
                f"v{v}: CHANGELOG日付とRelease公開日が**片方だけ**しか記載されていません"
                "（両方を2列で併記する決まり）"
            )
        else:
            errors.append(f"v{v}: CHANGELOG日付・Release公開日のいずれも見つかりません")

    if args.repo_dir and os.path.isdir(args.repo_dir):
        print(f"🔍 CHANGELOG.md実体との突き合わせ中（{args.repo_dir}）...")
        changelog_path = os.path.join(args.repo_dir, "CHANGELOG.md")
        if os.path.isfile(changelog_path):
            real_txt = open(changelog_path, encoding="utf-8").read()
            real_versions = re.findall(r'(?m)^## \[(\d+\.\d+\.\d+)\]', real_txt)
            missing = [v for v in real_versions if v not in versions and v in VALID_STABLE_VERSIONS]
            if missing:
                notes.append(f"CHANGELOG.md実体にある安定版で本文未反映: {missing}（Phase 4で執筆予定なら問題なし）")
            else:
                notes.append("CHANGELOG.md実体の安定版はすべて本文に反映済み")
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
        print("❌ changelog構造チェックに失敗しました")
        return 1

    print("✅ changelog構造は健全です")
    return 0


if __name__ == "__main__":
    sys.exit(main())

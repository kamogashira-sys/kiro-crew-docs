#!/usr/bin/env python3
"""check-changelog.py - kiro-crew-docs changelog 構造チェック

使用方法:
    ./scripts/kiro-crew-docs/check-changelog.py
    ./scripts/kiro-crew-docs/check-changelog.py --repo-dir <snapshot>/repo
        # CHANGELOG.md / Releases と突き合わせる（任意）
    ./scripts/kiro-crew-docs/check-changelog.py --doc-file <path>
        # 対象changelogを明示して検証する（ネガティブテスト用）

検証内容:
    1. 版見出しの書式（`### vX.Y.Z`）
    2. 版番号が実在する安定版のみであること（プレリリース・Unreleasedを含まない）
    3. 各版にCHANGELOG日付とRelease公開日の2列が両方あること
    4. 目次と本文の版見出しが、ともに降順（新しい版が先）であること
    5. 目次の版リンクが本文版見出しと同じ順序・集合であり、アンカーが対応すること

fail-safe: スナップショットが無い場合は実体との突き合わせをスキップしexit 0。
"""
import argparse
import os
import re
import sys

DOC_FILE = "kiro-crew-docs/02_update/01_changelog.md"
VALID_STABLE_VERSIONS = ["0.1.0", "0.1.1", "0.1.2", "0.1.3", "0.2.0", "0.3.0", "0.4.0", "0.4.1",
                         "0.5.0", "0.6.0"]

VERSION_HEAD_RE = re.compile(r"(?m)^### v(\d+\.\d+\.\d+)\s*$")
DATE_ROW_RE = re.compile(
    r"\|\s*(CHANGELOG\.md|GitHub Release\s*公開日)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|"
)
TOC_SECTION_RE = re.compile(r"(?ms)^## 📑 このページの内容\s*$\n(?P<items>.*?)(?=^---\s*$)")
TOC_VERSION_RE = re.compile(r"(?m)^\s*-\s+\[v(\d+\.\d+\.\d+)\]\(#([^)]+)\)\s*$")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_descending(versions):
    return all(
        VALID_STABLE_VERSIONS.index(versions[i]) > VALID_STABLE_VERSIONS.index(versions[i + 1])
        for i in range(len(versions) - 1)
        if versions[i] in VALID_STABLE_VERSIONS and versions[i + 1] in VALID_STABLE_VERSIONS
    )


def expected_anchor(version):
    return f"v{version.replace('.', '')}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo-dir", help="スナップショット内の repo ディレクトリ（任意）")
    ap.add_argument("--doc-file", default=DOC_FILE, help=f"検証するchangelog（既定: {DOC_FILE}）")
    args = ap.parse_args()
    os.chdir(repo_root())

    print("=== kiro-crew-docs changelog 構造チェック ===")
    print("")

    errors, notes = [], []
    doc_file = args.doc_file

    if not os.path.isfile(doc_file):
        print(f"⚠️  {doc_file} が未執筆です（Phase 4 で執筆予定）")
        print("✅ 検証対象が無いため exit 0")
        return 0

    txt = open(doc_file, encoding="utf-8").read()

    print("🔍 版見出しの書式と実在性を検証中...")
    versions = VERSION_HEAD_RE.findall(txt)
    for version in versions:
        if version not in VALID_STABLE_VERSIONS:
            errors.append(f"{doc_file}: 存在しない版番号です: v{version}")
    notes.append(f"検出した版見出し: {['v' + version for version in versions]}")

    print("🔍 目次・本文の降順、対応、アンカーを検証中...")
    if versions and not is_descending(versions):
        errors.append(f"{doc_file}: 本文版見出しが降順（新しい版が先）になっていません: {versions}")
    elif versions:
        notes.append("本文版見出しは降順（新しい版が先）")

    toc_match = TOC_SECTION_RE.search(txt)
    if not toc_match:
        errors.append(f"{doc_file}: 「## 📑 このページの内容」目次が見つかりません")
    else:
        toc_entries = TOC_VERSION_RE.findall(toc_match.group("items"))
        toc_versions = [version for version, _anchor in toc_entries]
        for version, anchor in toc_entries:
            if version not in VALID_STABLE_VERSIONS:
                errors.append(f"{doc_file}: 目次に存在しない版番号があります: v{version}")
            if anchor != expected_anchor(version):
                errors.append(
                    f"{doc_file}: 目次のv{version}アンカーが本文見出しに対応しません: #{anchor} "
                    f"（期待: #{expected_anchor(version)}）"
                )
        if toc_versions and not is_descending(toc_versions):
            errors.append(f"{doc_file}: 目次の版リンクが降順（新しい版が先）になっていません: {toc_versions}")
        elif toc_versions:
            notes.append("目次の版リンクは降順（新しい版が先）")
        if toc_versions != versions:
            errors.append(
                f"{doc_file}: 目次の版リンクと本文版見出しが順序・集合とも一致しません: "
                f"目次={toc_versions}, 本文={versions}"
            )
        else:
            notes.append("目次の版リンク・アンカーは本文版見出しと対応")

    print("🔍 各版のCHANGELOG日付・Release公開日の2列を検証中...")
    sections = re.split(r"(?m)^### v\d+\.\d+\.\d+\s*$", txt)[1:]
    for version, section in zip(versions, sections):
        has_changelog = bool(re.search(r"CHANGELOG\.md\s*\|\s*\d{4}-\d{2}-\d{2}", section[:500]))
        has_release = bool(re.search(r"公開日\s*\|\s*\d{4}-\d{2}-\d{2}", section[:500]))
        if has_changelog and has_release:
            notes.append(f"v{version}: CHANGELOG日付・Release公開日の両方を確認")
        elif has_changelog or has_release:
            errors.append(
                f"v{version}: CHANGELOG日付とRelease公開日が**片方だけ**しか記載されていません"
                "（両方を2列で併記する決まり）"
            )
        else:
            errors.append(f"v{version}: CHANGELOG日付・Release公開日のいずれも見つかりません")

    if args.repo_dir and os.path.isdir(args.repo_dir):
        print(f"🔍 CHANGELOG.md実体との突き合わせ中（{args.repo_dir}）...")
        changelog_path = os.path.join(args.repo_dir, "CHANGELOG.md")
        if os.path.isfile(changelog_path):
            real_txt = open(changelog_path, encoding="utf-8").read()
            real_versions = re.findall(r"(?m)^## \[(\d+\.\d+\.\d+)\]", real_txt)
            missing = [version for version in real_versions if version not in versions and version in VALID_STABLE_VERSIONS]
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
        for note in notes:
            print(f"   - {note}")
        print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for error in errors:
            print(f"   - {error}")
        print("")
        print("❌ changelog構造チェックに失敗しました")
        return 1

    print("✅ changelog構造は健全です")
    return 0


if __name__ == "__main__":
    sys.exit(main())

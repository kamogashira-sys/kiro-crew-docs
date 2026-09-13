#!/usr/bin/env python3
"""check-structure.py - kiro-crew-docs のディレクトリ・文書構造チェック

使用方法:
    ./scripts/kiro-crew-docs/check-structure.py

検証内容:
    1. 公開5セクションが存在すること
    2. 各セクションに README.md があること（未着手セクションは警告にとどめる）
    3. 各 Markdown が H1 見出しから始まること
    4. 各セクションのファイル軸が計画書 §5 で確定した構成に沿っていること
    5. ローカル管理セクション（05_meta / 06_embedded-docs / work_plans）が
       公開文書から参照されていないこと
    6. 本文ページ（README 以外）の冒頭に「Kiro Crew（OSS）の仕様」の明示があること
    7. 本文ページに出典（kiro.dev の docs、または GitHub の出典）があること
       （Crew は出典が2形式あるため、いずれか一方があればよい）

未執筆のセクションは「まだ執筆されていない」として警告にとどめ、エラーにしない。
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-crew-docs"

PUBLIC_SECTIONS = [
    "00_information",
    "01_features",
    "02_update",
    "03_deployment",
    "04_reference",
]

LOCAL_ONLY = ["05_meta", "06_embedded-docs", "work_plans"]

# 計画書 §5 で確定したファイル軸（Rev 2: 01_features 15ページ / 03_deployment 7ページ）
SECTION_FILES = {
    "00_information": [
        "01_repository-structure.md",
        "02_official-docs-structure.md",
        "03_information-sources.md",
    ],
    "01_features": [
        "01_architecture.md",
        "02_sessions.md",
        "03_chat.md",
        "04_memory-and-learning.md",
        "05_knowledge-library.md",
        "06_autonomy.md",
        "07_agents-skills-steering.md",
        "08_mcp-integration.md",
        "09_security.md",
        "10_apps.md",
        "11_interfaces.md",
        "12_artifacts.md",
        "13_computer-and-browser.md",
        "14_migration-import.md",
        "15_agent-backends.md",
        "16_aws-control.md",
        "17_workflows.md",
    ],
    "02_update": [
        "01_changelog.md",
        "02_release-policy.md",
    ],
    "03_deployment": [
        "01_installation.md",
        "02_windows.md",
        "03_running-24-7.md",
        "04_security-hardening.md",
        "05_troubleshooting.md",
        "06_telemetry-and-privacy.md",
    ],
    "04_reference": [
        "01_cli-commands.md",
        "02_configuration-keys.md",
        "03_directory-layout.md",
        "04_mcp-tools.md",
        "05_limits.md",
    ],
}

LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')

# 本文ページ冒頭で「Kiro Crew（OSS）の仕様」であることを明示する
CREW_SCOPE_RE = re.compile(r"Kiro Crew\s*[（(]OSS|本ページは\s*\*\*Kiro Crew")

# 出典URL: kiro.dev の docs、または GitHub（リポジトリ）のいずれか
SOURCE_URL_RE = re.compile(r"https://kiro\.dev/docs/crew/|https://github\.com/kirodotdev/KiroCrew")

HEAD_LINES = 30


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def strip_code(txt):
    out, in_fence = [], False
    for line in txt.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out.append(re.sub(r"`[^`\n]*`", "", line))
    return "".join(out)


def main():
    os.chdir(repo_root())
    errors, warnings = [], []

    print("=== kiro-crew-docs 構造チェック ===")
    print("")

    print("🔍 公開セクションの存在を検証中...")
    for sec in PUBLIC_SECTIONS:
        path = os.path.join(DOC_ROOT, sec)
        if not os.path.isdir(path):
            errors.append(f"公開セクションがありません: {path}")

    print("🔍 各セクションの README を検証中...")
    written_sections = []
    for sec in PUBLIC_SECTIONS:
        path = os.path.join(DOC_ROOT, sec)
        if not os.path.isdir(path):
            continue
        mds = [f for f in os.listdir(path) if f.endswith(".md")]
        if not mds:
            warnings.append(f"{sec}/ はまだ執筆されていません")
            continue
        if "README.md" not in mds:
            errors.append(f"{sec}/ に README.md がありません（本文が {len(mds)} 件あるのに索引がない）")
        if [f for f in mds if f != "README.md"]:
            written_sections.append(sec)

    print("🔍 各 Markdown の H1 見出しを検証中...")
    docs = sorted(glob.glob(f"{DOC_ROOT}/**/*.md", recursive=True))
    docs = [d for d in docs if not any(f"/{lo}/" in d.replace(os.sep, "/") or
                                       d.replace(os.sep, "/").endswith(f"/{lo}")
                                       for lo in LOCAL_ONLY)]
    for d in docs:
        try:
            with open(d, encoding="utf-8") as f:
                first = next((ln for ln in f if ln.strip()), "")
        except OSError:
            continue
        if not first.startswith("# "):
            errors.append(f"{d}: H1 見出し（`# `）から始まっていません: {first.strip()[:40]!r}")

    print("🔍 各セクションのファイル軸を検証中...")
    for sec, expected in SECTION_FILES.items():
        sec_dir = os.path.join(DOC_ROOT, sec)
        if not os.path.isdir(sec_dir):
            continue
        present = {f for f in os.listdir(sec_dir) if f.endswith(".md")}
        unexpected = present - set(expected) - {"README.md"}
        if unexpected:
            errors.append(
                f"{sec}/ に想定外のファイルがあります: {sorted(unexpected)}"
                f"（計画書 §5 で確定した軸は {expected}）"
            )
        missing = set(expected) - present
        if missing:
            warnings.append(f"{sec}/ の未執筆ファイル: {sorted(missing)}")

    print("🔍 公開文書からのリンク先を検証中...")
    for d in docs:
        try:
            txt = strip_code(open(d, encoding="utf-8").read())
        except OSError:
            continue
        for m in LINK_RE.finditer(txt):
            target = m.group(1).strip()
            norm = target.replace(os.sep, "/")
            if norm.startswith(("http://", "https://")):
                continue
            for lo in LOCAL_ONLY:
                if f"{lo}/" in norm:
                    errors.append(
                        f"{d}: ローカル管理領域へのリンクがあります: '{target}'"
                        f"（{lo}/ は GitHub 非公開のため公開リポジトリから辿れない）"
                    )

    print("🔍 本文ページのスコープ明示と出典を検証中...")
    body_docs = [d for d in docs if os.path.basename(d) != "README.md"]
    for d in body_docs:
        try:
            lines = open(d, encoding="utf-8").read().splitlines()
        except OSError:
            continue
        head = "\n".join(lines[:HEAD_LINES])
        if not CREW_SCOPE_RE.search(head):
            errors.append(
                f"{d}: 冒頭 {HEAD_LINES} 行に「Kiro Crew（OSS）の仕様」の明示がありません"
            )
        if not SOURCE_URL_RE.search(head):
            errors.append(
                f"{d}: 冒頭 {HEAD_LINES} 行に出典がありません"
                "（kiro.dev/docs/crew/ または github.com/kirodotdev/KiroCrew のいずれか）"
            )

    print("")
    print("=== チェック結果 ===")
    print(f"検証した公開 Markdown: {len(docs)} 件（うち本文ページ {len(body_docs)} 件）")
    print(f"本文を執筆済みのセクション: {len(written_sections)} / {len(PUBLIC_SECTIONS)}"
          f"（{', '.join(written_sections) or 'なし'}）")
    print("")

    if warnings:
        print(f"⚠️  警告 {len(warnings)} 件（未執筆。エラーではない）:")
        for w in warnings:
            print(f"   - {w}")
        print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 構造チェックに失敗しました")
        sys.exit(1)

    print("✅ 構造は健全です")
    sys.exit(0)


if __name__ == "__main__":
    main()

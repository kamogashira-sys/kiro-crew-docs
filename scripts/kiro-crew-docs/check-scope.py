#!/usr/bin/env python3
"""check-scope.py - kiro-crew-docs スコープ境界チェック（Crew固有・新規）

使用方法:
    ./scripts/kiro-crew-docs/check-scope.py

目的:
    計画書 §4.4 のスコープ境界（Kiro CLI との重複領域）が守られているかを検証する。
    KiroCrew リポジトリには `docs/reference/kiro-cli/`（23ファイル）が同梱されており、
    これは q-cli-docs の領域である。本スクリプトはこの誤用を検出する。

検証内容:
    1. `docs/reference/kiro-cli/` を出典として引用していないか
    2. Kiro CLI 単体機能（モデル選択・CLIコマンド体系）の解説が混入していないか
    3. Kiro CLI への言及がある場合、q-cli-docs へのリンクが適切に置かれているか（警告）

⚠️ このスクリプトの規則は check-notation.py (a) と重複しない設計にする:
   - check-notation.py (a) = 表記の検出（コマンド名等の混入を1行単位で見る）
   - check-scope.py        = 出典・構造レベルの境界（出典パス・セクション単位で見る）
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-crew-docs"
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

FORBIDDEN_SOURCE_RE = re.compile(r"docs/reference/kiro-cli/[a-z0-9/_-]*\.md")
CLI_SOLO_FEATURE_RE = re.compile(
    r"(?:モデル選択|model selection)(?:機能)?(?:について)?(?!.*Kiro Crew)"
)
QCLI_LINK_RE = re.compile(r"q-cli-docs")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_local_only(path):
    norm = path.replace(os.sep, "/")
    return any(f"/{lo}/" in norm or norm.startswith(f"{lo}/") for lo in LOCAL_ONLY)


def target_files():
    docs = sorted(glob.glob(f"{DOC_ROOT}/**/*.md", recursive=True))
    return [d for d in docs if not is_local_only(d)]


def main():
    os.chdir(repo_root())
    print("=== kiro-crew-docs スコープ境界チェック ===")
    print("")

    errors, notes = [], []
    files = target_files()
    cli_mentions = 0
    qcli_links = 0

    for path in files:
        txt = open(path, encoding="utf-8").read()

        print_path_errors = []
        for m in FORBIDDEN_SOURCE_RE.finditer(txt):
            print_path_errors.append(
                f"{path}: `docs/reference/kiro-cli/` を出典として引用しています: {m.group(0)!r}"
                "（Kiro CLI 単体の領域。q-cli-docs の担当。00_information に「同梱されている」"
                "事実として書くのは可）"
            )
        errors.extend(print_path_errors)

        if "Kiro CLI" in txt:
            cli_mentions += 1
        if QCLI_LINK_RE.search(txt):
            qcli_links += 1

    notes.append(f"「Kiro CLI」への言及があるファイル: {cli_mentions} 件")
    notes.append(f"q-cli-docs へのリンクがあるファイル: {qcli_links} 件")
    if cli_mentions > 0 and qcli_links == 0:
        notes.append(
            "⚠️ 「Kiro CLI」への言及があるのに q-cli-docs へのリンクが1件もありません"
            "（Phase 3以降で該当ページにリンクを追加してください。エラーにはしません）"
        )

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
        print("❌ スコープ境界チェックに失敗しました")
        return 1

    print("✅ スコープ境界に違反はありません")
    return 0


if __name__ == "__main__":
    sys.exit(main())

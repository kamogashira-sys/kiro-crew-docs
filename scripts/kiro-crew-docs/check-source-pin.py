#!/usr/bin/env python3
"""check-source-pin.py - kiro-crew-docs 参照時点記録チェック（Crew固有・新規）

使用方法:
    ./scripts/kiro-crew-docs/check-source-pin.py

目的:
    main ブランチが日次で動く Crew では、GitHub を出典にした記述に
    「参照日・commit SHA・版」の記録が必須（計画書 §4.5）。本スクリプトはこれを検証する。

検証内容:
    1. GitHub blob URL（`github.com/kirodotdev/KiroCrew/blob/main/...`）を出典にした
       記述の近辺に、参照日・commit SHA・版の記録があるか
    2. `docs/request-for-change/`・`docs/ci/`・`docs/build/`・`[Unreleased]` を
       出典にしていないか
    3. **削除済み・移行専用の仕様書を出典にしていないか**
       （`features/claude-code-provider.md`・`post-launch-removals.md` 等）
    4. **旧データホーム `~/.kirocrew` の記載**（現行は `~/.kiro/crew`）
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-crew-docs"
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

GITHUB_BLOB_RE = re.compile(r"github\.com/kirodotdev/KiroCrew/blob/main/[^\s)\"']+")
SHA_RE = re.compile(r"commit\s*`[0-9a-f]{7}`")
REF_DATE_RE = re.compile(r"参照[:：]\s*\d{4}-\d{2}-\d{2}")
VERSION_RE = re.compile(r"版\s*v\d+\.\d+\.\d+")

FORBIDDEN_SOURCE_PATHS = [
    (re.compile(r"docs/request-for-change/"), "RFC（未確定の将来仕様）"),
    (re.compile(r"docs/ci/"), "CI（開発者向け）"),
    (re.compile(r"docs/build/"), "ビルド（開発者向け）"),
    (re.compile(r"\[Unreleased\]"), "未リリースのCHANGELOG節"),
]

REMOVED_SPEC_FILES = [
    (re.compile(r"post-launch-removals\.md"), "移行専用の仕様書（旧データホームの記述を含む）"),
]
# ⚠️ v0.6.0 で claude-code-provider.md を本リストから外した（D-8）。
#    v0.4.1 の docs/system-specs/features/claude-code-provider.md はタイトルが
#    「# Standalone provider — removed」で削除済み機能の記録だったが、
#    v0.6.0 の docs/system-specs/modules/claude-code-provider.md は
#    「# Claude Code provider — a selectable ACP harness」＝現行機能（Agent Backends）の
#    仕様書に変わったため、出典として使える（commit 8575209 で確認）。

LEGACY_DATA_HOME_RE = re.compile(r"~/\.kirocrew\b(?!/)")
# ただし「post-launch-removals.md の言及として~/.kirocrewは現行では使わない」という
# 事実を書く場合は許容する（否定文脈）
LEGACY_OK_CONTEXT_RE = re.compile(r"現行では使わない|レガシー|移行済み|旧パス|使わない|Legacy|移行専用|delete予定|削除予定")


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
    print("=== kiro-crew-docs 参照時点記録チェック ===")
    print("")

    errors, notes = [], []
    files = target_files()
    github_refs = 0
    github_refs_pinned = 0

    for path in files:
        lines = open(path, encoding="utf-8").read().splitlines()
        # 「## 関連リンク」以降は参考リンク集であり、本文の主張の裏付けではないため
        # 参照時点記録の必須対象から除外する（冒頭の出典欄とは別の扱い）
        related_links_start = len(lines)
        for idx, l in enumerate(lines):
            if re.match(r"^##\s*関連リンク", l):
                related_links_start = idx
                break

        for i, line in enumerate(lines):
            in_related_links = i >= related_links_start
            if GITHUB_BLOB_RE.search(line) and not in_related_links:
                github_refs += 1
                # 同じ行か次の1行以内にSHA・参照日・版のいずれかがあるかを確認
                window = "\n".join(lines[i:i+2])
                has_sha = bool(SHA_RE.search(window))
                has_date = bool(REF_DATE_RE.search(window))
                has_version = bool(VERSION_RE.search(window))
                if has_sha or has_date or has_version:
                    github_refs_pinned += 1
                else:
                    errors.append(
                        f"{path}:{i+1} GitHub出典に参照日・commit SHA・版のいずれも"
                        "見つかりません（GitHub blob URLの近辺に記録が必要）"
                    )

            for pat, label in FORBIDDEN_SOURCE_PATHS:
                if pat.search(line):
                    # 「出典にしない」という方針の説明・件数や存在を述べる事実記述は許容する。
                    # 実際に出典として引用している文脈（「出典:」直後にこのパスがある等）のみを検出する。
                    if re.search(r"出典にしない|出典としない|出典から除外|扱わない|未確定|未リリース"
                                 r"|開発者向け|版節数|節が|の節|存在|件\)|件）", line):
                        continue
                    if re.search(r"出典[:：]|出典として|出典にしている|参照:", line):
                        errors.append(
                            f"{path}:{i+1} 出典にしてはいけないパスへの参照があります: "
                            f"{label}（{pat.pattern}）"
                        )

            for pat, label in REMOVED_SPEC_FILES:
                m = pat.search(line)
                if m:
                    # 「出典として引用」ではなく「削除された事実を書く」文脈は許容する
                    if re.search(r"削除済み|出典にしない|removed|no longer exist|削除予定|移行専用|台帳", line):
                        notes.append(f"{path}:{i+1} 削除済み仕様書への言及（削除の事実として許容）: {label}")
                    else:
                        errors.append(
                            f"{path}:{i+1} 削除済み・移行専用の仕様書を出典にしている疑いがあります: "
                            f"{label}"
                        )

            m = LEGACY_DATA_HOME_RE.search(line)
            if m and not LEGACY_OK_CONTEXT_RE.search(line):
                errors.append(
                    f"{path}:{i+1} 旧データホーム `~/.kirocrew` が現行パスのように書かれています"
                    "（現行は `~/.kiro/crew`。post-launch-removals.md の移行専用記述を"
                    "誤って引用した可能性）"
                )

    notes.append(f"GitHub blob URL出典: {github_refs} 件（うち参照時点記録あり: {github_refs_pinned} 件）")

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
        print("❌ 参照時点記録チェックに失敗しました")
        return 1

    print("✅ 参照時点記録に問題はありません")
    return 0


if __name__ == "__main__":
    sys.exit(main())

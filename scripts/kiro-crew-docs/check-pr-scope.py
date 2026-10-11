#!/usr/bin/env python3
"""check-pr-scope.py - PR の変更範囲が許可パス・許可行に収まっているかを検証する（作業計画書 P-5）

使用方法:
    ./scripts/kiro-crew-docs/check-pr-scope.py --base origin/main --profile version-update
        # 作業ツリー（未コミット・未追跡かつ非除外を含む）を BASE と比べる
    ./scripts/kiro-crew-docs/check-pr-scope.py --base ab81f0e^ --head ab81f0e --profile version-update
        # コミット範囲を比べる（過去コミットでの回帰試験用）
    make check-kiro-crew-pr-scope BASE=origin/main PROFILE=version-update [HEAD_REV=<rev>]

比較の起点:
    BASE と比較先（HEAD_REV または HEAD）の merge-base を起点にする（main が進んだ後も、PR 自身の変更だけを見るため）。
    --head 指定時に BASE が HEAD_REV の祖先であれば、BASE..HEAD_REV と同じ範囲になる。
    リネームは削除＋追加として扱う（--no-renames。旧パス・新パスの両方を判定する）。

プロファイル:
    version-update  版更新 PR 用。差分ファイルが次に限られること:
                    kiro-crew-docs/0[0-4]_*/**・kiro-crew-docs/README.md・README.md・
                    .github/release-notes/v*.md・.github/UPDATE_GUIDE.md・scripts/kiro-crew-docs/ledgers/**、
                    および scripts/kiro-crew-docs/check-*.py。check-*.py は変更行（git diff -U0 の追加・削除行。
                    追加行は変更後、削除行は変更前のファイルで判定）がすべて次のいずれかに収まること:
                      (i)   許可定数（ALLOWED_CONSTANTS）のトップレベル代入文の行範囲（ast の Assign／AnnAssign）
                      (ii)  モジュール docstring の行範囲
                      (iii) tokenize で COMMENT トークンだけから成る行（文字列リテラル内の # 行は含まれない）
                    ただし (i)(ii) の行範囲のうち、ほかのトップレベル文（許可定数の代入文・モジュール docstring 以外）と
                    重なる行は除く（例: `EXPECTED_MODULES = 104; print(...)` の行は許可しない）。
                    .github/WORKFLOW.md・.github/COMMIT_CHECKLIST.md・.github/workflows/*.yml・Makefile は許可しない
                    （CI・Release・検証の手順という安全装置を版更新 PR で変えないため）。
    infra           PR-1〜PR-4 用。上記に加えて scripts/kiro-crew-docs/**・Makefile・.github/**・AGENTS.md・
                    .kiro/workflows/**・.gitignore を許可する（check-*.py の行の制約も掛けない）。

終了コード: 0 = 範囲内 / 1 = 範囲外の変更あり、または引数の誤り（--profile 未指定を含む）
"""
import argparse
import ast
import io
import os
import re
import subprocess
import sys
import tokenize

# D-9 の許可定数（17件。ファイル名と定数名の組）。版更新 PR が変えてよいトップレベル定数の全体
ALLOWED_CONSTANTS = {
    ("check-changelog.py", "VALID_STABLE_VERSIONS"),
    ("check-notation.py", "VALID_STABLE_VERSIONS"),
    ("check-notation.py", "ALLOWED_CLI_COMMANDS"),
    ("check-notation.py", "DENIED_CLI_COMMANDS"),
    ("check-counts.py", "SSOT"),
    ("check-counts.py", "SECTIONS"),
    ("check-counts.py", "TOTAL_PAGES"),
    ("check-coverage.py", "EXPECTED_OFFICIAL_PAGES"),
    ("check-coverage.py", "EXPECTED_MODULES"),
    ("check-freshness.py", "KNOWN_LATEST_STABLE"),
    ("check-freshness.py", "KNOWN_STABLE_COUNT"),
    ("check-freshness.py", "KNOWN_CREW_PAGES"),
    ("check-freshness.py", "KNOWN_DOCS_FILES"),
    ("check-consistency.py", "DUAL_NOTATION"),
    ("check-consistency.py", "SSOT"),
    ("check-structure.py", "SECTION_FILES"),
    ("check-source-pin.py", "REMOVED_SPEC_FILES"),
}

VERSION_UPDATE_PATHS = (
    "kiro-crew-docs/0[0-4]_*/**",
    "kiro-crew-docs/README.md",
    "README.md",
    ".github/release-notes/v*.md",
    ".github/UPDATE_GUIDE.md",
    "scripts/kiro-crew-docs/ledgers/**",
)
CHECK_SCRIPT_GLOB = "scripts/kiro-crew-docs/check-*.py"
INFRA_EXTRA_PATHS = (
    "scripts/kiro-crew-docs/**",
    "Makefile",
    ".github/**",
    "AGENTS.md",
    ".kiro/workflows/**",
    ".gitignore",
)

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} が失敗しました: {r.stderr.strip()}")
    return r.stdout


def path_match(path, pattern):
    """`**` を「0階層以上」、`*` を「1階層内」として照合する。"""
    rx = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            rx += ".*"
            i += 2
        elif pattern[i] == "*":
            rx += "[^/]*"
            i += 1
        elif pattern[i] == "[":
            j = pattern.index("]", i)
            rx += pattern[i:j + 1]  # 文字クラス（例: [0-4]）はそのまま使う
            i = j + 1
        else:
            rx += re.escape(pattern[i])
            i += 1
    return re.fullmatch(rx, path) is not None


def matches_any(path, patterns):
    return any(path_match(path, p) for p in patterns)


def allowed_lines(source, filename):
    """(i)〜(iii) に当たる行番号の集合を返す。構文解析できなければ None。"""
    if source is None:
        return set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    lines = set()
    other = set()  # (i)(ii) 以外のトップレベル文が占める行（同じ物理行に置いた別の文を許可しないため）
    docstring = tree.body[0] if tree.body and isinstance(tree.body[0], ast.Expr) \
        and isinstance(getattr(tree.body[0], "value", None), ast.Constant) \
        and isinstance(tree.body[0].value.value, str) else None
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = {t.id for t in targets if isinstance(t, ast.Name)}
            if any((filename, n) in ALLOWED_CONSTANTS for n in names):
                lines.update(range(node.lineno, node.end_lineno + 1))
                continue
        if node is docstring:
            lines.update(range(node.lineno, node.end_lineno + 1))
            continue
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        other.update(range(start, node.end_lineno + 1))
    lines -= other
    kinds = {}
    ignore = {tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type in ignore:
                continue
            for ln in range(tok.start[0], tok.end[0] + 1):
                kinds.setdefault(ln, set()).add(tok.type)
    except (tokenize.TokenError, IndentationError):
        return None
    lines.update(ln for ln, ks in kinds.items() if ks == {tokenize.COMMENT})
    return lines


def changed_line_numbers(diff_text):
    """git diff -U0 から（削除行の旧行番号, 追加行の新行番号）を返す。"""
    removed, added = [], []
    for line in diff_text.splitlines():
        m = HUNK_RE.match(line)
        if not m:
            continue
        a, b = int(m.group(1)), int(m.group(2) or "1")
        c, d = int(m.group(3)), int(m.group(4) or "1")
        removed.extend(range(a, a + b))
        added.extend(range(c, c + d))
    return removed, added


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="origin/main", help="比較の基準（既定 origin/main）")
    ap.add_argument("--head", help="比較先のコミット（未指定なら作業ツリー）")
    ap.add_argument("--profile", help="version-update または infra（必須）")
    args = ap.parse_args()
    os.chdir(repo_root())

    print("=== kiro-crew-docs PR 変更範囲チェック ===")
    print("")
    if args.profile not in ("version-update", "infra"):
        print(f"❌ --profile は version-update または infra を指定してください（指定: {args.profile!r}）")
        return 1

    try:
        head = args.head or "HEAD"
        base = git("merge-base", args.base, head).strip()
        if args.head:
            names = git("diff", "--no-renames", "--name-only", base, args.head).split()
            new_rev = args.head
        else:
            names = git("diff", "--no-renames", "--name-only", base).split()
            names += git("ls-files", "-o", "--exclude-standard").split()
            new_rev = None
    except RuntimeError as e:
        print(f"❌ {e}")
        return 1
    names = sorted(set(names))
    target = f"{args.base}（merge-base {base[:7]}）..{args.head or '作業ツリー'}"
    print(f"比較: {target} / プロファイル: {args.profile}")
    print(f"差分ファイル: {len(names)} 件")
    print("")

    violations = []
    for path in names:
        if args.profile == "infra" and (matches_any(path, VERSION_UPDATE_PATHS)
                                        or path_match(path, CHECK_SCRIPT_GLOB)
                                        or matches_any(path, INFRA_EXTRA_PATHS)):
            print(f"  OK   {path}")
            continue
        if args.profile == "version-update" and matches_any(path, VERSION_UPDATE_PATHS):
            print(f"  OK   {path}")
            continue
        if args.profile == "version-update" and path_match(path, CHECK_SCRIPT_GLOB):
            filename = os.path.basename(path)
            old_src = git("show", f"{base}:{path}", check=False) or None
            if new_rev:
                new_src = git("show", f"{new_rev}:{path}", check=False) or None
                diff = git("diff", "--no-renames", "-U0", base, new_rev, "--", path)
            else:
                new_src = open(path, encoding="utf-8").read() if os.path.isfile(path) else None
                if git("ls-files", "--error-unmatch", path, check=False):
                    diff = git("diff", "--no-renames", "-U0", base, "--", path)
                else:  # 未追跡の新規ファイル: 全行が追加行
                    n = len((new_src or "").splitlines())
                    diff = f"@@ -0,0 +1,{n} @@" if n else ""
            removed, added = changed_line_numbers(diff)
            old_ok, new_ok = allowed_lines(old_src, filename), allowed_lines(new_src, filename)
            if old_ok is None or new_ok is None:
                violations.append(f"{path}: 構文解析できないため変更行を判定できません")
                print(f"  FAIL {path}（構文解析できない）")
                continue
            bad_removed = [n for n in removed if n not in old_ok]
            bad_added = [n for n in added if n not in new_ok]
            if bad_removed or bad_added:
                violations.append(
                    f"{path}: 許可定数の代入文・モジュール docstring・コメントだけの行の外を変更しています"
                    f"（削除行（変更前）{bad_removed[:10]}{' …' if len(bad_removed) > 10 else ''} / "
                    f"追加行（変更後）{bad_added[:10]}{' …' if len(bad_added) > 10 else ''}）")
                print(f"  FAIL {path}（許可外の行を変更）")
            else:
                print(f"  OK   {path}（変更行 削除 {len(removed)}・追加 {len(added)} がすべて許可範囲内）")
            continue
        violations.append(f"{path}: プロファイル {args.profile} の許可パス外です")
        print(f"  FAIL {path}（許可パス外）")

    print("")
    if violations:
        print(f"❌ 範囲外の変更 {len(violations)} 件:")
        for v in violations:
            print(f"   - {v}")
        return 1
    print("✅ すべての変更が許可範囲内です")
    return 0


if __name__ == "__main__":
    sys.exit(main())

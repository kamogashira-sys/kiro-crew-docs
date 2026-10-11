#!/usr/bin/env bash
# check-pr-body.sh - 公開される PR 本文の公開前検査（作業計画書 P-11）
#
# 使用方法:
#   scripts/kiro-crew-docs/check-pr-body.sh <pr-body.md> [--snapshot <dir>]
#   make check-kiro-crew-pr-body PR_BODY=<pr-body.md> CLOUD_ROOT=<一次情報のルート>
#
# 検出したら exit 1（check-ignore.sh はリポジトリのファイルしか走査しないため、PR 本文は別に検査する）:
#   - ローカル絶対パス（/home/<user>・/Users/<user>。/home/kirocrew は check-ignore.sh と同じく除外）
#   - GitHub トークンの書式（gh + p/o/s + "_"、github + "_pat_"）と PEM 秘密鍵の見出し
#   - --snapshot 指定時: 本文のコードブロック内の連続5行が、スナップショットの repo/ 配下・docs_md/ 配下の
#     いずれかのファイルの連続5行と一致する転記（行末の空白は無視。5行すべてが空行の窓は数えない）
#
# 表示は行番号と種別だけで、一致した値を出力しない。
# PR 本文が無い、--snapshot の repo/ と docs_md/ がどちらも無い、repo/・docs_md/ に照合できるファイルが
# 1件も無い（取得失敗後に残った空のディレクトリ等）場合は、検査を行わずに exit 1。
set -uo pipefail

usage() { echo "使い方: $0 <pr-body.md> [--snapshot <dir>]" >&2; }

BODY=""
SNAPSHOT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --snapshot) SNAPSHOT="${2:-}"; [ -z "$SNAPSHOT" ] && { usage; exit 1; }; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "❌ 不明なオプション: $1" >&2; usage; exit 1 ;;
    *) if [ -n "$BODY" ]; then usage; exit 1; fi; BODY="$1"; shift ;;
  esac
done

echo "=== PR 本文の公開前検査 ==="
if [ -z "$BODY" ] || [ ! -f "$BODY" ]; then
  echo "❌ PR 本文 ${BODY:-（未指定）} がありません。検査を行いませんでした"
  exit 1
fi

python3 - "$BODY" "$SNAPSHOT" <<'PY'
import os
import re
import sys

body_path, snapshot = sys.argv[1], sys.argv[2]
lines = open(body_path, encoding="utf-8", errors="replace").read().split("\n")

# check-ignore.sh と同じパターン。本スクリプト自身が一致しないよう文字クラスで書く
PATTERNS = [
    ("ローカル絶対パス", re.compile(r"/home/[a-z_][a-z0-9_-]*|/Users/[A-Za-z0-9_-]+"),
     re.compile(r"(^|[^a-z0-9_-])home/kirocrew([^a-z0-9_-]|$)")),
    ("トークンの書式", re.compile(r"gh[pos]_|github[_]pat_"), None),
    ("秘密鍵の書式", re.compile(r"-----BEGIN [A-Z ]*PRIVATE[ ]KEY-----"), None),
]

findings = []
for i, line in enumerate(lines, 1):
    for kind, pat, allow in PATTERNS:
        if pat.search(line) and not (allow and allow.search(line)):
            findings.append((i, kind))

WINDOW = 5
checked_snapshot = False
if snapshot:
    roots = [os.path.join(snapshot, d) for d in ("repo", "docs_md")]
    roots = [r for r in roots if os.path.isdir(r)]
    if not roots:
        print(f"❌ --snapshot {snapshot} に repo/・docs_md/ がありません。検査を行いませんでした")
        sys.exit(1)
    windows = set()
    nfiles = 0
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                try:
                    text = open(os.path.join(dirpath, name), encoding="utf-8").read()
                except (UnicodeDecodeError, OSError):
                    continue  # バイナリ等は対象外
                nfiles += 1
                flines = [x.rstrip() for x in text.split("\n")]
                for k in range(len(flines) - WINDOW + 1):
                    w = tuple(flines[k:k + WINDOW])
                    if any(w):
                        windows.add(w)
    if nfiles == 0:
        # 0ファイルとの照合を「検査済み」にしない（フェイルクローズド）
        print(f"❌ --snapshot {snapshot} の repo/・docs_md/ に照合できるファイルが0件です（取得に失敗した可能性）。検査を行いませんでした")
        sys.exit(1)
    # 本文のコードブロック内の行を、ブロックごとに（開始行番号, 行）で集める
    blocks, cur, in_fence = [], None, False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            if in_fence:
                blocks.append(cur)
                cur, in_fence = None, False
            else:
                cur, in_fence = [], True
            continue
        if in_fence:
            cur.append((i, line.rstrip()))
    if in_fence and cur:
        blocks.append(cur)
    for block in blocks:
        for k in range(len(block) - WINDOW + 1):
            w = tuple(x for _, x in block[k:k + WINDOW])
            if any(w) and w in windows:
                findings.append((block[k][0], f"上流文書の連続{WINDOW}行の転記（{block[k][0]}〜{block[k + WINDOW - 1][0]}行）"))
    checked_snapshot = True
    print(f"上流文書との照合: スナップショットの {nfiles} ファイルと照合（コードブロック {len(blocks)} 個）")
else:
    print("（--snapshot 未指定のため、上流文書の転記は検査していません）")

if findings:
    print(f"❌ 公開してはいけない記述が {len(findings)} 件あります（値は表示しません）:")
    seen = set()
    for i, kind in findings:
        if (i, kind) in seen:
            continue
        seen.add((i, kind))
        print(f"   - {i}行: {kind}")
    sys.exit(1)

print("✅ PR 本文に公開してはいけない記述はありません"
      + ("（上流文書の転記も検査済み）" if checked_snapshot else ""))
PY

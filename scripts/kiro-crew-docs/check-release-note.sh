#!/usr/bin/env bash
# check-release-note.sh - リリースノート（.github/release-notes/vX.Y.Z.md）の版の4者一致を検査する
#
# 使用方法:
#   scripts/kiro-crew-docs/check-release-note.sh <note>
#   scripts/kiro-crew-docs/check-release-note.sh --print-readme-version
#   make check-kiro-crew-release-note NOTE=.github/release-notes/vX.Y.Z.md
#
# 検査内容（<note> を渡した場合）:
#   次の4つの版がすべて一致すれば exit 0、1つでも異なる・抽出できなければ exit 1。
#     ① ファイル名の版        : <note> のファイル名が vX.Y.Z.md（プレリリースの -rc.N 等は不可）
#     ② H1 の先頭の版         : 1行目が「# vX.Y.Z — <内容>」（1行目を Release のタイトルにするため）
#     ③ README の固定版       : ルート README.md の「更新範囲と参照時点」表の「固定時点の最新安定版」行
#     ④ changelog の先頭の版  : kiro-crew-docs/02_update/01_changelog.md の最初の「### vX.Y.Z」見出し
#   <note> はリポジトリの外（/tmp など）にあってもよい。③④は常にこのリポジトリの作業ツリーから読む。
#
# --print-readme-version:
#   ③の版だけを1行で出力して exit 0（抽出できなければ exit 1）。CI の一次情報取得（VERSION の決定）と
#   Kiro Web Workflow の detect が同じ関数 readme_fixed_version を使う。
#
# 呼び出し元: validate CI の PR 実行（マージ前）、Kiro Web Workflow の converge（マージ前）、
#             Release ワークフローのゲート（マージ後）。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
README="$REPO_ROOT/README.md"
CHANGELOG="$REPO_ROOT/kiro-crew-docs/02_update/01_changelog.md"
VERSION_RE='v[0-9]+\.[0-9]+\.[0-9]+'

usage() {
  echo "使用方法: $0 <note> | --print-readme-version" >&2
}

# ルート README.md の「| 固定時点の最新安定版 | `vX.Y.Z` |」から版を抽出する。該当行がちょうど1行でなければ失敗
readme_fixed_version() {
  local rows n
  rows=$(grep -E '^\|[[:space:]]*固定時点の最新安定版[[:space:]]*\|' "$README" 2>/dev/null || true)
  n=$(printf '%s' "$rows" | grep -c . || true)
  if [ "$n" -ne 1 ]; then
    echo "❌ README.md の「固定時点の最新安定版」行が ${n} 行です（1行である必要があります）" >&2
    return 1
  fi
  local v
  v=$(printf '%s\n' "$rows" | grep -oE "\`${VERSION_RE}\`" | head -1 | tr -d '`')
  if [ -z "$v" ]; then
    echo "❌ README.md の「固定時点の最新安定版」行から vX.Y.Z を抽出できません" >&2
    return 1
  fi
  printf '%s\n' "$v"
}

# changelog の最初の「### vX.Y.Z」見出しの版
changelog_top_version() {
  local v
  v=$(grep -m1 -oE "^### ${VERSION_RE}[[:space:]]*$" "$CHANGELOG" 2>/dev/null | sed -E 's/^### //; s/[[:space:]]+$//')
  if [ -z "$v" ]; then
    echo "❌ $CHANGELOG に「### vX.Y.Z」見出しがありません" >&2
    return 1
  fi
  printf '%s\n' "$v"
}

if [ "$#" -ne 1 ]; then
  usage
  exit 1
fi

if [ "$1" = "--print-readme-version" ]; then
  readme_fixed_version || exit 1
  exit 0
fi

case "$1" in
  -h|--help) usage; exit 0 ;;
  -*) echo "❌ 不明なオプション: $1" >&2; usage; exit 1 ;;
esac

NOTE="$1"
if [ ! -f "$NOTE" ]; then
  echo "❌ リリースノート $NOTE がありません" >&2
  exit 1
fi

echo "=== kiro-crew-docs リリースノートの版の4者一致チェック ==="
echo "対象: $NOTE"
fail=0

base=$(basename "$NOTE")
if [[ "$base" =~ ^(${VERSION_RE})\.md$ ]]; then
  v_file="${BASH_REMATCH[1]}"
else
  v_file=""
  echo "❌ ① ファイル名が vX.Y.Z.md の形式ではありません: $base"
  fail=1
fi

h1=$(head -1 "$NOTE")
if [[ "$h1" =~ ^#\ (${VERSION_RE})\ —\ [^[:space:]].*$ ]]; then
  v_h1="${BASH_REMATCH[1]}"
else
  v_h1=""
  echo "❌ ② 1行目が「# vX.Y.Z — <内容>」の形式ではありません（.github/WORKFLOW.md §8 のタイトル形式）"
  fail=1
fi

v_readme=$(readme_fixed_version) || { v_readme=""; fail=1; }
v_changelog=$(changelog_top_version) || { v_changelog=""; fail=1; }

echo "   ① ファイル名の版       : ${v_file:-（抽出できません）}"
echo "   ② H1 の先頭の版        : ${v_h1:-（抽出できません）}"
echo "   ③ README の固定版      : ${v_readme:-（抽出できません）}"
echo "   ④ changelog の先頭の版 : ${v_changelog:-（抽出できません）}"

if [ "$fail" -eq 0 ]; then
  if [ "$v_file" = "$v_h1" ] && [ "$v_file" = "$v_readme" ] && [ "$v_file" = "$v_changelog" ]; then
    echo "✅ 4者が一致しています: $v_file"
    exit 0
  fi
  echo "❌ 4者が一致しません"
fi
echo "❌ リリースノートの版の4者一致チェックに失敗しました"
exit 1

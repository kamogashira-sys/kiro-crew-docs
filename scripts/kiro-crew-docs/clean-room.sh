#!/usr/bin/env bash
# clean-room.sh - 公開されるファイルだけの複製で make ターゲットを実行する
#
# 使用方法:
#   scripts/kiro-crew-docs/clean-room.sh <make ターゲット・変数>...
#   make check-kiro-crew-cleanroom TARGETS="check-kiro-crew-ignore check-kiro-crew-all" [ARGS="VAR=val ..."]
#
# 目的:
#   クラウドセッション（GitHub からの clone 直後）と同じ条件、つまり
#   「.gitignore で除外されたローカル管理領域（05_meta/・06_embedded-docs/・work_plans/ 等）が
#   無い状態」をローカルで再現し、その状態で検証が通るか（または想定どおり失敗するか）を確かめる。
#   未コミットの変更も含めて複製するため、コミット前に確認できる。
#
# 処理:
#   1. 複製対象 = git ls-files -co --exclude-standard（追跡＋未追跡かつ非除外）
#   2. /tmp/kcd-cleanroom.XXXX へ cp --parents で複製し、複製した件数と複製対象の件数を照合
#      （不一致なら exit 1。複製の取りこぼしによる偽の合格を防ぐ）
#   3. ローカル管理領域が複製先に無いことを ls で表示（あれば exit 1）
#   4. 複製先で git init -q && git add -A（check-ignore.sh が git ls-files を使うため）
#   5. 複製先で make <引数> を実行し、その終了コードを返す。複製先は終了時に必ず削除する
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT" || exit 1

if [ "$#" -eq 0 ]; then
  echo "使い方: $0 <make ターゲット・変数>..." >&2
  exit 1
fi

dst=$(mktemp -d /tmp/kcd-cleanroom.XXXX) || exit 1
cleanup() { rm -rf "$dst"; }
trap cleanup EXIT

echo "=== クリーンルームの作成（公開されるファイルだけを複製） ==="
expected=$(git ls-files -co --exclude-standard | wc -l)
if ! git ls-files -co --exclude-standard -z | xargs -0 cp --parents -t "$dst"; then
  echo "  FAIL 複製に失敗しました"
  exit 1
fi
copied=$( (cd "$dst" && find . \( -type f -o -type l \) | wc -l) )
echo "  複製対象: ${expected} 件 / 複製した件数: ${copied} 件"
if [ "$expected" -ne "$copied" ]; then
  echo "  FAIL 複製対象と複製した件数が一致しません（取りこぼしの可能性）"
  exit 1
fi

echo "=== ローカル管理領域が複製先に無いことを確認 ==="
absent_fail=0
for p in kiro-crew-docs/05_meta kiro-crew-docs/06_embedded-docs kiro-crew-docs/work_plans work_records; do
  if ls -d "$dst/$p" >/dev/null 2>&1; then
    echo "  FAIL present: $p"
    absent_fail=1
  else
    echo "  OK   absent:  $p"
  fi
done
if [ "$absent_fail" -ne 0 ]; then
  exit 1
fi

(cd "$dst" && git init -q && git add -A) || { echo "  FAIL git init / add に失敗しました"; exit 1; }

echo "=== クリーンルームで make $* を実行 ==="
make -C "$dst" --no-print-directory "$@"
rc=$?
echo "=== クリーンルームの結果: exit ${rc} ==="
exit "$rc"

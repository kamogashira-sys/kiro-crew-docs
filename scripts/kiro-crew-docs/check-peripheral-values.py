#!/usr/bin/env python3
"""check-peripheral-values.py - 周辺ファイル（.github/・Makefile）に版依存の値が無いことを検証する

使用方法:
    ./scripts/kiro-crew-docs/check-peripheral-values.py
    make check-kiro-crew-peripheral-values

目的:
    版更新 PR（check-pr-scope.py --profile version-update）は .github/（release-notes と
    UPDATE_GUIDE.md を除く）・Makefile を変更できない。これらのファイルに版で変わる値
    （公式ページ数など）を書くと、値が変わる版で「定数を直すと consistency が失敗し、
    周辺ファイルを直すと pr-scope が失敗する」状態になる。そこで周辺ファイルには
    値を書かない規則とし、本スクリプトで再混入を検出する。

検査内容:
    check-consistency.py の ssot_scan_targets() が返すファイルのうち、kiro-crew-docs/ 配下の
    文書とルート README.md を除いたもの（.github/**/*.md・.github/workflows/*.yml・Makefile）に、
    同スクリプトの SSOT 全件の pattern・extra_patterns を当てる。一致が1件でもあれば
    「ファイル:行: S-ID」を表示して exit 1。値が SSoT と一致していても失敗にする
    （check-consistency.py は値が一致すれば合格にするが、周辺ファイルでは値を書くこと自体を禁止する）。
    最終行に「周辺ファイルの版依存値 N件」を出す。

check-consistency.py の読み込み:
    importlib ではなくソースを compile/exec で読む（同じ秒・同じサイズの編集と復元の後に
    __pycache__ の古いバイトコードが読まれるため。measure-ssot.py と同じ方式）。
"""
import os
import sys
import types

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
CONSISTENCY = os.path.join(SCRIPTS_DIR, "check-consistency.py")


def repo_root():
    return os.path.abspath(os.path.join(SCRIPTS_DIR, "..", ".."))


def load_consistency():
    mod = types.ModuleType("kcd_consistency")
    mod.__file__ = CONSISTENCY
    exec(compile(open(CONSISTENCY, encoding="utf-8").read(), CONSISTENCY, "exec"), mod.__dict__)
    return mod


def peripheral_targets(mod):
    """ssot_scan_targets() から kiro-crew-docs/ 配下とルート README.md を除く。"""
    out = []
    for path in mod.ssot_scan_targets():
        norm = os.path.normpath(path).replace(os.sep, "/")
        if norm.startswith(f"{mod.DOC_ROOT}/") or norm == "README.md":
            continue
        out.append(norm)
    return out


def main():
    os.chdir(repo_root())
    mod = load_consistency()
    targets = peripheral_targets(mod)

    print("=== kiro-crew-docs 周辺ファイルの版依存値チェック ===")
    print("")
    print(f"検査ファイル: {len(targets)} 件（check-consistency.py の ssot_scan_targets() から"
          f" {mod.DOC_ROOT}/ 配下とルート README.md を除いたもの）")
    for t in targets:
        print(f"   - {t}")
    print(f"検査パターン: check-consistency.py の SSOT {len(mod.SSOT)} 件（pattern・extra_patterns）")
    print("")

    hits = []
    for path in targets:
        txt = open(path, encoding="utf-8").read()
        for s in mod.SSOT:
            for pat in [s["pattern"]] + s.get("extra_patterns", []):
                for m in pat.finditer(txt):
                    line_no = txt.count("\n", 0, m.start()) + 1
                    hits.append((path, line_no, s["id"]))
    hits = sorted(set(hits))

    if hits:
        print(f"❌ 周辺ファイルに版依存の値があります（値が SSoT と一致していても書かない規則です）:")
        for path, line_no, sid in hits:
            print(f"   {path}:{line_no}: {sid}")
        print("")
        print("   → 件数・版番号を書かず、数え方と正本（検証器の定数・公開ページ・.github/UPDATE_GUIDE.md）の参照に置き換えてください")
        print("")
    else:
        print("✅ 周辺ファイルに版依存の値はありません")
        print("")
    print(f"KCD-SUMMARY: 周辺ファイルの版依存値 {len(hits)}件")
    print(f"周辺ファイルの版依存値 {len(hits)}件")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())

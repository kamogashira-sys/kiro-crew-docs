# kiro-crew-docs

猫でもわかるKiro Crew — Kiro Crew（OSS）の主要機能を日本語で解説する非公式ドキュメントサイト。

## ここから読む

→ **[kiro-crew-docs/](kiro-crew-docs/)**

目的別の入口・セクション構成は [kiro-crew-docs/README.md](kiro-crew-docs/README.md) を参照してください。

## 機械検証

```bash
make check-kiro-crew-all
```

内部リンク・出典・SSoT（正準値）の一致・表記規約・公式43ページの網羅性・changelog構造・スコープ境界・参照時点記録をローカルで機械検証します。利用可能な個別ターゲットは `make`（引数なし）で確認できます。

> ⚠️ `check-kiro-crew-all` の exit 0 は「全部を検証した」ことを意味しません。網羅性チェックは一次情報スナップショット（`.gitignore`対象・非公開）が無い環境（クローン直後・CI）ではスキップされます。詳細は [.github/WORKFLOW.md](.github/WORKFLOW.md) を参照してください。

## 公式情報源

- リポジトリ: <https://github.com/kirodotdev/KiroCrew>（Apache-2.0）
- 公式ドキュメント: <https://kiro.dev/docs/crew/>
- 製品ページ: <https://kiro.dev/crew/>

## 貢献

Issue・PRの前に [.github/WORKFLOW.md](.github/WORKFLOW.md) と [.github/COMMIT_CHECKLIST.md](.github/COMMIT_CHECKLIST.md) をご確認ください。

## 姉妹サイト

- [kiro-web-docs](https://github.com/kamogashira-sys/kiro-web-docs) — 猫でもわかるKiro Web
- [kiro-ide-docs](https://github.com/kamogashira-sys/kiro-ide-docs) — 猫でもわかるKiro IDE
- [q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs) — 猫でもわかるKiro CLI

## 免責事項

本サイトは非公式のドキュメントです。Kiro Crew メンテナー、Kiro、Amazon Web Services, Inc. のいずれとも提携していません。
Kiro Crew 本体は Apache-2.0 ライセンスです。本サイト（解説文書）は MIT ライセンスです。

# 猫でもわかるKiro Crew

Kiro Crew（OSS: [kirodotdev/KiroCrew](https://github.com/kirodotdev/KiroCrew)）の**主要機能を日本語で解説する**非公式ドキュメントサイトです。

Kiro Crewは、Kiro CLIをランタイムに使い、チャット・Slack等のメッセージングチャネル・スケジュールジョブ・サブエージェントなど複数のサーフェスから1つのエージェントを操作できるようにするGatewayです。本サイトはアップデート情報ではなく、**この主要機能の解説をメインとします**（更新履歴は従属セクション）。

## 目的別の入口

| やりたいこと | 読むページ |
|-------------|-----------|
| Kiro Crewとは何かを知りたい | [01_features/01_architecture.md](01_features/01_architecture.md) |
| メモリの仕組みを知りたい | [01_features/04_memory-and-learning.md](01_features/04_memory-and-learning.md) |
| セキュリティモデルを知りたい | [01_features/09_security.md](01_features/09_security.md) |
| どんなApp（機能）があるか知りたい | [01_features/10_apps.md](01_features/10_apps.md) |
| 導入したい | [03_deployment/01_installation.md](03_deployment/01_installation.md) |
| Windowsで使いたい | [03_deployment/02_windows.md](03_deployment/02_windows.md) |
| CLIコマンドを調べたい | [04_reference/01_cli-commands.md](04_reference/01_cli-commands.md) |
| 上限値・既定値を調べたい | [04_reference/05_limits.md](04_reference/05_limits.md) |

## セクション構成

| セクション | 内容 | ページ数 |
|-----------|------|:---:|
| [00_information](00_information/) | リポジトリ・公式サイトの構造、情報源の使い分け | 4 |
| [01_features](01_features/) | **機能解説（本サイトの主眼）** | 15 |
| [02_update](02_update/) | 更新履歴・リリース方針 | 3 |
| [03_deployment](03_deployment/) | 導入・運用・セキュリティ設定・テレメトリ | 7 |
| [04_reference](04_reference/) | CLI・設定キー・ディレクトリ構造・上限値 | 6 |

## Kiro Crew固有の事情

- **OSSであり、一次情報がリポジトリ（GitHub）と公式サイト（kiro.dev）の二重構造**です。両者が食い違う場合、本サイトは裁定せず両方を記載します
- Kiro Crewのmainブランチは**日次で動く**ため、リポジトリを出典にした記述には参照日・commit SHA・版を必ず記録しています
- 最新安定版は **v0.2.0**（2026-08-16時点）
- Kiro Crew本体のライセンスは **Apache-2.0**、本サイト（解説文書）は **MIT** です

## 機械検証

本サイトの記述は機械的に検証されています。

```bash
make check-kiro-crew-all
```

内部リンク・出典・SSoT（正準値）の一致・表記規約・公式43ページの網羅性・changelog構造・スコープ境界・参照時点記録を検証します。

## 編集方針

- 推測を書かない。すべての記述は一次情報（リポジトリまたは公式サイト）で確認したものに限る
- 確認できない事項は「未確認事項」として明示する
- 出典間で値が食い違う場合は両方を記載し、裁定しない
- Kiro CLI単体の機能は解説しない（[q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs)の領域）

詳細は [.github/WORKFLOW.md](../.github/WORKFLOW.md) を参照してください。

## 姉妹サイト

- [kiro-web-docs](https://github.com/kamogashira-sys/kiro-web-docs) — 猫でもわかるKiro Web
- [kiro-ide-docs](https://github.com/kamogashira-sys/kiro-ide-docs) — 猫でもわかるKiro IDE
- [q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs) — 猫でもわかるKiro CLI

## 免責事項

本サイトは非公式のドキュメントです。Kiro Crew メンテナー、Kiro、Amazon Web Services, Inc. のいずれとも提携していません。
Kiro Crew 本体は Apache-2.0 ライセンスです。本サイト（解説文書）は MIT ライセンスです。

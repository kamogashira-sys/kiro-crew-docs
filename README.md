# 猫でもわかるKiro Crewアップデート情報

**[Kiro Crew](https://github.com/kirodotdev/KiroCrew)（OSS）** のアップデート情報・主要機能・導入と運用・リファレンスを、日本語でまとめた**非公式**ドキュメントサイトです。

Kiro Crewは、Kiro CLIをランタイムに使い、チャット・Slackなどのメッセージングチャネル・スケジュールジョブ・サブエージェントといった複数の窓口から、1つのエージェントを操作するためのGatewayです。本サイトでは更新履歴に加え、主要機能の解説を中心に扱います。

> ⚠️ 一次情報の固定参照時点は**2026-08-16**です。Kiro Crewの固定コミットは`64060f3`、この時点の最新安定版は`v0.2.0`です。以後のKiro Crewの更新は、反映されるまで本サイトには含まれません。

---

## 🚀 ここから読む

| やりたいこと | 見るページ |
|------------|----------|
| **Kiro Crewがどんなものか知りたい** | [アーキテクチャ](kiro-crew-docs/01_features/01_architecture.md) |
| **導入して使い始めたい** | [インストール](kiro-crew-docs/03_deployment/01_installation.md) |
| **メモリとKnowledge Libraryを理解したい** | [メモリと学習](kiro-crew-docs/01_features/04_memory-and-learning.md) / [Knowledge Library](kiro-crew-docs/01_features/05_knowledge-library.md) |
| **セキュリティモデルを確認したい** | [セキュリティ](kiro-crew-docs/01_features/09_security.md) |
| **常時運用・Windows・トラブル対応を知りたい** | [導入・運用](kiro-crew-docs/03_deployment/) |
| **何が変わったか知りたい** | [更新履歴](kiro-crew-docs/02_update/01_changelog.md) |
| **CLI・設定値・上限値を調べたい** | [リファレンス](kiro-crew-docs/04_reference/) |

**[→ サイト本体の目次](kiro-crew-docs/README.md)**

---

## 📚 セクション

| セクション | 内容 |
|-----------|------|
| [00_information](kiro-crew-docs/00_information/) | KiroCrewリポジトリ・公式サイトの構造、情報源の使い分け |
| [01_features](kiro-crew-docs/01_features/) | 機能解説（アーキテクチャ、セッション、メモリ、Knowledge、サブエージェント、Apps、セキュリティ、MCP、Artifactなど） |
| [02_update](kiro-crew-docs/02_update/) | Kiro Crewの更新履歴とリリース方針 |
| [03_deployment](kiro-crew-docs/03_deployment/) | インストール、Windows、常時運用、セキュリティ、トラブルシューティング、テレメトリ |
| [04_reference](kiro-crew-docs/04_reference/) | CLIコマンド、設定キー、ディレクトリ構成、MCPツール、上限値・既定値 |

---

## 📢 Kiro Crewとは

Kiro Crewは、Kiro CLIをランタイムとして利用するGatewayです。チャット、Slackなどのメッセージングチャネル、スケジュールジョブ、サブエージェントから同じエージェントに接続できます。

本サイトはKiro Crew本体の安定版を対象に、一次情報で確認できる機能・設定・運用方法を整理します。Kiro CLI単体の機能は扱わず、必要に応じて[猫でもわかるKiro CLI](https://github.com/kamogashira-sys/q-cli-docs)を参照します。

## 🔖 更新範囲と参照時点

| 項目 | 内容 |
|------|------|
| 固定参照日 | 2026-08-16 |
| Kiro Crew固定コミット | `64060f3ffecdf4aebeb764b4e3108e7375249ad8` |
| 固定時点の最新安定版 | `v0.2.0` |
| 更新履歴の対象 | 安定版 `v0.1.0`〜`v0.2.0` |
| 一次情報 | KiroCrew GitHubリポジトリ、公式ドキュメント、GitHub Releases、CHANGELOG.md |

一次情報間で記述や値が食い違う場合は、根拠なく裁定せず、両方の記述または未確認事項として示します。詳細は[リリース方針](kiro-crew-docs/02_update/02_release-policy.md)と[情報源](kiro-crew-docs/00_information/03_information-sources.md)を参照してください。

---

## 🐾 姉妹サイト

Kiro IDE・Kiro CLI・Kiro Web・Kiro Crewは別製品です。同名の機能でも仕様が異なることがあります。

| 対象 | サイト |
|------|-------|
| **Kiro Crew** | **本サイト** |
| Kiro IDE | [猫でもわかるKiro IDE アップデート情報](https://github.com/kamogashira-sys/kiro-ide-docs) |
| Kiro CLI | [猫でもわかるKiro CLI アップデート情報](https://github.com/kamogashira-sys/q-cli-docs) |
| Kiro Web | [猫でもわかるKiro Web アップデート情報](https://github.com/kamogashira-sys/kiro-web-docs) |

---

## 📌 本サイトの方針

| # | 方針 |
|---|------|
| 1 | リポジトリ・公式ドキュメント・GitHub Releases・CHANGELOG.mdなどの**一次情報**を根拠にする |
| 2 | リポジトリを出典にする記述には、参照日・commit SHA・版を記録する |
| 3 | 公式に確認できない事項は**未確認**と明示し、推測で補わない |
| 4 | 一次情報間の食い違いは両方を記載し、どちらが正しいかを裁定しない |
| 5 | Kiro CLI単体の機能をKiro Crewの機能として扱わない |

---

## ✅ 機械検証

リンク・アンカー、セクション構成、出典、SSoT（正準値）の一致、表記規約、公式ページの網羅性、changelog構造、スコープ境界、参照時点記録をローカルで検証します。

```bash
make check-kiro-crew-all      # 公開前の全チェック
make check-kiro-crew-quick    # 執筆中の常用チェック
make check-kiro-crew-ignore   # 公開範囲の確認
```

> ⚠️ `check-kiro-crew-all` の exit 0 は「すべてを検証した」ことを意味しません。網羅性チェックは一次情報スナップショット（`.gitignore`対象・非公開）がない環境ではスキップされます。`check-source-pin.py`はGitHub出典URLの近辺にSHA・日付・版があるかを確認しますが、URL先が本文の主張を支持するか、他の一次情報と矛盾しないかまでは検証しません。`check-consistency.py`も、事前に定義した文脈パターン外の不整合を検出しません。詳細は[ドキュメント作成ワークフロー](.github/WORKFLOW.md)を参照してください。

---

## 🔗 公式情報源

- KiroCrewリポジトリ: <https://github.com/kirodotdev/KiroCrew>（Apache-2.0）
- Kiro Crew公式ドキュメント: <https://kiro.dev/docs/crew/>
- Kiro Crew製品ページ: <https://kiro.dev/crew/>
- Kiro Crew Releases: <https://github.com/kirodotdev/KiroCrew/releases>

## 🤝 コントリビュート

Issue・PRの前に、以下をご確認ください。

- [ドキュメント作成ワークフロー](.github/WORKFLOW.md)
- [コミット前チェックリスト](.github/COMMIT_CHECKLIST.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## 📄 ライセンス

本サイト（解説文書）は[MIT License](LICENSE)です。Kiro Crew本体はApache-2.0ライセンスです。

---

**免責事項**: 本サイトは非公式のドキュメントプロジェクトであり、Kiro Crewメンテナー、Kiro、Amazon Web Services, Inc.のいずれとも提携していません。正確性には努めていますが、最新かつ正確な情報は必ず公式情報源で確認してください。

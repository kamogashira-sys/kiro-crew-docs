# KiroCrewリポジトリの地図

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew>（GitHub Tree API実測）
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [docs/配下の内訳](#docs配下の内訳)
- [ガバナンス文書](#ガバナンス文書)
- [注意すべき点](#注意すべき点)
- [未確認事項](#未確認事項)

---

## docs/配下の内訳

`docs/` 配下は**281ファイル**（v0.7.2タグ固定スナップショット実測。v0.6.0タグは230）。

| カテゴリ | ファイル数 | 本サイトでの扱い |
|---------|-----------|----------------|
| `docs/system-specs/` | 104 | **機能解説の最重要出典**。104ファイル全件の扱い判定は `05_meta/ledger-modules.md`（ローカル管理）。**`.md` のみなら101件**（差の3件は `modules/examples/workflows/*.py`）。v0.6.0 から `modules/` に16件追加（taskq・adaptive-concurrency・decisions・crew-log 系など） |
| `docs/request-for-change/` | 57 | RFC。**未確定の将来仕様のため出典にしない**（Markdown は56件・画像1件。[03_information-sources.md](03_information-sources.md)参照） |
| `docs/reference/` | 31 | `kiro-cli/` 22件は**Kiro CLIのリファレンス**（Crew本体ではない。[03_information-sources.md](03_information-sources.md)参照）。ほかに `crew-log/` 7件（v0.7.x で追加）・`ledger-conductor-sequence.md`・`README.md` |
| `docs/architecture/` | 21 | `overview.md`・`mcp.md`・`security-deep-dive.md`・`resource-protection.md`・`context-management.md`（v0.7.x で追加）等 |
| `docs/guides/` | 30 | `install.md`・`docker.md`・`windows-install.md`・`telemetry-otlp-export.md`・`oauth-app-registration/`（10件、v0.7.x で追加）等 |
| `docs/app-kit/` | 15 | App SDK |
| `docs/task-specs/` | 7 | 開発作業の資料。**出典にしない** |
| `docs/ci/` | 6 | 開発者向けCI。**解説対象外** |
| `docs/build/` | 6 | ビルド・リリース手順。**原則解説対象外だが、`release.md`・`changelog.md` はリリース運用の一次情報として参照する** |
| `docs/blog/` | 2 | 補助 |
| `docs/feature-map/` | 1 | 機能とUI面の対応表 |
| `docs/`直下 | 1 | `README.md`（索引） |

> 検算: 104＋57＋31＋21＋30＋15＋7＋6＋6＋2＋1＋1＝**281**（v0.7.2タグ実測）。v0.6.0 タグとの差は新規51件・削除0件（230＋51＝281）。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/tree/v0.7.2/docs>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
>
> **`docs/reference/kiro-cli/`（Kiro CLI単体のリファレンス）の件数の訂正**: 本サイトは以前「23ファイル」と記載していましたが、`kiro-cli/` ディレクトリ自体は v0.3.0・v0.6.0・v0.7.2 のいずれも22件です（23件は `docs/reference/README.md` を含めた v0.6.0 までの `docs/reference/` 全体の件数でした）。

## ガバナンス文書

リポジトリ直下に以下が実在します（すべて実測確認済み）: `README.md`／`CHANGELOG.md`／`CONTRIBUTING.md`／`SECURITY.md`／`LICENSE`／`NOTICE`／`CODE_OF_CONDUCT.md`／`GOVERNANCE.md`／`MAINTAINERS.md`／`TENETS.md`／`AGENTS.md`

## 注意すべき点

- **`docs/request-for-change/`は未確定の将来仕様です。** 実装済みと誤読しないでください
- **`docs/reference/kiro-cli/`（23ファイル）はKiro CLI単体のリファレンス**であり、本サイトの解説対象外です。q-cli-docsの領域です
- **削除済み・移行専用の仕様書に注意**: `docs/system-specs/post-launch-removals.md`（旧データホームの記述を含む）は、現行機能として誤読する経路があります
- **⚠️ `claude-code-provider.md` は v0.6.0 で性格が変わりました**: v0.4.1 までは `docs/system-specs/features/claude-code-provider.md`（タイトル「Standalone provider — removed」）＝削除済み機能の記録でしたが、**v0.6.0 では `docs/system-specs/modules/claude-code-provider.md`（タイトル「Claude Code provider — a selectable ACP harness」）＝現行機能の仕様書**です。削除済み扱いにしないでください（[01_features/15_agent-backends.md](../01_features/15_agent-backends.md)参照）

## 未確認事項

- なし（本ページの記述はGitHub Tree API実測で確認済み）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew>
- 情報源の使い分け: [03_information-sources.md](03_information-sources.md)
- アーキテクチャ: [01_features/01_architecture.md](../01_features/01_architecture.md)

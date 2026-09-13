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

`docs/` 配下は**230ファイル**（v0.6.0タグ固定スナップショット実測）。

| カテゴリ | ファイル数 | 本サイトでの扱い |
|---------|-----------|----------------|
| `docs/system-specs/` | 88 | **機能解説の最重要出典**。88ファイル全件の扱い判定は `05_meta/ledger-modules.md`（ローカル管理）。**`.md` のみなら85件**（差の3件は `modules/examples/workflows/*.py`） |
| `docs/request-for-change/` | 46 | RFC。**未確定の将来仕様のため出典にしない**（[03_information-sources.md](03_information-sources.md)参照） |
| `docs/reference/` | 23 | **Kiro CLIのリファレンス**（Crew本体ではない。[03_information-sources.md](03_information-sources.md)参照） |
| `docs/architecture/` | 20 | `overview.md`・`mcp.md`・`security-deep-dive.md`・`resource-protection.md`等 |
| `docs/guides/` | 19 | `install.md`・`docker.md`・`windows-install.md`・`telemetry-otlp-export.md`等 |
| `docs/app-kit/` | 15 | App SDK |
| `docs/task-specs/` | 5 | 補助 |
| `docs/ci/` | 5 | 開発者向けCI。**解説対象外** |
| `docs/build/` | 5 | ビルド・リリース手順。**原則解説対象外だが、`release.md`・`changelog.md` はリリース運用の一次情報として参照する** |
| `docs/blog/` | 2 | 補助 |
| `docs/feature-map/` | 1 | 機能とUI面の対応表 |
| `docs/` 直下の単体ファイル | 1 | — |

> 検算: 88＋46＋23＋20＋19＋15＋5＋5＋5＋2＋1＋1＝**230**（v0.6.0タグ実測）。v0.4.1 時点に存在した `docs/screenshots/`・`docs/design/` は v0.6.0 では見つかりません。
| `docs/`直下 | 1 | `README.md`（索引） |

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

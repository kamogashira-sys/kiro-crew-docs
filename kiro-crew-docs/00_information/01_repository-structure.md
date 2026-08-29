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

`docs/` 配下は**225ファイル**（v0.4.1タグ固定スナップショット実測）。

| カテゴリ | ファイル数 | 本サイトでの扱い |
|---------|-----------|----------------|
| `docs/system-specs/` | 76 | **機能解説の最重要出典**。76ファイル全件の扱い判定は `05_meta/ledger-modules.md`（ローカル管理） |
| `docs/reference/` | 23 | **Kiro CLIのリファレンス**（Crew本体ではない。§00_information/03参照） |
| `docs/request-for-change/` | 20 | RFC。**未確定の将来仕様のため出典にしない** |
| `docs/screenshots/` | 20 | 画像。再配布しない |
| `docs/architecture/` | 16 | `overview.md`・`mcp.md`・`security-deep-dive.md`・`resource-protection.md`等 |
| `docs/app-kit/` | 15 | App SDK |
| `docs/guides/` | 14 | `install.md`・`docker.md`・`windows-install.md`等 |
| `docs/ci/` | 6 | 開発者向けCI。**解説対象外** |
| `docs/build/` | 4 | ビルド。**解説対象外** |
| `docs/design/`・`docs/blog/`・`docs/task-specs/` | 各2 | 補助 |
| `docs/`直下 | 1 | `README.md`（索引） |

## ガバナンス文書

リポジトリ直下に以下が実在します（すべて実測確認済み）: `README.md`／`CHANGELOG.md`／`CONTRIBUTING.md`／`SECURITY.md`／`LICENSE`／`NOTICE`／`CODE_OF_CONDUCT.md`／`GOVERNANCE.md`／`MAINTAINERS.md`／`TENETS.md`／`AGENTS.md`

## 注意すべき点

- **`docs/request-for-change/`は未確定の将来仕様です。** 実装済みと誤読しないでください
- **`docs/reference/kiro-cli/`（23ファイル）はKiro CLI単体のリファレンス**であり、本サイトの解説対象外です。q-cli-docsの領域です
- **削除済み・移行専用の仕様書に注意**: `docs/system-specs/features/claude-code-provider.md`（タイトルが「Standalone provider — removed」）や`docs/system-specs/post-launch-removals.md`（旧データホームの記述を含む）は、現行機能として誤読する経路があります

## 未確認事項

- なし（本ページの記述はGitHub Tree API実測で確認済み）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew>
- 情報源の使い分け: [03_information-sources.md](03_information-sources.md)
- アーキテクチャ: [01_features/01_architecture.md](../01_features/01_architecture.md)

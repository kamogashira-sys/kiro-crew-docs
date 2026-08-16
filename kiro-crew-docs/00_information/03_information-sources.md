# 情報源の使い分けと落とし穴

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew>（一次情報ヒエラルキーの設計根拠）
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [一次情報の優先順位（8順位）](#一次情報の優先順位8順位)
- [出典にしないもの](#出典にしないもの)
- [Zenn記事の位置づけ](#zenn記事の位置づけ)
- [mainブランチが日次で動く](#mainブランチが日次で動く)
- [スコープ境界（Kiro CLIとの重複）](#スコープ境界kiro-cliとの重複)
- [未確認事項](#未確認事項)

---

## 一次情報の優先順位（8順位）

| 順位 | 情報源 | 何に使うか |
|-----|-------|-----------|
| 1 | リポジトリのソース／モジュール仕様（`docs/system-specs/`・`docs/architecture/`） | 仕様の最終根拠 |
| 2 | リポジトリのREADME／ガイド | 導入手順・運用手順 |
| 3 | 公式ドキュメント（`kiro.dev/docs/crew/`配下43ページ） | 機能の公式な言い方 |
| 4 | CHANGELOG.md + GitHub Releases | 版ごとの変更点 |
| 5 | 公式ブログ | 設計意図・背景 |
| 6 | AWS公式ブログ（日本語） | 日本語の公式用語 |
| 7 | AWS Japan社員のZenn記事（3本） | 日本語の解釈・検証済み手順 |
| 8 | 実機確認 | 1〜7で確定しない挙動 |

## 出典にしないもの

| 対象 | 理由 |
|------|------|
| `docs/request-for-change/`（20件） | 未確定の将来仕様 |
| `docs/ci/`・`docs/build/` | Crew開発者向け |
| 削除済み・移行専用の仕様書 | v0.2.0で既に存在しない機能の記録（例: `claude-code-provider.md`） |
| `## [Unreleased]`（CHANGELOG冒頭） | 未リリース |
| プレリリース（`-rc.N`） | 安定版のみを版番号として扱う |
| `kiro.dev/llms.txt` | crewの言及が0件（URL網羅には使えない） |

## Zenn記事の位置づけ

AWS Japan社員による記事3本を参考にしていますが、各記事に「個人の見解であり所属組織の公式見解ではない」旨のPublication注記があります。したがって**一次情報と同等に参照するが、Crewの仕様の根拠としてはGitHub／公式docsを優先**し、Zennを「日本語の解釈・検証済み手順の出典」として併記します。

参考にした3本（いずれも**0.1.2時点**）:

- Kai Mitsuzawa（Crew Contributor）「機能網羅」2026-08-05
- konippi「アーキテクチャ設計視点」2026-08-06
- Hiro「Windows導入手順」2026-08-06

> **版差の注意**: 0.1.2時点の記事とv0.2.0の実装で差異が見つかった実例があります（ブラウザ自動化が「Playwright MCP」→シェル機能に変わった等）。本サイトはv0.2.0の一次情報を優先し、版差がある場合は各ページに注記します。

## mainブランチが日次で動く

Zenn記事（Kai Mitsuzawa）は「週100コミットを超えるペース」、公式ブログは「週平均143コミット」と述べています。実測で最終pushは本サイト作成日と同日でした。**リポジトリを出典にする記述には必ず参照時点（取得日・commit SHA・版）を記録します。**

## スコープ境界（Kiro CLIとの重複）

KiroCrewリポジトリには `docs/reference/kiro-cli/`（23ファイル）が同梱されていますが、これは**Kiro CLI単体のリファレンス**です。

| 区分 | 本サイトの扱い |
|------|--------------|
| Crew Gateway自身の機能 | 解説する |
| Crewが Kiro CLI に依存する接点（ACP・`agent.provider=acp`） | 解説する |
| Kiro CLI単体の機能 | 解説しない。[q-cli-docs](https://github.com/kamogashira-sys/q-cli-docs)へリンク |
| `docs/reference/kiro-cli/`の内容 | 出典として使わない |

## 未確認事項

- なし

## 関連リンク

- Kiro CLI版ドキュメント（姉妹サイト）: <https://github.com/kamogashira-sys/q-cli-docs>
- リポジトリの地図: [01_repository-structure.md](01_repository-structure.md)
- 公式サイトの構造: [02_official-docs-structure.md](02_official-docs-structure.md)

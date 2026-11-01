# KiroCrewリポジトリの地図

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew>（タグ固定スナップショットの実測）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

---

## 📑 このページの内容

- [v0.11.1 での変更](#v0111-での変更)
- [docs/配下の内訳](#docs配下の内訳)
- [ガバナンス文書](#ガバナンス文書)
- [注意すべき点](#注意すべき点)
- [未確認事項](#未確認事項)

---

## v0.11.1 での変更

`docs/` 配下の合計は、v0.9.0 タグの349ファイルから **429ファイル**（+80）に増えました。v0.9.0 タグからの削除は0件です（v0.9.0 タグのファイルはすべて v0.11.1 タグにも存在します）。

| カテゴリ | v0.9.0 タグ | v0.11.1 タグ | 差 | 補足 |
|---|---|---|---|---|
| `docs/request-for-change/` | 108 | **161** | +53 | Markdown 94→**142**、画像（PNG）13→**18**、HTML 1（変化なし） |
| `docs/decisions/` | 7 | **30** | +23 | `README.md` 1件＋決定記録 **29**件（v0.9.0 タグは6件）。追加23件の日付は 2026-09-05〜2026-10-28 |
| `docs/guides/` | 34 | **37** | +3 | 追加は `lm-studio-and-openrouter.md`・`remote-crew-on-microvm.md`・`transcript-reverse-migration.md` |
| `docs/architecture/` | 22 | **23** | +1 | `design-notes/` が13→**14**件（追加は `wakatime-oauth-read-auth.md`） |
| `docs/system-specs/` | 107 | 107 | 0 | ファイル集合は同一（追加0・削除0）。内容が変わったファイルが93件あります |
| 上記以外のカテゴリ | — | — | 0 | `reference/` 33・`app-kit/` 15・`task-specs/` 7・`ci/` 6・`build/` 6・`blog/` 2・`feature-map/` 1・`docs/` 直下 1 は件数が同じです |

> **出典**: <https://github.com/kirodotdev/KiroCrew/tree/v0.11.1/docs>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
>
> 途中の版の `docs/` 配下の件数は、v0.10.0 タグが388ファイル、v0.11.0 タグが429ファイルです。v0.11.1 タグの件数は v0.11.0 タグと同じです。
>
> 上表の `docs/request-for-change/`・`docs/decisions/` の増加は件数の記録です。RFC は設計提案と決定の記録であり、本サイトは出典にしません（[03_information-sources.md](03_information-sources.md)）。`docs/decisions/` を出典にするかどうかは人の判断事項のため、今回の版更新ではいずれの決定記録も出典にしていません。

## docs/配下の内訳

`docs/` 配下は**429ファイル**（v0.11.1タグ固定スナップショット実測。v0.9.0タグは349、v0.8.0タグは298、v0.7.2タグは281、v0.6.0タグは230）。

| カテゴリ | ファイル数 | 本サイトでの扱い |
|---------|-----------|----------------|
| `docs/system-specs/` | 107 | **機能解説の最重要出典**。107ファイル全件の扱い判定は [`scripts/kiro-crew-docs/ledgers/modules.md`](../../scripts/kiro-crew-docs/ledgers/modules.md)。**`.md` のみなら104件**（差の3件は `modules/examples/workflows/*.py`）。v0.6.0 から `modules/` に16件追加（taskq・adaptive-concurrency・decisions・crew-log 系など）。v0.7.2 からは新規4件（`common/take-away-changes.md`・`modules/dashboard-instances.md`・`modules/dashboard-templates.md`・`modules/runtime-ownership.md`）・消滅1件（`modules/autopilot.md`。v0.8.0 タグには存在し、v0.9.0 タグには存在しない） |
| `docs/request-for-change/` | 161 | RFC。**設計提案と決定の記録で、現行コードの記述ではないため出典にしない**（Markdown は142件・画像（PNG）18件・HTML 1件。[03_information-sources.md](03_information-sources.md)参照） |
| `docs/reference/` | 33 | `kiro-cli/` 22件は**Kiro CLIのリファレンス**（Crew本体ではない。[03_information-sources.md](03_information-sources.md)参照）。ほかに `crew-log/` 8件（v0.7.x で追加。`fold-paths.md` は v0.9.0 で追加）・`debug/` 1件（`README.md`。v0.8.0 で追加）・`ledger-conductor-sequence.md`・`README.md` |
| `docs/architecture/` | 23 | `overview.md`・`mcp.md`・`security-deep-dive.md`・`resource-protection.md`・`context-management.md`（v0.7.x で追加）等。`design-notes/` は14件（v0.11.1 時点。`kas-nondestructive-session-teardown.md` は v0.8.0 タグで追加済み） |
| `docs/guides/` | 37 | `install.md`・`docker.md`・`windows-install.md`・`telemetry-otlp-export.md`・`oauth-app-registration/`（10件、v0.7.x で追加）等。v0.7.2 からは新規4件（`acp-compaction-capture.md`・`custom-llm-backend.md`・`endpoint-security-blocking-spawned-tools.md`・`remote-crew-on-fargate.md`）。v0.9.0 からは新規3件（`lm-studio-and-openrouter.md`・`remote-crew-on-microvm.md`・`transcript-reverse-migration.md`） |
| `docs/app-kit/` | 15 | App SDK |
| `docs/task-specs/` | 7 | 開発作業の資料。**出典にしない** |
| `docs/ci/` | 6 | 開発者向けCI。**解説対象外** |
| `docs/build/` | 6 | ビルド・リリース手順。**原則解説対象外だが、`release.md`・`changelog.md` はリリース運用の一次情報として参照する** |
| `docs/blog/` | 2 | 補助 |
| `docs/feature-map/` | 1 | 機能とUI面の対応表 |
| `docs/decisions/` | 30 | **v0.7.2 タグには無く、v0.8.0 タグ以降にあるディレクトリ**（v0.8.0 タグで3件、v0.9.0 タグで7件、v0.10.0 タグで20件、v0.11.0 タグ以降で30件）。チームの人が下したプロダクト・設計上の決定の記録で、`README.md` 1件＋決定記録29件。1決定1ファイル（`YYYY-MM-DD-<slug>.md`）で、記録済みのエントリは編集・改名・削除されない（`docs/decisions/README.md` 22・25行）。v0.9.0 タグの7件は v0.11.1 タグでも内容が変わっていません。**出典にするかどうかは人の判断事項のため、本サイトの今回の版更新ではいずれの決定記録も出典にしていません** |
| `docs/`直下 | 1 | `README.md`（索引） |

> 検算: 107＋161＋33＋23＋37＋15＋7＋6＋6＋2＋1＋30＋1＝**429**（v0.11.1タグ実測）。v0.9.0 タグとの差は新規80件・削除0件（349＋80＝429）。新規80件の内訳は RFC 53（`rfc-*.md` 47・`plans/` 配下の Markdown 1・PNG 5）・`docs/decisions/` 23・`docs/guides/` 3・`docs/architecture/` 1 です。
>
> 参考（v0.9.0 タグの検算）: 107＋108＋33＋22＋34＋15＋7＋6＋6＋2＋1＋7＋1＝349。v0.7.2 タグとの差は新規69件・削除1件（281＋69−1＝349）で、新規69件の内訳は RFC 51・`docs/decisions/` 7・`docs/guides/` 4・`docs/system-specs/` 4・`docs/reference/` 2・`docs/architecture/` 1、削除1件は `docs/system-specs/modules/autopilot.md` でした。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/tree/v0.11.1/docs>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。v0.9.0 タグの件数は commit `99e6253`）
>
> **`docs/reference/kiro-cli/`（Kiro CLI単体のリファレンス）の件数の訂正**: 本サイトは以前「23ファイル」と記載していましたが、`kiro-cli/` ディレクトリ自体は v0.3.0・v0.6.0・v0.7.2・v0.8.0・v0.9.0・v0.11.1 のいずれも22件です（23件は `docs/reference/README.md` を含めた v0.6.0 までの `docs/reference/` 全体の件数でした）。同じページの「注意すべき点」にも「23ファイル」の記述が残っていたため、あわせて22件に訂正しました（v0.7.2 以前から残っていた誤りです）。

## ガバナンス文書

リポジトリ直下に以下が実在します（すべて実測確認済み）: `README.md`／`CHANGELOG.md`／`CONTRIBUTING.md`／`SECURITY.md`／`LICENSE`／`NOTICE`／`CODE_OF_CONDUCT.md`／`GOVERNANCE.md`／`MAINTAINERS.md`／`TENETS.md`／`AGENTS.md`

## 注意すべき点

- **`docs/request-for-change/`は設計提案と決定の記録で、現行コードの記述ではありません。** `docs/request-for-change/README.md` は、RFC を「提案であり決定の記録。コードが今何をしているかの記述ではない」と位置づけています。同README の一覧表には status が `implemented` の行もありますが、本サイトはいずれも出典にしません。RFC の記述を現行機能として誤読しないでください
- **`docs/reference/kiro-cli/`（22ファイル）はKiro CLI単体のリファレンス**であり、本サイトの解説対象外です。q-cli-docsの領域です。`docs/reference/README.md`（v0.11.1。16・24行）は、`kiro-cli/` を kiro-cli の公式ドキュメントのミラー（3.0 の情報構成から取得。v0.7.2 の同ファイルは 2.x 系と記述）とし、kiro-cli を Kiro Crew の既定のエージェントバックエンドと説明したうえで、「ミラーに載っている機能が、そのまま Kiro Crew の機能になるわけではない」と明記しています
- **削除済み・移行専用の仕様書に注意**: `docs/system-specs/post-launch-removals.md` は、現行機能として誤読する経路があります。v0.11.1 の同ファイル（14行）は、`~/.kirocrew` を `~/.kiro/crew` に移す処理は無く、残る項目は `.kirocrew` のセキュリティパス表記の1件だけと記述しています
- **⚠️ `claude-code-provider.md` は v0.6.0 で性格が変わりました**: v0.4.1 までは `docs/system-specs/features/claude-code-provider.md`（タイトル「Standalone provider — removed」）＝削除済み機能の記録でしたが、**v0.6.0 では `docs/system-specs/modules/claude-code-provider.md`（タイトル「Claude Code provider — a selectable ACP harness」）＝現行機能の仕様書**です。削除済み扱いにしないでください（[01_features/15_agent-backends.md](../01_features/15_agent-backends.md)参照）
- **`docs/system-specs/modules/autopilot.md` は v0.9.0 タグ・v0.11.1 タグに存在しません**: v0.7.2・v0.8.0 タグには存在した仕様書です。現行機能として誤読しないでください（扱いの詳細は [01_features/03_chat.md](../01_features/03_chat.md) などの機能ページと台帳 [`modules.md`](../../scripts/kiro-crew-docs/ledgers/modules.md) を参照）

## 未確認事項

- なし（本ページの件数は v0.11.1 タグ固定スナップショットの実測で確認済み）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew>
- 情報源の使い分け: [03_information-sources.md](03_information-sources.md)
- アーキテクチャ: [01_features/01_architecture.md](../01_features/01_architecture.md)

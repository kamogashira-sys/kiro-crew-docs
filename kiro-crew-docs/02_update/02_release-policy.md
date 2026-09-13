# リリース方針

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew>（README「Release channels」節）
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/build/release.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

---

## 📑 このページの内容

- [版番号の付け方](#版番号の付け方)
- [プレリリースの系統](#プレリリースの系統)
- [配布チャネル](#配布チャネル)
- [強制更新の下限（最小サポート版）](#強制更新の下限最小サポート版)
- [`[Unreleased]`を出典にしない理由](#unreleasedを出典にしない理由)
- [日付の食い違い](#日付の食い違い)
- [未確認事項](#未確認事項)

---

## 版番号の付け方

`vX.Y.Z` 形式です。実在する安定版は固定参照時点（2026-09-13）で **v0.1.0／v0.1.1／v0.1.2／v0.1.3／v0.2.0／v0.3.0／v0.4.0／v0.4.1／v0.5.0／v0.6.0** の10件です（GitHub Releases実測、全59 Release中。残る49件はプレリリース）。

本サイトは安定版のみを扱う方針のため、プレリリースは本文の解説対象にしていません。

## プレリリースの系統

プレリリース49件のサフィックスは**2系統**あり、版によって使い分けられています。

| サフィックス | 対象 | 件数 |
|---|---|---|
| `-rc.N` | **v0.2.0系のみ**（例: `v0.2.0-rc.1`） | 8件 |
| `-insider.N` | v0.1.0／v0.1.1／v0.1.2／v0.1.3／v0.4.0／v0.4.1／v0.5.0／v0.6.0 系（例: `v0.1.3-insider.2`） | 41件 |

**v0.3.0系のプレリリースはGitHub Releases実測で0件**です（`v0.3.0` 本体のみで `-rc.N`・`-insider.N` いずれも存在しません）。

> **⚠️ 連番の最大値は件数ではありません。** 実測で欠番があります。
>
> | 系統 | 存在する番号 | 件数 | 欠番 |
> |---|---|---|---|
> | `v0.5.0-insider.N` | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11 | **10件** | `-insider.4` |
> | `v0.6.0-insider.N` | 1, 2, 3, 4, 6, 7 | **6件** | `-insider.5` |
>
> 最大番号（11・7）を件数として扱うと誤りになります。欠番の理由は公式に説明がなく**未確認**です。

## 配布チャネル

すべての導入経路（デスクトップアプリ・CLI・Dockerイメージ）が同じ3チャネルを提供します。

| チャネル | 対象 | ビルド元 | 頻度 |
|---------|------|---------|------|
| **Stable** | 全員（既定） | 十分に長く実績を積んだInsiderビルド | プロモーション時 |
| **Insider** | パワーユーザー | リリースブランチのリリース候補タグ | RCごと |
| **Nightly** | 未テストの `main` HEAD | – | 日次 |

> **v0.3.0での追加（変更ではない）**: デスクトップアプリのAboutからチャネルを切り替えられるようになり、再インストール不要でGatewayが再起動する（CHANGELOG タグ版120行「Change release channel without reinstalling」）。**3チャネルの構成自体は変わっていません**。手順の詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md) を参照してください。

詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md) を参照してください。

## 強制更新の下限（最小サポート版）

**v0.5.0 で追加されました。** CHANGELOG は「A release can declare a minimum supported version — An install below the floor gets an update prompt that cannot be snoozed, skipped or dismissed」と記述します（`[0.5.0]` 節 353-354行）。

`docs/build/release.md` 610行以降は仕組みをより詳しく説明しています。古いクライアントを動かし続けさせてはならないリリース（feed schema の破壊・プロトコルの破壊・後方互換のないデータ移行）が対象です。

| 要素 | 内容 |
|---|---|
| 宣言場所 | `packaging/MIN_VERSION` に**1行1つのリリース版**を記述（コメントと空行は無視。値の行が2つ以上あると publish が失敗する） |
| 伝搬 | その値を持つコミットから publish された CLI feed manifest が、任意項目の**署名付き `min_version` フィールド**として埋め込む |
| Gateway の挙動 | 通常の feed チェック時に下限と自分の版を比較する。**インストーラと同じピン留め鍵で manifest の署名を検証したあと**に比較する（`platform/feed_trust.py`）。版はまずチャネル単位で畳み込まれる（プロモートされた stable ビルドの `0.3.0rc13` スタンプは `0.3.0` リリースと同一とみなす） |
| 下限未満のとき | status frame と `GET /api/update/check` の `update_required` が true になり、ダッシュボードの更新モーダルが **snooze・skip・Escape を失う**（更新するまでプロンプトが出続ける）。**Gateway 自体は動作を続けます** |
| 失敗時 | 検証や解析の失敗は**通常の dismiss 可能なプロンプトに劣化**する。仕様書はこれを「the floor fails toward freedom, never toward coercion」と表現しています |
| インストーラ | フィールドの書式を検証するだけで、あとは無視する（常に署名された版をインストールする） |
| 企業ガバナンスのピン | `security_policy.json` の `updates.min_version` は**独立**しており、feed の下限と **OR** で結合される（どちらか一方だけでも更新が必須になる） |

## `[Unreleased]`を出典にしない理由

`CHANGELOG.md` 冒頭の `## [Unreleased]` 節は**未リリース**の項目であり、リリース済みの機能として扱うと誤情報になります。本サイトは常にこの節を出典から除外します。

> **⚠️ 現在この節は存在しません。** 固定参照時点（2026-09-13 / 版 v0.6.0）の `CHANGELOG.md` に `## [Unreleased]` 節はありません（実測0件）。リポジトリの開発方針文書は「**There is no `## [Unreleased]` section, and the gate refuses one.**」と明記し、保留中の内容を見るには `git log --oneline <last-tag>..HEAD` を読むよう指示しています（`docs/build/changelog.md` 23行）。
>
> gateの実体は `scripts/check_changelog_history.py` です。`docs/build/release.md` 1170-1172行は「There is no `## [Unreleased]` section to accumulate into and no in-progress prerelease heading to rename later — `scripts/check_changelog_history.py` refuses both」と記述し、**節を作ることも、進行中のプレリリース見出しを後で改名することも拒否される**としています。その結果、changelog の差分として合法な形は「新しい節を1つ先頭に足す」だけになります。
>
> したがって現時点では除外すべき対象がありません。**節が復活した場合に備えて、除外方針そのものは維持します。**
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/build/changelog.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
>
> 参考として、過去には存在していました（2026-08-16 時点の取得で約390行）。**この方針を述べた文の所在も版で移動しています**（v0.4.1 では `AGENTS.md` 254行、v0.6.0 では `docs/build/changelog.md` 23行）。

## 日付の食い違い

CHANGELOG.mdの日付とGitHub Releaseの公開日は**一致しません**（実測で8版すべてで食い違い）。

| 版 | CHANGELOG.mdの日付 | Release公開日 |
|----|-------------------|-------------|
| v0.6.0 | 2026-09-05 | 2026-09-11 |
| v0.5.0 | 2026-08-29 | 2026-09-05 |
| v0.4.1 | 2026-08-28 | 2026-08-29 |
| v0.4.0 | 2026-08-25 | 2026-08-27 |
| v0.3.0 | 2026-08-17 | 2026-08-21 |
| v0.2.0 | 2026-08-09 | 2026-08-10 |
| v0.1.3 | 2026-08-07 | 2026-08-05 |
| v0.1.2 | 2026-07-30 | 2026-08-04 |

**本サイトはこれを裁定せず、両方を記載します**（[01_changelog.md](01_changelog.md)参照）。

## 未確認事項

- 日付が食い違う理由（公式に明記された説明は見つかっていない。理由は未確認）
- `-insider.N` の欠番（`v0.5.0-insider.4`・`v0.6.0-insider.5`）の理由
- `packaging/MIN_VERSION` の現在の値（`src/`・`packaging/` はスナップショット取得対象外のため未確認）
- `-rc.N` から `-insider.N` へ切り替わった経緯（v0.2.0系のみ `-rc.N` である理由は公式に説明が見つかっていない）

## 関連リンク

- Releases: <https://github.com/kirodotdev/KiroCrew/releases>
- 更新履歴: [01_changelog.md](01_changelog.md)
- 導入経路: [03_deployment/01_installation.md](../03_deployment/01_installation.md)

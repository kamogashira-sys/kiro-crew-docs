# Agent Backends（ハーネス選択・Preview）

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://kiro.dev/docs/crew/features/agent-backends/>
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/claude-code-provider.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-onboarding.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

---

## 📑 このページの内容

- [概要](#概要)
- [セキュリティ上の重要な境界](#セキュリティ上の重要な境界)
- [有効化の手順](#有効化の手順)
- [選択できるハーネス](#選択できるハーネス)
- [バックエンドをまたいで同じもの](#バックエンドをまたいで同じもの)
- [設定キー](#設定キー)
- [未確認事項](#未確認事項)

---

## 概要

**v0.6.0 で追加された Preview 機能です。既定では無効で、有効化しないとセレクタが現れません。**

公式ページは「新しい Crew セッションを動かすハーネスを選ぶ」機能と説明しています。従来 Kiro Crew は Kiro CLI をランタイムとして固定的に使っていましたが、v0.6.0 では Claude Code・Codex・KAS も選択肢になります。

リポジトリ側の仕様書では、`AgentConfig.provider` が受け付けるのは ACP プロバイダのみで、**ハーネスの選択は `provider` とは別のフィールド `agent.acp_backend`** であると記述されています（`claude-code-provider.md` 7行）。

> **⚠️ 本サイトの位置づけ**: 本ページは Kiro Crew Gateway 側の「どのハーネスを使うか」という選択機構を扱います。Claude Code・Codex・KAS それぞれの単体機能は本サイトの対象外です。Kiro CLI 単体の機能は [猫でもわかるKiro CLI](https://github.com/kamogashira-sys/q-cli-docs) を参照してください。

## セキュリティ上の重要な境界

**Claude の設定で事前承認されたツール呼び出しは、Kiro Crew の承認パスに到達しません。**

CHANGELOG v0.6.0 節は「A tool pre-approved in Claude's own settings never reaches Crew's approval path, so its deny rules and audit log do not see that call」と記述します。公式ページも「Claude tools pre-approved in Claude's own settings bypass Crew approvals」と明記しています。

リポジトリ側の仕様書はこの仕組みをより詳しく説明しています。

| 出典（`claude-code-provider.md`） | 記述 |
|---|---|
| 92-94行 | 通常の呼び出しは `hooks.on_tool_call`・拒否ルール・機密パス検査・書き込み保護設定の検査・SEL の判定記録を通る。「A Claude session is governed like any other on that path」 |
| 96-100行 | 「**What escapes is a call that was already pre-approved, because it never asks.**」SDK は固定順で権限を評価し、`allow` ルールは step 5、コールバックは step 6 にある。Anthropic の文書は「Auto-approved tools never reach `canUseTool`」と太字で明記しており、コールバックが呼ばれない＝ACP リクエストが発生しないため、**その呼び出しについて Crew が検査・記録できるものが存在しない** |
| 304-310行 | ユーザーのグローバル設定（`~/.claude`）がツールファミリを事前承認している場合、それらは Claude 自身のエンジンで自動承認され `canUseTool` を呼ばず Crew のゲートに到達しない。**プロジェクトファイル側からも閉じられない**（Crew が作成していない `settings.local.json` は書き換えを辞退するため、ユーザー自身のプロジェクトファイルの `allow` エントリはそのまま残る） |

つまり **Claude Code バックエンドを選ぶと、Crew の拒否ルールと監査ログ（SEL）が見ない経路が生まれます**。セキュリティモデル全体は [09_security.md](09_security.md) を参照してください。

**Codex はサンドボックスが off の状態では起動しません**（CHANGELOG v0.6.0 節「Codex refuses to start while the sandbox is off」）。サンドボックスの設定は [09_security.md](09_security.md) と [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。

## 有効化の手順

公式ページの手順どおりです。

1. **Settings → Developer** を開き **Developer Mode** をオンにする（既定はオフ）
2. **Developer → Agent Backend** を開く
3. **Kiro CLI** / **Claude Code** / **Codex** / **KAS** から選ぶ

各バックエンドには、この端末に**インストール済み**か、**未インストール**か、**インストール済みだが Gateway 再起動待ち**かが表示されます。利用できない状態のバックエンドを選ぶ前に、インストールまたは再起動を行います。

**選択は新しいセッションに適用されます。既存のセッションは開始時のバックエンドを維持します。**

## 選択できるハーネス

**⚠️ 出典間で選択肢の数が食い違っています。本サイトは裁定せず両方を記載します。**

| 出典 | 選択できるハーネス |
|---|---|
| 公式ページ `features/agent-backends/` | **4種**（Kiro CLI / Claude Code / Codex / KAS） |
| CHANGELOG v0.6.0 節 30-33行 | 「Claude Code, Codex and KAS are selectable harnesses」（Kiro CLI に加えて**3種**が選択可能という表現） |
| `claude-code-provider.md` 7-11行 | `acp_backends.BASELINE_SELECTABLE_BACKENDS` は **`ACP_BACKEND_KIRO`（空文字列）・`ACP_BACKEND_CLAUDE`・`ACP_BACKEND_KAS` の3件**を含み、「i.e. all of `ACP_BACKENDS_KNOWN`」と記述する。`test_baseline_ships_every_known_backend` がこの同値をピン留めしている |

`ACP_BACKEND_CODEX` という定数自体はリポジトリの `docs/` 内に存在します。`harness-onboarding.md` は、ハーネスの状態を **Dormant**（`ACP_BACKENDS_KNOWN` に id はあるが選択不可）と **Selectable**（`BASELINE_SELECTABLE_BACKENDS` にある、またはエディションが追加する）に区別しており、同ファイルは Codex を「onboarding の題材」として扱っています（7行・198行「Worked example: the Codex seam」）。

**公式ページと CHANGELOG は Codex を選択可能として挙げ、`claude-code-provider.md` は `BASELINE_SELECTABLE_BACKENDS` を3件と記述します。どちらが最終的に正か・エディションによる差なのかは公式に説明がないため、本サイトは裁定しません。**

## バックエンドをまたいで同じもの

公式ページは「Crew keeps the same session controls across the selectable backends」と説明し、次の機能がすべてのバックエンドで動くと記述します。

- 監視ループ（Monitor loops）
- プロジェクトの変更（project changes）
- フォローアップカード（follow-up cards）
- 会話のリセット（conversation reset）

CHANGELOG v0.6.0 節は、これらが**従来は Kiro CLI 以外では fail closed になっていた**（"where they previously failed closed outside Kiro CLI"）と記述します。

## 設定キー

値と既定値の一覧は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。本ページでは重複させません。

| キー | 用途 |
|---|---|
| `agent.acp_backend` | ハーネスの選択。`acp_backends.resolve_selected_backend()` が値を正規化する（`claude-code-provider.md` 25行）。ゲートは1箇所に集約されている（同319行） |

## 未確認事項

- `agent.acp_backend` の既定値（`docs/system-specs/modules/config.md` には当該キーの記述が見つからず、`claude-code-provider.md` からは既定値を確定できない）
- Codex が `BASELINE_SELECTABLE_BACKENDS` に含まれるかどうか（上記のとおり出典間で食い違う）
- KAS の正式名称と位置づけ（`kas-auth.md` が存在するが、本サイトでは未精読）
- Preview を有効化したあとのハーネスごとの機能差の詳細（`harness-parity.md` が存在するが、本サイトでは未精読）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/agent-backends/>
- 公式（セキュリティ）: <https://kiro.dev/docs/crew/security/>
- セキュリティモデル: [09_security.md](09_security.md)
- アーキテクチャ: [01_architecture.md](01_architecture.md)
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

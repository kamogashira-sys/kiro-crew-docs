# Agent Backends（ハーネス選択・Preview）

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://kiro.dev/docs/crew/features/agent-backends/>
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/claude-code-provider.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-onboarding.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**: <https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-09-25）
**出典**（v0.7.0での変更・選択肢の食い違いの再確認・`agent.acp_backend` の既定値）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{claude-code-provider,agent-host-contract,harness-parity,harness-onboarding}.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

---

## 📑 このページの内容

- [概要](#概要)
- [セキュリティ上の重要な境界](#セキュリティ上の重要な境界)
- [有効化の手順](#有効化の手順)
- [選択できるハーネス](#選択できるハーネス)
- [ハーネスごとの機能差](#ハーネスごとの機能差)
- [バックエンドをまたいで同じもの](#バックエンドをまたいで同じもの)
- [設定キー](#設定キー)
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## 概要

**v0.6.0 で追加された Preview 機能です。既定では無効で、Developer Mode をオンにしないとセレクタが現れません**（公式ページ「The selector is a Preview feature and remains behind Developer Mode」）。

公式ページは「新しい Crew セッションを動かすハーネスを選ぶ」機能と説明しています。従来 Kiro Crew は Kiro CLI をランタイムとして固定的に使っていましたが、v0.6.0 で Claude Code・Codex・KAS が選択肢になり、**v0.7.0 で OpenCode・Pi・goose が加わりました**（[v0.7.0での変更](#v070での変更)）。公式ページは Kiro CLI を含む**7種**を挙げています。

リポジトリ側の仕様書では、`AgentConfig.provider` が受け付けるのは ACP プロバイダのみで、**ハーネスの選択は `provider` とは別のフィールド `agent.acp_backend`** であると記述されています（`claude-code-provider.md` 7行）。

> **⚠️ 本サイトの位置づけ**: 本ページは Kiro Crew Gateway 側の「どのハーネスを使うか」という選択機構を扱います。Claude Code・Codex・KAS・OpenCode・Pi・goose それぞれの単体機能は本サイトの対象外です。Kiro CLI 単体の機能は [猫でもわかるKiro CLI](https://github.com/kamogashira-sys/q-cli-docs) を参照してください。

## セキュリティ上の重要な境界

**Claude の設定で事前承認されたツール呼び出しは、Kiro Crew の承認パスに到達しません。**

CHANGELOG v0.6.0 節は「A tool pre-approved in Claude's own settings never reaches Crew's approval path, so its deny rules and audit log do not see that call」と記述します。公式ページも「A tool pre-approved in Claude Code's own settings can bypass Crew's approval flow, so Crew's deny and audit layers do not observe that call」と明記しています（Page updated 2026-09-25。v0.6.0 時点の同ページは「Claude tools pre-approved in Claude's own settings bypass Crew approvals」）。

リポジトリ側の仕様書はこの仕組みをより詳しく説明しています。

| 出典（`claude-code-provider.md`） | 記述 |
|---|---|
| 92-94行 | ふつうの呼び出しは `hooks.on_tool_call`・拒否ルール・機密パス検査・書き込み保護設定の検査・SEL の判定記録を通る。「A Claude session is governed like any other on that path」 |
| 96-100行 | 「**What escapes is a call that was already pre-approved, because it never asks.**」SDK は固定順で権限を評価し、`allow` ルールは step 5、コールバックは step 6 にある。Anthropic の文書は「Auto-approved tools never reach `canUseTool`」と太字で明記しており、コールバックが呼ばれない＝ACP リクエストが発生しないため、**その呼び出しについて Crew が検査・記録できるものが存在しない** |
| 304-310行 | ユーザーのグローバル設定（`~/.claude`）がツールファミリを事前承認している場合、それらは Claude 自身のエンジンで自動承認され `canUseTool` を呼ばず Crew のゲートに到達しない。**プロジェクトファイル側からも閉じられない**（Crew が作成していない `settings.local.json` は書き換えを辞退するため、ユーザー自身のプロジェクトファイルの `allow` エントリはそのまま残る） |

つまり **Claude Code バックエンドを選ぶと、Crew の拒否ルールと監査ログ（SEL）が見ない経路が生まれます**。セキュリティモデル全体は [09_security.md](09_security.md) を参照してください。

**Codex はサンドボックスが off の状態では起動しません**（CHANGELOG v0.6.0 節「Codex refuses to start while the sandbox is off」。公式ページ（Page updated 2026-09-25）は「Codex refuses to start while `agent.sandbox` is `off`」）。サンドボックスの設定は [09_security.md](09_security.md) と [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。

**OpenCode・Pi・goose は、最初のプロンプトの前に権限モードまたはゲートが検証されます**（公式ページ「Crew verifies the required permission mode or gate for OpenCode, Pi, and goose before allowing the first prompt」）。Pi について CHANGELOG は、ツール権限のゲートを検証できないセッションを Kiro Crew が拒否すると記述します（CHANGELOG v0.7.0 節 284-287行）。

## 有効化の手順

公式ページ（Page updated 2026-09-25）の手順です。

1. **Settings → Developer** を開き **Developer Mode** をオンにする（既定はオフ）
2. **Developer → Agent Backend** を開く
3. 使いたいバックエンドの **capability card** と導入状態を確認する
4. 選択し、新しいセッションを開始する

セレクタは不足しているコンポーネントを示し、対応するインストールコマンドを表示します。**実行中のセッションは開始時のバックエンドを維持します。**

> v0.6.0 時点の公式ページ（Page updated 2026-09-12）は、手順3を「Kiro CLI / Claude Code / Codex / KAS から選ぶ」とし、各バックエンドに「インストール済み／未インストール／インストール済みだが Gateway 再起動待ち」を表示すると記述していました。

## 選択できるハーネス

公式ページ（Page updated 2026-09-25）が挙げる**7種**です。OpenCode・Pi・goose は v0.7.0 で追加されました（**Preview・Developer Mode**）。

| バックエンド | 公式ページの説明 |
|---|---|
| **Kiro CLI** | **既定のバックエンド**。Crew との統合が最も完全で、MCP 設定の変更が実行中に反映される |
| **Claude Code** | Claude の agent adapter 経由で動き、Crew の MCP サーバをセッションごとに受け取る |
| **KAS** | Kiro CLI の ACP relay を通じて Kiro agent harness を動かす |
| **Codex** | Codex ACP adapter を使う。Crew のサンドボックスが必須。compaction に対応 |
| **OpenCode** | `opencode` バイナリを使う。Crew の MCP サーバを受け取り、compaction に対応 |
| **Pi** | `pi` と `pi-acp` の**両方**が必要。**Kiro Crew の MCP ツールを受け取らない** |
| **goose** | `goose` バイナリを使う。権限モードの検証後に Crew の MCP サーバを受け取る |

**⚠️ 出典間で選択肢の数が食い違っています。本サイトは裁定せず両方を記載します。**

| 出典 | 選択できるハーネス |
|---|---|
| 公式ページ `features/agent-backends/`（Page updated 2026-09-25） | **7種**（Kiro CLI / Claude Code / KAS / Codex / OpenCode / Pi / goose）。v0.6.0 時点（Page updated 2026-09-12）は4種（Kiro CLI / Claude Code / Codex / KAS） |
| CHANGELOG v0.6.0 節 703-706行・v0.7.0 節 271-274行・284-287行・415-418行（`c67c506`） | v0.6.0 で「Claude Code, Codex and KAS are selectable harnesses」、v0.7.0 で OpenCode・Pi・goose が選択可能に |
| `agent-host-contract.md` 86-93行（`c67c506`） | Codex・OpenCode・Pi・goose をそれぞれ「Selectable on a public build」と記述。DeepSeek（`ACP_BACKEND_DEEPSEEK`）は「KNOWN but **not selectable** on a public build」。なお同ファイル9-10行は「Five backends are described, and all five are selectable」と記述しており、表の行数（8行）と一致しません |
| `harness-parity.md` 20-29行（`c67c506`） | `BASELINE_SELECTABLE_BACKENDS` は `ACP_BACKENDS_KNOWN` と同じで、例外は `ACP_BACKEND_DEEPSEEK`（`NOT_SHIPPED_SELECTABLE`）の1件のみ。31-34行は Codex を「以前の例外で、条件を満たしてその集合を離れた」と記述 |
| `claude-code-provider.md` 7-11行（`c67c506`） | **v0.7.2 でも** `acp_backends.BASELINE_SELECTABLE_BACKENDS` は **`ACP_BACKEND_KIRO`（空文字列）・`ACP_BACKEND_CLAUDE`・`ACP_BACKEND_KAS` の3件**を含み「i.e. all of `ACP_BACKENDS_KNOWN`」と記述する（v0.6.0 から変化なし）。`test_baseline_ships_every_known_backend` がこの同値をピン留めしている |

`harness-onboarding.md` は、ハーネスの状態を **Dormant**（`ACP_BACKENDS_KNOWN` に id はあるが選択不可）と **Selectable**（`BASELINE_SELECTABLE_BACKENDS` にある、またはエディションが追加する）に区別しています（21-29行、`c67c506`）。v0.7.2 の同ファイルは Codex・OpenCode・DeepSeek・Pi・goose の onboarding を worked example として記述し（460行・482行・508行・597行・635行）、DeepSeek を「NOT selectable」、goose を「IS selectable」としています（511行・639行）。

**公式ページ・CHANGELOG・`agent-host-contract.md`・`harness-parity.md` は Codex などを選択可能として挙げ、`claude-code-provider.md` は `BASELINE_SELECTABLE_BACKENDS` を3件と記述します。どちらが最終的に正か・エディションによる差なのかは公式に説明がないため、本サイトは裁定しません。**

## ハーネスごとの機能差

公式ページ（Page updated 2026-09-25）は、Crew が最初のプロンプトの前にバックエンドが公開する権限パスを検査し、**Developer → Agent Backend の capability card** がモデル・推論・compaction・steering・MCP・セッション再開の対応状況の現行の情報源であると記述します。特に重要な制約として次の2点を挙げています。

- **Pi には Crew の MCP サーフェスがありません。** Pi は自身のツールを動かせますが、`pi-acp` が MCP サーバの配列を転送しません。Crew のメモリ・スケジューリング・Subagent などの MCP ツールが必要なセッションでは別のバックエンドを選びます。この状態は `kirocrew doctor` が報告します
- **OpenCode はサーバ単位でフィルタします。** ある Crew MCP サーバのツールを1つでも無効にすると、Crew はツールの一部だけを見せるのではなく、そのサーバ全体を OpenCode のセッションから外します

compaction は Codex と OpenCode のセッションで対応しています。

## バックエンドをまたいで同じもの

公式ページ（Page updated 2026-09-25）は、次の機能がすべてのバックエンドで動くと記述します。ただし「subject to what the capability card reports for the selected harness」（選択したハーネスについて capability card が報告する内容の範囲で）という条件が付いています。v0.6.0 時点の公式ページは「Crew keeps the same session controls across the selectable backends」と、条件なしで記述していました。

- 監視の操作（Monitor controls。v0.6.0 時点の公式ページでは Monitor loops）
- プロジェクトの変更（project changes）
- フォローアップカード（follow-up cards）
- 会話のリセット（conversation reset）

CHANGELOG v0.6.0 節は、これらが**従来は Kiro CLI 以外では fail closed になっていた**（"where they previously failed closed outside Kiro CLI"）と記述します。

## 設定キー

値と既定値の一覧は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。本ページでは重複させません。

| キー | 用途 |
|---|---|
| `agent.acp_backend` | ハーネスの選択。**既定は `ACP_BACKEND_KIRO`（Kiro CLI）**で、何も設定していない場合も、設定値が使えない場合も Kiro ハーネスになります（`harness-parity.md` 84行「H1」、`c67c506`。公式ページも Kiro CLI を「Default backend」と記述）。`acp_backends.resolve_selected_backend()` が値を正規化する（`claude-code-provider.md` 25行）。ゲートは1箇所に集約されている（同319行） |

## v0.7.0での変更

すべて **Preview** で、**Developer Mode**（Settings → Developer）をオンにした場合にだけ選べます。

- **OpenCode が選択肢に加わった**: Gateway ホストに `opencode` バイナリをインストールし、Developer ページの Agent Backend タブで選びます（CHANGELOG 271-274行）
- **Crew 自身のツールが OpenCode と Codex のセッションにも届く**: Claude と同じ方法で届きます。ただし OpenCode のセッションは、Crew のサーバのツールが1つでも無効化されていると、そのサーバ全体を外します（CHANGELOG 275-277行）
- **Codex でポリシーにブロックされたツール呼び出しが、チャットを黙って終了させなくなった**。インストール済みの App が登録するエージェントは KAS で起動し、ファイル名ではなく宣言した名前で解決されます（CHANGELOG 278-280行）
- **Pi が選択肢に加わった**: Gateway に `pi` と `pi-acp` の両方をインストールします。セレクタは不足しているコンポーネントを示し、ツール権限のゲートを検証できないセッションは拒否されます。**Pi のセッションは Kiro Crew の MCP ツールを持たない**ため（`kirocrew doctor` が報告）、Subagent・スケジューリング・メモリのツールが必要な場合は別のバックエンドを選びます（CHANGELOG 284-290行）
- **バックエンドの一覧化と goose の追加**: Developer → Agent Backend が、行ごとに capability card（できること・MCP 設定の扱い）を持つハーネスの一覧になりました。goose が選択可能なバックエンドに加わり、Codex と OpenCode のセッションが compaction に対応しました（CHANGELOG 415-418行）
- **修正**: 管理された KAS バックエンドのセッションがタイムアウトせずに開始する、バックエンドのツール承認プロンプトがキャンセルとして読まれずに届く、codex・opencode・goose・pi のセッションが最初のプロンプトの前に拒否されなくなった（CHANGELOG 612-615行）

出典: CHANGELOG.md v0.7.0節（`c67c506`）、<https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-09-25）。

## 未確認事項

- Codex・OpenCode・Pi・goose が `BASELINE_SELECTABLE_BACKENDS` に含まれるかどうか（上記のとおり `claude-code-provider.md` と他の出典で食い違う）
- KAS の正式名称（公式ページは「Runs the Kiro agent harness through Kiro CLI's ACP relay」、`agent-host-contract.md` 87行は「Kiro's agent service, run through `kiro-cli acp --agent-engine v3 --auth-method cli`」と記述するが、略称の展開は確認できていない。`kas-auth.md` は本サイトでは未精読）
- capability card に表示される項目の値（公式ページは card を現行の情報源とするが、ハーネスごとの値は一覧化していない。`harness-parity.md` の全体は本サイトでは未精読）

> **解消済み**: 「`agent.acp_backend` の既定値」は、`harness-parity.md` 84行（`c67c506`。v0.6.0（`8575209`）でも74行に同じ記述）で `ACP_BACKEND_KIRO` と確認できたため未確認事項から除きました（上記「設定キー」節参照）。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/agent-backends/>
- 公式（セキュリティ）: <https://kiro.dev/docs/crew/security/>
- セキュリティモデル: [09_security.md](09_security.md)
- アーキテクチャ: [01_architecture.md](01_architecture.md)
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

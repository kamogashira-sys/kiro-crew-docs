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
**出典**: <https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-10-12）・<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
**出典**（v0.8.0・v0.9.0での変更・選択肢の食い違いの解消・Claude のセキュリティ表の再確認・`agent.acp_backend` の既定値の再確認）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{claude-code-provider,agent-host-contract,harness-parity,harness-onboarding}.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.8.0・v0.9.0での変更）: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [概要](#概要)
- [セキュリティ上の重要な境界](#セキュリティ上の重要な境界)
- [有効化の手順](#有効化の手順)
- [選択できるハーネス](#選択できるハーネス)
- [ハーネスごとの機能差](#ハーネスごとの機能差)
- [バックエンドをまたいで同じもの](#バックエンドをまたいで同じもの)
- [設定キー](#設定キー)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## 概要

**v0.6.0 で追加された Preview 機能です。既定では無効で、Developer Mode をオンにしないとセレクタが現れません**（公式ページ「The selector is a Preview feature and remains behind Developer Mode」）。

公式ページは「新しい Crew セッションを動かすハーネスを選ぶ」機能と説明しています。従来 Kiro Crew は Kiro CLI をランタイムとして固定的に使っていましたが、v0.6.0 で Claude Code・Codex・KAS が選択肢になり、**v0.7.0 で OpenCode・Pi・goose が加わり**（[v0.7.0での変更](#v070での変更)）、**v0.8.0 で DeepSeek Harness が加わりました**（[v0.8.0での変更](#v080での変更)）。公式ページ（Page updated 2026-10-12）は Kiro CLI を含む**8種**を挙げています。

リポジトリ側の仕様書では、`AgentConfig.provider` が受け付けるのは ACP プロバイダのみで、**ハーネスの選択は `provider` とは別のフィールド `agent.acp_backend`** であると記述されています（`claude-code-provider.md` 7行）。

> **⚠️ 本サイトの位置づけ**: 本ページは Kiro Crew Gateway 側の「どのハーネスを使うか」という選択機構を扱います。Claude Code・Codex・KAS・OpenCode・Pi・goose・DeepSeek Harness それぞれの単体機能は本サイトの対象外です。Kiro CLI 単体の機能は [猫でもわかるKiro CLI](https://github.com/kamogashira-sys/q-cli-docs) を参照してください。

## セキュリティ上の重要な境界

**Claude の設定で事前承認されたツール呼び出しは、Kiro Crew の承認パスに到達しません。**

CHANGELOG v0.6.0 節は「A tool pre-approved in Claude's own settings never reaches Crew's approval path, so its deny rules and audit log do not see that call」と記述します。公式ページも「A tool pre-approved in Claude Code's own settings can bypass Crew's approval flow, so Crew's deny and audit layers do not observe that call」と明記しています（Page updated 2026-10-12。v0.6.0 時点の同ページは「Claude tools pre-approved in Claude's own settings bypass Crew approvals」）。

リポジトリ側の仕様書はこの仕組みをより詳しく説明しています。

| 出典（`claude-code-provider.md`） | 記述 |
|---|---|
| 96行 | ふつうの呼び出しは `hooks.on_tool_call`・拒否ルール・機密パス検査・書き込み保護設定の検査・SEL の判定記録を通る。「A Claude session is governed like any other on that path」 |
| 99-106行 | 「**What escapes is a call that was already pre-approved, because it never asks.**」SDK は固定順で権限を評価し、`allow` ルールは step 5、コールバックは step 6 にある。Anthropic の文書は「Auto-approved tools never reach `canUseTool`」と太字で明記しており、コールバックが呼ばれない＝ACP リクエストが発生しないため、**その呼び出しについて Crew が検査・記録できるものが存在しない** |
| 569-587行 | ユーザーのグローバル設定（`~/.claude`）がツールファミリを事前承認している場合、それらは Claude 自身のエンジンで自動承認され `canUseTool` を呼ばず Crew のゲートに到達しない（既知のギャップ。`CLAUDE_CONFIG_DIR` による分離は未実装）。`permissions.allow` のエントリはマージされる。プロジェクト自身の `settings.local.json` についての記述は v0.9.0 で変わり、Crew のツールを持つセッションは Crew が作ったシード（作成したものまたは共有したもの）を管理するか、プロジェクト層を設定ソースから除くため、このギャップの対象外と記述される（576-579行）。チェックイン済みの `.claude/settings.json` は、そのファイルを Crew が作成したセッションに限ってギャップの対象（v0.8.0 の同ファイル 336-348行は「Crew does not close this from the project file either」と記述していた） |

つまり **Claude Code バックエンドを選ぶと、Crew の拒否ルールと監査ログ（SEL）が見ない経路が生まれます**。セキュリティモデル全体は [09_security.md](09_security.md) を参照してください。

**Codex はサンドボックスが off の状態では起動しません**（CHANGELOG v0.6.0 節「Codex refuses to start while the sandbox is off」。公式ページ（Page updated 2026-10-12）は「Codex refuses to start while `agent.sandbox` is `off`」）。サンドボックスの設定は [09_security.md](09_security.md) と [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。

**OpenCode・Pi・goose は、最初のプロンプトの前に権限モードまたはゲートが検証されます**（公式ページ「Crew verifies the required permission mode or gate for OpenCode, Pi, and goose before allowing the first prompt」）。Pi について CHANGELOG は、ツール権限のゲートを検証できないセッションを Kiro Crew が拒否すると記述します（CHANGELOG v0.7.0 節 284-287行）。DeepSeek Harness については、`harness-parity.md`（27-34行）が、Crew がゲートプラグインをハーネスに組み込み、そのロードマーカーを最初のプロンプトの前に読み戻す（`Routing.VERIFIED_GATE_EXTENSION`）と記述しています。DeepSeek Harness は自前のサンドボックスがツール呼び出しを決めるため、この経路を経ないと Crew の PreToolUse ゲートが動かない、と同ファイルは記述します。

## 有効化の手順

公式ページ（Page updated 2026-10-12）の手順です。

1. **Settings → Developer** を開き **Developer Mode** をオンにする（既定はオフ）
2. **Developer → Agent Backend** を開く
3. 使いたいバックエンドの **capability card** と導入状態を確認する
4. 選択し、新しいセッションを開始する

セレクタは不足しているコンポーネントを示し、対応するインストールコマンドを表示します。**実行中のセッションは開始時のバックエンドを維持します。**

> v0.6.0 時点の公式ページ（Page updated 2026-09-12）は、手順3を「Kiro CLI / Claude Code / Codex / KAS から選ぶ」とし、各バックエンドに「インストール済み／未インストール／インストール済みだが Gateway 再起動待ち」を表示すると記述していました。

## 選択できるハーネス

公式ページ（Page updated 2026-10-12）が挙げる**8種**です。OpenCode・Pi・goose は v0.7.0 で、DeepSeek Harness は v0.8.0 で追加されました（**Preview・Developer Mode**）。

| バックエンド | 公式ページの説明 |
|---|---|
| **Kiro CLI** | **既定のバックエンド**。Crew との統合が最も完全で、MCP 設定の変更が実行中に反映される |
| **Claude Code** | Claude の agent adapter 経由で動き、Crew の MCP サーバをセッションごとに受け取る |
| **KAS** | Kiro CLI の ACP relay を通じて Kiro agent harness を動かす |
| **Codex** | Codex ACP adapter を使う。Crew のサンドボックスが必須。compaction に対応 |
| **OpenCode** | `opencode` バイナリを使う。Crew の MCP サーバを受け取り、compaction に対応 |
| **Pi** | `pi` と `pi-acp` の**両方**が必要。**Kiro Crew の MCP ツールを受け取らない** |
| **goose** | `goose` バイナリを使う。権限モードの検証後に Crew の MCP サーバを受け取る |
| **DeepSeek Harness** | `dsh --profile acp` を動かす。Gateway ホストに `dsh` をインストールし、プロバイダのキーを Settings → Secrets から `agent.deepseek_env` で対応づける |

**選択肢の数の食い違いは v0.9.0 で解消しました。** v0.9.0 時点では、次の出典がいずれも、Kiro CLI・Claude Code・KAS・Codex・OpenCode・Pi・goose・DeepSeek Harness の **8種**を公開ビルドで選択可能と記述しています。

| 出典 | 記述 |
|---|---|
| 公式ページ `features/agent-backends/`（Page updated 2026-10-12） | **8種**（冒頭の列挙順は Kiro CLI / KAS / Claude Code / Codex / OpenCode / Pi / goose / DeepSeek Harness）。v0.7.2 時点（Page updated 2026-09-25）は7種、v0.6.0 時点（Page updated 2026-09-12）は4種 |
| CHANGELOG v0.8.0節 405-410行（`99e6253`） | DeepSeek Harness が選択可能なバックエンドに加わった（Developer Mode をオンにし、`dsh` をインストールして選ぶ） |
| `claude-code-provider.md` 7-14行（`99e6253`） | 公開ベースラインが選択できるのは、kiro-cli（`ACP_BACKEND_KIRO`、空文字列）・Claude・KAS・Codex・OpenCode・Pi・goose・DeepSeek の `ACP_BACKENDS_KNOWN` のすべての id。`test_baseline_ships_every_known_backend` が `ACP_BACKENDS_KNOWN - NOT_SHIPPED_SELECTABLE` をピン留めし、`NOT_SHIPPED_SELECTABLE` は空 |
| `agent-host-contract.md` 9-14行・83-91行（`99e6253`） | 8つのバックエンドを記述し、「all eight are selectable on a plain public build」。DeepSeek は Crew が組み込んだゲートプラグイン経由で、ツール呼び出しが Crew の許可ゲートに届くため選択可能 |
| `harness-parity.md` 14行・22-34行（`99e6253`） | 8つが公開ビルドで選択可能。例外は現在なし（`NOT_SHIPPED_SELECTABLE` は空）。DeepSeek は直近の例外で、Crew がゲートプラグインを組み込む経路でその集合を離れた |

履歴: v0.7.2 時点では、公式ページが7種、`claude-code-provider.md` が `BASELINE_SELECTABLE_BACKENDS` を kiro-cli・Claude・KAS の3件と記述し、`agent-host-contract.md` は DeepSeek を「KNOWN but not selectable」と記述していました（同ファイル9-10行は「Five backends…all five」と記述し、表の行数と一致していませんでした）。v0.9.0 の `claude-code-provider.md` と `agent-host-contract.md` は上表のとおり8つに更新されています。

`harness-onboarding.md` は、ハーネスの状態を **Dormant**（`ACP_BACKENDS_KNOWN` に id はあるが選択不可）と **Selectable**（`BASELINE_SELECTABLE_BACKENDS` にある、またはエディションが追加する）に区別しています（21-29行）。同ファイルの「Worked example: the DeepSeek Harness」（570行以降）は、DeepSeek を Selectable としています（572-575行・585行）。

## ハーネスごとの機能差

公式ページ（Page updated 2026-10-12）は、Crew が最初のプロンプトの前にバックエンドが公開する権限パスを検査し、**Developer → Agent Backend の capability card** がモデル・推論・compaction・steering・MCP・セッション再開の対応状況の現行の情報源であると記述します。特に重要な制約として次の2点を挙げています。

- **Pi には Crew の MCP サーフェスがありません。** Pi は自身のツールを動かせますが、`pi-acp` が MCP サーバの配列を転送しません。Crew のメモリ・スケジューリング・Subagent などの MCP ツールが必要なセッションでは別のバックエンドを選びます。この状態は `kirocrew doctor` が報告します
- **OpenCode はサーバ単位でフィルタします。** ある Crew MCP サーバのツールを1つでも無効にすると、Crew はツールの一部だけを見せるのではなく、そのサーバ全体を OpenCode のセッションから外します

compaction は Codex と OpenCode のセッションで対応しています。

## バックエンドをまたいで同じもの

公式ページ（Page updated 2026-10-12）は、次の機能がすべてのバックエンドで動くと記述します。ただし「subject to what the capability card reports for the selected harness」（選択したハーネスについて capability card が報告する内容の範囲で）という条件が付いています。v0.6.0 時点の公式ページは「Crew keeps the same session controls across the selectable backends」と、条件なしで記述していました。

- 監視の操作（Monitor controls。v0.6.0 時点の公式ページでは Monitor loops）
- プロジェクトの変更（project changes）
- フォローアップカード（follow-up cards）
- 会話のリセット（conversation reset）

CHANGELOG v0.6.0 節は、これらが**従来は Kiro CLI 以外では fail closed になっていた**（"where they previously failed closed outside Kiro CLI"）と記述します。

## 設定キー

値と既定値の一覧は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。本ページでは重複させません。

| キー | 用途 |
|---|---|
| `agent.acp_backend` | ハーネスの選択。**既定は `ACP_BACKEND_KIRO`（Kiro CLI）**で、何も設定していない場合も、設定値が使えない場合も Kiro ハーネスになります（`harness-parity.md` 89行「H1」、`99e6253`。v0.7.2 では 84行。公式ページも Kiro CLI を「Default backend」と記述）。`acp_backends.resolve_selected_backend()` が値を正規化する（`claude-code-provider.md` 26行）。ゲートは1箇所に集約されている（同589-590行） |
| `agent.deepseek_env` | DeepSeek Harness の環境変数名を `secret://` の vault 参照に対応づける（既定は空。公式 Configuration ページ Page updated 2026-10-20 の設定表）。[v0.8.0での変更](#v080での変更)を参照 |

## v0.9.0での変更

本節の内容は v0.9.0 タグの CHANGELOG と仕様書で確認したものです。

- **KAS で予約名のテンプレートを持つ crewmate が動く**: KAS エンジンが予約している名前（`default` など）をテンプレートが使う crewmate は、拒否されずに KAS で動くようになりました。待機するツールが同じセッションの他のツールを止めることもなくなりました（CHANGELOG v0.9.0節 182-185行）
- **選択肢の食い違いの解消**: 上記「[選択できるハーネス](#選択できるハーネス)」のとおり、v0.9.0 の仕様書は8種を公開ビルドで選択可能と記述し、公式ページ・CHANGELOG と一致しました
- **Claude の既知のギャップの記述が変わった**: 上記「[セキュリティ上の重要な境界](#セキュリティ上の重要な境界)」の表の第3行を参照してください（`claude-code-provider.md` 569-587行）

出典: CHANGELOG.md v0.9.0節、`claude-code-provider.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

## v0.8.0での変更

すべて **Preview** で、**Developer Mode**（Settings → Developer）をオンにした場合にだけ選べます。

- **DeepSeek Harness が選択肢に加わった**: Developer Mode をオンにし、Gateway ホストに `dsh` をインストールして、Developer ページの Agent Backend タブで選びます（CHANGELOG v0.8.0節 405-410行）。プロバイダのキーは、環境変数名を Settings → Secrets のエントリに対応づける `agent.deepseek_env` で渡します（公式 Configuration ページ Page updated 2026-10-20、公式 Agent Backends ページ Page updated 2026-10-12）。公式ページは起動を `dsh --profile acp` と記述します
- **キーの渡し方（仕様書）**: `harness-onboarding.md` 625-645行は、Crew が自身の secret vault からキーを渡し（`entitlement_source = host_vault`）、ハーネス側の subprocess 層が `/KEY|PASSWORD|SECRET|TOKEN/i` に一致する継承環境変数を子プロセスに渡さないという性質に依存すると記述しています。この性質は spawn 時に canary で検証され、守られていなければ Crew はセッションを拒否します。同ファイルは、キーはハーネスのプロセス自身の環境には残ると記述します。この内容は仕様書だけにあり、CHANGELOG と公式ページは説明していません
- **ツール呼び出しの経路**: DeepSeek Harness は自前のサンドボックスがツール呼び出しを決めるため、Crew はゲートプラグインを組み込み、そのロードマーカーを最初のプロンプトの前に読み戻して、ツール呼び出しが Crew の許可ゲートに届くことを確認します（`harness-parity.md` 27-34行、`harness-onboarding.md` 570-590行）
- **KAS**: ダッシュボードのトランスクリプトに出るウェルカムメッセージと Powers が、KAS のセッションにも届くようになりました（CHANGELOG v0.8.0節 415-416行）。エージェント仕様のフックと権限が KAS バックエンドで効くようになり、KAS 上の sub-agent の起動が拒否されずに承認カードに届くようになったこと（同 558-560行）、KAS バックエンドで Kiro Crew のツール呼び出しがすべて「unattested」として拒否されていた不具合が直ったこと（同 648-649行）も、CHANGELOG は記述しています

出典: CHANGELOG.md v0.8.0節、<https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）、`harness-parity.md`・`harness-onboarding.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

## v0.7.0での変更

すべて **Preview** で、**Developer Mode**（Settings → Developer）をオンにした場合にだけ選べます。

- **OpenCode が選択肢に加わった**: Gateway ホストに `opencode` バイナリをインストールし、Developer ページの Agent Backend タブで選びます（CHANGELOG 271-274行）
- **Crew 自身のツールが OpenCode と Codex のセッションにも届く**: Claude と同じ方法で届きます。ただし OpenCode のセッションは、Crew のサーバのツールが1つでも無効化されていると、そのサーバ全体を外します（CHANGELOG 275-277行）
- **Codex でポリシーにブロックされたツール呼び出しが、チャットを黙って終了させなくなった**。インストール済みの App が登録するエージェントは KAS で起動し、ファイル名ではなく宣言した名前で解決されます（CHANGELOG 278-280行）
- **Pi が選択肢に加わった**: Gateway に `pi` と `pi-acp` の両方をインストールします。セレクタは不足しているコンポーネントを示し、ツール権限のゲートを検証できないセッションは拒否されます。**Pi のセッションは Kiro Crew の MCP ツールを持たない**ため（`kirocrew doctor` が報告）、Subagent・スケジューリング・メモリのツールが必要な場合は別のバックエンドを選びます（CHANGELOG 284-290行）
- **バックエンドの一覧化と goose の追加**: Developer → Agent Backend が、行ごとに capability card（できること・MCP 設定の扱い）を持つハーネスの一覧になりました。goose が選択可能なバックエンドに加わり、Codex と OpenCode のセッションが compaction に対応しました（CHANGELOG 415-418行）
- **修正**: 管理された KAS バックエンドのセッションがタイムアウトせずに開始する、バックエンドのツール承認プロンプトがキャンセルとして読まれずに届く、codex・opencode・goose・pi のセッションが最初のプロンプトの前に拒否されなくなった（CHANGELOG 612-615行）

出典: CHANGELOG.md v0.7.0節（`c67c506`）、<https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-09-25。v0.9.0 時点の同ページは DeepSeek Harness の追加を除いて差分なし）。

## 未確認事項

- KAS の正式名称（公式ページは「Runs the Kiro agent harness through Kiro CLI's ACP relay」、`agent-host-contract.md` 85行は「Kiro's agent service, run through `kiro-cli acp --agent-engine v3 --auth-method cli`」と記述するが、略称の展開は確認できていない。`kas-auth.md` は本サイトでは未精読）
- capability card に表示される項目の値（公式ページは card を現行の情報源とするが、ハーネスごとの値は一覧化していない。`harness-parity.md` の全体は本サイトでは未精読）

> **解消済み**:
>
> - 「`agent.acp_backend` の既定値」: `harness-parity.md` 89行（`99e6253`。v0.7.2（`c67c506`）では84行、v0.6.0（`8575209`）では74行）で `ACP_BACKEND_KIRO` と確認できています（上記「設定キー」節参照）
> - 「Codex・OpenCode・Pi・goose が `BASELINE_SELECTABLE_BACKENDS` に含まれるか」と選択肢の数の食い違い: v0.9.0 では公式ページ・CHANGELOG・仕様書が8種で一致しました（上記「選択できるハーネス」節参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/agent-backends/>
- 公式（セキュリティ）: <https://kiro.dev/docs/crew/security/>
- セキュリティモデル: [09_security.md](09_security.md)
- アーキテクチャ: [01_architecture.md](01_architecture.md)
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

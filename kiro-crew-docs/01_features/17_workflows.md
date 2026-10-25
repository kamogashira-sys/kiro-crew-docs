# Workflows（conductor・ワークフローライブラリ）

> **本ページは Kiro Crew（OSS）の仕様です。**
> Kiro CLI / Kiro IDE / Kiro Web の同名機能とは仕様が異なる場合があります。
> Crew は main ブランチが日次で動く OSS のため、仕様が変わることがあります。

**出典**: <https://kiro.dev/docs/crew/features/workflows/>
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/workflows.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/pipeline-conductor.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
**出典**: <https://kiro.dev/docs/crew/features/workflows/>（Page updated 2026-09-25）
**出典**（v0.7.0での変更・永続化されたワークフロー呼び出し）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{workflows,taskq}.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/features/workflows/>（Page updated 2026-10-12）・<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
**出典**（v0.8.0・v0.9.0での変更・ライブラリの保存先・`ctx` の概要）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{workflows,decisions,babysit-pr-watch,agent-interrupt-controller,monitor-architecture,session-work-ledger,pipeline-conductor}.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.8.0・v0.9.0での変更）: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [概要](#概要)
- [Subagent・Task Runner との使い分け](#subagenttask-runner-との使い分け)
- [使う場面のパターン](#使う場面のパターン)
- [`session_send`（セッション横断のメッセージ配送）](#session_sendセッション横断のメッセージ配送)
- [組み込みの conductor](#組み込みの-conductor)
- [グローバルワークフローライブラリ](#グローバルワークフローライブラリ)
- [エージェントが制御する監視ループ](#エージェントが制御する監視ループ)
- [Workflows アプリ](#workflows-アプリ)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## 概要

**v0.5.0 で conductor とワークフローライブラリが追加され、v0.6.0 で監視ループのエージェント制御などが加わりました。v0.7.0 では PR の structured watch とワークフロー呼び出しの永続化が加わり**（[v0.7.0での変更](#v070での変更)）、**v0.8.0 で監視ループの起床判定（wake judge）と crew log の既定オンが、v0.9.0 で conductor の既定パトロールが加わりました**（[v0.8.0での変更](#v080での変更)・[v0.9.0での変更](#v090での変更)）。

公式ページはワークフローを「**明示的なステージを通じて多数のエージェントをオーケストレーションする、人が書いた Python スクリプト**」と定義し、並列実行・出力の連結・次へ進む前の結果検査を行うと説明します。

公式ページは「You rarely write one by hand: describe the goal in plain English and the agent usually authors the script for you」とも記述しています（多くの場合エージェントがスクリプトを書く）。

## Subagent・Task Runner との使い分け

公式ページが示す使い分けです。

| 用途 | 使うもの | 参照 |
|---|---|---|
| **仕様書からの単一の自律実行** | Task Runner | [06_autonomy.md](06_autonomy.md) |
| **会話内のアドホックな並列実行** | Subagent | [06_autonomy.md](06_autonomy.md) |
| **多数のエージェントにまたがる再現可能な構造** | **Workflows**（本ページ） | — |

公式ページは「Workflows are for when you need repeatable structure across many agents」と記述します。また「Under the hood, a workflow coordinates the same background agents you can spawn yourself」とあり、各ステージは Subagent にファンアウトして結果を待ち、合成した出力を次のステージへ渡します。**ワークフロースクリプトが構造（どのステージがどの順で走るか、「完了」の定義）を持ち、各エージェントが実作業を行います。**

## 使う場面のパターン

公式ページが挙げる3パターンです。

| パターン | 内容 | 公式の例 |
|---|---|---|
| **Fan-out** | 同じステップを多数の入力に対して並列実行する | PR で変更されたすべてのファイルを一度にレビューする |
| **Pipeline** | あるステージの出力を次のステージへ渡す | Draft → critique → rewrite → format |
| **Judge-and-verify** | 結果を出したうえで別のエージェントに検査させる | 修正を生成し、それを仕様に対して検証する |

## `session_send`（セッション横断のメッセージ配送）

**v0.5.0 で追加されました。** `session_send` は他のセッションへ**その次のターンとして**メッセージを配送します。

公式ページは「A coordinator agent can direct peer sessions instead of only opening, reading, or stopping them. **This is the primitive underlying the conductor** and any cross-session orchestration pattern you build yourself」と記述します。従来はセッションを開く・読む・停止することしかできませんでした。

MCP ツールとしての詳細は [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md) を参照してください。

## 組み込みの conductor

conductor エージェントは**単一セッションでは大きすぎる目標**を扱います。公式ページの手順は次の4段です。

1. 目標を個別の作業項目に分解する
2. 各項目についてセッションを開始する
3. 完了した各セッションについて受け入れ基準を検査する
4. 結果に基づいて次のラウンドを決める（フォローアップの送信・再試行・終了）

**conductor は、タブを閉じてもターン上限に達しても生き残る監視ループの上で動きます**（"a monitoring loop that survives tab closes and turn caps"）。長時間の複数セッション計画が、離席中も進み続けます。

呼び出し方は「並列の作業ストリームに自然に分かれる目標を記述する」ことです（専用コマンドではありません）。

## グローバルワークフローライブラリ

セッションのワークフロー定義を**グローバルライブラリへ昇格**させ、セッションをまたいで再利用できます。

| 操作 | 場所 |
|---|---|
| バージョンと系譜（lineage）の管理 | **Agent Capabilities → Workflows**（公式ページの表記。画面名の食い違いは下記参照） |
| 保存済み定義の呼び出し | 任意のセッションで `/workflow <name>` |
| Task Runner の plan との共有 | 同じライブラリを共有するため、以前使った plan が名前付きワークフローとして利用できる |

**ライブラリ内のワークフローはバージョン管理されます。** リビジョン履歴を確認し、以前のバージョンへロールバックできます。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | ライブラリの管理場所の名称 |
> |---|---|
> | 公式 Workflows ページ（Page updated 2026-10-12） | **Agent Capabilities → Workflows** |
> | CHANGELOG v0.9.0節 150-151行（`99e6253`） | Agent Capabilities の名称が **Customize** になった |
> | `modules/workflows.md` 912行・932行（v0.9.0、`99e6253`） | **Customize > Workflows**（**Workflow library** と **Runs** の2つのビューを持つ） |

リポジトリの仕様書（`modules/workflows.md` 857-882行・1243行、v0.9.0）は、ライブラリを次のように記述しています。

- 保存したワークフローは1件につき1つの JSON ファイルとして `<KIROCREW_HOME>/workflow_library/<workflow_id>.json` に保存され、Kiro Crew のデータホーム全体で共有されます（Kiro や KAS などのハーネスからも同じライブラリです）。ラン スナップショットとは異なり、`workflows.dir` には従いません
- 定義は安定した `wfd_*` の ID、一意のスラッシュコマンド `slug`、現在のソース、SHA-256 のハッシュ、整数の `revision`、変更できない `revisions` を持ちます。更新には `expected_revision` が必要で、古い書き手は上書きではなく競合（409）を受け取ります
- 定義の作成・更新・実行への昇格は、アプリのトークンやエージェントの内部呼び出しではなく、認証されたダッシュボードのユーザー（ダッシュボード所有者）に限られます（同 869行・1214行）
- リビジョン数の上限は、読んだ範囲の仕様書に記述が見つかっていません（未確認）

> `/workflow` は**チャット内のコマンド**であり、`kirocrew` の CLI サブコマンドではありません。CLI コマンドの一覧は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) を参照してください。

## エージェントが制御する監視ループ

**v0.6.0 で追加されました。** 公式ページ（Page updated 2026-10-12）は、エージェントが**自分のセッションに結びついた**監視ループを開始・変更・**検査（inspect）**・停止できると記述します。単純なタイマーループ（`monitor_start`）は、ダッシュボードのチャット・Slack・Discord・**Webex** から使えます。

- goal chip は、待機中のループが実行中のターンと見分けられるよう、現在の**間隔（cadence）と予算（budget）**を表示します
- レビュー可能な PR に到達することが目的のときは、PR の structured watch（`monitor_watch`）を使います（v0.7.0。[v0.7.0での変更](#v070での変更)参照）

> v0.6.0 時点の公式ページ（Page updated 2026-09-12）は、操作を「開始・変更・停止」、利用場所を「ダッシュボード・Slack スレッド・Discord DM」とし、さらに次のように記述していました。**v0.7.2 時点の公式ページにはこれらの記述はありません。**
>
> - ループが1つの PR を名指しした場合、Crew はその PR が変化したときだけエージェントを起こす
> - goal chip にサイクル数と上限を表示する（例: `23/24`）
> - 承認が未応答のままループが停止した場合は、必要なアクセスを承認または再有効化してから再度 arm する
> - 監視ループは KAS バックエンドでも動く

**interrupt controller** は、対象となるポーリング型の cron を wake-on-change の割り込みに変え、静かな間隔にエージェントのターンを消費しないようにします。v0.9.0 時点の公式ページ（Page updated 2026-10-12）は対象を「an eligible polling cron」と記述しています（v0.7.2 時点も同じ記述。v0.6.0 時点は「any script cron」）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
>
> | 出典 | interrupt controller の対象 |
> |---|---|
> | 公式 Workflows ページ（Page updated 2026-10-12） | 対象となるポーリング型の cron（an eligible polling cron）を wake-on-change の割り込みに変える |
> | `modules/agent-interrupt-controller.md` 34-47行・`modules/babysit-pr-watch.md` 73-88行（v0.9.0、`99e6253`） | in-tree の driver は、AutoNudge の probe gate が呼ぶ `irq.poll` だけ。`gh-pr` の script/cron driver は廃止（retired）で、PR の監視には `monitor_watch` か有限の `monitor_start` ループを使う。廃止された driver のコピーを持つ cron ジョブが残っている場合は、probe がその文脈を拒否し、ジョブは連続失敗の閾値で自動停止（auto-paused）されて一覧に残る |
>
> 公式ページの「eligible polling cron」と、仕様書の `irq.poll` の関係は確認できていません。

### 監視ループの実行時間の上限

公式ページ（Page updated 2026-10-12）は、運用者の上限 `monitoring.max_runtime_secs` の既定が7日で、30日まで引き上げられると記述します。引き上げても、すでに動いているループに設定された期限は延びません。公式 Configuration ページ（Page updated 2026-10-20）の設定表も同じ値を示します。値の一覧は [04_reference/05_limits.md](../04_reference/05_limits.md) を参照してください。

## 長時間の作業

公式ページは「A chat turn can run for up to four hours」と記述します（v0.6.0 で `agent.chat_turn_timeout_secs` の既定が引き上げられました）。それより長い作業には監視ループまたは Task Runner を使い、ターン間も Crew が継続できるようにします。

タイムアウトの値は [04_reference/05_limits.md](../04_reference/05_limits.md) と [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md) を参照してください。本ページでは重複させません。

## Workflows アプリ

同梱の **Workflows** アプリは、ワークフローの作成・検証・実行監視を行うダッシュボード面を提供します。

**このアプリは無効かつメインのアプリカタログから隠された状態で出荷されます**（"It ships disabled and hidden from the main app catalog by default"）。CLI から有効化します。

```bash
kirocrew app enable workflows
```

有効化すると、サイドバーの `/workflows` にアプリが現れ、次のことができます。

- 実行前に、サンドボックス化された API に対してワークフロースクリプトを検証する
- 実行の進行に伴って各フェーズとエージェント単位のイベントを監視する
- 同梱の実行可能なサンプルから始める

### ワークフロースクリプトの `ctx`（仕様書の概要）

`modules/workflows.md` 91-175行（v0.9.0、`99e6253`）が定義するスクリプトの入口 `ctx` について、本サイトが確認できた範囲です。

- **入力**: `args`（run の引数）・`now`（呼び出し側が渡す、run 全体で固定された開始時刻の文字列）・`owner_dm`・`budget`（トークンの計上）。スクリプトからは `time`・`random`・`uuid`・`datetime` に到達できず、`ctx.now` が唯一の時計です
- **`ctx.agent(prompt, *, label, phase, schema, model, agent, effort, cwd, session, nudge)`**: 既定では呼び出しごとに新しい独立したセッション（Subagent）を使います。`session=<key>` を渡すと名前付きの共有セッションで動きます。`schema=` を渡すと検証済みの値か、再試行のあとの `None` になります。`agent()` が送出する例外は `BudgetExceeded` だけで、ほかの失敗は呼び出しごとに `None` になり、理由が記録されます（`modules/workflows.md` 154-163行）
- 仕様書自身が「Open question」として、`effort` と呼び出しごとの `nudge` は凍結されたシグネチャに含まれるが、同梱の実行関数がどちらも読まないため現状では効果がないと記述しています（同 170-173行）
- ほかに、同仕様書は `ctx` の節として Scheduling combinators・Concurrency・Progress・Budget・ports native to Kiro Crew を持ちます。これらの中身は本サイトでは確認できていません

## v0.9.0での変更

本節の内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG の v0.9.0 節は説明していません（画面名の変更を除く）。

- **画面名の変更**: CHANGELOG v0.9.0節 150-151行は、Agent Capabilities が **Customize** になったと記述します。ワークフローライブラリの管理場所の名称は、公式ページと仕様書で食い違っています（[グローバルワークフローライブラリ](#グローバルワークフローライブラリ)の表を参照）
- **conductor の既定パトロール**: 作業台帳（work ledger）に bind（`work_ledger_record` の `action=bind`）したとき、conductor のスロットにループが1つもなければ、ゲートウェイが既定のパトロールを自動で開始します。内容は `watch: "work-ledger"`、gated、600秒ごと、300サイクル、86400秒です。conductor 自身の `monitor_start`・`monitor_watch`、人のダッシュボードからの作成、チャネルからの開始は、有効な既定パトロールを置き換えます（409 にはなりません）。crew／member の conductor では拒否されます。既存の記録（有効・承認待ち・人が停止したもの）には触れません。bind の応答は `patrol: armed | existing | refused | unsupported` を返します（`modules/monitor-architecture.md` 126-160行）。v0.8.0 タグの仕様書にこの記述は見つかっていません
- **`work-ledger` 監視の静かな間隔の下限**: ワーカーからの報告がまだない間、ゲートされた `work-ledger` の監視は、静かな確認が続いても配送されるまでの回数が 10 ではなく 40 になります（`_IDLE_LEDGER_QUIET_FLOOR`）。新しいワーカーの報告があると 10 に戻ります（同 160-170行）
- **ワークフロー起動のルートはダッシュボード所有者に限られる**: ダッシュボードのユーザーからの要求で、ソース・intent・保存済み定義・再実行の起動（`POST /api/workflows/run`・`/run_intent`・`/definitions/{ref}/run`・`/runs/{run_id}/rerun`）を行うには、ダッシュボード所有者である必要があります（403 `owner_only`）。チャットの `workflow_*` MCP ツール（内部の呼び出し）とマニフェストで範囲が決まったアプリのトークンには、従来の制御が適用されます（`modules/workflows.md` 1205-1214行）。v0.7.2・v0.8.0 タグの仕様書に `owner_only` の記述は見つかっていません
- **公式ページの更新**: 公式 Workflows ページ（Page updated 2026-10-12）が、静かな確認の選別と、PR の watch の起床条件と終了条件（マージまたはクローズ）を追記しました。[v0.8.0での変更](#v080での変更)を参照してください

出典: `modules/monitor-architecture.md`・`modules/workflows.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）、CHANGELOG.md v0.9.0節（`99e6253`）、<https://kiro.dev/docs/crew/features/workflows/>（Page updated 2026-10-12）。

## v0.8.0での変更

### 静かな確認を起床の前に選別する（wake judge）

CHANGELOG v0.8.0節 200-212行（`99e6253`）は、監視ループが見つけたものを選別し、判断が必要な tick のときだけ起床させると記述します。

- 公式ページ（Page updated 2026-10-12）は、ループが「何を起床の理由にするか」と「何を静かなままにするか」の短いルールを2つ持てると記述します。静かと判定された確認は、チャットに小さな通知を書き、モデルのターンを使いません。`gate=false` で開始したループは、静かな間も動くことが目的のため、選別されません
- ルールを持たないループで選別を使うには、公式ページは **Settings → Developer → Feature Previews → Decisions (Jev)** の **Quiet check-ins: wake or skip** を開き、**Also send what a watching loop has found so Jev can skip a turn** を有効にするよう案内します。同意がない場合、ループは単純なタイマーとして動きます。**Decisions (Jev) は Feature Preview 配下の設定です**
- CHANGELOG は、判定の結果ごとにチャットへ wake judge の通知が書かれると記述します（同 209-212行）。Jev の鍵がなくても、この端末がすでに使っているモデルプロバイダで判定を動かせると記述します（CHANGELOG v0.8.0節 355-358行）
- 仕様書 `modules/decisions.md` 457-470行は、判定の担い手を `decisions.nudge_wake.provider`（`auto`／`jev`／`llm`）で選び、`llm` の経路で使うモデルを `decisions.nudge_wake.llm_model` で指定すると記述します。`auto` は Jev が有効ならそれ、そうでなければ小さいモデルを使います。`llm` の経路は、ループの `judge` 指定とあわせて、同意の行を必要としません（送信先は、運用者のセッションが毎ターン送っているモデルプロバイダと同じため、と同ファイルは記述します）。Jev の経路は、設定された送信先への同意とこの判定点の `nudge_evidence` スコープを必要とします
- 仕様書 `modules/babysit-pr-watch.md` 100-103行は、ゲートされたループが、静かな観測が `_MAX_QUIET_STREAK`（10）回続くと強制的に配送され、`floor_ticks` として起床とは別に数えると記述します

### crew log の既定オンと conductor

- **crew log は既定で記録されます**: 公式 Configuration ページ（Page updated 2026-10-20）は、`KIROCREW_CREW_LOG` は未設定のとき有効で、Gateway の起動前に `0` を設定すると、既定の編集済み crew log とセッション台帳が無効になると記述します（CHANGELOG v0.8.0節 330-334行）。v0.7.2 の `modules/session-work-ledger.md` 11行・19行は、セッション台帳の記録に `KIROCREW_CREW_LOG=1` が必要と記述していました。v0.9.0 の同ファイル 11行・19行は、`KIROCREW_CREW_LOG=0` ではセッション台帳が `crew_log_unavailable`（HTTP 409）で拒否されると記述します
- **個人の Discord／Telegram の DM でも conductor が動く**: ワーカーを dispatch し、作業台帳を使えます（以前は拒否されていました）。conductor は crew log から作業台帳を再構築できます（CHANGELOG v0.8.0節 313-316行）
- **conductor の表示**: サイドバーの conductor ビューは、conductor とそのワーカーを1つのツリーとして表示します（同 257-260行）

### 監視ループの修正

CHANGELOG v0.8.0節 526-536行（`99e6253`）は、次を記述します。

- 監視ループへの修正が拒否された場合は、ループが古い指示のまま黙って残るのではなく、チャットに報告されます
- ゲートウェイが適用できなかった要求は、「Monitor was not set up」「Monitor was not changed」「Monitor was not stopped」としてチャットに書かれます
- 止めたループは、すでに処理中の wake によって置き換えのループが開始されることがなくなりました
- PR の watch は、キャンセルされた再実行を実際の失敗として報告しなくなりました
- `monitoring.max_runtime_secs` が、新規または更新された watch の実行時間の上限を30日まで引き上げます。停止のたびに、理由・サイクル数・実行時間がゲートウェイのログに1行残ります

出典: CHANGELOG.md v0.8.0節（`99e6253`）、<https://kiro.dev/docs/crew/features/workflows/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）、`modules/decisions.md`・`modules/babysit-pr-watch.md`・`modules/session-work-ledger.md`（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）。

## v0.7.0での変更

### PR の structured watch（`monitor_watch`）

レビュー可能な pull request に到達することが目的のときに使います。プロバイダへのプローブは、対応が必要な変化がない間は**エージェントのターンなしで**動き、変化があると所有するセッションを要約付きで起こします（公式ページ「Structured pull request watches」）。

| PR のホスト | 必要なもの |
|---|---|
| GitHub | 認証済みの `gh` |
| GitLab.com または許可リストに登録した self-managed GitLab | 認証済みの `glab` |
| Azure DevOps Services | azure-devops 拡張付きの `az` と、`az login` または `AZURE_DEVOPS_EXT_PAT` |
| Bitbucket Cloud | 公開 PR はそのまま。private PR は `BITBUCKET_EMAIL` と `BITBUCKET_API_TOKEN` |

- 正規の PR URL を **Watch a pull request** に貼り付けます。**Azure DevOps Server と Bitbucket Data Center には対応していません**。Azure DevOps と private Bitbucket の watch は、所有者スコープの資格情報に依存するため**ダッシュボードの会話から開始する**必要があります（公式ページ／CHANGELOG 197-205行）
- `monitor_watch` はダッシュボード・Slack・Discord のセッションから使えます。**Webex のセッションは `monitor_start` のタイマーループのみ**で、structured watch は使えません（structured な起床の配送に Webex の経路がないため。公式ページ）
- `monitor_stop` で structured watch を終了し、`monitor_inspect` で現在の状態を読みます。どちらも PR watch・workflow watch・`monitor_start` のタイマーループのすべてに使えます。CHANGELOG は、従来は停止が拒否される・何も起きないことがあった Webex のセッションからも応答するようになったと記述します（公式ページ／CHANGELOG 206-209行）
- 公式ページ（Page updated 2026-10-12）は、レビューやコメントが変更を求める、または質問をする場合も、失敗したチェックと同様に起床の対象（actionable）として扱い、**マージまたはクローズされた PR は watch を終了させる**と記述します（CHANGELOG v0.8.0節 206-208行、`99e6253`）
- 終了条件について、公式ページは「対象が終端状態に達するか予算を使い切ると retire する」、CHANGELOG は「判定（verdict）が変化しなくなると retire する」と記述します。CHANGELOG はあわせて、編集されたレビューコメントや指定した緊急条件でも起床すること、複数の PR を watch していても確認ごとにまとめて1回の問い合わせになる（1件あたり3回の呼び出しではなく）ことを挙げています（公式ページ／CHANGELOG 429-432行）

### 永続化されたワークフロー呼び出し（durable workflow calls）

- 受け付けたワークフローのエージェント呼び出しは、Subagent・Task Runner のステップと**同じ永続タスクキュー**を使います。キューにある呼び出しは Gateway の再起動を生き残り、起動後にスケジューリングを再開します。ワークフローの run の状態と完了したエージェントの結果は Workflows の画面から引き続き参照できます（公式ページ「Durable workflow calls」／CHANGELOG 309-313行）
- 仕様書は、各 `ctx.agent()` 呼び出しが共有の runner lane を通じて `workflow_agent` 行として受け付けられ、その lane の上限が**適応的並行（adaptive concurrency）**の実効上限に従う（`agent.adaptive_concurrency_mode=fixed` で固定）と記述します（`workflows.md` 217-224行、`c67c506`。v0.9.0 では 227-234行）。また、ワークフローのエージェント並行数は設定できず、4 に固定されていると記述されています（`modules/workflows.md` 1444行、`modules/subagent.md` 175行、`99e6253`）
- キュー・適応的並行の設定キーと挙動は [06_autonomy.md](06_autonomy.md#v070での変更subagent永続タスクキュー適応的並行) を参照してください

出典: <https://kiro.dev/docs/crew/features/workflows/>（Page updated 2026-09-25）、CHANGELOG.md v0.7.0節（`c67c506`）。

## 未確認事項

- ワークフロースクリプトが使える API のうち、`ctx.agent()` と入力以外の詳細（`modules/workflows.md` の Scheduling combinators・Concurrency・Progress・Budget・ports の各節。上記「ワークフロースクリプトの `ctx`」参照）
- conductor エージェントの名称と、Agent Capabilities（v0.9.0 では Customize）上での扱い（builtin agent か組み込み機能か）。公式ページは名称を挙げていない。`modules/pipeline-conductor.md` は `kirocrew-pipeline-conductor`（1つのリポジトリの issue／PR パイプラインを、ワーカーのセッション群として監督するエージェント）を記述するが、公式ページの conductor との関係は確認できていない
- ライブラリのリビジョン数の上限（保存先は確認済み: [グローバルワークフローライブラリ](#グローバルワークフローライブラリ)参照）
- `docs/system-specs/modules/workflows.md`（1751行）の全体と `pipeline-conductor.md` の本文（本サイトでは `ctx` の入口・ライブラリ・ceilings・起動のアクセス制御・Configuration のみ確認。公式ページを主な出典としている）
- goal chip に表示される予算（budget）の既定値と設定可否（v0.6.0 時点の公式ページの例 `23/24` の `24` を含め、既定値は確認できていない。v0.9.0 の仕様書 `modules/monitor-architecture.md` 126-160行は、conductor の既定パトロールの予算を 300 サイクル・86400 秒と記述するが、goal chip の表示値との対応は記述が見つかっていない）
- 監視ループが KAS バックエンドで動くかどうかの現行の記述（v0.6.0 時点の公式ページにあった「Monitor loops also work on KAS」は v0.7.2 時点の公式ページから削除されている。公式 Agent Backends ページ（Page updated 2026-10-12）は Monitor controls がすべてのバックエンドで動くと記述する。[15_agent-backends.md](15_agent-backends.md#バックエンドをまたいで同じもの)参照）
- interrupt controller の対象（公式ページの「eligible polling cron」と、仕様書の `irq.poll` のみとの関係。[エージェントが制御する監視ループ](#エージェントが制御する監視ループ)の表を参照）

> **解消済み**: 「ワークフロー呼び出しのキュー行の扱い」は、`modules/taskq.md` 31-40行・1355-1363行（`99e6253`）が、`workflow_agent` の行は共有の `RunnerAdmission` が書き、再起動後は reconciler が付ける `awaiting_adapter` を `WorkflowService.attach_task_admission` の採用処理が settle すると記述している（ワークフローの run は個々の呼び出しの行から再開せず、自身のレジストリから再開する）ため、未確認事項から除きました。`awaiting_adapter` は復旧の引き継ぎ用の印で、本来のディスパッチ経路ではないと記述されています（詳細は [06_autonomy.md](06_autonomy.md#未確認事項)）。ライブラリの保存先パスも、`modules/workflows.md` 862行で確認できたため除きました。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/workflows/>
- 公式（Subagents）: <https://kiro.dev/docs/crew/features/subagents/>
- 公式（Task Runner）: <https://kiro.dev/docs/crew/features/task-runner/>
- 自律実行（Subagent・Task Runner・Cron）: [06_autonomy.md](06_autonomy.md)
- Apps: [10_apps.md](10_apps.md)
- MCPツール: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)
- 上限値・既定値: [04_reference/05_limits.md](../04_reference/05_limits.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

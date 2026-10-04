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
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## 概要

**v0.5.0 で conductor とワークフローライブラリが追加され、v0.6.0 で監視ループのエージェント制御などが加わりました。v0.7.0 では PR の structured watch とワークフロー呼び出しの永続化が加わりました**（[v0.7.0での変更](#v070での変更)）。

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
| バージョンと系譜（lineage）の管理 | **Agent Capabilities → Workflows** |
| 保存済み定義の呼び出し | 任意のセッションで `/workflow <name>` |
| Task Runner の plan との共有 | 同じライブラリを共有するため、以前使った plan が名前付きワークフローとして利用できる |

**ライブラリ内のワークフローはバージョン管理されます。** リビジョン履歴を確認し、以前のバージョンへロールバックできます。

> `/workflow` は**チャット内のコマンド**であり、`kirocrew` の CLI サブコマンドではありません。CLI コマンドの一覧は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) を参照してください。

## エージェントが制御する監視ループ

**v0.6.0 で追加されました。** 公式ページ（Page updated 2026-09-25）は、エージェントが**自分のセッションに結びついた**監視ループを開始・変更・**検査（inspect）**・停止できると記述します。単純なタイマーループ（`monitor_start`）は、ダッシュボードのチャット・Slack・Discord・**Webex** から使えます。

- goal chip は、待機中のループが実行中のターンと見分けられるよう、現在の**間隔（cadence）と予算（budget）**を表示します
- レビュー可能な PR に到達することが目的のときは、PR の structured watch（`monitor_watch`）を使います（v0.7.0。[v0.7.0での変更](#v070での変更)参照）

> v0.6.0 時点の公式ページ（Page updated 2026-09-12）は、操作を「開始・変更・停止」、利用場所を「ダッシュボード・Slack スレッド・Discord DM」とし、さらに次のように記述していました。**v0.7.2 時点の公式ページにはこれらの記述はありません。**
>
> - ループが1つの PR を名指しした場合、Crew はその PR が変化したときだけエージェントを起こす
> - goal chip にサイクル数と上限を表示する（例: `23/24`）
> - 承認が未応答のままループが停止した場合は、必要なアクセスを承認または再有効化してから再度 arm する
> - 監視ループは KAS バックエンドでも動く

**interrupt controller** は、対象となるポーリング型の cron を wake-on-change の割り込みに変え、静かな間隔にエージェントのターンを消費しないようにします。v0.7.2 時点の公式ページは対象を「an eligible polling cron」、v0.6.0 時点は「any script cron」と記述しています。

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
- 終了条件について、公式ページは「対象が終端状態に達するか予算を使い切ると retire する」、CHANGELOG は「判定（verdict）が変化しなくなると retire する」と記述します。CHANGELOG はあわせて、編集されたレビューコメントや指定した緊急条件でも起床すること、複数の PR を watch していても確認ごとにまとめて1回の問い合わせになる（1件あたり3回の呼び出しではなく）ことを挙げています（公式ページ／CHANGELOG 429-432行）

### 永続化されたワークフロー呼び出し（durable workflow calls）

- 受け付けたワークフローのエージェント呼び出しは、Subagent・Task Runner のステップと**同じ永続タスクキュー**を使います。キューにある呼び出しは Gateway の再起動を生き残り、起動後にスケジューリングを再開します。ワークフローの run の状態と完了したエージェントの結果は Workflows の画面から引き続き参照できます（公式ページ「Durable workflow calls」／CHANGELOG 309-313行）
- 仕様書は、各 `ctx.agent()` 呼び出しが共有の runner lane を通じて `workflow_agent` 行として受け付けられ、その lane の上限が**適応的並行（adaptive concurrency）**の実効上限に従う（`agent.adaptive_concurrency_mode=fixed` で固定）と記述します（`workflows.md` 217-224行、`c67c506`）
- キュー・適応的並行の設定キーと挙動は [06_autonomy.md](06_autonomy.md#v070での変更subagent永続タスクキュー適応的並行) を参照してください

出典: <https://kiro.dev/docs/crew/features/workflows/>（Page updated 2026-09-25）、CHANGELOG.md v0.7.0節（`c67c506`）。

## 未確認事項

- ワークフロースクリプトが使える API の詳細（公式ページは「sandboxed API」と記述するが、API 仕様は未確認）
- conductor エージェントの名称と、Agent Capabilities 上での扱い（builtin agent か組み込み機能か）
- ライブラリのリビジョン数の上限、保存先のパス
- `docs/system-specs/modules/workflows.md` と `pipeline-conductor.md` の本文（本サイトでは未精読。公式ページを主な出典としている。v0.7.0での変更節で `workflows.md` 217-224行のみ参照）
- goal chip に表示される予算（budget）の既定値と設定可否（v0.6.0 時点の公式ページの例 `23/24` の `24` を含め、既定値は確認できていない。v0.7.2 時点の公式ページは数値例を記載していない）
- 監視ループが KAS バックエンドで動くかどうかの現行の記述（v0.6.0 時点の公式ページにあった「Monitor loops also work on KAS」は v0.7.2 時点の公式ページから削除されている。公式 Agent Backends ページは Monitor controls がすべてのバックエンドで動くと記述する。[15_agent-backends.md](15_agent-backends.md#バックエンドをまたいで同じもの)参照）
- ワークフロー呼び出しのキュー行の扱い（`taskq.md` 32-35行は「TaskRunner and workflows are imported as rows but not yet dispatched from them (`awaiting_adapter`)」と記述し、同1232-1234行は `WorkflowService.attach_task_admission` が復旧アダプタを実行すると記述している。本サイトでは両者の関係を精査していない）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/features/workflows/>
- 公式（Subagents）: <https://kiro.dev/docs/crew/features/subagents/>
- 公式（Task Runner）: <https://kiro.dev/docs/crew/features/task-runner/>
- 自律実行（Subagent・Task Runner・Cron）: [06_autonomy.md](06_autonomy.md)
- Apps: [10_apps.md](10_apps.md)
- MCPツール: [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)
- 上限値・既定値: [04_reference/05_limits.md](../04_reference/05_limits.md)
- 更新履歴: [02_update/01_changelog.md](../02_update/01_changelog.md)

# チャット体験

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/chat/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{autopilot,side,file-search,themes}.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（v0.7.0での変更・`@`メンションの再確認・Autopilot の記述の食い違い）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{autopilot,side,file-search,decisions}.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/chat/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-09-25）
**出典**（v0.8.0・v0.9.0での変更・Autopilot の仕様書の有無・Side Chat の不変条件の再確認）: <https://kiro.dev/docs/crew/chat/>・<https://kiro.dev/docs/crew/chat/message-controls/>・<https://kiro.dev/docs/crew/chat/voice/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-10-20）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/side.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.10.0・v0.11.0・v0.11.1での変更・Side Chat の読み取り専用ツールの対象・Dashboard の Preview 要否・Mate の呼称・`decisions.history_budget_chars` の既定・Autopilot の再確認）: <https://kiro.dev/docs/crew/chat/>・<https://kiro.dev/docs/crew/capabilities/agents/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-10-20）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{side,config,decisions,stt-streaming,themes,file-search,command-bar,history}.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

---

## 📑 このページの内容

- [Autopilot](#autopilot)
- [`/side`（サイドカンバセーション）](#sideサイドカンバセーション)
- [`@` メンションによるファイル添付](#-メンションによるファイル添付)
- [テーマ](#テーマ)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## Autopilot

**v0.9.0・v0.11.1 の時点で、Autopilot の説明は出典によって異なります。** 公式ドキュメントと、v0.7.2・v0.8.0 のリポジトリの仕様書が別の機能を記述しており、v0.9.0 と v0.11.1 のリポジトリには仕様書そのものがありません。

**公式ドキュメント（v0.9.0）**: Autopilot は**セッション単位のツール自動承認のトグル**です。セキュリティゲートを通過したツール呼び出しが個別の確認なしで進みます。拒否コマンド・機微パス・ガバナンスポリシーは Autopilot でも引き続き適用されます（<https://kiro.dev/docs/crew/chat/sessions/>・<https://kiro.dev/docs/crew/capabilities/agents/>・<https://kiro.dev/docs/crew/security/>。Sessions・Agents は Page updated 2026-10-20、Security は 2026-10-12）。

**v0.7.2・v0.8.0 の `modules/autopilot.md`（5-9行）**: Autopilot は Chat の per-slot（スロット単位）モードで、`_ChatSlot.mode == "orchestrator"` のときに有効になり、`PATCH /api/chat/slots/{slot}/mode` で切り替えます。モデルが段階的なプランを提示し、ユーザーが承認すると、**Python 制御のステージループ**が1段ずつ実行を進めます。単純な依頼は普通のチャットと同様に動作し、チェックポイント付きのプランに値する作業だけがプラン／承認／実行のフローに入ります。同仕様書は、`orchestrated` builtin app は既に存在せず、「Autopilot」がユーザー向けの名前（スロットの `mode` 値・設定セクション・システムプロンプトのファイル名は内部名 `orchestrator`）であるとも記述していました。

**v0.9.0 のリポジトリ**: `modules/autopilot.md` がありません（v0.7.2 と v0.8.0 のタグにはあります）。`modules/README.md` の索引行も消えています。v0.9.0 の仕様書は Autopilot を **「the retired chat Autopilot」** と呼ぶ記述を2か所に残しています（`taskq.md` 464行は `_stage_boundary_owner` の説明、`subagent.md` 3401-3402行は `stage_cancel` の tombstone の説明）。CHANGELOG の v0.8.0 節と v0.9.0 節に、Autopilot の変更・廃止を告知する項目はありません。

**v0.11.1 のリポジトリ（再確認）**: `modules/autopilot.md` は v0.11.1 のタグにもありません。`taskq.md` 530行は `_stage_boundary_owner` を「written by the retired chat Autopilot」と、`subagent.md` 3923-3924行は `stage_cancel` の tombstone を「from the retired chat Autopilot」と記述しています（`fe6f5be`）。`decisions.md` 155行は、Decisions の注釈が動くセッションを `_session_auto_approves`（`_slot_is_trusted(slot) or state.is_yolo_active()`）で判定すると記述しています。CHANGELOG の v0.10.0〜v0.11.1 節にも Autopilot の変更・廃止を告知する項目はありません。公式 Sessions ページ（100-102行、Page updated 2026-10-20）は、今もセッション単位の Autopilot トグルを説明し、公式 Security ページ（Page updated 2026-10-12）は承認レベルの表に **Autopilot**（「All tools auto-approved for this session」）を載せています。

> ⚠️ **Proactive とは別物**です。Proactiveは起動モード5分類の1つ（AutoNudge・goal-loopスキル）で、Autopilotとは異なる仕組みです。詳細は [06_autonomy.md](06_autonomy.md) を参照してください（本記述は v0.7.2 時点の確認で、v0.9.0 では再検証していません）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **公式ドキュメント（v0.9.0）**: セッション単位のツール自動承認のトグル（上記）
> - **v0.7.2・v0.8.0 の `modules/autopilot.md`**: プラン承認とステージループを持つスロット単位のモード（上記）
> - **v0.9.0・v0.11.1 の仕様書**: `modules/autopilot.md` がなく、2か所が「the retired chat Autopilot」と記述（v0.11.1 は `taskq.md` 530行・`subagent.md` 3923-3924行）
> - **公式 Configuration ページ**（Page updated 2026-10-20）は `orchestrator.max_plan_duration_seconds`（既定 `7200`、「Whole-plan limit for unattended auto-run plans」。101行）を設定表に載せていますが、v0.9.0 と v0.11.1 の `config.md` にこのキーの記述はありません
>
> プラン承認型の Autopilot が v0.9.0・v0.11.1 に存在するか、公式の「Autopilot トグル」と旧仕様書のモードが同じ機能を指すかは、一次情報から判断できません。`orchestrator.stage_timeout_seconds` も v0.9.0・v0.11.1 の仕様書・公式ドキュメントでは確認できません。
> 参考: v0.9.0 の `decisions.md` 155行（v0.11.1 も 155行）は、Decisions の注釈が動くセッションを「ツール呼び出しを自動承認するセッション（`_slot_is_trusted(slot)` または `state.is_yolo_active()`）」と記述しています。これが公式の「Autopilot トグル」と同じものかは、同ファイルに書かれていません。

**出典**（v0.7.2・v0.8.0 の仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/v0.8.0/docs/system-specs/modules/autopilot.md>
（参照: 2026-10-25 / commit `4d205da` / 版 v0.8.0。v0.7.2 の同ファイルは参照: 2026-10-04 / commit `c67c506` で同じ記述を確認）
**出典**（v0.9.0 の「retired」記述）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/taskq.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.11.1 の「retired」記述の再確認）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/taskq.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/subagent.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/decisions.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://kiro.dev/docs/crew/chat/sessions/>（Page updated 2026-10-20）、<https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）

## `/side`（サイドカンバセーション）

親チャットのスロットに、一時的なQ&Aスレッドを追加する機能です（ユーザー向けの名称は **Side Chat**）。`/side` コマンド（v0.7.0 からは `/btw` も）またはActivityパネルの「Side Chat」タブから起動します。v0.7.0 で、Kiro CLI バックエンドでは読み取り専用ツールを承認なしで実行できるようになりました（「[v0.7.0での変更](#v070での変更)」参照）。v0.10.0 以降は、Kiro CLI 以外のバックエンドにも対象が広がっています（「[v0.11.1での変更](#v0111での変更)」の Side Chat 節。公式 Chat ページは Kiro CLI のバックエンドだけを記載しており、食い違いとして併記しています）。

**主な設計上の不変条件**:

1. **新しいスロットIDを作らない**: `slot._side: SideState | None` として存在
2. **別の封筒**（v0.9.0 で変更）: side は `side_context.build_side_message` で自分の封筒を作り、`ContextBuilder.build_message` を通さず、`slot.messages` にも書かない（レビュー時のルール。`side.md` 53-56行、`99e6253`）。v0.7.2 の仕様書は「Main path byte-frozen」（メインスレッドパスは変更されない）と記述していました
3. **Birth-onlyメモリモード**: side は memory/learn/save を一切呼ばない。サイドカーバッファはクローズ時に**永続化なしで破棄**される
4. **独立したLLMセッション**: キーは `side:<slot>:<gen>`（サイドカーの世代 `gen` を含む。v0.9.0 の `side.md` 59-61行）で、親のセッションとは別。裸の `side:<slot>` は旧表記としてのみ残る（v0.7.2 の仕様書は `f"side:{slot.key}"`）。ターンが親のコンテキストを汚染しない
5. **非ブロッキング**: `api_side_turn` は即座に応答を返し、ストリーミングはバックグラウンドタスクで実行される
6. **受理された送信は黙って失われない**（v0.9.0 で表現が変更）: ターンが進行中でも、メッセージはそのターンにsteerされるかキューされる。キュー満杯（HTTP 429）・サイドカー閉鎖済み（409）・不正な質問（400）は目に見える形で拒否され、コンポーザは入力を保持する（`side.md` 64-67行）。v0.7.2 の仕様書は「拒否パスはない」と記述していました

上記の不変条件は v0.9.0 の `side.md` 50-67行（`99e6253`）で確認しました（2・4・6 が上記のとおり変わり、1・3・5 は同じ内容です）。

親のコンテキストは**凍結スナップショット**として読み込まれ、side は**JSONLやメモリストアに一切永続化しません**。ゲートウェイは side の会話をメモリ上に保持し、ページを再読み込みしても復元します（v0.11.0。「[v0.11.1での変更](#v0111での変更)」参照）。

## `@` メンションによるファイル添付

ダッシュボードのチャット入力欄で `@` に続けてクエリを入力すると、プロジェクト全体を対象にしたファイル検索ピッカーが起動します。結果を選ぶとトークンが挿入され、プロンプト内で添付マーカーとしてシリアライズされます。v0.7.0 からは、`./`・`../` と入力するとそのディレクトリから1階層ずつたどるピッカーも開きます（`GET /api/path-complete`。CHANGELOG v0.7.0節 338-339行／`file-search.md` 5-8行、`c67c506`）。

結果は**ファイルとディレクトリの両方**をカバーします。

- **ファイル**: 内容がエージェントに届く添付物
- **ディレクトリ**: **パス参照のみ**。エージェントはパスを受け取り、自身のglob/grep/readツールで探索します。ディレクトリの一覧や再帰的な内容はインライン化されません

`GET /api/file-search` の結果は、あいまい検索スコア→同スコアなら**ファイルがディレクトリより優先**→短い名前→新しさの順でランキングされます（`file-search.md` 44行、`c67c506`）。

> **件数・文字数の記述について**: 本サイトは以前「2文字以上で起動」「最大15件」と記載していました。これは v0.3.0 の `file-search.md`（20行「Fewer than 2 characters returns an empty result set」・38行「At most 15 results are returned」、`21584ea`）に基づく値です。v0.7.2 の `file-search.md` は数値を記載せず、「Queries shorter than the accepted minimum return an empty result set」（23行）、`limit` は「normalizes it to a positive server ceiling; invalid input uses the default」（27行）と記述しています（`c67c506`）。**現行の最小文字数と既定件数は一次情報で確認できません**（v0.6.0 の同ファイルも数値を記載していません）。

## テーマ

ダッシュボードは完全にスキン変更可能です。**テーマ**は素のカラーパレットから、フル「experience pack」（フォント・サンドボックス化されたオーバーレイ・音声・ペルソナ）まで幅広く、Settings → Display の**1つのThemeドロップダウン**の裏に全スペクトルがあります。複数インストールして1つを選択する形式です。

**テーマはKiroCrewのAppではなく、`useTheme`の上に構築された独立したサブシステムです。** `theme.json` は `"formatVersion": 1` を必須で宣言する必要があります。

## v0.11.1での変更

v0.10.0・v0.11.0・v0.11.1 の CHANGELOG と v0.11.1 の仕様書で確認できた、チャット体験の追加・変更です。内容が v0.10.0 または v0.11.0 に由来するものは、その版を明記します。v0.11.1 の CHANGELOG（5-54行）でチャットに関わる項目は次のとおりです。

- kiro-cli v3 の書き込みツールによるファイル変更が、トランスクリプトに再び表示されます。kiro-cli の読み取り専用のファイル検索は、安全チェックのあとに承認されます
- バックグラウンドのツール承認ごとに個別の id が付き、1つの回答が別の承認を決着させません
- Settings は、`config.local.json` が上書きしてしまう保存を拒否します

出典: CHANGELOG.md v0.11.1節 29-34行（`fe6f5be`）。

### コンポーザとメッセージ（v0.11.0）

- **Escape で停止・ターン中のモデル切替**: コンポーザで **Escape** を押すと、実行中のターンが止まります。返信の最中に選んだモデルは、失敗せずターンの境界で有効になります。**Optimize prompt** はターンの実行中も動き、取り消せます（CHANGELOG.md v0.11.0節 92-94行）
- **フォーク**: Tail-only Fork が on のとき、メッセージのメニューに **Fork with later messages only** と **Fork with earlier messages** が出ます（同 95-96行）。Tail-only Fork はサーバー側で `dashboard.tail_fork_enabled` により制御され、ゲートがオフのとき通常のエントリは履歴つきでフォークします（`history.md` 1308-1320行）。設定画面での場所と既定値は、一次情報で確認できません
- **小さな改善**: メッセージの右クリックメニューに **Open link in new tab** が加わりました。コンポーザでは Tab／Shift+Tab がリストの行をインデント／アウトデントします（同 97-98行）
- v0.9.0 で加わった Cmd+Up／Ctrl+Up による直前のメッセージの編集は、このページの「[v0.9.0での変更](#v090での変更)」にあります

### トランスクリプトの表示

- **v0.10.0**（CHANGELOG.md v0.10.0節 273-282行）: 返信の右クリックメニューの **Copy as rich text**（Outlook や Word に見出し・リスト・表を保ったまま貼れます）。Alt+↑／Alt+↓ で、開いているチャットのプロンプトの間を移動します。エージェントが挙げたファイルは、返信の下に **Open file** チップで出ます。実行中のターンは直近5件の作業行だけを表示します。**Settings → Chat → Transcript → Tool calls start expanded** はツールの行を開いた状態にします。セッションメニューの **Export as readable Markdown** は、人が読めるトランスクリプトを保存します
- **v0.10.0**: エージェントの質問カードは、利用者の回答を待ってエージェントに返します。利用者名義のメッセージとしては送られません（同 268-269行）
- **v0.11.0**（同 99-102行）: エージェントが lesson を保存したときの行が出て、**Review lessons** にリンクします。画像の読み取りは、見た内容のサムネイルを表示します。同じファイルへの連続した編集は1行にまとまります。会話の途中のセッションリセットはすべて印が付きます。圧縮で途切れた返信は続きを出します
- **v0.11.0**（同 103-109行）: **Settings → Chat → Side panel** に **Keep Side Panel Open** と **Pin Summary in Side Panel** が加わりました。サイドパネルの Git タブは、チャットが作業しているすべてのリポジトリを一覧します。ファイルツリーが切り捨てたフォルダは、専用のフォルダタブで開きます。artifact のコードブロックは、行に固定したコメントを受け付けます。**Pin Summary in Side Panel** の既定と設定キーは、一次情報で確認できません

### Side Chat

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **公式 Chat ページ**（Page updated 2026-10-20）: 親セッションが Kiro CLI のバックエンドを使うとき、Side Chat はファイルの読み取り・検索・fetch・読み取り専用のシェルコマンドを承認なしで実行できると記載しています（79行）
> - **CHANGELOG と仕様書**（`fe6f5be`）: v0.10.0 は Claude Code・goose・KAS で Side Chat が読み取り専用ツールを実行できると記載し（CHANGELOG.md v0.10.0節 302行）、v0.11.0 は DeepSeek ハーネスでの読み取り専用ツールと、Kiro の side chat が認証情報のパスを拒否することを記載しています（同 v0.11.0節 163-165行）。仕様書 `side.md` は、読み取り専用ツールを許可するバックエンドの集合 `ACP_BACKENDS_SIDE_READONLY` を kiro-cli・KAS・claude・goose・deepseek と記述しています（530-537行）。v0.7.2 の `side.md` 322-324行にあった「kiro-cli only」の記述は、v0.11.1 の `side.md` に存在しません

バックエンドごとの囲い方は、仕様書の記述では次のとおりです。

| バックエンド | Side Chat のターンの読み取り専用の囲い方 | 出典（`side.md`） |
|---|---|---|
| kiro-cli・KAS | 読み取り専用に派生させたエージェント仕様で動かします（KAS には `<agent>--readonly` のカスタムエージェントを渡します） | 530-538行 |
| claude | シェルを持たない境界プロンプト（`SIDE_BOUNDARY_PROMPT_NO_SHELL`）。シェルコマンドの名前を挙げません | 378-379行 |
| goose | フォルダの一覧と画像の表示だけができ、ファイルの本文を読むツールを持たない境界プロンプト（`SIDE_BOUNDARY_PROMPT_LISTING`） | 380-382行 |
| deepseek | Crew の検証済みの gate プラグイン。すべての呼び出しが承認要求を経由し、`read`・`grep`・`glob` だけが読み取りとして扱われます | 557-575行 |

- **認証情報のパス**: 派生した仕様に `deniedPaths` が加わり、kiro-cli はセッションの cwd の内側でも認証情報のパスの読み取りを拒否します。派生した仕様を作れない・公開できないターンは、コード付きのエラーで拒否されます（`credential_paths_unresolved` を含みます）。ターンは基底のエージェントでは実行されません（`side.md` 485-497行）
- **feature-map のみ**: `docs/feature-map/README.md` 132行は、kiro-cli と KAS が読み取り・検索・fetch・読み取り専用シェル、Claude Code がファイルの読み取り・検索・Web fetch、DeepSeek がファイルの読み取りと検索と記述しています（goose は該当行にありません）。CHANGELOG・Release 本文に説明がなく、一次情報の順位表にない資料です
- **再読み込みでの復元（v0.11.0）**: ページを再読み込みしても、ゲートウェイが保持している side の会話が復元され、次の質問はその会話に続きます（CHANGELOG.md v0.11.0節 202行）。仕様書は、side の会話がスロットの上に、閉じるかゲートウェイを再起動するまで保持されると記述し（`side.md` 204-205行）、`GET /api/chat/slots/{slot}/side` を owner 専用と記述しています（188行）。ゲートウェイを再起動すると会話は終わります。side の会話をメモリ上に保持することは、JSONL やメモリストアへ永続化しないという v0.9.0 までの記述（`side.md` 14-20行）と両立します
- **仕様書の差分にだけある項目**（CHANGELOG に説明なし）: `GET /api/chat/side/tools` が、Side Chat で読み取り専用ツールが動くかどうかを返します（`side.md` 195行）。中断されたターン（`PromptBusyExhaustedError`）は、それまでに流れた内容とその通知を保存し、再読み込みのあとも同じ表示になります（257-262行）

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/side.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://kiro.dev/docs/crew/chat/>（Page updated 2026-10-20）

### Dashboard（v0.10.0 で Preview から外れた）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **公式 Agents ページ**（Page updated 2026-10-20）: **Settings → Developer → Feature Previews → Dynamic Dashboard** を有効にすると Mate（公式ページでは crewmate）の Dashboard タブにページが入ると記載し、出荷されるページは12種類で、Mate は出荷済みのページからだけ選べ、自分でページを書くことはできないと記載しています（128-138行）
> - **CHANGELOG v0.10.0**（`fe6f5be`）: Dashboard タブは Feature Preview を必要としなくなり、メインセッションのサイドパネルにも専用の dashboard が出ます。**Automatic cards for all sessions** は Settings → Developer の専用カードに移り、既定はオフのままです（249-252行）。Mate は `dashboard` スキルで自分のページを作り、利用者は Dashboard タブで採用か破棄を選びます（253-255行）。v0.11.0 は、Mate が自分の Dashboard ページを作って装飾し、適用すると公開され、元に戻す呼び出しが1つあると記載しています（79-82行）
> - **仕様書 `config.md`**（`fe6f5be`）: `dashboard.dynamic_dashboard_cards` は既定 false で、Dynamic Dashboard の画面に専用のスイッチがあります（158-160行）

- 公式ページの「12種類」が v0.11.1 でも成り立つかは、一次情報から確認できません（v0.10.0 の CHANGELOG 256-259行は、利用者が `~/.kiro/crew/panel-templates/` に置いたページが出荷済みのページと並ぶこと、組み込みページが UI の言語に従うことを記載しています）
- **feature-map のみ**: `docs/feature-map/README.md` 336行は、Dashboard ビューが root セッションにも出ること、+ メニューの項目・永続化された Dashboard タブ・All Dashboards のメニュー項目がすべての利用者に出ることを記述しています。CHANGELOG・Release 本文に説明がなく、一次情報の順位表にない資料です
- 呼称は、v0.11.0 から UI と CHANGELOG が **Mate** です（次の「Mate の呼称」）

**出典**（CHANGELOG）: CHANGELOG.md v0.10.0節 249-259行・v0.11.0節 79-82行（`fe6f5be`）
**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）

### Mate の呼称

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **CHANGELOG v0.11.0**（59行・74-75行、`fe6f5be`）: 「crewmate」は見える場所すべてで「Mate」と表示されます。Mates ページ・roster・ダイアログ・設定の行・チャットのヘッダーが Mate と表示します
> - **公式ページ**（Sessions・Agents・Configuration は Page updated 2026-10-20）: 「Crewmates」「crewmate」のままです（Sessions ページ 62行・Agents ページ 84-86行・Configuration ページ 33行）
> - **仕様書**（`fe6f5be`）: Command Bar の検索は「mate search」（`command-bar.md` 34行）ですが、設定キー `dashboard.crewmate_threads` のように識別子は `crewmate` の綴りのままです（`history.md` 2679行）

本ページは、v0.11.0 以降の UI と CHANGELOG の呼称に合わせて **Mate**（v0.10.0 以前・公式ページでは crewmate）と書き、設定キー・コード識別子・API パスは元の綴りのまま書きます。Settings → Developer → Feature Previews のカード名は、v0.10.0 の CHANGELOG（236行）が「Crewmates」と記載しており、v0.11.0 以降のカード名は一次情報で確認できません。

### Decisions (Jev): 既定値の食い違いと派生した tier

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **公式 Configuration ページ**（Page updated 2026-10-20）: `decisions.history_budget_chars` の既定は `0` で、「`0` sends none」（判断に過去の会話を送らない）と記載しています（136行）
> - **仕様書 `config.md`**（`fe6f5be`）: 「Superseded Defaults」の表が `decisions.history_budget_chars` の変更を **0 → 2000**（`reports`）として載せ（722行）、同意済みの履歴上限で採用が抑えられる注記があります（655行）。同じ節は、出荷済みの既定値を変えても反映されるのは変更後に作られたインストールだけで、既存のインストールは最後に書き出された値を保つと記述し、`reports` の行は報告だけで自動では採用されないと記述しています（629-648行）

- `DecisionsConfig` のデータクラスの既定値は `docs/` に定義行が見つからず、どちらが現在の既定かは判定できません。CHANGELOG（v0.9.0〜v0.11.1）にこのキーの記述はありません。この表の行は v0.9.0 の `config.md` 636行にもあり、v0.9.0 から v0.11.1 の間の変更ではありません。本サイトは以前、公式の値だけを書き、仕様書との食い違いを書いていませんでした
- **`decisions.model_route_derive`**（仕様書にだけ記述がある。CHANGELOG・公式 Configuration ページに説明なし）: bool で**既定 `false`** です。オンにすると、オーナーが空にした tier に限り、アカウントが今アドバタイズしているモデルの価格から tier を導き出します。固定（pin）した tier はそのままです。導き出した記録には `source: "derived"` が付き、価格が取れないときは `derive: "unpriced"` が付きます。この値は `config.json` の値で、同意（キーストーン）の下で質問が行われる点は変わりません（`decisions.md` 238-239行）。v0.9.0 の `decisions.md` に記述はありません

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/decisions.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）

### Voice

- **v0.10.0**: `stt.transcribe_languages` で、Amazon Transcribe が2〜5言語を1つのストリームで検出します（`config.md` 3079行は「transcribe provider, live stream only」と記述）。音声入力が自動で止まったときに音が鳴ります。返信の読み上げ中は、コンポーザの上のバーに **Stop reading** が出ます（CHANGELOG.md v0.10.0節 355-357行）
- **v0.11.0**: Text-to-Speech の言語を選ぶ設定が加わりました。**Settings → Voice → Fine-tuning** で、意図して止めたときに音声入力を送信できます（`stt.submit_on_release`、既定 false。`config.md` 3072行）。選んだプロバイダごとに、**Settings → Voice** が「Is my audio kept?」に1行で答えます（`stt-streaming.md` 136-139行）。Read aloud は、ゲートウェイのホストで読み上げられないとき、利用者のデバイスで読み上げます（CHANGELOG.md v0.11.0節 141-144行）
- **仕様書にだけある項目**（CHANGELOG に説明なし）: `stt.threads`（ローカルデコードのスレッド数、既定 0 はコア数の半分で上限16。環境変数 `KIROCREW_STT_THREADS` が優先）が加わっています（`config.md` 3070行）。v0.9.0 の `config.md` に記述はありません

### テーマ（v0.11.0）

- **Nu Disco** が組み込みテーマに加わりました。Create Theme ダイアログには **Paste CSS** タブが加わり、AI に渡せるデザインプロンプトをコピーできます。オーバーレイをコンテンツの背面に描けるようになり、インストールした pack が welcome 画面のゴーストを置き換えられます（CHANGELOG.md v0.11.0節 145-147行）
- 仕様書は、オーバーレイの宣言の `layer` が `above`（既定）または `behind` を取ると記述し（`themes.md` 185-188行）、welcome 画面の画像を pack の `branding/welcome.svg|png|webp|gif` で置き換えると記述しています（58-59行）。`theme.json` が `"formatVersion": 1` を宣言する必要がある点は v0.11.1 でも同じです（18行）

### v0.9.0 の記述が v0.11.1 でも成り立つことの再確認

- Side Chat の不変条件6つ: `side.md` 52-67行（stop の経路は 194行）。`GET /api/file-search` は owner 専用: `file-search.md` 33行。`./`・`../` のパス補完 `GET /api/path-complete` は最小文字数なし: 69行
- `@` メンションの最小文字数と既定件数は、v0.11.1 の `file-search.md` 26行・30行・55行も数値を記載していません
- Response Verbosity の既定 `answer_only`（`ultra` は廃止）: `config.md` 3120行。`subagent:` セッションは [RESPONSE PREFERENCES] を受け取りません: 4046行。`dashboard.default_memory_mode` の既定 `persistent`: 3119行。`stt.transcribe_vocabulary`: 3078行
- Decisions (Jev) の Auto の扱い（食い違い）: `decisions.md` 232行・238行と公式 Configuration ページの記述は v0.9.0 から変わっていません。`orchestrator.max_plan_duration_seconds` は公式 Configuration ページ 101行にあり、`config.md` に記述はありません
- 公式 Chat・Message controls・Voice・Configuration の各ページ（いずれも Page updated 2026-10-20）は v0.9.0 時点から変化なし

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/side.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/file-search.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/decisions.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## v0.9.0での変更

公式 Chat・Message controls・Voice・Configuration の各ページ（いずれも Page updated 2026-10-20）と v0.9.0 の CHANGELOG で確認できた、チャット体験の追加・変更です。

### コンポーザ

- **コンテキストウィンドウの警告**: プロンプトがモデルのコンテキストウィンドウに近づくか超えると警告します。上限を超える送信は保留され、もう一度送信すると送られます（キーの押しっぱなしは2回目に数えません。保留はプロンプトを削る機会を与えるもので、再送信は保留を回避するだけです）
- **Style Markdown While Typing**（**Settings → Chat → Composer**、**既定 off**）: 太字・斜体・取り消し線・インラインコードを入力中に装飾します。マーカーは表示されたままで、送信されるメッセージは変わりません。**リッチテキストの入力欄に切り替わり、この入力欄はまだ beta** のため既定は off です。プレーンな入力欄は、この設定に関係なく改行で Markdown のリストを継続します
- **Files タブからのドラッグ**: Files タブのファイル／フォルダの行をコンポーザにドラッグすると、ドロップした位置に `@path`／`@folder/` を挿入します
- **直前のメッセージの編集**: コンポーザが空のとき、Cmd+Up（macOS）／Ctrl+Up で直前のメッセージを編集します。ピッカーのメニューが開いている間と IME 入力中は動作しません
- **`! <command>`**: `!`・空白・コマンド（例: `! git status`）を入力すると、セッションのプロジェクトターミナルで実行します。実行前にコマンドを確認する画面が出ます。**セッションがリモート crew で動いているとき、メッセージに添付があるとき、ターミナルドックが使えない／オフのときは拒否されます**。`!` の直後に空白がないもの（Markdown の画像など）は、そのままチャットのメッセージとして送られます

出典: CHANGELOG.md v0.9.0節 45-57行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/chat/>（Page updated 2026-10-20）

### メッセージ操作

- **Quote**: メッセージにホバーして **Quote**（または右クリックの **Quote message**）を選ぶと、メッセージ全体を次の送信に引用カードとして持ち込みます。送信後のトランスクリプト内のカードは、選ぶと元のメッセージへジャンプします。引用は一度に1つで、別のメッセージを引用すると置き換わり、別のセッションに切り替えると破棄されます
- **Widen**: 返信内の表にホバーすると **Widen** が出て、表をペインの余白まで広げます（広げているときは **Narrow**）。ヘッダーセルの端をドラッグして列幅を変えられます。Markdown／CSV のコピーは従来どおりです
- **Add to main chat**: 完了した Side Chat の回答を、メインのコンポーザに置きます（送信は自分で行うため、編集できます）。応答しなくなった side のターンは Side Chat から停止できます。仕様書によると停止は `POST /api/chat/slots/{slot}/side/stop`（owner 専用）で、待機は最大 5 秒です（`side.md` 193-199行）

出典: CHANGELOG.md v0.9.0節 59-68行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/chat/message-controls/>（Page updated 2026-10-20）

### 応答の既定・圧縮の時間制限

- **Response Verbosity の既定が変わりました**: **Settings → Chat → Transcript → Response Verbosity** は、v0.9.0 の新規インストールで **Answer only** から始まります（既存の設定は保存済みのレベルを維持します）。**Ultra** レベルは廃止され、Ultra を保存していた設定は Answer only として動作します。どのレベルでもコード・コマンド・エラー文字列は原文のままです。設定は組み込み・カスタム・スケジュールのエージェントに適用されますが、`subagent:` セッションには [RESPONSE PREFERENCES] が渡されません（その最終メッセージを親エージェントが読むため。`config.md` 2784行・3492-3520行）
- **Compaction Time Limit**（**Settings → Chat → Advanced → Compaction Time Limit (seconds)**、`session.compact_wait_secs`）: 圧縮が走れる最長時間です。`0` は既定の **300 秒**を意味し、それ以外は **60〜3600 秒**で、範囲外の値はクランプされます。制限を超えたときの動作は起動元で異なります。自動圧縮とタスクランナーの圧縮はセッションを再起動し、チャネルの上限近辺の圧縮は断念してセッションを維持し、手動の `/compact` はタイムアウトを報告します。数値は公式 Configuration ページの記述で、`session.compact_wait_secs` のデータクラス既定値は `config.md` に定義行が見つかりません（`code-style.md` 40行は共有の予算 `COMPACT_WAIT_TIMEOUT_SECS` に言及しています）

出典: CHANGELOG.md v0.9.0節 150-156行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### Voice（音声入力）

公式 Voice ページ（Page updated 2026-10-20）で、v0.9.0 に加わった入力側の設定です（既定の `local` プロバイダはプロセス内で動き、初回に自分でモデルをダウンロードします）。

- **Test microphone**（**Settings → Voice**）: 選んだ入力（またはシステム既定）を開き、レベルバーだけを表示します。録音・送信・文字起こしはせず、スピーカーからも再生されません
- **Use a key to start dictation**（**既定 on**）: off にするとショートカットキーは何もしません。**Shortcut key** でキーを選び、**How the key works** で **Hold to talk**・**Press on/off**・**Both** を選びます
- **Custom vocabulary**（Amazon Transcribe のみ）: Amazon Transcribe に作成済みのカスタム語彙を選びます。設定キーは `stt.transcribe_vocabulary` で、AWS の名前規則（1〜200文字の `[0-9A-Za-z._-]`）に合う名前だけが保存されます。語彙の一覧には `transcribe:ListVocabularies` の権限が必要で、`READY` 状態の語彙だけが並びます。ローカルプロバイダはこの設定を無視します
- **設定例のキーの訂正**: v0.7.2 の公式 Voice ページの設定例は `"voice": {"stt_model": ...}`・`"voice": {"stt_provider": ...}` でしたが、v0.9.0 の同ページは `"stt": {"model": ...}`・`"stt": {"provider": ...}` です。リポジトリの `config.md`・`stt-streaming.md` のキーも `stt.*` で、v0.7.2 の公式ページの `voice.*` の表記は仕様書と異なっていました
- 既定のモデルは `base`（ダウンロード約 148 MB）で、`turbo` は約 1.6 GB です

出典: CHANGELOG.md v0.9.0節 141-143行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/chat/voice/>（Page updated 2026-10-20）
**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/stt-streaming.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。287-311行）

### 画面・設定の移動

- **Customize**: **Agent Capabilities** は **Customize** に改称されました（公式 Configuration ページは「labeled **Agent Capabilities** before 0.9」と記載。一部の公式ページは旧称のままです）。**Subagent Settings** と **Warm Pool**（カード名は **Pre-started Sessions**）は **Settings → Agent Harness** に移動しました
- **Zoom**: **Settings → Display → Zoom Level** は正確なパーセント（50〜300%にクランプ）を入力できます。デスクトップアプリのみで、ブラウザのタブではブラウザ自身のズームを設定できないため、ショートカットのヒントが表示されます
- **Translucent panels**（**Settings → Display → View**、**既定 off**）: トップバー・メッセージボックス・検索欄を磨りガラス風にします。既定はソリッドなカードです
- **その他**: **Settings → Chat → Sessions → Dim Inactive Panes** を off にできます。プロジェクトピッカーに Favorites タブが加わりました。Settings → Display → Terminal に Cursor style と Reuse the current terminal が加わり、Ctrl+\` でターミナルを開閉、Ctrl+Shift+\` でターミナルを追加できます

出典: CHANGELOG.md v0.9.0節 135-157行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）

### Command Bar とファイル検索

- Command Bar の Mate（v0.10.0 以前・公式ページでは crewmate）検索ビューは **`PREVIEW_CREW` フラグの背後**にあります（`command-bar.md`。v0.11.1 では 34行・418行で「mate search」と記述）。仕様書は、`/members` ページへの入口であり、そのページが同じフラグで登録されているためと説明しています
- `GET /api/file-search` は **owner 専用**です（owner 以外は 403 `owner_only`、古い pre-owner セッションは 401。`file-search.md` 33行）
- 同じ `file-search.md` の次の2点は v0.9.0 で新しくなった内容ではありません。ファイルの内容検索が `.pdf` の本文も out of process で抽出する点（上限に当たった文書はスキップされ、結果は `truncated` になります。v0.9.0 の 248-263行）は **v0.8.0 から**です（v0.8.0 の `file-search.md` 235-241行に `RLIMIT_AS` 1 GiB・`RLIMIT_CPU` 60 秒の記述があります）。v0.7.2 の同ファイル 235-241行（`c67c506`）は「`.pdf` is deliberately absent」と記述していました。`./`・`../` のパス補完（`GET /api/path-complete`）の `q` が最小文字数を持たない点（v0.9.0 の 69行）は、v0.7.2 の 56行（`c67c506`）から同じ記述です

> v0.9.0 で新しいのは `/api/file-search` の owner 専用化と、Command Bar の Mate 検索（当時の呼称は crewmate）が `PREVIEW_CREW` フラグの背後にある点で、本節はこの2点を v0.9.0 タグの仕様書で確認したものです。CHANGELOG/Release 本文は、この2点を説明していません（PDF の検索については、CHANGELOG.md v0.9.0 タグのファイルの 636-637行、v0.8.0節が「PDFs are searchable again from the file browser and from knowledge ingest」と記載しています）。`@` メンションの最小文字数と既定件数は、引き続き一次情報で確認できません（下の「未確認事項」）。

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/file-search.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/command-bar.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### Mate（v0.10.0 以前・公式ページでは crewmate）の Dashboard（v0.9.0 時点は Preview）

**v0.9.0 時点の記述です。v0.10.0 で Dashboard タブは Feature Preview を必要としなくなりました**（「[v0.11.1での変更](#v0111での変更)」の Dashboard 節）。

v0.9.0 では、**Settings → Developer → Feature Previews → Dynamic Dashboard** を有効にすると、Mate のサイドパネルに Dashboard タブが開き、既定ではプロジェクトレポートを表示しました。出荷されるページは12種類で（standup・roadmap・kanban など）、ほかのページはチャットで Mate に頼みます。数値はすべて Mate の Crew log から読み、測定されていないコストは 0 ではなく「—」で表示し、Mate 自身が書いた値は「crewmate wrote this」とタグ付けします（公式 Agents ページの表記）。`dashboard.dynamic_dashboard_cards` の既定は `false` です。v0.9.0 では、Mate を開いたときの挨拶カード、プロフィールカード（Permission・Model・Reasoning effort・Schedules・Sessions）、ヘッダーのスイッチャーも加わりました。

> Dynamic Dashboard は Mates ページ（v0.10.0 以前は Crewmates ページ）の機能です。本節は CHANGELOG v0.9.0節 15-43行と公式 Agents ページの記述の要約にとどめます。プロフィールカードの内容が v0.11.1 でも同じかどうかは、一次情報で確認できません（「[未確認事項](#未確認事項)」参照）。

出典: CHANGELOG.md v0.9.0節 15-43行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/capabilities/agents/>（Page updated 2026-10-20）

## v0.8.0での変更

v0.8.0 の CHANGELOG と、v0.9.0 時点の公式ページで確認できた、チャット体験の変更です。

### 外観・入力

- **Message Font Size**（**Settings → Chat → Transcript**）: メッセージ本文・コード・差分・表・チップ・コンポーザをまとめて拡大縮小します。サイドバーなどのダッシュボードのコントロールは元のサイズのままで、Compact の幅も文字に合わせて広がります
- **ターンミニマップがスクラブ用のレールになりました**: レールを選択またはドラッグして会話をスクラブでき、ホバーでそのターンと前後のターンをプレビューします。**Minimap location** で左端か右端かを選べます。スマートフォンとタッチ操作では表示されません
- **小さな改善**: ファイルのアップロード中の **Cancel upload** ボタン、**Double-click to edit your messages**（opt-in）、Keyboard shortcuts ダイアログの検索欄、ターミナルタブの **Rename**
- **Chat の設定のグループ化**: **Settings → Chat** は Transcript・Composer・Sessions・Side panel・Model・About You・Discovery・Advanced のグループになりました
- **Font Family**: **Settings → Display** に Font Family（Custom 可）と **Enable ligatures** が加わりました
- **すりガラスのコンポーザ**: コンポーザがトランスクリプトをぼかすペインの上に載ります。reduced transparency・high contrast・backdrop blur のないブラウザではソリッドなペインになります。v0.9.0 で、トップバーなどの磨りガラスは opt-in（**Translucent panels**、既定 off）になりました

出典: CHANGELOG.md v0.8.0節 239-250行・283-288行・447-466行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/chat/>（Page updated 2026-10-20）

### Decisions (Jev) の拡張（Preview）

**Preview** です（**Settings → Developer → Feature Previews → Decisions (Jev)**）。

- **Quiet check-ins** の行で、Jev のキーなしに、このマシンが既に使っているモデルプロバイダで監視ループの wake judge を動かせます（wake judge は、新しいことがないティックでモデルのターンを消費せず、プルリクエストが merge／close されると監視を終えます）
- **危険バッジ**は、プロバイダの確信度が **80% 以上**のときだけ付きます。判断には、同意した上限の範囲内で直近2〜3ターンを含められます
- `decisions.history_budget_chars` の既定は `0`（公式 Configuration ページの値。仕様書 `config.md` は 0 → 2000 の既定値の変更を載せており、食い違いとして「[v0.11.1での変更](#v0111での変更)」に併記しています）、`decisions.model_route.*` の既定は `""` のままです

出典: CHANGELOG.md v0.8.0節 200-213行・353-362行（`99e6253`）。
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **CHANGELOG v0.8.0**（358-359行）と **`modules/decisions.md`** 232行（`99e6253`）: スイッチが on のとき、モデルを固定していない（Auto のままの）セッションはターンごとに振り分けられ、コンポーザのチップは Auto (Jev) と表示されます
> - **公式 Configuration ページ**（Page updated 2026-10-20）: メインスイッチを on にしただけでは各機能は有効にならず、チャットのモデルピッカーで Auto (Jev) を選ぶ必要があると説明しています

> **解消済み（Developer Mode の要否）**: 公式 Configuration ページは Decisions (Jev) の手順として **Settings → Developer → Feature Previews → Decisions (Jev)** だけを記載し、Developer Mode に触れていません。v0.9.0 の `learn-cron-dashboard.md` 4265行（`99e6253`）は Feature Previews の節が Developer Mode の背後にないと記述しています。

## v0.7.0での変更

公式 Chat ページと v0.7.0 の CHANGELOG で確認できる、チャット体験の追加・変更です。

### Side Chat の読み取り専用ツール

- `/side` に加えて **`/btw`** エイリアスで開けるようになりました（CHANGELOG 76-77行）
- 公式 Chat ページは、親セッションが **Kiro CLI バックエンド**の場合に、Side Chat がファイルの読み取り・検索・fetch・読み取り専用のシェルコマンドを**承認プロンプトなしで**実行できると説明しています。それ以外は、読み取りしかしない MCP ツールも含めて**拒否**されます。Side Chat のターンには承認カードがないためです（CHANGELOG 76-80行／公式 Chat ページ「Side Chat」）
- 上記の不変条件（Birth-onlyメモリ・凍結スナップショット・JSONLやメモリストアに永続化しない）は v0.7.2 の `side.md`（17-19行・50-61行、`c67c506`）でも維持されています。v0.7.2 時点の読み取り専用の許可は kiro-cli バックエンドに限られていました（`side.md` 322-324行「kiro-cli only」）。**これは v0.10.0 以降は成り立ちません**。v0.10.0 の CHANGELOG と v0.11.1 の仕様書は、ほかのバックエンドにも許可を広げています（「[v0.11.1での変更](#v0111での変更)」の Side Chat 節）

### 送信・モデルピッカー

- **作業中の送信（Steer／Queue）**: 既定の動作を **Settings → Chat** で選べます。詳細は [02_sessions.md](02_sessions.md#v070での変更) を参照してください（CHANGELOG 65-68行）
- **モデルチップ**: コンポーザのモデルチップから推論の effort を同じメニューで選べるようになりました。**Settings → Chat → Selectable Models** でピッカーに出すモデルを選べますが、Auto と現在のセッションのモデルは常に表示されます（CHANGELOG 62-64行）
- **コンテンツフィルタ時のフォールバック**: 拒否されたメッセージを、**Settings → Chat** で選んだモデル（`agent.refusal_fallback_model`、**既定 off**）で1回だけ再試行します。次のターンでは元のモデルに戻ります（CHANGELOG 356-359行）
- **Response Verbosity** の設定が、組み込み・カスタム・スケジュールのすべてのエージェントに適用されるようになりました（CHANGELOG 360-362行）。v0.9.0 で既定が変わりました。下の「[v0.9.0での変更](#v090での変更)」を参照してください

### Decisions with Jev（Preview・Feature Preview）

**Preview 機能**です。**Settings → Developer → Feature Previews → Decisions (Jev)** カードで有効化します。カードに表示される送信先とデータの分類を確認してから有効化するよう公式が案内しています。同意は `config.json` の外に保存されるため、エージェントが設定を編集して有効化することはできません（公式 Configuration ページ「Decisions with Jev (Preview)」／CHANGELOG 292-298行）。

- **ターンごとのモデルの振り分け（model routing）**: チャットのモデルピッカーで **Auto (Jev)** を選ぶと、Jev がメッセージを simple／medium／complex に分類し、`config.json` の `decisions.model_route.simple`／`.medium`／`.complex` に割り当てたモデルでそのターンを実行します。3つとも**既定は `""`**（現在のモデルのまま）です。具体的なモデルを選んだ場合は常にそちらが優先され、スケジュールジョブ・サブエージェント・App のリクエスト・リモート crew のターンはそれぞれのモデル設定を使います（CHANGELOG 294-298行／公式 Configuration ページ）
- **Steer／Queue の判断**: 作業中の送信ボタンで **Auto (Jev)** を選ぶと、ターン途中に入力したメッセージを、実行中のターンに割り込ませるか次のターンまで待たせるかを Jev が判断します（CHANGELOG 299-301行）
- **判断の記録**: 返信の下のストリップに、そのターンが読み込んだスキル、メモリ想起で落としたもの、マシンの外に出たものが表示され、選択が正しかったかの評価を付けられます（CHANGELOG 302-304行）
- **無効化**: ガバナンスプロファイルの `capabilities.decisions` でプレビュー全体をオフにできます（CHANGELOG 304-305行）。`decisions.md` 61行は、所有者の同意（キーストーン）とは別に、このフリート側の上限が上位に立つと記述しています
- メインスイッチをオンにしただけでは各機能は有効になりません。上記の **Auto (Jev)** の選択など、機能ごとに所有者の選択が別に必要です（v0.7.2 時点の公式 Configuration ページ／`decisions.md` 7行「consenting to the seam arms nothing by itself」）。**v0.8.0 の CHANGELOG と v0.9.0 の `decisions.md` は、Auto のままのセッションがターンごとに振り分けられると記述しており、公式 Configuration ページ（Page updated 2026-10-20）の記述と食い違っています**（下の「[v0.8.0での変更](#v080での変更)」の「Decisions (Jev)」を参照）
- 判断のリクエストに含める過去の会話の文字数 `decisions.history_budget_chars` は、公式 Configuration ページでは**既定 `0`**（過去の会話を送らない）です。仕様書との食い違いは「[v0.11.1での変更](#v0111での変更)」に併記しています

### 画面・操作（UI）

- **ターンミニマップ**: デスクトップのチャットの左余白に、ターンごとのマーカーを表示します（ホバーでプレビュー、クリックでジャンプ、端のキャップで古い履歴を読み込み）。スマートフォンとタッチ操作では表示されません（CHANGELOG 49-51行）。v0.8.0 でスクラブ用のレールになりました（下の「[v0.8.0での変更](#v080での変更)」を参照）
- **Text Link Patterns**: **Settings → Chat → Text Link Patterns** で、正規表現と URL テンプレートの組を登録すると、チケット ID などのテキストを表示時にリンクにします（CHANGELOG 70-72行／公式 Chat ページ）
- **差分・表・コード**: 大きな差分の簡易表示に **Show line-by-line diff** が加わりました。返信内の Markdown の表は Markdown または CSV としてコピーでき、長いコードブロックは下端にもコピー・編集ボタンを表示します（CHANGELOG 56-58行・81-84行）
- **読みやすいツール呼び出し名**: トランスクリプトのツール行が、生のシェルコマンドではなく Read file・Search・Git のように処理内容で表示されます。分類できない場合は生のコマンドを残します（CHANGELOG 353-355行）
- **コンポーザ**: **Settings → Chat → Composer** に **Show Pasted Text in Full**（**既定 off**）と **Spell Check Message Input**（**既定 on**）が加わりました（CHANGELOG 338-342行）
- **Command Bar（Cmd+K／Ctrl+K）とナビゲーション**: Command Bar からフォルダとアーティファクト（Search Artifacts）も探せるようになりました。デスクトップ幅のウィンドウの上部バーに戻る／進むボタンが加わり、Cmd／Ctrl＋左右矢印キーでも操作できます。セッションの一覧はブックマーク可能な `/sessions` ページでも開けます（CHANGELOG 88-93行・366-373行／公式 Chat ページ「Navigation and the command bar」）

出典: CHANGELOG.md v0.7.0節 49-84行・292-305行・338-373行（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）。
**出典**: <https://kiro.dev/docs/crew/chat/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-09-25）

## 未確認事項

- `@` メンションの最小文字数と `GET /api/file-search` の既定件数（v0.9.0・v0.11.1 の `file-search.md` 26行・30行・55行も数値を記載していないため。上記「`@` メンションによるファイル添付」節を参照）
- プラン承認型の Autopilot が v0.9.0・v0.11.1 に存在するか、公式の「Autopilot トグル」と旧仕様書のモードが同じ機能を指すか（上記「Autopilot」節の食い違い）。`orchestrator.max_plan_duration_seconds` が v0.9.0・v0.11.1 で有効なキーかどうか
- `session.compact_wait_secs` のデータクラス既定値（公式 Configuration ページの記述のみ。v0.11.1 の `config.md` にも定義行がありません。上記「v0.9.0での変更」を参照）
- `decisions.history_budget_chars` のデータクラス既定値（公式 Configuration ページは `0`、仕様書 `config.md` の既定値変更表は 0 → 2000。「[v0.11.1での変更](#v0111での変更)」の食い違い）
- Dynamic Dashboard が出荷するページの数（公式 Agents ページは12種類。v0.10.0 以降の変更で増減したかは一次情報から確認できません）。プロフィールカード（Permission・Model・Reasoning effort・Schedules・Sessions）の内容が v0.11.1 でも同じかどうか
- v0.11.0 のコンポーザ・サイドパネルの設定のうち、Tail-only Fork の既定値と、**Pin Summary in Side Panel** の既定値・設定キー（CHANGELOG・仕様書・公式ページのいずれにも見つかりません）
- Settings → Developer → Feature Previews のカード名が v0.11.0 以降に「Mates」へ変わったかどうか（v0.10.0 の CHANGELOG 236行は「Crewmates」。v0.11.0 の CHANGELOG はカード名に触れていません）
- 「自分自身に応答する会話は1時間に90ターンで一時停止する」（v0.8.0 の CHANGELOG 604-605行。v0.11.1 のファイルでは 1005-1006行）の設定キー・既定値・対象チャネル。v0.11.1 の仕様書に記述が見つかりません

> **解消済み（Decisions (Jev) と Developer Mode）**: 以前は「Decisions (Jev) の有効化に Developer Mode が必要か」を未確認としていました。公式 Configuration ページと CHANGELOG v0.8.0 節は Feature Previews の手順だけを記載し、v0.9.0 の `learn-cron-dashboard.md` 4265行（`99e6253`。v0.11.1 では 5025行、`fe6f5be`）が Feature Previews の節は Developer Mode の背後にないと記述しています。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/v0.8.0/docs/system-specs/modules/autopilot.md>（v0.8.0 のタグには存在し、v0.9.0 のタグには存在しないため、タグ固定のURLを示します）
- リポジトリ（Side Chat）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/side.md>
- セッション基盤: [02_sessions.md](02_sessions.md)
- 自律実行（Proactive）: [06_autonomy.md](06_autonomy.md)

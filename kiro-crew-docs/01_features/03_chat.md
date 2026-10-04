# チャット体験

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/chat/>（配下の各ページ、Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{autopilot,side,file-search,themes}.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（v0.7.0での変更・`@`メンションの再確認・Autopilot の記述の食い違い）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/{autopilot,side,file-search,decisions}.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/chat/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-09-25）

---

## 📑 このページの内容

- [Autopilot](#autopilot)
- [`/side`（サイドカンバセーション）](#sideサイドカンバセーション)
- [`@` メンションによるファイル添付](#-メンションによるファイル添付)
- [テーマ](#テーマ)
- [v0.7.0での変更](#v070での変更)
- [未確認事項](#未確認事項)

---

## Autopilot

**Autopilot は Chat の per-slot（スロット単位）モードであり、独立したAppやページではありません。**

`_ChatSlot.mode == "orchestrator"` のときに有効化され、`PATCH /api/chat/slots/{slot}/mode` で切り替えます。モデルが段階的なプランを提示し、ユーザーが承認すると、**Python制御のステージループ**が1段ずつ実行を進めます。単純な依頼は普通のチャットと同様に動作し（プロンプトがモデルに直接回答するよう指示）、チェックポイント付きのプランに値する作業だけがプラン／承認／実行のフローに入ります。

> **`orchestrated` builtin app は既に存在しません**。`apps/manager.py` が起動時に古いインストールを削除します。フロントエンドは `/orchestrated/:slug?` を `/chat` へのリダイレクトとしてのみ保持しています。

**用語について**: 「Autopilot」がユーザー向けの名前（ナビ・ウェルカムビュー・セッションメニュー）です。スロットの `mode` 値・設定セクション・システムプロンプトのファイル名は内部名 `orchestrator` を保持しています（モード値がセッション履歴のメタデータに永続化されているため、リネームすると復元済みセッションが壊れます）。

> ⚠️ **Proactive とは別物**です。Proactiveは起動モード5分類の1つ（AutoNudge・goal-loopスキル）で、Autopilotとは異なる仕組みです。詳細は [06_autonomy.md](06_autonomy.md) を参照してください。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **モジュール仕様** `modules/autopilot.md` 5-9行（`c67c506`）: Autopilot は「the model presents a staged plan, the user approves it, and a Python-controlled stage loop drives execution one stage at a time」（上記の説明。v0.6.0 の同ファイルも同じ記述）
> - **公式ドキュメント**: Sessions ページ「Autopilot」節は「tool calls that pass the security gate to proceed without individual prompts」（拒否コマンド・機微パス・ガバナンスポリシーは引き続き適用）、Agents ページは「All tools auto-approved for this session」と、**セッション単位のツール自動承認**として説明しています（<https://kiro.dev/docs/crew/chat/sessions/>・<https://kiro.dev/docs/crew/capabilities/agents/>、いずれも Page updated 2026-09-25。v0.6.0 時点の両ページも同じ趣旨）
>
> 両者が同じトグルを指すのか、別の仕組みを指すのかは一次情報から判断できません。

## `/side`（サイドカンバセーション）

親チャットのスロットに、一時的なQ&Aスレッドを追加する機能です（ユーザー向けの名称は **Side Chat**）。`/side` コマンド（v0.7.0 からは `/btw` も）またはActivityパネルの「Side Chat」タブから起動します。v0.7.0 で、Kiro CLI バックエンドでは読み取り専用ツールを承認なしで実行できるようになりました（「[v0.7.0での変更](#v070での変更)」参照）。

**主な設計上の不変条件**:

1. **新しいスロットIDを作らない**: `slot._side: SideState | None` として存在
2. **メインパスは変更しない**: `context.py.build_message()` 等のメインスレッドパスは変更されない
3. **Birth-onlyメモリモード**: side は memory/learn/save を一切呼ばない。サイドカーバッファはクローズ時に**永続化なしで破棄**される
4. **独立したLLMセッション**: `f"side:{slot.key}"` というキーで、親のセッションとは別。ターンが親のコンテキストを汚染しない
5. **非ブロッキング**: `api_side_turn` は即座に応答を返し、ストリーミングはバックグラウンドタスクで実行される
6. **送信は決して失われない**: ターンが進行中でも、メッセージはそのターンにsteerされるかキューされる（拒否パスはない）

親のコンテキストは**凍結スナップショット**として読み込まれ、side は**JSONLやメモリストアに一切永続化しません**。

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

## v0.7.0での変更

公式 Chat ページと v0.7.0 の CHANGELOG で確認できる、チャット体験の追加・変更です。

### Side Chat の読み取り専用ツール

- `/side` に加えて **`/btw`** エイリアスで開けるようになりました（CHANGELOG 76-77行）
- 親セッションが **Kiro CLI バックエンド**の場合、Side Chat はファイルの読み取り・検索・fetch・読み取り専用のシェルコマンドを**承認プロンプトなしで**実行できます。それ以外は、読み取りしかしない MCP ツールも含めて**拒否**されます。Side Chat のターンには承認カードがないためです（CHANGELOG 76-80行／公式 Chat ページ「Side Chat」）
- 上記の不変条件（Birth-onlyメモリ・凍結スナップショット・JSONLやメモリストアに永続化しない）は v0.7.2 の `side.md`（17-19行・50-61行、`c67c506`）でも維持されています。読み取り専用の許可は kiro-cli バックエンドに限られます（`side.md` 322-324行「kiro-cli only」）

### 送信・モデルピッカー

- **作業中の送信（Steer／Queue）**: 既定の動作を **Settings → Chat** で選べます。詳細は [02_sessions.md](02_sessions.md#v070での変更) を参照してください（CHANGELOG 65-68行）
- **モデルチップ**: コンポーザのモデルチップから推論の effort を同じメニューで選べるようになりました。**Settings → Chat → Selectable Models** でピッカーに出すモデルを選べますが、Auto と現在のセッションのモデルは常に表示されます（CHANGELOG 62-64行）
- **コンテンツフィルタ時のフォールバック**: 拒否されたメッセージを、**Settings → Chat** で選んだモデル（`agent.refusal_fallback_model`、**既定 off**）で1回だけ再試行します。次のターンでは元のモデルに戻ります（CHANGELOG 356-359行）
- **Response Verbosity** の設定が、組み込み・カスタム・スケジュールのすべてのエージェントに適用されるようになりました（CHANGELOG 360-362行）

### Decisions with Jev（Preview・Feature Preview）

**Preview 機能**です。**Settings → Developer → Feature Previews → Decisions (Jev)** カードで有効化します。カードに表示される送信先とデータの分類を確認してから有効化するよう公式が案内しています。同意は `config.json` の外に保存されるため、エージェントが設定を編集して有効化することはできません（公式 Configuration ページ「Decisions with Jev (Preview)」／CHANGELOG 292-298行）。

- **ターンごとのモデルの振り分け（model routing）**: チャットのモデルピッカーで **Auto (Jev)** を選ぶと、Jev がメッセージを simple／medium／complex に分類し、`config.json` の `decisions.model_route.simple`／`.medium`／`.complex` に割り当てたモデルでそのターンを実行します。3つとも**既定は `""`**（現在のモデルのまま）です。具体的なモデルを選んだ場合は常にそちらが優先され、スケジュールジョブ・サブエージェント・App のリクエスト・リモート crew のターンはそれぞれのモデル設定を使います（CHANGELOG 294-298行／公式 Configuration ページ）
- **Steer／Queue の判断**: 作業中の送信ボタンで **Auto (Jev)** を選ぶと、ターン途中に入力したメッセージを、実行中のターンに割り込ませるか次のターンまで待たせるかを Jev が判断します（CHANGELOG 299-301行）
- **判断の記録**: 返信の下のストリップに、そのターンが読み込んだスキル、メモリ想起で落としたもの、マシンの外に出たものが表示され、選択が正しかったかの評価を付けられます（CHANGELOG 302-304行）
- **無効化**: ガバナンスプロファイルの `capabilities.decisions` でプレビュー全体をオフにできます（CHANGELOG 304-305行）。`decisions.md` 61行は、所有者の同意（キーストーン）とは別に、このフリート側の上限が上位に立つと記述しています
- メインスイッチをオンにしただけでは各機能は有効になりません。上記の **Auto (Jev)** の選択など、機能ごとに所有者の選択が別に必要です（公式 Configuration ページ／`decisions.md` 7行「consenting to the seam arms nothing by itself」）
- 判断のリクエストに含める過去の会話の文字数 `decisions.history_budget_chars` は**既定 `0`**（過去の会話を送らない）です（公式 Configuration ページ）

### 画面・操作（UI）

- **ターンミニマップ**: デスクトップのチャットの左余白に、ターンごとのマーカーを表示します（ホバーでプレビュー、クリックでジャンプ、端のキャップで古い履歴を読み込み）。スマートフォンとタッチ操作では表示されません（CHANGELOG 49-51行）
- **Text Link Patterns**: **Settings → Chat → Text Link Patterns** で、正規表現と URL テンプレートの組を登録すると、チケット ID などのテキストを表示時にリンクにします（CHANGELOG 70-72行／公式 Chat ページ）
- **差分・表・コード**: 大きな差分の簡易表示に **Show line-by-line diff** が加わりました。返信内の Markdown の表は Markdown または CSV としてコピーでき、長いコードブロックは下端にもコピー・編集ボタンを表示します（CHANGELOG 56-58行・81-84行）
- **読みやすいツール呼び出し名**: トランスクリプトのツール行が、生のシェルコマンドではなく Read file・Search・Git のように処理内容で表示されます。分類できない場合は生のコマンドを残します（CHANGELOG 353-355行）
- **コンポーザ**: **Settings → Chat → Composer** に **Show Pasted Text in Full**（**既定 off**）と **Spell Check Message Input**（**既定 on**）が加わりました（CHANGELOG 338-342行）
- **Command Bar（Cmd+K／Ctrl+K）とナビゲーション**: Command Bar からフォルダとアーティファクト（Search Artifacts）も探せるようになりました。デスクトップ幅のウィンドウの上部バーに戻る／進むボタンが加わり、Cmd／Ctrl＋左右矢印キーでも操作できます。セッションの一覧はブックマーク可能な `/sessions` ページでも開けます（CHANGELOG 88-93行・366-373行／公式 Chat ページ「Navigation and the command bar」）

出典: CHANGELOG.md v0.7.0節 49-84行・292-305行・338-373行（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）。
**出典**: <https://kiro.dev/docs/crew/chat/>・<https://kiro.dev/docs/crew/configuration/>（いずれも Page updated 2026-09-25）

## 未確認事項

- `@` メンションの最小文字数と `GET /api/file-search` の既定件数（v0.7.2 の `file-search.md` が数値を記載していないため。上記「`@` メンションによるファイル添付」節を参照）
- Decisions (Jev) の有効化に Developer Mode が必要かどうか。公式 Configuration ページと CHANGELOG v0.7.0節は **Settings → Developer → Feature Previews → Decisions (Jev)** の手順だけを記載し、Developer Mode に触れていません。v0.7.2 の `learn-cron-dashboard.md` 2700行（`c67c506`）は Feature Previews 節が「NOT behind Developer Mode」と記述しています

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/chat/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/v0.7.2/docs/system-specs/modules/autopilot.md>（`main` ブランチでは v0.7.2 以降にこのファイルが削除されているため、タグ固定のURLを示します）
- セッション基盤: [02_sessions.md](02_sessions.md)
- 自律実行（Proactive）: [06_autonomy.md](06_autonomy.md)

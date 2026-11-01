# 更新履歴

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/releases>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

---

## 📑 このページの内容

- [v0.11.1](#v0111)
- [v0.11.0](#v0110)
- [v0.10.0](#v0100)
- [v0.9.0](#v090)
- [v0.8.0](#v080)
- [v0.7.2](#v072)
- [v0.7.1](#v071)
- [v0.7.0](#v070)
- [v0.6.0](#v060)
- [v0.5.0](#v050)
- [v0.4.1](#v041)
- [v0.4.0](#v040)
- [v0.3.0](#v030)
- [v0.2.0](#v020)
- [v0.1.3](#v013)
- [v0.1.2](#v012)
- [v0.1.0・v0.1.1](#v010v011)
- [未確認事項](#未確認事項)

---

> このページは **v0.1.2〜v0.11.1** をCHANGELOG.mdに版節があるものから要約しています。CHANGELOG.mdは開発者向けの詳細記述（PR番号付き・1項目10行超）のため、そのまま転記せず、利用者に影響する変更に絞っています。

### v0.11.1

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-10-31 |
| GitHub Release 公開日 | 2026-10-31 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.11.1>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md#0111---2026-10-31>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

v0.11.1 は v0.11.0 へのホットパッチです（CHANGELOG.md v0.11.1節 5-9行）。節は「Notable fixes」だけで、「**Before you upgrade**」節はありません。2系統の日付は一致しています。

#### 利用者に影響する変更（C-L1/C-L2）

- **メモリ**: メモリの読み取りが書き込みの後ろで待たなくなりました。メモリプールが混んでいるときは、ターンを待たせ続けずに再試行できるエラーで終わります。再起動後の最初の応答が早く始まります。別のプロセスがメモリデータベースを閉じても書き込みログが保持されるため、直近の記憶が失われなくなりました。起動時の prefetch でメモリインデックスが壊れることもなくなりました（CHANGELOG.md 13-19行）
  → 詳細は [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md#v0111での変更)
- **KAS エンジン**: エージェント仕様に従う動作が kiro-cli に近づきました（CHANGELOG.md 20-28行）。
  - 仕様が許可する組み込みツールは、Crew 自身の検査を通った後に自動承認されます
  - 仕様が許可するシェルコマンドをゲートで尊重し、既定で拒否する仕様ではそれ以外のコマンドを拒否します
  - 既定で拒否する仕様の許可パスの外へのファイル書き込みを拒否します
  - 仕様の hooks は終了コード 2 のときだけツールをブロックします（kiro-cli と同じ）
  - MCP サーバーには真偽値の env フラグが渡され、シークレットは渡されません
  - 相対パスのプロンプトファイルで `..` が使えます（kiro-cli と同じ）
  - 履歴が返らなかった再開済みセッションは、履歴を再生します
  - ウェブ検索はエンジンが期待する名前でマウントされます

  → 詳細は [01_features/15_agent-backends.md](../01_features/15_agent-backends.md#v0111での変更) / [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md#v0111での変更)
- **チャットと設定**: kiro-cli v3 の書き込みツールによるファイル変更がトランスクリプトに再び表示されます。バックグラウンドのツール承認ごとに ID が付くため、1つの回答で別の承認が決着しません。kiro-cli の読み取り専用のファイル検索は、安全性の検査の後に承認されます。無限大・非数の値を保存したワークフローの run が再び開きます。`config.local.json` が上書きする保存を Settings が拒否します。スケジュールの時刻ラベルが夏時間の切り替えをまたいでも壁時計の時を保ちます。ライブ crew log・Knowledge の取り込み・サブエージェントのイベントなどのバックグラウンド処理は、通知なしに止まらず最後まで実行されます（CHANGELOG.md 29-38行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更) / [01_features/17_workflows.md](../01_features/17_workflows.md#v0111での変更) / [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **セキュリティ**: シェルリーダーが、オプションやリダイレクトの後ろに置かれた `-c` スクリプトを検出します。クラウドガードの人間専用アクションでは、すべてのエージェントプロセスがエージェントとして数えられます。`find -type f` や `od -tx1` などを curl のアップロードと誤認して拒否していた拒否ルールを削除しました。ローカルの判定モデルは、公表済みの勧告が修正された `filelock` をインストールします（CHANGELOG.md 39-44行）
  → 詳細は [01_features/09_security.md](../01_features/09_security.md#v0111での変更)
- **デスクトップと CLI**: ワンライナーと `install.sh` のインストーラは、既定で Crew 組み込みの KAS エンジンをダウンロードします（`--no-kas` で省略）。`kirocrew restart` は別の gateway が同じポートを使っているときにそれを知らせます。`kirocrew stop` と `kirocrew restart` は、デスクトップアプリが監督する gateway を拒否します。起動中にデスクトップアプリを終了しても gateway が残りません。Windows の復旧は、ネットワーク検査に失敗したとき諦める前に再試行します。iPhone のキーボードの上に新しいターミナルが留まります。Crew スタックの動作中アイコンの点滅と位置が改善しました。ホスト全体のメモリ不足 kill を1つのサンドボックス上限のせいにしなくなりました（CHANGELOG.md 45-54行）
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md#v0111での変更) / [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md#v0111での変更)

#### 開発者向け変更（C-L3・件数のみ）

- CHANGELOG.md に開発者向け変更として区分された節はありません: 0件

### v0.11.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-10-24 |
| GitHub Release 公開日 | 2026-10-30 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.11.0>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md#0110---2026-10-24>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

> v0.11.0 の CHANGELOG.md には「**Before you upgrade**」節が**ありません**（v0.11.1 のファイルの行番号で 55-226行）。本サイトは破壊的変更として分類せず、既定値が変わった項目を明記します。
>
> **呼称の変更**: v0.11.0 で、画面上の「crewmate」が「**Mate**」の表記に変わりました（Mates ページ・名簿・ダイアログ・設定行・チャットヘッダー。CHANGELOG.md 88-89行）。公式ページには「crewmate」の表記が残るものがあります。v0.10.0 以前の節では「crewmate」と書きます。

#### 利用者に影響する変更（C-L1/C-L2）

- **既定のハーネスが KAS に変わりました**: 保存した選択のない新規インストールは KAS で始まり、一覧では Kiro CLI より前に並び、各ハーネスのロゴとともに「Kiro Agent」と表示されます。明示的に選んだ Kiro CLI は維持されます（CHANGELOG.md 149-153行）。デスクトップアプリは固定した KAS エンジンを同梱し、`install.sh` で取得でき、kiro-cli の同梱をやめて利用者自身のインストールを検出します。クレジット使用量は Crew のサインインから読み、エンジンの切り替えは Settings → Developer → Feature Previews に移りました（同 154-158行）。MCP サーバーの elicitation 要求に応答し、MCP の変更が稼働中のセッションにその場で反映されます。`agent.kas_persist_mcp_sign_in`（既定オフ）で、リモート MCP のサインインがセッションをまたいで保持されます（同 158-161行の「MCP on KAS」項。行範囲は 149-168行）。他のバックエンドでは、稼働中の pi のターンを steer でき、pi のメンバースレッドは Mate パネルを得て、opencode は稼働中のターンへのメッセージ追加を受け付けます。DeepSeek ハーネスの Side Chat は読み取り専用ツールを実行し、Kiro の Side Chat は認証情報のパスを拒否します。Opus 5.5・Sonnet 5.5・Fable 5.1・MiniMax のウィンドウが登録され、Usage タブは kiro-cli のトークン推定を表示しなくなりました
  → 詳細は [01_features/15_agent-backends.md](../01_features/15_agent-backends.md#v0111での変更) / [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md#v0111での変更) / [03_deployment/01_installation.md](../03_deployment/01_installation.md#v0111での変更)

  > ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
  >
  > | 出典 | 記述 |
  > |------|------|
  > | CHANGELOG.md v0.11.0節（v0.11.1 のファイルの 149-153行） | 保存した選択のない新規インストールは KAS で始まる |
  > | 公式 Agent Backends ページ（Page updated 2026-10-12） | Kiro CLI を既定のバックエンドと記述 |
  >
  > 公式ページの更新日（2026-10-12）は、CHANGELOG.md の v0.11.0 の日付（2026-10-24）より前です。
- **Mate の新しい仕組み（Mate 2.0）**: 各 Mate が `~/.kiro/mates/agents/` の下に自分のエージェントファイルを持ちます。メモを残す conductor のチャットで利用者と話し、実作業は Profile に従いスキルを持つ worker セッションに任せます。既存の Mate は起動時に1度だけ移行され、変更点を知らせる通知が出ます。conductor はアーカイブ済みの worker にメッセージを送って復帰させられます。worker の報告は再起動後も Mate を起こします。Goals タブの Heartbeat check-in（オプトイン）は 30・60・120・240 分ごとに Mate を起こします。Profile は monitor の状態を示します。`.crewmate` ファイルから Mate を1つインポートできます。Mate は自分の Dashboard ページを作って着せ替えでき、適用で公開され、1回の呼び出しで戻せます。ページを PNG として見たり、進捗をチャットでなくページに置いたり、worker セッションを表示したり、週次レポートを印刷できるページとして送ったりもできます。**Mate 自身のプレビュー（既定オフ）**をオンにすると、worker に無いツールを探してカードで要求できます。チャットを開き直すと最後に読んだメッセージに着地し、古い履歴はスクロールして読み込まれます。メッセージは実行中のターンに steer され、Mate の DM は通知を出します（CHANGELOG.md 65-89行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更) / [01_features/02_sessions.md](../01_features/02_sessions.md#v0111での変更) / [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **チャットの停止・フォーク・読みやすさ**: コンポーザの Escape で実行中のターンを止められます。返信のストリーミング中に選んだモデルはターンの境界で有効になり、失敗しなくなりました。Optimize prompt はターン実行中にも使え、キャンセルできます。Tail-only Fork をオンにすると、メッセージのメニューに「Fork with later messages only」と「Fork with earlier messages」が加わります。右クリックメニューに「Open link in new tab」が加わり、コンポーザでは Tab・Shift+Tab でリスト行をインデント・解除できます。エージェントが lesson を保存した行が出て Review lessons にリンクし、画像の読み取りはサムネイルを示し、同じファイルへの連続した編集は1行にまとまり、会話途中のセッションリセットはすべて印が付き、compaction で切れた返信は続きます。Settings → Chat → Sessions でサイドバーのセッションを専用のタブに開け、Settings → Chat → Side panel に Keep Side Panel Open と Pin Summary in Side Panel が加わります。Git タブはチャットが触るすべてのリポジトリを列挙し、ファイルツリーが切り詰めたフォルダは専用タブで開き、artifacts のコードブロックは行を指すコメントを受け、Mate のサイドパネル文書はインラインコメントを受けます（CHANGELOG.md 90-110行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更) / [01_features/12_artifacts.md](../01_features/12_artifacts.md#v0111での変更)
- **サイドバー・検索・通知**: 固定されていない行の間にセッションをドロップすると並び順が Manual に切り替わり、Undo 付きの「Sorted by hand」が出ます。Alt+Up・Alt+Down でフォーカス行を動かせます。並び順と選択は gateway に保存されるため、どのブラウザも同じ一覧を示します。サイドバーの Broadcast message は複数のセッションへ1通を送ります。Settings → Chat で New Chat の Default Sidebar Folder を指定できます。検索は `title:` 接頭辞でタイトルに限定でき、中国語のクエリは1文字ずつでなく単語に分割されます。固定した行の帯は、タグのフィルタで一覧を絞っている間ラベルが付きます。通知は送信者ごとに積み重なりグループ単位で消え、エージェントが公開した通知は元のセッションへリンクし、Fix with Crew は通知を事前入力した新しいチャットを開きます（CHANGELOG.md 111-125行）
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md#v0111での変更)
- **スケジュールとコマンドライン**: Schedule のジョブフォームで、実行時間の上限と自動停止の上限（0 は無制限）をジョブごとに設定できます。失敗のバックオフ中であることがボードに出ます。「Runs as」で Custom agent か Mate を選べます。`app.json` の cron は `strict_schedule` で分の頭に起動できます。`kirocrew spawn run` は `--model`・`--agent`・`--crew` を、エージェントの作成・更新コマンドは `--model` を、`kirocrew cron add` と `update` は `--auto-pause-after` を受け取ります。チャットの権限プロンプトは入力した返答を受け付け、`spawn_run` のタスクは短いラベルを持てます（CHANGELOG.md 126-138行）
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) / [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md#v0111での変更)
- **音声とテーマ**: Text-to-Speech の言語を設定で選べます。Settings → Voice → Fine-tuning で、利用者が意図して止めたときに音声入力を送れます。音声設定は選んだプロバイダについて「Is my audio kept?」に答えます。gateway ホストで読み上げられない場合、Read aloud は利用者の端末で読み上げます。組み込みテーマに Nu Disco が加わり、Create Theme ダイアログに Paste CSS タブが加わります（CHANGELOG.md 139-148行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更)
- **リモートセッション・App・スキル**: チャットのワークスペースを Coder のワークスペース上で動かせます（エージェントエンジンは gateway に残ります）。Bitbucket Server のプルリクエストを `dashboard.bitbucket_server_hosts` で読み、Azure DevOps の監視は編集されたレビューコメントで起きます。初回起動と Settings のインポートで Amazon Quick の設定を読めます。インストール済み App は新版の公開を知り、外部レジストリの App はストアが更新を案内し、ChatEmbed のホストはチャットの一部を隠して停止ボタンを出せ、インストール同意ゲートはコミュニティレジストリのレビュー階層を示します。組み込みの `living-ui` スキルは、ウィジェットと Dashboard ページでの動き・フォーカス・読み出しのあり方を教えます（CHANGELOG.md 169-184行）
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md) / [01_features/10_apps.md](../01_features/10_apps.md#v0111での変更) / [01_features/14_migration-import.md](../01_features/14_migration-import.md) / [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md#v0111での変更) / [01_features/17_workflows.md](../01_features/17_workflows.md#v0111での変更)
- **軽さと速さ**: ストリーミング中の返信は最後の段落だけを再解析します。バックグラウンドのセッションはフレームごとに1回ページへ通知します。新しいチャットのメモリ検索はセッション起動と並行します。ブラウジングが未設定のときはプロンプトから Browser 節を外し、ターンが使えないスキルは注入しません。Crew 自身の MCP サーバーは起動時の読み込みが軽くなり、コールド検索は採点を1回で共有します（CHANGELOG.md 185-194行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更) / [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md#v0111での変更)
- **Notable fixes**: チャット・セッション、チャネル（Slack・Telegram・Weixin）、スケジュール、デスクトップと更新、セキュリティとアクセスの5分野の修正が列挙されています（CHANGELOG.md 195-226行）。主なもの: システム全体の呼び出しホットキーは新規インストールでオプトインになりました（既定値が変わりました）。シェル展開がクラウドメタデータの拒否をすり抜けなくなり、ルートやホームの `rm -rf` はよく使われる書き方でも拒否されます。リモート MCP のプローブ URL は SSRF の検査を受け、CLI は gateway のピアを確認してからローカルのシークレットを送り、owner ゲートはセッション履歴・Knowledge の読み取り・タスク操作に及び、Mate の記録は gateway 専用のディレクトリに置かれ、各ハーネス自身の権限ファイルは書き込み保護されます。分割された AWS キーペアやストリーム途中で切れたリンクは1つのまとまりとして秘匿され、certifi は勧告に合わせて更新されました
  → 詳細は [01_features/09_security.md](../01_features/09_security.md#v0111での変更) / [01_features/11_interfaces.md](../01_features/11_interfaces.md#v0111での変更) / [03_deployment/01_installation.md](../03_deployment/01_installation.md#v0111での変更)

#### 開発者向け変更（C-L3・件数のみ）

- CHANGELOG.md に開発者向け変更として区分された節はありません: 0件

### v0.10.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-10-15 |
| GitHub Release 公開日 | 2026-10-25 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.10.0>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md#0100---2026-10-15>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

> v0.10.0 の CHANGELOG.md には「**Before you upgrade**」節が**ありません**（v0.11.1 のファイルの行番号で 227-405行）。本サイトは破壊的変更として分類せず、既定値が変わった項目を明記します。本節の「crewmate」は v0.10.0 当時の呼称で、v0.11.0 から画面上は「Mate」に変わりました。

#### 利用者に影響する変更（C-L1/C-L2）

- **crewmate が利用者と計画を立てる（Preview）**: Settings → Developer → Feature Previews → Crewmates をオンにすると、Crewmates ページの初回表示で最初の crewmate「Mate」が開き、crewmate の役割を説明して名前を付けさせます。New crewmate は、チャットの上の窓に1枚のカードとして開きます。crewmate はマイルストーンを紐づけた目標を持ち、check-in とレポートをカードで提案します。変更はカードで提案され、利用者が承認します。自分の名前と説明をチャットから更新でき、作成時に専用のワークスペースを得ます（CHANGELOG.md 234-246行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更) / [01_features/02_sessions.md](../01_features/02_sessions.md#v0111での変更)
- **Dashboard が Preview を外れました**: Dashboard タブに Feature Preview が不要になり、メインセッションのサイドパネルが専用の dashboard を示します。「Automatic cards for all sessions」は Settings → Developer の独立したカードに移り、**既定はオフのまま**です。crewmate は `dashboard` スキルで自分のページを作り、利用者が Dashboard タブで保持か破棄を選びます。`~/.kiro/crew/panel-templates/` に置いたページが同梱ページと並んで提示され、conductor は board で開き、組み込みページは UI 言語に従います（CHANGELOG.md 247-260行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更) / [01_features/12_artifacts.md](../01_features/12_artifacts.md#v0111での変更)
- **リードと引き継ぎ**: 既定のエージェントとして `kirocrew-team-lead` が同梱され、目標を作業項目に分け、項目ごとにセッションを開き、小さなものは自分で行います。`spawn_run` はタスクごとにバックエンドを取り、Subagents カードはサブエージェントのツール呼び出しをすべて列挙します。エージェントの質問カードは利用者の回答を待ち、回答をエージェントへ返します（利用者の名前のメッセージとしては送られません）（CHANGELOG.md 261-270行）
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) / [01_features/15_agent-backends.md](../01_features/15_agent-backends.md)
- **チャットの移動**: 返信の右クリックメニューに Copy as rich text（Outlook や Word に見出し・リスト・表を保って貼れる）が加わりました。Alt+Up・Alt+Down で開いているチャットのプロンプトを移動でき、エージェントが名指したファイルは返信の下に Open file チップで出ます。実行中のターンは直近5行の活動だけを示し、Settings → Chat → Transcript → Tool calls start expanded でツール行を開いたままにでき、セッションメニューの Export as readable Markdown は人が読めるトランスクリプトを保存します（CHANGELOG.md 271-283行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更)
- **ターンを終える**: Settings → Chat → Advanced → Turn Time Limit (seconds) でターンの実行時間を設定でき、タイムアウトのカードで1つのセッションだけ別の上限で動かせます。モデルプロバイダへの短いネットワーク断は待って越えます。満杯で続けられない会話は、再試行を繰り返さず新しいセッションを提案します（CHANGELOG.md 284-293行）
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md#v0111での変更)
- **各バックエンドの強化**: Claude Code と goose のターン中に送ったメッセージはそのターンへ steer されます。reasoning effort の操作が goose と opencode に届き、手動の `/compact` が KAS と pi で動きます。Settings → Agent Harness → Use the built-in KAS engine（**既定オフ**）は、このリリースに固定したエンジンビルドから KAS をインストールして動かすため、KAS に kiro-cli のインストールが不要になります。Side Chat は Claude Code・goose・KAS で読み取り専用ツールを実行し、pi のセッションは Crew の MCP サーバーを得ます（CHANGELOG.md 294-304行）
  → 詳細は [01_features/15_agent-backends.md](../01_features/15_agent-backends.md)
- **サイドバー**: フィルタメニューに Filter by model が加わり（モデルごとのセッション数と Hide sessions on these models 行）、動作中のセッション名の前に脈動する点が付き、crew のグループヘッダーは承認待ち・回答待ち・動作中のチャット数を数えます。crew 自身のフォルダは crew グループ内に出て、Settings → Chat → Sessions → Show Full Titles While Scrolling は長いタイトルを読める状態に保ちます（CHANGELOG.md 305-315行）
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md#v0111での変更)
- **設定（プロキシ・プロファイル・信頼）**: `agent.env` はすべてのエージェントプロセスに `HTTPS_PROXY` や `NODE_EXTRA_CA_CERTS` などの変数を設定します。`aws.project_profiles` はプロジェクトフォルダに対応づけた AWS プロファイルでセッションを始めます。チャットの承認プロンプトに、このコマンド、または同種のすべてのコマンドを1時間または当日の残りだけ信頼する選択肢が加わります。`dashboard.github_hosts` で GitHub Enterprise ホストを追加でき、チャネルトークンは `secret://` 参照を受けて新しいものを vault に保存し、`agent.model_context_tokens` はモデルが提供されるコンテキストウィンドウを宣言します（CHANGELOG.md 316-329行）
  → 詳細は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md#v0111での変更) / [01_features/09_security.md](../01_features/09_security.md#v0111での変更)
- **メモリの制御**: `kirocrew memory forget` でメモリを削除でき、Memory ページは各 lesson の由来を示します。`memory.writes_enabled` と `memory.lesson_extraction_enabled` でメモリの書き込みと lesson 抽出を止められます。Settings → Import / Export の Export memory only・Import memory only でメモリだけを移せ、crew config のエクスポートはシークレットを置き換えたエージェントテンプレートを含められます（CHANGELOG.md 330-340行）
  → 詳細は [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md#v0111での変更) / [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md#v0111での変更)
- **リモート crew**: `cloud.json` の `microvm` ブロックで、AWS Lambda MicroVM（秒課金）上で crew を動かすレーンを追加できます。既定の寿命は1時間で、その後はホームが消えます。Remote Crew 行と crew ウィンドウのヘッダーは、古いビルドで動く crew を示して更新を案内し、owner は1つのリモート crew を無効にできます（CHANGELOG.md 341-349行）
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- **Usage・音声・サウンド**: Usage タブの Overview に、チャネル・エージェント・モデル・週で積み上げる Spend over time (credits) チャートが加わり、Developer → Telemetry は全カードで1つの時間窓を使います。`stt.transcribe_languages` は Amazon Transcribe に1ストリーム内で2〜5言語を検出させます。音声入力が自動で止まると音が鳴り、返信の読み上げ中はコンポーザの上に Stop reading のバーが出ます。Settings → Notifications → Custom sounds は名前付きの音を保存前に試せ、crewmate の通知にはアバターが付きます（CHANGELOG.md 350-361行）
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md) / [01_features/03_chat.md](../01_features/03_chat.md#v0111での変更)
- **Issue Radar**: 自分のプルリクエストの CI 失敗を通知でき（CI runs タブとリポジトリごとのスイッチ）、GitLab のグループを追うとサブグループを含むすべてのレビュー依頼が届きます（CHANGELOG.md 362-368行）
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md#v0111での変更)
- **軽さと速さ**: 埋め込みモデルは1時間アイドルでアンロードされ（`memory.embedding_idle_evict_secs`）、コアの多いホストで gateway が保持するメモリが減ります。Knowledge 検索は約5分の1の時間で返り、長いセッションは全メッセージを再検査せずに描画されます。Crew 自身の MCP サーバーは起動が速く、終わったツールにすぐ応答します（CHANGELOG.md 369-378行）
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md#v0111での変更) / [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md#v0111での変更)
- **Notable fixes**: チャット・セッション、チャネル、スケジュール、Windows、セキュリティとアクセスの5分野の修正が列挙されています（CHANGELOG.md 379-405行）。主なもの: git は読み取り専用のシェルコマンドとして自動承認されなくなりました。プログラムへの信頼付与は書き込みリダイレクトを含まなくなりました。デスクトップアプリはダッシュボードのトークンをログに出さず、gateway は切れた署名鍵で起動を拒否し、webapp のプレビューは `unsafe-eval` なしで動きます。Slack・Telegram・Discord は切断後に返信を二重投稿せず、1回限りの cron は失敗・タイムアウト・キャンセルでも保持されて保留されます
  → 詳細は [01_features/09_security.md](../01_features/09_security.md#v0111での変更) / [01_features/11_interfaces.md](../01_features/11_interfaces.md#v0111での変更) / [01_features/06_autonomy.md](../01_features/06_autonomy.md) / [03_deployment/02_windows.md](../03_deployment/02_windows.md#v0111での変更)

#### 開発者向け変更（C-L3・件数のみ）

- CHANGELOG.md に開発者向け変更として区分された節はありません: 0件

### v0.9.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-10-09 |
| GitHub Release 公開日 | 2026-10-16 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.9.0>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

> v0.9.0 の CHANGELOG.md・Release 本文には「**Before you upgrade**」節が**ありません**。本サイトは破壊的変更として分類せず、既定値が変わった項目を下に分けて示します。Release 本文は CHANGELOG.md の版節全文に PR 一覧（What's Changed）を付けたものです。

#### 既定値・名称が変わったもの（一次情報で確認したもの）

- **新規インストールの Response Verbosity が Answer only**（既存の設定は保存済みのレベルを維持）。**Ultra レベルは廃止**されました（CHANGELOG.md v0.9.0節 154-156行）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md)
- **半透明パネルは opt-in**（Settings → Display → View → Translucent panels。既定は不透明のカード）
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md)
- **Agent Capabilities が Customize に改称**（CHANGELOG.md v0.9.0節 150-152行）。公式の一部ページは「Agent Capabilities」のままで、出典間で表記が異なります
  → 詳細は [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md)
- **`session.watchdog_rss_max_mb` の既定が 0（無効）に戻りました**（v0.7.0〜v0.8.0 は 1536）。CHANGELOG.md と Release 本文に説明はありません（`config.md` 634行・仕様書で確認）
  → 詳細は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

#### 新機能・変更（利用者に影響するもの・抜粋）

- **crewmate が一目で分かる** — Crewmates ページで開くと目標・完了・実行中・待機中・次の一手を示すカード、プロフィールカード（Permission・Model・Reasoning effort・Schedules・Sessions）、ヘッダーの切り替え
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md) / [01_features/03_chat.md](../01_features/03_chat.md)
- **crewmate ごとのダッシュボード（Preview）** — Settings → Developer → Feature Previews → Dynamic Dashboard をオンにすると、Dashboard タブに12種の出荷済みページから選べます。数値は crew log から読み、未計測の値は 0 ではなくダッシュで表示されます
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md) / [01_features/12_artifacts.md](../01_features/12_artifacts.md)
- **リモート crew を生きた窓として開く（Preview）** — Settings → Developer → Feature Previews → Remote crew sessions。相手の transcript・実行状態・承認待ちを窓として開き、このマシンには保存しません。旧 turn relay は廃止され、relay で動いたチャットは読み取り専用です
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md) / [01_features/02_sessions.md](../01_features/02_sessions.md)
- **コンポーザ** — コンテキストウィンドウの警告、Style Markdown While Typing（既定オフ・beta）、Files タブからのドラッグ、Cmd/Ctrl+Up で直前のメッセージを編集、`! <command>` でシェルコマンドをレビューして実行
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md)
- **メッセージ操作** — Quote、表の Widen、Side Chat の Add to main chat
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md)
- **サイドバー** — 状態別の非表示と Pause all filters、Clean up empty folders、Regenerate title、Mark sessions unread only when they need you
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md)
- **チャネル** — Slack でダッシュボードの新規セッションを bot との DM のスレッドに自動で結び付け（`slack.auto_link_sessions`・既定オフ）、Telegram の forum topic と `TELEGRAM_API_BASE_URL`、Telegram・Teams のターン中メッセージは steer またはキュー
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md)
- **Usage** — Kiro の推定トークン、クレジットがいつ尽きるかの見積り、サブエージェントと cron のクレジット表示
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- **スケジュール・メモリ・CLI** — 失敗した実行を Ask the agent でチャットへ渡す、保存済みメモリの Restore、`kirocrew memory create-store`、`kirocrew cron add --managed-by`、`kirocrew cloud launch --ami/--extra-packages`、Import / Export に永続チャット履歴
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) / [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md) / [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)
- **デスクトップ・ターミナル・音声** — ターミナルのカーソル形状と Ctrl+`、画像のコピー、PowerPoint のスライド表示、音声入力の語彙
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md)
- **セキュリティ** — データホームのファイルは `0600`・ディレクトリは `0700`、組み込み App の書き込みルートは dashboard owner のみ、信頼できないチェックアウトの agent spec の hooks はターンループに届かない、ホスト側 git の git hooks は無効。あわせて、既知のギャップの8点目（Design Critique の capture browser の DNS rebinding）が `security-deep-dive.md` に追加されています（CHANGELOG.md に記述なし）
  → 詳細は [01_features/09_security.md](../01_features/09_security.md) / [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)

### v0.8.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-10-08 |
| GitHub Release 公開日 | 2026-10-09 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.8.0>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

> **日付の注記**: 上の CHANGELOG.md の日付は v0.9.0 タグのファイル（187行目）の値です。同じ `[0.8.0]` 節の日付は v0.8.0 タグのファイル（5行目）では 2026-09-27 で、節の本文は変わっていません。日付が変わった理由は一次情報に書かれていません。本サイトは裁定せず、両方を示します。
>
> v0.8.0 の CHANGELOG.md・Release 本文には「**Before you upgrade**」節が**ありません**。本サイトは破壊的変更として分類せず、既定値が変わった項目を下に分けて示します。

#### 既定値が変わったもの（一次情報で確認したもの）

- **crew log が既定で記録される**（`KIROCREW_CREW_LOG=0` で無効。v0.7.x は既定オフ）。会話を削除すると crew log も削除され、セッション ledger・conductor の作業ボード・Issue Radar の crew ledger が新規インストールで動きます
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md) / [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- **所有者が書いた自動承認リストが保持される**（`mcp.honour_auto_approve`・既定 `true`・変更に再起動が必要）。リストのツールは承認カードと Crew のツールゲートを飛ばします
  → 詳細は [01_features/09_security.md](../01_features/09_security.md) / [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md)
- **サブエージェントの起動に要求する空きメモリが 4.5 GB から、起動後に 2 GB 残る場合へ**（`agent.spawn_min_memory_gb` の既定 2.0。`config.md` は旧既定を 4.0 と記述）
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **単一タスクの委任に理由を要求する拒否がなくなりました**（CHANGELOG.md v0.8.0節）。公式 Subagents ページは拒否すると記述したままで、出典間で食い違います
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **`agent.max_subagents` 0（自動）・`agent.subagent_auto_max` 32 に `config.md` が一致**（v0.7.2 の `config.md` は 3 と 16 で、`subagent.md` と食い違っていた）
  → 詳細は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

#### 新機能・変更（利用者に影響するもの・抜粋）

- **監視ループが必要なときだけ起こす** — wake judge（Quiet check-ins）、レビューやコメントでも起床、マージ・クローズで終了、`monitoring.max_runtime_secs`
  → 詳細は [01_features/17_workflows.md](../01_features/17_workflows.md)
- **デスクトップアプリが Kiro CLI を同梱**（macOS・Linux・Windows）。サインイン後すぐ動きます
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **認証情報の秘匿化が読める** — 除去された認証情報のカード、ブロックされたリンクの Open once／Allow for this host／Inspect、ファイル表示の秘匿化トグル（既定オン）
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **厳格なサンドボックス層** — `agent.sandbox` に `strict`。承認の再検査（approval floor）、設定ファイルの書き換え禁止
  → 詳細は [01_features/09_security.md](../01_features/09_security.md) / [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)
- **チャットの設定と操作** — Message Font Size、ターンのミニマップ（スクラブ・位置選択）、Chat 設定を名前付きグループに整理
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md)
- **フォルダとタグ** — フォルダごとの追加 steering ディレクトリ、フォルダの並び順、conductor ビュー、タグごとの Agent permissions、`dashboard.title_refresh_every_turns`
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md) / [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md)
- **Agent templates タブと crewmate の表示名** — テンプレートの作成・複製・編集、Chat with this template／Enroll as crewmate
  → 詳細は [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md)
- **チームと Decisions (Jev)（Preview）** — Crew Members preview の teams、Quiet check-ins、Auto (Jev)
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md) / [01_features/17_workflows.md](../01_features/17_workflows.md)
- **メモリを切り替えられる** — `memory.persistence_enabled`・`memory.inject_memory`・`memory.inject_lessons`・`memory.inject_activity`
  → 詳細は [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md)
- **App・MCP** — MCP App からチャットへメッセージを送る、共有 MCP バックエンドの Stub レビュー（Developer Mode）、WeCom のファイル送信、Code Review Sage の Requests タブ、Tool Search（kiro-cli 2.27.0 以上）
  （管理対象サーバに `kirocrew-debug` が加わっていますが、CHANGELOG.md に記述はありません。`architecture/mcp.md` と `docs/reference/debug/README.md` で確認した内容は、下記リンク先に記載しています）
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md) / [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md) / [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)
- **DeepSeek Harness（Preview・Developer Mode）と hooks の作成** — Agent Backends の選択肢が8種に。Hooks ページで Kiro Agent の11トリガーのフックを書けます
  → 詳細は [01_features/15_agent-backends.md](../01_features/15_agent-backends.md) / [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md)
- **リモート crew** — EC2 のサブネット指定、crew の連鎖（2ホップまで）、Fargate レーンの `internal_only`（既定 `false`・サンドボックスなしで動く宣言）
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- **コマンドライン** — `kirocrew cron add` が script・command・ワンショットを含むすべてのジョブを登録、`kirocrew doctor` がスキルのずれを報告、Browser パネルが追加ポート転送なしでトンネル越しに動作
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md) / [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)

### v0.7.2

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-09-28 |
| GitHub Release 公開日 | 2026-09-29 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.7.2>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

CHANGELOG.md と Release 本文はともに「**A small fix.**」の1文だけで、内容を説明していません（Release 本文の PR 一覧は「drop the rc suffix for the 0.7.2 stable cut」の1件）。

> **仕様書側の差分（本サイトの実測）**: v0.7.1 タグと v0.7.2 タグの `docs/` の差分は `modules/messaging.md`・`modules/security.md`・`modules/subagent.md` の3ファイルです。内容は、オペレーターとして信頼されないチャネル送信者のターンをツールを持たないエージェント `kirocrew-guest` で動かすこと、および Subagent の run 操作（steer・status・retry など）を起点セッションに限定すること（範囲外は 404 `task_scope_denied`）です。これらが v0.7.2 の変更であると CHANGELOG/Release は述べていません。
>  → 詳細は [01_features/09_security.md](../01_features/09_security.md) / [01_features/06_autonomy.md](../01_features/06_autonomy.md)

### v0.7.1

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-09-24 |
| GitHub Release 公開日 | 2026-09-25 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.7.1>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

ダッシュボードの遅さ2点（チャット開始が遅い・チャット間の移動が遅い）に対するホットパッチです（CHANGELOG.md 9-26行）。

- **セッションとサブエージェント**: エージェントバックエンド用に公開するエージェント単位のビューファイルを、実行中のセッションが保持しなくなった時点で回収するようになりました。数千件まで増えたホストでは新しいチャットとバックグラウンドのサブエージェントが最初の応答まで数秒待ち、さらに増えるとエージェントを読み込めずチャットが開始できなくなっていました。掃除は次にセッションを開いたときに自動で行われます
- **チャットペイン**: タブ切り替えでダッシュボードが止まらなくなりました。再接続するペインは表示する行だけを要求し、読み直したメッセージは計算済みの秘匿化（redaction）結果を再利用します

### v0.7.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-09-15 |
| GitHub Release 公開日 | 2026-09-24 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.7.0>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

> v0.7.0 の CHANGELOG.md・Release 本文には「**Before you upgrade**」節が**ありません**。本サイトは破壊的変更として分類せず、既定値が変わった項目を下に分けて示します。Release 本文は CHANGELOG.md の版節全文に PR 一覧（What's Changed）を付けたものです。

#### 既定値が変わったもの（一次情報で確認したもの）

- **`agent.subagent_max_turns` の既定が 100 → 1000**（`config.md` 407・1849行）。キー未設定なら更新後も自動で1000に従い、保存済みの値は保持されます
  → 詳細は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)
- **`skills.lazy_load` の既定が true**（v0.6.0 の仕様書は false）。スキル本文を一括注入せず、短い索引と `skill_search` で見つける方式です
  → 詳細は [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md)
- **リポジトリのコンテキストバジェット（`_CONTEXT_BUDGET_BASE`）が固定 33,000 文字**（v0.6.0 は 165,000 文字）。公式 memory ページは変わっておらず、出典間で食い違います
  → 詳細は [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md) / [04_reference/05_limits.md](../04_reference/05_limits.md)
- **Windows で委譲できるサンドボックスがない経路が既定で非サンドボックス実行**（`windows-install.md`。v0.6.0 は fail closed）。公式ページ・README は fail-closed と記述しており、出典間で食い違います。CHANGELOG はこの変更に触れていません
  → 詳細は [03_deployment/02_windows.md](../03_deployment/02_windows.md)
- **Windows・Linux の「設定を開く」ショートカットが `Alt+,`**（macOS は `Cmd+,` のまま）
- **`session.watchdog_rss_max_mb` の既定が 1536 MiB**（v0.6.0 は 0＝無効）
  → 詳細は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

#### 新機能・変更（利用者に影響するもの・抜粋）

- **設定が再起動なしで反映** — `config.json` の保存や Settings の変更がほぼすべて実行中の Gateway に即時反映されます
- **更新チェックが12時間ごと** — 自動適用は新しいターンを止め、進行中の作業が終わるまで待ちます。必要な Python を満たさないソース更新はチェックアウトを動かす前に拒否します
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **キューに入った作業が再起動を越えて残る** — サブエージェント・TaskRunner のステップ・workflow 呼び出しが永続キューに入り、並行数はホストの実際の空きに合わせて変わります。`spawn_run` は理由のない単独タスクを拒否します
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) / [01_features/17_workflows.md](../01_features/17_workflows.md)
- **チャット** — ターンのミニマップ、Steer/Queue の既定の選択、Default Memory Mode、Text Link Patterns、Side Chat の `/btw` と読み取り専用ツール、`/sessions` ページ、セッションのファイル書き出し・取り込み
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md) / [01_features/02_sessions.md](../01_features/02_sessions.md)
- **Jev がターンごとにモデルを選ぶ（Preview）** — Settings → Developer → Feature Previews の Decisions (Jev) をオンにし、`decisions.model_route` で対応付けます。`capabilities.decisions` でプレビュー全体を無効化できます
  → 詳細は [01_features/03_chat.md](../01_features/03_chat.md)
- **エージェントバックエンドの追加（Preview・Developer Mode 前提）** — OpenCode・Pi・goose が選択肢に加わりました。Pi のセッションは Kiro Crew 自身の MCP ツールを持ちません
  → 詳細は [01_features/15_agent-backends.md](../01_features/15_agent-backends.md)
- **チャネル** — 任意のファイル種別の添付（最大50MB）、再起動中に届いたメッセージへの通知、Slack の `update_message` ツール。Settings → Channels は Messaging Channels に改称
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md)
- **PR の監視が GitHub 以外にも対応** — GitLab・Bitbucket Cloud・Azure DevOps Services。監視ループは種類を問わず停止・確認できます
  → 詳細は [01_features/17_workflows.md](../01_features/17_workflows.md)
- **Windows** — 隔離 pod が Task Scheduler 経由で動作（`pod api` を除く）、デスクトップ版 Gateway のコールドスタートが約4倍速く、TLS 検査プロキシの背後でもターンが動作
  → 詳細は [03_deployment/02_windows.md](../03_deployment/02_windows.md)
- **セキュリティ** — 資格情報スキャナが止めたファイル配信の承認（`kirocrew file-delivery approve`）、同意による SSH agent forwarding（既定オフ）、ポリシーが読めない場合の fail closed、既知のギャップに7点目（同一ユーザーによるランチャの自己汚染は受容・非防御）
  → 詳細は [01_features/09_security.md](../01_features/09_security.md) / [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)
- **エージェントとスキル** — 親テンプレートからの継承、Markdown 1ファイルのエージェント、リポジトリからのスキル取り込み、lesson の `applies`（`always`／`on_topic`）
  → 詳細は [01_features/07_agents-skills-steering.md](../01_features/07_agents-skills-steering.md) / [01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md)
- **Knowledge** — C#・Kotlin・Swift・Scala の取り込み、検索のスコープ指定、`kirocrew knowledge stats`
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)
- **Apps** — `kirocrew app import` による他ハーネスのプラグイン取り込み（パッケージ内のコードは実行しない）、App によるセッション操作（App ごとに既定オフ）、ソース別のストア表示
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **Cron** — Minimal context トグル、`cron-cost-optimize` スキル
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **Remote crews** — 接続方式に Fargate が加わりました（AWS CLI と Session Manager plugin が必要）
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- **インストーラ** — 事前ビルドの wheel のみを使い、ない場合は理由を表示して止まります（`KIROCREW_ALLOW_SOURCE_BUILDS=1` で従来動作）
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)

#### Notable fixes

チャット・モバイル・セキュリティ・承認・MCP・メッセージング・Windows/macOS など22分野の修正が列挙されています（CHANGELOG.md 485-675行）。本サイトの既存記述と矛盾するものは各ページに反映しました。

### v0.6.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-09-05 |
| GitHub Release 公開日 | 2026-09-11 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.6.0>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

#### Before you upgrade（破壊的変更・4件）

- **Python 3.12 が下限**になりました。3.10・3.11 のホストはインストール・更新の前に上げる必要があります。システムのパッケージマネージャに 3.12 がない場合は、各インストーラが自分で 3.12 を用意します
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **インストーラが自前の Python を持ち込む**ようになりました。`curl -fsSL https://download.crew.kiro.dev/cli.sh | sh` はシステムの Python ではなく**ピン留めされた CPython** を用意します。意図してシステム側に対してビルドする場合は `--system-python` を渡します
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **コマンドゲートがコマンド文字列を読んで credential パスを塞ぐ方式をやめました**。今後は**サンドボックスの bind mask が境界**です。この文字列ゲートに依存していた場合は、`config.json` の `agent.sandbox` が `off` になっていないか確認が必要です
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **無人の auto-run plan が2時間で停止**します。`config.json` の `orchestrator.max_plan_duration_seconds` で引き上げるか、`0` で上限を外します。**stage-gated な plan は打ち切られません**
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md) / [04_reference/05_limits.md](../04_reference/05_limits.md)

#### 新機能（利用者に影響するもの・抜粋）

- **ハーネスの選択（Preview）** — Claude Code・Codex・KAS を選べます。Settings → Developer で Developer Mode をオン（既定オフ）にしてから Developer → Agent Backend で選択します。**Claude 自身の設定で事前承認されたツール呼び出しは Crew の承認パスに到達せず、拒否ルールと監査ログがその呼び出しを見ません**
  → 詳細は [01_features/15_agent-backends.md](../01_features/15_agent-backends.md)
- **Remote crews（Preview）** — `instances.enabled` で、接続済みの別 crew 上でチャットを実行できます。別所で動くセッションには server badge と crew 名が付きます
  → 詳細は [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)
- **長時間の作業** — チャットの1ターンが最大4時間（`agent.chat_turn_timeout_secs`）、サブエージェントは3時間・最大1000ツール呼び出しになりました
  → 詳細は [04_reference/05_limits.md](../04_reference/05_limits.md) / [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)
- **エージェントが自分の監視ループを制御** — 開始・変更・停止をエージェント自身が行えます。goal chip にサイクル上限が表示されます。`agent.session_control` は既定 true で、`false` で無効化します
  → 詳細は [01_features/17_workflows.md](../01_features/17_workflows.md)
- **AWS Control が Overview で開く** — アカウント・キーの健全性・ドライブ使用量・共有リンク・バックアップスケジュールを1画面に表示します。Files ペインはその場でプレビュー・リネームします
  → 詳細は [01_features/16_aws-control.md](../01_features/16_aws-control.md)
- **Apps に Launchpad** — Apps → Library がグリッド表示になり、アプリはバックグラウンド処理・Command Bar の行・埋め込みチャットを持てます
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **Crew members に顔（Preview）** — ghost avatar を組み立てられます。**Developer Mode 前提の Preview opt-in** です
- **ゲートが理由を説明する** — ブロックされたツール呼び出しが次の手を示します。拒否ルールは綴り替えに耐えるようになり、通常の作業が誤って拒否されることが減りました。**サンドボックスできないホスト（armv7l・riscv64 など）はエージェントの実行を拒否します**
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **承認の形を変えられる** — サンドボックス内のコマンドが自分の上限を書き換えられなくなりました。再起動時に auto-approve grant を落としたことを通知します
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **計測** — cron・heartbeat を含むすべてのターンがトークン・支出・レイテンシを報告します
  → 詳細は [03_deployment/06_telemetry-and-privacy.md](../03_deployment/06_telemetry-and-privacy.md)
- **Artifact の公開** — 自分の AWS アカウント上の公開 HTTPS URL へ artifact を公開できます（`publish.allowed_destinations`）
  → 詳細は [01_features/12_artifacts.md](../01_features/12_artifacts.md)
- **自動 Knowledge フォルダの廃止** — フォルダは明示的に追加したときだけ Library に入ります
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)

### v0.5.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-29 |
| GitHub Release 公開日 | 2026-09-05 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.5.0>
（参照: 2026-09-13 / commit `e683282` / 版 v0.5.0）

#### Before you upgrade（破壊的変更・12件）

> **⚠️ 出典間で件数が食い違っています。本サイトは裁定せず両方を示します。**
> CHANGELOG.md の `[0.5.0]` 節の "Before you upgrade" は **12項目**ですが、GitHub Release 本文は **5項目**のみを挙げ、本文中で "Five changes" と明記しています。本サイトは**CHANGELOG.md の12件を根拠**とし、Release 本文には5件しか記載がないことを注記します。どちらが正しいかは判断しません。

- **Dictation provider が単一の `local` provider に統合**されました
- **Snapshot-to-S3 が廃止**されました。`kirocrew snapshot --to s3://…`・`--aws-profile`・`s3://` からの fetch が削除され、クラウドバックアップは AWS Control app に移りました。引き換えにスナップショットは live state への restore を獲得しています
  → 詳細は [01_features/16_aws-control.md](../01_features/16_aws-control.md)
- **App の実行信頼が、同意したコードに束縛**されました。grant は同意した時点のコードに紐づきます
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **黙って実行されていた一部のコマンドが確認を求める**ようになりました
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **Kiro CLI へは published relay 経由で到達**するようになりました（bundle-path 系の環境変数2件が削除）
- **security-policy の `sandbox` キーの綴り誤りが検証エラーになりました**（従来は黙って無視）。`publish` が malformed な場合は publish を拒否します
- **リリースが最小サポート版を宣言できる**ようになりました。下回るインストールには snooze・skip・dismiss ができない更新プロンプトが出ます
  → 詳細は [02_release-policy.md](02_release-policy.md)
- **Knowledge が Agent Capabilities 配下へ移動**しました（単独の Knowledge ページは廃止）
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)
- **単独の Auto-Triage Pipeline app が廃止**され、そのボードは他所へ移りました
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **Disconnect が本当に切断する**ようになりました。接続の削除は OAuth grant の revoke も行います
- **Malformed な agent spec が明示的に失敗**するようになりました（従来は黙って読み飛ばし）
- **`kirocrew gateway --no-tunnel`** — 新フラグで起動した gateway はトンネルを張りません
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

> **注**: 上記のうち、Release 本文に記載があるのは「Dictation provider の統合」「Snapshot-to-S3 の廃止」「App 実行信頼の束縛」「確認を求めるコマンド」と、Knowledge 移動と Auto-Triage 廃止を1項目に統合したものです。残りは CHANGELOG.md にのみ記載されています。

#### 新機能（利用者に影響するもの・抜粋）

- **AWS Control（builtin App・既定オフ）** — 接続済み AWS アカウントの健全性・プライベート S3 ドライブ・クラウドバックアップ・費用を1画面で扱います。**Apps > Library で有効化**します
  → 詳細は [01_features/16_aws-control.md](../01_features/16_aws-control.md)
- **セキュリティポリシーの中央配布** — `security_policy.json` を URL で配布し、各ホストが fetch します
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **セッションがタブになる** — ダッシュボードのセッション表示がタブ形式になりました
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md)
- **エージェントが他のエージェントを動かす** — `session_send` が他セッションへ次のターンとしてメッセージを配送します。conductor エージェントがこの上に構築されています
  → 詳細は [01_features/17_workflows.md](../01_features/17_workflows.md)
- **承認を誘導できる** — 承認の挙動を設定で方向づけられます
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **Secrets の適用範囲拡大**・**MCP サーバの無言劣化の解消**・**スマートフォンとタッチ対応**・**Meetings の自動翻訳**（対象言語を選ぶと逐行で翻訳）
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md) / [04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)
- **どこからでも自己更新**・**Issue Radar と Dev Fleet の強化**・**高速化と軽量化**
- **多言語化の拡充** — CHANGELOG は「Counted labels, confirmation dialogs and sign-in guidance are fully translated in all 12 languages」と記述しています（**v0.1.2 節の「10言語対応」から増加**）。破壊的プロンプトはその言語の引用符で資源名を囲み、5つのメニューがキーボード操作・フォーカス復帰・スクリーンリーダー通知に対応しました
- **`tunnel.enabled`・`dashboard.browser_view_port`・`slack.trusted_bot_ids`** の設定キーが追加されました
  → 詳細は [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

### v0.4.1

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-28 |
| GitHub Release 公開日 | 2026-08-29 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.4.1>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

安定チャネルの表示修正です。About、Settings footer、更新ポップアップは、内部のrelease-candidate stampではなく、インストール済み・利用可能な**正式リリース番号**を表示します。更新の仕組み、skip、snoozeの動作は変わりません。

### v0.4.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-25 |
| GitHub Release 公開日 | 2026-08-27 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.4.0>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

主な変更（利用者に影響するもの・抜粋）:

- **WindowsとLinuxの導入** — Windowsは署名済みinstallerとin-app auto-updateをstable配布。Linux desktopは`.deb`/`.rpm`（glibc 2.34以上）を提供し、旧ディストリビューション向けに`--managed-python`がある
- **Windows Computer Use** — UI AutomationでWindowsネイティブアプリを読み取り・操作でき、Windows agent treeにはJob objectのprocess/memory ceilingが追加
- **チャネル** — WhatsApp、iMessage、Feishuが追加。Teams/Telegram/WebexがSlackとの機能パリティへ近づき、Discordにはコマンドメニュー等が追加
- **Secrets** — config fileではなく暗号化vaultに保存し、MCP環境で`secret://NAME`参照を使える。値はSettings → Secretsでマスクされ、ブラウザへ送られない
- **ダッシュボード/セッション** — inline編集・diff・file tree、複数Gateway横断のセッション検索、Session hand-off、Reloadなどを追加
- **Memory / Skills** — repository scopeのLessonが有効化、tag別episodic decay、project-local skills、hooksのmatcher/injectionを追加

暗号方式、設定キー、保存先、およびbuiltin App数は、このCHANGELOG記述だけでは確定しないため補完しません。詳細は各機能ページを参照してください。

### v0.3.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-17 |
| GitHub Release 公開日 | 2026-08-21 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.3.0>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

#### Before you upgrade（破壊的変更・5件）

- **Node.js 22が最小要件**（24 LTS推奨）。Node 20のインストールは拒否される
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **Multi-account Telegramが撤回**。単一bot tokenのみ受理し`telegram.bot_token`へ移行
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md)
- **`kirocrew logout`がrefresh tokenも失効**させる（access tokenに加えて）
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)
- **terminal出力のcredentialスキャンに関する記述**。**⚠️ 同一v0.3.0節内に「スキャンしない」（Before you upgrade）と「ライブストリームでscrubする」（Security and governance）という矛盾する記述があり、本サイトは裁定せず両方を記載しています**
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)
- **Knowledge auto-ingestがopt-in化**（既定オフ）。設定キー`knowledge.auto_ingest_artifacts`
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)

#### 新機能（利用者に影響するもの・抜粋）

- **Crew Mode** — 前のメッセージを待たずに次を送信でき、並列サブセッションで処理される
- **Session summaries** — サイドパネルタブが各スレッドの意図と着地点を示す（opt-in）
  → 詳細は [01_features/02_sessions.md](../01_features/02_sessions.md)
- **Browser panel** — エージェントがダッシュボードのサイドパネルを直接操作。Playwright CLIはリモートセッション用に残る
  → 詳細は [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)
- **Git panel** — サイドパネルにリポジトリ状態とコミットログ
- **Linux ARM64・Windowsのfirst-class build**
  → 詳細は [03_deployment/01_installation.md](../03_deployment/01_installation.md)
- **`kirocrew tailnet up`によるtailnet公開**・ダッシュボードからのcloud crew起動
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)
- **Personal Shopper・Issue Radar Crews**（CHANGELOGは「2つの新App」と表現）・App Store刷新。**⚠️ 両Appの実装自体は既存**（`personal_shopper`はv0.2.0以前から、`issue_radar`はv0.1.2から存在）で、CHANGELOGの表現と実装年代が一致しません。本サイトは両方を記載しています
  → 詳細は [01_features/10_apps.md](../01_features/10_apps.md)
- **Computer Useの提示方法が変更**（動作する環境にのみ提示）。**プラットフォームは引き続きmacOSのみ**
  → 詳細は [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md)
- **各jobが自身の時間予算を設定可能**（最大24時間）
  → 詳細は [04_reference/05_limits.md](../04_reference/05_limits.md)
- **メモリガバナー**（メモリ枯渇時にスケジュールジョブを延期・新規subagentを拒否）
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **`kirocrew policy show`が拒否コマンドカタログをカテゴリ別に要約**
  → 詳細は [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)
- **MCPサーバの共有可否をプローブ**・per-agent tool sets・認証付きカスタムサーバ
  → 詳細は [01_features/08_mcp-integration.md](../01_features/08_mcp-integration.md)
- **Subagentが主エージェントと同様に承認を要求**
  → 詳細は [01_features/06_autonomy.md](../01_features/06_autonomy.md)
- **Knowledge支出に上限**・lessonsが関連度で浮上
  → 詳細は [01_features/05_knowledge-library.md](../01_features/05_knowledge-library.md)
- **画像がartifactとして保持**・push to talk
  → 詳細は [01_features/12_artifacts.md](../01_features/12_artifacts.md)
- **Telegramに実際のコマンドメニュー**
  → 詳細は [01_features/11_interfaces.md](../01_features/11_interfaces.md)
- **パフォーマンス改善**（初回メッセージのレイテンシ短縮・コールド読込の転送量削減・ディクテーション高速化・ストリーミング改善）

#### Security and governance（セキュリティ・ガバナンス・7件）

- Appは自身のイベントのみ参照可能に
- スケジュールジョブが毎実行ごとに再審査される
- メモリ上限が全同時エージェント合計に適用
- ライブストリームでcredentialがscrubされる（**Before you upgradeの記述と矛盾。上記参照**）
- ピン留めされたポリシー下限をローカルで引き下げ不可
- メモリ編集に認識済みセッションが必要
- 独自のIDプロバイダを持ち込み可能
  → 詳細は [01_features/09_security.md](../01_features/09_security.md)・[03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)

#### 開発者向け変更（C-L3・件数のみ）

- Notable fixes（Chat and composer／Sessions and stopping／Apps and settings／Channels and notifications／Desktop, install, and CLI／Security and resources／Everywhere else）: **7カテゴリ**（v0.2.0以前のCHANGELOG節に前例がないため件数のみ記載。個別項目は展開しません）

### v0.2.0

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-09 |
| GitHub Release 公開日 | 2026-08-10 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.2.0>

主な変更（利用者に影響するもの・抜粋）:

- **Persistent Browser Mode** — Settingsのスイッチ1つでエージェントが永続ブラウザセッションを使えるようになった
- **Spec Builder** — 仕様駆動開発のサーフェス（[01_features/10_apps.md](../01_features/10_apps.md)のbuiltin App参照）
- **Ops Mission Control** — インシデントタイムライン付きの自律的な運用初動対応者
- **Crew Companion** — エージェントの動きを反映するデスクコンパニオン
- **Auto-Improvement** — measurement-firstの自己改善（[01_features/04_memory-and-learning.md](../01_features/04_memory-and-learning.md)参照）

### v0.1.3

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-08-07 |
| GitHub Release 公開日 | 2026-08-05 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.3>

model entitlementのhot patch: モデルピッカーがアカウントが利用可能なモデルにスコープを限定し、アカウントが利用できないモデルは送信されなくなりました。利用不可のモデルは、容量エラーや生のJSON-RPCダンプではなく、アクセス問題として報告されます（箇条書き項目はなく、CHANGELOG.md本文の概要記述が出典）。

### v0.1.2

| 日付系統 | 値 |
|---------|-----|
| CHANGELOG.md | 2026-07-30 |
| GitHub Release 公開日 | 2026-08-04 |

**出典**: <https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.2>

主な変更（利用者に影響するもの・抜粋）:

- **One agent, ten ways in** — Webダッシュボード・ネイティブデスクトップアプリ・ターミナル等、複数のサーフェスからアクセス可能に
- **長時間セッション向けのダッシュボード** — 複数の並行チャットに対応
- **音声入出力** — WebSocket経由のライブストリーミングSTT
- **10言語対応** — インターフェースの多言語化
- **無人のマルチステップタスク** — 仕様を渡すと分解・実行する（TaskRunner。[01_features/06_autonomy.md](../01_features/06_autonomy.md)参照）

### v0.1.0・v0.1.1

CHANGELOG.mdに版節が存在しません（**最古の節はv0.1.2**）。Release本文のみが出典です。

- v0.1.0（<https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.0>） — 2026-07-22公開
- v0.1.1（<https://github.com/kirodotdev/KiroCrew/releases/tag/v0.1.1>） — 2026-07-28公開

## 未確認事項

- v0.1.0・v0.1.1のRelease本文の詳細な要約（本ページでは版とリンクのみを記載）
- v0.10.0 の CHANGELOG.md の日付（2026-10-15）と GitHub Release 公開日（2026-10-25）、v0.11.0 の CHANGELOG.md の日付（2026-10-24）と Release 公開日（2026-10-30）が異なる理由（一次情報に記述なし。v0.11.1 は2系統とも 2026-10-31 で一致）
- v0.10.0 の Release 一覧には `-insider.1` の Release が存在しない（`-insider.2`〜`-insider.5` と `-rc.1` が存在）。欠番の理由は一次情報に記述なし。プレリリースの扱いは [02_release-policy.md](02_release-policy.md) を参照
- v0.11.0 の既定ハーネスの変更（KAS）と公式 Agent Backends ページ（Page updated 2026-10-12）の記述（Kiro CLI が既定）の食い違い。本ページは裁定せず、v0.11.0 の節に両方を示した

## 関連リンク

- CHANGELOG: <https://github.com/kirodotdev/KiroCrew/blob/main/CHANGELOG.md>
- Releases: <https://github.com/kirodotdev/KiroCrew/releases>
- リリース方針: [02_release-policy.md](02_release-policy.md)

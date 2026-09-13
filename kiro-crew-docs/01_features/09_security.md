# セキュリティ

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [脅威モデル](#脅威モデル)
- [8つの保護機構（公式の順序）](#8つの保護機構公式の順序)
- [層数についての注記](#層数についての注記)
- [Owner lock](#owner-lock)
- [ガバナンス（POLICY ∩ PROFILE）](#ガバナンスpolicy--profile)
- [Audit（SEL）](#auditsel)
- [v0.3.0での変更](#v030での変更)
- [既知のギャップ（公式が明記）](#既知のギャップ公式が明記)
- [未確認事項](#未確認事項)

---

## 脅威モデル

Crew はAIエージェントに実際のツールアクセス（ファイル読み込み・シェルコマンド・ウェブブラウジング）を与えます。セキュリティモデルは**多層防御**（defense-in-depth）で、各層はプロンプトの指示だけに頼らず、**ランタイムの境界で強制されます**。モデルは信頼できる呼び出し元ではなく、信頼できない入力として扱われます。

## 8つの保護機構（公式の順序）

公式ページは、すべてのツール呼び出しが以下の順序でチェックされると明記しています。

1. **Owner lock** — チャネルGatewayが、メッセージがセッションに到達する前に未認可ユーザーを拒否
2. **Denied commands**（拒否コマンド） — **137パターン**が破壊的操作をブロック（承認を求める前にチェック）
3. **Governance ceiling**（ガバナンス上限） — Policy ∩ Profile（最も厳しい方が勝つ）。エージェントやAppは緩められない
4. **Sensitive path blocking**（機密パスのブロック） — 認証情報のディレクトリ・ファイルはツール呼び出しからアクセス不可
5. **Tool approval**（ツール承認） — 対話的レビュー・信頼の段階的昇格・Autopilot（拒否チェックを通過した後のみ発動）
6. **Input validation**（入力検証） — MCPスキーマ・型チェック・長さ制限・Unicode正規化
7. **OS sandbox**（OSサンドボックス） — LinuxのnamespaceまたはmacOSのSeatbeltによるプロセスレベルのファイルシステム隔離
8. **Output redaction**（出力の秘匿化） — チャットに到達する前に認証情報のパターンを応答から除去

> **⚠️ v0.3.0に関する注意**: 上記8番目は公式ページが示す**エージェント応答全般**の秘匿化です。これとは別に、**terminal出力の秘匿化についてはv0.3.0のCHANGELOG内で相反する記述があります**。詳細は下記「[v0.3.0での変更](#v030での変更)」を参照してください。

**Audit（SEL）はすべての段階の決定を記録します**（横断的な仕組みであり、順序上の1ゲートではありません）。

## 層数についての注記

> **重要**: リポジトリのアーキテクチャ文書は番号付きの層（Layer 0〜5、全層を貫く2つの制御）として整理していますが、**公式ドキュメントは層数を数値で示していません**（"defense-in-depth: multiple independent layers" という表現のみ）。したがって本ページでは**公式の8機構リスト**（上記）を正としつつ、「公式が何層と述べている」という表現は使いません。

## サンドボックスの3モード

| モード | 設定値 | 隠されるもの | アクセスできるもの | 想定用途 |
|-------|-------|------------|-----------------|---------|
| **標準（既定）** | **`auto`** | `.gnupg` / `.gcloud` / `.azure` / `.docker` | `.aws` / `.ssh` / `.kube` | ほとんどの利用者（git-over-SSHとAWS CLIが使える） |
| 厳格 | `strict` | 上記すべて＋`.aws` / `.ssh` / `.kube` | `~/.ssh/known_hosts` のみ | ロックダウン運用 |
| 無効 | `off` | 何も隠さない | すべて | トレードオフを理解している場合 |

設定は Settings → Security、または `kirocrew config set agent.sandbox <mode>`。**Windowsには OS レベルのサンドボックス層がありません**（公式明記: 「Windows does not currently have this OS-level layer — all other protections still apply」）。Linuxではuser/mount namespaces、macOSではSeatbeltプロファイルを使用します。

> ⚠️ **呼称と値域の食い違い（出典3系統・裁定しない）**
>
> | 出典 | 記述 |
> |---|---|
> | リポジトリ `README.md` **385行** | 「Seatbelt isolation. **Standard, strict, and off modes** make the tradeoff…」＝**3モード**として提示 |
> | `docs/system-specs/modules/config.md` **940行** | `agent.sandbox` の既定は **`"auto"`**（Linuxはnamespace、macOSはseatbelt。macOSで有効時はkiro-cli内部のサンドボックスに委譲）、**`"off"`** はKiro Crewのサンドボックスをスキップ。**`strict` の記載はありません** |
> | `docs/architecture/security-deep-dive.md` **107-112行** | `wrap_argv` の内部ティア語彙は設定enumより広く **`standard`（`auto` の解決先）／`cc`／`strict`／`off` の4種**。これらは内部呼び出しとガバナンスの `sandbox.min_level` 順序尺度（`_ORDINAL_SCALES["sandbox"] = ("off", "standard", "cc", "strict")`）から到達し、要求されたモードを**上へ**クランプする。**「They are not values an operator writes into `agent.sandbox`」と明記** |
>
> 設定値は `auto`、内部ティア名は `standard` という対応です。**上の表の `strict` は README を根拠にしていますが、`security-deep-dive.md` は運用者が `agent.sandbox` に書ける値ではないと述べています。** また同ファイルにのみ登場する **`cc`** ティアは上の表に含まれていません。どちらが正しいかは公式に説明がないため、本サイトは裁定せず両方を記載します。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）
>
> 値の一覧は [04_reference/05_limits.md](../04_reference/05_limits.md) の「セキュリティ」節も参照してください。

導入時の設定手順は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

## Owner lock

各メッセージングチャネルは認可されたユーザーにロックされます。

| チャネル | 方式 |
|---------|------|
| Slack | `KIROCREW_OWNER_ID`（単一owner） |
| Discord | ユーザーIDの許可リスト（deny-by-default） |
| Telegram | 数値ユーザーIDの許可リスト |
| Teams | Azure AD email/object IDの許可リスト |
| Webex | emailの許可リスト |
| WeCom | userids の許可リスト（または明示的な `allow_all_users` opt-in） |
| WeChat | ユーザーIDの許可リスト（既定は全員拒否） |
| Dashboard | トークン認証（すべてのリクエストが有効なトークンを要求） |

未認可のメッセージは黙って破棄され、監査ログに記録されます。

## ガバナンス（POLICY ∩ PROFILE）

任意のポリシー・プロファイルファイルが**最も厳しい方が勝つ**モデルで合成されます。実行中のAppやエージェントは許可スコープを狭めることはできますが、上限を緩めることはできません。

- **Policy**（ポリシー） — エンタープライズレベルの上限（`~/.kiro/crew/security_policy.json` から読み込み）
- **Profile**（プロファイル） — サーフェス単位・タスク単位の絞り込み（`~/.kiro/crew/profiles/` から読み込み）
- **Effective**（実効） = Policy ∩ Profile（最も厳しい方が勝つ）

ポリシー・プロファイル・admissionファイルは `security._SENSITIVE_HOME_DIRS` に置かれ、**エージェントは自分自身の上限を読み書きできません**。これが上限を無効化不能にする唯一の仕組みです。

CLIから確認できます: `kirocrew policy show` / `kirocrew policy validate` / `kirocrew policy explain`

## Audit（SEL）

すべてのツール呼び出し・承認・拒否・セキュリティイベントが記録されます。追記専用（append-only）で、HMAC-SHA256によるハッシュチェーンJSONL（`<data home>/security_events.jsonl`）です。

CLIから確認できます: `kirocrew security events` / `kirocrew security audit` / `kirocrew security verify`

監査ログはsnapshotに含まれ、ダッシュボードの Settings → Security から確認できます。

## v0.3.0での変更

### terminalのcredential秘匿化について（一次情報が4件で食い違う・裁定しない）

**v0.3.0のCHANGELOGには、terminal出力のcredential秘匿化について、同一版節内で相反する記述が存在します。** セキュリティ挙動であり片側だけを断定すると導入判断を誤らせるため、**本サイトは裁定せず、確認できた4つの記述をすべて原文の対象表現のまま併記します**。

| # | 出典 | 記述（対象の書き方に注意） |
|---|------|--------------------------|
| ① | CHANGELOG.md **21行**（v0.3.0節「Before you upgrade」） | 「**The terminal no longer scans its output for credentials.**（terminalは出力のcredentialスキャンを行わなくなった）」。理由として**CJKテキストとemojiがPTYストリームで壊れていたこと**、および**意図的に出力した秘密を飲み込んでいたこと**が挙げられている。「**Terminal output is now passed through untouched**（terminal出力は手を加えず素通しになった）」 |
| ② | CHANGELOG.md **221行**（v0.3.0節「Security and governance」） | 「**Credentials are scrubbed on the live stream**（ライブストリームでcredentialがscrubされる）— Redaction now covers **real-time output** as well as replayed history（redactionが再生履歴に加えてリアルタイム出力もカバーするようになった）」 |
| ③ | リポジトリ `README.md` **332〜333行** | 「... strips sensitive environment variables, and **redacts credential patterns from output before it reaches a chat surface**（チャットサーフェスに到達する前に出力からcredentialパターンをredactする）」 |
| ④ | `src/kiro_crew/dashboard/handlers/terminal.py` **932〜938行**（`api_terminal_redact` のdocstring） | `POST /api/terminal/redact` は「**チャットに挿入される前に** terminal選択範囲の**全体**をスキャンする」エンドポイントで、docstringは「**This is the whole credential boundary for the web terminal**（これがWeb terminalのcredential境界のすべて）: **the live PTY stream is forwarded to the browser unscanned**（ライブPTYストリームはスキャンされずにブラウザへ転送される）, and the scrollback ring buffer is replayed only there, so **the selection hand-off is the one path by which terminal output reaches a model**（選択範囲の受け渡しが、terminal出力がモデルに届く唯一の経路である）」と述べる。さらに「It therefore runs **unconditionally**, and callers **MUST fail closed**: no chat insertion unless this returns 200 with redacted text（したがって無条件に実行され、呼び出し元はfail closedでなければならない。redact済みテキストで200が返らない限りチャットへの挿入は行わない）」 |

**4件は「対象」の書き方がそれぞれ異なります**（①は terminal の出力スキャン全般、②は「ライブストリーム」、③は「chat surface に到達する出力」、④は「ブラウザへのPTYストリームは未スキャンだが、モデルに渡る選択範囲は無条件にredactされる」）。どれが正しいか・なぜ併存するのかは公式に説明がないため、**本サイトは推測しません**。

**④の記述は①②③のいずれとも整合する読み方が可能ですが、本サイトはその解釈を採用して他の記述を退けることはしません**（「ブラウザ表示は素通し・モデルへの受け渡しはredact」という切り分けは④のdocstringにのみ書かれており、①②③の文面はその区別をしていないため）。

いずれの記述を前提にしても、**terminalに秘密を表示させる運用は避ける**のが安全側の判断です。導入時の設定は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

出典はすべて`21584ea`（参照: 2026-08-22）。

### Security and governance（7件）

| 変更 | 内容 | CHANGELOG行 |
|------|------|:---:|
| **Appは自身のイベントのみ参照可能** | インストール済みAppは**manifestが宣言したイベントスコープのみ**を受け取り、ユーザーのチャット・スケジュールジョブの結果・他Appの活動を**観測できなくなりました**（[10_apps.md](10_apps.md)の権限モデルも参照） | 212行 |
| **スケジュールジョブが毎実行ごとに再審査される** | 作成時のみでなく**発火ごとに現行ポリシーへ照合**されます。復元したバックアップが承認システムを迂回してshellコマンドを持ち込むことができなくなりました（[06_autonomy.md](06_autonomy.md)参照） | 215行 |
| **メモリ上限が全同時エージェント合計に適用** | 上限が同時実行中の全エージェントにまとめて適用され、小さなspawnを多数行ってホストを食い潰すことができなくなりました | 218行 |
| **ライブストリームでcredentialがscrubされる** | **⚠️ 上記「terminalのcredential秘匿化について」の②。①と矛盾するため裁定しません** | 221行 |
| **ピン留めされたポリシー下限をローカルで引き下げ不可** | governed hostでは**ポリシーがローカル設定に勝ちます**。**`unsandboxed-exec`のopt-inに対しても勝ちます**（`agent.sandbox_allow_unsandboxed_exec`を立てても、ポリシーが禁じていれば通りません） | 223行 |
| **メモリ編集に認識済みセッションが必要** | 偽造キーで保存済みメモリを削除できる経路が封鎖されました（[04_memory-and-learning.md](04_memory-and-learning.md)参照） | 226行 |
| **独自のIDプロバイダを持ち込める** | 管理者が**設定により自身のOAuthプロバイダを認可**でき、リリースを待つ必要がなくなりました | 228行 |

### その他のセキュリティ関連の変更

- **Subagentが主エージェントと同様に承認を求める**（193行）。subagentの承認要求が trust／auto-approve／プロンプトを通るようになり、要求がドロップされて子が固まることがなくなりました（[06_autonomy.md](06_autonomy.md)参照）
- **`kirocrew policy show` が拒否コマンドカタログを列挙する**（176行）。`21584ea`の`modules/cli.md` 135行によると、`show`はカタログを**カテゴリ別のグループ件数として要約**し、`--ids`で各カテゴリのrule idを列挙します。**エンタープライズポリシーが有効かどうかに関わらず全インストールで利用可能**です。上記「Denied commands（137パターン）」の内容をソースを見ずに読めるようになりました（[04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)参照）

出典: CHANGELOG.md v0.3.0節（`21584ea`）／`docs/system-specs/modules/cli.md` 135行。

## 既知のギャップ（公式が明記）

**リポジトリのアーキテクチャ文書（`security-deep-dive.md`「Known gaps」節）が明記している事実**です。伏せると導入判断を誤らせるため必ず記載します。

1. **既定でネットワーク送信（egress）の制御がない**: サンドボックスは認証情報ファイルを隠しますが、外向きのネットワークアクセスは制限しません。侵害されたエージェントは任意のホストへ非認証情報データを送信できます
2. **コマンドマッチングはbash ASTパーサではない**: regex/tokenizerによる正規化（引用符処理・空文字列結合・`$HOME`/チルダ展開等）で既知の回避手法は防ぎますが、実行時に組み立てられたペイロード（文字列結合・base64・間接的な `eval "$CMD"`）はパターンにマッチしません
3. **監査ダッシュボードがない**: SEL イベントはAPI（`/api/sel/events`）経由で照会できますが、閲覧・フィルタ・アラート用のUIがなく、改ざん検知や異常検知は手動です
4. **エージェント内部からのサンドボックス脱出検知がない**: Gatewayはバックエンドの有無をfail-closedで判定しますが、プロセス内部から閉じ込めが実際に機能しているかを検証する仕組みはありません
5. **Base64認証情報検出には下限がある**: 最小長以上のBase64チャンクのみが復号・再チェックされるため、短い断片や複数メッセージに分割された認証情報は検出を逃れる可能性があります
6. **書き込み保護はCrew自身のトラストルートのみで、ユーザーのシェル起動ファイルは対象外**: 認証情報ディレクトリとキーストーンは読み書きブロックされますが、`~/.bashrc`・`~/.zshrc`のような通常の永続化先はブロックされません（ホームディレクトリ全体をブロックするとエージェントが機能しなくなるため）。承認ゲートと破壊的コマンドルールのみが緩和策です

**（gapsの箇条書きの外側にある追加事項）**: リソース上限はプラットフォームに依存します。fork bombやメモリ暴走を抑えるcgroup v2スコープはLinux＋cgroup delegationを要求し、利用できない環境（macOS・古いLinux・ユーザーセッションなし）では警告付きでno-opとなり、ファイルディスクリプタ上限のみが有効です。

## 未確認事項

- なし。既知ギャップは当初4点として計画されていたが、`security-deep-dive.md`の実測で6点（＋別枠のリソース上限依存）であることを確認した

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
- 導入時の設定: [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

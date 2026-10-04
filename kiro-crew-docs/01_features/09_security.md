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
- [ツール承認のレベル](#ツール承認のレベル)
- [Owner lock](#owner-lock)
- [ガバナンス（POLICY ∩ PROFILE）](#ガバナンスpolicy--profile)
- [Audit（SEL）](#auditsel)
- [Run制御の所有権スコープ](#run制御の所有権スコープ)
- [v0.7.0での変更](#v070での変更)
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
4. **Sensitive paths and sandbox masks**（機密パスとサンドボックスマスク） — 直接のファイルツールは保護パスをブロックし、OSサンドボックスは保護された認証情報の場所を**子プロセスから**マスクする
5. **Tool approval**（ツール承認） — 対話的レビュー・信頼の段階的昇格・Autopilot（拒否チェックを通過した後のみ発動）
6. **Input validation**（入力検証） — MCPスキーマ・型チェック・長さ制限・Unicode正規化
7. **OS sandbox**（OSサンドボックス） — LinuxのnamespaceまたはmacOSのSeatbeltによるプロセスレベルのファイルシステム隔離
8. **Output redaction**（出力の秘匿化） — チャットに到達する前に認証情報のパターンを応答から除去

> **4番目の名称の修正**: 本サイトは4番目を v0.3.0 時点の公式表記「Sensitive path blocking — credential directories and files are inaccessible to tool calls」のまま掲載していましたが、公式ページは v0.6.0 時点（Page updated 2026-09-12）で既に上記の表記に変わっていたため、修正しました。現行の公式ページ（Page updated 2026-09-30）も同じ表記です。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）

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

設定は Settings → Security、または `kirocrew config set agent.sandbox <mode>`。Linuxではuser/mount namespaces、macOSではSeatbeltプロファイルを使用します。

サンドボックスを適用できない場合は**fail-closed**です。公式ページは、Linuxでは `armv7l`・`riscv64`・`ppc64le`・`s390x` や `prctl` を持たないlibcが該当し、**Windowsでは Kiro CLI の内部サンドボックスがオフの場合に該当する**と記述しています。これらの場合、`agent.sandbox` を明示的に `off` にするか `agent.sandbox_allow_unsandboxed_exec` を `true` にしない限り、Crew はエージェントを起動しません。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** Windows について、公式ページと `README.md` は上記の fail-closed を記述していますが、v0.7.0 以降の `docs/guides/windows-install.md` 285-290行と `modules/security.md` 309行（`c67c506`）は、委譲できるサンドボックスがない経路（Script cron・hooks・Appバックエンドなど）は**Windowsでは既定で非サンドボックス実行（UNCONFINED）**と記述しています。詳細と両方の原文は [03_deployment/02_windows.md](../03_deployment/02_windows.md#osレベルサンドボックス層の不在) を参照してください。
>
> **Windowsの記述の修正**: 本サイトはこれまで公式の旧記述「Windows does not currently have this OS-level layer — all other protections still apply」を引用していましたが、この文は v0.6.0 時点の公式ページに既に無く、上記の fail-closed の記述に置き換わっていたため、修正しました。リポジトリ `README.md` 399-402行も「Windows offers no equivalent OS-level layer, so Kiro Crew fails closed there」と記述しています。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/README.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

> ⚠️ **呼称と値域の食い違い（出典3系統・裁定しない）**
>
> | 出典 | 記述 |
> |---|---|
> | リポジトリ `README.md` **398行** | 「Seatbelt isolation. **Standard, strict, and off modes** make the tradeoff…」＝**3モード**として提示 |
> | `docs/system-specs/modules/config.md` **1843行** | `agent.sandbox` の既定は **`"auto"`**（Linuxはnamespace、macOSはseatbelt。macOSで有効時はkiro-cli内部のサンドボックスに委譲）、**`"off"`** はKiro Crewのサンドボックスをスキップ。**`strict` の記載はありません** |
> | `docs/architecture/security-deep-dive.md` **107-112行** | `wrap_argv` の内部ティア語彙は設定enumより広く **`standard`（`auto` の解決先）／`cc`／`strict`／`off` の4種**。これらは内部呼び出しとガバナンスの `sandbox.min_level` 順序尺度（`_ORDINAL_SCALES["sandbox"] = ("off", "standard", "cc", "strict")`）から到達し、要求されたモードを**上へ**クランプする。**「They are not values an operator writes into `agent.sandbox`」と明記** |
>
> 設定値は `auto`、内部ティア名は `standard` という対応です。**上の表の `strict` は README を根拠にしていますが、`security-deep-dive.md` は運用者が `agent.sandbox` に書ける値ではないと述べています。** また同ファイルにのみ登場する **`cc`** ティアは上の表に含まれていません。どちらが正しいかは公式に説明がないため、本サイトは裁定せず両方を記載します。
>
> v0.7.2 タグでも3系統の記述内容は変わっておらず、食い違いは解消していません（README・`config.md` は行番号のみ変更。v0.6.0 タグでは README 385行・`config.md` 940行）。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
>
> 値の一覧は [04_reference/05_limits.md](../04_reference/05_limits.md) の「セキュリティ」節も参照してください。

導入時の設定手順は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

## ツール承認のレベル

公式ページの「Tool approval」節は、Settings → Security またはセッションごとの Autopilot トグルで設定する以下のレベルを示しています。

| レベル | 挙動 |
|-------|------|
| **Automatic**（既定） | 拒否・ガバナンス・サンドボックスの各ゲートを通過したツール呼び出しは、個別の承認プロンプトなしで進む |
| Interactive | プロンプトを表示できるサーフェスで、ツール呼び出しごとに承認を求める |
| Trust this command | このツールと引数の完全一致に対する、セッション単位の自動承認 |
| Trust this tool | このツール（引数は任意）に対する、セッション単位の自動承認 |
| Autopilot | このセッションのすべてのツールを自動承認（拒否ルールは引き続き適用） |

拒否コマンドと機密パスのブロックは、Autopilot でも迂回されません。

> **公式ページの既定表記が変わりました**: v0.6.0 時点の公式ページ（Page updated 2026-09-12）は「**Interactive** (default) — Every tool call prompts for approval in the dashboard or messaging channel」と記載していましたが、現行の公式ページ（Page updated 2026-09-30）は上表のとおり **Automatic** を既定としています。
>
> 一方、リポジトリ `docs/system-specs/modules/config.md` の `approval_mode: str = "auto"    # "auto" or "interactive"` は、v0.6.0 タグ（936行）・v0.7.2 タグ（1839行）のいずれにも同じ記述があり、**リポジトリ側の既定は v0.6.0 時点で既に `"auto"` でした**（CHANGELOG v0.1.2節 2106行も「Tool calls are auto-approved by default (`agent.approval_mode: "auto"`)」と記述）。v0.6.0 時点にあった公式ページとリポジトリの食い違いは、現行の公式ページで解消しています。公式ページの表記変更に対応する CHANGELOG の記述は見当たらず、どの版で表記が変わったかは未確認です。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）／CHANGELOG.md v0.1.2節 2106行（`c67c506`）

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
| WhatsApp | リンクしたアカウントが operator。DMのアクセスは `whatsapp.dm_policy` に従い、設定済みグループは operator と `whatsapp.allowed_wa_ids` の番号のみを受け入れる。受け入れたそれ以外の送信者は、Kiro backend では**ツールなしの別セッション**で処理され、他のエージェントバックエンドではそのターンを拒否する |
| iMessage | 明示的なハンドル許可リストによる deny-by-default（**macOSのみ**） |
| Feishu (Lark) | 認可ユーザーの許可リスト |
| Dashboard | トークン認証（すべてのリクエストが有効なトークンを要求） |

未認可のメッセージは黙って破棄され、監査ログに記録されます。

> **表の追記について**: WhatsApp・iMessage・Feishu (Lark) は v0.6.0 時点の公式ページにも記載されていましたが、本サイトの表から漏れていたため追加しました。WhatsApp の記述は、v0.6.0 時点の公式ページでは「linked to a single personal account by QR code」のみで、現行の公式ページ（Page updated 2026-09-30）で上記の内容に更新されています。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）

**ツールなしエージェント**: `docs/system-specs/modules/security.md` は、チャネルが operator として信頼しないメッセージングのターン（`ChannelTurn.deny_all_tools`）を、**`kirocrew-guest`**（`tools: []`・MCPサーバなし・独自のprompt）という `dispatch.TOOLLESS_TURN_AGENT` で、専用のセッションで処理すると記述しています。理由として、operator のエージェントが `allowedTools` で自動承認するツールは kiro backend で承認要求を発生させず、承認時点の拒否が届かないことを挙げています。本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません（v0.6.0・v0.7.0・v0.7.1 タグの `docs/` には `kirocrew-guest` の記述はありません）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（1688-1691行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

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

## Run制御の所有権スコープ

`docs/system-specs/modules/security.md`「Dashboard Authentication & Authorization」は、run単位のspawnルート（`steer`・`release`・`status`・`retry`・`delete`・`continue`）とrun一覧について、`internal_auth` の呼び出し元は**自分が所有するrunのみ**操作できると記述しています。所有とは、runの起点セッション（`parent_session_key == X-Session-Key`）またはrun自身（`subagent:<id>`）であることです。

- `X-Session-Key` を提示しない呼び出し元は、セッションが開始したrunを所有せず、親を持たないrun（ホストの operator 自身のCLI run）にのみ到達します
- 拒否は **404 `task_scope_denied`** で返り、見る権限のない呼び出し元にrun idの存在を確認させません
- フェンスなしで受け入れられるのは**ダッシュボードの owner（cookie認証、`internal_auth` なし）のみ**です

本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません（v0.6.0・v0.7.0・v0.7.1 タグの `docs/` には `task_scope_denied` の記述はありません）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（1672-1686行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## v0.7.0での変更

CHANGELOG v0.7.0節「Security you can operate」（443-454行）と「Privacy and safety」（667-672行）のうち、本ページの範囲に関わるものです。

### フラグ付きファイル配信の承認

`file_send` が認証情報のような内容を検出すると、配信を拒否してレビュー経路を示します。ダッシュボードの owner が **Settings → Security** で一回限りの承認をアームし、宛先とファイルを確認したうえで、**Gatewayホスト上で直接**次を実行します。

```bash
kirocrew file-delivery approve
```

- エージェントはこのホスト側の手順を自分で完了できません。**Computer Use が有効な間はこのコマンドが拒否され**、エージェントがキーボード自動化で operator の承認を偽装することを防ぎます（公式ページ）
- 承認はアームされた要求に限定され、今後のファイルに対する一般的な迂回にはなりません（公式ページ）
- `docs/feature-map/README.md` は、`self-protection-file-delivery` という拒否コマンドの floor ルールがエージェントによる `kirocrew file-delivery approve` の実行自体をブロックすると記述しています
- 同じ CHANGELOG 項目は、Denied Commands カードがその層の見えない範囲（見るのはコマンドラインであり、スクリプトの本文は見ない）を明示するようになったことも挙げています

> **注記**: `kirocrew file-delivery approve` は、リポジトリでは CHANGELOG v0.7.0節（445-448行）と `docs/feature-map/README.md` にのみ登場し、CLI仕様書 `docs/system-specs/modules/cli.md` には記載がありません。

出典: CHANGELOG.md v0.7.0節 445-448行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>（298-318行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

### SSH agent forwarding（同意制・既定オフ）

git over SSH と SSHによるコミット署名は、明示的な keystone の同意の後でのみ、エージェントのサンドボックス内で operator の `SSH_AUTH_SOCK` を使えます。**既定はオフ**です。

サンドボックスの外（自分の端末）から `~/.kiro/crew/ssh_auth_sock_consent.json` を作成します。

```json
{"enabled": true}
```

- ソケットはSSH agentが保持する鍵の**使用**を許可するもので、秘密鍵の素材はサンドボックスへコピーされません
- ただしエージェントが実行するコードは、そのソケットが公開する任意のIDを使えます（公式はこれを既定オフの理由として挙げています）
- この認可のためのエージェント向け設定やCLIトグルはありません。`modules/security.md` は `agent.*` 設定フィールドを意図的に設けていない（エージェントが書き込めるため）と記述し、同意ファイルはエージェントのファイルツールが拒否し、OSサンドボックスが読み取り専用でマウントする keystone リーフに置かれます
- 他の機密環境変数は引き続き除去され、strict モードでは鍵ファイル自体も隠されたままです

出典: CHANGELOG.md v0.7.0節 449-451行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（282行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

### ポリシーの fail closed

- 2つのポリシー層から合成された上限は、そのルールが読み込まれるようになりました
- ポリシーを読み込めない場合、operator が拒否したツールは拒否されます
- API経由での skill の作成・編集には owner が必要になりました

出典: CHANGELOG.md v0.7.0節 452-454行（`c67c506`）

### リスクの高いツール呼び出しのフラグ付け（Preview・既定オフ）

**Decisions (Jev) は Preview 機能**です（Settings → Developer → Feature Previews。詳細は [03_chat.md](03_chat.md) を参照）。リスクの高いツール呼び出しのフラグ付けは、Decisions 配下の**独自の同意スイッチ**を持ち、**以前から同意していた人に対してもオフ**です。CHANGELOG はその理由を、ツールの引数を送信するためと述べています。

- `docs/feature-map/README.md` は、このフラグ（Tool risk badge）を**注釈にすぎず、許可の判断には使われない**と記述しています
- ガバナンスプロファイルは `capabilities.decisions` でこのプレビュー全体をオフにできます

出典: CHANGELOG.md v0.7.0節 292-305行・670-672行（`c67c506`）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>（92行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

### 既知のギャップが7点に

`security-deep-dive.md`「Known gaps」節に、7点目として「同一ユーザーによるランチャの自己汚染」が追加されました（下記「[既知のギャップ（公式が明記）](#既知のギャップ公式が明記)」の7）。v0.7.0 タグの同ファイル629行に存在し、v0.6.0 タグの同節にはありません。CHANGELOG には対応する記述は見当たりません。

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
6. **書き込み保護はCrew自身のトラストルートのみで、ユーザーのシェル起動ファイルは対象外**: 認証情報ディレクトリとキーストーンは読み書きブロックされますが、`~/.bashrc`・`~/.zshrc`のような永続化先（原文「ordinary persistence targets」）はブロックされません（ホームディレクトリ全体をブロックするとエージェントが機能しなくなるため）。承認ゲートと破壊的コマンドルールのみが緩和策です
7. **同一ユーザーによるランチャの自己汚染は受容されており、防御されない**（CWE-345。v0.7.0 で追加）: 解決された `kiro-cli` ランチャは署名・ハッシュ・所有者・インストール元の検査なしにそのまま実行され、唯一のゲートは `platform_compat.is_executable_file` です。呼び出しユーザーとして動くエージェントが自身のランチャを上書きすると、次回のspawnでそのバイト列が実行されます。**Status: ACCEPTED**。塞ぐ仕組みは見落としではなく**設計上退けられています**: owner／パス／Developer-IDによるゲートは、実際のインストール（toolbox・Homebrew・winget・自己更新された `/Applications` バンドル）を製品内の回復手段なしに立ち往生させるためです。攻撃は operator としてのローカル書き込み権限を前提とし、本製品の脅威モデルの外にあります（上記6の `~/.bashrc` と同じ分類）。残存影響は閉じ込めたspawn経路（Linux namespace・macOS seatbelt）では限定され、汚染されたランチャもKiro Crew自身のサンドボックス内で動きます。直接execするのはmacOSの内部サンドボックスへの委譲時のみです。マルチテナント／エンタープライズ運用には署名基盤・鍵管理・インストール配置の決定が必要で、そのようなゲートは**既定オフ**でなければならないと記述されています

**出典**（7の根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（629-659行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

**（gapsの箇条書きの外側にある追加事項）**: リソース上限はプラットフォームに依存します。fork bombやメモリ暴走を抑えるcgroup v2スコープはLinux＋cgroup delegationを要求し、利用できない環境（macOS・古いLinux・ユーザーセッションなし）では警告付きでno-opとなり、ファイルディスクリプタ上限のみが有効です。

## 未確認事項

- なし。既知ギャップは当初4点として計画されていたが、`security-deep-dive.md`の実測で6点（＋別枠のリソース上限依存）であることを確認した。v0.7.2 タグ（`c67c506`）の実測では、v0.7.0 で追加されたランチャの自己汚染を含めて**7点（＋別枠のリソース上限依存）**である

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
- 導入時の設定: [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

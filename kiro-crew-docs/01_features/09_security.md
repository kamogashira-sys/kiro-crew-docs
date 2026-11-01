# セキュリティ

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [脅威モデル](#脅威モデル)
- [8つの保護機構（公式の順序）](#8つの保護機構公式の順序)
- [層数についての注記](#層数についての注記)
- [サンドボックスの3モード](#サンドボックスの3モード)
- [ツール承認のレベル](#ツール承認のレベル)
- [Owner lock](#owner-lock)
- [ガバナンス（POLICY ∩ PROFILE）](#ガバナンスpolicy--profile)
- [Audit（SEL）](#auditsel)
- [Run制御の所有権スコープ](#run制御の所有権スコープ)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [v0.3.0での変更](#v030での変更)
- [既知のギャップ（リポジトリのアーキテクチャ文書が明記）](#既知のギャップリポジトリのアーキテクチャ文書が明記)
- [未確認事項](#未確認事項)

---

## 脅威モデル

Crew はAIエージェントに実際のツールアクセス（ファイル読み込み・シェルコマンド・ウェブブラウジング）を与えます。セキュリティモデルは**多層防御**（defense-in-depth）で、各層はプロンプトの指示だけに頼らず、**ランタイムの境界で強制されます**。モデルは信頼できる呼び出し元ではなく、信頼できない入力として扱われます。

## 8つの保護機構（公式の順序）

公式ページは、すべてのツール呼び出しが以下の順序でチェックされると明記しています。

1. **Owner lock** — チャネルGatewayが、メッセージがセッションに到達する前に未認可ユーザーを拒否
2. **Denied commands**（拒否コマンド） — 組み込みのパターンと設定したパターンが破壊的操作をブロック（承認を求める前にチェック）
3. **Governance ceiling**（ガバナンス上限） — Policy ∩ Profile（最も厳しい方が勝つ）。エージェントやAppは緩められない
4. **Sensitive paths and sandbox masks**（機密パスとサンドボックスマスク） — 直接のファイルツールは保護パスをブロックし、OSサンドボックスは保護された認証情報の場所を**子プロセスから**マスクする
5. **Tool approval**（ツール承認） — 対話的レビュー・信頼の段階的昇格・Autopilot（拒否チェックを通過した後のみ発動）
6. **Input validation**（入力検証） — MCPスキーマ・型チェック・長さ制限・Unicode正規化
7. **OS sandbox**（OSサンドボックス） — LinuxのnamespaceまたはmacOSのSeatbeltによるプロセスレベルのファイルシステム隔離
8. **Output redaction**（出力の秘匿化） — チャットに到達する前に認証情報のパターンを応答から除去

> **拒否コマンドの件数について（v0.11.1 でも確認できない）**: 本サイトはこれまで、2番目の項目を「137パターン」と掲載していました。この数値は、v0.3.0・v0.4.1 時点の公式 security ページ（Page updated 表記あり）と、v0.7.2 時点の公式 hooks ページ（<https://kiro.dev/docs/crew/capabilities/hooks/> ）に記載されていたものです。現行の公式 security ページ（Page updated 2026-10-12）と公式 hooks ページ（Page updated 2026-10-12）には件数の記載がなく、公式 security ページは v0.6.0 時点のスナップショット以降、件数を記載していませんでした（**v0.7.2 以前の本ページは、件数の記載がない版の公式ページの項目に「137パターン」を載せていました**）。リポジトリのアーキテクチャ文書は件数を文書に書かない方針を明記しており（`security-deep-dive.md` 17-20行）、`security.md` も現在値を文書に書かないとしています（3670-3695行）。この方針は v0.11.1 でも維持されています。件数は実行時に `GET /api/security/posture` から導かれます。このため、**拒否ルールの現行件数は未確認です**（v0.11.1 では拒否ルール 1 件が削除されています。[v0.11.1での変更](#v0111での変更)を参照）。
>
> また、`security.md` は認証情報ファイルのパスを読む行を拒否カタログから意図的に除外しており（1637行）、拒否カタログのカテゴリに `sensitive-file-read` はありません（1772-1777行）。カタログのカテゴリは `aws-destructive`・`credential-exfil`・`iac-teardown`・`local-destructive`・`pipe-to-shell`・`sql`・`self-protection`・`git-publish`・`reverse-shell` です。拒否コマンドの設定は「[Denied commands の管理](#denied-commands-の管理)」を参照してください。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（17-20行）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／旧記載の出典: CHANGELOG.md v0.1.2節 2810行（v0.9.0 タグのファイルの行。`99e6253`）

> **4番目の名称の修正**: 本サイトは4番目を v0.3.0 時点の公式表記「Sensitive path blocking — credential directories and files are inaccessible to tool calls」のまま掲載していましたが、公式ページは v0.6.0 時点（Page updated 2026-09-12）で既に上記の表記に変わっていたため、修正しました。現行の公式ページ（Page updated 2026-10-12）も同じ表記です。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）

> **⚠️ v0.3.0に関する注意**: 上記8番目は公式ページが示す**エージェント応答全般**の秘匿化です。これとは別に、**terminal出力の秘匿化についてはv0.3.0のCHANGELOG内で相反する記述があります**。詳細は下記「[v0.3.0での変更](#v030での変更)」を参照してください。

**Audit（SEL）はすべての段階の決定を記録します**（横断的な仕組みであり、順序上の1ゲートではありません）。

## 層数についての注記

> **重要**: リポジトリのアーキテクチャ文書は番号付きの層（Layer 0〜5）として整理したうえで、全層にまたがるものとして4項目を挙げています。request auth（dashboard tokens・CSRF・Host allowlist）、Slack owner lock と workspace origin check、governance ceiling（Policy ∩ Profile）、SEL audit です。一方で**公式ドキュメントは層数を数値で示していません**（"defense-in-depth: multiple independent layers" という表現のみ）。したがって本ページでは**公式の8機構リスト**（上記）を正としつつ、「公式が何層と述べている」という表現は使いません。
>
> **全層を貫く制御の数の修正**: 本サイトは v0.7.2 以前、「全層を貫く2つの制御」と記載していました。この数に対応する記述は、v0.7.2 タグ・v0.9.0 タグ・v0.11.1 タグのいずれの `security-deep-dive.md` にもありません（同ファイルの図は、いずれの版でも上記の4項目を挙げています）。v0.3.0 時点の記述は未確認です。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（66-79行。v0.11.1 でも同じ行に同じ 4 項目）
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／同ファイル 66-79行（`99e6253`、v0.9.0）／同ファイル 66-79行（`c67c506`、v0.7.2）

## サンドボックスの3モード

| モード | 設定値 | 隠されるもの | アクセスできるもの | 想定用途 |
|-------|-------|------------|-----------------|---------|
| **標準（既定）** | **`auto`** | `.gnupg` / `.gcloud` / `.azure` / `.docker` | `.aws` / `.ssh` / `.kube` | ほとんどの利用者（git-over-SSHとAWS CLIが使える） |
| 厳格 | `strict`（v0.8.0 で追加） | 上記すべて＋`.aws` / `.ssh` / `.kube` | `~/.ssh/known_hosts` のみ | ロックダウン運用 |
| 無効 | `off` | 何も隠さない | すべて | トレードオフを理解している場合 |

設定は Settings → Security、または `kirocrew config set agent.sandbox <mode>`。Linuxではuser/mount namespaces、macOSではSeatbeltプロファイルを使用します。

**標準（`auto`）で `~/.aws`・`~/.ssh`・`~/.kube` が見える点（公式の警告）**: 公式ページは、コマンドゲートがシェルテキスト中の綴りの一致では認証情報パスを保護しないこと、サンドボックスのバインドマスクがサブプロセスの境界であることを警告しています。リポジトリのアーキテクチャ文書は、`auto` では `cat ~/.aws/credentials` のようなシェル読み取りが成功し、読み取り専用コマンドは自動承認されると記述しています（v0.10.0 以降、git は読み取り専用のシェルコマンドとして自動承認されません。[v0.11.1での変更](#v0111での変更)を参照）。これらのディレクトリを隠すには `agent.sandbox` を `strict` にしますが、`aws` CLI の `credential_process`・git-over-SSH・`kubectl` はエージェント内で使えなくなります。`strict` は、Kiro Crew がラップしないspawn（Windows、およびkiro-cliの内蔵サンドボックスへ委譲されるmacOSのspawn）は絞り込みません。

この点は v0.6.0 の CHANGELOG（「The command gate no longer fences credential paths by reading the command text」）で、コマンドゲートが認証情報パスをコマンド文の読み取りで防ぐ方式をやめ、サンドボックスのバインドマスクを境界にしたと記述されています。

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（178-218行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.6.0節 1405-1408行（v0.9.0 タグのファイルの行。`99e6253`）

サンドボックスを適用できない場合は**fail-closed**です。公式ページは、Linuxでは `armv7l`・`riscv64`・`ppc64le`・`s390x` や `prctl` を持たないlibcが該当し、**Windowsでは Kiro CLI の内部サンドボックスがオフの場合に該当する**と記述しています。これらの場合、`agent.sandbox` を明示的に `off` にするか `agent.sandbox_allow_unsandboxed_exec` を `true` にしない限り、Crew はエージェントを起動しません。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。** Windows について、公式 security ページ（Page updated 2026-10-12）の上記の記述と、公式 configuration ページ（Page updated 2026-10-20）の `agent.sandbox_allow_unsandboxed_exec`（既定 `false`、明示的に有効にした場合だけ非サンドボックス実行を許可）、およびリポジトリの CHANGELOG v0.6.0節（1562-1565行）は、サンドボックスを適用できないときの fail-closed を記述しています。一方、リポジトリの `docs/guides/windows-install.md`（316-325行）と `modules/security.md`（955行・961行）は、委譲できるサンドボックスがない経路（Script cron・hooks・サードパーティのACPバックエンド・Appバックエンド・MCPプローブ・`gh`/`glab`）は**Windowsでは既定で非サンドボックス実行（UNCONFINED）**になり、`agent.sandbox_allow_unsandboxed_exec` が未宣言のときの既定はWindowsで許可、それ以外のプラットフォームで fail-closed だと記述しています。拒否するには、`windows-install.md`（327-333行）が `agent.sandbox_allow_unsandboxed_exec: false` を `config.json` に宣言する方法を示しています。
>
> 公式 security ページは Windows の fail-closed を「Kiro CLI の内部サンドボックスがオフの場合」と記述し、`windows-install.md`（303-306行）は、公式の Kiro CLI のWindowsでのspawnは Kiro CLI の内蔵サンドボックスへ委譲されると記述しています。`security.md`（968-971行）は、非サンドボックス実行がすべて SEL に `unconfined` として記録され、`kirocrew doctor` が実効状態（拒否／宣言による unconfined／プラットフォームの既定による unconfined）を表示すると記述しています。Windowsの既定を許可にした変更を説明する CHANGELOG の記述は、v0.10.0〜v0.11.1 の節を含めて見当たらず、変更した版は未確認です。詳細と両方の原文は [03_deployment/02_windows.md](../03_deployment/02_windows.md#osレベルサンドボックス層の不在) を参照してください。
>
> **v0.11.0 以降の新規インストールの既定ハーネス KAS（Windows）**: `windows-install.md`（307-314行・373行）は、既定のチャットハーネス KAS が Windows で**非サンドボックス（UNCONFINED）**で動くと記述しています。KAS には Windows 上の OS サンドボックスがなく、Kiro CLI のスポーンでもないため、他のハーネスと同じ「後ろ盾なし」経路に入るためです。ホームディレクトリ（`.aws`・`.ssh` を含む）を読めます。Kiro CLI のサンドボックス内にとどめるには Settings → Agent Harness で **Kiro CLI** を選びます（`"acp_backend": "kiro"`）。`agent.sandbox_allow_unsandboxed_exec: false` を宣言すると、KAS のチャットは拒否されます。`security.md`（987行）は、KAS の relay route（`kiro-cli acp --agent-engine v3`）が Windows では非サンドボックスと実測されたこと、macOS でスイッチがオンなら kiro-cli の内蔵サンドボックスへ委譲されること、KAS の bundle route は Crew の seatbelt を使うことを記述しています。既定ハーネスが KAS になった経緯は [v0.11.1での変更](#v0111での変更)の「既定ハーネス」を参照してください。公式 security ページの Windows の記述（Kiro CLI の内部サンドボックスがオフの場合に該当）は、この KAS の記述と食い違ったままです。本サイトは裁定しません。
>
> **Windowsの記述の修正**: 本サイトは v0.7.2 以前、リポジトリ `README.md` 399-402行の「Windows offers no equivalent OS-level layer, so Kiro Crew fails closed there」を fail-closed 側の当事者として引用していました（v0.7.2 の `README.md`）。この文は v0.9.0 タグの `README.md` に存在しないため、食い違いの当事者から `README.md` を外しました。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.6.0節 1562-1565行（`99e6253`）

### サンドボックスの値域（解消済み）と `strict` の隠蔽対象（食い違い）

**値域の食い違いは v0.9.0 で解消しました（v0.11.1 でも同じ値域です）。** v0.7.2 以前は、`README.md`（`Standard, strict, and off modes`）・`config.md`（`strict` の記載なし）・`security-deep-dive.md`（運用者が書ける値ではないと記述）の3系統が食い違っていました。v0.9.0 では、運用者が `agent.sandbox` に書ける値は `auto`（既定）／`strict`／`off` で、リポジトリの `config.md`（2969行）、`security-deep-dive.md`（96-100行）、公式 configuration ページ（Page updated 2026-10-20）、公式 security ページがこの値域で一致しています。`strict` を運用者の設定値にした版は v0.8.0 です（CHANGELOG v0.8.0節「The sandbox, on your terms」、418-422行）。v0.8.0 タグの `config.md` は enum に `"strict"` を加えており、v0.7.2 の `config.md` は `auto`／`off` のみでした。v0.9.0 の `README.md` には、サンドボックスの3モードを述べた記述自体がありません。

`standard`（`auto` の解決先）と `cc`（Claude Code backend が使う）は内部ティアで、運用者が `agent.sandbox` に書く値ではありません（`security-deep-dive.md` 107-112行、`security.md` 920・926行）。内部ティアを含むガバナンスの `sandbox.min_level` の順序尺度は `("off", "standard", "cc", "strict")` で、要求されたモードを上へクランプします。`security.md` の詳細表（917-922行）は Standard／cc／Strict／Off の4行です。`strict` の変更は、変更後に開始したセッションに適用されます。設定は `config.json`・`kirocrew config set`・Developer ページの Config タブのいずれかで行います。

> ⚠️ **`strict` が隠す対象は、出典によって記述が異なります。本サイトは裁定しません。**
>
> | 出典 | `strict` の記述 |
> |---|---|
> | 公式 security ページ（Page updated 2026-10-12） | `auto` の隠蔽対象にすべて加えて `.aws`・`.ssh`・`.kube`。アクセスできるのは `~/.ssh/known_hosts` のみ |
> | `docs/system-specs/modules/security.md` 921行 | Standard の隠蔽対象にすべて加えて `.aws`・`.ssh`・`.kube`・`.config/gh`・`.midway`。アクセスできるのは `~/.ssh/known_hosts` のみ |
> | `docs/system-specs/modules/config.md` 2969行 | `~/.aws`（`sso/cache` を含む）・`~/.ssh`（`known_hosts` を除く）・`~/.kube`・`~/.config/gh`・`_CC_FILES` の認証情報ファイルも隠す |
> | `docs/guides/install.md` 980-990行 | `~/.aws`（`sso/cache` を含む）・`~/.ssh`（`known_hosts` を除く）・`~/.kube`・`~/.config/gh`、および `~/.npmrc`・`~/.pypirc`・`~/.netrc`・`~/.git-credentials` |
> | CHANGELOG.md v0.8.0節 420-422行 | クラウド・ssh・kube・gh の認証情報ディレクトリを隠す |
>
> `.midway` を含むのは `security.md` だけです。`~/.npmrc` などの認証情報ファイルを含むのは `config.md`（`_CC_FILES`）と `install.md` です。`~/.config/gh` を含まないのは公式 security ページだけです。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.8.0節 420-422行（`99e6253`）

値の一覧は [04_reference/05_limits.md](../04_reference/05_limits.md) の「セキュリティ」節も参照してください。導入時の設定手順は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

## ツール承認のレベル

公式ページの「Tool approval」節は、Settings → Security またはセッションごとの Autopilot トグルで設定する以下のレベルを示しています。

| レベル | 挙動 |
|-------|------|
| **Automatic**（既定） | 拒否・ガバナンス・サンドボックスの各ゲートを通過したツール呼び出しは、個別の承認プロンプトなしで進む |
| Interactive | プロンプトを表示できるサーフェスで、ツール呼び出しごとに承認を求める |
| Trust this command | このツールと引数の完全一致に対する、セッション単位の自動承認（v0.10.0 以降は 1 時間／その日の残りの期限付きも選べる） |
| Trust this tool | このツール（引数は任意）に対する、セッション単位の自動承認（同上） |
| Autopilot | このセッションのすべてのツールを自動承認（拒否ルールは引き続き適用） |

拒否コマンドと機密パスのブロックは、Autopilot でも迂回されません。ただし、オーナーが `mcp.json` またはエージェントファイルに書いた `autoApprove` 一覧のツールは、`mcp.honour_auto_approve`（既定 `true`）の下でこれらのゲートを迂回します（[v0.8.0での変更](#v080での変更)を参照）。

公式ページは、承認の追加動作として次も記述しています（v0.7.2 時点から公式ページに存在し、本サイトが未掲載だったものです）。

- 複数のツール呼び出しが同時に承認待ちのとき、1回の操作で全件を承認または拒否できます。確認画面は対象のコマンドをすべて列挙します。1件だけを拒否して残りのレビューを続けることもでき、拒否はその1件にだけ適用されます
- 再起動で時間制限付きの自動承認が失効した場合は、その旨が報告されます。承認期限切れ・ターン予算の枯渇・Slack 配信失敗のように人ではなくホストが拒否した場合は、原因が名前で示されます
- **Claude Code harness**: Claude 自身の設定で事前承認済みのツールは Crew の承認フローを迂回し、Crew の拒否ルールと監査ログはその呼び出しを観測しません。**Codex** は `agent.sandbox` が `off` のとき起動を拒否します（Crew が OS レベルのサンドボックス境界であるため）
- `kirocrew chat` は承認プロンプトをインラインで表示します

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）

期限付きの信頼は公式 security ページの承認レベル表（Page updated 2026-10-12）に記載がなく、CHANGELOG と仕様書に基づく記述です。詳細は [v0.11.1での変更](#v0111での変更)の「ツール承認」を参照してください。

> **公式ページの既定表記が変わりました**: v0.6.0 時点の公式ページ（Page updated 2026-09-12）は「**Interactive** (default) — Every tool call prompts for approval in the dashboard or messaging channel」と記載していましたが、現行の公式ページ（Page updated 2026-10-12）は上表のとおり **Automatic** を既定としています。
>
> 一方、リポジトリ `docs/system-specs/modules/config.md` の `approval_mode: str = "auto"    # "auto" or "interactive"` は、v0.6.0 タグ（936行）・v0.7.2 タグ（1839行）・v0.9.0 タグ（2644行）のいずれにも同じ記述があり、**リポジトリ側の既定は v0.6.0 時点で既に `"auto"` でした**（v0.11.1 の `config.md` 2963行も `"auto"` です）（CHANGELOG v0.1.2節 2106行も「Tool calls are auto-approved by default (`agent.approval_mode: "auto"`)」と記述）。v0.6.0 時点にあった公式ページとリポジトリの食い違いは、現行の公式ページで解消しています。公式ページの表記変更に対応する CHANGELOG の記述は見当たらず、どの版で表記が変わったかは未確認です（v0.7.0〜v0.11.1 の CHANGELOG 節でも対応する記述は確認できません）。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.1.2節 2106行（v0.7.2 タグのファイルの行。`c67c506`）

### Denied commands の管理

公式ページは、拒否コマンドの例として `rm -rf /`、保護ブランチへの `git push`、IMDS（`curl 169.254.169.254`）、`aws ec2 terminate-instances`・`cdk destroy`・`DROP TABLE`、認証情報の値を表示するコマンドなどを挙げています。ルールは Settings → Security → Denied Commands で、ID 単位の無効化・pinned 以外すべての無効化・独自パターンの追加ができ、edition が提供するルールにはタグが付きます。ガバナンスの pin は優先されます（`security.md` 1612-1647行・1768-1796行）。拒否コマンドは Crew 自身のツールゲートで強制され、kiro-cli のエージェント設定を編集しても弱められません（公式ページ）。

- マッチャーは、引用符・エスケープ・コマンド置換・ワイルドカード綴りのプログラム名を通しても拒否ルールを適用します。一方で、worktree 内の再帰 `grep`、`cd` の後のパイプ、バッククォートを含む heredoc はブロックされず実行できます（公式ページ。CHANGELOG v0.6.0節 1557-1561行〈v0.9.0 タグのファイルの行。`99e6253`〉も同じ内容を記述）
- force push は保護対象または曖昧なブランチ宛のものが拒否され、feature ブランチへの force push は force フラグだけでは保護対象になりません（`security.md` 1645行・1740行）
- v0.8.0 から、`chmod`・`chown`・`netcat` のように危険な動詞を単にデータとして言及するだけのコマンドは拒否されません（CHANGELOG v0.8.0節 824-826行・1017-1019行、`security.md` 2437行〜「Inert mentions of a permission verb」）

> ⚠️ **公式 security ページの記述が内部で食い違っています。本サイトは裁定しません。** 公式ページの「Denied commands」の例には `cat ~/.aws/credentials`・`cat ~/.ssh/id_rsa` が挙がっています（80行）が、同じページのサンドボックスの警告（40行）と、リポジトリの仕様書（`security.md` 1231行・1637行、`security-deep-dive.md` 195-199行）は、コマンドゲートがシェルテキスト中の認証情報パスの綴りを一致の対象にしないと記述しています。この食い違いは v0.7.2 以前から存在します。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

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
| Feishu (Lark) | 認可ユーザーの許可リスト。グループメッセージは、bot にメンションしたものだけが処理される（v0.10.0 以降。[v0.11.1での変更](#v0111での変更)を参照） |
| Dashboard | トークン認証（すべてのリクエストが有効なトークンを要求） |

未認可のメッセージは黙って破棄され、監査ログに記録されます。

> **表の追記について**: WhatsApp・iMessage・Feishu (Lark) は v0.6.0 時点の公式ページにも記載されていましたが、本サイトの表から漏れていたため追加しました。WhatsApp の記述は、v0.6.0 時点の公式ページでは「linked to a single personal account by QR code」のみで、現行の公式ページ（Page updated 2026-10-12）で上記の内容に更新されています。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）

**WhatsApp グループの検査**（`messaging.md` 6254-6264行・6458-6466行）: 設定済みグループでは operator が無条件に通り、他の送信者は `whatsapp.allowed_wa_ids` に載っている場合だけ通ります。**空のリストは operator 以外を誰も通しません**。@メンション・エージェントへの返信・rules モードの自発発言のいずれでも同じ検査が行われ、破棄は無言で SEL に `denied` として記録されます。未設定のグループは、この検査の前に破棄されます。Kiro backend 以外のバックエンドでは非 operator のターンが拒否され、Gateway は起動時に警告を1回出します。CHANGELOG v0.8.0節（1012-1015行）も同じ内容を記述しています。

**Dashboard のトークン**: トークン付き URL は CLI（`kirocrew token`）のほか、Slack（`!dashboard` または `/kirocrew dashboard`）・Telegram と Webex（`/kirocrew dashboard`）・Teams（`/dashboard`）のダイレクトメッセージコマンドで発行されます（`dashboard-token-auth.md` 5行）。リンクはダイレクトの会話にのみ送られ、トークンのリンクは5分の有効期間、セッションTTLは最大20時間で、ループバックも免除されません（`security.md` 2887-2894行）。

**ツールなしエージェント**: `docs/system-specs/modules/security.md` は、チャネルが operator として信頼しないメッセージングのターン（`ChannelTurn.deny_all_tools`）を、**`kirocrew-guest`**（`tools: []`・MCPサーバなし・独自のprompt）という `dispatch.TOOLLESS_TURN_AGENT` で、専用のセッションで処理すると記述しています。理由として、operator のエージェントが `allowedTools` で自動承認するツールは kiro backend で承認要求を発生させず、承認時点の拒否が届かないことを挙げています。本内容は v0.7.2 タグの仕様書で確認したもので、v0.7.2 の CHANGELOG/Release 本文（「A small fix.」）は説明していませんでした（v0.6.0・v0.7.0・v0.7.1 タグの `docs/` には `kirocrew-guest` の記述はありません）。v0.8.0 の CHANGELOG は WhatsApp グループについて、設定したグループでは operator と許可リストの番号だけが応答を引き出せ、受け入れた人はツールなしのエージェントと話す、と記述しています（v0.9.0 タグのファイルの 611-614行、v0.11.1 のファイルの 1012-1015行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（2874-2879行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.8.0節 611-614行（v0.9.0 タグのファイルの行。`99e6253`）

## ガバナンス（POLICY ∩ PROFILE）

任意のポリシー・プロファイルファイルが**最も厳しい方が勝つ**モデルで合成されます。実行中のAppやエージェントは許可スコープを狭めることはできますが、上限を緩めることはできません。

- **Policy**（ポリシー） — エンタープライズレベルの上限（`~/.kiro/crew/security_policy.json` から読み込み）
- **Profile**（プロファイル） — サーフェス単位・タスク単位の絞り込み（`~/.kiro/crew/profiles/` から読み込み）
- **Effective**（実効） = Policy ∩ Profile（最も厳しい方が勝つ）

ポリシー・プロファイル・admissionファイルは `security._SENSITIVE_HOME_DIRS` に置かれ、**エージェントは自分自身の上限を読み書きできません**。これが上限を無効化不能にする唯一の仕組みです。リポジトリのアーキテクチャ文書（253-263行）は、この読み書きブロックの対象として、`security_policy.json`・`profiles/`・`admission_policy.json`・`denied_commands.json`・SEL の HMAC キーとログ・ダッシュボードのトークン署名キー・App Kit レジストリの trust grants（`registry_trust.json`）・チャネル認証情報の `.env` を挙げています。公式ページは、どのサンドボックスモードでも、security policy・admission policy・profiles・denied-command リストが読み取り専用でマウントされ、サンドボックス内のスクリプト・Hook・コマンド cron が書き換えられないと記述しています。

CLIから確認できます: `kirocrew policy show` / `kirocrew policy validate` / `kirocrew policy explain`

公式ページは、v0.7.2 時点から次の運用機能も記述しています（本サイトが未掲載だったものです）。

- **Remote fleet policy**: 管理者は1つの `security_policy.json` を URL で公開でき、各ホストが取得・キャッシュ・定期更新します。ポリシーの変更は再起動もホスト訪問もなしに全体へ反映されます。取得元に到達できない場合は、ホストはキャッシュしたコピーを使い続けます。検証に失敗した文書は拒否され、実行中の上限は下がりません。管理者がポリシーの URL を公開した場合にだけ関係します
- **security policy の検証**: `sandbox` キーの綴り誤りは検証エラーになり、ポリシーが読み込まれません。不正な `publish` 節は公開を拒否します。ポリシーファイルの編集後は `kirocrew policy validate` で確認します
- **Enterprise MCP governance**: エンタープライズの Kiro アカウントで管理者が MCP レジストリを設定した場合に、バージョンのピンを含む組織レベルの MCP 制御が有効になります。個人アカウントには影響しません
- **Bring your own identity provider**: 管理者は、リリースを待たずに設定で自身の OAuth プロバイダを認可できます

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。253-263行）

## Audit（SEL）

すべてのツール呼び出し・承認・拒否・セキュリティイベントが記録されます。追記専用（append-only）で、HMAC-SHA256によるハッシュチェーンJSONL（`<data home>/security_events.jsonl`）です。

CLIから確認できます: `kirocrew security events` / `kirocrew security audit` / `kirocrew security verify`

監査ログはsnapshotに含まれ、ダッシュボードの Settings → Security から確認できます。監査の署名キー（`sel_hmac.key`）はsnapshotに含まれません（公式ページ）。

`GET /api/sel/events?limit=N`（最大1000件）は**ダッシュボードの owner だけ**が参照できます。ダッシュボードのセッションを持つだけの呼び出し元には `403 owner_only` が返り、その拒否も監査されます。`GET /api/sel/verify` はハッシュチェーンの整合性（件数と理由のみ）を返し、owner 限定ではありません（`sel.md` 201-202行、`security-deep-dive.md` 443-447行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/sel.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## Run制御の所有権スコープ

`docs/system-specs/modules/security.md`「Dashboard Authentication & Authorization」は、run単位のspawnルート（`steer`・`release`・`status`・`retry`・`delete`・`continue`）とrun一覧について、`internal_auth` の呼び出し元は**自分が所有するrunのみ**操作できると記述しています。所有とは、runの起点セッション（`parent_session_key == X-Session-Key`）またはrun自身（`subagent:<id>`）であることです。

- `X-Session-Key` を提示しない呼び出し元は、セッションが開始したrunを所有せず、親を持たないrun（ホストの operator 自身のCLI run）にのみ到達します
- 拒否は **404 `task_scope_denied`** で返り、見る権限のない呼び出し元にrun idの存在を確認させません
- フェンスなしで受け入れられるのは**ダッシュボードの owner（cookie認証、`internal_auth` なし）のみ**です

本内容は v0.7.2 タグの仕様書で確認したもので、v0.7.2 の CHANGELOG/Release 本文（「A small fix.」）は説明していませんでした（v0.6.0・v0.7.0・v0.7.1 タグの `docs/` には `task_scope_denied` の記述はありません）。v0.9.0 タグ・v0.11.1 タグの仕様書でも内容に変化はありません。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（2856-2872行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## v0.11.1での変更

CHANGELOG v0.10.0節・v0.11.0節・v0.11.1節のうち本ページの範囲に関わるものと、v0.9.0 から v0.11.1 までの仕様書の差分で確認できたものです。v0.10.0・v0.11.0・v0.11.1 の CHANGELOG に「Before you upgrade」節はありません。v0.10.0・v0.11.0 由来の項目は版を明記します。このページが v0.9.0 までに引用していた仕様書の行は、v0.11.1 では移動しています（CHANGELOG の v0.9.0 以前の節は 401 行下がりました）。ページ内の行番号は、確認できたものを v0.11.1 の行に改めました。

### 既定ハーネスの変更と Windows（v0.11.0 以降）

- v0.11.0 以降、保存したハーネスの選択がない新規インストールの既定は **KAS** です。Kiro CLI を明示的に選んだ場合は、その選択が保たれます（`harness-parity.md` 89行、CHANGELOG v0.11.0節 151-153行）
- KAS は Windows で非サンドボックス（UNCONFINED）で動きます。詳細は「[サンドボックスの3モード](#サンドボックスの3モード)」の Windows の注記を参照してください
- v0.11.0 以降の UI と CHANGELOG は、Mate（v0.10.0 以前・公式ページでは crewmate）と呼びます（CHANGELOG v0.11.0節 59行・74-75行）。コード識別子・設定キー・API パスは crewmate のままです

> ⚠ **出典間で記述が食い違っています。本サイトは裁定しません。** 既定ハーネスについて、リポジトリの `harness-parity.md`（89行）と CHANGELOG v0.11.0節（151-153行）は KAS を既定と記述しています。公式 agent-backends ページ（Page updated 2026-10-12）は Kiro CLI を「Default backend」と記述しています。

**出典**: <https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-parity.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.11.0節 59行・74-75行・151-153行（`fe6f5be`）

### SSH agent の転送

仕様書の記述では、`off`・`standard`（`auto`）・`cc` のティアで `~/.ssh` が読める構成は、同意ファイルなしで `SSH_AUTH_SOCK` を保持します。公式 security ページは既定オフと記述しており、食い違いは「[SSH agent forwarding](#ssh-agent-forwarding同意制v0111-の仕様書は既定が異なる)」の注記に書きました。CHANGELOG に説明はなく、仕様書の記述は v0.10.0 タグの `security.md`（817行）で確認できます（v0.9.0 タグでは「default OFF」）。実際の挙動がどの版から変わったかは**未確認**です。

### ツール承認

- **時限の信頼**（v0.10.0）: チャットの承認プロンプトは、「このコマンド」または同種のすべてのコマンドを、セッション全体に加えて、**1時間**または**その日の残り**の期間でも許可できます（CHANGELOG v0.10.0節 322-324行）。仕様書は、リクエストの `ttl_seconds` を 1〜86400 の整数とし、それ以外の値は許可を記録せず拒否すると記述しています。期限は壁時計と単調時計の両方で保持し、どちらかが過ぎると失効します。時限の許可はそのチャットだけに効き、再起動で消えます（`security-deep-dive.md` 591-607行）。公式 security ページ（Page updated 2026-10-12）の承認レベル表には、この選択肢の記載がありません
- **Reads モードで無確認になる Crew 自身の読み取り MCP ツール**（仕様書のみ。v0.11.0 タグの `security.md` で確認でき、v0.10.0 タグにはありません。CHANGELOG・Release 本文に説明なし）: ダッシュボードの Reads 承認モード（`trust_reads`）は、Crew が同梱するコアサーバーの `memory_recall`・`search_chat_history`・`get_chat_session`・`skill_search`・`local_knowledge_search` の閉じた集合を、カードなしで承認します。それ以外の MCP 呼び出しは従来どおり確認を求めます（`security.md` 2303-2310行、`security-deep-dive.md` 582-589行）
- **読み取り専用の自動承認の絞り込み**: v0.10.0 で、git は読み取り専用のシェルコマンドとして自動承認されなくなり、プログラムへの信頼付与は書き込みリダイレクトを覆わなくなりました（CHANGELOG v0.10.0節 401-402行）。v0.11.1 では、kiro-cli の読み取り専用のファイル検索（`grep`・`glob`・`code` の検索系）が安全確認の後に承認されます（CHANGELOG v0.11.1節 29-37行、`security.md` 2355行）
- **承認 ID の分離**（v0.11.1）: バックグラウンドの各ツール承認は固有の ID を持ち、1つの回答が別の承認を決着させません（CHANGELOG v0.11.1節 29-37行）
- **KAS の spec が許可する内容を Crew が処理する**（v0.11.1）: KAS は、spec の `allowedTools` が許可する組み込みツールを、Crew 自身のチェックを通過した後で自動承認します。deny floor・機密パス検査・書き込み保護の検査・ガバナンスは、許可より先に走ります。`toolsSettings.shell.allowedCommands` は、リテラル文字・エスケープされた句読点・`.*` だけのサブセットで書かれた最大 64 件が対象で、4096 文字以内の単純な 1 コマンドにだけ効きます。連結・パイプ・リダイレクト・グループ・置換を含むコマンドは許可されません。`toolsSettings.shell.denyByDefault` は許可リスト以外のシェル呼び出しの拒否になり、`AUTO_APPROVE` の下でも拒否が効きます。`toolsSettings.fs_write.fallbackAction: "deny"` は、`allowedPaths` に含まれない書き込みを拒否します。リモートワークスペースは、これらの許可リストを持つエージェントを拒否します（`REMOTE_AGENT_RESTRICTED`）（CHANGELOG v0.11.1節 20-27行、`security.md` 2168-2282行）
- **エージェント spec の hooks**（v0.11.1）: エージェント spec の hooks がツールをブロックするのは、終了コードが 2 のときだけです。kiro-cli と同じ挙動です（CHANGELOG v0.11.1節 20-27行）。信頼できないチェックアウトの spec の hooks の扱いは「[v0.9.0での変更](#v090での変更)」を参照してください

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.10.0節 322-324行・401-402行、v0.11.1節 20-37行（`fe6f5be`）

### 拒否コマンドとコマンドゲート

- **拒否ルールを 1 件削除**（v0.11.1）: `find -type f` や `od -tx1` のようなコマンドを curl のアップロードとして誤って拒否していたルールが削除されました（CHANGELOG v0.11.1節 39-43行）。仕様書の差分は、削除されたルールの ID を示していません。`data-exfil-curl-file-body` は `security.md` 2650行に引き続き存在し、削除されたルールとの関係は**判定不能**です。拒否ルールの現行件数は未確認のままです
- **`rm -rf` の根・ホームの綴り違い**（v0.11.0）: `local-destructive-rm-rf-*` の 2 行は連続した 1 つの綴りだけにマッチしていましたが、引用符・エスケープ・コマンド置換・空白だけの語などの綴り違いも拒否する小さな安全網が加わりました（CHANGELOG v0.11.0節 219-220行、`security.md` 1660行）
- **シェル展開によるクラウドメタデータ拒否の迂回**（v0.11.0）: 算術展開を IMDS アドレスの最後のオクテットに挟んだトークンが、IMDS 拒否をすり抜けられなくなりました（CHANGELOG v0.11.0節 219行、`security.md` 1634行）
- **`-c` スクリプトの読み取り**（v0.11.1）: オプションやリダイレクトの後ろに置かれた `-c` のスクリプトを見つけます（CHANGELOG v0.11.1節 39-40行、`security.md` 1673行）
- **切り詰められたシェルタイトル**（仕様書のみ。v0.10.0 タグで確認できます。CHANGELOG・Release 本文に説明なし）: kiro-cli は `Running: <command>` のコマンドを先頭 197 文字に切り詰めますが、deny の判定は切り詰められていないコマンドを併せて見ます（`security.md` 1237行）
- **自己保護 floor が 6 件に**（仕様書のみ。CHANGELOG・Release 本文に説明なし）: カタログの行を持たず floor だけの自己保護ルールが `security.md` 1743行に 6 件挙がっています。`self-protection-skills-authority-retire`（オペレーターの端末で auto-skill の公開権限を脇に移す回復操作を、エージェントのシェルから実行できなくする floor）は v0.11.0 タグで確認でき、v0.10.0 タグにはありません。v0.7.0 のフラグ付きファイル配信の floor（`self-protection-file-delivery`）はこの 6 件に含まれます
- **クラウドガード**（v0.11.1）: CHANGELOG は、エージェントのプロセスがすべて、人間専用のアクションに対するクラウドガードでエージェントとして扱われると記述しています（v0.11.1節 39-41行）。仕様書に対応する記述は特定できず、人間専用のアクションの範囲は**未確認**です

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.11.0節 219-220行、v0.11.1節 39-43行（`fe6f5be`）

### 出力の秘匿化

- **`redact_credentials()` は 4 段です**: 固定パターン（クラウドのアクセスキー ID・秘密鍵・PEM・チャット／フォージのトークン・パッケージレジストリのトークン・JWT・`Authorization: Bearer`・認証情報を含む DB 接続 URI）、Base64 の復号後の再検査、ラベルのない 40 文字の秘密鍵の推測、`token` URL パラメータの値です。ラベル付きの一致は、ラベルごと値を置き換えます（`{"AccessKeyId": "..."}` は `{"[REDACTED: credential]"}` になります）（`security-deep-dive.md` 401-416行）
- **外向き URL の例外**: 有効な S3 presigned URL は除外されます。ACP の OAuth バナーは、承認済みの認可エンドポイントで標準の OAuth パラメータを許します。Crew 自身の Slack アプリ作成リンクはエイリアスだけが残ります。companion の厳密なホストと、読み手が許可したホスト（*Allow for this host*。ワークスペース単位に read-only leaf へ保存）は、長さと Base64 のヒューリスティックだけを免除し、認証情報の検査は有効のままです（`security-deep-dive.md` 417-428行）
- **分断された AWS キー対とストリーム中で切れたリンク**（v0.11.0）: 1 つの塊として秘匿化されます。certifi は advisory に対応した版に更新されました（CHANGELOG v0.11.0節 222-225行）
- **`filelock`**（v0.11.1）: ローカルの判定モデルが入れる `filelock` は、公開された advisory が修正された版になりました。対象の版と advisory の ID は CHANGELOG に記載がなく**未確認**です（CHANGELOG v0.11.1節 39-43行）
- **チャネルトークンの `secret://` 参照**（v0.10.0）: [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md#シークレットと環境変数)を参照してください

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.11.0節 222-225行、v0.11.1節 39-43行（`fe6f5be`）

### アクセス制御

- **v0.11.0**: owner gate がセッション履歴・Knowledge の読み取り・タスク操作に及びます。Mate のレコード（ルール・目標・DM スレッドの紐づけ）は、ゲートウェイ専用のディレクトリ（`member-records`）に置かれます。各ハーネス自身の許可ファイルは書き込み保護されます。リモート MCP のプローブ URL は SSRF 検査を受けます。CLI は、ローカルシークレットを送る前にゲートウェイ側のピアを確認します（CHANGELOG v0.11.0節 219-225行、`security.md` 1279行、`cli.md` 84-89行）
- **v0.10.0**: デスクトップアプリはダッシュボードのトークンをログに出しません。ゲートウェイは、切り詰められた署名鍵では起動を拒否します。webapp のプレビューは `unsafe-eval` なしで動きます（CHANGELOG v0.10.0節 401-404行。仕様書での確認は行っていません）
- **Feishu（Lark）のグループメッセージ**（v0.10.0）: bot にメンションしたメッセージだけが処理されます。メンションのないメッセージは、`authorize` の前に SEL の記録なしで破棄されます。DM はこの判定を見ません（CHANGELOG v0.10.0節 388-390行、`messaging.md` 6778-6791行）
- **内部 MCP 認証の拒否コード**（仕様書のみ。v0.10.0 タグで確認できます。CHANGELOG・Release 本文に説明なし）: `403 Forbidden` の原因が複数あるため、`unix_peer_unverified`・`peer_session_mismatch`・`caller_record_missing`・`internal_secret_missing` のラベルで区別します（`security.md` 2897行）
- **ガバナンス**（仕様書のみ。CHANGELOG・Release 本文に説明なし）: `channels.posture` は葉ごとに結合され、両層が設定した葉は 2 つのルールセットの共通部分になります（v0.10.0 タグで確認でき、v0.9.0 タグにはありません。`governance.md` 159-164行）。crew に紐づく共有テンプレート（Crew が所有しない spec）は、kiro-cli での開始時に、ガバナンスの上限を超える許可（`allowedTools` や `autoApprove` の項目）が含まれていると開始を拒否されます。KAS は spec から許可を取らず、開始時に上限と照合して投影します（v0.11.0 タグで確認でき、v0.10.0 タグにはありません。`governance.md` 1020-1034行）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/governance.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/messaging.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.10.0節 388-390行・401-404行、v0.11.0節 219-225行（`fe6f5be`）

### ホスト側 git の hooks

- **設定で定義された git hooks も無効化されます**（git 2.54+ の `hook.<name>.command`。v0.10.0 タグで確認でき、v0.9.0 タグにはありません）: auto-improvement App のホスト側 git の全コマンドに、worktree と初期化済みサブモジュールの `hook.<name>.*` ごとに `hook.<name>.enabled=false` が付きます。`core.hooksPath` はフック用ディレクトリにしか効かないためです。フック名を安全に列挙できない場合は、コマンドを拒否します（`auto-improvement.md` 976行）
- **他の経路**: `git worktree add` は `core.hooksPath` と `core.fsmonitor` を `-c` で抑止します（`followup-suggestions-trust-model.md` 42-45行）。dev-fleet は `GIT_CONFIG_KEY_*` の 9 組で `core.fsmonitor` と `core.hooksPath` を無効にし、さらに設定で定義された hooks を呼び出しごとに無効にします（`dev-fleet.md` 1920-1921行・1937-1945行）。`followup-suggestions-trust-model.md` と `dev-fleet.md` 1920-1921行の `core.hooksPath`・`core.fsmonitor` の記述は v0.9.0 の一次情報にもあり、v0.9.0 までの本ページは、これらを確認しないまま「他の経路への適用範囲は未確認」と書いていました。
- 上記以外のすべての経路への適用は**判定不能**です

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/dev-fleet.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/followup-suggestions-trust-model.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.9.0節 575-579行（`fe6f5be`）

### 既知のギャップは 9 点になりました

`security-deep-dive.md`「Known gaps」節に、「接頭辞もラベルもない 40 文字の秘密鍵らしき文字列の判定は推測にすぎない」が加わり（v0.11.0 タグで確認でき、v0.10.0 タグにはありません）、番号付きの項目は 9 点（＋別枠のリソース上限依存）になりました。詳細は「[既知のギャップ](#既知のギャップリポジトリのアーキテクチャ文書が明記)」の 6 を参照してください。CHANGELOG に対応する記述はありません（`security-deep-dive.md` 709-713行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（672-788行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## v0.9.0での変更

CHANGELOG v0.9.0節「Notable fixes」の **Security and access**（174-178行）のうち、本ページの範囲に関わるものです。v0.9.0 の CHANGELOG に「Before you upgrade」節はありません。

- **データホームのファイルは本人だけが読める権限で作成される**: 詳細（ファイル `0600`・ディレクトリ `0700`、既存ストアの起動時スイープ、Windows の扱い）は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md#シークレットと環境変数) を参照してください（`security.md` 2677-2739行）
- **組み込み App の書き込みルートは dashboard owner だけが受け付ける**: 汎用の `PUT /api/apps/<name>/config` は owner 以外に 403 `owner_only` を返します（App トークンは、トークンに与えられた範囲内で別扱い）。App のインストール・更新・レジストリ書き込みのルートは全呼び出し元に対して owner 限定で、自分自身の `/api/apps/<self>/update` を呼ぶ App トークンも 403 になります（`app-kit-platform.md` 2392-2399行）
- **投影されたシークレットを含むエージェント spec は owner だけが読める権限で書かれる**: OAuth クライアントシークレットは vault が正で、エージェント spec には `oauth.clientSecret` として投影されます。この spec の書き込みは POSIX では毎回 `0o600`（既存ファイルは owner のビットを保ち group/other を外す）で、他のローカルユーザーが平文を読めません。シークレットをディスクから無くすには kiro-cli のランタイム側のシークレット経路が必要で、課題 #10702 で追跡されています（`connections.md` 46-49行）。POSIX の記述です
- **信頼できないチェックアウトのエージェント spec の hooks は、ターンループに届かない**: 仕様書で確認できたのは、goose・opencode の各 backend で、エージェント spec の `hooks` が、チェックアウト側の spec にその `mcpServers` の起動を許可する判定（`session_mcp._project_mcp_trusted`）の下でのみ採用されることです。拒否された場合はユーザーレベルの同名 spec を読み、無ければそのターンに spec hooks を持たず、新しいセッションにその旨の notice 行（`project_spec_hooks_withheld`）が付きます。**KAS はユーザーレベルの spec だけを読み**（`spec_hooks.spec_project_dir`）、チェックアウト側の判定の対象ではありません。kiro-cli は spec の hooks を自分で実行するため Crew は発火せず、claude と codex では spec の hooks がどこでも実行されません（両 backend の新規セッションに、事象名を挙げる notice 行が 1 行付きます）。以上は `agent-host-contract.md` 635行の記述です。**訂正**: v0.9.0 以前の本ページは、判定の対象に KAS を含めて記載していましたが、誤りでした。v0.9.0 タグの仕様書（591行）にも同じ区別（KAS はユーザーレベルのみ）が書かれていました。上記以外の backend での扱いは**未確認**です
- **ホスト側 git では、設定で定義された git hooks が無効になる**: CHANGELOG の記述です。仕様書で確認できた範囲は、[v0.11.1での変更](#v0111での変更)の「ホスト側 git の hooks」にまとめました。v0.9.0 タグの `auto-improvement.md` 955-972行で確認できたのは、auto-improvement App のホスト側 git で、全ホスト側 git コマンドに `core.hooksPath` を空デバイスに向ける設定と `core.fsmonitor=false` が付くことでした。他のすべての経路への適用範囲は**未確認**です
- **ダッシュボードはフォントをローカルから配信する**（CHANGELOG の記述のみ。仕様書での確認は行っていません）

出典: CHANGELOG.md v0.9.0節 174-178行（`99e6253`）。v0.11.1 のファイルでは 575-579行（`fe6f5be`）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/app-kit-platform.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/connections.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/agent-host-contract.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。`auto-improvement.md` 955-972行のみ `99e6253`、v0.9.0）

### 既知のギャップが8点に

`security-deep-dive.md`「Known gaps」節に、8点目として Design Critique の capture browser におけるクロスオリジン・サブリソースの DNS rebinding が追加されました（下記「[既知のギャップ](#既知のギャップリポジトリのアーキテクチャ文書が明記)」の9。v0.9.0 時点の番号は 8）。v0.9.0 タグの同ファイル713行にあり、v0.8.0 タグ・v0.7.2 タグの同節にはありません。CHANGELOG には対応する記述は見当たりません。また、リソース上限の段落は v0.8.0 タグで更新されています（下記）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（628-739行）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）（v0.9.0 時点の行。v0.11.1 では 672-788行）

## v0.8.0での変更

CHANGELOG v0.8.0節のうち、本ページの範囲に関わるものです（「Redaction you can read」225-237行、「The sandbox, on your terms」418-425行、「Approvals, install and update」616-624行、「Security and scheduled jobs」696-703行ほか）。v0.8.0 の CHANGELOG に「Before you upgrade」節はありません。

### 承認の再検査（approval floor）

どの面（ダッシュボード・チャネル・サブエージェント）で Approve が押されても、実行前にもう一度、現行の denied-command ルールと protected-path ルールで検査されます。拒否された呼び出しは実行されず、SEL に `rejected_transport_floor` として記録されます。トランスポートが記録していない要求に対する承認は、実行されずに拒否されます。この検査が検査対象を取得できない場合も拒否されます（fail closed）。

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/acp-client.md>（1268-1281行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.8.0節 616-624行（v0.9.0 タグのファイルの行。`99e6253`）

### オーナーが書いた auto-approve 一覧（`mcp.honour_auto_approve`）

`mcp.honour_auto_approve` は**既定で `true`**で、変更後は **Gateway の再起動が必要**です（Settings では「Changes need a restart」のバッジが付くフィールドです）。

- オーナーが `mcp.json` またはエージェントファイルに書いた `autoApprove` 一覧のツールは、承認カードと Crew のツールゲートを飛ばします。kiro-cli がそれらのツールをローカルで承認するため、Crew は権限要求を見ず、自身のツールゲートも動きません。**approval floor と `PreToolUse` hook も迂回します**
- governance ceiling は、この設定にかかわらず一覧を取り除けます
- `false` にして Gateway を再起動すると、サーバー spec が安全と宣言していないツールがすべて Crew のゲートに戻ります。稼働中の Gateway には影響しません
- App 自身の一覧は、設定にかかわらず常に無視されます
- SEL には、一覧を残したとき `mcp_auto_approve_honoured`、取り除いたとき `mcp_auto_approve_withheld` が記録されます

v0.7.2 タグの `docs/` には `mcp.honour_auto_approve` の記述がありません。v0.7.2 でのオーナー作成の `autoApprove` 一覧の扱いは、v0.7.2 の `architecture/mcp.md`（315-320行）がガバナンスの上限に従って処理すると記述するにとどまり、**未確認**です。

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>（193-209行・406-416行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.8.0節 616-620行（v0.9.0 タグのファイルの行。`99e6253`）

### 認証情報の秘匿化の表示

- **認証情報カード**: 返信から認証情報が除去されると、鍵アイコン（lock）のタグが表示されます。選択するとカードが開き、何に一致したか・どのファイルやコマンド由来か・安全な参照方法を示します。vault の項目の場合は Settings → Secrets を案内し、値は表示しません
- **ブロックされたリンクのカード**: 外向きデータの検査で止められたリンクには警告タグが付きます。**Inspect** を選び、**Review full URL** を展開してから操作を選びます。**Open once** は確認を求め、何も保存しません。**Allow for this host** は現在のワークスペースにホストを保存し、長いクエリとエンコード済みデータの検査だけを緩めます。認証情報の検査は有効のままです。許可の解除は **Undo** または設定画面で行います
- **ファイル表示の秘匿化トグル**: **Redact credentials in files the dashboard opens for you** は Settings → Security にあり、**既定でオン**です。Chat の Files タブ、Library と Artifacts のプレビューに適用されます。オフにすると、ダッシュボードではファイルが書かれたとおりに表示されますが、会話とすべてのメッセージングチャネルは秘匿化されたままです。キーストーン `credential_redaction.json` に保存されます（`security.md` 1583行）
- 長いテキストを切り詰める前に認証情報が秘匿化されるため、切り詰め境界をまたぐシークレットが監査行・ログ・ダッシュボードのペイロード・Hook 出力に漏れません（公式ページ）

> ⚠️ **許可したホストの設定場所の呼称は、出典によって異なります。本サイトは裁定しません。** 公式 security ページ（Page updated 2026-10-12）は許可の解除先を「**Settings → Security → Redaction**」と記述し、CHANGELOG v0.8.0節（230-232行）は許可したホストが「Settings → Security → **Allowed link hosts**」に一覧表示されると記述しています。

> ⚠️ **ファイル表示の秘匿化トグルの適用範囲は、出典によって記述が異なります。本サイトは裁定しません。** 公式 security ページ（Page updated 2026-10-12）は、Chat の Files タブと Library・Artifacts のプレビューに適用されると記述しています。`security-deep-dive.md`（425-427行）は、オーナーのスイッチが Files ビューの中だけに適用されると記述しています。`security.md`（1583行）は、スイッチを参照する場面がファイルビューア 1 か所であり、それを支える 2 つのハンドラー（`api_file_read` と `api_file_diff`）を挙げています。この差は v0.9.0 の一次情報から続いています。

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.8.0節 225-237行（v0.9.0 タグのファイルの行。`99e6253`）

### エージェントが書き換えられない設定ファイル

サンドボックス内のエージェントプロセス（Linux・macOS）は、`config.json` と `config.local.json` を書き換えられません。Crew のファイルエディタは `~/.kiro/settings/mcp.json` を書き換えられません。Windows のディレクトリジャンクションにも、symlink と同じ保護パスの検査が適用されます（公式ページ）。仕様書は、`config.json` が `agent.sandbox`・`agent.apps_allow_third_party`・`agent.apps_trusted`・`agent.sandbox_allow_unsandboxed_exec`・`agent.approval_mode` など、閉じ込めを緩めるスイッチを持つため、読み取り専用で封印していると記述しています（`security.md` 1282行）。同じ行は、Linux では封印がファイル単位のバインドマウントであり、Gateway が当該ファイルを保存すると、次のspawnまで封印が外れた状態になる残余リスクも記述しています。サンドボックス内では `kirocrew config set` が失敗し、ダッシュボードを案内します。

出典: CHANGELOG.md v0.8.0節 696-703行（`99e6253`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（1282行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### ダッシュボードの書き込み系ルートは owner 限定

アプリのインストール・起動・有効化、スケジュールジョブの編集・実行・確認・キャンセル、ホストファイルの読み取り、エージェントの駆動を行うダッシュボードの全ルートは、ダッシュボードの owner を要求します。App トークンは、自分のスケジュールジョブだけを管理できます。v0.9.0 では組み込み App の書き込みルートにも同じ制限が広がっています（[v0.9.0での変更](#v090での変更)）。

出典: CHANGELOG.md v0.8.0節 696-701行（`99e6253`）

### `strict` サンドボックスと Fargate の非サンドボックス実行

- **`strict`**: `agent.sandbox` に設定できる値として追加されました（[サンドボックスの3モード](#サンドボックスの3モード)を参照）
- **Fargate レーンの `internal_only`（既定 `false`）**: `cloud.json` の Fargate レーンのキーです。`true` にすると、自分の Crew を自分のアカウントで動かし、Crew が読み込む内容のリスクを自分が負うという宣言になり、モデルの subprocess が**サンドボックスなし**で起動します（Fargate は user namespace を提供できず、サンドボックスを維持するタスクは起動時に終了するため）。起動時に警告が出ます。プロダクトはこのキーを書きません。マルチテナントや外部から到達可能な Crew では設定しないよう、ガイドが記述しています。Fargate レーンのみで、既定はオフです（`remote-crew-on-fargate.md` 46行・72-88行、`cloud.md` 218行。CHANGELOG v0.8.0節 440-446行（v0.9.0 タグのファイルの行。`99e6253`））

### その他

- 危険な動詞を単にデータとして言及するコマンド（`chmod`・`chown`・`netcat`）は拒否されなくなりました（[Denied commands の管理](#denied-commands-の管理)）
- WhatsApp グループの許可リスト検査（[Owner lock](#owner-lock)）
- Dashboard のトークンの発行経路（[Owner lock](#owner-lock)）

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

> **注記**: `kirocrew file-delivery approve` は、v0.9.0 タグのリポジトリでは CHANGELOG v0.7.0節（445-448行）と `docs/feature-map/README.md` にのみ登場し、CLI仕様書 `docs/system-specs/modules/cli.md` には記載がありませんでした。v0.11.1 の `cli.md` には、このコマンドが 83行（`cli_server.py` が持つコマンドの一覧）・657行と 669行（タイムアウトの分類）・1721行（ゲートウェイ側のピア確認を通す内部シークレットの送信元の表）に登場します。`file-delivery` を含む行はこの 4 か所だけで、`policy` などのコマンドを説明する表（598行）に `file-delivery` の行はありません。

出典: CHANGELOG.md v0.7.0節 445-448行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>（373-392行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### SSH agent forwarding（同意制。v0.11.1 の仕様書は既定が異なる）

git over SSH と SSHによるコミット署名は、明示的な keystone の同意の後でのみ、エージェントのサンドボックス内で operator の `SSH_AUTH_SOCK` を使えます。**公式 security ページ（Page updated 2026-10-12）と CHANGELOG v0.7.0節は、既定をオフと記述しています。** v0.11.1 の仕様書（`security.md` 930行）は、同意なしで転送される場合を記述しています（下の注記と、[v0.11.1での変更](#v0111での変更)の「SSH agent の転送」を参照）。

同意が必要な場合は、サンドボックスの外（自分の端末）から `~/.kiro/crew/ssh_auth_sock_consent.json` を作成します。

```json
{"enabled": true}
```

- ソケットはSSH agentが保持する鍵の**使用**を許可するもので、秘密鍵の素材はサンドボックスへコピーされません
- ただしエージェントが実行するコードは、そのソケットが公開する任意のIDを使えます（公式はこれを既定オフの理由として挙げています）
- この認可のためのエージェント向け設定やCLIトグルはありません。`modules/security.md` は `agent.*` 設定フィールドを意図的に設けていない（エージェントが書き込めるため）と記述し、同意ファイルはエージェントのファイルツールが拒否し、OSサンドボックスが読み取り専用でマウントする keystone リーフに置かれます
- 他の機密環境変数は引き続き除去され、strict モードでは鍵ファイル自体も隠されたままです

> **解消済みの食い違い**: v0.9.0 以前は、`security-deep-dive.md`（212-215行）が「サンドボックスのティアが有効なときは常に `SSH_AUTH_SOCK` を除去する」と記述し、`security.md`（736行）と公式 security ページが同意制の転送を記述していたため、リポジトリ内の記述が食い違っていました。v0.11.1 の `security-deep-dive.md`（214-218行）は `security.md`（930行）と同じ内容に書き換わっており、この食い違いは解消しました。
>
> ⚠ **出典間で記述が食い違っています。本サイトは裁定しません。** 公式 security ページ（Page updated 2026-10-12、208-210行）は、git over SSH と SSH によるコミット署名が、明示的な keystone の同意の後でのみ operator の `SSH_AUTH_SOCK` を使え、**既定はオフ**だと記述しています。一方、v0.11.1 の `security.md`（930行）は、有効なティア（ガバナンスの `sandbox.min_level` で引き上げた後）が `off`・`standard`（`auto`）・`cc` のいずれかで、かつそのスポーンのハーネス別の認証情報マスクが `~/.ssh` を覆わない場合は、**同意なしで** `SSH_AUTH_SOCK` を保持すると記述しています。同行は理由として、`~/.ssh` が読めるティアなので、ソケットが加えるのはファイルに存在しない鍵（パスフレーズ、ハードウェアトークン、外部 agent）だけだと挙げています。`strict` と、`~/.ssh` を隠す強制ハーネスでは、従来どおり同意ファイルが必要です。この既定の変更を説明する記述は、CHANGELOG の v0.10.0・v0.11.0・v0.11.1 の節に見当たらず、導入した版は**未確認**です（v0.9.0 の `security.md` 736行は「default OFF」でした）。公式ページの更新日は 2026-10-12 のままです。

出典: CHANGELOG.md v0.7.0節 449-451行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（930行）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（214-218行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／v0.9.0 の記述は `security.md` 736行（`99e6253`）。CHANGELOG に説明が無く、仕様書の差分にだけある変更です

### ポリシーの fail closed

- 2つのポリシー層から合成された上限は、そのルールが読み込まれるようになりました
- ポリシーを読み込めない場合、operator が拒否したツールは拒否されます
- API経由での skill の作成・編集には owner が必要になりました

出典: CHANGELOG.md v0.7.0節 452-454行（`c67c506`）

### リスクの高いツール呼び出しのフラグ付け（Preview・既定オフ）

**Decisions (Jev) は Preview 機能**です（Settings → Developer → Feature Previews。詳細は [03_chat.md](03_chat.md) を参照）。リスクの高いツール呼び出しのフラグ付けは、Decisions 配下の**独自の同意スイッチ**を持ち、**以前から同意していた人に対してもオフ**です。CHANGELOG はその理由を、ツールの引数を送信するためと述べています。

- `docs/feature-map/README.md` は、このフラグ（Tool risk badge）を**注釈にすぎず、許可の判断には使われない**と記述しています
- ガバナンスプロファイルは `capabilities.decisions` でこのプレビュー全体をオフにできます
- v0.8.0 から、リスクのバッジはプロバイダの確信度が80パーセント以上の場合にのみ付き、Decisions の判断は、合意した上限の範囲で直近2〜3ターンを含められます（Preview。CHANGELOG v0.8.0節 360-362行、`99e6253`）

出典: CHANGELOG.md v0.7.0節 292-305行・670-672行（`c67c506`）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>（92行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

### 既知のギャップが7点に

`security-deep-dive.md`「Known gaps」節に、7点目として「同一ユーザーによるランチャの自己汚染」が追加されました（下記「[既知のギャップ](#既知のギャップリポジトリのアーキテクチャ文書が明記)」の8。v0.9.0 時点の番号は 7）。v0.7.0 タグの同ファイル629行に存在し、v0.6.0 タグの同節にはありません。CHANGELOG には対応する記述は見当たりません。

## v0.3.0での変更

### terminalのcredential秘匿化について（一次情報が4件で食い違う・裁定しない）

**v0.3.0のCHANGELOGには、terminal出力のcredential秘匿化について、同一版節内で相反する記述が存在します。** セキュリティ挙動であり片側だけを断定すると導入判断を誤らせるため、**本サイトは裁定せず、確認できた4つの記述をすべて原文の対象表現のまま併記します**。

| # | 出典 | 記述（対象の書き方に注意） |
|---|------|--------------------------|
| ① | CHANGELOG.md **21行**（v0.3.0節「Before you upgrade」。v0.9.0 タグのファイルでは2258-2260行） | 「**The terminal no longer scans its output for credentials.**（terminalは出力のcredentialスキャンを行わなくなった）」。理由として**CJKテキストとemojiがPTYストリームで壊れていたこと**、および**意図的に出力した秘密を飲み込んでいたこと**が挙げられている。「**Terminal output is now passed through untouched**（terminal出力は手を加えず素通しになった）」 |
| ② | CHANGELOG.md **221行**（v0.3.0節「Security and governance」。v0.9.0 タグのファイルでは2458-2459行） | 「**Credentials are scrubbed on the live stream**（ライブストリームでcredentialがscrubされる）— Redaction now covers **real-time output** as well as replayed history（redactionが再生履歴に加えてリアルタイム出力もカバーするようになった）」 |
| ③ | v0.7.2 以前のリポジトリ `README.md` **332〜333行**（v0.9.0 タグの `README.md` には該当する記述がありません） | 「... strips sensitive environment variables, and **redacts credential patterns from output before it reaches a chat surface**（チャットサーフェスに到達する前に出力からcredentialパターンをredactする）」 |
| ④ | `docs/system-specs/modules/learn-cron-dashboard.md` **3673行**（v0.9.0 タグ。v0.7.2 の同ファイルにも同じ記述があります） | `POST /api/terminal/redact` は、チャットのコンポーザに挿入される前に terminal の選択範囲の**全体**をスキャンするエンドポイントで、「**WHOLE credential boundary** for the web terminal」だと記述している。ライブのPTYストリームはスキャンされずにブラウザへ転送され、スクロールバックの再生もブラウザへだけ行われるため、**この選択範囲の受け渡しが、terminal出力がモデルに届く唯一の経路**だという。したがって**設定による無効化なしに無条件に実行**され、フロントエンドは200が返らない限り挿入しない（fail closed）。選択範囲全体が連続したテキストであることが、正規表現による秘匿化の精度を保てる唯一の入力だとも述べている |

**4件は「対象」の書き方がそれぞれ異なります**（①は terminal の出力スキャン全般、②は「ライブストリーム」、③は「chat surface に到達する出力」、④は「ブラウザへのPTYストリームは未スキャンだが、モデルに渡る選択範囲は無条件にredactされる」）。どれが正しいか・なぜ併存するのかは公式に説明がないため、**本サイトは推測しません**。

**④の記述は①②③のいずれとも整合する読み方が可能ですが、本サイトはその解釈を採用して他の記述を退けることはしません**（「ブラウザ表示は素通し・モデルへの受け渡しはredact」という切り分けは④にのみ書かれており、①②③の文面はその区別をしていないため）。

いずれの記述を前提にしても、**terminalに秘密を表示させる運用は避ける**のが安全側の判断です。導入時の設定は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

> **④の出典の修正**: 本サイトは v0.7.2 以前、④を `src/kiro_crew/dashboard/handlers/terminal.py` の `api_terminal_redact` の docstring（932〜938行）として掲載していました。同じ趣旨の記述が仕様書 `learn-cron-dashboard.md` 3673行にあることを v0.9.0 タグで確認したため、`src/` の解析に依存しない形に差し替えました。

①②の出典は`21584ea`（参照: 2026-08-22）で確認した行番号と、v0.9.0 タグ（`99e6253`、参照: 2026-10-25）のファイルの行番号を併記しています。③の出典は v0.3.0（`21584ea`）の `README.md` です。

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
- **`kirocrew policy show` が拒否コマンドカタログを列挙する**（176行）。`21584ea`の`modules/cli.md` 135行によると、`show`はカタログを**カテゴリ別のグループ件数として要約**し、`--ids`で各カテゴリのrule idを列挙します。**エンタープライズポリシーが有効かどうかに関わらず全インストールで利用可能**です。拒否されている内容をソースを見ずに読めるようになりました（[04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)参照）

出典: CHANGELOG.md v0.3.0節（`21584ea`）／`docs/system-specs/modules/cli.md` 135行。

## 既知のギャップ（リポジトリのアーキテクチャ文書が明記）

**リポジトリのアーキテクチャ文書（`security-deep-dive.md`「Known gaps」節）が明記している事実**です。公式 security ページに Known gaps の節はありません（v0.7.2 以前の本ページは、見出しに「公式が明記」と書いていましたが、誤りでした）。伏せると導入判断を誤らせるため必ず記載します。

1. **既定でネットワーク送信（egress）の制御がない**: サンドボックスは認証情報ファイルを隠しますが、外向きのネットワークアクセスは制限しません。侵害されたエージェントは任意のホストへ非認証情報データを送信できます
2. **コマンドマッチングはbash ASTパーサではない**: regex/tokenizerによる正規化（引用符処理・空文字列結合・`$HOME`/チルダ展開等）で既知の回避手法は防ぎますが、実行時に組み立てられたペイロード（文字列結合・base64・間接的な `eval "$CMD"`）はパターンにマッチしません
3. **監査ダッシュボードがない**: SEL イベントはAPI（`/api/sel/events`、owner 限定）経由で照会できますが、閲覧・フィルタ・アラート用のUIがなく、改ざん検知や異常検知は手動です
4. **エージェント内部からのサンドボックス脱出検知がない**: Gatewayはバックエンドの有無をfail-closedで判定しますが、プロセス内部から閉じ込めが実際に機能しているかを検証する仕組みはありません
5. **Base64認証情報検出には下限がある**: 最小長以上のBase64チャンクのみが復号・再チェックされるため、短い断片や複数メッセージに分割された認証情報は検出を逃れる可能性があります
6. **接頭辞もラベルもない 40 文字の秘密鍵らしき文字列の判定は推測にすぎない**（v0.11.0 タグの `security-deep-dive.md` から記載。v0.10.0 タグにはありません）: 出力の秘匿化の第 3 段（pass 3）は、ラベルのない 40 文字の並びをエントロピーと形で判定します。ランダムな秘密とランダムなダイジェストを区別できないため、除外規則を持っていても、無害な値を誤って秘匿化する場合があります。記録された方向性は、大文字小文字を区別しないラベルとキー ID のペアリングに置き換えることです（この方向性は `security-deep-dive.md` が参照する `docs/decisions/` の決定文書に記録されています。CHANGELOG・Release 本文に説明はありません）。その置き換えが v0.11.1 で実装済みかどうかは**未確認**です（決定文書は段階的な実装としており、`security-deep-dive.md` は第 3 段を現行の機構として記述しています）
7. **書き込み保護はCrew自身のトラストルートのみで、ユーザーのシェル起動ファイルは対象外**: 認証情報ディレクトリとキーストーンは読み書きブロック、`config.json` とマイグレーションマーカーは書き込みブロックされますが、`~/.bashrc`・`~/.zshrc`のような永続化先（原文「ordinary persistence targets」）はブロックされません（ホームディレクトリ全体をブロックするとエージェントが機能しなくなるため）。承認ゲートと破壊的コマンドルールのみが緩和策です。`config.json` の書き込みブロックは v0.8.0 で追加されました（CHANGELOG v0.8.0節 1097-1104行）
8. **同一ユーザーによるランチャの自己汚染は受容されており、防御されない**（CWE-345。v0.7.0 で追加。v0.9.0 時点の番号は 7）: 解決された `kiro-cli` ランチャは署名・ハッシュ・所有者・インストール元の検査なしにそのまま実行され、唯一のゲートは `platform_compat.is_executable_file` です。呼び出しユーザーとして動くエージェントが自身のランチャを上書きすると、次回のspawnでそのバイト列が実行されます。**Status: ACCEPTED**。塞ぐ仕組みは見落としではなく**設計上退けられています**: owner／パス／Developer-IDによるゲートは、実際のインストール（toolbox・Homebrew・winget・自己更新された `/Applications` バンドル）を製品内の回復手段なしに立ち往生させるためです。攻撃は operator としてのローカル書き込み権限を前提とし、本製品の脅威モデルの外にあります（上記7の `~/.bashrc` と同じ分類）。残存影響は閉じ込めたspawn経路（Linux namespace・macOS seatbelt）では限定され、汚染されたランチャもKiro Crew自身のサンドボックス内で動きます。直接execするのはmacOSの内部サンドボックスへの委譲時のみです。マルチテナント／エンタープライズ運用には署名基盤・鍵管理・インストール配置の決定が必要で、そのようなゲートは**既定オフ**でなければならないと記述されています
9. **Design Critique の capture browser におけるクロスオリジン・サブリソースの DNS rebinding は、限定的にのみ閉じられている**（v0.9.0 で追加。v0.9.0 時点の番号は 8。**Status: ACCEPTED, bounded**）: URL レンダー取得経路は、信頼できない外部ページに対して headless Chromium を起動します。ベースホストと、同一ホストのサブリソースは、SSRF ガードとホスト名の IP ピンで閉じています。一方、ベースと別ホストのクロスオリジン・サブリソースは、ガードが公開アドレスと判定して通した後に Chromium が自前で名前解決するため、公開アドレス→内部アドレスの順に答える名前が窓になります。攻撃には、批評対象のページと rebinding 用の DNS 名の両方の制御が必要です。ルート層で塞ぐと正当な CDN のフォントや画像まで落とすことになります。完全な対策は Chromium のリゾルバから独立した、ブラウザより下層の egress フィルタ（ネットワーク名前空間またはホストファイアウォールの許可リスト）で、機構の選択はプラットフォームごとのインフラ判断のため、設計項目（#17748）として追跡されています。Design Critique の capture browser が Preview かどうか・既定でオンかどうかは、この記述からは**未確認**です

**出典**（全体。1〜9 と別枠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（672-788行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

**出典**（6の根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（709-713行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

**出典**（8の根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（730-760行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

**出典**（9の根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（762-788行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

**（gapsの箇条書きの外側にある追加事項）**: リソース上限はプラットフォームに依存します。Linux は、cgroup delegation がある場合に cgroup v2 でサブツリーのプロセス数とメモリを制限します。Windows の ACP エージェントツリーは、Job Object のプロセス数とメモリの上限を使います（thread ではなく process の意味）。macOS と、delegation のない Linux には、サブツリー単位の hard なプロセス数・メモリ上限がなく、ファイルディスクリプタ上限と事後の reaper のみが有効です（`security-deep-dive.md` 723-728行）。

> **リソース上限の記述の更新（v0.8.0 タグで確認）**: v0.7.2 以前の本ページは、cgroup v2 が使えない環境ではファイルディスクリプタ上限のみが有効だと記載していました。v0.8.0 タグの同ファイルは Windows の Job Object を追加しており、本内容は仕様書で確認したもので、CHANGELOG の v0.8.0節・v0.9.0節に対応する記述は見当たりません（v0.10.0〜v0.11.1 の節にもありません）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（723-728行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## 未確認事項

- 拒否コマンドルールの現行件数（v0.11.1 の公式ページ・仕様書にも件数の記載がなく、`src/` は解析していません）。v0.11.1 で削除された拒否ルールの ID も、仕様書の差分から特定できません
- 公式 security ページの既定表記（Interactive→Automatic）が、どの版で変わったか
- Windows で `agent.sandbox_allow_unsandboxed_exec` が未宣言のときの既定（許可）を、どの版で導入したか
- `SSH_AUTH_SOCK` を同意なしで保持する仕様書の記述に対応する挙動を、どの版で導入したか（仕様書では v0.10.0 タグで確認でき、v0.9.0 タグでは default OFF。CHANGELOG に説明なし）
- エージェント spec の hooks の扱いのうち、KAS・goose・opencode・kiro-cli・claude・codex 以外の backend での扱い（本ページの「v0.9.0での変更」に記載した範囲以外）と、ホスト側 git の hooks 無効化が全経路に及ぶかどうか（本ページの「v0.11.1での変更」に記載した範囲以外は判定不能）
- `mcp.honour_auto_approve` を導入する前（v0.7.2）の、オーナー作成の `autoApprove` 一覧の扱い
- Design Critique の capture browser が Preview かどうか・既定でオンかどうか
- 出力の秘匿化でラベルのない 40 文字の秘密鍵の推測（第 3 段）を、ラベルとキー ID のペアリングに置き換える方向性が、v0.11.1 で実装済みかどうか
- CHANGELOG v0.11.1節のクラウドガードが対象とする「人間専用のアクション」の範囲と、`filelock` の対象の版・advisory の ID
- 既知のギャップの件数は、v0.11.1 タグ（`fe6f5be`）の実測で**9点（＋別枠のリソース上限依存）**です。既知ギャップは当初4点として計画されていましたが、`security-deep-dive.md` の実測で6点、v0.7.2 タグで7点、v0.9.0 タグで8点、v0.11.1 タグで9点であることを確認しました
- 食い違いが継続している項目（裁定していません）: Windows の非サンドボックス実行の既定（v0.11.0 以降の既定ハーネス KAS を含む）、`strict` の隠蔽対象、許可したリンクホストの設定場所の呼称、ファイル表示の秘匿化トグルの適用範囲（v0.9.0 から継続）、terminal の credential 秘匿化の4件、公式 security ページの Denied commands の例と警告、SSH agent の転送の既定（公式 security ページと v0.11.1 の `security.md`。新規）、既定ハーネス（公式 agent-backends ページと v0.11.1 の `harness-parity.md`。新規）。SSH agent の転送に関する `security-deep-dive.md` と `security.md` の食い違いは、v0.11.1 で解消しました

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
- 導入時の設定: [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

# セキュリティのハードニング（導入時の設定）

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（egress既知ギャップの根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

---

## 📑 このページの内容

- [サンドボックスの設定](#サンドボックスの設定)
- [バックエンド不在時の挙動](#バックエンド不在時の挙動)
- [macOSでの相互排他](#macosでの相互排他)
- [ガバナンスファイルの配置](#ガバナンスファイルの配置)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [terminal出力とcredentialについて（v0.3.0・裁定しない）](#terminal出力とcredentialについてv030裁定しない)
- [シークレットと環境変数](#シークレットと環境変数)
- [ネットワークegressについて](#ネットワークegressについて)
- [未確認事項](#未確認事項)

---

> セキュリティの概念・機構の解説は [01_features/09_security.md](../01_features/09_security.md) を参照してください。本ページは**導入時の設定手順**に絞ります。

## サンドボックスの設定

```bash
kirocrew config set agent.sandbox <mode>
```

または Settings → Security、Developer ページの Config タブ。設定可能な値は `auto`（既定）／`strict`（v0.8.0 で追加）／`off`（[01_features/09_security.md](../01_features/09_security.md)の表を参照）。変更は、変更後に開始したセッションに適用されます（`config.md` 2969行）。

**推奨（公式のBest practices）**: `agent.sandbox` は `auto` または `strict` に保つ。特別な理由がない限り `off` で運用しない。

**`auto` と `strict` の選び方**: `auto`（標準）では `~/.aws`・`~/.ssh`・`~/.kube` がサンドボックス内から見えます。公式ページは、コマンドゲートがシェルテキスト中の綴りでは認証情報パスを保護せず、サンドボックスのバインドマスクがサブプロセスの境界だと警告しています。`strict` はこれらのディレクトリを隠しますが、`aws` CLI の `credential_process`・git-over-SSH・`kubectl` はエージェント内で使えなくなります。`strict` が隠す対象の記述は出典によって異なります（[01_features/09_security.md](../01_features/09_security.md#サンドボックスの値域解消済みと-strict-の隠蔽対象食い違い)を参照。本サイトは裁定しません）。

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（178-218行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## バックエンド不在時の挙動

サンドボックスのバックエンドが存在しないホストでは**fail-closed**（無防備に起動せず拒否）します。

> ⚠️ **Windows では出典間で記述が食い違っています（裁定しません）。** `docs/guides/windows-install.md`（316-325行・327-333行）と `modules/security.md`（955行・961行）は、Windows では委譲先のない経路が**既定で非サンドボックス実行**され、拒否するには `agent.sandbox_allow_unsandboxed_exec` を `false` と明示宣言する、と記述しています。公式 `security/` ページ（Page updated 2026-10-12）と公式 `configuration/` ページ（Page updated 2026-10-20。`agent.sandbox_allow_unsandboxed_exec` の既定を `false` と記載）は、サンドボックスを適用できないときの fail-closed を記述しています。v0.7.2 以前は `README.md` も fail-closed の当事者として引用していましたが、この文は v0.9.0 の `README.md` に存在しないため、当事者から外しました。詳細は [02_windows.md](02_windows.md#osレベルサンドボックス層の不在) を参照してください。
>
> `security.md`（968-971行）は、バックエンドのないホストで `kirocrew setup` が非サンドボックス実行の可否を尋ねる（Windows 以外では opt-in、Windows では opt-out の形）こと、非サンドボックス実行がすべて SEL に `unconfined` として記録されること、`kirocrew doctor` が実効状態（拒否／宣言による unconfined／プラットフォームの既定による unconfined）を表示することを記述しています。
>
> **v0.11.0 以降の新規インストールの既定ハーネス KAS（Windows）**: `windows-install.md`（307-314行・373行）は、既定のチャットハーネス KAS が Windows で**非サンドボックス（UNCONFINED）**で動くと記述しています。KAS には Windows 上の OS サンドボックスがなく、Kiro CLI のスポーンでもないため、他のハーネスと同じ「後ろ盾なし」経路に入るためです。ホームディレクトリ（`.aws`・`.ssh` を含む）を読めます。公式 security ページの Windows の記述（Kiro CLI の内部サンドボックスがオフの場合に該当）は、この記述と食い違ったままです。本サイトは裁定しません。KAS のチャットをサンドボックス内にとどめる手順は [v0.11.1での変更](#v0111での変更)の「Windows で KAS のチャットを制限する」を参照してください。
>
> Windows の既定を許可にした変更を説明する CHANGELOG の記述は、v0.10.0〜v0.11.1 の節を含めて見当たらず、変更した版は未確認です。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
> （参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

明示的にopt-inするには:

```bash
kirocrew config set agent.sandbox_allow_unsandboxed_exec true
```

> **⚠️ v0.3.0での重要な変更**: **governed host（ポリシーがピン留めされたホスト）では、ポリシーがローカル設定に勝ちます。これは`agent.sandbox_allow_unsandboxed_exec`のopt-inに対しても適用されます**。つまりポリシーが非サンドボックス実行を禁じている環境では、上記コマンドで`true`にしても実行は通りません。
>
> 出典: CHANGELOG.md v0.3.0節 223行（`21584ea`）「**A pinned policy floor cannot be lowered locally** — On a governed host the policy wins over local configuration, **including over the unsandboxed-exec opt-in**」。ポリシーの配置は下記「[ガバナンスファイルの配置](#ガバナンスファイルの配置)」を参照してください。

## macOSでの相互排他

macOSでは kiro-cli ≥ 2.13 の内蔵サンドボックスとの**相互排他**が働きます。カーネルが入れ子のサンドボックスプロファイルに対して`EPERM`を返すため、1つのプロセス起動につき有効な層は厳密に1つです。kiro-cli自身の内蔵サンドボックスが有効な場合、Kiro Crewはそちらに処理を委譲します。これは「既定が`off`だから委譲される」のではなく、**設定駆動の決定論的な委譲**です。

## ガバナンスファイルの配置

| ファイル | 用途 |
|---------|------|
| `~/.kiro/crew/security_policy.json` | POLICY（エンタープライズレベルの上限） |
| `~/.kiro/crew/profiles/` | PROFILE（サーフェス単位・タスク単位の絞り込み） |

これらはトラストルートとして `_SENSITIVE_HOME_DIRS` に置かれ、エージェント自身は読み書きできません。

```bash
kirocrew policy show        # 実効ポリシーを表示
kirocrew policy validate    # ポリシーファイルのエラーを検査
kirocrew policy explain     # ツール呼び出しがどう評価されるかを説明
```

> **v0.3.0での`policy show`の詳細**: `show`は拒否コマンドカタログを**カテゴリ別のグループ件数として要約**し、`--ids`を付けると各カテゴリのrule idを列挙します。**エンタープライズポリシーが有効かどうかに関わらず、全インストールで利用可能**です（`docs/system-specs/modules/cli.md` 135行・`21584ea`。v0.11.1 では 598行・`fe6f5be`）。CHANGELOG（176行）は「拒否されている内容をソースを見ずに読めるようになった」と述べています。拒否ルールの件数は、v0.11.1 の公式ページ・仕様書にも記載がなく未確認です（経緯は [01_features/09_security.md](../01_features/09_security.md#8つの保護機構公式の順序) を参照してください）。

## v0.11.1での変更

CHANGELOG v0.10.0節・v0.11.0節・v0.11.1節のうち導入・運用の設定に関わるものと、v0.9.0 から v0.11.1 までの仕様書の差分で確認できたものです。v0.10.0・v0.11.0・v0.11.1 の CHANGELOG に「Before you upgrade」節はありません。v0.10.0・v0.11.0 由来の項目は版を明記します。仕様書の行番号は v0.11.1 の行です（CHANGELOG の v0.9.0 以前の節は 401 行下がりました）。

### Windows で KAS のチャットを制限する

- v0.11.0 以降、保存したハーネスの選択がない新規インストールの既定は **KAS** です。Kiro CLI を明示的に選んだ場合は、その選択が保たれます（`harness-parity.md` 89行、CHANGELOG v0.11.0節 151-153行）
- 既定の KAS は Windows で**非サンドボックス（UNCONFINED）**で動き、ホームディレクトリ（`.aws`・`.ssh` を含む）を読めます。KAS には Windows 上の OS サンドボックスがなく、Kiro CLI のスポーンでもないためです。新しいデスクトップインストールでも、最初のチャットの前に設定ファイルの編集は要りません（`windows-install.md` 303-314行）
- チャットを Kiro CLI のサンドボックス内にとどめるには、Settings → Agent Harness で **Kiro CLI** を選びます（`"acp_backend": "kiro"` として保存されます）
- `agent.sandbox_allow_unsandboxed_exec: false` を宣言すると、KAS のチャットは `sandbox_allow_unsandboxed_exec` を名指しするメッセージで拒否されます。この状態でチャットするには Kiro CLI を選びます（`windows-install.md` 303-314行・373行）
- macOS では、KAS の relay route（`kiro-cli acp --agent-engine v3`）は kiro-cli のスポーンなので、内蔵サンドボックスのスイッチがオンなら kiro-cli の内蔵サンドボックスに委譲されます。KAS の bundle route（Node を kiro-cli なしで実行）は Crew の seatbelt を使います（`security.md` 987行）

> ⚠ **出典間で記述が食い違っています。本サイトは裁定しません。** 既定ハーネスについて、リポジトリの `harness-parity.md`（89行）と CHANGELOG v0.11.0節（151-153行）は KAS を既定と記述しています。公式 agent-backends ページ（Page updated 2026-10-12）は Kiro CLI を「Default backend」と記述しています。Windows のサンドボックスについても、公式 security ページ（Page updated 2026-10-12）の記述（Kiro CLI の内部サンドボックスがオフの場合に fail-closed）と `windows-install.md` の記述が食い違ったままです（「[バックエンド不在時の挙動](#バックエンド不在時の挙動)」を参照）。

**出典**: <https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-parity.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.11.0節 151-153行（`fe6f5be`）

### SSH agent の転送の既定

仕様書（`security.md` 930行）は、有効なティアが `off`・`standard`（`auto`）・`cc` で、そのスポーンの認証情報マスクが `~/.ssh` を覆わない場合、同意ファイルなしで `SSH_AUTH_SOCK` を保持すると記述しています。`strict` と、`~/.ssh` を隠す強制ハーネスでは、従来どおり同意ファイルが必要です。公式 security ページは既定オフと記述しており、食い違いを含む詳細は「[SSH agent forwarding を同意ファイルで有効にする](#ssh-agent-forwarding-を同意ファイルで有効にする)」に書きました。CHANGELOG に説明はなく、導入した版は**未確認**です。

### agent.env でエージェントの環境変数を設定する（v0.10.0）

`agent.env` は、`HTTPS_PROXY`・`NODE_EXTRA_CA_CERTS` などの変数を、すべてのエージェントプロセスに設定します（CHANGELOG v0.10.0節 318-319行、`config.md` 2990行）。

- 値は、エージェントの子プロセスが継承する環境の上に重ねられ、ドライバー自身の変数より前、拒否名のスクラブより前に適用されます。拒否名のスクラブは `agent.env` で設定した値にも効きます（`security.md` 943行）
- 保存時に、次の名前は理由つきで書き込みが拒否されます（手編集で入れた場合は、読み込み時にキー名だけを警告して捨てます）。Crew やサンドボックスが持つ名前、ローダー・シェル・言語ランタイムなどがコードを読み込む原因になる名前（`LD_*`・`BASH*`・`NODE_OPTIONS`・`GIT_*` など）、`KEY`・`TOKEN`・`SECRET`・`PASSWORD`・`PASSWD`・`CREDENTIAL` を名前の区切り語に持つ資格情報らしい名前です。資格情報は vault に置きます
- 仕様書は、これが拒否リストであってフェンスではなく、`config.json` を誰が書けるかが境界のままだと記述しています

### チャネルトークンの secret:// 参照と隠しファイルの保存（v0.10.0）

- チャネルトークンは `secret://` 参照を受け付け、ダッシュボードでチャネルを保存すると、新しい秘密は vault に保存され、`.env` には `KEY=secret://KEY` の形で書かれます。`kirocrew secrets import [--apply]` は、データホームの `.env` だけを読み（`--file` はありません）、資格情報の行を `secret://KEY` 参照に書き換えます。解決できない参照は未設定として扱われ、キー名だけがログに残ります（CHANGELOG v0.10.0節 325-327行、`security.md` 788-805行）
- データホーム直下のゲートウェイが書く隠しファイル（ブラウザ拡張のトークン、Ops Mission Control のシークレットストア、データホームの `.env` など）は、検証済みのステージングディレクトリ経由で保存されます。ステージングディレクトリを使えない場合は保存を拒否し、ウィザードはメッセージを表示し、ダッシュボードと Weixin の保存は 409 で答えます（`security.md` 412-430行。CHANGELOG に説明なし）

### MCP サーバーの環境変数を KAS に渡す範囲（v0.11.0・v0.11.1）

KAS のセッションは、エージェントの spec を ACP で渡すため、MCP サーバーの `env` の値がフレーム・記録・ログに載ります。そこで Crew は、`${NAME}` 形式の edition 中継を除き、Crew が作っていないサーバーでは `true`/`false`（大文字小文字・前後の空白を許す）だけを中継し、数値・単語・URL・パス・JSON・参照・`secret://` は差し止めます。差し止めたときはログにキー名だけを出します（CHANGELOG v0.11.1節 20-27行、`security.md` 719行）。

### 読み取り専用で封印されるパス（v0.10.0）

- KAS エンジンの置き場所 `<data-home>/engines` は、サンドボックスでは読み取り専用で、エージェントのファイルツールも拒否します。インストーラーはサンドボックスの外の自分の端末で動き、置いた成果物は取得前に manifest で sha256 を固定されています（`security.md` 1287行）
- `kiro_crew` パッケージが `site-packages`（または `dist-packages`）に直接置かれている構成（ホイールのインストール、デスクトップ同梱のインタープリター）では、そのインストールディレクトリが読み取り専用で封印されます（`security.md` 1286行）
- どちらも CHANGELOG に説明はなく、仕様書の差分にだけある項目です

### Docker の seccomp プロファイル（v0.11.0）

`docs/guides/docker.md` の Option A のプロファイル（固定した moby の既定から生成）は、`unshare`・`clone`・`mount`・`umount2` の 4 つを無条件に許可します。コンテナは `CAP_SYS_ADMIN` を持たないため、既定プロファイルの `umount2` の条件付き許可が効かず、private window を持つスポーンが拒否されるのを避けるためだと、仕様書は記述しています（`security.md` 1024行。CHANGELOG に説明なし）。

### Lambda MicroVM レーン（v0.10.0）

`cloud.json` の `microvm` ブロックで、Crew を AWS Lambda MicroVM で動かすレーンを追加できます（CHANGELOG v0.10.0節 343-346行）。ガイド `remote-crew-on-microvm.md`（185-200行）は、次を記述しています。

- VM の HTTPS エンドポイントには**常にインターネットから到達できます**。`NO_INGRESS` コネクタを付けて起動しても閉じません。このレーンでは、クルーが提供するすべてのルートが呼び出し元を認証します
- ゲストは `KIROCREW_ALLOW_UNSANDBOXED=1` で動きます。MicroVM がクルーの作業の隔離境界であり、1 プロセスの user namespace の代わりに、マシン全体を Firecracker の境界が囲むためです

「[v0.8.0での変更](#v080での変更)」の Fargate レーンの `internal_only` と並べると、サンドボックスなしで動く構成として、Fargate の `internal_only` を有効にした場合と MicroVM レーンの 2 つになります。

### ホスト側 git の hooks

- **設定で定義された git hooks も無効化されます**（git 2.54+ の `hook.<name>.command`。v0.10.0 タグで確認でき、v0.9.0 タグにはありません）: auto-improvement App のホスト側 git の全コマンドに、worktree と初期化済みサブモジュールの `hook.<name>.*` ごとに `hook.<name>.enabled=false` が付きます。`core.hooksPath` はフック用ディレクトリにしか効かないためです。フック名を安全に列挙できない場合は、コマンドを拒否します（`auto-improvement.md` 976行）
- **他の経路**: `git worktree add` は `core.hooksPath` と `core.fsmonitor` を `-c` で抑止します（`followup-suggestions-trust-model.md` 42-45行）。dev-fleet は `GIT_CONFIG_KEY_*` の 9 組で `core.fsmonitor` と `core.hooksPath` を無効にします（`dev-fleet.md` 1920-1921行）。この 2 つの記述は v0.9.0 の一次情報にもあり、v0.9.0 までの本ページは、これらを確認しないまま「他の経路への適用範囲は未確認」と書いていました
- 上記以外のすべての経路への適用は**判定不能**です

### 承認と拒否コマンドの変更

操作に関わる変更は [01_features/09_security.md](../01_features/09_security.md#v0111での変更) にまとめました。主なものは、チャットの承認プロンプトの 1 時間／その日の残りの期限付き信頼（v0.10.0）、git が読み取り専用のシェルコマンドとして自動承認されなくなったこと（v0.10.0）、`rm -rf` の根・ホームの綴り違いの拒否（v0.11.0）、v0.11.1 での拒否ルール 1 件の削除です。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/config.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/remote-crew-on-microvm.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/docker.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/dev-fleet.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/followup-suggestions-trust-model.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／CHANGELOG.md v0.10.0節 318-319行・325-327行・343-346行、v0.11.1節 20-27行（`fe6f5be`）

## v0.9.0での変更

CHANGELOG v0.9.0節「Notable fixes」の **Security and access**（174-178行）のうち、導入・運用の設定に関わるものです。v0.9.0 の CHANGELOG に「Before you upgrade」節はありません。

### データホームのファイル権限

データホーム配下のファイルは `0600`、ディレクトリは `0700` で作成されます。想定する脅威は、別のローカルアカウントによる会話記録・Knowledge Library・ログ・設定の読み取りです（`security.md` 2677-2739行）。仕様書は次の3層で実現すると記述しています。

| 層 | 内容 |
|---|---|
| 作成時 | 各ストアが作成時にモードを指定します。SQLite データベースは接続の前に `0600` で事前作成され、`-wal`・`-shm`・`-journal` にも引き継がれます。会話記録・通知・`gateway.log`・ロックファイルは `0600` で開かれ、ディレクトリは全階層が `0700` で作られます |
| ルート | `ensure_data_home()` が、CLI の起動のたびにデータホーム自体を `0700` にします |
| 既存のファイル | Gateway の起動ごとに1回、リスナーが応答を始めた後のワーカースレッドで、Kiro Crew 自身の固定のストア一覧（会話記録・エージェントとメンバーの状態・Artifacts・メモリ・Knowledge と research のストア・meetings のストア・ログ・監査と security-event のログ・通知・設定）について group/other のビットを外します。時間（30秒）とエントリ数（1,000,000）に上限があり、symlink を辿らず、他のオーナーのファイルやハードリンクされたファイルは対象外です。データホームの下に置いたプロジェクトやユーザーのファイルは対象にしません |

- プロセスの umask は変更されません。エージェントがユーザー自身のリポジトリに書くファイルまで `0600` になるのを避けるためです（仕様書の記述）
- 一覧のストアに、幅広いモードを維持するスイッチはありません
- **Windows は変更なし**です。データホームの継承可能な owner-only の DACL が、新規ファイルに適用されます

### 投影されたシークレットを含むエージェント spec

OAuth クライアントシークレットは vault が正で、エージェント spec には `oauth.clientSecret` として投影されます。この spec の書き込みは POSIX では毎回 `0o600` で、既存ファイルは owner のビットを保ち group/other を外します。ディスクからシークレットを無くすには kiro-cli のランタイム側のシークレット経路が必要で、課題 #10702 で追跡されています（`connections.md` 46-49行。POSIX の記述）。

### 信頼できないチェックアウトの hooks とホスト側 git

CHANGELOG は、信頼できないチェックアウトのエージェント spec の hooks がターンループに届かなくなったこと、設定で定義された git hooks がホスト側の git で無効になったことを記述しています（v0.9.0節 174-178行、v0.11.1 のファイルでは 575-579行）。仕様書で確認できた範囲は次のとおりです。

- エージェント spec の `hooks` は、goose・opencode の各 backend で、チェックアウト側の spec にその `mcpServers` の起動を許可する判定の下でのみ採用されます。拒否された場合はユーザーレベルの同名 spec を読み、無ければそのターンに spec hooks を持ちません。**KAS はユーザーレベルの spec だけを読み**、kiro-cli は spec の hooks を自分で実行し、claude と codex では spec の hooks がどこでも実行されません（`agent-host-contract.md` 635行）。**訂正**: v0.9.0 以前の本ページは、判定の対象に KAS を含めて記載していましたが、誤りでした。v0.9.0 タグの仕様書（591行）にも同じ区別が書かれていました
- auto-improvement App のホスト側 git は、全コマンドに `core.hooksPath` を空デバイスに向ける設定と `core.fsmonitor=false` を付けます（v0.9.0 タグの `auto-improvement.md` 955-972行。v0.11.1 では 956-973行）。設定で定義された git hooks の無効化と他の経路は、[v0.11.1での変更](#v0111での変更)の「ホスト側 git の hooks」を参照してください

上記以外の backend・App・経路への適用範囲は**未確認**です。

出典: CHANGELOG.md v0.9.0節 174-178行（`99e6253`）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/connections.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/agent-host-contract.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## v0.8.0での変更

CHANGELOG v0.8.0節のうち、導入・運用の設定に関わるものです（「Redaction you can read」225-237行、「The sandbox, on your terms」418-425行・440-446行、「Approvals, install and update」616-624行、「Security and scheduled jobs」696-703行）。

### `mcp.honour_auto_approve`（既定 `true`・Gateway の再起動が必要）

オーナーが `mcp.json` またはエージェントファイルに書いた `autoApprove` 一覧のツールは、承認カードと Crew のツールゲートを飛ばし、approval floor と `PreToolUse` hook も迂回します。既定は `true` です。サーバー spec が安全と宣言していないツールをすべて Crew のゲートに戻すには、`false` にして **Gateway を再起動**します（稼働中の Gateway には影響せず、Settings では「Changes need a restart」のバッジが付くフィールドです）。governance ceiling は設定にかかわらず一覧を取り除け、App 自身の一覧は常に無視されます。詳細は [01_features/09_security.md](../01_features/09_security.md#オーナーが書いた-auto-approve-一覧mcphonour_auto_approve) を参照してください。

### 認証情報の秘匿化の表示

Settings → Security の **Redact credentials in files the dashboard opens for you** は既定でオンです。オフにすると、Chat の Files タブ、Library と Artifacts のプレビューでファイルが書かれたとおりに表示されますが、会話とすべてのメッセージングチャネルは秘匿化されたままです。ブロックされたリンクの **Allow for this host** はホストをワークスペース単位で保存します。許可したホストの設定場所の呼称は出典で異なります（[01_features/09_security.md](../01_features/09_security.md#v080での変更)を参照）。

### 設定ファイルの封印

サンドボックス内のエージェントプロセス（Linux・macOS）は `config.json` と `config.local.json` を書き換えられません。サンドボックス内では `kirocrew config set` が失敗し、ダッシュボードを案内します。設定は、サンドボックスの外の自分の端末またはダッシュボードから変更します。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（1282行。v0.9.0 タグでは 1054行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### Fargate レーンの `internal_only`（既定 `false`）

Fargate のタスクは user namespace を提供できないため、サンドボックスを維持する Crew コンテナは起動時に終了します。`cloud.json` の Fargate レーンで `internal_only` を `true` にすると、モデルの subprocess を**サンドボックスなし**で起動します。自分の Crew を自分のアカウントで動かし、Crew が読み込む内容のリスクを自分が負うという宣言で、起動時に警告が出ます。プロダクトはこのキーを書きません。マルチテナントや外部から到達可能な Crew では設定しないよう、ガイドが記述しています（`remote-crew-on-fargate.md` 46行・72-88行。CHANGELOG v0.8.0節 440-446行）。

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/remote-crew-on-fargate.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）／CHANGELOG.md v0.8.0節 616-620行（`99e6253`）

## v0.7.0での変更

### フラグ付きファイル配信を承認する（ホスト上での手順）

`file_send` が認証情報のような内容を検出して配信を拒否した場合、次の手順で一回限りの配信を承認します。

1. ダッシュボードの owner が **Settings → Security** で一回限りの承認をアームする
2. 宛先とファイルを確認する
3. **Gatewayホスト上で直接**次を実行する

```bash
kirocrew file-delivery approve
```

- **Computer Use が有効な間はこのコマンドが拒否されます**（エージェントがキーボード自動化で operator の承認を偽装することを防ぐため。公式ページ）。承認するには Gatewayホストの端末が必要です
- 承認はアームされた要求に限定され、今後のファイルに対する一般的な迂回にはなりません
- `kirocrew file-delivery approve` は、v0.9.0 タグのリポジトリでは CHANGELOG v0.7.0節（445-448行）と `docs/feature-map/README.md` にのみ登場し、CLI仕様書 `docs/system-specs/modules/cli.md` には記載がありませんでした。v0.11.1 の `cli.md` には 83行・657行・669行・1721行に登場しますが、`policy` などのコマンドを説明する表（598行）に `file-delivery` の行はありません

出典: CHANGELOG.md v0.7.0節 445-448行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>（373-392行。v0.9.0 タグでは 327-346行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### SSH agent forwarding を同意ファイルで有効にする

サンドボックス内で git over SSH や SSHによるコミット署名に operator の `SSH_AUTH_SOCK` を使わせる必要があるのに同意が要る構成（`strict`、および `~/.ssh` を隠す強制ハーネス）では、**サンドボックスの外（自分の端末）から** `~/.kiro/crew/ssh_auth_sock_consent.json` を次の内容で作成します。

```json
{"enabled": true}
```

| 項目 | 内容 |
|------|------|
| 置き場所 | `~/.kiro/crew/ssh_auth_sock_consent.json`（keystone リーフ。エージェントのファイルツールは拒否し、OSサンドボックスは読み取り専用でマウント） |
| 設定キー・CLI | **なし**（`agent.*` の設定フィールドもCLIトグルも意図的に設けられていない） |
| 保持されるもの | `SSH_AUTH_SOCK` のみ。他の機密環境変数は引き続き除去される |
| 鍵素材 | サンドボックスへはコピーされない。strict モードでは鍵ファイル自体も隠されたまま |
| トレードオフ | エージェントが実行するコードは、そのソケットが公開する任意のIDを使える |

> ⚠ **出典間で記述が食い違っています。本サイトは裁定しません。** 公式 security ページ（Page updated 2026-10-12、208-210行）と CHANGELOG v0.7.0節は、この同意の後でのみ転送でき、既定はオフだと記述しています。一方、v0.11.1 の `security.md`（930行）は、有効なティア（ガバナンスの `sandbox.min_level` で引き上げた後）が `off`・`standard`（`auto`）・`cc` のいずれかで、そのスポーンのハーネス別の認証情報マスクが `~/.ssh` を覆わない場合は、**同意なしで** `SSH_AUTH_SOCK` を保持すると記述しています。理由として同行は、`~/.ssh` が読めるティアなので、ソケットが加えるのはファイルに存在しない鍵（パスフレーズ、ハードウェアトークン、外部 agent）だけだと挙げています。この既定の変更を説明する記述は、CHANGELOG の v0.10.0・v0.11.0・v0.11.1 の節に見当たらず、導入した版は**未確認**です（v0.9.0 の `security.md` 736行は「default OFF」でした）。公式ページの更新日は 2026-10-12 のままです。詳細は [01_features/09_security.md](../01_features/09_security.md#ssh-agent-forwarding同意制v0111-の仕様書は既定が異なる) を参照してください。

出典: CHANGELOG.md v0.7.0節 449-451行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（930行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）／v0.9.0 の記述は `security.md` 736行（`99e6253`）。CHANGELOG に説明が無く、仕様書の差分にだけある変更です

### ポリシーの fail closed

ポリシーを読み込めない場合、operator が拒否したツールは拒否されます。2つのポリシー層から合成された上限はそのルールが読み込まれ、API経由での skill の作成・編集には owner が必要になりました。ポリシーファイルを編集した後は `kirocrew policy validate` で検査してください（公式ページのGovernance節の警告）。

出典: CHANGELOG.md v0.7.0節 452-454行（`c67c506`）

## terminal出力とcredentialについて（v0.3.0・裁定しない）

**v0.3.0のCHANGELOGには、terminal出力のcredential秘匿化について相反する記述が同一版節内に存在します。** 本サイトは裁定せず4件を併記しています。**運用上は、terminalに秘密を表示させないことを前提に設計するのが安全側の判断です。**

詳細な4件の併記は [01_features/09_security.md](../01_features/09_security.md) の「v0.3.0での変更」を参照してください。

## シークレットと環境変数

`.env` は認証情報ロード時とセットアップウィザードで `chmod 600` が強制されます（`security.md` 2675行。v0.9.0 タグでは 2194-2196行）。チャネルトークンは `.env` に `secret://` 参照として保存でき、環境変数の設定には `agent.env` が使えます（[v0.11.1での変更](#v0111での変更)を参照）。データホーム配下の他のファイルも `0600`、ディレクトリは `0700` で作成されます（v0.9.0。[v0.9.0での変更](#v090での変更)を参照）。機密パスとして以下がブロックされます: `~/.aws`・`~/.ssh`・`~/.gnupg`・`~/.gpg`・`~/.config/gcloud`・`~/.azure`・`~/.docker/config.json`・`~/.kube/config`・`~/.npmrc`・`~/.pypirc`・`~/.netrc`・`~/.git-credentials`・Crew自身のトラストルート（`.env`・`sel_hmac.key`・`trust`・`security_events.jsonl`等）。

## ネットワークegressについて

> **重要（既知ギャップの1つ）**: **既定でネットワーク送信（egress）の制御はありません。** サンドボックスは認証情報ファイルを隠しますが、外向きのネットワークアクセスは制限しません。`network.egress` というガバナンススコープでポリシーが設定されている場合はホストを制限できますが、既定でオンのegress境界はありません。ネットワークnamespace（Linux）やトラステッドデスティネーションの許可リストを使ったホストファイアウォールルールで閉じることができます。

## 未確認事項

- エージェント spec の hooks と、ホスト側 git の hooks 無効化の適用範囲。spec の hooks は、KAS・goose・opencode・kiro-cli・claude・codex 以外の backend での扱いが判定不能です（「v0.9.0での変更」に記載した範囲以外）。ホスト側 git の hooks 無効化は、「v0.11.1での変更」の「ホスト側 git の hooks」に記載した経路以外は判定不能です
- `mcp.honour_auto_approve` の導入前（v0.7.2）の、オーナー作成の `autoApprove` 一覧の扱い
- Windows で `agent.sandbox_allow_unsandboxed_exec` が未宣言のときの既定（許可）を、どの版で導入したか（Windows の記述の食い違いは継続しており、裁定していません）
- `SSH_AUTH_SOCK` を同意なしで保持する仕様書の記述に対応する挙動を、どの版で導入したか（仕様書では v0.10.0 タグで確認でき、v0.9.0 タグでは default OFF。CHANGELOG に説明なし。公式 security ページとの食い違いは裁定していません）
- 拒否ルールの現行件数（v0.11.1 の公式ページ・仕様書にも記載がありません）
- 本ページの上記以外の記述は、公式 security ページ、`modules/security.md`、`architecture/security-deep-dive.md` で確認済みです。`architecture/resource-protection.md` を出典にした記述は v0.3.0（`21584ea`）で確認したものです
- 既定ハーネスについて、公式 agent-backends ページ（Kiro CLI が既定）と `harness-parity.md`・CHANGELOG（KAS が既定）の食い違いは、裁定していません

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- セキュリティの概念: [01_features/09_security.md](../01_features/09_security.md)
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

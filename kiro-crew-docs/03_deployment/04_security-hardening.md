# セキュリティのハードニング（導入時の設定）

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（egress既知ギャップの根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

---

## 📑 このページの内容

- [サンドボックスの設定](#サンドボックスの設定)
- [バックエンド不在時の挙動](#バックエンド不在時の挙動)
- [macOSでの相互排他](#macosでの相互排他)
- [ガバナンスファイルの配置](#ガバナンスファイルの配置)
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

または Settings → Security、Developer ページの Config タブ。設定可能な値は `auto`（既定）／`strict`（v0.8.0 で追加）／`off`（[01_features/09_security.md](../01_features/09_security.md)の表を参照）。変更は、変更後に開始したセッションに適用されます（`config.md` 2648行）。

**推奨（公式のBest practices）**: `agent.sandbox` は `auto` または `strict` に保つ。特別な理由がない限り `off` で運用しない。

**`auto` と `strict` の選び方**: `auto`（標準）では `~/.aws`・`~/.ssh`・`~/.kube` がサンドボックス内から見えます。公式ページは、コマンドゲートがシェルテキスト中の綴りでは認証情報パスを保護せず、サンドボックスのバインドマスクがサブプロセスの境界だと警告しています。`strict` はこれらのディレクトリを隠しますが、`aws` CLI の `credential_process`・git-over-SSH・`kubectl` はエージェント内で使えなくなります。`strict` が隠す対象の記述は出典によって異なります（[01_features/09_security.md](../01_features/09_security.md#サンドボックスの値域解消済みと-strict-の隠蔽対象食い違い)を参照。本サイトは裁定しません）。

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>（178-217行）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## バックエンド不在時の挙動

サンドボックスのバックエンドが存在しないホストでは**fail-closed**（無防備に起動せず拒否）します。

> ⚠️ **Windows では出典間で記述が食い違っています（裁定しません）。** `docs/guides/windows-install.md`（286-295行・297-303行）と `modules/security.md`（757行・763行）は、Windows では委譲先のない経路が**既定で非サンドボックス実行**され、拒否するには `agent.sandbox_allow_unsandboxed_exec` を `false` と明示宣言する、と記述しています。公式 `security/` ページ（Page updated 2026-10-12）と公式 `configuration/` ページ（Page updated 2026-10-20。`agent.sandbox_allow_unsandboxed_exec` の既定を `false` と記載）は、サンドボックスを適用できないときの fail-closed を記述しています。v0.7.2 以前は `README.md` も fail-closed の当事者として引用していましたが、この文は v0.9.0 の `README.md` に存在しないため、当事者から外しました。詳細は [02_windows.md](02_windows.md#osレベルサンドボックス層の不在) を参照してください。
>
> `security.md`（770-773行）は、バックエンドのないホストで `kirocrew setup` が非サンドボックス実行の可否を尋ねる（Windows 以外では opt-in、Windows では opt-out の形）こと、非サンドボックス実行がすべて SEL に `unconfined` として記録されること、`kirocrew doctor` が実効状態（拒否／宣言による unconfined／プラットフォームの既定による unconfined）を表示することを記述しています。
>
> **出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）、<https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

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

> **v0.3.0での`policy show`の詳細**: `show`は拒否コマンドカタログを**カテゴリ別のグループ件数として要約**し、`--ids`を付けると各カテゴリのrule idを列挙します。**エンタープライズポリシーが有効かどうかに関わらず、全インストールで利用可能**です（`docs/system-specs/modules/cli.md` 135行・`21584ea`）。CHANGELOG（176行）は「拒否されている内容をソースを見ずに読めるようになった」と述べています。拒否ルールの件数は、v0.9.0 の公式ページ・仕様書に記載がなく未確認です（経緯は [01_features/09_security.md](../01_features/09_security.md#8つの保護機構公式の順序) を参照してください）。

## v0.9.0での変更

CHANGELOG v0.9.0節「Notable fixes」の **Security and access**（174-178行）のうち、導入・運用の設定に関わるものです。v0.9.0 の CHANGELOG に「Before you upgrade」節はありません。

### データホームのファイル権限

データホーム配下のファイルは `0600`、ディレクトリは `0700` で作成されます。想定する脅威は、別のローカルアカウントによる会話記録・Knowledge Library・ログ・設定の読み取りです（`security.md` 2198-2260行）。仕様書は次の3層で実現すると記述しています。

| 層 | 内容 |
|---|---|
| 作成時 | 各ストアが作成時にモードを指定します。SQLite データベースは接続の前に `0600` で事前作成され、`-wal`・`-shm`・`-journal` にも引き継がれます。会話記録・通知・`gateway.log`・ロックファイルは `0600` で開かれ、ディレクトリは全階層が `0700` で作られます |
| ルート | `ensure_data_home()` が、CLI の起動のたびにデータホーム自体を `0700` にします |
| 既存のファイル | Gateway の起動ごとに1回、リスナーが応答を始めた後のワーカースレッドで、Kiro Crew 自身の固定のストア一覧（会話記録・エージェントとメンバーの状態・Artifacts・メモリ・Knowledge と research のストア・meetings のストア・ログ・監査と security-event のログ・通知・設定）について group/other のビットを外します。時間（30秒）とエントリ数（1,000,000）に上限があり、symlink を辿らず、他のオーナーのファイルやハードリンクされたファイルは対象外です。データホームの下に置いたプロジェクトやユーザーのファイルは対象にしません |

- プロセスの umask は変更されません。エージェントがユーザー自身のリポジトリに書くファイルまで `0600` になるのを避けるためです（仕様書の記述）
- 一覧のストアに、幅広いモードを維持するスイッチはありません
- **Windows は変更なし**です。データホームの継承可能な owner-only の DACL が、新規ファイルに適用されます

### 投影されたシークレットを含むエージェント spec

OAuth クライアントシークレットは vault が正で、エージェント spec には `oauth.clientSecret` として投影されます。この spec の書き込みは POSIX では毎回 `0o600` で、既存ファイルは owner のビットを保ち group/other を外します。ディスクからシークレットを無くすには kiro-cli のランタイム側のシークレット経路が必要で、課題 #10702 で追跡されています（`connections.md` 34-37行。POSIX の記述）。

### 信頼できないチェックアウトの hooks とホスト側 git

CHANGELOG は、信頼できないチェックアウトのエージェント spec の hooks がターンループに届かなくなったこと、設定で定義された git hooks がホスト側の git で無効になったことを記述しています。仕様書で確認できた範囲は次のとおりです。

- エージェント spec の `hooks` は、KAS・goose・opencode の各 backend で、チェックアウト側の spec にその `mcpServers` の起動を許可する判定の下でのみ採用されます。拒否された場合はユーザーレベルの同名 spec を読み、無ければそのターンに spec hooks を持ちません（`agent-host-contract.md` 591行）
- auto-improvement App のホスト側 git は、全コマンドに `core.hooksPath` を空デバイスに向ける設定と `core.fsmonitor=false` を付けます（`auto-improvement.md` 955-972行）

上記以外の backend・App・経路への適用範囲は**未確認**です。

出典: CHANGELOG.md v0.9.0節 174-178行（`99e6253`）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/connections.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/agent-host-contract.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/auto-improvement.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.8.0での変更

CHANGELOG v0.8.0節のうち、導入・運用の設定に関わるものです（「Redaction you can read」225-237行、「The sandbox, on your terms」418-425行・440-446行、「Approvals, install and update」616-624行、「Security and scheduled jobs」696-703行）。

### `mcp.honour_auto_approve`（既定 `true`・Gateway の再起動が必要）

オーナーが `mcp.json` またはエージェントファイルに書いた `autoApprove` 一覧のツールは、承認カードと Crew のツールゲートを飛ばし、approval floor と `PreToolUse` hook も迂回します。既定は `true` です。サーバー spec が安全と宣言していないツールをすべて Crew のゲートに戻すには、`false` にして **Gateway を再起動**します（稼働中の Gateway には影響せず、Settings では「Changes need a restart」のバッジが付くフィールドです）。governance ceiling は設定にかかわらず一覧を取り除け、App 自身の一覧は常に無視されます。詳細は [01_features/09_security.md](../01_features/09_security.md#オーナーが書いた-auto-approve-一覧mcphonour_auto_approve) を参照してください。

### 認証情報の秘匿化の表示

Settings → Security の **Redact credentials in files the dashboard opens for you** は既定でオンです。オフにすると、Chat の Files タブ、Library と Artifacts のプレビューでファイルが書かれたとおりに表示されますが、会話とすべてのメッセージングチャネルは秘匿化されたままです。ブロックされたリンクの **Allow for this host** はホストをワークスペース単位で保存します。許可したホストの設定場所の呼称は出典で異なります（[01_features/09_security.md](../01_features/09_security.md#v080での変更)を参照）。

### 設定ファイルの封印

サンドボックス内のエージェントプロセス（Linux・macOS）は `config.json` と `config.local.json` を書き換えられません。サンドボックス内では `kirocrew config set` が失敗し、ダッシュボードを案内します（`security.md` 1054行）。設定は、サンドボックスの外の自分の端末またはダッシュボードから変更します。

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
- `kirocrew file-delivery approve` は、リポジトリでは CHANGELOG v0.7.0節（445-448行）と `docs/feature-map/README.md` にのみ登場し、CLI仕様書 `docs/system-specs/modules/cli.md` には記載がありません

出典: CHANGELOG.md v0.7.0節 445-448行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>（327-346行）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### SSH agent forwarding を有効にする（既定オフ）

サンドボックス内で git over SSH や SSHによるコミット署名に operator の `SSH_AUTH_SOCK` を使わせるには、**サンドボックスの外（自分の端末）から** `~/.kiro/crew/ssh_auth_sock_consent.json` を次の内容で作成します。**既定はオフ**です。

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

出典: CHANGELOG.md v0.7.0節 449-451行（`c67c506`）

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（736行）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### ポリシーの fail closed

ポリシーを読み込めない場合、operator が拒否したツールは拒否されます。2つのポリシー層から合成された上限はそのルールが読み込まれ、API経由での skill の作成・編集には owner が必要になりました。ポリシーファイルを編集した後は `kirocrew policy validate` で検査してください（公式ページのGovernance節の警告）。

出典: CHANGELOG.md v0.7.0節 452-454行（`c67c506`）

## terminal出力とcredentialについて（v0.3.0・裁定しない）

**v0.3.0のCHANGELOGには、terminal出力のcredential秘匿化について相反する記述が同一版節内に存在します。** 本サイトは裁定せず4件を併記しています。**運用上は、terminalに秘密を表示させないことを前提に設計するのが安全側の判断です。**

詳細な4件の併記は [01_features/09_security.md](../01_features/09_security.md) の「v0.3.0での変更」を参照してください。

## シークレットと環境変数

`.env` は認証情報ロード時とセットアップウィザードで `chmod 600` が強制されます（`security.md` 2194-2196行）。データホーム配下の他のファイルも `0600`、ディレクトリは `0700` で作成されます（v0.9.0。[v0.9.0での変更](#v090での変更)を参照）。機密パスとして以下がブロックされます: `~/.aws`・`~/.ssh`・`~/.gnupg`・`~/.gpg`・`~/.config/gcloud`・`~/.azure`・`~/.docker/config.json`・`~/.kube/config`・`~/.npmrc`・`~/.pypirc`・`~/.netrc`・`~/.git-credentials`・Crew自身のトラストルート（`.env`・`sel_hmac.key`・`trust`・`security_events.jsonl`等）。

## ネットワークegressについて

> **重要（既知ギャップの1つ）**: **既定でネットワーク送信（egress）の制御はありません。** サンドボックスは認証情報ファイルを隠しますが、外向きのネットワークアクセスは制限しません。`network.egress` というガバナンススコープでポリシーが設定されている場合はホストを制限できますが、既定でオンのegress境界はありません。ネットワークnamespace（Linux）やトラステッドデスティネーションの許可リストを使ったホストファイアウォールルールで閉じることができます。

## 未確認事項

- 信頼できないチェックアウトの hooks とホスト側 git の hooks 無効化の適用範囲（「v0.9.0での変更」に記載した範囲以外）
- `mcp.honour_auto_approve` の導入前（v0.7.2）の、オーナー作成の `autoApprove` 一覧の扱い
- Windows で `agent.sandbox_allow_unsandboxed_exec` が未宣言のときの既定（許可）を、どの版で導入したか（Windows の記述の食い違いは継続しており、裁定していません）
- 拒否ルールの現行件数（v0.9.0 の公式ページ・仕様書に記載がありません）
- 本ページの上記以外の記述は、公式 security ページ、`modules/security.md`、`architecture/security-deep-dive.md` で確認済みです。`architecture/resource-protection.md` を出典にした記述は v0.3.0（`21584ea`）で確認したものです

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- セキュリティの概念: [01_features/09_security.md](../01_features/09_security.md)
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

# セキュリティのハードニング（導入時の設定）

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（egress既知ギャップの根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [サンドボックスの設定](#サンドボックスの設定)
- [バックエンド不在時の挙動](#バックエンド不在時の挙動)
- [macOSでの相互排他](#macosでの相互排他)
- [ガバナンスファイルの配置](#ガバナンスファイルの配置)
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

または Settings → Security。設定可能な値は `auto`（既定）／`strict`／`off`（[01_features/09_security.md](../01_features/09_security.md)の表を参照）。

**推奨（公式のBest practices）**: `agent.sandbox` は `auto` または `strict` に保つ。特別な理由がない限り `off` で運用しない。

## バックエンド不在時の挙動

サンドボックスのバックエンドが存在しないホストでは**fail-closed**（無防備に起動せず拒否）します。

> ⚠️ **Windows では出典間で記述が食い違っています（裁定しません）。** v0.7.0 以降の `docs/guides/windows-install.md` 285-290行と `modules/security.md` 309行（`c67c506`）は、Windows では委譲先のない経路が**既定で非サンドボックス実行**され、拒否するには `agent.sandbox_allow_unsandboxed_exec` を `false` と明示宣言する、と記述しています。公式 `security/` ページと `README.md` は fail-closed を記述しています。詳細は [02_windows.md](02_windows.md#osレベルサンドボックス層の不在) を参照してください。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

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

> **v0.3.0での`policy show`の詳細**: `show`は拒否コマンドカタログを**カテゴリ別のグループ件数として要約**し、`--ids`を付けると各カテゴリのrule idを列挙します。**エンタープライズポリシーが有効かどうかに関わらず、全インストールで利用可能**です（`docs/system-specs/modules/cli.md` 135行・`21584ea`）。CHANGELOG（176行）は「拒否されている内容をソースを見ずに読めるようになった」と述べています。拒否ルールの件数（137）は [01_features/09_security.md](../01_features/09_security.md) を参照してください。

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

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>（298-318行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

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

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>（282行）
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

### ポリシーの fail closed

ポリシーを読み込めない場合、operator が拒否したツールは拒否されます。2つのポリシー層から合成された上限はそのルールが読み込まれ、API経由での skill の作成・編集には owner が必要になりました。ポリシーファイルを編集した後は `kirocrew policy validate` で検査してください（公式ページのGovernance節の警告）。

出典: CHANGELOG.md v0.7.0節 452-454行（`c67c506`）

## terminal出力とcredentialについて（v0.3.0・裁定しない）

**v0.3.0のCHANGELOGには、terminal出力のcredential秘匿化について相反する記述が同一版節内に存在します。** 本サイトは裁定せず4件を併記しています。**運用上は、terminalに秘密を表示させないことを前提に設計するのが安全側の判断です。**

詳細な4件の併記は [01_features/09_security.md](../01_features/09_security.md) の「v0.3.0での変更」を参照してください。

## シークレットと環境変数

`.env` は認証情報ロード時とセットアップウィザードで `chmod 600` が強制されます。機密パスとして以下がブロックされます: `~/.aws`・`~/.ssh`・`~/.gnupg`・`~/.gpg`・`~/.config/gcloud`・`~/.azure`・`~/.docker/config.json`・`~/.kube/config`・`~/.npmrc`・`~/.pypirc`・`~/.netrc`・`~/.git-credentials`・Crew自身のトラストルート（`.env`・`sel_hmac.key`・`trust`・`security_events.jsonl`等）。

## ネットワークegressについて

> **重要（既知ギャップの1つ）**: **既定でネットワーク送信（egress）の制御はありません。** サンドボックスは認証情報ファイルを隠しますが、外向きのネットワークアクセスは制限しません。`network.egress` というガバナンススコープでポリシーが設定されている場合はホストを制限できますが、既定でオンのegress境界はありません。ネットワークnamespace（Linux）やトラステッドデスティネーションの許可リストを使ったホストファイアウォールルールで閉じることができます。

## 未確認事項

- なし（本ページの記述は公式securityページと `modules/security.md`、`architecture/resource-protection.md` で確認済み。「v0.7.0での変更」は CHANGELOG v0.7.0節・`docs/feature-map/README.md` も含めて `c67c506` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- セキュリティの概念: [01_features/09_security.md](../01_features/09_security.md)
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

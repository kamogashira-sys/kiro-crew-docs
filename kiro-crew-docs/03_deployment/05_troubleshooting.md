# トラブルシューティング

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/troubleshooting/>（Page updated 表記あり）
**出典**（venvパスの不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（venvパスの再測定・公式 `troubleshooting/` 本文の差分確認）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.9.0での追記: `doctor` のチェック項目・Dockerのseccomp/AppArmor・Windowsデスクトップ版の起動失敗）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/docker.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/docker-troubleshooting.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（公式 `troubleshooting/` ページの再確認。本文は v0.7.2 から変更なし）: <https://kiro.dev/docs/crew/troubleshooting/>（Page updated 2026-09-12）

---

## 📑 このページの内容

- [まず `kirocrew doctor`](#まず-kirocrew-doctor)
- [インストール・セットアップ](#インストールセットアップ)
- [エージェント（kiro-cli）関連](#エージェントkiro-cli関連)
- [未確認事項](#未確認事項)

---

## まず `kirocrew doctor`

大半のCrewの問題は、シェルコマンド1つで収まる修正があります。まずヘルスチェックから始めます。

```bash
kirocrew doctor
```

`doctor` はすべてのサブシステムの状態を報告します: `kiro-cli`バイナリの検出・エージェント認証・埋め込みモデル・Slackトークン・設定の妥当性・MCPサーバのプローブ。問題があれば該当する節に進みます。

v0.9.0 の `modules/cli.md` 1188-1220行「Doctor Checks」は、上に加えて次の項目を挙げています（`99e6253`。CHANGELOG/Release 本文からの確認は行っていません）。

- **Node.js**: `node` が `PATH` にあり、22.12.0 以上であること。未満は `❌` と対処を示し、doctor は exit 1 になります（Node.js の下限については [01_installation.md](01_installation.md) の食い違い注記を参照）
- **MCP ツールの自動修復**: 不足したエントリは自動で直しますが、共有の agent ホームを所有してはならないインスタンスは何も書かず、スキップした修復を issue として報告します
- **masked credential leaf**（Linux・macOS）: 秘匿対象の認証情報ファイルにハードリンクで2つ目の名前がある形。起動が拒否される形のため報告されます。問題が無ければ何も出ません
- **Agents ディレクトリ**: 回収できる孤立 temp と古いバックアップ、skill view の census。報告のみで、削除はしません
- **インストール済みスキルの現行性**: インストール元のソースツリーに対して、古い／ローカル編集／検証不能なスキルを挙げます。ネットワークは呼びません。POSIX のみで、Windows では実行されません
- **hook の auto-approve のプラットフォーム範囲**
- `kirocrew doctor --bundle` はチェックではなくモードで、ヘルスチェックの代わりに秘匿済みの診断 zip を作り、version と channel を事前入力した GitHub issue のリンクを出します
- doctor は読み取り専用です。完了済みの ledger の掃除は `kirocrew ledger-sweep` で行います

公式 `installation/` ページ（Page updated 2026-10-20）は、`kirocrew doctor` が Crew の選んだ Kiro CLI のバイナリとサインイン状態を報告すると記述しています。デスクトップアプリは Kiro CLI を同梱するため（v0.8.0〜）、同梱版が選ばれる場合があります。

## インストール・セットアップ

### インストール後に `kirocrew: command not found`

インストール先のディレクトリが `PATH` にありません。インストーラによって対処が異なります。

- **事前ビルドwheelインストーラ**: `pipx`があればそれを使用、無ければ管理対象venv（`~/.kiro/crew-venv`。`KIROCREW_VENV`で変更可）を作成し、`~/.local/bin/kirocrew`にsymlinkします。`~/.local/bin`（pipx既定・symlink先とも共通）が`PATH`にあることを確認
- **`pip install -e .`**: Pythonのスクリプトディレクトリが`PATH`にあることを確認
- **Docker**: `docker exec kirocrew kirocrew …` で呼び出す

その後 `source ~/.bashrc`（またはシェルを再起動）。

v0.9.0 の `install.md` 200-215行（`99e6253`）によれば、管理対象venvの更新は `crew-venv-<version>` を別に作って `crew-venv-current` リンクを切り替えます（[01_installation.md](01_installation.md)参照）。更新後に `PATH` へ追加するディレクトリ（`~/.kiro/crew-venv/bin` か、versioned／`current` の木か）が変わるかどうかは、公式 `troubleshooting/` ページ・`install.md` のいずれにも明記がなく、**未確認**です。

> **venvパスの食い違いは解消しています（v0.7.2 実測）**。本サイトは以前「公式 `troubleshooting/` ページは `~/.kiro/crew/venv` と案内し、`install.md` の `~/.kiro/crew-venv` と異なる」と注記していました。しかし公式 `troubleshooting/` ページ（`docs_md/troubleshooting.md` 23行）は「else `~/.kiro/crew-venv`. Ensure `~/.local/bin` (pipx default) or `~/.kiro/crew-venv/bin` is on `PATH`」と記述しており、`install.md` 196-198行・公式 `installation/` ページ（`docs_md/installation.md` 59行）と一致します。**この一致は v0.6.0 の時点で既に成立しており**（`~/.kiro/crew/venv` は v0.3.0 時点の公式ページの記述）、本サイトの注記が追随していませんでした。`PATH` には `~/.local/bin` か `~/.kiro/crew-venv/bin` を追加します。
>
> **出典**: <https://kiro.dev/docs/crew/troubleshooting/>（Page updated 表記あり）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
> （参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

### Windows: インストール後に `python: command not found`

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -e . tzdata
python -m kiro_crew gateway
```

`tzdata` が必須です（WindowsはIANAゾーンデータベースを同梱していないため、`zoneinfo.ZoneInfo(...)`がこれなしでは失敗します）。

### Docker: コンテナ起動後にエージェント実行が無効化される

エントリポイントが内部のLinux user-namespaceサンドボックスをプローブし、コンテナランタイムのseccomp/AppArmorポリシー下で失敗した場合です。2つの選択肢があります。

1. **user namespacesを許可**: `--security-opt seccomp=<unshare/cloneを許可するプロファイル>` で再起動。次回起動時にGatewayが再プローブしサンドボックスを有効化
2. **非サンドボックス実行を許容**: `-e KIROCREW_ALLOW_UNSANDBOXED=1` で再起動。エージェントコマンドは内部サンドボックスなしで実行され、コンテナが唯一の隔離境界になる

v0.9.0 の `docker.md` 197-207行・254-311行（`99e6253`）は、原因を次のように説明しています。

- サンドボックスが必要とする `unshare(CLONE_NEWUSER)`・`unshare(CLONE_NEWNS)`・private mount namespace のいずれかを、ランタイムの seccomp または AppArmor が拒否します。**seccomp の挙動は Docker／ランタイムの版により異なり**、近年の既定が unshare を許可する場合もあれば、堅牢化された、または `RuntimeDefault` のプロファイルが `EPERM` を返す場合もあります
- ランタイムの既定 AppArmor プロファイルは、2回の unshare が成功したあとの mount を拒否することがあります（errno 13 `EACCES`）。Kubernetes は seccomp プロファイルを明示しない（2回の unshare は成功する）場合が多く、そこにランタイムの既定 AppArmor プロファイルが組み合わさると mount が失敗する段になる、と説明されています（`docker.md` 205-207・311-322行）
- 起動時のプローブは3手順すべてを実行し、使えるバックエンドが無ければ fail closed のまま、実行を無効にします
- リポジトリは `docker/seccomp/kirocrew-seccomp.json`（Docker の既定の許可リストに `unshare`・`clone`・`mount` の規則を足したもの）を同梱します。`--security-opt seccomp=unconfined` より許可が狭いと説明されています。AppArmor が有効なホスト（Ubuntu・Debian系）では seccomp プロファイルだけでは足りず、`--security-opt apparmor=unconfined` を併用します（AppArmor のコンテナごとの規則だけを外し、seccomp は有効のままとされています）
- メモリ: サブエージェントの扇形展開は `agent.max_subagents`（`0` のときは自動サイズの上限）で抑えられ、明示ピンは最小 3 です。開いているチャットセッション数を直接制限する設定は無いため、コンテナ側の上限を最後の防壁にします（`docker-troubleshooting.md` 449-451・500行）

> **⚠️ 注意**: `-e KIROCREW_ALLOW_UNSANDBOXED=1` と `apparmor=unconfined` は、いずれも隔離を弱める選択です。前者はエージェントのコマンドを内部サンドボックス無しで実行します（`docker.md` 88・186・217行）。

### Windows: デスクトップアプリが起動せず、灰色または空白のウィンドウがすぐ終了する

`kirocrew gateway` とブラウザは正常に動くのに、デスクトップアプリのウィンドウが灰色または空白のまま終了する場合です。v0.9.0 の `windows-install.md` 679-830行「Troubleshooting」節（`99e6253`。この切り分けの項目は v0.8.0 のタグから存在し、v0.7.2 のタグには無く、CHANGELOG/Release 本文は説明していません）は、**Chromium がこのデバイスでサンドボックス化された子プロセスを開始できていない**場合の切り分けを次のように記述しています。

- `%APPDATA%\kirocrew-desktop\logs\gateway-launch.log`（nightly は `kirocrew-desktop-nightly`）に `renderer died` が出ます。終了コードは `-2147483645`（`0x80000003`）が多いですが、別の値でもこの故障を除外できません。この故障は、起動スプラッシュすら描画しない点で、描画後にクラッシュする V8 の異常終了とは区別されます
- **まず、アプリをトレイから完全に終了します**（単一インスタンスのため、起動引数が無視されます）。そのうえで `--no-sandbox` を**1回だけ**付けて起動し、ダッシュボードが読み込めればサンドボックスが原因です。改善しなければサンドボックスは原因ではなく、`KIROCREW_DISABLE_GPU=1`（GPU やレンダリングの失敗向け。恒久化は `setx KIROCREW_DISABLE_GPU 1`）または再インストールを試します
- **`--no-sandbox` を恒久化してはいけません**（レンダラ・GPU・utility の隔離が全子プロセスで外れます。ショートカットの Target を編集すると、更新のたびに引数ごと残ります）
- 修正は、デバイスを管理するエンドポイントセキュリティ製品で Kiro Crew の実行ファイルを**プロセス除外**にすることです。除外すべき対象は、イベントビューアーの Windows ログ > アプリケーションの `AppCrash` エントリで、死んだ子プロセスの障害モジュール名から調べます。サンドボックスのオプトアウトを恒久化する手段は意図的に提供されません
- エージェントの `git`／`cr` が「A process was blocked because malicious behavior was detected」で止まり、アプリのウィンドウは正常な場合は別の事象です。セキュリティコンソールの検知エントリから実行ファイルのパスと検知 ID を調べ、その組に限定した例外を管理者に依頼します

出典: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>（Windows。`git`／`cr` の件は `endpoint-security-blocking-spawned-tools.md` が扱い、同ガイドは原因の説明が macOS／Linux 固有で、例外を絞る手順だけを Windows にも使うよう案内しています）
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## エージェント（kiro-cli）関連

### `AcpTimeoutError: ACP prompt timed out`

エージェントバックエンドがハンドシェイクに応答しませんでした。よくある原因:

1. **`kiro-cli`が未インストール**: ダッシュボードの**Set up Kiro**ページで案内される、または`kirocrew doctor`が欠落を報告。デスクトップアプリは Kiro CLI を同梱するため（v0.8.0〜）、同梱版は `PATH` 上に無く、セットアップ画面が同梱バイナリの絶対パス付きサインインコマンドを表示します。wheel・ソース・Docker・リモートGatewayではGatewayホストへの導入が必要です（[01_installation.md](01_installation.md)参照）
2. **ログインしていない**: `kiro-cli login` を実行
3. **MCP設定が壊れている**: `kirocrew setup --agent-only --clean` でエージェントを最初から再構築
4. **初回起動が遅い**: MCPサーバの初期化に60秒以上かかることがある。待つ

## 未確認事項

- 完全なトラブルシューティング項目（本ページは主要な項目のみを記載。詳細は公式ページを参照）
- 更新後の管理対象venv（`crew-venv-<version>`／`crew-venv-current`）で `PATH` に追加するディレクトリ（上記「`kirocrew: command not found`」の注記参照）

> 以前ここに記載していた venvパスの食い違い（公式 `~/.kiro/crew/venv` と `install.md` `~/.kiro/crew-venv`）は、公式ページも `~/.kiro/crew-venv` に揃ったため**解消**として外しました（上記「インストール後に`kirocrew: command not found`」の注記参照）。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/troubleshooting/>
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

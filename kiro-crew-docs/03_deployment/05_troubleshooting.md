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
**出典**（v0.11.1での再検証: `doctor` のチェック項目・Kiro CLI の同梱の取りやめ・Windows の起動失敗の画面表示・macOS の起動・Dockerのseccomp）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/cli.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/macos-troubleshooting.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/docker.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**（v0.11.1）: <https://kiro.dev/docs/crew/troubleshooting/>（Page updated 2026-09-12）・<https://kiro.dev/docs/crew/installation/>（Page updated 2026-10-20）

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
- **v0.11.1 の `modules/cli.md` 1419-1449行「Doctor Checks」**（`fe6f5be`）は、項目 23・24 を加えて 24 項目になっています。版は、v0.10.0 と v0.11.0 のタグの `modules/cli.md` との比較で絞りました（項番 7・8・23 は v0.10.0 のタグから、項番 16・24 は v0.11.0 のタグから確認できます）。CHANGELOG/Release 本文からの確認は行っていません
  - **ACP runtimes**（項番 23、Linux のみ、助言。v0.10.0）: 生きている ACP runtime の数、実行中の Gateway が所有しているか、バックエンドの CPU 負荷を報告します。セッションより長く生き残って CPU を使い続ける runtime を、`ps` で探す前に名指しするための項目です
  - **Ledgers**（項番 24、助言。v0.11.0）: `kirocrew ledger-sweep` が既定の 30 日の窓で列挙する台帳の件数を 1 行で報告します。台帳があっても doctor は失敗せず、確認用のコマンドを示します
  - **Python environment**（項番 7。v0.10.0）は「Python 3.9+」の文言をやめ、実行中のインタープリタでコア依存（`websockets`・`slack_sdk`・`aiohttp`）が import できるかを検査します。対応するインタープリタの下限は `pyproject.toml` の `requires-python` です
  - **Vector memory**（項番 8。v0.10.0）の対象外プラットフォームの例が `linux/armv7l` と `win32/arm64` になりました（Intel Mac は `macos_x86_64` で対応）
  - **Cron job health**（項番 16。v0.11.0）の自動停止の閾値は `auto_pause_limit()`（既定 5、`0` で無効）になりました
- `kirocrew doctor --bundle` はチェックではなくモードで、ヘルスチェックの代わりに秘匿済みの診断 zip を作り、version と channel を事前入力した GitHub issue のリンクを出します
- doctor は読み取り専用です。完了済みの ledger の掃除は `kirocrew ledger-sweep` で行います

公式 `installation/` ページ（Page updated 2026-10-20）は、`kirocrew doctor` が Crew の選んだ Kiro CLI のバイナリとサインイン状態を報告すると記述しています。v0.8.0〜v0.10.0 のデスクトップアプリは Kiro CLI を同梱していたため、同梱版が選ばれる場合がありました。**v0.11.0 以降のデスクトップアプリは Kiro CLI を同梱せず**、利用者が導入した kiro-cli を検出します（CHANGELOG.md v0.11.0節 154-156行、`install.md` 585-592行。`fe6f5be`）。公式 `installation/` ページは同梱の記述のままで、食い違いがあります（[01_installation.md](01_installation.md) を参照）。

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

### macOS: 再起動後、ログインするまで Gateway が上がらない

自動ログインをオフにした Mac（SSH や Tailscale で使う Mac mini など）で、再起動後にゲートウェイのポート（既定 5476）が応答せず、Mac のログイン画面でログインすると自動で上がる場合です。`kirocrew service install` は**ユーザー単位の LaunchAgent**を設定します。launchd はこれをログインセッションの `gui/<uid>` ドメインに読み込み、このドメインは Mac 自体でログインして初めて生じます。SSH でのログインでは作られません。この動作は仕様どおりです（`macos-troubleshooting.md` 127-159行）。

- SSH から確かめるには `launchctl print "gui/$(id -u)/dev.kirocrew.gateway"` と `lsof -nP -iTCP:5476 -sTCP:LISTEN` を実行します。ログイン前は前者が `gui` ドメインが見つからないと答え、後者は何も出しません
- 対処は、そのユーザーの自動ログインをオンにする（System Settings > Users & Groups）か、再起動のたびに 1 回ログインすることです
- 前回のブートから残った `~/.kiro/crew/gateway.lock` は安全で、削除しません。起動がロックの保持で拒否されたときは、実際に何かのプロセスが保持しています（`lsof ~/.kiro/crew/gateway.lock`）

詳細は [03_running-24-7.md](03_running-24-7.md) の「macOS: ログインするまで Gateway が上がりません」を参照してください。

出典: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/macos-troubleshooting.md>（127-170行）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>（805-808行）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。仕様書・ガイドの差分で確認したもので、CHANGELOG の説明なし）

### Windows: インストール後に `python: command not found`

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -e . tzdata
python -m kiro_crew gateway
```

`tzdata` が必須です（WindowsはIANAゾーンデータベースを同梱していないため、`zoneinfo.ZoneInfo(...)`がこれなしでは失敗します）。補足: v0.11.1 の `windows-install.md` 254-256行は、`setup.cfg` が全プラットフォームで `tzdata` を宣言するため、素の `pip install -e .` でも入ると記述しています（v0.9.0 の記述は Windows マーカー付きでした）。上のコマンドは引き続き有効です。`ZoneInfoNotFoundError` が出たときは `tzdata` を入れます（同 914行）。

### Docker: コンテナ起動後にエージェント実行が無効化される

エントリポイントが内部のLinux user-namespaceサンドボックスをプローブし、コンテナランタイムのseccomp/AppArmorポリシー下で失敗した場合です。2つの選択肢があります。

1. **user namespacesを許可**: `--security-opt seccomp=<unshare/cloneを許可するプロファイル>` で再起動。次回起動時にGatewayが再プローブしサンドボックスを有効化
2. **非サンドボックス実行を許容**: `-e KIROCREW_ALLOW_UNSANDBOXED=1` で再起動。エージェントコマンドは内部サンドボックスなしで実行され、コンテナが唯一の隔離境界になる

v0.9.0 の `docker.md` 197-207行・254-311行（`99e6253`）は、原因を次のように説明しています。

- サンドボックスが必要とする `unshare(CLONE_NEWUSER)`・`unshare(CLONE_NEWNS)`・private mount namespace のいずれかを、ランタイムの seccomp または AppArmor が拒否します。**seccomp の挙動は Docker／ランタイムの版により異なり**、近年の既定が unshare を許可する場合もあれば、堅牢化された、または `RuntimeDefault` のプロファイルが `EPERM` を返す場合もあります
- ランタイムの既定 AppArmor プロファイルは、2回の unshare が成功したあとの mount を拒否することがあります（errno 13 `EACCES`）。Kubernetes は seccomp プロファイルを明示しない（2回の unshare は成功する）場合が多く、そこにランタイムの既定 AppArmor プロファイルが組み合わさると mount が失敗する段になる、と説明されています（`docker.md` 205-207・311-322行）
- 起動時のプローブは3手順すべてを実行し、使えるバックエンドが無ければ fail closed のまま、実行を無効にします
- リポジトリは `docker/seccomp/kirocrew-seccomp.json`（Docker の既定の許可リストに `unshare`・`clone`・`mount` の規則を足したもの。**v0.11.1 では `umount2` の規則も加わっています**。`docker.md` 258-259行、`fe6f5be`。v0.9.0 の `docker.md` に `umount2` の記載はありません）を同梱します。`--security-opt seccomp=unconfined` より許可が狭いと説明されています。AppArmor が有効なホスト（Ubuntu・Debian系）では seccomp プロファイルだけでは足りず、`--security-opt apparmor=unconfined` を併用します（AppArmor のコンテナごとの規則だけを外し、seccomp は有効のままとされています）
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

**v0.10.0 以降の追記（`windows-install.md` の差分で確認したもの。CHANGELOG の説明なし）**: 行番号は v0.11.1（`fe6f5be`）のものです。切り分けの節は 771行以降にあります

- **アプリが原因を画面に表示します**（v0.10.0 から。v0.10.0 タグの `windows-install.md` 763行にあり、v0.9.0 にはありません）。再読み込みを使い切ると、ウィンドウプロセスが何回、どの終了コードで終了したかを示すネイティブのダイアログが出ます。Windows で終了コードが `-2147483645` で、ダッシュボードのページがまだ読み込まれていなければ、このサンドボックスの原因を名指しし、サンドボックスは無効化されていないと述べ、この節を開くボタンが付きます。古い版は黒いウィンドウだけで、ログの行は同じです（786-793行）
- **ブラウザで Gateway を使う別の手段**（v0.10.0 から）: ウィンドウが描画できないホスト（VMware／VirtualBox のゲストへの RDP、VDI、無人サーバ）では、デスクトップアプリ無しで `kirocrew gateway` を動かし、ダッシュボードをブラウザで使えます。手順と、この方法に監視（`service install`・ブート時の起動・再起動）が無い点は [02_windows.md](02_windows.md) の「v0.11.1での変更」を参照してください（`windows-install.md` 732-769行）
- 終了コードが別の値でも、この故障を除外できません。次の起動チェックで確かめます（同 804-807行）

（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## エージェント（kiro-cli）関連

### `AcpTimeoutError: ACP prompt timed out`

エージェントバックエンドがハンドシェイクに応答しませんでした。よくある原因:

1. **`kiro-cli`が未インストール**: ダッシュボードの**Set up Kiro**ページで案内される、または`kirocrew doctor`が欠落を報告。**v0.11.0 以降のデスクトップアプリは Kiro CLI を同梱せず**、利用者が導入した kiro-cli を検出し、見つかるまで **Set up Kiro** ページがインストールとサインインのコマンドを表示します（`install.md` 585-592行）。`BUNDLE_KIRO_CLI=1` でビルドしたアプリだけが同梱版を持ち、その場合は同梱版が `PATH` 上に無いため、ページが同梱バイナリの絶対パス付きサインインコマンドを表示します。**v0.8.0〜v0.10.0 のデスクトップアプリは同梱版を持ち**、同じ表示をしていました。v0.9.0 以前のアプリから更新して自前の kiro-cli を入れていなければ、<https://kiro.dev/cli/> の手順で入れます（サインインは引き継がれます）。wheel・ソース・Docker・リモートGatewayではGatewayホストへの導入が必要です（[01_installation.md](01_installation.md)参照。公式 `installation/` ページは同梱の記述のままで、食い違いがあります）
2. **ログインしていない**: `kiro-cli login` を実行
3. **MCP設定が壊れている**: `kirocrew setup --agent-only --clean` でエージェントを最初から再構築
4. **初回起動が遅い**: MCPサーバの初期化に60秒以上かかることがある。待つ

## 未確認事項

- 完全なトラブルシューティング項目（本ページは主要な項目のみを記載。詳細は公式ページを参照）
- 更新後の管理対象venv（`crew-venv-<version>`／`crew-venv-current`）で `PATH` に追加するディレクトリ（上記「`kirocrew: command not found`」の注記参照）。v0.11.1 の `install.md` 209-221行と公式 `troubleshooting/` ページ（`docs_md/troubleshooting.md` 23行）にも記載がなく、判定できません

> 以前ここに記載していた venvパスの食い違い（公式 `~/.kiro/crew/venv` と `install.md` `~/.kiro/crew-venv`）は、公式ページも `~/.kiro/crew-venv` に揃ったため**解消**として外しました（上記「インストール後に`kirocrew: command not found`」の注記参照）。

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/troubleshooting/>
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

# インストール

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/installation/>（Page updated 表記あり）
**出典**: リポジトリ README「App downloads」節、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（v0.7.0での変更・Node.js要件とvenvパスの再測定・版ピン留めの下限）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.9.0での再検証: 前提要件・導入経路・管理対象venvの更新・デスクトップ版の自動更新）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.9.0）: <https://kiro.dev/docs/crew/installation/>（Page updated 2026-10-20）
**出典**（v0.11.1での再検証: KAS エンジンの取得・デスクトップアプリの kiro-cli 同梱の取りやめ・既定ハーネス・`KIROCREW_INSTALL_KAS`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/harness-parity.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**（v0.11.1）: <https://kiro.dev/docs/crew/installation/>（Page updated 2026-10-20）・<https://kiro.dev/docs/crew/features/agent-backends/>（Page updated 2026-10-12）

---

## 📑 このページの内容

- [4つの導入経路](#4つの導入経路)
- [デスクトップ版の配布物](#デスクトップ版の配布物)
- [チャネル（stable/insider/nightly）](#チャネルstableinsidernightly)
- [前提要件](#前提要件)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [v0.6.0での変更](#v060での変更)
- [v0.4.0での変更](#v040での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## 4つの導入経路

| 経路 | 同梱物 | 特徴 |
|------|-------|------|
| **デスクトップアプリ（Electron）** | Pythonバックエンド一式＋フロントエンド。v0.8.0〜v0.10.0 は **Kiro CLI も同梱**していましたが、**v0.11.0 から同梱しません**（アプリが利用者の導入済みの kiro-cli を検出します。下記「[v0.11.1での変更](#v0111での変更)」。公式 `installation/` ページは同梱のままで、食い違いがあります） | ローカルGatewayを自動起動。ダウンロードしたチャネルで自動更新。SSHトンネル経由でリモートGatewayに接続可能 |
| **ワンライナー（署名済みwheel）** | – | `curl -fsSL https://download.crew.kiro.dev/cli.sh \| sh`。sha256検証済み。cloneもnpmもローカルビルドも不要。**v0.11.1 から、組み込みの KAS エンジンも既定で取得します**（`--no-kas` で省略。下記「[v0.11.1での変更](#v0111での変更)」） |
| **Docker** | – | `linux/amd64`・`linux/arm64` の両方を全タグで提供 |
| **ソースインストール** | 何も同梱しない | Windowsでは署名済みデスクトップインストーラ（v0.4.0〜）と並ぶ導入経路（[02_windows.md](02_windows.md)参照）。`install.md` 10行は「Windows supports both the signed desktop installer and a native Python source install」と記述。**本サイトは以前「Windowsの唯一のサポート経路」と書いていましたが、これは誤りでした**（同ページのデスクトップ版の配布物表・v0.4.0節の記述と矛盾しており、v0.7.2 以前からの誤り） |

## デスクトップ版の配布物

| プラットフォーム | 配布形態 |
|----------------|---------|
| **macOS** | **ユニバーサル `.dmg` 1種**（Apple Silicon＋Intel）。Electronシェルはlipo結合、バックエンドはlipo不可のため`process.arch`で選択される2つの完全なPBSツリーとして同梱 |
| **Linux x86_64** | `.AppImage`（独自のビルド・auto-update feed・SLSA provenance attestationを持つ） |
| **Linux aarch64**（Graviton・Raspberry Pi・ARMラップトップ向け） | `.AppImage`（同上。x86_64とは**独立したレーン**） |
| **Linux desktop packages** | `.deb` / `.rpm`。glibc 2.34以上が必要。古いhostはone-line CLI installを利用 |
| **Windows** | **署名済みinstaller**をstable配布。in-app auto-updateに対応。v0.9.0 の `windows-install.md` 24-39行によれば、インストーラは nightly・insider・stable の**全チャネル**で公開される（Windowsビルドが失敗したreleaseはインストーラ無しで出る）。Authenticode署名済みだが、署名後も新しいファイルハッシュの初回ダウンロードではSmartScreenの警告が出ることがある。詳細は[02_windows.md](02_windows.md)参照 |

`uname -m` で `x86_64` か `aarch64` かを確認できます。

## チャネル（stable/insider/nightly）

すべての導入経路（デスクトップアプリ・CLI・Dockerイメージ）が同じ3チャネルを提供します。

| チャネル | 対象 | ビルド元 | 頻度 |
|---------|------|---------|------|
| **Stable** | 全員（既定） | 十分に長く実績を積んだInsiderビルド | プロモーション時（カレンダー約束なし） |
| **Insider** | 数日〜数週間早く機能を得たいパワーユーザー | リリースブランチのリリース候補タグ | RCごと |
| **Nightly** | 未テストの`main` HEAD | – | 日次 |

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh -s -- --channel insider
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh -s -- --version 0.6.0
```

**`--version` でピン留めできる最小の版は `0.1.2` です。** `--version` は版ごとの署名済みマニフェストを解決し、マニフェストが無いとインストールは失敗します（fail closed）。`0.1.0`・`0.1.1` は公開されていますが署名済みマニフェストを持たないため、**インストーラではインストールできません**（バックフィルもされません）。ロールバック手順書が `0.1.0`・`0.1.1` を指定している場合は `0.1.2` 以降に変えるか、`--version` を外して現行の `stable` を使います（`docs/guides/install.md` 172-193行）。**本サイトは以前、例として `--version 0.1.0` を掲載していました**（v0.6.0 の `install.md` 133行の例に従っていた）。v0.7.2 の `install.md` 160行の例は `--version 0.6.0` です。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - 公式 `installation/` ページ（`docs_md/installation.md` 62行。v0.9.0・Page updated 2026-10-20）は「Pin an exact version」の例として `--version 0.1.0` を掲載しています
> - リポジトリの `docs/guides/install.md` 172-177行（`99e6253`）は「`0.1.0` and `0.1.1` … cannot be installed by the installer」と記述しています

インストーラはwheelのダイジェストを署名済みマニフェストと照合し、不一致なら**インストールを拒否**します（チェックサムのみのフォールバックはありません）。`pipx`が使えればそれを使い、無ければ管理対象venv（`~/.kiro/crew-venv`。`KIROCREW_VENV`で変更可）を**データホームの外**に作成します（ホーム全体を操作する処理が動いているインタープリタを削除しないため）。選択したチャネルは `~/.kiro/crew/channel` に記録されます。

**管理対象venvの更新（v0.9.0 の `install.md` 200-215行）**: `kirocrew update`・アプリ内の承認済み更新・Gatewayの自動更新は、新版ごとに隣へ `crew-venv-<version>`（依存込みで約350 MiB）を作り、`crew-venv-current` リンクを切り替えます。更新後に残すのは、現行の木・1つ前の木（復旧先）・実行中の `kirocrew` プロセスが使っている木で、それより古いものは削除されます。インストーラの直接実行は、固定の `crew-venv` をその場で作り直します。`~/.kiro/crew-venv` というパス自体の記述は変わっていません。

## 前提要件

| 要件 | 用途 | 下限 |
|------|------|------|
| **Python** | バックエンド | **`>= 3.12`**（v0.6.0で3.10から引き上げ。`pyproject.toml` の `requires-python`） |
| **Node.js + npm** | ダッシュボードのビルド | リポジトリの `install.md` 40行は **`>= 22.12.0`**（`website/package.json` の `engines`。Node 24 LTS推奨。ビルド時のみ必要。事前ビルド済みwheel/DMG/AppImage/`.deb`/`.rpm`の利用者はNode不要）。**公式 `installation/` ページ（16・75行）は「Node.js 22+」のままで、書き分けが生じています**（下記の注記参照）。`kirocrew doctor` は `node` が 22.12.0 未満だと失敗（exit 1）として報告します（`modules/cli.md` 1425行。v0.9.0 では 1194行）。**本サイトは以前 `20 \|\| >= 22` と記載していましたが、これは v0.3.0〜v0.4.1 時点の `install.md` 40行の値で、v0.6.0 の `install.md` 40行は既に `>= 22` でした**（下記「[v0.3.0での変更](#v030での変更)」の注記参照） |
| **Kiro CLI（`kiro-cli`）** | LLM駆動 | **v0.11.0 以降、デスクトップアプリは Kiro CLI を同梱しません**。アプリが利用者の導入済みの kiro-cli を検出し、見つかるまで **Set up Kiro** ページがインストールとサインインのコマンドを表示します（CHANGELOG.md v0.11.0節 154-156行、`install.md` 585-592行）。`BUNDLE_KIRO_CLI=1` を付けてビルドしたアプリだけが、アプリ内に kiro-cli を持ちます。wheel・ソース・Docker・リモートGatewayでは、従来どおりGatewayホストへの導入が必要です。**既定ハーネスが KAS になった v0.11.0 以降も、既定の KAS が kiro-cli を必要とするか**は出典間で記述が分かれます（下記「[v0.11.1での変更](#v0111での変更)」）。Crewは、絶対パスの `KIROCREW_KIRO_BIN` が指定されていればそれを最優先で選びます。`kirocrew doctor` は選ばれたバイナリとサインイン状態を報告します。**v0.8.0〜v0.10.0 のデスクトップアプリは動作確認済みの Kiro CLI を同梱し、同梱版をシステム／`PATH` 上のものより先に使っていました**（公式 `installation/` ページ17・21-25行は現在もこの記述です） |

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（Node.jsの下限）
> - リポジトリ `docs/guides/install.md` 40行・`docs/guides/windows-install.md` 205行・`docs/system-specs/modules/cli.md` 1425行（`fe6f5be`。v0.9.0 の `99e6253` では `windows-install.md` 191行・`cli.md` 1194行）: `22.12.0`（`cli.md` は `MIN_NODE_VERSION` ＝ 22.12.0 を `doctor` が検査すると記述）
> - 公式 `installation/` ページ（`docs_md/installation.md` 16・75行。Page updated 2026-10-20）: 「Node.js 22+」
>
> v0.7.2 の `install.md` 40行は `>= 22` で公式と一致していました（v0.8.0 の `install.md` にも `22.12.0` の記載はありません）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（デスクトップアプリがKiro CLIを同梱するか。v0.11.0 で記述の組み合わせが変わりました）
> - 公式 `installation/` ページ（`docs_md/installation.md` 17・21-25行。Page updated 2026-10-20）: デスクトップアプリは動作確認済みの Kiro CLI を同梱し、`KIROCREW_KIRO_BIN` が無ければ同梱版をシステム／`PATH` 上のものより先に使う
> - CHANGELOG.md v0.11.0節 154-156行・`docs/guides/install.md` 585-592行（`fe6f5be`）: アプリは kiro-cli の同梱をやめ、利用者が導入したものを検出する。同梱されるのは `BUNDLE_KIRO_CLI=1` でビルドしたアプリだけ
> - 公式ページ内にも、157行の Info 注記（デスクトップアプリが「guides kiro-cli installation and sign-in from the app itself」）と、17・21-25行の同梱の記述があります
> - リポジトリ `README.md` 51-52行と `windows-install.md` 93-94行（Finish ページ）は、利用者が別に kiro-cli を導入しサインインする前提の記述で、v0.11.0 の記述とは矛盾しません。v0.9.0 まではこれらが公式・CHANGELOG（同梱）との食い違いの当事者でした

出典（Node.js要件。v0.11.1 でも `22.12.0` のまま）: `docs/guides/install.md` 40行・`docs/guides/windows-install.md` 205行（v0.9.0 では 191行）・`docs/system-specs/modules/cli.md` 1425行（v0.9.0 では 1194行）、公式 `installation/` ページ（`docs_md/installation.md` 16・75行）。
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1。公式ページは Page updated 2026-10-20）
出典（Kiro CLIの同梱）: 公式 `installation/` ページ（`docs_md/installation.md` 17・21-25行）、CHANGELOG.md v0.11.0節 154-156行、`docs/guides/install.md` 585-592行、`README.md` 51-52行、`docs/guides/windows-install.md` 93-94行。
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
出典（v0.8.0〜v0.10.0 の同梱の記述）: CHANGELOG.md v0.8.0節 214-218・666-668行（`99e6253`）、`docs/guides/install.md` 573-577行（`99e6253`）。
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.11.1での変更

v0.10.0・v0.11.0・v0.11.1 のいずれにも CHANGELOG の「Before you upgrade」節はありません。以下のうち、各項目の版は見出しに明記しています。

### インストーラが KAS エンジンを既定で取得します（v0.11.1）

- ワンライナー（`cli.sh`）と `install.sh` は、Kiro Crew を入れたあとに **`kirocrew kas install`** を実行し、この版がピン留めする KAS エンジン（プラットフォームごとに約 55〜70 MB）を既定でダウンロードします。取得に失敗してもインストールは成功し、再試行するコマンドを表示します
- **`--no-kas`**（または環境変数 **`KIROCREW_INSTALL_KAS=0`**）で取得を省けます。インストーラは取得するだけで、`agent.kas_bundle` はオンになりません
- 他の方法で入れた場合や再試行は、`kirocrew kas install` を自分で実行します。ソースビルドもこのコマンドを自動では実行しません（`windows-install.md` 262-274行）
- **`KIROCREW_INSTALL_KAS` は `install.md` 163行にだけあり、CHANGELOG には書かれていません**。`--no-kas` は CHANGELOG に書かれています

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh -s -- --no-kas
```

出典: `docs/guides/install.md` 159-168・595-605行、`docs/system-specs/modules/cli.md` 384行
出典: CHANGELOG.md v0.11.1節 45-47行（`fe6f5be`）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### 組み込み KAS エンジン経路（v0.10.0 導入、`agent.kas_bundle` は既定オフ）

- v0.10.0 で、Settings → Agent Harness の「Use the built-in KAS engine」（既定オフ）が加わりました。この版がピン留めしたエンジンを Crew 自身が入れて KAS を動かすため、そのために kiro-cli を導入する必要がなくなる経路です（CHANGELOG.md v0.10.0節 299-301行）
- v0.11.0 で、この切り替えは Settings → Developer → Feature Previews の「**Run KAS on Kiro Crew's own engine**」に移りました（CHANGELOG.md v0.11.0節 154-157行）。`install.md` 595-605行は、スイッチが**全プラットフォームで既定オフ**で、シャドウテスト中の扱いであり、何も自動ではオンにしないと記述しています
- 試すには、そのスイッチをオンにするか `kirocrew config set agent.kas_bundle true` を実行して再起動します。サインインは Settings → Agent Harness → KAS の **Kiro sign-in** カードで行い、`kiro-cli login` は使いません
- デスクトップアプリはエンジンをアプリ内に同梱します（ビルド時の `BUNDLE_KAS=1` が既定）。ダウンロードは要りません

出典: `docs/guides/install.md` 595-605行（`fe6f5be`）、CHANGELOG.md v0.10.0節 299行・v0.11.0節 154-157行
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### デスクトップアプリは kiro-cli を同梱しなくなりました（v0.11.0）

- 出荷されるデスクトップアプリは kiro-cli を持ちません。アプリは利用者が導入した kiro-cli を検出し、見つかるまで **Set up Kiro** ページがインストールとサインインのコマンドを表示します（CHANGELOG.md v0.11.0節 154-156行、`install.md` 585-592行）
- `BUNDLE_KIRO_CLI=1` でビルドしたアプリだけが kiro-cli をアプリ内に持ちます。その場合の kiro-cli はシェルの `PATH` 上に無く、ページは同梱バイナリの絶対パス付きのログインコマンドを表示します
- **v0.9.0 以前のアプリから更新し、自前の kiro-cli を入れていない場合**は、公式サイト（<https://kiro.dev/cli/>）の手順で入れます。サインインは引き継がれます（同梱版と導入版が同じアカウントストアを読むため。`install.md` 585-592行）

出典: `docs/guides/install.md` 583-592行（`fe6f5be`）、CHANGELOG.md v0.11.0節 154-156行
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### 既定ハーネスは KAS です（v0.11.0）

保存した選択のない新規インストールの既定ハーネスは、v0.11.0 から KAS です（`harness-parity.md` 89行、CHANGELOG.md v0.11.0節 151-153行。明示した Kiro CLI の選択は維持されます）。KAS を kiro-cli なしで動かせるかについて、出典の表現が分かれています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（既定ハーネスと kiro-cli の要否）
> - CHANGELOG.md v0.11.0節 58-59行・154-157行（`fe6f5be`）: 新規インストールは KAS で始まり、KAS は「no longer needs kiro-cli」
> - `docs/guides/install.md` 47-52行: 見出しは「Default agent backend: kiro-cli」で、「a fresh configuration uses Kiro」。595-605行は、kiro-cli が要らない組み込みエンジン経路を、スイッチをオンにした場合の代替として記述
> - `docs/guides/windows-install.md` 203行: `kiro-cli` は「既定の KAS ハーネスも中継する」ため、別途導入してサインインする
> - 公式 `features/agent-backends/` ページ24行（Page updated 2026-10-12）: Kiro CLI を「Default backend」と記述

出典: 上記の各ファイルの行（`fe6f5be`）、`docs/system-specs/modules/harness-parity.md` 89行
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

### その他

- **wheel の extras**: `voice` の依存の下限が `amazon-transcribe>=0.6.3,<1` になりました（v0.9.0 の記載は `>=0.6`。`install.md` 436行）。ほかの extras の記述は変わっていません。本内容は仕様書・ガイドの差分で確認したもので、CHANGELOG には説明がありません
- **README の「App downloads」表**: macOS・Windows・Linux（x86_64・aarch64 の `.deb`・`.rpm`・AppImage）の Stable・Insider・Nightly への直リンクに拡張されました（`README.md` 54-77行）。Linux デスクトップパッケージの手順は `install.md` の「Installing a Linux desktop package」節に案内されています。CHANGELOG には説明がありません
- 前提要件の Python（`>= 3.12`）、Node.js（`>= 22.12.0`）、`--version` でピン留めできる最小の版（`0.1.2`）、管理対象 venv の記述は v0.9.0 から変わっていません（`install.md` 39-40・188・201・209-221行）

出典: `docs/guides/install.md`、`README.md`（`fe6f5be`）
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）

## v0.9.0での変更

v0.9.0 に「Before you upgrade」節はありません。以下のうち、CHANGELOG.md v0.9.0節が説明するのは最初の項目だけです。それ以外は **v0.9.0 タグの `docs/guides/install.md`・`windows-install.md` で確認した内容で、CHANGELOG/Release 本文は説明していません**（v0.8.0 タグの `install.md` には、`22.12.0`・`crew-venv-current`・「Install app updates automatically」・`KIROCREW_INSTALL_PLAIN` の記載が無いことを確認済み）。

- **インストーラの進捗表示**: 端末ではwheelのダウンロードにcurlの進捗バーが出て、遅い手順（venv作成・pip）は1行のライブ進捗を描きます。**`KIROCREW_INSTALL_PLAIN=1`** で止められ、パイプやログへの出力はこの状態になります（ダウンロードは無音、遅い手順は30秒ごとに `still running`、各手順の終わりに `done` を1行出す）。CHANGELOG.md v0.9.0節 168-172行は「The installer shows live progress, a Windows installer exit 17 names its cause」と記述しています
- **Node.jsの下限が `22.12.0` と書かれた**: リポジトリ側の記述です（公式 `installation/` ページは「22+」のまま）。上記「[前提要件](#前提要件)」の食い違い注記を参照してください
- **管理対象venvの更新方式**: 新版ごとに `crew-venv-<version>` を作って `crew-venv-current` を切り替えます（上記「[4つの導入経路](#4つの導入経路)」節末尾の説明。`install.md` 200-215行）
- **`KIROCREW_ALLOW_SOURCE_BUILDS=1` の説明が変わりました**: 下記「[v0.7.0での変更](#v070での変更)」の該当項目を参照してください（`install.md` 259-268行）
- **デスクトップ版の自動更新**（`install.md` 470-485行）: 既定では新しいreleaseをバックグラウンドでダウンロードし、アプリの終了時に導入します（ウィンドウを閉じるとトレイに隠れるだけです）。About ページの **Install app updates automatically** をオフにすると、更新ごとに確認してからダウンロードします。DMGや読み取り専用ボリュームからの起動、macOSのtranslocatedコピー、書き込めないディレクトリのAppImage、不明なパッケージ形式、`EXTERNALLY-MANAGED`、非パッケージビルドではupdaterが無効で、About がその旨を表示します。ローカルビルドのアプリはstableチャネルより先の版として刻印され、新しいreleaseが出るまで更新されません。AppImageは `PATH` に `kirocrew` ランチャを置きません
- **Windows**: デスクトップ版のインストーラの現状は [02_windows.md](02_windows.md) を参照してください

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/docker.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.9.0節 168-172行（`99e6253`）

## v0.8.0での変更

v0.8.0 に「Before you upgrade」節はありません。

- **デスクトップアプリがKiro CLIを同梱**（**v0.11.0 で同梱をやめました**。上記「[v0.11.1での変更](#v0111での変更)」。以下は v0.8.0 当時の内容）: macOS・Linux・Windowsの新規インストールは、サインインだけでエージェントが動きます。セットアップ画面は、同梱版の絶対パス付きサインインコマンドを表示します（CHANGELOG.md v0.8.0節 214-218行）。同梱版は kiro-cli 2.27.1 です（同 666-668行）
- **Kiro CLIの選択順**（v0.9.0 時点の公式ページ・`install.md` の記述。v0.11.0 以降は `install.md` が同梱を前提にしていません）: 絶対パスの `KIROCREW_KIRO_BIN` が最優先、次にデスクトップアプリの同梱版、その次にシステム／`PATH` 上のものです（公式 `installation/` ページ21-25行、`install.md` 573-577行）。wheel・ソース・Docker・リモートGatewayでは、従来どおりGatewayホストにKiro CLIが必要です
- **wheel の extras の記載**（`install.md` 428-437行・594行、`docker.md` 3-8行）: `voice-aws`（`boto3`＋`amazon-transcribe`）、`voice`（`voice-aws`＋`pywhispercpp`）、`whatsapp`（`neonize`）、`feishu`（`lark-oapi`）。`kirocrew setup --whatsapp` はWhatsAppの任意依存とペアリング状態を確認してから有効化します。Dockerの標準イメージはMicrosoft Teams・Feishu・WhatsAppの依存を含まず、iMessageはmacOS専用でイメージでは使えません。**本内容は v0.8.0 タグの仕様書で確認したもの（v0.7.2 の `install.md` には `voice-aws`・`neonize`・`lark-oapi`・`--whatsapp` の記載が無い）で、CHANGELOG/Release 本文は extras 一覧としては説明していません**

出典: CHANGELOG.md v0.8.0節 214-218・666-668行（`99e6253`）、公式 `installation/` ページ（Page updated 2026-10-20）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.7.0での変更

v0.7.x に「Before you upgrade」節はありません。以下は機能追加・既定動作の変更です。

### ソースチェックアウトの更新チェックが定期化

- Gatewayは起動時に加えて**12時間ごと**に新しい版を確認します（設定キー `auto_update`、既定 `true`）
- 自動適用は、まず**新規ターンの受付を止め**、進行中のターン・スケジュール実行・サブエージェント・Task Runnerステップ・ワークフローが落ち着くまで待ってから適用します。**作業中の処理はキャンセルされず、更新のほうが延期されます**

出典: CHANGELOG.md v0.7.0節 148-150行（`c67c506`）、公式 `installation/` ページ（`docs_md/installation.md` 121行「Source checkouts」）、公式 `configuration/` ページ（`auto_update` 行）。

### 更新前の Python 要件チェック

- 更新先リビジョンの `requires-python` を現在のvenvのインタープリタが満たすかを、**チェックアウトを動かす前に**検査します。満たさない場合は、そのvenvとインタープリタのパスを示して**拒否**します。3.12未満のPythonは無条件に却下されます
- 未コミットの変更がある・分岐したチェックアウトも、リセットせずに拒否します

出典: CHANGELOG.md v0.7.0節 151-153行（`c67c506`）、公式 `installation/` ページ（`docs_md/installation.md` 123行）、`docs/system-specs/modules/cli.md` 234行（`kirocrew update`）。

### インストーラは事前ビルドwheelのみを使う

- 依存パッケージは**事前ビルドwheelのみ**（`pip --only-binary=:all:`）から入れるため、ホストにCコンパイラや `-dev` ヘッダは不要です
- ホストで動くwheelをどのリリースも公開していない場合（glibcが古い・アーキテクチャ向けwheelが無い）は、ビルド開始前に**プラットフォームとパッケージ名を示して中止**します
- ツールチェーンとヘッダがあるホストでは **`KIROCREW_ALLOW_SOURCE_BUILDS=1`** でソースビルドに戻せます。**この指定は記憶されません**

出典: CHANGELOG.md v0.7.0節 461-464行（`c67c506`）、`docs/guides/install.md` 232-248行（`c67c506`）。

> **v0.9.0 での記述の変更**: v0.7.2 の `install.md`（232-248行）は、更新エンジンがGatewayの動く環境からこの変数を読むため、`kirocrew service install` で常駐させている場合はサービスユニット側にも設定が必要と記述していました。v0.9.0 の `install.md` 259-268行は逆で、更新中に依存パッケージをコンパイルするには、ツールチェーンが `PATH` にあるシェルから `KIROCREW_ALLOW_SOURCE_BUILDS=1 kirocrew update` を実行します（そのコマンドはシェル自身の環境でビルドします）。Gatewayの自動更新と承認済み更新のビルド手順は、信頼されたシステム `PATH` だけで動きます。
> （参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - CHANGELOG.md v0.7.0節 1176行（`99e6253`。v0.7.2 のタグでは 463-464行）は「the Linux AppImage starts on distributions without the older FUSE library」と記述しています
> - `docs/guides/install.md` 136行・508行（`99e6253`。v0.7.2 のタグでは 133行・444行）は AppImage について「needs FUSE present」と記述しています

### 版のピン留めは `0.1.2` 以降

`--version` でピン留めできる最小の版は `0.1.2` です（上記「[チャネル](#チャネルstableinsidernightly)」参照）。本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません（`docs/guides/install.md` 172-193行）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## v0.6.0での変更

### 破壊的変更: Python 3.12 が下限

**3.10・3.11 のホストは、インストールまたは更新の前に上げる必要があります。** システムのパッケージマネージャに 3.12 がない場合は、各インストーラが自分で 3.12 を用意します。

出典: `docs/guides/install.md` 39行（`requires-python`）。

### 破壊的変更: インストーラが自前の Python を持ち込む

次のインストーラは、システムの Python ではなく**ピン留めされた CPython** を用意します。

```bash
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh
```

意図してシステム側の Python に対してビルドする場合は **`--system-python`** を渡します。環境変数 `KIROCREW_MANAGED_PYTHON=0` でもシステムの Python 3.12+ を使う経路があります（`docs/guides/install.md` 156・160・171行）。

### Kiro CLI が古いときのゲート

セットアップは、エージェントセッションに対して古すぎる Kiro CLI を検出します（起動時のゲート）。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## v0.4.0での変更

Windowsは署名済みinstallerとin-app auto-updateをstableチャネルで提供し、Linux desktopは`.deb`/`.rpm`を提供します。これはv0.4.0 CHANGELOGの記述であり、旧版の「Windows desktop未配布」は現行状況としては用いません。v0.9.0 の `windows-install.md` 24-39行は、インストーラが stable だけでなく nightly・insider を含む全チャネルで公開されると記述しています（[02_windows.md](02_windows.md)参照）。

## v0.3.0での変更

### 破壊的変更: Node.js 22が最小要件（24 LTS推奨）

**v0.3.0からNode.js 22が最小要件になりました。Node 20でのインストールは拒否されます。**

**この値の出典は、当時の「前提要件」表の出典とは異なります。** 当時の表のNode.js要件（`20 || >= 22`）は`docs/guides/install.md` 40行（`website/package.json`の`engines`）に基づいていましたが、**この記述は`21584ea`では更新されていませんでした**。v0.3.0の実際の下限は以下の一次情報で確認できます。

| 出典（`21584ea`） | 記述 |
|---|---|
| CHANGELOG.md v0.3.0節 **14行** | 「**Node.js 22 is now the minimum** (24 LTS recommended). A Node 20 install is ...」 |
| `src/kiro_crew/constants.py` **33行** | `MIN_NODE_MAJOR = 22`。コメントは「22 is the oldest non-EOL line the frontend bundler supports（`ensure-node.sh`はより細かい22.12の下限を強制し、`.nvmrc`は推奨の24 LTSをピン留めする）」 |
| `install.sh` **48行** | `NODE_MIN_MAJOR=22`。コメントは「Minimum Node major the frontend build actually supports」。**インストーラは検出段階でこの値を参照し、下限未満のnodeが既にある場合はそれを使わずインストールのはしごに進みます**（263行「Node.js ... is below the supported floor (>= $NODE_MIN_MAJOR) — installing a supported Node…」） |

**⚠️ 以下は `21584ea`（v0.3.0）時点の記録です。** 公式`installation/`ページの「Node.js 18+」と`install.md`の「`20 || >= 22`」の食い違いは`21584ea`では解消されておらず、そこに**インストーラ実体の22という第3の値**が加わった状態でした。

> **この3値の食い違いは解消しています（v0.7.2 実測）。** 3つの記述はすべて「22」で一致しました。
>
> | 出典 | v0.3.0（`21584ea`） | v0.6.0（`8575209`） | v0.7.2（`c67c506`） |
> |---|---|---|---|
> | 公式 `installation/`（`docs_md/installation.md` 16行） | Node.js 18+ | **Node.js 22+**（24 LTS推奨） | **Node.js 22+**（24 LTS推奨） |
> | `docs/guides/install.md` 40行 | `20 \|\| >= 22` | **`>= 22`**（Node 24 LTS推奨） | **`>= 22`**（Node 24 LTS推奨） |
> | インストーラ実体（`install.sh` 48行 `NODE_MIN_MAJOR=22`・`constants.py` 33行 `MIN_NODE_MAJOR = 22`） | 22 | 未再測定 | 未再測定 |
>
> 公式ページと `install.md` は **v0.6.0 の時点で既に22に揃っていました**。本サイトの表と注記が追随していませんでした。インストーラ実体（`install.sh`・`constants.py`）は、本サイトの v0.6.0・v0.7.2 のリポジトリスナップショットにソースコードが含まれないため再測定していません。
>
> **v0.9.0 で、この一致は再び崩れました。** v0.9.0 の `install.md` 40行は `>= 22.12.0`、公式 `installation/` ページ（16・75行）は「22+」のままです（上記「[前提要件](#前提要件)」の食い違い注記を参照）。v0.9.0 のインストーラ実体は未再測定です。

### デスクトップ版のプラットフォームに関するCHANGELOGの記載

CHANGELOGは以下2件を新機能として挙げています。**ただし上記「[デスクトップ版の配布物](#デスクトップ版の配布物)」表の内容と照らすと、いずれも本サイトが`64060f3`時点で既に記録していた内容と重なります。**

| CHANGELOGの記載 | 本サイトの既存記述との関係 | CHANGELOG行 |
|---|---|:---:|
| **Linux ARM64** — ネイティブaarch64デスクトップビルド。**アーキテクチャチェック付きで公開**され、誤ったものをダウンロードすることがない | 既存表に「**Linux aarch64**（Graviton・Raspberry Pi・ARMラップトップ向け）`.AppImage`（x86_64とは独立したレーン）」として記載済み。**新規の情報は「アーキテクチャチェック付きで公開される」という点** | 114行 |
| **Windowsがfirst-class build** — macOS・Linuxと**同じターゲット**になり、独自のインストールガイドを持つ | 既存表は「**Windows: デスクトップ版は未配布**。ソースインストールを実行しブラウザでダッシュボードを開く」と記載。**`21584ea`の`windows-install.md` 18〜30行は引き続き「CI artifact only ... not yet published to the download CDN」「Signing wired but not yet active ... installers are still unsigned」と述べており、配布状況は変わっていません** | 116行 |

**⚠️ 「first-class build」はビルドターゲットとしての扱いを指し、ダウンロードCDNでの配布や署名の有効化を意味しません。** 本サイトは既存表の「デスクトップ版は未配布」という記述を**変更しません**（一次情報で配布開始を確認できないため）。Windowsの詳細は [02_windows.md](02_windows.md) を参照してください。

### リリースチャネルの切替が再インストール不要になった

**AboutからStable・Insider・Nightlyの間を移動でき、更新後にGatewayがその場で再起動します。**

出典: CHANGELOG.md v0.3.0節 120行（`21584ea`）「**Change release channel without reinstalling** — Move between Stable, Insider, and Nightly from About, and the gateway restarts in place after an update」。**3チャネルの構成自体は変わっていません**（[02_update/02_release-policy.md](../02_update/02_release-policy.md)参照）。

### その他

- **システム全体のホットキー** — macOSは`Cmd+Shift+K`、それ以外は`Alt+Shift+K`でダッシュボードを呼び出せます。再設定・無効化も可能（118行）
- **tailnetへの公開** — `kirocrew tailnet up`でダッシュボードをTailscaleネットワークに載せ、他のデバイスから到達できます（122行。[04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)参照）
- **ダッシュボードからのcloud crew起動** — リモートEC2のプロビジョニング（デバイスサインインを含む）が、閉じてはいけないCLIセッションではなく**再起動可能なジョブ**として実行されます。`--subnet`でプライベートサブネットに固定できます（124行）
- **GNOMEでのタイトルバー重複の解消** — 独自装飾を描くデスクトップで、重複していたネイティブタイトルバーがなくなりました（126行）

## 未確認事項

- インストーラ実体のNode.js下限（`install.sh` の `NODE_MIN_MAJOR`・`constants.py` の `MIN_NODE_MAJOR`）の v0.11.1 での値（`src/` の解析は行っていないため未再測定。v0.3.0 時点は22。ドキュメント側では `install.md` 40行・`cli.md` 1425行が `22.12.0`、公式 `installation/` ページが「22+」で食い違っています。**継続**）
- AppImage の FUSE 要件（CHANGELOG 1577行と `install.md` 136・518行の記述差。v0.11.1 でも**継続**。上記「[v0.7.0での変更](#v070での変更)」参照）
- デスクトップアプリがKiro CLIを同梱するか（公式 `installation/` ページ（Page updated 2026-10-20）と、CHANGELOG v0.11.0節・`install.md` 585-592行の記述差。**継続**。v0.9.0 の `README.md`・`windows-install.md` との食い違いからは当事者が入れ替わりました。上記「[前提要件](#前提要件)」参照）
- 既定ハーネスが KAS の新規インストールで kiro-cli が要るか（CHANGELOG v0.11.0節と `install.md` 47-52・595-605行・`windows-install.md` 203行の記述差。公式 `features/agent-backends/` ページは Kiro CLI を既定と記述。**v0.11.0 で生じた新規の食い違い**。上記「[v0.11.1での変更](#v0111での変更)」参照。裁定しない）
- 公式 `installation/` ページの `--version 0.1.0` の例と `install.md` の「`0.1.0` はインストーラで入れられない」記述の差（**継続**。上記「[チャネル](#チャネルstableinsidernightly)」参照）

> 以前ここに記載していた2件は**解消**したため外しました。
> - **Node.jsの下限**: 公式`installation/`ページ・`install.md` 40行とも「22」で一致していました（v0.6.0〜v0.7.2。上記「[v0.3.0での変更](#v030での変更)」の注記参照）。**v0.9.0 で `install.md` 側が `22.12.0` に変わり、再び書き分けが生じています**（上の未確認事項）
> - **managed venvのパス**: 公式`installation/`ページ（`docs_md/installation.md` 59行）・公式`troubleshooting/`ページ（`docs_md/troubleshooting.md` 23行）・`install.md` 196-198行のすべてが `~/.kiro/crew-venv` で一致（v0.6.0 で既に一致。`~/.kiro/crew/venv` は v0.3.0 時点の公式ページの記述）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/installation/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
- Windows: [02_windows.md](02_windows.md)
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

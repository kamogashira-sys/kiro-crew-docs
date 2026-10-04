# インストール

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/installation/>（Page updated 表記あり）
**出典**: リポジトリ README「App downloads」節、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（v0.7.0での変更・Node.js要件とvenvパスの再測定・版ピン留めの下限）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

---

## 📑 このページの内容

- [4つの導入経路](#4つの導入経路)
- [デスクトップ版の配布物](#デスクトップ版の配布物)
- [チャネル（stable/insider/nightly）](#チャネルstableinsidernightly)
- [前提要件](#前提要件)
- [v0.7.0での変更](#v070での変更)
- [v0.6.0での変更](#v060での変更)
- [v0.4.0での変更](#v040での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## 4つの導入経路

| 経路 | 同梱物 | 特徴 |
|------|-------|------|
| **デスクトップアプリ（Electron）** | Pythonバックエンド一式＋フロントエンド | ローカルGatewayを自動起動。ダウンロードしたチャネルで自動更新。SSHトンネル経由でリモートGatewayに接続可能 |
| **ワンライナー（署名済みwheel）** | – | `curl -fsSL https://download.crew.kiro.dev/cli.sh \| sh`。sha256検証済み。cloneもnpmもローカルビルドも不要 |
| **Docker** | – | `linux/amd64`・`linux/arm64` の両方を全タグで提供 |
| **ソースインストール** | 何も同梱しない | Windowsの唯一のサポート経路（[02_windows.md](02_windows.md)参照） |

## デスクトップ版の配布物

| プラットフォーム | 配布形態 |
|----------------|---------|
| **macOS** | **ユニバーサル `.dmg` 1種**（Apple Silicon＋Intel）。Electronシェルはlipo結合、バックエンドはlipo不可のため`process.arch`で選択される2つの完全なPBSツリーとして同梱 |
| **Linux x86_64** | `.AppImage`（独自のビルド・auto-update feed・SLSA provenance attestationを持つ） |
| **Linux aarch64**（Graviton・Raspberry Pi・ARMラップトップ向け） | `.AppImage`（同上。x86_64とは**独立したレーン**） |
| **Linux desktop packages** | `.deb` / `.rpm`。glibc 2.34以上が必要。古いhostはone-line CLI installを利用 |
| **Windows** | **署名済みinstaller**をstable配布。in-app auto-updateに対応 |

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
> - 公式 `installation/` ページ（`docs_md/installation.md` 55-56行）は「Pin an exact version」の例として `--version 0.1.0` を掲載しています
> - リポジトリの `docs/guides/install.md` 172-176行は「`0.1.0` and `0.1.1` … cannot be installed by the installer」と記述しています

インストーラはwheelのダイジェストを署名済みマニフェストと照合し、不一致なら**インストールを拒否**します（チェックサムのみのフォールバックはありません）。`pipx`が使えればそれを使い、無ければ管理対象venv（`~/.kiro/crew-venv`。`KIROCREW_VENV`で変更可）を**データホームの外**に作成します（ホーム全体を操作する処理が動いているインタープリタを削除しないため）。選択したチャネルは `~/.kiro/crew/channel` に記録されます。

## 前提要件

| 要件 | 用途 | 下限 |
|------|------|------|
| **Python** | バックエンド | **`>= 3.12`**（v0.6.0で3.10から引き上げ。`pyproject.toml` の `requires-python`） |
| **Node.js + npm** | ダッシュボードのビルド | **`>= 22`**（Node 24 LTS推奨。ビルド時のみ必要。事前ビルド済みwheel/DMG/AppImage/`.deb`/`.rpm`の利用者はNode不要）。**本サイトは以前 `20 \|\| >= 22` と記載していましたが、これは v0.3.0〜v0.4.1 時点の `install.md` 40行の値で、v0.6.0 の `install.md` 40行は既に `>= 22` でした**（v0.7.2 も同じ。下記「[v0.3.0での変更](#v030での変更)」の注記参照） |
| **`kiro-cli`** | LLM駆動 | 必須 |

出典（Node.js要件）: `docs/guides/install.md` 40-45行（`c67c506`）、公式 `installation/` ページ（`docs_md/installation.md` 16・69行「Node.js 22+」）。

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
- ツールチェーンとヘッダがあるホストでは **`KIROCREW_ALLOW_SOURCE_BUILDS=1`** でソースビルドに戻せます。**この指定は記憶されません**。更新エンジンはGatewayが動く環境からこの変数を読むため、`kirocrew service install` で常駐させている場合はサービスユニット側にも設定が必要です

出典: CHANGELOG.md v0.7.0節 461-464行（`c67c506`）、`docs/guides/install.md` 232-248行（`c67c506`）。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - CHANGELOG.md v0.7.0節 463-464行は「the Linux AppImage starts on distributions without the older FUSE library」と記述しています
> - `docs/guides/install.md` 133行・444行（`c67c506`）は AppImage について「needs FUSE present」と記述しています

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

Windowsは署名済みinstallerとin-app auto-updateをstableチャネルで提供し、Linux desktopは`.deb`/`.rpm`を提供します。これはv0.4.0 CHANGELOGの記述であり、旧版の「Windows desktop未配布」は現行状況としては用いません。

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

- インストーラ実体のNode.js下限（`install.sh` の `NODE_MIN_MAJOR`・`constants.py` の `MIN_NODE_MAJOR`）の v0.7.2 での値（本サイトのスナップショットにソースコードが含まれないため未再測定。v0.3.0 時点は22）
- AppImage の FUSE 要件（CHANGELOG と `install.md` の記述差。上記「[v0.7.0での変更](#v070での変更)」参照）

> 以前ここに記載していた2件は**解消**したため外しました。
> - **Node.jsの下限**: 公式`installation/`ページ・`install.md` 40行とも「22」で一致（v0.6.0 で既に一致。上記「[v0.3.0での変更](#v030での変更)」の注記参照）
> - **managed venvのパス**: 公式`installation/`ページ（`docs_md/installation.md` 59行）・公式`troubleshooting/`ページ（`docs_md/troubleshooting.md` 23行）・`install.md` 196-198行のすべてが `~/.kiro/crew-venv` で一致（v0.6.0 で既に一致。`~/.kiro/crew/venv` は v0.3.0 時点の公式ページの記述）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/installation/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
- Windows: [02_windows.md](02_windows.md)
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

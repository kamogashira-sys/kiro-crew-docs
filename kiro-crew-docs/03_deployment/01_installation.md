# インストール

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/installation/>（Page updated 表記あり）
**出典**: リポジトリ README「App downloads」節、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

---

## 📑 このページの内容

- [4つの導入経路](#4つの導入経路)
- [デスクトップ版の配布物](#デスクトップ版の配布物)
- [チャネル（stable/insider/nightly）](#チャネルstableinsidernightly)
- [前提要件](#前提要件)
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
curl -fsSL https://download.crew.kiro.dev/cli.sh | sh -s -- --version 0.1.0
```

インストーラはwheelのダイジェストを署名済みマニフェストと照合し、不一致なら**インストールを拒否**します（チェックサムのみのフォールバックはありません）。`pipx`が使えればそれを使い、無ければ管理対象venv（`~/.kiro/crew-venv`。`KIROCREW_VENV`で変更可）を**データホームの外**に作成します（ホーム全体を操作する処理が動いているインタープリタを削除しないため）。選択したチャネルは `~/.kiro/crew/channel` に記録されます。

## 前提要件

| 要件 | 用途 | 下限 |
|------|------|------|
| **Python** | バックエンド | **`>= 3.12`**（v0.6.0で3.10から引き上げ。`pyproject.toml` の `requires-python`） |
| **Node.js + npm** | ダッシュボードのビルド | `20 \|\| >= 22`（ビルド時のみ必要。事前ビルド済みwheel/DMG/AppImageの利用者はNode不要） |
| **`kiro-cli`** | LLM駆動 | 必須 |

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

**この値の出典は、上記「前提要件」表の出典とは異なります。** 上表のNode.js要件（`20 || >= 22`）は`docs/guides/install.md` 40行（`website/package.json`の`engines`）に基づきますが、**この記述は`21584ea`でも更新されていません**。v0.3.0の実際の下限は以下の一次情報で確認できます。

| 出典（`21584ea`） | 記述 |
|---|---|
| CHANGELOG.md v0.3.0節 **14行** | 「**Node.js 22 is now the minimum** (24 LTS recommended). A Node 20 install is ...」 |
| `src/kiro_crew/constants.py` **33行** | `MIN_NODE_MAJOR = 22`。コメントは「22 is the oldest non-EOL line the frontend bundler supports（`ensure-node.sh`はより細かい22.12の下限を強制し、`.nvmrc`は推奨の24 LTSをピン留めする）」 |
| `install.sh` **48行** | `NODE_MIN_MAJOR=22`。コメントは「Minimum Node major the frontend build actually supports」。**インストーラは検出段階でこの値を参照し、下限未満のnodeが既にある場合はそれを使わずインストールのはしごに進みます**（263行「Node.js ... is below the supported floor (>= $NODE_MIN_MAJOR) — installing a supported Node…」） |

**⚠️ 本サイトは上表（`install.md`由来の`20 || >= 22`）を削除していません。** 公式`installation/`ページの「Node.js 18+」と`install.md`の「`20 || >= 22`」の食い違いは`21584ea`でも解消されておらず、そこに**インストーラ実体の22という第3の値**が加わった状態です。**どの記述が最終的に正か・なぜ更新が追随していないかは公式に説明がないため、本サイトは裁定しません。**

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

- Node.jsの下限バージョンについて、公式`installation/`ページは「Node.js 18+」と記述するが、リポジトリの`docs/guides/install.md`は「20 || >= 22」と記述しており一致しない。本サイトはリポジトリ側（一次情報順位1）を採用している
- managed venvのパスについて、公式`installation/`ページ相当の`docs_md/installation.md:47`は`~/.kiro/crew/venv`と記述するが、リポジトリの`docs/guides/install.md`は`~/.kiro/crew-venv`と記述しており一致しない（[03_deployment/05_troubleshooting.md](05_troubleshooting.md)も参照）。本サイトはリポジトリ側を採用している

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/installation/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
- Windows: [02_windows.md](02_windows.md)
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

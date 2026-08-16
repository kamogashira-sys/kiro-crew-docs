# インストール

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/installation/>（Page updated 表記あり）
**出典**: リポジトリ README「App downloads」節、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [4つの導入経路](#4つの導入経路)
- [デスクトップ版の配布物](#デスクトップ版の配布物)
- [チャネル（stable/insider/nightly）](#チャネルstableinsidernightly)
- [前提要件](#前提要件)
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
| **Windows** | **デスクトップ版は未配布**。ソースインストールを実行しブラウザでダッシュボードを開く |

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
| **Python** | バックエンド | `>= 3.10`（`make build`は既定で3.12の`.venv`を用意） |
| **Node.js + npm** | ダッシュボードのビルド | `20 \|\| >= 22`（ビルド時のみ必要。事前ビルド済みwheel/DMG/AppImageの利用者はNode不要） |
| **`kiro-cli`** | LLM駆動 | 必須 |

## 未確認事項

- Node.jsの下限バージョンについて、公式`installation/`ページは「Node.js 18+」と記述するが、リポジトリの`docs/guides/install.md`は「20 || >= 22」と記述しており一致しない。本サイトはリポジトリ側（一次情報順位1）を採用している
- managed venvのパスについて、公式`installation/`ページ相当の`docs_md/installation.md:47`は`~/.kiro/crew/venv`と記述するが、リポジトリの`docs/guides/install.md`は`~/.kiro/crew-venv`と記述しており一致しない（[03_deployment/05_troubleshooting.md](05_troubleshooting.md)も参照）。本サイトはリポジトリ側を採用している

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/installation/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/install.md>
- Windows: [02_windows.md](02_windows.md)
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

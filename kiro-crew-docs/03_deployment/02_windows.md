# Windows専用の注意点

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**（埋め込みのWindows対応に関する不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [ソースインストールが唯一の経路](#ソースインストールが唯一の経路)
- [OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)
- [機能別対応状況](#機能別対応状況)
- [デスクトップ版の状況](#デスクトップ版の状況)
- [未確認事項](#未確認事項)

---

## ソースインストールが唯一の経路

Windowsは**ネイティブなソースインストール**（`pip install -e ".[voice]"`、`python -m kiro_crew gateway` で起動）を実行します。すべてのPOSIX専用のプロセス・シグナル・ファイルロック・メトリクス呼び出しは `kiro_crew.platform_compat` を経由します。

## OSレベルサンドボックス層の不在

**公式ドキュメントが明記**: 「Windows does not currently have this OS-level layer — all other protections still apply」。つまりWindowsには他OSにある namespace/Seatbeltレベルのサンドボックスがありませんが、**他の保護層（拒否ルール・ガバナンス・機密パスブロック・出力の秘匿化等）は機能します**。

サンドボックスバックエンドが存在しないため、Script cron・Script hooks・Papyrusのコンパイル/git操作等は既定で **fail-closed**（無防備に実行せず拒否）になります。`agent.sandbox_allow_unsandboxed_exec=true` を明示的に設定するとopt-inで実行できます。

## 機能別対応状況

| 機能 | Windowsでの状況 |
|------|----------------|
| コアGateway/チャット/ダッシュボード | **works**（ディレクトリジャンクションで配信） |
| LLM cronジョブ（`message`種） | **works** |
| Scriptのcronジョブ | `agent.sandbox_allow_unsandboxed_exec` opt-inが必要 |
| Commandのcronジョブ（`sh -c "…"`） | **サポート外**。POSIX shセマンティクスで検証されるが、Windowsに対応するシェルが無い（cmd.exeはPOSIXでない、Git for Windowsの`sh.exe`はbashで別の問題がある） |
| Script hooks | `agent.sandbox_allow_unsandboxed_exec` opt-inが必要。cmd.exe言語で実行（`%ComSpec% /c`） |
| Pull-requestソースの取得/確認/解決 | **not yet**（POSIX OSレベルサンドボックスが必要） |
| ブラウザ自動化（`playwright-cli`） | **works**（Node.js 20以降が必要） |
| ベクトルメモリ／埋め込み | `windows-install.md`本体の記載: リモート埋め込みエンドポイントまたはDocker経由。**ローカルOllamaの自動インストールはnot yet**（※下記の注記参照） |
| STT（whisper／任意のクラウド文字起こし） | **works** |
| 音声応答（Piper TTS） | **not yet**（upstream rhasspy/piperがWindowsバイナリを提供していない）。Amazon Pollyはopt-in設定併用で動作 |
| SSHトンネル（`kirocrew cloud` リモートダッシュボード） | **not yet**（OpenSSHクライアントとシグナル処理の監査が必要） |
| MCPサーバのツール一覧 | 組み込みサーバ（`kirocrew-core`等）はopt-in不要でworks。サードパーティサーバは opt-in が必要 |
| MCP Gateway（opt-in・既定オフ） | **works**（named pipeトランスポート） |
| Papyrus（LaTeXエディタ・opt-inのbuiltin） | works。コンパイル・gitは opt-in が必要 |

`not yet` の項目はWindows機能パリティのフォローアップとして追跡されています。

> **注記: ベクトルメモリ／埋め込み行に一次情報内の不整合があります**。`memory-skills-hooks.md`は「macOS (Apple Silicon and Intel), Linux (x86_64, arm64/Graviton), and **Windows supported**」「Windows x86_64 | `win_amd64/` | CPU」「the old Docker fallback is **gone**」と明記しており、vendored `llama-cpp-python`のin-process embedderがWindows向けにネイティブ提供され、リモートエンドポイントやDockerは不要と読めます。一方、本ページの主要出典である`windows-install.md`は上表のとおり「remote embedding endpointまたはDocker経由」「local Ollama auto-installはnot yet」と記載しており、この2つの一次情報は一致しません。本サイトはページの主要出典である`windows-install.md`の記述をそのまま採用していますが、実際の挙動はより新しい`memory-skills-hooks.md`の記述（Windowsネイティブサポート）に近い可能性があります。

## デスクトップ版の状況

- **CI成果物のみ**: nightly/releaseの実行と手動の`workflow_dispatch`プローブで生成されるが、**ダウンロードCDNには未公開**（今後 `publish-windows.yml` レーンで対応予定）
- **署名は配線済みだが未有効化**: AWS Signerパスは準備済みだが、署名プロファイルがプロビジョニングされるまではスキップされる。**現在のインストーラは未署名**で、SmartScreenが「unrecognized app」の警告を出す（More info > Run anywayで進める）

> **v0.3.0での「Windows is a first-class build」について**: CHANGELOG v0.3.0節 116行（`21584ea`）は「**Windows is a first-class build** — The same targets as macOS and Linux, with its own install guide（macOS・Linuxと同じターゲットになり、独自のインストールガイドを持つ）」と述べています。
>
> **一方、上記2点（CI成果物のみ・署名未有効化）は`21584ea`の`windows-install.md` 18〜30行でも文言レベルで変わっていません**（「**CI artifact only** — ... **not yet published to the download CDN**」「**Signing wired but not yet active** — ... installers are still unsigned and SmartScreen shows an "unrecognized app"」）。
>
> **したがって「first-class build」はビルドターゲットとしての扱いを指し、ダウンロードCDNでの配布開始や署名の有効化を意味しません。** 本サイトは一次情報で配布開始を確認できないため、上記2点の記述を維持します。**なぜCHANGELOGが「first-class」と表現し、配布ガイドが「CI成果物のみ」と述べるのかは公式に説明がないため、本サイトは推測しません。**

## 未確認事項

- ベクトルメモリ／埋め込みのWindows対応状況について、本ページの主要出典`windows-install.md`と`memory-skills-hooks.md`の間に不整合がある（上記「機能別対応状況」の注記を参照）。どちらが実際の挙動を反映するかは公式情報だけでは確定できない

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
- セキュリティ（サンドボックス）: [01_features/09_security.md](../01_features/09_security.md)
- 導入経路一覧: [01_installation.md](01_installation.md)

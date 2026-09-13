# Windows専用の注意点

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（埋め込みのWindows対応に関する不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）

---

## 📑 このページの内容

- [デスクトップ版の導入](#デスクトップ版の導入)
- [OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)
- [機能別対応状況](#機能別対応状況)
- [デスクトップ版の状況](#デスクトップ版の状況)
- [未確認事項](#未確認事項)

---

## デスクトップ版の導入

**v0.4.0でWindowsは署名済みinstallerをstableチャネルで配布し、in-app auto-updateに対応します。** ソースインストールは開発・検証などで引き続き利用できますが、唯一の導入経路ではありません。すべてのPOSIX専用のプロセス・シグナル・ファイルロック・メトリクス呼び出しは `kiro_crew.platform_compat` を経由します。

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
| ベクトルメモリ／埋め込み | **動作する**。埋め込みは vendored `llama-cpp-python`（`_vendor/llama_cpp_libs/win_amd64`）を通じて**in-process**で実行され、`~/.kiro/crew/models` から Qwen3-Embedding-0.6B GGUF を読み込む。**リモートエンドポイント・Docker・Ollamaサーバはどのプラットフォームでも介在しない**（`windows-install.md` 286行） |
| STT（whisper／任意のクラウド文字起こし） | **works** |
| 音声応答（Piper TTS） | **not yet**（upstream rhasspy/piperがWindowsバイナリを提供していない）。Amazon Pollyはopt-in設定併用で動作 |
| SSHトンネル（`kirocrew cloud` リモートダッシュボード） | **not yet**（OpenSSHクライアントとシグナル処理の監査が必要） |
| MCPサーバのツール一覧 | 組み込みサーバ（`kirocrew-core`等）はopt-in不要でworks。サードパーティサーバは opt-in が必要 |
| MCP Gateway（opt-in・既定オフ） | **works**（named pipeトランスポート） |
| Papyrus（LaTeXエディタ・opt-inのbuiltin） | works。コンパイル・gitは opt-in が必要 |

`not yet` の項目はWindows機能パリティのフォローアップとして追跡されています。

> **以前記載していた不整合は解消しています（v0.6.0実測）**。本サイトは以前「`windows-install.md` はリモート埋め込みエンドポイントまたはDocker経由と記載し、`memory-skills-hooks.md` はWindowsネイティブ対応と記載していて一致しない」と注記していました。しかし **v0.6.0 の `windows-install.md` 286行は「works — embeddings run in-process through the vendored llama-cpp-python (`_vendor/llama_cpp_libs/win_amd64`)… No remote endpoint, no Docker and no Ollama server is involved on any platform」と明記**しており、`memory-skills-hooks.md` 284行（`_vendor/llama_cpp_libs/{…,win_amd64}` のプラットフォーム別ネイティブライブラリ）と一致します。
>
> **なお v0.4.1 時点の `windows-install.md` も既に同じ記述**（289行）であり、この不整合は少なくとも v0.4.1 の時点で解消していました。本サイトの注記が追随していませんでした。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## デスクトップ版の状況

現在の配布状況はv0.4.0 CHANGELOGの「Signed Windows installer」に基づきます。Windows installerは署名済みでstableチャネルから提供され、in-app auto-updateに対応します。旧v0.3.0資料にあるCI artifactのみ・CDN未公開・未署名という説明は、その時点の履歴であり、現在の配布状況を示しません。


## 未確認事項

- ベクトルメモリ／埋め込みのWindows対応については、**v0.6.0実測で `windows-install.md` と `memory-skills-hooks.md` が一致しており、以前記載していた不整合は解消**した（上記「機能別対応状況」の注記を参照）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
- セキュリティ（サンドボックス）: [01_features/09_security.md](../01_features/09_security.md)
- 導入経路一覧: [01_installation.md](01_installation.md)

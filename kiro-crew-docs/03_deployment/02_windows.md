# Windows専用の注意点

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（埋め込みのWindows対応に関する不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（v0.7.0での既定の反転・機能別対応状況の再測定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

---

## 📑 このページの内容

- [デスクトップ版の導入](#デスクトップ版の導入)
- [OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)
- [機能別対応状況](#機能別対応状況)
- [v0.7.0での変更](#v070での変更)
- [デスクトップ版の状況](#デスクトップ版の状況)
- [未確認事項](#未確認事項)

---

## デスクトップ版の導入

**v0.4.0でWindowsは署名済みinstallerをstableチャネルで配布し、in-app auto-updateに対応します。** ソースインストールは開発・検証などで引き続き利用できますが、唯一の導入経路ではありません。すべてのPOSIX専用のプロセス・シグナル・ファイルロック・メトリクス呼び出しは `kiro_crew.platform_compat` を経由します。

## OSレベルサンドボックス層の不在

WindowsにはKiro CrewのOSサンドボックスバックエンド（Linuxのuser namespace、macOSの`sandbox-exec`に相当するもの）がありません。既定のチャットバックエンド（公式Kiro CLI）・モデル一覧・アカウント情報・使用量の読み取りは、**Kiro CLI自身の組み込みサンドボックスに自動で委譲**されるため、初回チャットの前に設定を編集する必要はありません（`windows-install.md` 280-283行）。

> ⚠️ **v0.7.0 で、Windowsの既定が「拒否」から「非サンドボックス実行」に反転しました（既定値が変わりました）。**
>
> スクリプト（Script cron）・hooks・サードパーティACPバックエンド・Appバックエンド・MCPプローブ・`gh`/`glab`などのプロバイダCLIは、委譲できるサンドボックスがありません。**v0.7.0 以降、これらは Windows では既定で UNCONFINED（OSによる閉じ込めなし）で実行されます。** `windows-install.md` 285-290行はこれを「このプラットフォームの文書化された既定であり、利用者が有効にしたバイパスでも失敗でもない」と説明しています。
>
> - エージェントが起動したサブプロセスは、**`.aws`・`.ssh` を含むホームディレクトリをOSの閉じ込めなしに読めます**。Kiro Crewは認証情報の環境変数を除去し、こうした起動をすべて監査ログに記録しますが、**悪意のあるリポジトリや文書がファイルを読むことは止められません**
> - 非サンドボックス実行のサブプロセスは**利用者自身のユーザー権限**で動きます（シェルで自分でツールを実行するのと同じ姿勢）
>
> **v0.6.0 までは逆でした。** v0.6.0 の `windows-install.md` 232-238行は、これらの経路は「still fail closed」であり、実行するには `agent.sandbox_allow_unsandboxed_exec` を `true` にして**明示的にopt-in**する必要がある、と記述していました。
>
> 本内容は v0.7.2 タグの仕様書で確認したもので、CHANGELOG/Release 本文（「A small fix.」）は説明していません。v0.7.0〜v0.7.2 の各タグの `windows-install.md` 289行が同じ記述です。CHANGELOG.md v0.7.0節（27-675行）にこの反転の記載は見つかりません。

**拒否したい場合**は、`%USERPROFILE%\.kiro\crew\config.json` で**明示的に `false` を宣言**します（opt-out）。宣言すると、MCPサーバ・Appバックエンド・Script cron・hooks・Papyrusのコンパイラはサンドボックスエラーを返すようになります。

```json
{ "agent": { "sandbox_allow_unsandboxed_exec": false } }
```

- **宣言した値は、どちらの向きでもプラットフォーム既定より優先**されます。ガバナンスの `sandbox.min_level` 下限は、その両方をフリート全体で上書きします（`windows-install.md` 304-305行）
- **`kirocrew setup` がこの判断を提示します**。WindowsにOSサンドボックスが無いことを検出して露出を1回説明し、拒否するかを尋ねます。**既定の答えは「no」**（プラットフォーム既定のまま）で、yesと答えない限り何も書き込みません（キーは未宣言のまま）。非対話実行でも通知は表示されます（307-313行）
- **`kirocrew doctor`** は **Sandbox** の項目で実効状態（拒否／宣言による非サンドボックス／プラットフォーム既定による非サンドボックス）を報告します（315-317行）
- 設定はライブで読まれるため、変更後にGatewayの再起動は不要です（320-321行）

`security.md` 309行も「未宣言の `sandbox_allow_unsandboxed_exec` は `sandbox.unsandboxed_exec_platform_default()` で解決され、**Windowsでは許可、それ以外ではfail-closed**」と記述しています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - リポジトリの `docs/guides/windows-install.md` 285-305行・`docs/system-specs/modules/security.md` 309行（`c67c506`）: 未宣言時の既定は**プラットフォーム依存**で、**Windowsでは非サンドボックス実行を許可**
> - 公式 `configuration/` ページ（`docs_md/configuration.md` 88行）: `agent.sandbox_allow_unsandboxed_exec` の既定は `false`、「Allows execution without a sandbox only when explicitly enabled」（プラットフォームによる違いの記載なし）
> - 公式 `security/` ページ（`docs_md/security.md` 38行）: 「On Windows, it applies when Kiro CLI's internal sandbox is off. In these cases, Crew refuses to start the agent unless you explicitly set `agent.sandbox` to `off` or set `agent.sandbox_allow_unsandboxed_exec` to `true`」
> - リポジトリ `README.md` 397-402行（`c67c506`）: 「Windows offers no equivalent OS-level layer, so Kiro Crew fails closed there: agent subprocesses are refused rather than run unconfined, until you declare the `sandbox_allow_unsandboxed_exec` opt-in」

> **以前の引用について**: 本節は以前、公式 `security/` ページの「Windows does not currently have this OS-level layer — all other protections still apply」を引用していました。**この文は v0.6.0 の公式 `security/` ページには既に存在しません**（v0.4.1 時点の公式ページまでは存在）。本サイトの記述が追随していませんでした。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/configuration/>・<https://kiro.dev/docs/crew/security/>（Page updated 表記あり）

## 機能別対応状況

`windows-install.md` 338-365行「Per-feature status on Windows」（`c67c506`）の抜粋です。「既定で非サンドボックス実行」は、上記「[OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)」のプラットフォーム既定によるもので、`agent.sandbox_allow_unsandboxed_exec=false` を宣言すると拒否されます。

| 機能 | Windowsでの状況 |
|------|----------------|
| コアGateway/チャット/ダッシュボード | **works**（ディレクトリジャンクションで配信） |
| LLM cronジョブ（`message`種） | **works** |
| Scriptのcronジョブ | **既定で非サンドボックス実行**（`wrap_argv`経由）。`false` を宣言すると、設定名を示すメッセージでジョブが失敗する（346行）。**v0.6.0までは opt-in が必要だった** |
| Commandのcronジョブ（`sh -c "…"`） | **サポート外**。POSIX shセマンティクスで検証されるが、Windowsに対応するシェルが無い（cmd.exeはPOSIXでない、Git for Windowsの`sh.exe`はbashで別の問題がある） |
| Script hooks | **既定で非サンドボックス実行**。`false` を宣言するとhookはそのメッセージを`error`として返す。cmd.exe言語で実行（`%ComSpec% /c`）（348行）。**v0.6.0までは opt-in が必要だった** |
| Pull-requestソースの取得/確認/解決 | **not yet**（POSIX OSレベルサンドボックスが必要） |
| ブラウザ自動化（`playwright-cli`） | **works**（Node.js 20以降が必要） |
| **`kirocrew pod`（隔離ワークツリーのテストGateway）**（v0.7.0） | **works**。**Task Scheduler**（`schtasks.exe`）経由で**非昇格**で動作。`pod up/down/ls/status/token/url/logs/prune/provision/scenarios` が動作する。制約: **クラッシュ時の自動再起動なし**、**`pod api` は拒否**（AF_UNIXソケットが必要なため。`pod token` と自前のクライアントでループバックポートに接続する）。メモリ・fork-bombの上限はJob objectで適用されるが、Linuxのcgroupと同等ではない（CPU上限なし）。タスクを作成できない場合はグループポリシー等が原因で、非管理者での回避策はない（354行） |
| ベクトルメモリ／埋め込み | **動作する**。埋め込みは vendored `llama-cpp-python`（`_vendor/llama_cpp_libs/win_amd64`）を通じて**in-process**で実行され、`~/.kiro/crew/models` から Qwen3-Embedding-0.6B GGUF を読み込む。**リモートエンドポイント・Docker・Ollamaサーバはどのプラットフォームでも介在しない**（`windows-install.md` 355行） |
| STT（whisper／任意のクラウド文字起こし） | **works** |
| 音声応答 | **既定の `system` プロバイダで追加インストールなしに動作**（Windows PowerShell 5.1 経由で `System.Speech` を使用。`wrap_argv`を通らないためサンドボックス不在の影響を受けない）。`piper`・`polly` は`wrap_argv`を通るため**既定で非サンドボックス実行**、`false` を宣言すると音声が返らない。`pip install piper-tts` はWindows x64 wheelを提供している（357行）。**v0.6.0までは「not yet（rhasspy/piperがWindowsバイナリを提供していない）」だった** |
| SSHトンネル（`kirocrew cloud` リモートダッシュボード） | **not yet**（OpenSSHクライアントとシグナル処理の監査が必要） |
| MCPサーバのツール一覧 | 組み込みサーバ（`kirocrew-core`等）はopt-in不要でworks。サードパーティサーバのツール一覧は `agent.sandbox_allow_unsandboxed_exec` の opt-in が必要（359行。サーバ自体はkiro-cliが起動するため、チャットでのツール利用には影響しない） |
| MCP Gateway（opt-in・既定オフ） | **works**（named pipeトランスポート） |
| Papyrus（LaTeXエディタ・opt-inのbuiltin） | works。**コンパイル・gitは既定で非サンドボックス実行**。`false` を宣言すると422（`compiler_sandbox_unavailable`／`git_sandbox_unavailable`）を返す（361行）。**v0.6.0までは opt-in が必要だった** |

`not yet` の項目はWindows機能パリティのフォローアップとして追跡されています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（音声応答の既定プロバイダ）
> - `windows-install.md` 357行・`docs/system-specs/modules/voice-streaming.md` 5-8行（`c67c506`）: 既定はホスト組み込みの音声エンジン（`system`）。「macOSとWindowsで何もインストール不要な唯一のプロバイダ」のため
> - 公式 `chat/voice/` ページ（`docs_md/chat__voice.md` 85・109行）: 「Piper (the default)」、`voice.tts_provider` の既定は `piper`（「only `piper` today」）

> **MCPサーバのツール一覧の行について**: `windows-install.md` 359行は、サードパーティサーバのツール一覧に「`agent.sandbox_allow_unsandboxed_exec` opt-in」が必要と記述しています。同じ文書の 289行・346-361行の他の行は「既定で非サンドボックス実行」と記述しており、この行だけ表現が異なります。本サイトは原文どおり記載し、未宣言時にツール一覧が得られるかどうかは裁定しません（[未確認事項](#未確認事項)参照）。

> **以前記載していた不整合は解消しています（v0.6.0実測）**。本サイトは以前「`windows-install.md` はリモート埋め込みエンドポイントまたはDocker経由と記載し、`memory-skills-hooks.md` はWindowsネイティブ対応と記載していて一致しない」と注記していました。しかし **v0.6.0 の `windows-install.md` 286行は「works — embeddings run in-process through the vendored llama-cpp-python (`_vendor/llama_cpp_libs/win_amd64`)… No remote endpoint, no Docker and no Ollama server is involved on any platform」と明記**しており、`memory-skills-hooks.md` 284行（`_vendor/llama_cpp_libs/{…,win_amd64}` のプラットフォーム別ネイティブライブラリ）と一致します。
>
> **なお v0.4.1 時点の `windows-install.md` も既に同じ記述**（289行）であり、この不整合は少なくとも v0.4.1 の時点で解消していました。本サイトの注記が追随していませんでした。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## v0.7.0での変更

- **非サンドボックス実行がWindowsの既定になりました**（既定値が変わりました）。詳細と拒否の方法は上記「[OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)」を参照してください
- **隔離pod（`kirocrew pod`）がWindowsで動作**: `pod up` と down・ls・status・token・url・logs・prune・provision が Task Scheduler 経由で動きます。対象はソースチェックアウトのgit worktreeで、自分のユーザーがスケジュールタスクを作成できるホストに限られます。**`pod api` だけはWindowsで拒否**されます（podの非公開リクエストにUnixドメインソケットが必要なため）（CHANGELOG.md v0.7.0節 122-126行）
- **WindowsデスクトップアプリのGatewayのコールドスタートが約4倍高速化**（同梱Pythonのimportが約17秒から約4秒へ）（同 110-112行。公式 `installation/` ページ 109行も「noticeably faster in 0.7」と記述）
- **設定を開くショートカットが `Alt+,` に変更**（WindowsとLinux。中国語・日本語の入力メソッドでカンマを再び入力できるようにするため。macOSは `Cmd+,` のまま）（同 458-460行）
- **その他（Windows catches up）**: TLSインスペクションを行うプロキシの背後でもターンが動作する（エージェントプロセスのWindows信頼ストアを置き換えなくなった）／ディレクトリジャンクションがシンボリックリンクと同じ防御に掛かる／Issue Radar が WSL なしで Azure DevOps を読める（Apps → Library で有効化し、azure-devops 拡張付きの認証済み `az` が必要）／PPTX Maker が既定のインストール先の LibreOffice を `PATH` になくても見つける（同 132-145行）
- **フラグ付きファイル配送の承認（`kirocrew file-delivery approve`）はネイティブWindowsでは拒否されます**。承認はエージェントがnonceを読めないことを前提にしており、WindowsにはCrewのサンドボックスバックエンドが無い（起動が委譲される）ためです（`docs/feature-map/README.md` 320-325行）

**出典**: CHANGELOG.md v0.7.0節（`c67c506`）、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/feature-map/README.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）

## デスクトップ版の状況

現在の配布状況はv0.4.0 CHANGELOGの「Signed Windows installer」に基づきます。Windows installerは署名済みでstableチャネルから提供され、in-app auto-updateに対応します。旧v0.3.0資料にあるCI artifactのみ・CDN未公開・未署名という説明は、その時点の履歴であり、現在の配布状況を示しません。


## 未確認事項

- `agent.sandbox_allow_unsandboxed_exec` の既定値の書き方が、`windows-install.md`・`security.md`（Windowsでは未宣言＝許可）と、公式 `configuration/`・`security/` ページおよびリポジトリ `README.md`（`false`／fail closed）で異なる（上記「[OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)」の注記参照。裁定しない）
- Windowsで未宣言のとき、サードパーティMCPサーバのツール一覧が得られるか（`windows-install.md` 359行は opt-in が必要と記述し、同文書の他の行の「既定で非サンドボックス実行」と表現が異なる）
- 音声応答の既定プロバイダ（リポジトリは `system`、公式 `chat/voice/` ページは `piper`。上記注記参照）
- ベクトルメモリ／埋め込みのWindows対応については、**v0.6.0実測で `windows-install.md` と `memory-skills-hooks.md` が一致しており、以前記載していた不整合は解消**した（上記「機能別対応状況」の注記を参照）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
- セキュリティ（サンドボックス）: [01_features/09_security.md](../01_features/09_security.md)
- 導入経路一覧: [01_installation.md](01_installation.md)

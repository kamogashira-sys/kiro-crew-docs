# Windows専用の注意点

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（埋め込みのWindows対応に関する不整合の指摘）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/memory-skills-hooks.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（v0.7.0での既定の反転・機能別対応状況の再測定）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**（v0.9.0での再検証: デスクトップインストーラの現状・サンドボックス委譲・機能別対応状況・トラブルシューティング）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**（v0.11.1での再検証: 既定ハーネス KAS の閉じ込め・音声応答の `piper` 削除・アプリ無しで Gateway を動かす手順・起動失敗時の画面表示・`kirocrew kas install`）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/voice-streaming.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/acp-client.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
**出典**（v0.11.1）: <https://kiro.dev/docs/crew/chat/voice/>（Page updated 2026-10-20）

---

## 📑 このページの内容

- [デスクトップ版の導入](#デスクトップ版の導入)
- [OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)
- [機能別対応状況](#機能別対応状況)
- [v0.11.1での変更](#v0111での変更)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [デスクトップ版の状況](#デスクトップ版の状況)
- [未確認事項](#未確認事項)

---

## デスクトップ版の導入

**v0.4.0でWindowsは署名済みinstallerをstableチャネルで配布し、in-app auto-updateに対応します。** ソースインストールは開発・検証などで引き続き利用できますが、唯一の導入経路ではありません（v0.9.0 の `windows-install.md` 3-5行は「through the desktop installer or a supported Python source install」と記述）。すべてのPOSIX専用のプロセス・シグナル・ファイルロック・メトリクス呼び出しは `kiro_crew.platform_compat` を経由します。

v0.9.0 の `windows-install.md` 14-60行によるインストーラの現状（詳細は下記「[デスクトップ版の状況](#デスクトップ版の状況)」）:

- NSIS インストーラ（`KiroCrew-Setup.exe`）で、バックエンドを同梱するため別途 Python の導入は不要です
- **nightly・insider・stable の全チャネルで公開**されます。`latest/` の URL は `https://download.crew.kiro.dev/desktop/<channel>/latest/KiroCrew-Setup.exe` です。Windows ビルドが失敗した release は、インストーラ無しで出ます
- Authenticode 署名済みで、自動更新はダウンロードしたインストーラの署名を fail-closed で検証します。署名後も、新しいファイルハッシュの初回ダウンロードでは SmartScreen の警告が出ることがあります
- 既定はユーザー単位のインストール（UAC なし）です。インストールモード画面で「すべてのユーザー」を選ぶと Program Files への昇格インストールになります
- アンインストールは `~/.kiro/crew` を残します（`deleteAppDataOnUninstall` は false）
- Node.js 22.12+ はソースビルド（`make.ps1 build`）に必要で、デスクトップ版・wheel には不要です（`windows-install.md` 191行）。Kiro CLI の扱いは [01_installation.md](01_installation.md) の食い違い注記を参照してください

## OSレベルサンドボックス層の不在

WindowsにはKiro CrewのOSサンドボックスバックエンド（Linuxのuser namespace、macOSの`sandbox-exec`に相当するもの）がありません。**Kiro CLIハーネス**のチャットバックエンド・モデル一覧・アカウント情報・使用量の読み取りは、**Kiro CLI自身の組み込みサンドボックスに自動で委譲**されるため、初回チャットの前に設定を編集する必要はありません（`windows-install.md` 300-305行・311-312行。v0.9.0 の 281-285行は「既定のチャットバックエンド（公式Kiro CLI）」と書いていました）。**v0.11.0 以降の既定ハーネス KAS は、この委譲の対象ではありません**（下の注記）。

> ⚠️ **既定のチャットハーネス KAS は、Windows では OS による閉じ込め無しで動きます（v0.11.0 以降の既定）。**
>
> - KAS は Windows に自前の OS サンドボックスを持たず、Kiro CLI を起動する経路でもないため、**`.aws`・`.ssh` を含むホームディレクトリを読めます**（`windows-install.md` 307-311行）。初回チャットの前に設定を編集する必要がない点は変わりません（同 311-312行）
> - Kiro CLI のサンドボックスの中にチャットを置くには、Settings → Agent Harness で **Kiro CLI** を選びます（保存値は `"acp_backend": "kiro"`。同 312-313行）
> - 下で説明する `sandbox_allow_unsandboxed_exec=false` を宣言すると、KAS のチャットは、その設定名を示して拒否されます。その状態でチャットするには Kiro CLI を選びます（同 313-315行）
> - 根拠の補強: `docs/system-specs/modules/harness-parity.md` 89行（既定は KAS）、`docs/system-specs/modules/acp-client.md` 3613-3619行（KAS プロセスは自前の OS サンドボックスを持たない）
>
> 本内容は **`windows-install.md` の差分で確認したもので、CHANGELOG・Release 本文は説明していません**（CHANGELOG.md v0.11.0節 151-153行は、既定ハーネスが KAS になったことだけを記述）。v0.9.0 以前は既定が Kiro CLI で、既定のチャットが委譲を受けていました。

> ⚠️ **v0.7.0 で、Windowsの既定が「拒否」から「非サンドボックス実行」に反転しました（既定値が変わりました）。**
>
> スクリプト（Script cron）・hooks・サードパーティACPバックエンド・Appバックエンド・MCPプローブ・`gh`/`glab`などのプロバイダCLIは、委譲できるサンドボックスがありません。**v0.7.0 以降、これらは Windows では既定で UNCONFINED（OSによる閉じ込めなし）で実行されます。** `windows-install.md` 286-296行（v0.7.2 のタグでは 285-290行）はこれを「このプラットフォームの文書化された既定であり、利用者が有効にしたバイパスでも失敗でもない」と説明しています。
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

- **宣言した値は、どちらの向きでもプラットフォーム既定より優先**されます。ガバナンスの `sandbox.min_level` 下限は、その両方をフリート全体で上書きします（`windows-install.md` 305-306行）
- **`kirocrew setup` がこの判断を提示します**。WindowsにOSサンドボックスが無いことを検出して露出を1回説明し、拒否するかを尋ねます。**既定の答えは「no」**（プラットフォーム既定のまま）で、yesと答えない限り何も書き込みません（キーは未宣言のまま）。非対話実行でも通知は表示されます（308-314行）
- **`kirocrew doctor`** は **Sandbox** の項目で実効状態（拒否／宣言による非サンドボックス／プラットフォーム既定による非サンドボックス）を報告します（316-318行）
- 設定はライブで読まれるため、変更後にGatewayの再起動は不要です（321-322行）

`security.md` 763行（v0.7.2 のタグでは 309行）も「未宣言の `sandbox_allow_unsandboxed_exec` は `sandbox.unsandboxed_exec_platform_default()` で解決され、**Windowsでは許可、それ以外ではfail-closed**」と記述しています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - リポジトリの `docs/guides/windows-install.md` 316-322行・`docs/system-specs/modules/security.md` 961行（`fe6f5be`。v0.9.0 の `99e6253` では 286-306行・763-767行）: 未宣言時の既定は**プラットフォーム依存**で、**Windowsでは非サンドボックス実行を許可**
> - 公式 `configuration/` ページ（`docs_md/configuration.md` 103行。Page updated 2026-10-20）: `agent.sandbox_allow_unsandboxed_exec` の既定は `false`、「Allows execution without a sandbox only when explicitly enabled」（プラットフォームによる違いの記載なし）
> - 公式 `security/` ページ（`docs_md/security.md` 38行。Page updated 2026-10-12）: 「On Windows, it applies when Kiro CLI's internal sandbox is off. In these cases, Crew refuses to start the agent unless you explicitly set `agent.sandbox` to `off` or set `agent.sandbox_allow_unsandboxed_exec` to `true`」
>
> v0.7.2 のリポジトリ `README.md` 397-402行は「Windows offers no equivalent OS-level layer, so Kiro Crew fails closed there」と記述し、公式側に近い立場でした。**v0.9.0 の `README.md` には該当する記述がなく、v0.11.1 の `README.md` にも見つかりません**（`sandbox_allow_unsandboxed_exec`・「fail closed」・「equivalent OS-level」のいずれも検索で見つからない）。食い違いは、リポジトリの `windows-install.md`・`security.md` 対 公式 `configuration/`・`security/` ページの組として継続しています。

> **以前の引用について**: 本節は以前、公式 `security/` ページの「Windows does not currently have this OS-level layer — all other protections still apply」を引用していました。**この文は v0.6.0 の公式 `security/` ページには既に存在しません**（v0.4.1 時点の公式ページまでは存在）。本サイトの記述が追随していませんでした。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
**出典**: <https://kiro.dev/docs/crew/configuration/>（Page updated 2026-10-20）・<https://kiro.dev/docs/crew/security/>（Page updated 2026-10-12）

## 機能別対応状況

`windows-install.md`「Per-feature status on Windows」（v0.9.0 の `99e6253` では 339-363行。v0.11.1 の `fe6f5be` では 369行以降）の抜粋です。**コア行・音声応答の行は v0.11.1 の行番号、それ以外の行の行番号は v0.9.0 のものです**。「既定で非サンドボックス実行」は、上記「[OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)」のプラットフォーム既定によるもので、`agent.sandbox_allow_unsandboxed_exec=false` を宣言すると拒否されます。

| 機能 | Windowsでの状況 |
|------|----------------|
| コアGateway/チャット/ダッシュボード | **`sandbox_allow_unsandboxed_exec` 無しで works**。**既定の KAS ハーネスは、未宣言のプラットフォーム既定で閉じ込め無しで動き**、`false` を宣言すると拒否される。**Kiro CLI ハーネスは Kiro CLI の組み込みサンドボックスへ委譲**される。親プロセスは機密性のある環境変数をどちらでも除去する（`windows-install.md` 373行。`fe6f5be`。v0.9.0 の記述は「**works**（ディレクトリジャンクションで配信）」）。ソースインストールでビルド済みの `website/dist` は、Gateway の起動時にディレクトリジャンクションで配信される（権限は不要。従来の記述どおり） |
| LLM cronジョブ（`message`種） | **works** |
| Scriptのcronジョブ | **既定で非サンドボックス実行**（`wrap_argv`経由）。`false` を宣言すると、設定名を示すメッセージでジョブが失敗する（347行）。**v0.6.0までは opt-in が必要だった** |
| Commandのcronジョブ（`sh -c "…"`） | **サポート外**。POSIX shセマンティクスで検証されるが、Windowsに対応するシェルが無い（cmd.exeはPOSIXでない、Git for Windowsの`sh.exe`はbashで別の問題がある） |
| Script hooks | **既定で非サンドボックス実行**。`false` を宣言するとhookはそのメッセージを`error`として返す。cmd.exe言語で実行（`%ComSpec% /c`）（349行）。**v0.6.0までは opt-in が必要だった** |
| Pull-requestソースの取得/確認/解決 | **既定で非サンドボックス実行**（Script cron・hooks と同じプラットフォーム既定）。`sandbox_allow_unsandboxed_exec=false` を宣言すると、`sandboxed_spawn_argv` が設定名を示すメッセージで拒否する。ドロワーは独自の非同期・サンドボックス経由の spawn（`source_providers.runner._run_json`）を保ち、許可実行ファイル・環境変数 allowlist・出力上限・タイムアウト・監査は引き続き掛かる。provider-CLI の信頼チェックも適用される（350行）。**v0.7.2 のタグでは not yet だった** |
| ブラウザ自動化（`playwright-cli`） | **works**（Node.js 20以降が必要） |
| **`kirocrew pod`（隔離ワークツリーのテストGateway）**（v0.7.0） | **works**。**Task Scheduler**（`schtasks.exe`）経由で**非昇格**で動作。`pod up/down/ls/status/token/url/logs/prune/provision/scenarios` が動作する。制約: **クラッシュ時の自動再起動なし**、**`pod api` は拒否**（AF_UNIXソケットが必要なため。`pod token` と自前のクライアントでループバックポートに接続する）。メモリ・fork-bombの上限はJob objectで適用されるが、Linuxのcgroupと同等ではない（CPU上限なし）。タスクを作成できない場合はグループポリシー等が原因で、非管理者での回避策はない（356行） |
| ベクトルメモリ／埋め込み | **動作する**。埋め込みは vendored `llama-cpp-python`（`_vendor/llama_cpp_libs/win_amd64`）を通じて**in-process**で実行され、`~/.kiro/crew/models` から Qwen3-Embedding-0.6B GGUF を読み込む。**リモートエンドポイント・Docker・Ollamaサーバはどのプラットフォームでも介在しない**（`windows-install.md` 357行） |
| STT（whisper／任意のクラウド文字起こし） | **works** |
| 音声応答 | **既定の `system` プロバイダ（ホスト組み込みの音声エンジン）で追加インストールなしに動作**（Windows PowerShell 5.1 経由で `System.Speech` を使用。`wrap_argv`を通らないためサンドボックス不在の影響を受けない）。`polly` は`wrap_argv`を通るため**未宣言のプラットフォーム既定で閉じ込め無し**、`false` を宣言すると音声が返らない（ログに設定名が出る）（`windows-install.md` 389行、`fe6f5be`）。**`piper` の記述は v0.11.1 では消え、`piper` プロバイダは削除されました**（下記「[v0.11.1での変更](#v0111での変更)」）。**v0.9.0 までは「`piper`・`polly` は`wrap_argv`を通り、`pip install piper-tts` はWindows x64 wheelを提供している」と書かれていました。v0.6.0までは「not yet（rhasspy/piperがWindowsバイナリを提供していない）」だった** |
| SSHトンネル（`kirocrew cloud` リモートダッシュボード） | **not yet**（OpenSSHクライアントとシグナル処理の監査が必要） |
| MCPサーバのツール一覧 | 組み込みサーバ（`kirocrew-core`等）はopt-in不要でworks。サードパーティサーバのツール一覧は `agent.sandbox_allow_unsandboxed_exec` の opt-in が必要（361行。サーバ自体はkiro-cliが起動するため、チャットでのツール利用には影響しない） |
| MCP Gateway（opt-in・既定オフ） | **works**（named pipeトランスポート） |
| Papyrus（LaTeXエディタ・opt-inのbuiltin） | works。**コンパイル・gitは既定で非サンドボックス実行**。`false` を宣言すると422（`compiler_sandbox_unavailable`／`git_sandbox_unavailable`）を返す（363行）。**v0.6.0までは opt-in が必要だった** |

| ダッシュボードの terminal タブのタイトル・コマンド補完・チャットへ渡す cwd | **Windowsでは使えない**。タブは既定のタイトルのまま。ConPTY が前景プロセスグループとシェルの cwd の取得手段を持たないため。terminal 自体は動く（354行） |
| 対話 SSO ログインのパネル | **Windowsでは非対応**（`pty`／`fork`／`termios` が必要。「not supported on Windows」の応答を返す）（827-830行） |
| `resource_limits`（Job object） | Job object が強制するのは `max_processes` と `max_memory_mb` の**2つだけ**。`cpu_weight`・`max_cpu_percent`・`max_cpu_seconds`・`max_open_files`・`max_total_memory_mb`・`max_total_processes` は受理されるが Windows では働かず、設定しているものごとに Gateway が警告を1回ログする（552-556行）。メモリの上限は同等だが、プロセス数の上限は `TasksMax`（スレッドを数える）と `ActiveProcessLimit`（プロセスを数える）で1対1ではない |

`not yet` の項目はWindows機能パリティのフォローアップとして追跡されています。

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**（音声応答の既定プロバイダ。v0.11.1 で食い違いが大きくなりました）
> - `windows-install.md` 389行・`docs/system-specs/modules/voice-streaming.md` 5-10行・122-124行（`fe6f5be`）: 既定はホスト組み込みの音声エンジン（`system`）。TTS プロバイダは組み込みエンジンと Amazon Polly の2つで、**ローカルの `piper` プロバイダは削除された**。削除済みプロバイダの指定は既定に解決され、`piper_*` キーは `config.json` に残っても読まれない
> - 公式 `chat/voice/` ページ（`docs_md/chat__voice.md` 105・129行。Page updated 2026-10-20）: 「Piper (the default)」、`voice.tts_provider` の既定は `piper`（「only `piper` today」）
>
> v0.9.0 の時点では、リポジトリは「既定が `system`」で、公式は「`piper`」でした。v0.11.1 では、リポジトリは `piper` の削除そのものを記述しています。

> **MCPサーバのツール一覧の行について**: `windows-install.md` 361行（`99e6253`）は、サードパーティサーバのツール一覧に「`agent.sandbox_allow_unsandboxed_exec` opt-in」が必要と記述しています。同じ文書の 290行・347-363行の他の行は「既定で非サンドボックス実行」と記述しており、この行だけ表現が異なります（v0.7.2 のタグでも 359行で同じ記述）。本サイトは原文どおり記載し、未宣言時にツール一覧が得られるかどうかは裁定しません（[未確認事項](#未確認事項)参照）。

> **以前記載していた不整合は解消しています（v0.6.0実測）**。本サイトは以前「`windows-install.md` はリモート埋め込みエンドポイントまたはDocker経由と記載し、`memory-skills-hooks.md` はWindowsネイティブ対応と記載していて一致しない」と注記していました。しかし **v0.6.0 の `windows-install.md` 286行は「works — embeddings run in-process through the vendored llama-cpp-python (`_vendor/llama_cpp_libs/win_amd64`)… No remote endpoint, no Docker and no Ollama server is involved on any platform」と明記**しており、`memory-skills-hooks.md` 284行（`_vendor/llama_cpp_libs/{…,win_amd64}` のプラットフォーム別ネイティブライブラリ）と一致します。
>
> **なお v0.4.1 時点の `windows-install.md` も既に同じ記述**（289行）であり、この不整合は少なくとも v0.4.1 の時点で解消していました。本サイトの注記が追随していませんでした。
>
> **出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
> （参照: 2026-09-13 / commit `8575209` / 版 v0.6.0）

## v0.11.1での変更

v0.10.0・v0.11.0・v0.11.1 に「Before you upgrade」節はありません。以下のうち、**`windows-install.md` と `voice-streaming.md` の差分で確認した項目は、CHANGELOG・Release 本文が説明していません**（各項目に明記します）。

- **既定ハーネス KAS は Windows で閉じ込め無しで動きます（v0.11.0 以降の既定）**: 詳細は上記「[OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)」の注記と「[機能別対応状況](#機能別対応状況)」のコア行を参照してください。Kiro CLI ハーネスを選ぶと委譲されます（`windows-install.md` 307-315・373行）。**CHANGELOG に説明なし**（既定ハーネスの変更だけが CHANGELOG.md v0.11.0節 151-153行にあります）
- **音声応答の `piper` プロバイダが削除されました**: `voice-streaming.md` 5-10行は、TTS プロバイダを組み込みエンジン（既定）と Amazon Polly の2つとし、ローカルの `piper` は削除されたと記述します（issue #23154）。削除済みプロバイダの指定は既定に解決され、`piper_*` キーは `config.json` に残っても読まれません（同 122-124行）。`windows-install.md` 389行からも `piper` の記述が消えました。**CHANGELOG に説明なし**（v0.10.0・v0.11.0・v0.11.1 の節に Piper 削除の記載はありません）。**削除の時期は仕様書の比較で絞れます**: v0.10.0 タグの `voice-streaming.md` は `piper` を TTS プロバイダとして記述し、v0.11.0 タグの同ファイル（5-10行）は削除済みと記述します。したがって削除は v0.11.0 で入っています（CHANGELOG には説明がないため、仕様書の比較による判断です）。食い違いは上記「[機能別対応状況](#機能別対応状況)」の注記を参照してください
- **デスクトップアプリ無しで Gateway を動かす手順が加わりました**（v0.10.0 から。v0.10.0 タグの `windows-install.md` 701行に同名の節があり、v0.9.0 の `windows-install.md` にはありません。v0.11.1 では 732-769行の節「Running the gateway without the desktop app」）。Electron のウィンドウが描画できないホスト（VMware／VirtualBox のゲストへの RDP、VDI、無人サーバ）向けです
  1. `kirocrew gateway` で Gateway を動かし、ダッシュボードはブラウザで使います。デスクトップインストーラは CLI を `PATH` に追加しないため、デスクトップ版を入れたホストでは、同梱のシム `<install dir>\resources\backend-dist\kirocrew-backend\bin\kirocrew.cmd` をフルパスで呼びます。そのウィンドウを閉じると Gateway は止まります
  2. 同じホストの別シェルで `kirocrew token` を実行し、出力されたリンクを 5 分以内に開きます
  3. リンクはアクセス Cookie と 30 日のリフレッシュ Cookie を設定し、アクセス Cookie の期限が切れる前に両方が更新されます。30 日間ダッシュボードを開かなかった場合だけ、新しいリンクが要ります
  4. 同じポート（既定 5476）で待ち受ける Gateway は 1 つだけです。この Gateway が動いている間にデスクトップアプリを開くと、アプリは新しい Gateway を起動せず、既存のものを再利用します
  5. **この方法には監視がありません。** `kirocrew service install` は Windows のバックエンドを持たず（対応は systemd と launchd のみ）、サインアウトやウィンドウを閉じると Gateway は止まり、ブート時には起動せず、終了しても再起動されません。Windows の監視は別の作業として提案されています（`windows-install.md` 766-769行が参照する PR #11289）。**CHANGELOG に説明なし**
- **灰色／空白のウィンドウが終了するときの画面表示が加わりました**（v0.10.0 から。v0.10.0 タグの `windows-install.md` 763行に同じ記述があり、v0.9.0 にはありません）: 再読み込みを使い切ると、ウィンドウプロセスが何回、どの終了コードで終了したかを示すネイティブのダイアログが出ます。Windows で終了コードが `-2147483645` で、ダッシュボードのページがまだ読み込まれていなければ、サンドボックスが原因であることを名指しし、サンドボックスは無効化されていないと述べ、トラブルシューティングの該当節を開くボタンが付きます。古い版は黒いウィンドウだけです（`windows-install.md` 786-793行。切り分けの手順は [05_troubleshooting.md](05_troubleshooting.md) を参照）。**CHANGELOG に説明なし**
- **ソースインストールで KAS エンジンを取得する手順**: `kirocrew kas install` を実行すると、この版がピン留めするエンジンをデータホームに入れます。`agent.kas_bundle`（既定オフ）をオンにしたときに追加のダウンロードが要りません。ソースビルドはこのコマンドを自動では実行せず、デスクトップインストーラはエンジンをアプリ内に持ちます。`install.ps1` は Gateway をこのマシンで動かさず、起動するインスタンスが `install.sh` で入れて、エンジンを既定で取得します（`windows-install.md` 262-274行。詳細は [01_installation.md](01_installation.md) を参照）。**CHANGELOG に説明なし**（`--no-kas` の変更は CHANGELOG.md v0.11.1節 45-47行）
- **CHANGELOG が説明する Windows の変更**: v0.11.1 は「Windows の復旧が、失敗したネットワーク確認を、諦める前に再試行する」と記述します（CHANGELOG.md v0.11.1節 49-50行）。v0.10.0 は、ストア書き込みが Windows が一時的に保持するリネームを再試行する、ホストのスリープが Gateway の死亡と読まれない、MCP サーバがツール実行中も ping に応答する、と記述します（同 v0.10.0節 397-399行）
- **その他（`windows-install.md` の差分で確認したもの。CHANGELOG に説明なし）**: `scripts/five_whys.py` のログロックが、Windows では待機するようになり、約 10 秒後の `EDEADLOCK` で失敗しません（533-553行）。設定コマンドのヒントは、インストール済みバンドルで検証されます（44-57行）

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/voice-streaming.md>
（参照: 2026-11-01 / commit `fe6f5be` / 版 v0.11.1）
出典: CHANGELOG.md v0.10.0節 397-399行・v0.11.0節 151-153行・v0.11.1節 45-50行（`fe6f5be`）

## v0.9.0での変更

v0.9.0 に「Before you upgrade」節はありません。

- **Pull-requestソースドロワーが「既定で非サンドボックス実行」になりました**: v0.7.2・v0.8.0 のタグの `windows-install.md` 349行では not yet でした。v0.9.0 では 350行が、Script cron・hooks と同じプラットフォーム既定で動き、`sandbox_allow_unsandboxed_exec=false` の宣言で拒否されると記述しています（上記「[機能別対応状況](#機能別対応状況)」）
- **ダッシュボードの terminal タブのタイトル・コマンド補完・チャットへ渡す cwd は Windows では使えません**（354行）。`resource_limits` のうち Job object が働くのは2つだけです（552-556行）。いずれも上記「機能別対応状況」の表に載せました
- **CHANGELOG.md v0.9.0節 168-172行**（「Windows and installs」）: Windows のコマンドラインが UTF-8 として読まれる、BOM 付きの `.env` と Claude のプロジェクト設定が正しく読まれる、単発の Kiro CLI 呼び出しがコンソールウィンドウを開かない、インストーラが進捗を表示する、Windows インストーラの exit 17 が原因を示す、更新は再構築した環境を検証してからバックアップを捨てる、と記述されています。ロックされたファイルによって他のタブの保存済みコンテキスト値が消えない修正も同節にあります（165行）

以上のうち上2項は **v0.9.0 タグの `windows-install.md` で確認したもので、CHANGELOG/Release 本文は説明していません**。

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.9.0節 165・168-172行（`99e6253`）

## v0.8.0での変更

- **新しい Crew Member が Windows でも private Memory V2 ストアを自動で受け取ります**: v0.7.2 の `windows-install.md` 8-12行は、Windows のネイティブ Gateway では新規メンバーの作成と V1 から V2 への明示的な設定が書き込み前に拒否されると記述していました。v0.8.0 以降は、他のプラットフォームと同じく自動で作られます。作成は owner-only の NTFS 権限で行われ、POSIX が共有のストア使用ロックで保護する部分は SQLite のネイティブなファイルハンドルが担います（v0.9.0 の `windows-install.md` 8-12行）。本内容は v0.8.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません
- **デスクトップアプリが Kiro CLI を同梱します**（CHANGELOG.md v0.8.0節 214-218行。**v0.11.0 で同梱をやめました**。[01_installation.md](01_installation.md) を参照）。`windows-install.md` 80行（v0.9.0）の Finish ページは「the default Kiro agent needs Kiro CLI」と案内しており、当時は同梱の記述と食い違っていました。v0.11.0 以降は同梱しない記述になり、この案内（v0.11.1 では 93-94行）と矛盾しません
- **トラブルシューティング節に「灰色／空白のウィンドウが終了する」場合の切り分けが加わりました**: 内容は [05_troubleshooting.md](05_troubleshooting.md) を参照してください。本内容は v0.8.0 タグの `windows-install.md` で確認したもので、CHANGELOG/Release 本文は説明していません

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）
出典: CHANGELOG.md v0.8.0節 214-218行（`99e6253`）

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

現在の配布状況はv0.4.0 CHANGELOGの「Signed Windows installer」と、v0.9.0 の `windows-install.md` 14-60行に基づきます。Windows installerは署名済みで、nightly・insider・stable の全チャネルから提供され、in-app auto-updateに対応します（詳細は上記「[デスクトップ版の導入](#デスクトップ版の導入)」）。旧v0.3.0資料にあるCI artifactのみ・CDN未公開・未署名という説明は、その時点の履歴であり、現在の配布状況を示しません。


## 未確認事項

- `agent.sandbox_allow_unsandboxed_exec` の既定値の書き方が、`windows-install.md`・`security.md`（Windowsでは未宣言＝許可）と、公式 `configuration/`・`security/` ページ（`false`／fail closed）で異なる（**継続**。`windows-install.md` 316-322行・`security.md` 961行（`fe6f5be`）と公式ページの記述は v0.11.1 でも変わっていない。`README.md` は v0.9.0 から当事者から外れたまま。上記「[OSレベルサンドボックス層の不在](#osレベルサンドボックス層の不在)」の注記参照。裁定しない）
- Windowsで未宣言のとき、サードパーティMCPサーバのツール一覧が得られるか（`windows-install.md` 391行（`fe6f5be`。v0.9.0 では 361行）は opt-in が必要と記述し、同文書の他の行の「未宣言のプラットフォーム既定で閉じ込め無し」と表現が異なる。**継続**）
- 音声応答の既定プロバイダ（リポジトリは `system` で `piper` は削除済み、公式 `chat/voice/` ページは `piper`。**継続**で、v0.11.1 で食い違いが大きくなった。上記注記参照）
- デスクトップアプリが Kiro CLI を同梱するかの記述差（公式 `installation/` ページと CHANGELOG v0.11.0節・`install.md` 585-592行。**継続**。v0.11.0 で当事者が入れ替わり、`windows-install.md` 93-94行（Finish ページ）は食い違いの当事者から外れた。[01_installation.md](01_installation.md) の食い違い注記を参照。裁定しない）
- ベクトルメモリ／埋め込みのWindows対応については、**v0.6.0実測で `windows-install.md` と `memory-skills-hooks.md` が一致しており、以前記載していた不整合は解消**した（上記「機能別対応状況」の注記を参照）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/guides/windows-install.md>
- セキュリティ（サンドボックス）: [01_features/09_security.md](../01_features/09_security.md)
- 導入経路一覧: [01_installation.md](01_installation.md)

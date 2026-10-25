# Computer Use・ブラウザ自動化

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-08-29 / commit `bba3f195212992eaa07d83c082e1ec55e395c32b` / 版 v0.4.1）
**出典**（v0.6.0 で公式ドキュメントに新設された2ページ）: <https://kiro.dev/docs/crew/features/computer-use/>・<https://kiro.dev/docs/crew/features/browser/>
**出典**（v0.7.0での変更・Windows のポインタの扱いの修正・ブラウザの記述の食い違い）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）
**出典**: <https://kiro.dev/docs/crew/features/computer-use/>（Page updated 2026-08-31）・<https://kiro.dev/docs/crew/features/browser/>（Page updated 2026-09-25）
**出典**（v0.9.0 での再検証・ブラウザの2経路・食い違いの解消・Computer Use の owner 専用 API）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。公式 `features/computer-use/` は Page updated 2026-08-31、`features/browser/` は 2026-09-25 で、いずれも v0.7.2 時点から変化なし）

---

## 📑 このページの内容

- [Computer Use（デスクトップGUI自動化）](#computer-useデスクトップgui自動化)
- [ブラウザ自動化](#ブラウザ自動化)
- [v0.9.0での変更](#v090での変更)
- [v0.8.0での変更](#v080での変更)
- [v0.7.0での変更](#v070での変更)
- [v0.6.0での変更（公式ドキュメントへのページ新設）](#v060での変更公式ドキュメントへのページ新設)
- [v0.4.0での変更](#v040での変更)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## Computer Use（デスクトップGUI自動化）

エージェントに、操作者自身のデスクトップアプリケーションを**プラットフォームのアクセシビリティ層経由**で読み取り・操作させる機能です。画面上のアプリを列挙し、1つのアプリウィンドウをインデックス化されたアクセシビリティツリーに展開し、要素をインデックスで指定して操作します（押す・入力・値の設定・スクロール・名前付きアクションの実行）。アドレス指定可能な要素を持たないUIについては、画面上の点（クリック・ドラッグ）を使います。

**この機能でないもの**（実装のギャップではなく、製品として意図的な決定であることが明記されています）:

- **要素指定・非ポインタ入力が既定であり、そのままで使える唯一の方法です。** `element_index` を指定した `computer_click` は `AXPress` を実行し、ポインタを一切介さずにコントロールを起動します。これがインデックスがある場合に `auto` が常に選ぶ方法です。座標クリックと `computer_drag` はキャンバス・地図・独自描画UI向けに用意されています。**macOS では**、これらも `click_method: "app_post"`（`CGEventPostToPid` で対象プロセスに位置付きのマウスイベントを送る）により物理カーソルには触れません。**Windows では、座標指定のクリックとドラッグは実際のポインタをその位置へ移動させます**（下記「実際のカーソルを動かす経路」参照）
- **操作者がオフバンドで有効化するまで無効**です。有効化ファイルはエージェントが読み書きできません（キーストーン方式）

**v0.4.0時点でmacOSとWindowsに対応します**。WindowsではUI Automationによりネイティブアプリを読み取り・操作します。Linux対応はv0.4.0 CHANGELOGでは確認できないため、対応プラットフォームに含めません。

### 実際のカーソルを動かす経路

**macOS では**、物理カーソルを実際に動かす唯一の経路は `click_method: "global"` です。これは**モデルが明示的に指定**する必要があり、`auto` は決してこの経路を選びません。使用ごとに専用の `tool_kind` でSELレコードが記録されます（`computer-use.md` 15-28行、`99e6253`。v0.7.2 では 15-26行）。

**Windows では**、座標指定のクリックとドラッグが実際のポインタをその位置へ移動させます（公式 `features/computer-use/`「On Windows, a coordinate-based click or drag warps the real pointer to that point」）。モジュール仕様は、Windows にはプロセス単位の入力配送がなく（`SendInput` は hwnd も pid も持たない）、操作者のカーソルを動かさずに1つのアプリにマウスイベントを渡す方法がないと説明しています。要素指定の操作は UI Automation のパターン経由でポインタもフォーカスも動かさず、`auto` が選ぶのはこの形だけで、ポインタとキーボードの経路は名前で指定したときだけ使われます（`computer-use.md` 1831行・2103-2118行、`99e6253`。v0.7.2 では 1819行・2087-2096行）。

> **記述の修正**: 本サイトは以前、OSを区別せずに「座標クリックと `computer_drag` も物理カーソルには触れない」「実カーソルを動かす唯一の経路は `click_method: "global"`」と記載していました。これは macOS の挙動で、Windows には当てはまりません。公式 `features/computer-use/` は v0.6.0 時点から Windows のポインタ移動を記載しており（v0.7.2 時点の同ページは v0.6.0 と同一）、v0.7 での変更ではありません。

### 2つの補助的な人間向けビュー

- **ライブビュー（PiP）**: モデルが既に読んだスクリーンショットを映すだけ
- **Cursor Motion**: 実際のデスクトップ上に偽のカーソルを描画する化粧的機能のみ（`screencapture` からは意図的に見えない）

## ブラウザ自動化

v0.9.0 の `modules/browser.md` 3-7行（`99e6253`）は、ブラウザ自動化に**2つの経路**があると記述しています。

1. **デスクトップアプリ**: **`browser` MCP ツール**が、Browser パネルのネイティブな組み込み Chromium ビューを操作します。単一のツールで、Playwright のツール名前空間ではありません。`op` 列挙で `navigate`・`snapshot`・`click`・`type`・`press_key`・`hover`・`select_option`・`screenshot`・`wait_for`・`back`・`console` を指定します。MCP の shim がゲートウェイのコマンドバスに1つの制限付きコマンドを投げ、Electron が自分のパネルで操作を実行して結果を返します。Node.js や Playwright の別途インストールは不要です（公式 `features/browser/` ページ）
2. **`playwright-cli` のシェル経路**（フォールバック）: ネイティブのパネルがセッションにないとき、または `dashboard.use_builtin_browser`（既定 `true`）が off のときは、ツールが `playwright-cli`（Playwright のエージェント用 CLI）のシェル経路へ誘導します。リモートや普通のブラウザでのダッシュボードセッション、ローカルの開発プレビュー、高度なブラウザ操作でも、この経路を使います（公式 `features/browser/` ページ）

```
agent turn ──MCP browser(op, args)──▶ gateway command bus ──▶ Electron native view
     │                                      │
     │                                      └─ no panel / built-in disabled
     └─shell fallback──▶ playwright-cli <verb> …
                              │
                              ├─▶ stdout: ページURL, ページタイトル, スナップショットYAMLへのパス
                              └─▶ disk:   .../page-<timestamp>.yml （アクセシビリティツリー）
```

エージェントはタスクごとに、ブラウザが必要か `web_fetch` で足りるかを判断します。`browser` ツールが core MCP のブラウジングの入口であることは `architecture/mcp.md` 1694行・1803-1809行（`99e6253`）も記述しています。

**`playwright-cli` 経路の stdout の1行が契約です**: すべてのコマンドが結果のページURL・ページタイトル・スナップショットYAMLへのファイルシステムパスを出力します。約250文字のstdoutで1つの完全な操作結果を伝え、アクセシビリティツリーはエージェントが必要とするまでディスクに留まります。

> **版差の注記**: AWS Japan社員のZenn記事（0.1.2時点）はブラウザ自動化を「Playwright MCP」と記述しています。v0.2.0 から v0.7.2 の `modules/browser.md` は「ブラウザはシェル機能であり、ツールの名前空間ではない」と記述していました。v0.8.0 と v0.9.0 の同ファイル（いずれも冒頭 3-7行）は上記の2経路の記述になっています。変更は v0.7.2 と v0.8.0 の間に入っており、v0.8.0・v0.9.0 の CHANGELOG の版節に、この記述の変更を告知する項目は見つかりません。

> **解消済み（以前の食い違い）**: 以前は、公式 `features/browser/` ページ（デスクトップアプリでは埋め込み Browser ビューを直接操作し、ネイティブの Browser ツールは Node.js や Playwright の別途インストールが不要）と、`modules/browser.md`（ブラウザはシェル機能）が食い違っていました。v0.9.0 の `browser.md` 3-7行は公式ページと同じ内容で、デスクトップアプリでは `browser` ツールがネイティブ Browser ビューを操作し、`playwright-cli` がフォールバックだと記述しています。なお `architecture/mcp.md` は、v0.7.2 では 1391行で「Browsing is deliberately not an MCP server」と記述していました（`c67c506`）。v0.8.0 の 1508行・1581-1587行（`4d205da`）から、`browser` ツールを core MCP の入口として記述しています。

## v0.9.0での変更

CHANGELOG.md の v0.9.0節（5-186行）に、Computer Use とブラウザ自動化を扱う項目は見つかりません。本節の内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。

### ブラウザ: ネイティブ `browser` ツールの制約

- **ガバナンスの確認**: `browser` ツールは常に提示されますが、呼び出しのたびに `capabilities.browse` のガバナンスと CLI の利用可否を確認します。ガバナンスが拒否した場合は CLI へフォールバックしません。`dashboard.use_builtin_browser`（既定 `true`）を off にしても、ガバナンスの拒否は上書きされません（`browser.md` 97-100行・957行、`99e6253`）
- **`navigate` の対象**: 自動で操作するのは**公開 HTTP(S) の宛先だけ**です。loopback・private・link-local・予約済みのアドレス、数値表記の別形式やパーセントエンコードされた形式、非 ASCII のホスト名、パーサ間で解釈が分かれる形式、HTTP(S) 以外の形式は拒否され、承認ゲート付きの CLI 経路へ誘導されます。DNS 名は解決しないため、公開名から private アドレスへの rebinding は、仕様書が「accepted residual（受け入れ済みの残余リスク）」と記載しています（`browser.md` 115-123行）
- **結果の扱い**: 引数はスカラーまたはスカラーのリストに限られ、結果のテキストは認証情報と持ち出し用 URL を redact したうえで長さが制限されます。スクリーンショットのデータはモデルへの応答にインラインで入りません（`browser.md` 957行）
- **サブエージェントからの操作**: 仕様書は、サブエージェントのプロセスが親のスロットに解決されうるため、サブエージェントのツール呼び出しが親のネイティブパネルを操作することがあると記載しています（同一ユーザー・同一マシン内で、公開宛先への移動に限られる、受け入れ済みの残余リスクとして）
- **内部ルートと上限**: ネイティブ経路は `/api/browser/command`・`/api/browser/command-drain`・`/api/browser/command-result` を使い、3つとも internal-secret 認証でダッシュボードの cookie の呼び出しは受け付けません。コマンドキューは**1セッションあたり 32 件**、操作のタイムアウトは **15 秒**（`navigate` と `wait_for` は **60 秒**）、パネルの liveness は drain も結果もないまま **30 秒**で失効します（`browser.md` 29-36行）

出典（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/mcp.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0。`browser.md` 29-36行はキュー・タイムアウトの上限、97-123行・957行はガバナンスと `navigate` の対象）

> 内部ルート・キュー・タイムアウトの記述（`browser.md` 29-36行）は v0.8.0 のタグにも同じ内容があります。`navigate` の公開宛先限定の記述は、v0.8.0 の `browser.md` 849行（Native `browser` MCP tool の行）にも同じ趣旨があります。

### ブラウザ: インストールジョブと証明書

- **インストールジョブ**: ブラウザ関連のインストールは、ゲートウェイが持つ1つのスロットでジョブとして動きます。種類は `cli_setup`（CLI のセットアップ）と `engine_download`（ブラウザエンジンのダウンロード）、状態は `running`・`succeeded`・`failed`・`interrupted` です。別のジョブの実行中に別のインストールを要求すると HTTP 409（`install_already_running`）が返ります（`POST /api/browser/install` は実行中の `cli_setup` ジョブには合流します）。ジョブの状態はメモリ上にあり、ゲートウェイを再起動すると `install_job: null` を報告します。ジョブはシャットダウン時にプロセスツリーごと停止され `interrupted` になります（`browser.md` 178-215行）
- **OS の証明書ストア**: インストール手順が起動する Node の子プロセス（npm・CLI・CLI が起動するブラウザのダウンロード）には、利用者が `NODE_USE_SYSTEM_CA` を設定していない限り `NODE_USE_SYSTEM_CA=1` が渡され、Node が同梱のルート証明書に加えて OS の証明書ストアを信頼します。TLS を中継する企業のプロキシの CA を OS が信頼していれば、PEM のエクスポートなしで動作します。仕様書は、シェルのプロファイルを持たない GUI 起動のゲートウェイで特に重要だと説明しています（`browser.md` 165-172行）

> 本節の内容は v0.9.0 の `browser.md` に記載があり、v0.7.2 と v0.8.0 の同ファイルには「Install jobs」節と `NODE_USE_SYSTEM_CA` の記述が見つかりません。CHANGELOG/Release 本文は説明していません。

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

### Computer Use: owner 専用の設定 API と既知の制限

- **`PUT /api/computer-use/config` は owner 専用です**: ダッシュボードのブラウザ（cookie）からの呼び出しに限られ、owner 以外のダッシュボードユーザーは 403 `owner_only` で拒否されます。App-Kit のトークンでは呼べません（`request["app"]` が空でなければ本文を読む前に 403）。仕様書は、この拒否が設定の書き込みの境界であり、Computer Use が操作者のオフバンドの有効化まで無効である設計（キーストーン）の前提になっていると記述しています（`computer-use.md` 522行・580-586行）
- **設定の応答**: `GET /api/computer-use/config` の応答には `cursor_motion`（既定 off）・`cursor_motion_supported`・`policy_error` が含まれます。権限状態のプローブは macOS と Windows の両方で動き、プローブがないプラットフォームでは `unsupported` を報告します（`computer-use.md` 558-570行。`cursor_motion_supported` は v0.8.0 の同ファイル538行にもあり、v0.7.2 にはありません）
- **既知の制限**: ネイティブ処理はゲートウェイに集約されます。ドライバーの例外は `_guarded` で変換され、`subprocess_executor` のスレッドプールがアプリのハングをイベントループから隔離しますが、ネイティブプロセスのクラッシュは防げず、ctypes の障害がゲートウェイを終了させることがあります（`computer-use.md` 156-160行・2551行以降）
- **エージェントのプロンプト**: デフォルトのエージェントのプロンプトの Computer Use の節は、ゲートが開いているセッションにだけ全文が入り、閉じているときは Settings → Computer Use への短い案内になります（`computer-use.md` 120-137行）

> 本節の内容は v0.9.0 タグの仕様書で確認したもので、CHANGELOG/Release 本文は説明していません。

**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.8.0での変更

### ブラウザ: リモート／トンネル経由のダッシュボード

v0.8.0 の CHANGELOG（Notable fixes）は、Browser パネルがダッシュボード自身のアドレスから提供されるため、SSH で到達するリモートのダッシュボードでも、別のポートを転送する必要がないと記載しています。仕様書は、同一オリジンの relay（`/browser-view/<token>/`）を経由する仕組みで、`dashboard.browser_view_port` が意味を持つのは、relay が提供されないときにパネルが使う直接 URL のフォールバックの場合だけだと記述しています（`browser.md` 535-541行・924-940行、`99e6253`）。

出典: CHANGELOG.md v0.8.0節 495-497行（`99e6253`）。
**出典**（仕様書）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-10-25 / commit `99e6253` / 版 v0.9.0）

## v0.7.0での変更

### Browser パネルの追加機能

- **Annotate モード**: パッケージ版デスクトップアプリの組み込み Browser パネルで、アプリ自身の埋め込みブラウザビューに開いたページの要素を選んでメモを付けると、番号付きの一覧とスクリーンショットをチャットのコンポーザに送り、エージェントに作業させられます（CHANGELOG 186-189行）
- **アドレスバーから公開 Web サイトを開ける**: クエリ文字列やフラグメントを含まない公開サイトのアドレスを入力すると、デスクトップアプリではない普通の Web ブラウザで開いたダッシュボードでは、ページが **Gateway ホストの managed browser** で開かれ、パネルに埋め込まれて表示されます。Gateway ホストにそのブラウザがインストールされている必要があり、操作できるのは所有者だけです（CHANGELOG 190-193行）。`browser.md` は、デスクトップアプリではネイティブの Chromium ビューがパネルを担い、それ以外の環境では `POST /api/browser/open` のランチャーを使う「2つの transport」として記述しています（v0.9.0 は 706-722行、`99e6253`。v0.7.2 では 587-599行、`c67c506`）

### 公式 `features/browser/` ページの改訂

v0.7.2 時点の公式ページ（Page updated 2026-09-25。v0.9.0 時点でも同じ内容）は、Browser パネルを主な体験として次のように説明しています。

- パッケージ版デスクトップアプリでは、**エージェントが埋め込みの Browser ビューを直接操作**します。CAPTCHA・2FA・判断が必要な場面では人が引き継ぎ、操作をエージェントに戻せます
- デスクトップアプリの**ネイティブの Browser ツールは Node.js や Playwright の別途インストールを必要としません**。`playwright-cli` は、リモートや普通のブラウザでのダッシュボードセッション、ローカルの開発プレビュー、高度なブラウザ操作のためのフォールバックとして残ります
- 利用者が明示的に選んだ場合は、利用者自身が起動している Chrome に接続できます。既存のタブとサインイン状態を持つため、借りた状態として扱うよう公式は案内しています

> **解消済み**: v0.7.2 の時点では、`modules/browser.md` 10-14行・24-30行（`c67c506`）が「The browser is a **shell capability, not a tool namespace.**」と記述し、上記の公式ページの説明と食い違っていました。v0.9.0 の `browser.md` 3-7行（`99e6253`）は公式ページと同じ内容（デスクトップアプリでは `browser` ツールがネイティブ Browser ビューを操作し、`playwright-cli` がフォールバック）になり、食い違いは解消しています。上記「ブラウザ自動化」節を参照してください。

出典: CHANGELOG.md v0.7.0節 184-193行（参照: 2026-10-04 / commit `c67c506` / 版 v0.7.2）。
**出典**: <https://kiro.dev/docs/crew/features/browser/>（Page updated 2026-09-25）

## v0.6.0での変更（公式ドキュメントへのページ新設）

**v0.6.0 で、公式ドキュメントに `features/computer-use/` と `features/browser/` の2ページが新設されました**（v0.4.1 時点の公式ドキュメントには両ページが存在しませんでした）。

公式 `features/computer-use/` は対応プラットフォームを明記しています。

- **Computer Use は既定でオフ**。**Settings → Computer Use** から有効化する
- **macOS**（アクセシビリティレイヤ = AX 経由）と **Windows**（ネイティブバックエンド経由）で動作する
- **Linux はサポート対象外**（"Linux is not supported."）

これは上記「v0.4.0での変更」の内容と整合します（本サイトの記述を変更する必要はありません）。

**出典**: <https://kiro.dev/docs/crew/features/computer-use/>

## v0.4.0での変更

**Windows Computer Use** — v0.4.0 CHANGELOGは、Windows UI AutomationでネイティブWindowsアプリを読み取り・操作できるようになったと記載します。これにより、旧版資料の「macOS限定」「Windowsは型付き拒否」は現在の説明としては用いません。

出典: CHANGELOG.md v0.4.0節（`bba3f195212992eaa07d83c082e1ec55e395c32b`）。

## v0.3.0での変更

### Browser panelについて（v0.3.0 時点の食い違いは v0.9.0 で解消）

v0.3.0のCHANGELOGは「**The Browser panel is the browser**（Browser panelがブラウザそのもの）」として、**エージェントがダッシュボード自身のサイドパネルを直接操作する**（navigate・click・type・screenshot）と述べています。しかし`21584ea`の`modules/browser.md`には、この「エージェントがサイドパネルを直接操作する」という記述が**見つかりませんでした**（同ファイルは`playwright-cli`ベースのシェル機能として全体を記述していました）。このため v0.3.0 から v0.7.2 まで、本サイトは両方の記述を併記していました。

| 出典 | 記述 |
|------|------|
| **CHANGELOG.md 49〜53行**（`21584ea`） | 「**The Browser panel is the browser** — The agent drives the dashboard's own side panel directly: navigate, click, type, screenshot. Browsing happens where you are already looking, **with no second window and no security prompt**（第2のウィンドウもセキュリティプロンプトもなく、今見ている場所でブラウズが行われる）. **The Playwright CLI remains for remote sessions and for a browser you are already logged into**（Playwright CLIはリモートセッションと、既にログイン済みのブラウザ用に残る）」 |
| **CHANGELOG.md 54〜56行**（`21584ea`） | 「**Nothing to install first** — Browsing no longer needs **Node or npm** on the machine. **A private, verified copy is fetched for you**（検証済みの専用コピーが取得される）, so a locked-down laptop is one click from a working browser rather than a dead end」 |
| **`modules/browser.md` 10〜13行**（`21584ea`、v0.7.2 まで同趣旨） | 「The browser is a **shell capability, not a tool namespace.** Each browser action is one `playwright-cli` invocation on the agent's ordinary command path（各ブラウザ操作はエージェントの普段どおりのコマンドパス上での`playwright-cli`の1回の呼び出し）」。**MCPサーバ登録は不要**という記述も維持されていました |
| **`modules/browser.md` 3〜7行**（v0.9.0、`99e6253`） | デスクトップアプリでは `browser` MCP ツールがネイティブの組み込み Chromium ビュー（Browser パネル）を操作し、ネイティブのパネルがないとき、または `dashboard.use_builtin_browser` が off のときは `playwright-cli` のシェル経路へ誘導する。図は 19〜27行 |

**解消済み**: v0.9.0 の `browser.md` 3-7行・19-27行（`99e6253`）は、「エージェント → `browser` MCP ツール → ゲートウェイのコマンドバス → Electron のネイティブビュー」という経路を記述しており、CHANGELOG v0.3.0 の「The Playwright CLI remains for remote sessions」とも整合します（CLI はフォールバックとして残る）。確実に言えるのは以下です。

- **ブラウズにNode/npmが不要になった**（CHANGELOG 54行。デスクトップアプリのネイティブ経路は Node.js や Playwright の別途インストールが不要と、公式 `features/browser/` も記載しています）
- **Playwright CLIは廃止されていない**（CHANGELOG 52〜53行が明示。v0.9.0 の仕様書ではフォールバック経路）
- **`browser` は1つの MCP ツールで、Playwright のツール名前空間ではない**（v0.9.0 の `browser.md` 11-14行。v0.7.2 までの「MCPサーバとしては提供されない」という本サイトの記述は、`browser` ツール（`op` 列挙）の存在により現行の説明としては用いません。[04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)参照）

### Computer Useの提示方法の変更

**Computer Useは「動作する環境にのみ提示される」ようになりました。** ネイティブなデスクトップ自動化は**当時はmacOSに出現しました**。従来の「どこでも提示して失敗する」方式が改められたものです。

**⚠️ この記述はv0.3.0時点のものです。** v0.4.0でWindows対応が追加されました。変わったのは「動作しない環境にも機能を提示していた」という**UIの提示方法**です。

出典: CHANGELOG.md v0.3.0節 57行（`21584ea`）「**Computer Use is offered only where it works** — Native desktop automation appears on macOS」。

## 未確認事項

なし。以前の未確認事項（エージェントがデスクトップアプリの埋め込み Browser ビューを `playwright-cli` を介さずに直接操作するのかどうか）は、v0.9.0 の `modules/browser.md` 3-7行（`99e6253`）が `browser` MCP ツールによる操作を記述し、公式 `features/browser/` ページと一致したため、解消しました。

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
- セキュリティ: [09_security.md](09_security.md)
- MCP統合: [08_mcp-integration.md](08_mcp-integration.md)

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

---

## 📑 このページの内容

- [Computer Use（デスクトップGUI自動化）](#computer-useデスクトップgui自動化)
- [ブラウザ自動化](#ブラウザ自動化)
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

**macOS では**、物理カーソルを実際に動かす唯一の経路は `click_method: "global"` です。これは**モデルが明示的に指定**する必要があり、`auto` は決してこの経路を選びません。使用ごとに専用の `tool_kind` でSELレコードが記録されます（`computer-use.md` 15-26行、`c67c506`）。

**Windows では**、座標指定のクリックとドラッグが実際のポインタをその位置へ移動させます（公式 `features/computer-use/`「On Windows, a coordinate-based click or drag warps the real pointer to that point」）。モジュール仕様は、Windows にはプロセス単位の入力配送がなく（`SendInput` は hwnd も pid も持たない）、操作者のカーソルを動かさずに1つのアプリにマウスイベントを渡す方法がないと説明しています。要素指定の操作は UI Automation のパターン経由でポインタもフォーカスも動かさず、`auto` が選ぶのはこの形だけで、ポインタとキーボードの経路は名前で指定したときだけ使われます（`computer-use.md` 1819行・2087-2096行、`c67c506`）。

> **記述の修正**: 本サイトは以前、OSを区別せずに「座標クリックと `computer_drag` も物理カーソルには触れない」「実カーソルを動かす唯一の経路は `click_method: "global"`」と記載していました。これは macOS の挙動で、Windows には当てはまりません。公式 `features/computer-use/` は v0.6.0 時点から Windows のポインタ移動を記載しており（v0.7.2 時点の同ページは v0.6.0 と同一）、v0.7 での変更ではありません。

### 2つの補助的な人間向けビュー

- **ライブビュー（PiP）**: モデルが既に読んだスクリーンショットを映すだけ
- **Cursor Motion**: 実際のデスクトップ上に偽のカーソルを描画する化粧的機能のみ（`screencapture` からは意図的に見えない）

## ブラウザ自動化

> **重要: ブラウザ自動化はMCPサーバではありません。**

一次情報は明確に「**The browser is a shell capability, not a tool namespace**（ブラウザはシェル機能であり、ツールの名前空間ではない）」と明記しています。

> v0.7.0 以降の Browser パネルは、デスクトップ版の埋め込みブラウザビューと、Web ダッシュボードでの Gateway 側 managed browser の2系統で説明されています。公式ページとモジュール仕様の記述が食い違う点を含め、「[v0.7.0での変更](#v070での変更)」を参照してください。

`playwright-cli`（Playwrightのエージェント用CLI）経由でウェブサイトを閲覧します。エージェントはブラウザを普段どおりのコマンドパス上のシェルコマンド実行として操作します。

```
agent turn ──shell──▶ playwright-cli <verb> …
                          │
                          ├─▶ stdout: ページURL, ページタイトル, スナップショットYAMLへのパス
                          └─▶ disk:   .../page-<timestamp>.yml （アクセシビリティツリー）
```

**そのため、登録すべきMCPサーバは存在せず**、リクエストごとに再送されるツールスキーマもなく、メッセージごとのブラウズマーカーもありません。エージェントはタスクごとに、ブラウザが必要か `web_fetch` で足りるかを判断します。

**stdoutの1行が契約です**: すべてのコマンドが結果のページURL・ページタイトル・スナップショットYAMLへのファイルシステムパスを出力します。約250文字のstdoutで1つの完全な操作結果を伝え、アクセシビリティツリーはエージェントが必要とするまでディスクに留まります。

> **版差の注記**: AWS Japan社員のZenn記事（0.1.2時点）はブラウザ自動化を「Playwright MCP」と記述していますが、これは執筆時点の設計から変わった可能性があります。v0.2.0以降の一次情報は明確に「MCPサーバではなくシェル機能」と述べているため、本サイトはこれを正として採用します。

## v0.7.0での変更

### Browser パネルの追加機能

- **Annotate モード**: パッケージ版デスクトップアプリの組み込み Browser パネルで、アプリ自身の埋め込みブラウザビューに開いたページの要素を選んでメモを付けると、番号付きの一覧とスクリーンショットをチャットのコンポーザに送り、エージェントに作業させられます（CHANGELOG 186-189行）
- **アドレスバーから公開 Web サイトを開ける**: クエリ文字列やフラグメントを含まない公開サイトのアドレスを入力すると、デスクトップアプリではない普通の Web ブラウザで開いたダッシュボードでは、ページが **Gateway ホストの managed browser** で開かれ、パネルに埋め込まれて表示されます。Gateway ホストにそのブラウザがインストールされている必要があり、操作できるのは所有者だけです（CHANGELOG 190-193行）。`browser.md` 587-599行は、デスクトップアプリではネイティブの Chromium ビューがパネルを担い、それ以外の環境では `POST /api/browser/open` のランチャーを使う「2つの transport」として記述しています（`c67c506`）

### 公式 `features/browser/` ページの改訂

v0.7.2 時点の公式ページ（Page updated 2026-09-25）は、Browser パネルを主な体験として次のように説明しています。

- パッケージ版デスクトップアプリでは、**エージェントが埋め込みの Browser ビューを直接操作**します。CAPTCHA・2FA・判断が必要な場面では人が引き継ぎ、操作をエージェントに戻せます
- デスクトップアプリの**ネイティブの Browser ツールは Node.js や Playwright の別途インストールを必要としません**。`playwright-cli` は、リモートや普通のブラウザでのダッシュボードセッション、ローカルの開発プレビュー、高度なブラウザ操作のためのフォールバックとして残ります
- 利用者が明示的に選んだ場合は、利用者自身が起動している Chrome に接続できます。既存のタブとサインイン状態を持つため、借りた状態として扱うよう公式は案内しています

> ⚠️ **出典間で記述が食い違っています。本サイトは裁定しません。**
> - **公式 `features/browser/`**（Page updated 2026-09-25）: 「In the packaged desktop app, the agent drives the embedded Browser view directly」「The native Browser tool in the packaged desktop app needs no separate Node.js or Playwright installation」
> - **`modules/browser.md` 10-14行・24-30行**（`c67c506`）: 「The browser is a **shell capability, not a tool namespace.** Each browser action is one `playwright-cli` invocation on the agent's ordinary command path」「Everything an agent does with a browser still goes through its shell」
>
> 上記「v0.3.0での変更」の食い違い（CHANGELOG の「The Browser panel is the browser」とモジュール仕様）は、v0.7.2 時点でも公式ページとモジュール仕様の間で続いています。

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

### Browser panelについて（CHANGELOGとモジュール仕様が食い違う・裁定しない）

v0.3.0のCHANGELOGは「**The Browser panel is the browser**（Browser panelがブラウザそのもの）」として、**エージェントがダッシュボード自身のサイドパネルを直接操作する**（navigate・click・type・screenshot）と述べています。しかし`21584ea`の`modules/browser.md`には、この「エージェントがサイドパネルを直接操作する」という記述が**見つかりません**（同ファイルは引き続き`playwright-cli`ベースのシェル機能として全体を記述しています）。**本サイトは裁定せず、両方の記述を併記します。**

| 出典 | 記述 |
|------|------|
| **CHANGELOG.md 49〜53行**（`21584ea`） | 「**The Browser panel is the browser** — The agent drives the dashboard's own side panel directly: navigate, click, type, screenshot. Browsing happens where you are already looking, **with no second window and no security prompt**（第2のウィンドウもセキュリティプロンプトもなく、今見ている場所でブラウズが行われる）. **The Playwright CLI remains for remote sessions and for a browser you are already logged into**（Playwright CLIはリモートセッションと、既にログイン済みのブラウザ用に残る）」 |
| **CHANGELOG.md 54〜56行**（`21584ea`） | 「**Nothing to install first** — Browsing no longer needs **Node or npm** on the machine. **A private, verified copy is fetched for you**（検証済みの専用コピーが取得される）, so a locked-down laptop is one click from a working browser rather than a dead end」 |
| **`modules/browser.md` 10〜13行**（`21584ea`） | 「The browser is a **shell capability, not a tool namespace.** Each browser action is one `playwright-cli` invocation on the agent's ordinary command path（各ブラウザ操作はエージェントの普段どおりのコマンドパス上での`playwright-cli`の1回の呼び出し）」。**MCPサーバ登録は不要**という記述も維持されています |
| **`modules/browser.md` 179〜186行**（`21584ea`） | ダッシュボードのパネルについては「`playwright-cli show --port <n> --host 127.0.0.1` がCLI自身のダッシュボードをループバックHTTPで提供し、**パネルはそれをiframeで埋め込む**」と記述。用途は「**人間がセッションを直接引き継ぐための経路**（エージェントが完了できない・すべきでないCAPTCHAや2FAプロンプトのため）」とされている |

**この食い違いをどう解釈すべきかは公式に説明がないため、本サイトは推測しません。** 確実に言えるのは以下です。

- **ブラウズにNode/npmが不要になった**（CHANGELOG 54行。これは`browser.md`の「OS dependencies」節が扱うインストール要件の変更に相当します）
- **Playwright CLIは廃止されていない**（CHANGELOG 52〜53行が明示。リモートセッション・ログイン済みブラウザ用に残る）
- **MCPサーバとしては提供されない**（`browser.md` 10行が`21584ea`でも維持。[04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)参照）

### Computer Useの提示方法の変更

**Computer Useは「動作する環境にのみ提示される」ようになりました。** ネイティブなデスクトップ自動化は**当時はmacOSに出現しました**。従来の「どこでも提示して失敗する」方式が改められたものです。

**⚠️ この記述はv0.3.0時点のものです。** v0.4.0でWindows対応が追加されました。変わったのは「動作しない環境にも機能を提示していた」という**UIの提示方法**です。

出典: CHANGELOG.md v0.3.0節 57行（`21584ea`）「**Computer Use is offered only where it works** — Native desktop automation appears on macOS」。

## 未確認事項

- エージェントがデスクトップアプリの埋め込み Browser ビューを `playwright-cli` を介さずに直接操作するのかどうか（公式 `features/browser/` とモジュール仕様 `browser.md` の記述が食い違う。「[v0.7.0での変更](#v070での変更)」参照）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
- セキュリティ: [09_security.md](09_security.md)
- MCP統合: [08_mcp-integration.md](08_mcp-integration.md)

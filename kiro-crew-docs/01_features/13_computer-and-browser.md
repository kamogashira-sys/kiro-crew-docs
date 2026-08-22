# Computer Use・ブラウザ自動化

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [Computer Use（デスクトップGUI自動化）](#computer-useデスクトップgui自動化)
- [ブラウザ自動化](#ブラウザ自動化)
- [v0.3.0での変更](#v030での変更)
- [未確認事項](#未確認事項)

---

## Computer Use（デスクトップGUI自動化）

エージェントに、操作者自身のデスクトップアプリケーションを**プラットフォームのアクセシビリティ層経由**で読み取り・操作させる機能です。画面上のアプリを列挙し、1つのアプリウィンドウをインデックス化されたアクセシビリティツリーに展開し、要素をインデックスで指定して操作します（押す・入力・値の設定・スクロール・名前付きアクションの実行）。アドレス指定可能な要素を持たないUIについては、画面上の点（クリック・ドラッグ）を使います。

**この機能でないもの**（実装のギャップではなく、製品として意図的な決定であることが明記されています）:

- **要素指定・非ポインタ入力が既定であり、そのままで使える唯一の方法です。** `element_index` を指定した `computer_click` は `AXPress` を実行し、ポインタを一切介さずにコントロールを起動します。これがインデックスがある場合に `auto` が常に選ぶ方法です。座標クリックと `computer_drag` はキャンバス・地図・独自描画UI向けに用意されており、これらも物理カーソルには触れません
- **操作者がオフバンドで有効化するまで無効**です。有効化ファイルはエージェントが読み書きできません（キーストーン方式）

**macOS限定**（このリリースでは）。**Windows・Linuxは型付きの拒否を返します。**

### 実際のカーソルを動かす経路

物理カーソルを実際に動かす唯一の経路は `click_method: "global"` です。これは**モデルが明示的に指定**する必要があり、`auto` は決してこの経路を選びません。使用ごとに専用の `tool_kind` でSELレコードが記録されます。

### 2つの補助的な人間向けビュー

- **ライブビュー（PiP）**: モデルが既に読んだスクリーンショットを映すだけ
- **Cursor Motion**: 実際のデスクトップ上に偽のカーソルを描画する化粧的機能のみ（`screencapture` からは意図的に見えない）

## ブラウザ自動化

> **重要: ブラウザ自動化はMCPサーバではありません。**

一次情報は明確に「**The browser is a shell capability, not a tool namespace**（ブラウザはシェル機能であり、ツールの名前空間ではない）」と明記しています。

`playwright-cli`（Playwrightのエージェント用CLI）経由でウェブサイトを閲覧します。エージェントはブラウザを通常のコマンドパス上のシェルコマンド実行として操作します。

```
agent turn ──shell──▶ playwright-cli <verb> …
                          │
                          ├─▶ stdout: ページURL, ページタイトル, スナップショットYAMLへのパス
                          └─▶ disk:   .../page-<timestamp>.yml （アクセシビリティツリー）
```

**そのため、登録すべきMCPサーバは存在せず**、リクエストごとに再送されるツールスキーマもなく、メッセージごとのブラウズマーカーもありません。エージェントはタスクごとに、ブラウザが必要か `web_fetch` で足りるかを判断します。

**stdoutの1行が契約です**: すべてのコマンドが結果のページURL・ページタイトル・スナップショットYAMLへのファイルシステムパスを出力します。約250文字のstdoutで1つの完全な操作結果を伝え、アクセシビリティツリーはエージェントが必要とするまでディスクに留まります。

> **版差の注記**: AWS Japan社員のZenn記事（0.1.2時点）はブラウザ自動化を「Playwright MCP」と記述していますが、これは執筆時点の設計から変わった可能性があります。v0.2.0以降の一次情報は明確に「MCPサーバではなくシェル機能」と述べているため、本サイトはこれを正として採用します。

## v0.3.0での変更

### Browser panelについて（CHANGELOGとモジュール仕様が食い違う・裁定しない）

v0.3.0のCHANGELOGは「**The Browser panel is the browser**（Browser panelがブラウザそのもの）」として、**エージェントがダッシュボード自身のサイドパネルを直接操作する**（navigate・click・type・screenshot）と述べています。しかし`21584ea`の`modules/browser.md`には、この「エージェントがサイドパネルを直接操作する」という記述が**見つかりません**（同ファイルは引き続き`playwright-cli`ベースのシェル機能として全体を記述しています）。**本サイトは裁定せず、両方の記述を併記します。**

| 出典 | 記述 |
|------|------|
| **CHANGELOG.md 49〜53行**（`21584ea`） | 「**The Browser panel is the browser** — The agent drives the dashboard's own side panel directly: navigate, click, type, screenshot. Browsing happens where you are already looking, **with no second window and no security prompt**（第2のウィンドウもセキュリティプロンプトもなく、今見ている場所でブラウズが行われる）. **The Playwright CLI remains for remote sessions and for a browser you are already logged into**（Playwright CLIはリモートセッションと、既にログイン済みのブラウザ用に残る）」 |
| **CHANGELOG.md 54〜56行**（`21584ea`） | 「**Nothing to install first** — Browsing no longer needs **Node or npm** on the machine. **A private, verified copy is fetched for you**（検証済みの専用コピーが取得される）, so a locked-down laptop is one click from a working browser rather than a dead end」 |
| **`modules/browser.md` 10〜13行**（`21584ea`） | 「The browser is a **shell capability, not a tool namespace.** Each browser action is one `playwright-cli` invocation on the agent's ordinary command path（各ブラウザ操作はエージェントの通常のコマンドパス上での`playwright-cli`の1回の呼び出し）」。**MCPサーバ登録は不要**という記述も維持されています |
| **`modules/browser.md` 179〜186行**（`21584ea`） | ダッシュボードのパネルについては「`playwright-cli show --port <n> --host 127.0.0.1` がCLI自身のダッシュボードをループバックHTTPで提供し、**パネルはそれをiframeで埋め込む**」と記述。用途は「**人間がセッションを直接引き継ぐための経路**（エージェントが完了できない・すべきでないCAPTCHAや2FAプロンプトのため）」とされている |

**この食い違いをどう解釈すべきかは公式に説明がないため、本サイトは推測しません。** 確実に言えるのは以下です。

- **ブラウズにNode/npmが不要になった**（CHANGELOG 54行。これは`browser.md`の「OS dependencies」節が扱うインストール要件の変更に相当します）
- **Playwright CLIは廃止されていない**（CHANGELOG 52〜53行が明示。リモートセッション・ログイン済みブラウザ用に残る）
- **MCPサーバとしては提供されない**（`browser.md` 10行が`21584ea`でも維持。[04_reference/04_mcp-tools.md](../04_reference/04_mcp-tools.md)参照）

### Computer Useの提示方法の変更

**Computer Useは「動作する環境にのみ提示される」ようになりました。** ネイティブなデスクトップ自動化は**macOSに出現します**。従来の「どこでも提示して失敗する」方式が改められたものです。

**⚠️ v0.3.0でプラットフォームが拡大したわけではありません。** 上記「[Computer Use（デスクトップGUI自動化）](#computer-useデスクトップgui自動化)」の**macOS限定という記述は引き続き正しい**です。変わったのは「動作しない環境にも機能を提示していた」という**UIの提示方法**です。

出典: CHANGELOG.md v0.3.0節 57行（`21584ea`）「**Computer Use is offered only where it works** — Native desktop automation appears on macOS」。

## 未確認事項

- なし（本ページの記述は各モジュール仕様書で確認済み）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
- セキュリティ: [09_security.md](09_security.md)
- MCP統合: [08_mcp-integration.md](08_mcp-integration.md)

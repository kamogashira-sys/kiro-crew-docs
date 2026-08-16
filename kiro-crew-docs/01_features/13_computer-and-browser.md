# Computer Use・ブラウザ自動化

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [Computer Use（デスクトップGUI自動化）](#computer-useデスクトップgui自動化)
- [ブラウザ自動化](#ブラウザ自動化)
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

> **版差の注記**: AWS Japan社員のZenn記事（0.1.2時点）はブラウザ自動化を「Playwright MCP」と記述していますが、これは執筆時点の設計から変わった可能性があります。v0.2.0の一次情報は明確に「MCPサーバではなくシェル機能」と述べているため、本サイトはこれを正として採用します。

## 未確認事項

- なし（本ページの記述は各モジュール仕様書で確認済み）

## 関連リンク

- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/computer-use.md>、<https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/browser.md>
- セキュリティ: [09_security.md](09_security.md)
- MCP統合: [08_mcp-integration.md](08_mcp-integration.md)

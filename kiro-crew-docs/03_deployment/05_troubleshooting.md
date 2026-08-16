# トラブルシューティング

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/troubleshooting/>（Page updated 表記あり）

---

## 📑 このページの内容

- [まず `kirocrew doctor`](#まず-kirocrew-doctor)
- [インストール・セットアップ](#インストールセットアップ)
- [エージェント（kiro-cli）関連](#エージェントkiro-cli関連)
- [未確認事項](#未確認事項)

---

## まず `kirocrew doctor`

大半のCrewの問題は、シェルコマンド1つで収まる修正があります。まずヘルスチェックから始めます。

```bash
kirocrew doctor
```

`doctor` はすべてのサブシステムの状態を報告します: `kiro-cli`バイナリの検出・エージェント認証・埋め込みモデル・Slackトークン・設定の妥当性・MCPサーバのプローブ。問題があれば該当する節に進みます。

## インストール・セットアップ

### インストール後に `kirocrew: command not found`

インストール先のディレクトリが `PATH` にありません。インストーラによって対処が異なります。

- **事前ビルドwheelインストーラ**: `pipx`があればそれを使用、無ければ`~/.kiro/crew/venv`。`~/.local/bin`（pipx既定）か`~/.kiro/crew/venv/bin`が`PATH`にあることを確認
- **`pip install -e .`**: Pythonのスクリプトディレクトリが`PATH`にあることを確認
- **Docker**: `docker exec kirocrew kirocrew …` で呼び出す

その後 `source ~/.bashrc`（またはシェルを再起動）。

### Windows: インストール後に `python: command not found`

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -e . tzdata
python -m kiro_crew gateway
```

`tzdata` が必須です（WindowsはIANAゾーンデータベースを同梱していないため、`zoneinfo.ZoneInfo(...)`がこれなしでは失敗します）。

### Docker: コンテナ起動後にエージェント実行が無効化される

エントリポイントが内部のLinux user-namespaceサンドボックスをプローブし、コンテナランタイムのseccomp/AppArmorポリシー下で失敗した場合です。2つの選択肢があります。

1. **user namespacesを許可**: `--security-opt seccomp=<unshare/cloneを許可するプロファイル>` で再起動。次回起動時にGatewayが再プローブしサンドボックスを有効化
2. **非サンドボックス実行を許容**: `-e KIROCREW_ALLOW_UNSANDBOXED=1` で再起動。エージェントコマンドは内部サンドボックスなしで実行され、コンテナが唯一の隔離境界になる

## エージェント（kiro-cli）関連

### `AcpTimeoutError: ACP prompt timed out`

エージェントバックエンドがハンドシェイクに応答しませんでした。よくある原因:

1. **`kiro-cli`が未インストール**: ダッシュボードの**Set up Kiro**ページで案内される、または`kirocrew doctor`が欠落を報告
2. **ログインしていない**: `kiro-cli login` を実行
3. **MCP設定が壊れている**: `kirocrew setup --agent-only --clean` でエージェントを最初から再構築
4. **初回起動が遅い**: MCPサーバの初期化に60秒以上かかることがある。待つ

## 未確認事項

- 完全なトラブルシューティング項目（本ページは主要な項目のみを記載。詳細は公式ページを参照）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/troubleshooting/>
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

# セキュリティ

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [脅威モデル](#脅威モデル)
- [8つの保護機構（公式の順序）](#8つの保護機構公式の順序)
- [層数についての注記](#層数についての注記)
- [Owner lock](#owner-lock)
- [ガバナンス（POLICY ∩ PROFILE）](#ガバナンスpolicy--profile)
- [Audit（SEL）](#auditsel)
- [既知のギャップ（公式が明記）](#既知のギャップ公式が明記)
- [未確認事項](#未確認事項)

---

## 脅威モデル

Crew はAIエージェントに実際のツールアクセス（ファイル読み込み・シェルコマンド・ウェブブラウジング）を与えます。セキュリティモデルは**多層防御**（defense-in-depth）で、各層はプロンプトの指示だけに頼らず、**ランタイムの境界で強制されます**。モデルは信頼できる呼び出し元ではなく、信頼できない入力として扱われます。

## 8つの保護機構（公式の順序）

公式ページは、すべてのツール呼び出しが以下の順序でチェックされると明記しています。

1. **Owner lock** — チャネルGatewayが、メッセージがセッションに到達する前に未認可ユーザーを拒否
2. **Denied commands**（拒否コマンド） — **137パターン**が破壊的操作をブロック（承認を求める前にチェック）
3. **Governance ceiling**（ガバナンス上限） — Policy ∩ Profile（最も厳しい方が勝つ）。エージェントやAppは緩められない
4. **Sensitive path blocking**（機密パスのブロック） — 認証情報のディレクトリ・ファイルはツール呼び出しからアクセス不可
5. **Tool approval**（ツール承認） — 対話的レビュー・信頼の段階的昇格・Autopilot（拒否チェックを通過した後のみ発動）
6. **Input validation**（入力検証） — MCPスキーマ・型チェック・長さ制限・Unicode正規化
7. **OS sandbox**（OSサンドボックス） — LinuxのnamespaceまたはmacOSのSeatbeltによるプロセスレベルのファイルシステム隔離
8. **Output redaction**（出力の秘匿化） — チャットに到達する前に認証情報のパターンを応答から除去

**Audit（SEL）はすべての段階の決定を記録します**（横断的な仕組みであり、順序上の1ゲートではありません）。

## 層数についての注記

> **重要**: リポジトリのアーキテクチャ文書は番号付きの層（Layer 0〜5、全層を貫く2つの制御）として整理していますが、**公式ドキュメントは層数を数値で示していません**（"defense-in-depth: multiple independent layers" という表現のみ）。したがって本ページでは**公式の8機構リスト**（上記）を正としつつ、「公式が何層と述べている」という表現は使いません。

## サンドボックスの3モード

| モード | 設定値 | 隠されるもの | アクセスできるもの | 想定用途 |
|-------|-------|------------|-----------------|---------|
| **標準（既定）** | **`auto`** | `.gnupg` / `.gcloud` / `.azure` / `.docker` | `.aws` / `.ssh` / `.kube` | ほとんどの利用者（git-over-SSHとAWS CLIが使える） |
| 厳格 | `strict` | 上記すべて＋`.aws` / `.ssh` / `.kube` | `~/.ssh/known_hosts` のみ | ロックダウン運用 |
| 無効 | `off` | 何も隠さない | すべて | トレードオフを理解している場合 |

設定は Settings → Security、または `kirocrew config set agent.sandbox <mode>`。**Windowsには OS レベルのサンドボックス層がありません**（公式明記: 「Windows does not currently have this OS-level layer — all other protections still apply」）。Linuxではuser/mount namespaces、macOSではSeatbeltプロファイルを使用します。

> ⚠️ **呼称の食い違い**: README は「Standard, strict, and off modes」と書き、公式docsは「`auto` (default)」と書きます。設定値は `auto`、内部ティア名は `standard` という対応で、本サイトは両方の表記を併記します。

導入時の設定手順は [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md) を参照してください。

## Owner lock

各メッセージングチャネルは認可されたユーザーにロックされます。

| チャネル | 方式 |
|---------|------|
| Slack | `KIROCREW_OWNER_ID`（単一owner） |
| Discord | ユーザーIDの許可リスト（deny-by-default） |
| Telegram | 数値ユーザーIDの許可リスト |
| Teams | Azure AD email/object IDの許可リスト |
| Webex | emailの許可リスト |
| WeCom | userids の許可リスト（または明示的な `allow_all_users` opt-in） |
| WeChat | ユーザーIDの許可リスト（既定は全員拒否） |
| Dashboard | トークン認証（すべてのリクエストが有効なトークンを要求） |

未認可のメッセージは黙って破棄され、監査ログに記録されます。

## ガバナンス（POLICY ∩ PROFILE）

任意のポリシー・プロファイルファイルが**最も厳しい方が勝つ**モデルで合成されます。実行中のAppやエージェントは許可スコープを狭めることはできますが、上限を緩めることはできません。

- **Policy**（ポリシー） — エンタープライズレベルの上限（`~/.kiro/crew/security_policy.json` から読み込み）
- **Profile**（プロファイル） — サーフェス単位・タスク単位の絞り込み（`~/.kiro/crew/profiles/` から読み込み）
- **Effective**（実効） = Policy ∩ Profile（最も厳しい方が勝つ）

ポリシー・プロファイル・admissionファイルは `security._SENSITIVE_HOME_DIRS` に置かれ、**エージェントは自分自身の上限を読み書きできません**。これが上限を無効化不能にする唯一の仕組みです。

CLIから確認できます: `kirocrew policy show` / `kirocrew policy validate` / `kirocrew policy explain`

## Audit（SEL）

すべてのツール呼び出し・承認・拒否・セキュリティイベントが記録されます。追記専用（append-only）で、HMAC-SHA256によるハッシュチェーンJSONL（`<data home>/security_events.jsonl`）です。

CLIから確認できます: `kirocrew security events` / `kirocrew security audit` / `kirocrew security verify`

監査ログはsnapshotに含まれ、ダッシュボードの Settings → Security から確認できます。

## 既知のギャップ（公式が明記）

**リポジトリのアーキテクチャ文書（`security-deep-dive.md`「Known gaps」節）が明記している事実**です。伏せると導入判断を誤らせるため必ず記載します。

1. **既定でネットワーク送信（egress）の制御がない**: サンドボックスは認証情報ファイルを隠しますが、外向きのネットワークアクセスは制限しません。侵害されたエージェントは任意のホストへ非認証情報データを送信できます
2. **コマンドマッチングはbash ASTパーサではない**: regex/tokenizerによる正規化（引用符処理・空文字列結合・`$HOME`/チルダ展開等）で既知の回避手法は防ぎますが、実行時に組み立てられたペイロード（文字列結合・base64・間接的な `eval "$CMD"`）はパターンにマッチしません
3. **監査ダッシュボードがない**: SEL イベントはAPI（`/api/sel/events`）経由で照会できますが、閲覧・フィルタ・アラート用のUIがなく、改ざん検知や異常検知は手動です
4. **エージェント内部からのサンドボックス脱出検知がない**: Gatewayはバックエンドの有無をfail-closedで判定しますが、プロセス内部から閉じ込めが実際に機能しているかを検証する仕組みはありません
5. **Base64認証情報検出には下限がある**: 最小長以上のBase64チャンクのみが復号・再チェックされるため、短い断片や複数メッセージに分割された認証情報は検出を逃れる可能性があります
6. **書き込み保護はCrew自身のトラストルートのみで、ユーザーのシェル起動ファイルは対象外**: 認証情報ディレクトリとキーストーンは読み書きブロックされますが、`~/.bashrc`・`~/.zshrc`のような通常の永続化先はブロックされません（ホームディレクトリ全体をブロックするとエージェントが機能しなくなるため）。承認ゲートと破壊的コマンドルールのみが緩和策です

**（gapsの箇条書きの外側にある追加事項）**: リソース上限はプラットフォームに依存します。fork bombやメモリ暴走を抑えるcgroup v2スコープはLinux＋cgroup delegationを要求し、利用できない環境（macOS・古いLinux・ユーザーセッションなし）では警告付きでno-opとなり、ファイルディスクリプタ上限のみが有効です。

## 未確認事項

- なし。既知ギャップは当初4点として計画されていたが、`security-deep-dive.md`の実測で6点（＋別枠のリソース上限依存）であることを確認した

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
- 導入時の設定: [03_deployment/04_security-hardening.md](../03_deployment/04_security-hardening.md)
- 値の一覧: [04_reference/05_limits.md](../04_reference/05_limits.md)

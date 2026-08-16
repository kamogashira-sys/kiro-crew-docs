# セキュリティのハードニング（導入時の設定）

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/security/>（Page updated 表記あり）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/resource-protection.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）
**出典**（egress既知ギャップの根拠）: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/architecture/security-deep-dive.md>
（参照: 2026-08-16 / commit `64060f3` / 版 v0.2.0）

---

## 📑 このページの内容

- [サンドボックスの設定](#サンドボックスの設定)
- [バックエンド不在時の挙動](#バックエンド不在時の挙動)
- [macOSでの相互排他](#macosでの相互排他)
- [ガバナンスファイルの配置](#ガバナンスファイルの配置)
- [シークレットと環境変数](#シークレットと環境変数)
- [ネットワークegressについて](#ネットワークegressについて)
- [未確認事項](#未確認事項)

---

> セキュリティの概念・機構の解説は [01_features/09_security.md](../01_features/09_security.md) を参照してください。本ページは**導入時の設定手順**に絞ります。

## サンドボックスの設定

```bash
kirocrew config set agent.sandbox <mode>
```

または Settings → Security。設定可能な値は `auto`（既定）／`strict`／`off`（[01_features/09_security.md](../01_features/09_security.md)の表を参照）。

**推奨（公式のBest practices）**: `agent.sandbox` は `auto` または `strict` に保つ。特別な理由がない限り `off` で運用しない。

## バックエンド不在時の挙動

サンドボックスのバックエンドが存在しないホストでは**fail-closed**（無防備に起動せず拒否）します。明示的にopt-inするには:

```bash
kirocrew config set agent.sandbox_allow_unsandboxed_exec true
```

## macOSでの相互排他

macOSでは kiro-cli ≥ 2.13 の内蔵サンドボックスとの**相互排他**が働きます。カーネルが入れ子のサンドボックスプロファイルに対して`EPERM`を返すため、1つのプロセス起動につき有効な層は厳密に1つです。kiro-cli自身の内蔵サンドボックスが有効な場合、Kiro Crewはそちらに処理を委譲します。これは「既定が`off`だから委譲される」のではなく、**設定駆動の決定論的な委譲**です。

## ガバナンスファイルの配置

| ファイル | 用途 |
|---------|------|
| `~/.kiro/crew/security_policy.json` | POLICY（エンタープライズレベルの上限） |
| `~/.kiro/crew/profiles/` | PROFILE（サーフェス単位・タスク単位の絞り込み） |

これらはトラストルートとして `_SENSITIVE_HOME_DIRS` に置かれ、エージェント自身は読み書きできません。

```bash
kirocrew policy show        # 実効ポリシーを表示
kirocrew policy validate    # ポリシーファイルのエラーを検査
kirocrew policy explain     # ツール呼び出しがどう評価されるかを説明
```

## シークレットと環境変数

`.env` は認証情報ロード時とセットアップウィザードで `chmod 600` が強制されます。機密パスとして以下がブロックされます: `~/.aws`・`~/.ssh`・`~/.gnupg`・`~/.gpg`・`~/.config/gcloud`・`~/.azure`・`~/.docker/config.json`・`~/.kube/config`・`~/.npmrc`・`~/.pypirc`・`~/.netrc`・`~/.git-credentials`・Crew自身のトラストルート（`.env`・`sel_hmac.key`・`trust`・`security_events.jsonl`等）。

## ネットワークegressについて

> **重要（既知ギャップの1つ）**: **既定でネットワーク送信（egress）の制御はありません。** サンドボックスは認証情報ファイルを隠しますが、外向きのネットワークアクセスは制限しません。`network.egress` というガバナンススコープでポリシーが設定されている場合はホストを制限できますが、既定でオンのegress境界はありません。ネットワークnamespace（Linux）やトラステッドデスティネーションの許可リストを使ったホストファイアウォールルールで閉じることができます。

## 未確認事項

- なし（本ページの記述は公式securityページと `modules/security.md`、`architecture/resource-protection.md` で確認済み）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/security/>
- リポジトリ: <https://github.com/kirodotdev/KiroCrew/blob/main/docs/system-specs/modules/security.md>
- セキュリティの概念: [01_features/09_security.md](../01_features/09_security.md)
- 設定キー: [04_reference/02_configuration-keys.md](../04_reference/02_configuration-keys.md)

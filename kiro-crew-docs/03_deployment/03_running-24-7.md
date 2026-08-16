# 常駐化・24時間運用

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/docs/crew/running-24-7/>（Page updated 表記あり）
**出典**: <https://kiro.dev/docs/crew/features/multi-instance/>・<https://kiro.dev/docs/crew/features/snapshot/>

---

## 📑 このページの内容

- [ローカルサービス化](#ローカルサービス化)
- [Docker常駐](#docker常駐)
- [マルチインスタンス](#マルチインスタンス)
- [スナップショットと復元](#スナップショットと復元)
- [未確認事項](#未確認事項)

---

Crewは、SlackボットやCronジョブ、Task Runnerがデスクから離れても動き続けるよう、継続運用を想定して設計されています。公式ページが挙げる4つの一般的な運用パターンです。

## ローカルサービス化

最も簡単な方法は組み込みのインストーラです。システムレベルのサービス（Linuxはsystemd、macOSはlaunchd）として登録され、SSH切断後も生き続け、クラッシュ時は自動再起動、起動時は自動起動します。

```bash
kirocrew service install    # ユニットを登録して起動
kirocrew service status     # 稼働状態を確認
kirocrew logs -f            # ライブログを追跡
kirocrew restart            # atomicな再起動（systemd）または unload+load（launchd）
kirocrew service uninstall  # 削除
```

Linuxではインストール時にsudoを1回要求してユニットファイルを書きます。**Gateway自身はユーザー権限で動作**し、rootでは動きません。

**sudoのスコープ**: `kirocrew service install` は `sudo tee`（ユニットファイルの書き込み）と `sudo systemctl ...`（daemon-reload・enable・restart）のみを実行します。`kirocrew`本体・MCP・LLMのコードパスはsudo下では動きません。

サービス化を避けたい場合、`tmux` はSSH切断には耐えますが**クラッシュ時の自動再起動・再起動時の自動起動はしません**。

## Docker常駐

常時稼働のサーバー（Slack/Discordボット、リモートダッシュボード）にはGHCRのマルチアーキイメージを使います。

```bash
docker run -d --name kirocrew \
  -p 127.0.0.1:5476:5476 \
  -v kirocrew-home:/home/kirocrew \
  ghcr.io/kirodotdev/kirocrew:stable
```

初回セットアップは2ステップ:

```bash
# 1. エージェントランタイムにログイン（認証情報はボリュームに残るためアップグレードでも維持）
docker exec -it kirocrew kiro-cli login

# 2. ダッシュボードログインリンクを発行（すべてのリクエストがトークンを要求）
docker exec kirocrew kirocrew token --ttl 2h
```

## マルチインスタンス

複数のCrewインスタンスを運用するための機能です（詳細は公式 `features/multi-instance/` を参照）。

## スナップショットと復元

Memory（`memory.db`・`memory_index.db`）とワークスペース（`workspace/memory/`）はスナップショットに含まれます。

```bash
kirocrew snapshot                     # 既定は ~/.kiro/crew/snapshots
kirocrew restore snapshot.tar.gz      # replace/mergeを自動判定
```

## 未確認事項

- マルチインスタンスの詳細な運用手順（公式ページの参照のみで、本サイトでは概要にとどめる）

## 関連リンク

- 公式: <https://kiro.dev/docs/crew/running-24-7/>、<https://kiro.dev/docs/crew/features/multi-instance/>、<https://kiro.dev/docs/crew/features/snapshot/>
- CLIコマンド: [04_reference/01_cli-commands.md](../04_reference/01_cli-commands.md)

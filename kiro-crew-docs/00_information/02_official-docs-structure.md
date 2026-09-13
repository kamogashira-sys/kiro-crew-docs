# 公式サイトの構造

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/sitemap.xml>（実測）／<https://kiro.dev/docs/crew/>
（参照: 2026-08-22 / commit `21584ea` / 版 v0.3.0）

---

## 📑 このページの内容

- [49ページの構造](#49ページの構造)
- [`changelog/crew/`は存在しない](#changelogcrewは存在しない)
- [`.md` companionの実在](#md-companionの実在)
- [未確認事項](#未確認事項)

---

## 49ページの構造

`kiro.dev/docs/crew/` 配下は**49ページ**（sitemap.xml実測）。内訳は**トップ1＋カテゴリ索引5＋カテゴリ配下37＋単独6＝49**です。

```
/docs/crew/                                     ← トップ1
├── apps/            (+ aws-control, build-first-app, manifest, publishing, sdk)
├── capabilities/     (+ agent-templates, agents, hooks, mcp-tools, prompts, skills, steering)
├── chat/             (+ artifacts, message-controls, prompt-optimizer, sessions, voice)
├── features/         (+ agent-backends, artifact-deploy, browser, computer-use, cron,
│                        knowledge, memory, multi-instance, snapshot, subagents,
│                        task-runner, workflows)
├── interfaces/        (+ cli-reference, discord, slack, teams, telegram, webex, wechat, wecom)
├── configuration/                              ┐
├── installation/                               │
├── running-24-7/                               ├ 単独6ページ
├── security/                                   │
├── system/                                     │
└── troubleshooting/                            ┘
```

> **v0.6.0での増加（43→49・新規6件／消滅0件）**
>
> | 新規ページ | 本サイトの担当 |
> |---|---|
> | `features/agent-backends/` | [01_features/15_agent-backends.md](../01_features/15_agent-backends.md) |
> | `features/computer-use/` | [01_features/13_computer-and-browser.md](../01_features/13_computer-and-browser.md) |
> | `features/browser/` | 同上 |
> | `features/workflows/` | [01_features/17_workflows.md](../01_features/17_workflows.md) |
> | `apps/aws-control/` | [01_features/16_aws-control.md](../01_features/16_aws-control.md) |
> | `system/` | [03_deployment/03_running-24-7.md](../03_deployment/03_running-24-7.md)（System & storage 節） |
>
> `features/computer-use/`・`features/browser/` は **v0.4.1 まで公式ページが存在せず**、モジュール仕様書のみが出典でした。単独ページは5→6（`system/` の追加）です。1対1の割当は `05_meta/ledger-official-pages.md` で管理しています（非公開）。

## `changelog/crew/`は存在しない

Kiro公式サイトにはCrew用changelogパスがありません（changelogのカテゴリはcli/ide/models/web/generalのみ）。更新履歴の一次情報はGitHub（CHANGELOG.md・Releases）のみです。

## `.md` companionの実在

**49ページ全件に `.md` companion が存在します**（末尾スラッシュを除去して `.md` を付与するURL形式。`content-type: text/markdown` で確認済み）。値の取得はHTMLを正としますが、テキスト抽出にはcompanionも利用可能です。

## 未確認事項

- なし（本ページの記述はsitemap.xml実測と49ページの`.md` companion取得結果で確認済み）

## 関連リンク

- sitemap: <https://kiro.dev/sitemap.xml>
- 公式ドキュメント: <https://kiro.dev/docs/crew/>
- 情報源の使い分け: [03_information-sources.md](03_information-sources.md)

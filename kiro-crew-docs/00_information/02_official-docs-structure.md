# 公式サイトの構造

> **本ページは Kiro Crew（OSS）の仕様です。**

**出典**: <https://kiro.dev/sitemap.xml>（実測）／<https://kiro.dev/docs/crew/>
（参照: 2026-08-16）

---

## 📑 このページの内容

- [43ページの構造](#43ページの構造)
- [`changelog/crew/`は存在しない](#changelogcrewは存在しない)
- [`.md` companionの実在](#md-companionの実在)
- [未確認事項](#未確認事項)

---

## 43ページの構造

`kiro.dev/docs/crew/` 配下は**43ページ**（sitemap.xml実測）。5カテゴリ＋単独5ページに分類されます。

```
/docs/crew/
├── apps/            (+ build-first-app, manifest, publishing, sdk)
├── capabilities/     (+ agent-templates, agents, hooks, mcp-tools, prompts, skills, steering)
├── chat/             (+ artifacts, message-controls, prompt-optimizer, sessions, voice)
├── configuration/
├── features/         (+ artifact-deploy, cron, knowledge, memory, multi-instance,
│                        snapshot, subagents, task-runner)
├── installation/
├── interfaces/        (+ cli-reference, discord, slack, teams, telegram, webex, wechat, wecom)
├── running-24-7/
├── security/
└── troubleshooting/
```

## `changelog/crew/`は存在しない

`https://kiro.dev/changelog/crew/` は**存在しません**（changelogのカテゴリはcli/ide/models/web/generalのみ）。更新履歴の一次情報はGitHub（CHANGELOG.md・Releases）のみです。

## `.md` companionの実在

**43ページ全件に `.md` companion が存在します**（末尾スラッシュを除去して `.md` を付与するURL形式。`content-type: text/markdown` で確認済み）。値の取得はHTMLを正としますが、テキスト抽出にはcompanionも利用可能です。

## 未確認事項

- なし（本ページの記述はsitemap.xml実測と43ページの`.md` companion取得結果で確認済み）

## 関連リンク

- sitemap: <https://kiro.dev/sitemap.xml>
- 公式ドキュメント: <https://kiro.dev/docs/crew/>
- 情報源の使い分け: [03_information-sources.md](03_information-sources.md)

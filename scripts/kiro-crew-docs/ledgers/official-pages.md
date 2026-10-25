# 公式49ページ 1対1割当台帳

- **取得日**: 2026-10-25（v0.9.0対応で再取得。URL集合は 2026-10-04 取得分と完全一致・新規0・消滅0。担当ページの変更なし。49ページ中24ページで Page updated と `.md` sha256 が変化）
- **出典**: `https://kiro.dev/sitemap.xml`（`docs/crew/` 配下の抽出。49件）
- **検証**: `check-coverage.py` の入力データ。49行すべてに担当ページまたは不扱い理由があること（未割当0件）を機械検証する
- **公式 Page updated・`.md` sha256 列（固定時点）**: v0.9.0 タグのスナップショットの `PIN.json`（ref `v0.9.0`・commit `99e6253`・reference_date 2026-10-25）の `official_page_updated`・`official_md_sha256` の値。`measure-ssot.py --page-updated-diff`・`--expect-ledger-current`（`make check-kiro-crew-ledger-current`）が、新しく取得した `PIN.json` と URL ごとに比べる。版更新では対象版の `PIN.json` の値で更新する。sha256 は `.md` companion の内容から計算した値だけを置き、内容そのものは置かない

> **v0.3.0再確認（2026-08-22・v0.3.0タグ`21584ea`）**: sitemap実測43件＝台帳記録44行（ヘッダ含む）で一致確認済み（変化なし・S1）。（v0.3.0 対応。コミット `aaaefa9`）
>
> **v0.6.0再構築（2026-09-13・v0.6.0タグ`8575209`）**: sitemap実測**49件**（43→49、**新規6件・消滅0件**）。新規は `features/agent-backends/`・`features/computer-use/`・`features/browser/`・`features/workflows/`・`apps/aws-control/`・`system/`。番号は振り直したため、v0.4.1以前の台帳の #N とは対応しない。（v0.6.0 対応。コミット `1333ec1`）

| # | 公式URL | 担当ページ（`01_features/` 配下） | 備考 | 公式 Page updated（固定時点） | `.md` sha256（固定時点） |
|---|--------|--------------------------------|------|---|---|
| 1 | `/docs/crew/` | `01_architecture.md` | トップページ。製品概要 | 2026-10-20 | `ef0deb99637d4edf8bc2c23fa783d9e74c2326a5c7cae1899910609f54f5d6b6` |
| 2 | `/docs/crew/installation/` | `03_deployment/01_installation.md` | 01_features 外（導入セクション） | 2026-10-20 | `5fa203e59aa1f1a9e4d41421199d916719ddc915b3cd8744fc1b22e217ee58c0` |
| 3 | `/docs/crew/running-24-7/` | `03_deployment/03_running-24-7.md` | 同上 | 2026-08-04 | `f5769038a6cf80a291d948b4a6756f5f4f4474c098cd7d3039deeb1e429eb013` |
| 4 | `/docs/crew/chat/` | `03_chat.md` | チャット体験の索引 | 2026-10-20 | `c6f1c9f92417bc574bbec77c553eabc514e97ad0aae4e7f0c292ef176dac8825` |
| 5 | `/docs/crew/chat/sessions/` | `02_sessions.md` |  | 2026-10-20 | `f8ee06d6880c72737e73bca2854851523683304c03888b61722ffb2eeb6b800e` |
| 6 | `/docs/crew/chat/message-controls/` | `03_chat.md` |  | 2026-10-20 | `6d176a9fd9841e88112309d8b0448b96d76c84be8b21ad2db5faa10971a035e4` |
| 7 | `/docs/crew/chat/prompt-optimizer/` | `03_chat.md` |  | 2026-08-04 | `b832eb728882694544a5c0b718e2d96a076d7d941f9142d02f7bec958b4f6078` |
| 8 | `/docs/crew/chat/voice/` | `03_chat.md` |  | 2026-10-20 | `11fbec7e3ed23300a40f654f766b3ef29fe2a1347cb86502b18b331fb65db114` |
| 9 | `/docs/crew/chat/artifacts/` | `12_artifacts.md` | チャット内Artifacts（①） | 2026-09-12 | `42340dd168a224d4be3a6fd256907002946ff8d6fc87ca0dedbcd5d46b2d75ad` |
| 10 | `/docs/crew/capabilities/` | `07_agents-skills-steering.md` | Agent Capabilities の索引 | 2026-09-12 | `5c07d3e67e1ae947d92b0d13da220262d363458ee516b6594af1aaa7360dce4f` |
| 11 | `/docs/crew/capabilities/agents/` | `07_agents-skills-steering.md` |  | 2026-10-20 | `eb846a5ddc5e7b74e59aef8c2b11f900f52c71e1250e73ea855e5c47519af004` |
| 12 | `/docs/crew/capabilities/agent-templates/` | `07_agents-skills-steering.md` |  | 2026-10-12 | `eb4149bf1a1e5960b38a8a88c89abf7ddb1812eeb88f1ee2193dbb3175b00713` |
| 13 | `/docs/crew/capabilities/mcp-tools/` | `08_mcp-integration.md` |  | 2026-08-31 | `e3cff993355b8156b0d23a36be7967e7233674c450c984a140a6009cb1d6f911` |
| 14 | `/docs/crew/capabilities/skills/` | `07_agents-skills-steering.md` |  | 2026-09-25 | `b1cccd1377db35a40e3ea837278576df1ca820855bb567a0f631f692babfcb46` |
| 15 | `/docs/crew/capabilities/steering/` | `07_agents-skills-steering.md` |  | 2026-10-12 | `34e75f1c8329c6b16a513090e850450c75383f83d3578ea98916b5c065d6ce52` |
| 16 | `/docs/crew/capabilities/hooks/` | `07_agents-skills-steering.md` |  | 2026-10-12 | `d127c9ac83a74f64965fa18ade9987b2eec2075b294782c82f19da50a40cc99c` |
| 17 | `/docs/crew/capabilities/prompts/` | `07_agents-skills-steering.md` |  | 2026-09-12 | `10ec63b5e8fdb48ef088aca59400c1bba9e7042b9f6f55a3c8902d18fbf25cf0` |
| 18 | `/docs/crew/features/` | `06_autonomy.md` | Features の索引（cron/task-runner/subagents 中心） | 2026-09-25 | `f109569999e87c2f94c98c0222834f1e03829047a74cabe43c0ec0ae0ab093bc` |
| 19 | `/docs/crew/features/subagents/` | `06_autonomy.md` |  | 2026-09-30 | `9e4ebbad99e7da2b6f872c0dcf7c193ed66f86bb14ec212070682d396d8aaeb6` |
| 20 | `/docs/crew/features/cron/` | `06_autonomy.md` | 表示名「Scheduling」 | 2026-10-20 | `66c894ec4652546143e31782584f37765d01e4d06dd5aca54ee3e39066c56708` |
| 21 | `/docs/crew/features/artifact-deploy/` | `12_artifacts.md` | Artifact Deploy（②）。表示名「Artifacts」 | 2026-09-12 | `62a02e3e142ea08d55e7b325219f9a057e1e6a9a51bbfd1e3f3d8125c4d4e2c7` |
| 22 | `/docs/crew/features/multi-instance/` | `03_deployment/03_running-24-7.md` |  | 2026-10-20 | `a031db04182045e8e3af327273ea3442d3208ea7af449181783494146875887c` |
| 23 | `/docs/crew/features/task-runner/` | `06_autonomy.md` |  | 2026-09-25 | `c6f2c0b022167b6c0608bfb30a88d80ad2ede75110bc4e063793c7c43bb8d192` |
| 24 | `/docs/crew/features/memory/` | `04_memory-and-learning.md` |  | 2026-10-20 | `ff9a6b3cdeafca5cfbffe4f8c0c9feede5ea15dce19067c6d726aa993e1b7970` |
| 25 | `/docs/crew/features/knowledge/` | `05_knowledge-library.md` |  | 2026-09-25 | `982079d2667e6d1c1feddd976aefeff98f5a52d8500f9597af856f70b1f03385` |
| 26 | `/docs/crew/features/snapshot/` | `03_deployment/03_running-24-7.md` | 表示名「Snapshot & restore」 | 2026-09-11 | `a9953aad7df19756bddc90bacde46e9f2ee2db0ea3faedac3bbf0c461582dd24` |
| 27 | `/docs/crew/features/agent-backends/` | `15_agent-backends.md` | **v0.6.0で公式に新設**。Preview・ハーネス選択 | 2026-10-12 | `e88e3ebca80e11ba97b618449e8c27bc97e92f8643ccf5c084ba5977637fd59b` |
| 28 | `/docs/crew/features/computer-use/` | `13_computer-and-browser.md` | **v0.6.0で公式に新設**（従来はモジュール仕様書のみが出典） | 2026-08-31 | `a098f7569f76543fe9bdbad59a892fef5ec567fdc809122bb31409ed310d1902` |
| 29 | `/docs/crew/features/browser/` | `13_computer-and-browser.md` | **v0.6.0で公式に新設**（従来はモジュール仕様書のみが出典） | 2026-09-25 | `a8a3c2ef055126a5c49f987431e694c454f0752204c7b53f65e45726267e8249` |
| 30 | `/docs/crew/features/workflows/` | `17_workflows.md` | **v0.6.0で公式に新設**。conductor・ワークフローライブラリ | 2026-10-12 | `36b8be4cbf5688dd06c3aabdabab0781cf49e3e293df2ab1a3635808f65a26a7` |
| 31 | `/docs/crew/interfaces/` | `11_interfaces.md` | Interfaces の索引 | 2026-09-30 | `d7fde0a6da67a696d3b8c7dc08493a7e1b1db521dbc02ea849ff4f7c5a87323a` |
| 32 | `/docs/crew/interfaces/slack/` | `11_interfaces.md` |  | 2026-10-20 | `fd84039d1e0de45c5fe3d4521636b0d455cc6310b17446ab80d452fbcb051f02` |
| 33 | `/docs/crew/interfaces/discord/` | `11_interfaces.md` |  | 2026-09-25 | `743a7ddffdb1bd18a1433ec0268bf22ea731602728e57d89ac3f27c1d31c8da7` |
| 34 | `/docs/crew/interfaces/telegram/` | `11_interfaces.md` |  | 2026-10-20 | `60ad0bd3d8baa9b91151a839c68c8805f3a323bca4a2d2d0233b9242584c50e1` |
| 35 | `/docs/crew/interfaces/teams/` | `11_interfaces.md` |  | 2026-10-20 | `4ed63e028c562631cb096c6829e4cf0e3c46cda0b3fcfd105d29a6da6f6b563e` |
| 36 | `/docs/crew/interfaces/webex/` | `11_interfaces.md` |  | 2026-09-25 | `b33624c609deeb87c14140774e6b2b1f350e0eecb42e3e5bb516da63ef01e471` |
| 37 | `/docs/crew/interfaces/wecom/` | `11_interfaces.md` |  | 2026-10-12 | `9519c9229f4f5a960b63e780669c9a17d8e08e7bb1b1172e0ebe1f971491d0eb` |
| 38 | `/docs/crew/interfaces/wechat/` | `11_interfaces.md` |  | 2026-09-25 | `bd3298223f4938e7a21b330e9b8152ca05d99e4d4ead567c775b34d75b1760d0` |
| 39 | `/docs/crew/interfaces/cli-reference/` | `04_reference/01_cli-commands.md` | 01_features 外 | 2026-10-20 | `5fcad3e3383c2cf9da4d1d2e1edcb1c114be8d92312785de31eb567a4c7c3d31` |
| 40 | `/docs/crew/apps/` | `10_apps.md` | Apps の索引 | 2026-10-12 | `7dbcde0c38d9e00aaa2926700b8d0f534fa795cf2e6cb340628213c7a94f96bc` |
| 41 | `/docs/crew/apps/build-first-app/` | `10_apps.md` |  | 2026-08-04 | `9c96251d9b62f1a5de11bbc4fb958eeb1bcfd7200d3191a78fe5186f8b69dd20` |
| 42 | `/docs/crew/apps/manifest/` | `10_apps.md` |  | 2026-09-25 | `7330ac5563fff3847311d7a6c86b8d205a85614712e511afdc4fd5cd9f5a9e80` |
| 43 | `/docs/crew/apps/sdk/` | `10_apps.md` |  | 2026-09-25 | `4c83feea3139ee6e067a7826ab70c1a35a2feba806475580f1ac38da6c035f67` |
| 44 | `/docs/crew/apps/publishing/` | `10_apps.md` |  | 2026-09-25 | `befee13d25cb04658cc58b5bab25187e4aaa389a6613d079dec131abaf907be0` |
| 45 | `/docs/crew/apps/aws-control/` | `16_aws-control.md` | **v0.6.0で公式に新設**。builtin App・既定オフ | 2026-09-12 | `9fb7c06ddeae772c6721459759f68cedc05e623e6d25341500404e7af91f57f7` |
| 46 | `/docs/crew/configuration/` | `04_reference/02_configuration-keys.md` | 01_features 外 | 2026-10-20 | `8c0381d6cca9f045391cb21bbc3747fe49a58526b53e1d7a5eb1e1f3e4f4bfa0` |
| 47 | `/docs/crew/security/` | `09_security.md` ＋ `03_deployment/04_security-hardening.md` | 二層構成 | 2026-10-12 | `7b1d0be3607ea7c1f403e03aab393dbf1ed4cedfe031193ab0fe179e047fa87a` |
| 48 | `/docs/crew/system/` | `03_deployment/03_running-24-7.md` | **v0.6.0で公式に新設**。System & storage 節 | 2026-10-20 | `ad970b3eb1c4d083eea8321f2efd30d3f898e0655eb81f87c01a5f18683dd737` |
| 49 | `/docs/crew/troubleshooting/` | `03_deployment/05_troubleshooting.md` | 01_features 外 | 2026-09-12 | `0c9ac2f2db6e6c6299ccf8848c1b319d25f166a35eb13626f9d8c67f00a0f69a` |

## 検証結果

- **49行すべてに担当ページが割り当てられている（未割当0件）**
- **v0.6.0 で前提が変わった点**: Computer Use・ブラウザ自動化（`13_computer-and-browser.md`）は v0.4.1 まで「公式ページに専用ページが無く、モジュール仕様書 `modules/{computer-use,browser}.md` のみが出典」でしたが、**v0.6.0 で公式に `features/computer-use/`・`features/browser/` が新設**され、割当対象になりました
- テレメトリ（`06_telemetry-and-privacy.md`）は引き続き**公式49ページに専用ページが無く**、README の独立セクションと `modules/metrics.md`・`guides/telemetry-otlp-export.md` が出典です（割当対象外）
- `system/`（v0.6.0新設）は `03_deployment/03_running-24-7.md` の「System & storage」節が担当します

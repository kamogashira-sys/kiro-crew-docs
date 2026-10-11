# 公式49ページ 1対1割当台帳（Phase 0-7）

- **取得日**: 2026-10-04（v0.7.2対応で再取得。URL集合は 2026-09-13 取得分と完全一致・新規0・消滅0。担当ページの変更なし）
- **出典**: `https://kiro.dev/sitemap.xml`（`docs/crew/` 配下の抽出。49件）
- **検証**: `check-coverage.py` の入力データ。49行すべてに担当ページまたは不扱い理由があること（未割当0件）を機械検証する
- **公式 Page updated・`.md` sha256 列（固定時点）**: v0.7.2 タグのスナップショットの `PIN.json`（ref `v0.7.2`・commit `c67c506`・reference_date 2026-10-11）の `official_page_updated`・`official_md_sha256` の値。`measure-ssot.py --page-updated-diff`・`--expect-ledger-current`（`make check-kiro-crew-ledger-current`）が、新しく取得した `PIN.json` と URL ごとに比べる。版更新では対象版の `PIN.json` の値で更新する。sha256 は `.md` companion の内容から計算した値だけを置き、内容そのものは置かない

> **v0.3.0再確認（2026-08-22・v0.3.0タグ`21584ea`）**: sitemap実測43件＝台帳記録44行（ヘッダ含む）で一致確認済み（変化なし・S1）。（v0.3.0 対応。コミット `aaaefa9`）
>
> **v0.6.0再構築（2026-09-13・v0.6.0タグ`8575209`）**: sitemap実測**49件**（43→49、**新規6件・消滅0件**）。新規は `features/agent-backends/`・`features/computer-use/`・`features/browser/`・`features/workflows/`・`apps/aws-control/`・`system/`。番号は振り直したため、v0.4.1以前の台帳の #N とは対応しない。（v0.6.0 対応。コミット `1333ec1`）

| # | 公式URL | 担当ページ（`01_features/` 配下） | 備考 | 公式 Page updated（固定時点） | `.md` sha256（固定時点） |
|---|--------|--------------------------------|------|---|---|
| 1 | `/docs/crew/` | `01_architecture.md` | トップページ。製品概要 | 2026-08-31 | `1cbcc8d5788520c5b836e46f569234c02b75983dd806cb7d5695c92b97e74a2f` |
| 2 | `/docs/crew/installation/` | `03_deployment/01_installation.md` | 01_features 外（導入セクション） | 2026-09-25 | `fa75379bb636b3959e8c216320ac89552f1e81a1f92b7fa4fd9667537b7cdaa3` |
| 3 | `/docs/crew/running-24-7/` | `03_deployment/03_running-24-7.md` | 同上 | 2026-08-04 | `f5769038a6cf80a291d948b4a6756f5f4f4474c098cd7d3039deeb1e429eb013` |
| 4 | `/docs/crew/chat/` | `03_chat.md` | チャット体験の索引 | 2026-09-25 | `ead8795d6bcdf272936a1a5528308dff6a446e984510bede389f4949a5846f86` |
| 5 | `/docs/crew/chat/sessions/` | `02_sessions.md` |  | 2026-09-25 | `597aa7e0fe3f15f2f3ad60b8d546b735fa24a2d6f11e39591473b6ec96cf43d9` |
| 6 | `/docs/crew/chat/message-controls/` | `03_chat.md` |  | 2026-09-25 | `f6a385d855991732348cc5ba42b20a70e957fc7c67d7d734f0e070a79e037783` |
| 7 | `/docs/crew/chat/prompt-optimizer/` | `03_chat.md` |  | 2026-08-04 | `b832eb728882694544a5c0b718e2d96a076d7d941f9142d02f7bec958b4f6078` |
| 8 | `/docs/crew/chat/voice/` | `03_chat.md` |  | 2026-09-12 | `b06c0e1fe032dbb8d1b6e636afc27e107540a1feccdd2a21b78a43b404237fe1` |
| 9 | `/docs/crew/chat/artifacts/` | `12_artifacts.md` | チャット内Artifacts（①） | 2026-09-12 | `42340dd168a224d4be3a6fd256907002946ff8d6fc87ca0dedbcd5d46b2d75ad` |
| 10 | `/docs/crew/capabilities/` | `07_agents-skills-steering.md` | Agent Capabilities の索引 | 2026-09-12 | `5c07d3e67e1ae947d92b0d13da220262d363458ee516b6594af1aaa7360dce4f` |
| 11 | `/docs/crew/capabilities/agents/` | `07_agents-skills-steering.md` |  | 2026-09-25 | `a2ae6d27a2195e317933d74ff2a20e92e6706a8afbf721d1eaba7cf9ea8226db` |
| 12 | `/docs/crew/capabilities/agent-templates/` | `07_agents-skills-steering.md` |  | 2026-09-25 | `e1dbd33e7d747d13f1cd53469561de6170d672047aea67e9dcdec783be55b857` |
| 13 | `/docs/crew/capabilities/mcp-tools/` | `08_mcp-integration.md` |  | 2026-08-31 | `e3cff993355b8156b0d23a36be7967e7233674c450c984a140a6009cb1d6f911` |
| 14 | `/docs/crew/capabilities/skills/` | `07_agents-skills-steering.md` |  | 2026-09-25 | `b1cccd1377db35a40e3ea837278576df1ca820855bb567a0f631f692babfcb46` |
| 15 | `/docs/crew/capabilities/steering/` | `07_agents-skills-steering.md` |  | 2026-09-12 | `8173d8d88f5d3382cd270a53b9493cd7243c232f80d3e4156bc34d97536c41ca` |
| 16 | `/docs/crew/capabilities/hooks/` | `07_agents-skills-steering.md` |  | 2026-08-04 | `1a78a77a20aa310f9f3c57cbabb36c587fec4db4007fac0bb894b28fe465cb79` |
| 17 | `/docs/crew/capabilities/prompts/` | `07_agents-skills-steering.md` |  | 2026-09-12 | `10ec63b5e8fdb48ef088aca59400c1bba9e7042b9f6f55a3c8902d18fbf25cf0` |
| 18 | `/docs/crew/features/` | `06_autonomy.md` | Features の索引（cron/task-runner/subagents 中心） | 2026-09-25 | `f109569999e87c2f94c98c0222834f1e03829047a74cabe43c0ec0ae0ab093bc` |
| 19 | `/docs/crew/features/subagents/` | `06_autonomy.md` |  | 2026-09-30 | `9e4ebbad99e7da2b6f872c0dcf7c193ed66f86bb14ec212070682d396d8aaeb6` |
| 20 | `/docs/crew/features/cron/` | `06_autonomy.md` | 表示名「Scheduling」 | 2026-09-25 | `757cabd105da8a8f986558359f895634b18c97d51d6ea45f71eaa1bb884ea3b9` |
| 21 | `/docs/crew/features/artifact-deploy/` | `12_artifacts.md` | Artifact Deploy（②）。表示名「Artifacts」。**Rev 1 で唯一未割当だったページ** | 2026-09-12 | `62a02e3e142ea08d55e7b325219f9a057e1e6a9a51bbfd1e3f3d8125c4d4e2c7` |
| 22 | `/docs/crew/features/multi-instance/` | `03_deployment/03_running-24-7.md` |  | 2026-09-25 | `01e9d34db8e6767368723780ae1d2a312a23eb96ab92ae436ed17feed0c5b13b` |
| 23 | `/docs/crew/features/task-runner/` | `06_autonomy.md` |  | 2026-09-25 | `c6f2c0b022167b6c0608bfb30a88d80ad2ede75110bc4e063793c7c43bb8d192` |
| 24 | `/docs/crew/features/memory/` | `04_memory-and-learning.md` |  | 2026-08-04 | `89ff511eaf8d75a96b586fbff91a2d2bee457c94416e895987119f44fdb2434b` |
| 25 | `/docs/crew/features/knowledge/` | `05_knowledge-library.md` |  | 2026-09-25 | `982079d2667e6d1c1feddd976aefeff98f5a52d8500f9597af856f70b1f03385` |
| 26 | `/docs/crew/features/snapshot/` | `03_deployment/03_running-24-7.md` | 表示名「Snapshot & restore」 | 2026-09-11 | `a9953aad7df19756bddc90bacde46e9f2ee2db0ea3faedac3bbf0c461582dd24` |
| 27 | `/docs/crew/features/agent-backends/` | `15_agent-backends.md` | **v0.6.0で公式に新設**。Preview・ハーネス選択 | 2026-09-25 | `b31d190d2673e6b84d51e216a47a1c36ae2748a849d46630da9e3bb279bcbdc8` |
| 28 | `/docs/crew/features/computer-use/` | `13_computer-and-browser.md` | **v0.6.0で公式に新設**（従来はモジュール仕様書のみが出典） | 2026-08-31 | `a098f7569f76543fe9bdbad59a892fef5ec567fdc809122bb31409ed310d1902` |
| 29 | `/docs/crew/features/browser/` | `13_computer-and-browser.md` | **v0.6.0で公式に新設**（従来はモジュール仕様書のみが出典） | 2026-09-25 | `a8a3c2ef055126a5c49f987431e694c454f0752204c7b53f65e45726267e8249` |
| 30 | `/docs/crew/features/workflows/` | `17_workflows.md` | **v0.6.0で公式に新設**。conductor・ワークフローライブラリ | 2026-09-25 | `cc34b35f813ee65fc4087e83663bbf23623c74f683e38cd052be276c1b9c91c4` |
| 31 | `/docs/crew/interfaces/` | `11_interfaces.md` | Interfaces の索引 | 2026-09-30 | `d7fde0a6da67a696d3b8c7dc08493a7e1b1db521dbc02ea849ff4f7c5a87323a` |
| 32 | `/docs/crew/interfaces/slack/` | `11_interfaces.md` |  | 2026-09-25 | `b7c6a7fb6979ae3e5901d05e83c399086c2ac5b594b2ab605cbc13658ceb40c3` |
| 33 | `/docs/crew/interfaces/discord/` | `11_interfaces.md` |  | 2026-09-25 | `743a7ddffdb1bd18a1433ec0268bf22ea731602728e57d89ac3f27c1d31c8da7` |
| 34 | `/docs/crew/interfaces/telegram/` | `11_interfaces.md` |  | 2026-09-25 | `5a36d0b8f4141a121d088dfa3ca01ca0e6fc0ed40122a18cac62320d92bd7e05` |
| 35 | `/docs/crew/interfaces/teams/` | `11_interfaces.md` |  | 2026-09-25 | `fbfdc96b5a2e327893a0d673d4d38aa46a5e99f09bfb73b110b63013d0ee75f0` |
| 36 | `/docs/crew/interfaces/webex/` | `11_interfaces.md` |  | 2026-09-25 | `b33624c609deeb87c14140774e6b2b1f350e0eecb42e3e5bb516da63ef01e471` |
| 37 | `/docs/crew/interfaces/wecom/` | `11_interfaces.md` |  | 2026-09-25 | `e594ec22eb13a538a0cf402cfe0e5795a3163edf9dd109fda7c12afe0b4e7aaa` |
| 38 | `/docs/crew/interfaces/wechat/` | `11_interfaces.md` |  | 2026-09-25 | `bd3298223f4938e7a21b330e9b8152ca05d99e4d4ead567c775b34d75b1760d0` |
| 39 | `/docs/crew/interfaces/cli-reference/` | `04_reference/01_cli-commands.md` | 01_features 外 | 2026-09-25 | `6559b17630d31dc0b912659643a6132bfb56d8c52f3448d3862e22459e04888b` |
| 40 | `/docs/crew/apps/` | `10_apps.md` | Apps の索引 | 2026-09-25 | `4657ae4e7e70076046f9ec206b8ad606421950564ad37099e48a84f11106ec17` |
| 41 | `/docs/crew/apps/build-first-app/` | `10_apps.md` |  | 2026-08-04 | `9c96251d9b62f1a5de11bbc4fb958eeb1bcfd7200d3191a78fe5186f8b69dd20` |
| 42 | `/docs/crew/apps/manifest/` | `10_apps.md` |  | 2026-09-25 | `7330ac5563fff3847311d7a6c86b8d205a85614712e511afdc4fd5cd9f5a9e80` |
| 43 | `/docs/crew/apps/sdk/` | `10_apps.md` |  | 2026-09-25 | `4c83feea3139ee6e067a7826ab70c1a35a2feba806475580f1ac38da6c035f67` |
| 44 | `/docs/crew/apps/publishing/` | `10_apps.md` |  | 2026-09-25 | `befee13d25cb04658cc58b5bab25187e4aaa389a6613d079dec131abaf907be0` |
| 45 | `/docs/crew/apps/aws-control/` | `16_aws-control.md` | **v0.6.0で公式に新設**。builtin App・既定オフ | 2026-09-12 | `9fb7c06ddeae772c6721459759f68cedc05e623e6d25341500404e7af91f57f7` |
| 46 | `/docs/crew/configuration/` | `04_reference/02_configuration-keys.md` | 01_features 外 | 2026-09-25 | `3493696c59c657b2736fbff4e4fc10b02e1568d67ffd52a6ac1e262569d6c398` |
| 47 | `/docs/crew/security/` | `09_security.md` ＋ `03_deployment/04_security-hardening.md` | 二層構成（§4.7） | 2026-09-30 | `dba2db95c4669e4d113040750b797ed6dbc6739c9348a527d54fe7cce1be8d34` |
| 48 | `/docs/crew/system/` | `03_deployment/03_running-24-7.md` | **v0.6.0で公式に新設**。System & storage 節 | 2026-09-25 | `d370dd18113ea68890186ef182f0dff3db6c457a1a6428541c6da609a9b99fd3` |
| 49 | `/docs/crew/troubleshooting/` | `03_deployment/05_troubleshooting.md` | 01_features 外 | 2026-09-12 | `0c9ac2f2db6e6c6299ccf8848c1b319d25f166a35eb13626f9d8c67f00a0f69a` |

## 検証結果

- **49行すべてに担当ページが割り当てられている（未割当0件）**
- **v0.6.0 で前提が変わった点**: Computer Use・ブラウザ自動化（`13_computer-and-browser.md`）は v0.4.1 まで「公式ページに専用ページが無く、モジュール仕様書 `modules/{computer-use,browser}.md` のみが出典」でしたが、**v0.6.0 で公式に `features/computer-use/`・`features/browser/` が新設**され、割当対象になりました
- テレメトリ（`06_telemetry-and-privacy.md`）は引き続き**公式49ページに専用ページが無く**、README の独立セクションと `modules/metrics.md`・`guides/telemetry-otlp-export.md` が出典です（割当対象外）
- `system/`（v0.6.0新設）は `03_deployment/03_running-24-7.md` の「System & storage」節が担当します
- Rev 1 で未割当だった `#21 features/artifact-deploy`（現 #21）は `12_artifacts.md` に割当済み

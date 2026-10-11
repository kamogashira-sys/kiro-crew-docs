# builtin App 20件 台帳

- **取得日**: 2026-08-16
- **commit SHA**: `64060f3ffecdf4aebeb764b4e3108e7375249ad8`
- **出典**: `src/kiro_crew/apps/builtins/*/app.json`（clone --depth 1 で取得したソース全件を機械抽出）
- **検証コマンド**: `python3` で `json.load` し `displayName` / `defaultEnabled` を抽出（本ファイル下部に再現コマンドを記載）

> **v0.3.0再確認（2026-08-22・v0.3.0タグ`21584ea`）**: `ls -d src/kiro_crew/apps/builtins/*/`実測20件＝台帳記録21行（ヘッダ含む）で一致確認済み（変化なし・S12）。`defaultEnabled:true`は`projects`のみ（変化なし）。`personal_shopper`・`issue_radar`は実在しともに`defaultEnabled: false`。main HEAD `32872ff`に存在する`command_bar`・`design_tweak`（v0.4.0系）は`21584ea`に不在であり本台帳に含めない。（v0.3.0 対応。コミット `aaaefa9`）
>
> **⚠️ 重要な訂正**: CHANGELOG v0.3.0節は`personal_shopper`・`issue_radar`を「Two new apps」（2つの新しいApp）として発表しているが、**両Appの実装は既存**であることを`64060f3`（v0.2.0時点）のフルクローンで確認した。`personal_shopper`の`app.json`は`64060f3`と`21584ea`で**完全に同一（差分0）**。`issue_radar`は`displayName: "Issue Radar"`のまま変更なしで、**v0.1.2のCHANGELOG（628行）に既に「Shipping in the box」として記載**されている。CHANGELOGの「新規」という表現と実装年代は矛盾するため、裁定せず両面を記載する。
>
> **v0.6.0では再測定していない（2026-09-13）**: 本台帳の出典は `src/kiro_crew/apps/builtins/*/app.json` であり、v0.6.0 のスナップショット取得スクリプト（`fetch-snapshot.sh`）は **`src/` を取得しません**。したがって **v0.6.0 時点の builtin App 数は再測定できておらず、`[要検証]` を継続します**。本台帳の20件は `21584ea`（v0.3.0）時点の実測値であり、**v0.6.0 の値として追認しません**。
>
> **v0.7.2でも再測定していない（2026-10-04）**: 同じ理由（`src/` 未取得・`src/` 直接解析は未承認）で `[要検証]` を継続します。v0.7.0 の CHANGELOG は Dev Fleet・PPTX Maker・Issue Radar・Ops Mission Control などの App に言及しますが、件数の根拠にはしません。
>
> v0.5.0・v0.6.0 の CHANGELOG から確認できる範囲では、**`aws_control`（AWS Control）と `workflows`（Workflows）が builtin App として存在し、いずれも既定で無効**です（`01_features/16_aws-control.md`・`17_workflows.md` 参照）。ただしこれは CHANGELOG 由来の事実であり、`app.json` の実測ではありません。
>
> **⚠️ 20件という数値を v0.6.0 の件数として引用しないこと。** `04_reference/05_limits.md` の S12 は `[要検証]` のままにしてあります。

## 20件の一覧（ディレクトリ名順）

| # | ディレクトリ名 | 表示名（displayName） | defaultEnabled | 概要（description 冒頭） |
|---|--------------|---------------------|---------------|------------------------|
| 1 | `agent_worlds` | Agent Worlds | (未設定=false相当) | Turns your running agents into characters in an animated pixel world |
| 2 | `auto_improvement` | Auto-Improvement | (未設定=false相当) | Measures a GitHub repository before it changes it. Designs a... |
| 3 | `auto_research` | Research Lab | (未設定=false相当) | Runs multi-cycle research campaigns that keep working after... |
| 4 | `channels` | Channels | (未設定=false相当) | A shared room where several agents work a problem together in... |
| 5 | `code_review_sage` | Code Review Sage | (未設定=false相当) | Deep-reviews GitHub pull requests and tells you which changes... |
| 6 | `crew_companion` | Crew Companion | (未設定=false相当) | A desktop companion for Kiro Crew that helps you pace your day... |
| 7 | `design_critique` | Design Critique | (未設定=false相当) | A design critique you can run before you ask a colleague... |
| 8 | `dev_fleet` | Dev Fleet | (未設定=false相当) | A control panel for working on Kiro Crew itself. Lists every... |
| 9 | `file_explorer` | Files | (未設定=false相当) | Browse and read files on the machine running Kiro Crew without... |
| 10 | `issue_radar` | Issue Radar | (未設定=false相当) | An issue triage assistant that remembers. Browse, filter, and... |
| 11 | `md_notebook` | Notes | (未設定=false相当) | Keep a markdown notebook that lives in a git repository, so... |
| 12 | `meetings` | Meetings | (未設定=false相当) | An AI meeting assistant. Transcribes a live meeting, keeps s... |
| 13 | `mochi` | Mochi | (未設定=false相当) | A desktop companion that lives on your screen. Mochi chats t... |
| 14 | `ops_mission_control` | Ops Mission Control | (未設定=false相当) | An autonomous ops first responder. Watches your alarms, page... |
| 15 | `papyrus` | Papyrus | (未設定=false相当) | A LaTeX paper editor with live PDF preview and an AI co-auth... |
| 16 | `personal_shopper` | Personal Shopper | (未設定=false相当) | A personal advisor that researches real stores and helps sol... |
| 17 | `pptx_maker` | PPTX Maker | (未設定=false相当) | Describe the deck you want in chat and get a real .pptx back... |
| 18 | **`projects`** | **Task Runner** | **`true`** | Hand over a multi-step job and let it run to completion unat... |
| 19 | `spec_builder` | Spec Builder | (未設定=false相当) | Spec-driven development inside Kiro Crew: turn a feature idea... |
| 20 | `workflows` | Workflows | (未設定=false相当) | Author, run, and watch dynamic workflows: Python scripts, us... |

## 確定事項

- **合計20件**。全ディレクトリに `app.json` が存在（S12 と一致）
- **`defaultEnabled: true` は `projects`（表示名 Task Runner）の1件のみ**。他19件は `defaultEnabled` キー自体が存在しない（＝false相当、App Store で opt-in）→ S12「既定で有効なのは Task Runner のみ」を再確認
- ディレクトリ名と表示名が異なるもの: `projects`→Task Runner／`file_explorer`→Files／`md_notebook`→Notes／`auto_research`→Research Lab

## 再現コマンド

```bash
git clone --depth 1 https://github.com/kirodotdev/KiroCrew.git
cd KiroCrew
python3 -c "
import json,glob
files = sorted(glob.glob('src/kiro_crew/apps/builtins/*/app.json'))
for f in files:
    d=json.load(open(f))
    print(f.split('/')[-2], d.get('displayName'), d.get('defaultEnabled'))
"
```

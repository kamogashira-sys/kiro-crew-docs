# builtin App 24件 台帳

- **取得日**: 2026-11-01
- **commit SHA**: `fe6f5be1e43a89f08d1fd52e9e32a01bd49155ff`（短縮 `fe6f5be`・版 v0.11.1）
- **出典**: `src/kiro_crew/apps/builtins/*/app.json`（v0.11.1 タグの `src/` を依頼者の承認（`SRC_ANALYSIS: APPROVED`）のうえで別に clone し、全件を機械抽出）
- **検証コマンド**: `python3` で `json.load` し `displayName` / `defaultEnabled` を抽出（本ファイル下部に再現コマンドを記載）

> **v0.11.1での再測定（2026-11-01・`fe6f5be`）**: v0.3.0 以後で初めて `src/` を再測定しました。`ls -d src/kiro_crew/apps/builtins/*/` の実測は**24件**で、台帳記録24行と一致します（S12）。v0.3.0 時点の20件に対し、**追加4件・消滅0件・改名0件**です。追加は `aws_control`（AWS Control）・`command_bar`（Command Bar）・`design_tweak`（Design Tweak）・`project_scaffolder`（Create Folders From Project）です。旧20件の `displayName` と `description` 先頭50文字は、台帳の旧記録と全件一致しました。**`defaultEnabled` は24件すべての `app.json` にキーがあり**、`true` は **`command_bar` と `projects` の2件**、`false` は22件です（仕様書 `app-kit-platform.md` 1762-1765行とも一致）。
>
> **導入版は判定していません**: 追加4件がどの版で builtin になったかは、v0.9.0・v0.10.0・v0.11.0 の `src/` を取得していない（clone は履歴1件の shallow）ため確認できません。CHANGELOG の言及（Design Tweak=v0.4.0節、AWS Control=v0.5.0節・v0.6.0節、Create Folders From Project=v0.6.0節、Command Bar=v0.7.0節）は機能への言及であり、builtin 化の時期の根拠にしません。v0.9.0・v0.10.0・v0.11.0 時点の個別の件数は未実測です。`app.json` の `version`（参考）は `aws_control` 0.1.0・`command_bar` 0.1.0・`design_tweak` 0.10.0・`project_scaffolder` 0.1.0 です。

## 過去の再確認の記録（履歴）

以下は各時点の記録です。現在の値は上の「v0.11.1での再測定」と下の24件の一覧が正です。

> **v0.3.0再確認（2026-08-22・v0.3.0タグ`21584ea`）**: `ls -d src/kiro_crew/apps/builtins/*/`実測20件＝台帳記録21行（ヘッダ含む）で一致確認済み（変化なし・S12）。`defaultEnabled:true`は`projects`のみ（変化なし）。`personal_shopper`・`issue_radar`は実在しともに`defaultEnabled: false`。**v0.3.0 時点では**、main HEAD `32872ff`に存在する`command_bar`・`design_tweak`（v0.4.0系）は`21584ea`に不在であったため本台帳に含めませんでした（**v0.11.1 では両方が存在し、一覧に含めています**）。（v0.3.0 対応。コミット `aaaefa9`）
>
> **⚠ 重要な訂正（v0.3.0 時点の記録）**: CHANGELOG v0.3.0節は`personal_shopper`・`issue_radar`を「Two new apps」（2つの新しいApp）として発表しているが、**両Appの実装は既存**であることを`64060f3`（v0.2.0時点）のフルクローンで確認した。`personal_shopper`の`app.json`は`64060f3`と`21584ea`で**完全に同一（差分0）**。`issue_radar`は`displayName: "Issue Radar"`のまま変更なしで、**v0.1.2のCHANGELOG（628行）に既に「Shipping in the box」として記載**されている。CHANGELOGの「新規」という表現と実装年代は矛盾するため、裁定せず両面を記載する。この食い違いは v0.11.1 でも継続している（CHANGELOG 2731-2736行・3170-3173行）。
>
> **v0.6.0・v0.7.2・v0.9.0では再測定していません（記録）**: 当時の `fetch-snapshot.sh` は `src/` を取得せず、`src/` 直接解析も未承認だったため、これらの版の builtin App 数は `[要検証]` でした。**v0.6.0・v0.7.2・v0.9.0 の件数として「20件」を引用しないこと。** v0.5.0・v0.6.0 の CHANGELOG から、`aws_control`（AWS Control）と `workflows`（Workflows）が builtin App として存在し既定で無効であることは確認できていました。`aws_control` は v0.11.1 で `app.json` を実測し、`defaultEnabled: false` でした。

## 24件の一覧（ディレクトリ名順）

| # | ディレクトリ名 | 表示名（displayName） | defaultEnabled | 概要（description 冒頭） |
|---|--------------|---------------------|---------------|------------------------|
| 1 | `agent_worlds` | Agent Worlds | `false` | Turns your running agents into characters in an animated pixel... |
| 2 | `auto_improvement` | Auto-Improvement | `false` | Measures a GitHub repository before it changes it. Designs a c... |
| 3 | `auto_research` | Research Lab | `false` | Runs multi-cycle research campaigns that keep working after yo... |
| 4 | `aws_control` | AWS Control | `false` | Your cloud accounts, in plain language. See every AWS account ... |
| 5 | `channels` | Channels | `false` | A shared room where several agents work a problem together ins... |
| 6 | `code_review_sage` | Code Review Sage | `false` | Deep-reviews GitHub pull requests and tells you which changes ... |
| 7 | **`command_bar`** | **Command Bar** | **`true`** | Replaces the quick-search (Cmd+K / Ctrl+K) surface with a laun... |
| 8 | `crew_companion` | Crew Companion | `false` | A desktop companion for Kiro Crew that helps you pace your day... |
| 9 | `design_critique` | Design Critique | `false` | A design critique you can run before you ask a colleague. Give... |
| 10 | `design_tweak` | Design Tweak | `false` | Visually select elements in your live app preview and turn the... |
| 11 | `dev_fleet` | Dev Fleet | `false` | A control panel for working on Kiro Crew itself. Lists every f... |
| 12 | `file_explorer` | Files | `false` | Browse and read files on the machine running Kiro Crew without... |
| 13 | `issue_radar` | Issue Radar | `false` | An issue triage assistant that remembers. Browse, filter, and ... |
| 14 | `md_notebook` | Notes | `false` | Keep a markdown notebook that lives in a git repository, so yo... |
| 15 | `meetings` | Meetings | `false` | An AI meeting assistant. Transcribes a live meeting, keeps str... |
| 16 | `mochi` | Mochi | `false` | A desktop companion that lives on your screen. Mochi chats thr... |
| 17 | `ops_mission_control` | Ops Mission Control | `false` | An autonomous ops first responder. Watches your alarms, pages,... |
| 18 | `papyrus` | Papyrus | `false` | A LaTeX paper editor with live PDF preview and an AI co-author... |
| 19 | `personal_shopper` | Personal Shopper | `false` | A personal advisor that researches real stores and helps solve... |
| 20 | `pptx_maker` | PPTX Maker | `false` | Describe the deck you want in chat and get a real .pptx back. ... |
| 21 | `project_scaffolder` | Create Folders From Project | `false` | Point it at a project directory and it works out which sub-pro... |
| 22 | **`projects`** | **Task Runner** | **`true`** | Hand over a multi-step job and let it run to completion unatte... |
| 23 | `spec_builder` | Spec Builder | `false` | Spec-driven development inside Kiro Crew: turn a feature idea ... |
| 24 | `workflows` | Workflows | `false` | Author, run, and watch dynamic workflows: Python scripts, usua... |

## 確定事項

- **合計24件**（v0.11.1 の `src/` 実測）。全ディレクトリに `app.json` が存在（S12 と一致）
- **`defaultEnabled: true` は `command_bar`（表示名 Command Bar）と `projects`（表示名 Task Runner）の2件**。他22件は `defaultEnabled: false` が明記されている（App Store で opt-in）。v0.3.0 時点の20件では `projects` のみが `true`、他19件は `defaultEnabled` キー自体が存在しませんでした（`false` 相当）。v0.11.1 では24件すべてにキーがあります
- 追加4件は `aws_control`・`command_bar`・`design_tweak`・`project_scaffolder`。導入版は未確認（上の注記）
- ディレクトリ名と表示名が異なるもの: `projects`→Task Runner／`file_explorer`→Files／`md_notebook`→Notes／`auto_research`→Research Lab／`project_scaffolder`→Create Folders From Project

## 再現コマンド

```bash
git clone --depth 1 --branch v0.11.1 https://github.com/kirodotdev/KiroCrew.git
cd KiroCrew
python3 -c "
import json,glob
files = sorted(glob.glob('src/kiro_crew/apps/builtins/*/app.json'))
print(len(files))
for f in files:
    d=json.load(open(f))
    print(f.split('/')[-2], d.get('displayName'), d.get('defaultEnabled'))
"
```

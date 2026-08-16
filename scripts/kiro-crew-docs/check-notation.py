#!/usr/bin/env python3
"""check-notation.py - kiro-crew-docs 表記規約チェック

使用方法:
    ./scripts/kiro-crew-docs/check-notation.py

規約 (a)〜(i):
    (a) 他製品のコマンド・固有機能の混入
        Kiro CLI 単体の機能（`docs/reference/kiro-cli/` の内容）が Crew の文脈に
        混入するのは誤り。「別製品/依存関係」と説明する文脈は正当。
    (b) 製品名・表記の揺れ
        Kiro Crew（製品名）/ KiroCrew（リポジトリ名）/ kirocrew（CLIコマンド）を
        混同していないか。
    (c) 非ISO日付
        本文は `YYYY-MM-DD`。
    (d) 存在しない版番号の創作
        実在するのは v0.1.0〜v0.2.0（安定版）のみ。プレリリース（-rc.N）は本文で
        「実装済み」として扱わない。
    (e) 取得日の本文混入
        取得日は作業記録に残す。
    (f) 裸URL直後の全角文字によるautolink事故
    (g) 禁止表現（推測表現）
    (h) **存在しないCLIサブコマンドの記載**（Crew固有・新規）
        許可リストは公式cli-reference + README + --helpの3系統から生成。
        `cloud`のように一次情報で確認できない語を弾く。
    (i) **存在しない層数・件数の創作**（Crew固有・新規）
        「公式8層」のような未確認の数値表現を検出する。Rev 1の実際の誤りから追加。

⚠️ 設計方針: 規則の所有権を分ける。URLの書式はcheck-links.py、件数はcheck-counts.py、
値の水平展開はcheck-consistency.pyが持つ。本スクリプトは表記だけを見る。
"""
import glob
import os
import re
import sys

DOC_ROOT = "kiro-crew-docs"
LOCAL_ONLY = ("05_meta", "06_embedded-docs", "work_plans", "work_records")

POLICY_DOCS = (".github/WORKFLOW.md", ".github/COMMIT_CHECKLIST.md",
               ".github/pull_request_template.md")

# ------------------------------------------------------------
# (a) Kiro CLI単体機能の混入
# ------------------------------------------------------------
OTHER_PRODUCT_PATTERNS = [
    (re.compile(r"docs/reference/kiro-cli/"), "Kiro CLIリファレンスへの直接参照"),
    (re.compile(r"\bkiro-cli\s+(?:chat|steering|hooks)\b"), "Kiro CLI単体のコマンド"),
]
DISTINCTION_RE = re.compile(r"Kiro CLI|別製品|依存|q-cli-docs|ACP|CLI 単体|CLI の領域|出典として使わない|出典にしない|解説しない")

# ------------------------------------------------------------
# (b) 製品名・表記の揺れ
# ------------------------------------------------------------
PRODUCT_NAME_RE = re.compile(r"\b(?:kiro\s+Crew|Kiro\s+crew|KIRO\s+CREW|Kirocrew|kiroCrew)\b")

# ------------------------------------------------------------
# (c) 非ISO日付
# ------------------------------------------------------------
MONTHS = (r"(?:January|February|March|April|May|June|July|August|September|"
          r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)")
EN_DATE_RE = re.compile(rf"\b{MONTHS}\.?\s+\d{{1,2}},\s*\d{{4}}")
DATE_OK_RE = re.compile(r"Page updated|出典|公式|引用|略記|月名フル|形式|表記|>")

# ------------------------------------------------------------
# (d) 存在しない版番号の創作
# ------------------------------------------------------------
VERSION_RE = re.compile(r"\bv(\d+)\.(\d+)\.(\d+)\b")
VALID_STABLE_VERSIONS = {"0.1.0", "0.1.1", "0.1.2", "0.1.3", "0.2.0"}
VERSION_ALLOW = [
    (re.compile(r"-rc\.\d+"), "プレリリース版への言及（実装済みとして書かない文脈）"),
]

# ------------------------------------------------------------
# (e) 取得日の混入
# ------------------------------------------------------------
FETCH_DATE_RE = re.compile(r"取得日\s*[:：]|取得日は\s*\d{4}")

# ------------------------------------------------------------
# (f) autolink事故
# ------------------------------------------------------------
BARE_URL_FULLWIDTH_RE = re.compile(
    r"(?<![<(\[])\bhttps?://[^\s<>()\[\]]+[０-９Ａ-Ｚａ-ｚぁ-んァ-ヶ一-龠、。（）「」]")

# ------------------------------------------------------------
# (g) 禁止表現
# ------------------------------------------------------------
BANNED = ["おそらく", "と思われる", "と思われます", "かもしれない", "かもしれません",
          "だろう", "でしょう", "予想されます", "一般的に", "通常は", "たぶん"]

# ------------------------------------------------------------
# (h) 存在しないCLIサブコマンド
# ------------------------------------------------------------
# 05_meta/ledger-cli-commands.md（Phase 0-10で確定・Phase 4でmodules/cli.mdを追加して訂正）の
# 突合結果から許可リストを生成する。
ALLOWED_CLI_COMMANDS = {
    "setup", "doctor", "gateway", "stop", "restart", "logs", "service", "update", "token",
    "chat", "run", "cron", "spawn", "learn", "snapshot", "restore", "config",
    "app", "manifest", "status", "eval", "computer", "logout", "chown",
    "telemetry", "security", "policy",  # README限定（公式ページには無いが実在確認済み）
    "cloud", "pod", "memory", "knowledge", "workspace", "mcp-cron", "mcp-core", "mcp-computer",
    # ↑ modules/cli.md でのみ確認できたコマンド群（Phase 4で追加。公式cli-reference/READMEには無い）
}
# 明示的に「記載しない」と判定した語。現時点では該当なし（cloud/podはmodules/cli.mdで実在確認済み）
DENIED_CLI_COMMANDS = set()
CLI_COMMAND_RE = re.compile(r"`kirocrew\s+([a-z][a-z-]*)")
# 「記載しない」という事実を説明する否定文脈。この文脈での言及は許容する
DENIAL_CONTEXT_RE = re.compile(r"記載しません|出現しません|存在しません|実在しない|記載しない")

# ------------------------------------------------------------
# (i) 存在しない層数・件数の創作
# ------------------------------------------------------------
# 「公式8層」のような、一次情報に存在しない数値表現を検出する。
# Rev 1の実際の誤り（公式サイト=8層）を教訓に、「公式」+層数の組み合わせを警戒する。
FABRICATED_LAYERS_RE = re.compile(r"公式(?:サイト|docs|ページ|は)[^\n]{0,10}?(\d+)\s*層")
# 許可される層数表現（リポジトリ側=6層+2貫通制御が正）
ALLOWED_LAYER_COUNTS = {"6"}


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def is_local_only(path):
    norm = path.replace(os.sep, "/")
    return any(f"/{lo}/" in norm or norm.startswith(f"{lo}/") for lo in LOCAL_ONLY)


def target_files():
    files = sorted(glob.glob(f"{DOC_ROOT}/**/*.md", recursive=True))
    files = [f for f in files if not is_local_only(f)]
    files += ["README.md"] + sorted(glob.glob(".github/*.md"))
    return [f for f in files if os.path.isfile(f)]


def code_line_flags(path):
    flags = {}
    in_fence = False
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            flags[i] = True
            continue
        flags[i] = in_fence
    return flags


def main():
    os.chdir(repo_root())
    print("=== kiro-crew-docs 表記規約チェック ===")
    print("")

    errors = []
    allowed_versions = []
    allowed_cli = []
    stats = {"files": 0, "lines": 0}

    for path in target_files():
        stats["files"] += 1
        in_code = code_line_flags(path)
        is_policy = path in POLICY_DOCS

        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            stats["lines"] += 1
            code = in_code.get(i, False)

            # (a) Kiro CLI単体機能の混入（コードブロック内も対象。規約文書自体は対象外）
            if not is_policy:
                for pat, label in OTHER_PRODUCT_PATTERNS:
                    m = pat.search(line)
                    if m and not DISTINCTION_RE.search(line):
                        errors.append(
                            f"{path}:{i} (a) {label} が Crew の文脈に混入しています: "
                            f"{m.group(0)!r}（別製品と明示するか削除してください）"
                        )

            # (h) 存在しないCLIサブコマンド（コードブロック内も対象。コマンド例に出るため）
            for m in CLI_COMMAND_RE.finditer(line):
                cmd = m.group(1)
                if cmd in DENIED_CLI_COMMANDS:
                    if DENIAL_CONTEXT_RE.search(line):
                        continue  # 「記載しない」という事実の説明は許容
                    errors.append(
                        f"{path}:{i} (h) 存在しないCLIサブコマンド `kirocrew {cmd}` が"
                        "記載されています（05_meta/ledger-cli-commands.md でいずれの系統にも"
                        "出現しないと確定済み。U14参照）"
                    )
                elif cmd not in ALLOWED_CLI_COMMANDS:
                    allowed_cli.append((path, i, cmd))

            if code:
                continue

            # (b) 製品名・表記の揺れ
            m = PRODUCT_NAME_RE.search(line)
            if m:
                errors.append(
                    f"{path}:{i} (b) 製品名・表記が揺れています: {m.group(0)!r}"
                    "（正: Kiro Crew=製品名／KiroCrew=リポジトリ名／kirocrew=CLIコマンド）"
                )

            # (c) 非ISO日付
            for m in EN_DATE_RE.finditer(line):
                if not DATE_OK_RE.search(line):
                    errors.append(
                        f"{path}:{i} (c) 英語表記の日付が出典・引用以外で使われています: "
                        f"{m.group(0)!r}（本文は ISO YYYY-MM-DD）"
                    )

            # (d) 存在しない版番号の創作
            for m in VERSION_RE.finditer(line):
                ver = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
                reason = None
                for allow_pat, label in VERSION_ALLOW:
                    if any(a.start() <= m.start() and m.end() <= a.end()
                           for a in allow_pat.finditer(line)):
                        reason = label
                        break
                if reason:
                    allowed_versions.append((path, i, m.group(0), reason))
                elif ver not in VALID_STABLE_VERSIONS:
                    errors.append(
                        f"{path}:{i} (d) 存在しない版番号です: v{ver}"
                        f"（実在する安定版は {sorted(VALID_STABLE_VERSIONS)} のみ）"
                    )

            # (e) 取得日の混入
            if not is_policy and FETCH_DATE_RE.search(line):
                errors.append(
                    f"{path}:{i} (e) 取得日が本文に書かれています"
                    "（取得日は作業記録に残し、本文には出典日・参照日を書きます）"
                )

            # (f) autolink事故
            m = BARE_URL_FULLWIDTH_RE.search(line)
            if m:
                errors.append(
                    f"{path}:{i} (f) 裸のURLの直後に全角文字があります: {m.group(0)[-40:]!r}"
                    "（`<https://...>` で囲むか半角空白を入れてください）"
                )

            # (g) 禁止表現
            if not is_policy:
                for w in BANNED:
                    if w in line:
                        errors.append(
                            f"{path}:{i} (g) 推測表現が使われています: {w!r}"
                            "（一次情報で確認して断定するか「未確認」と明示してください）"
                        )

            # (i) 存在しない層数の創作
            m = FABRICATED_LAYERS_RE.search(line)
            if m and m.group(1) not in ALLOWED_LAYER_COUNTS:
                errors.append(
                    f"{path}:{i} (i) 存在しない層数の創作の疑いがあります: {m.group(0)!r}"
                    "（公式は層数を数値で示していない。正はリポジトリ側の6層+2貫通制御。"
                    "Rev 1の「公式8層」と同種の誤り）"
                )

    print(f"検査ファイル: {stats['files']} 件 / {stats['lines']} 行")
    print("")
    print(f"(d) プレリリース版への許容された言及: {len(allowed_versions)} 件")
    for path, line, matched, reason in allowed_versions:
        print(f"      {path}:{line} {matched!r} … {reason}")
    print("")
    print(f"(h) 許可リスト外だが denied でもない CLI コマンド（要確認）: {len(allowed_cli)} 件")
    for path, line, cmd in allowed_cli:
        print(f"      {path}:{line} `kirocrew {cmd}`（許可リストに未登録。05_meta/ledger-cli-commands.md で確認してください）")
    print("")

    if errors:
        print(f"❌ エラー {len(errors)} 件:")
        for e in errors:
            print(f"   - {e}")
        print("")
        print("❌ 表記規約チェックに失敗しました")
        return 1

    print("✅ 表記規約に違反はありません")
    return 0


if __name__ == "__main__":
    sys.exit(main())

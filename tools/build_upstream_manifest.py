#!/usr/bin/env python3
"""從 MiniMax 版 plugin 目錄產生 Codex 版的 UPSTREAM.json。

為什麼需要這支：UPSTREAM.json 要回答「這個 Codex 套件的每個檔案，是從
MiniMax 版的哪個檔案來的、內容有沒有被改過」。手寫這份清單會漏，
而且檔案一多就對不起來；這支腳本把清單機械重建出來。

**來源側的雜湊一律從 git 物件取**（`git show <commit>:<prefix>/<path>`），
不是從工作樹讀。原因：工作樹會在來源側 commit 之後又被改動，
這時產出的 manifest 會記下「不是該 commit 的內容」的雜湊，
而工具自己不會發現 —— manifest 正是用來證明兩邊對得上���機制，
它自己不能是那個會出錯的環節。所以流程是：**先提交來源側 → 產生 manifest
→ 提交移植側**，本工具會在來源檔案不在該 commit 裡時直接失敗。

寫完之後會**自我驗證**一遍（重新讀回檔案、重新比對每一筆雜湊），
不符就以非零碼結束。

對應規則（依 Codex 套件的實際版面）：
  1. `skills/**` 與 `references/**` 等路徑相同的檔案 → 直接對應。
  2. Codex 把圖示放在 `assets/`，MiniMax 版放在 plugin 根 → 以檔名對應。
  3. Codex 的 `plugin.json` 與 `.codex-plugin/plugin.json` 取代 MiniMax 版的
     `.minimax-plugin/plugin.json` → `change: replaced_by_codex_manifests`。
  4. 其餘（`CODEX.md`、`README.md`、`agents/openai.yaml`）是 Codex 原生檔，
     MiniMax 版沒有對應物 → `source_path: null`。

用法：
    python3 tools/build_upstream_manifest.py \\
        --src plugins/<name> --codex codex/marketplace/plugins/<name> \\
        --name <name> --source-commit <sha> --ported-date YYYY-MM-DD \\
        --source-version 1.0.0 --codex-version 1.0.0 \\
        [--repo .] [--src-prefix plugins/<name>]
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_ls_tree(repo, commit, prefix):
    """回傳該 commit 裡 prefix 底下的所有檔案路徑（相對於 prefix）。"""
    r = subprocess.run(
        ["git", "-C", repo, "ls-tree", "-r", "--name-only", commit, prefix],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"git ls-tree 失敗（{commit}:{prefix}）：{r.stderr.strip()}")
    head = prefix.rstrip("/") + "/"
    return [line[len(head):] for line in r.stdout.splitlines() if line.startswith(head)]


def git_show_bytes(repo, commit, path):
    """回傳 git 物件內容；不存在就回 None。"""
    r = subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def walk(root):
    """回傳 root 底下所有檔案的相對路徑（排除快取與側車檔）。"""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.startswith("._") or name == ".DS_Store":
                continue
            out.append(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="MiniMax 版 plugin 目錄（工作樹）")
    ap.add_argument("--codex", required=True, help="Codex 版 plugin 目錄（工作樹）")
    ap.add_argument("--name", required=True)
    ap.add_argument("--source-commit", required=True,
                    help="被移植來源所在的 commit；來源側雜湊一律從這個 commit 的 git 物件取")
    ap.add_argument("--ported-date", required=True)
    ap.add_argument("--source-version", required=True)
    ap.add_argument("--codex-version", required=True)
    ap.add_argument("--repo", default=".", help="git repo 根目錄")
    ap.add_argument("--src-prefix", default=None,
                    help="來源在 repo 內的路徑前綴；預設為 plugins/<name>")
    ap.add_argument("--source-repository",
                    default="https://github.com/travisebill/minimax-plugins")
    ap.add_argument("--out", default=None,
                    help="輸出路徑；預設寫到 Codex 目錄下的 UPSTREAM.json")
    args = ap.parse_args()

    src_root = os.path.abspath(args.src)
    codex_root = os.path.abspath(args.codex)
    repo = os.path.abspath(args.repo)
    src_prefix = args.src_prefix or f"plugins/{args.name}"
    out_path = args.out or os.path.join(codex_root, "UPSTREAM.json")

    # 來源側的檔案清單與雜湊一律以 git 物件為準。
    commit_files = set(git_ls_tree(repo, args.source_commit, src_prefix))
    if not commit_files:
        raise SystemExit(
            f"commit {args.source_commit} 裡沒有 {src_prefix}/ 底下的任何檔案。\n"
            f"請確認 --source-commit 與 --src-prefix 指向正確的來源狀態。"
        )
    codex_files = [f for f in walk(codex_root) if f != "UPSTREAM.json"]

    def source_hash_of(rel):
        """回傳該來源檔案在 source commit 的 SHA-256；不在就回 None。"""
        if rel not in commit_files:
            return None
        data = git_show_bytes(repo, args.source_commit, f"{src_prefix}/{rel}")
        if data is None:
            raise SystemExit(
                f"來源檔案 {src_prefix}/{rel} 不在 commit {args.source_commit} 裡。\n"
                f"請先把來源側提交，再用那個 commit 重新產生 manifest。"
            )
        return sha256_bytes(data)

    entries = []
    for rel in codex_files:
        codex_full = os.path.join(codex_root, rel)
        codex_hash = sha256_file(codex_full)

        # 規則 3：兩份 manifest 取代 MiniMax 版的那一份
        if rel in ("plugin.json", ".codex-plugin/plugin.json"):
            source_rel = ".minimax-plugin/plugin.json"
            source_hash = source_hash_of(source_rel)
            entries.append({
                "source_path": source_rel if source_hash else None,
                "source_sha256": source_hash,
                "codex_path": rel,
                "codex_sha256": codex_hash,
                "change": "replaced_by_codex_manifests",
            })
            continue

        # 規則 1：同路徑；規則 2：圖示改名搬到 assets/
        source_rel = rel
        if source_rel not in commit_files and rel.startswith("assets/"):
            candidate = rel.split("/", 1)[1]
            if candidate in commit_files:
                source_rel = candidate

        source_hash = source_hash_of(source_rel)
        if source_hash is None:
            source_rel = None
            change = "codex_native_not_in_source"
        else:
            change = "unchanged" if source_hash == codex_hash else "adapted"

        entries.append({
            "source_path": source_rel,
            "source_sha256": source_hash,
            "codex_path": rel,
            "codex_sha256": codex_hash,
            "change": change,
        })

    doc = {
        "source_repository": args.source_repository,
        "source_commit": args.source_commit,
        "ported_date": args.ported_date,
        "name": args.name,
        "source_version": args.source_version,
        "codex_version": args.codex_version,
        "files": entries,
    }

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # 自我驗證：重新讀回檔案，逐一比對 —— 這份 manifest 是證明「兩邊對得上」
    # 的機制，它自己不能是那個會出錯的環節。
    problems = []
    written = json.load(open(out_path, encoding="utf-8"))
    for e in written["files"]:
        actual = sha256_file(os.path.join(codex_root, e["codex_path"]))
        if actual != e["codex_sha256"]:
            problems.append(f"codex_sha256 不符：{e['codex_path']}")
        if e["source_path"]:
            data = git_show_bytes(repo, written["source_commit"],
                                  f"{src_prefix}/{e['source_path']}")
            if data is None or sha256_bytes(data) != e["source_sha256"]:
                problems.append(f"source_sha256 不符：{e['source_path']}")
            same = e["source_sha256"] == e["codex_sha256"]
            if same != (e["change"] == "unchanged"):
                problems.append(f"change 分類不符：{e['codex_path']}")
        elif e["change"] != "codex_native_not_in_source":
            problems.append(f"change 分類不符：{e['codex_path']}")

    counts = {}
    for e in entries:
        counts[e["change"]] = counts.get(e["change"], 0) + 1
    print(f"{out_path}：{len(entries)} 筆 {counts}")
    if problems:
        print(f"\n❌ 自我驗證發現 {len(problems)} 個問題：")
        for p in problems:
            print("  -", p)
        return 1
    print(f"✅ 自我驗證通過：{len(entries)} 筆的 codex_sha256、source_sha256、change 分類全部相符")
    return 0


if __name__ == "__main__":
    sys.exit(main())

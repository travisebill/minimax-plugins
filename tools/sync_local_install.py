#!/usr/bin/env python3
"""把 repo 裡的外掛同步到本機安裝處，並驗證與 GitHub 的某個 commit **逐位元一致**。

**為什麼需要這支**：runtime 要求外掛放在 `<activeDataDir>/plugins/<name>/` 且拒絕 symlink，
所以 repo 與本機安裝處是兩份實體檔案。本機那份是「副本」，會被改到就會與 repo 分岔。

**驗證為什麼要做成比對 commit**：`diff` 工作目錄只能證明「本機＝目前工作區」，
但工作區可能有未提交的修改、或剛好被別的東西動過。
要證明的是「本機＝GitHub 上的某一個 commit」，唯一可靠的做法是
把該 commit 用 `git archive` 取出來再逐檔比對。

用法：
    # 同步並驗證（本機安裝處必須在 agent session 之外執行 —— agent 沙箱對
    # ~/.minimax 是唯讀的）
    python3 tools/sync_local_install.py

    # 指定別的 commit 驗證
    python3 tools/sync_local_install.py --commit 609817c

    # 只驗證不同步
    python3 tools/sync_local_install.py --check-only

驗證會忽略 `._*`（macOS 在 exFAT／外接卷產生的 AppleDouble 側車檔）與
`__pycache__`、`.DS_Store` —— 這些不是交付內容，且整包驗證會直接斷言失敗。
"""
from __future__ import annotations

import argparse
import filecmp
import fnmatch
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN = "three-kingdoms-focus-studio"
INSTALL_ROOT = Path.home() / ".minimax" / "plugins"


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        # 讓真正的原因露出來，不要只丟一個 returncode
        detail = "\n".join(x for x in (proc.stderr, proc.stdout) if x and x.strip()).strip()
        raise subprocess.CalledProcessError(
            proc.returncode, cmd,
            output=proc.stdout, stderr=detail or None)
    return proc


def excluded(rel: str) -> bool:
    """`._*` 是 glob 樣式，必須用 fnmatch 比對，不能用字串相等。"""
    parts = Path(rel).parts
    base = parts[-1] if parts else ""
    if base == ".DS_Store" or base == "__pycache__":
        return True
    if fnmatch.fnmatch(base, "._*"):
        return True
    return any(p == "__pycache__" for p in parts)


def collect(root: Path) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            if not excluded(rel):
                out.append(rel)
    return sorted(out)


def verify_against_commit(commit: str, install_dir: Path) -> int:
    """把 commit 的該外掛取出來，與本機安裝處逐位元比對。"""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # git archive 取出該 commit 的外掛樹（用 -o 落地，不走 stdout）
        archive = tmp / "p.tar"
        run(["git", "archive", "-o", str(archive), commit, f"plugins/{PLUGIN}"], cwd=REPO_ROOT)
        extract = tmp / "x"
        extract.mkdir()
        run(["tar", "-xf", str(archive), "-C", str(extract)])
        src = extract / "plugins" / PLUGIN

        a = collect(src)
        b = collect(install_dir)
        only_src = [p for p in a if p not in set(b)]
        only_dst = [p for p in b if p not in set(a)]
        diff = [p for p in a if p in set(b)
                and not filecmp.cmp(src / p, install_dir / p, shallow=False)]

        print(f"  commit        ：{commit}")
        print(f"  來源檔案數    ：{len(a)}")
        print(f"  本機檔案數    ：{len(b)}")
        if only_src:
            print(f"  ❌ 只在 commit 有（{len(only_src)}）：")
            for p in only_src[:20]:
                print(f"       {p}")
        if only_dst:
            print(f"  ❌ 只在本機有（{len(only_dst)}）：")
            for p in only_dst[:20]:
                print(f"       {p}")
        if diff:
            print(f"  ❌ 內容不同（{len(diff)}）：")
            for p in diff[:20]:
                print(f"       {p}")
        if not (only_src or only_dst or diff):
            print("  ✅ 與 commit 逐位元一致")
            return 0
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plugin", default=PLUGIN)
    ap.add_argument("--commit", default="HEAD", help="要驗證的 commit（預設 HEAD）")
    ap.add_argument("--install-dir", default=None)
    ap.add_argument("--check-only", action="store_true", help="只驗證不同步")
    args = ap.parse_args()

    src_dir = REPO_ROOT / "plugins" / args.plugin
    dst_dir = Path(args.install_dir) if args.install_dir else INSTALL_ROOT / args.plugin
    if not src_dir.is_dir():
        print(f"❌ 找不到來源：{src_dir}", file=sys.stderr)
        return 2
    if not dst_dir.parent.is_dir():
        print(f"❌ 找不到安裝根目錄：{dst_dir.parent}", file=sys.stderr)
        return 2

    if not args.check_only:
        print(f"同步：{src_dir}  →  {dst_dir}")
        cmd = ["rsync", "-a",
               "--exclude", ".DS_Store", "--exclude", "._*", "--exclude", "__pycache__",
               str(src_dir) + "/", str(dst_dir) + "/"]
        try:
            run(cmd)
        except subprocess.CalledProcessError as e:
            print("  ❌ rsync 失敗：", file=sys.stderr)
            for line in (e.stderr or "").splitlines()[:12]:
                print(f"     {line}", file=sys.stderr)
            print("\n  這通常是 agent 沙箱把 ~/.minimax 設為唯讀造成的。", file=sys.stderr)
            print("  請在 agent session 之外（你自己的 shell）執行本腳本。", file=sys.stderr)
            return 2
        print("  rsync 完成")

    print("\n驗證：")
    try:
        rc = verify_against_commit(args.commit, dst_dir)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 驗證指令失敗：{e.stderr or e.stdout}", file=sys.stderr)
        return 2
    return rc


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""重算 UPSTREAM.json 的移植側雜湊，並精確登錄本次新增／修改的檔案。

基準來源
--------
上游的「改動前狀態」= 本 repo 的 git HEAD（MiniMax 版 plugin 在 HEAD 時是 1.3.0）。
因此：
- **HEAD 上游有、現在沒有** → 來源被刪除
- **HEAD 上游沒有、現在有** → 本次真正新增（`source_path: null`）
- **兩邊都有但內容不同** → 本次修改

處理原則
--------
- `source_sha256` 永遠不動：它指向原始上游倉庫內容，屬不可變出處。
- 移植側雜湊（`codex_sha256` / `minimax_sha256`）重算為**目前**檔案的雜湊。
- `change` 三態：
  - `unchanged` — 與上游 HEAD 逐位元相同
  - `adapted` — 移植時就已改寫（沿用原有值）
  - `adapted_for_mcp_execution_layer` / `added_for_mcp_execution_layer` — 本次改動

用法：
    python3 tools/refresh_upstream_hashes.py --repo . --src <minimax-plugin-dir> --codex <codex-plugin-dir> [--date YYYY-MM-DD]
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

ADDED = "added_for_mcp_execution_layer"
ADAPTED = "adapted_for_mcp_execution_layer"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_show(repo, rev, path):
    """回傳 git 物件內容；不存在則回傳 None。"""
    r = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def walk_files(root):
    out = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if fn.startswith("._") or fn == "UPSTREAM.json":
                continue
            out.add(os.path.relpath(os.path.join(dirpath, fn), root))
    return out


def classify(codex_path, codex_head_hash, upstream_head_hash):
    """判定 change 欄位。"""
    if upstream_head_hash is not None and codex_path == upstream_head_hash:
        return "unchanged"
    if codex_head_hash is not None and codex_path != codex_head_hash:
        return ADAPTED
    return "adapted"


def refresh_root_codex(repo, codex_root, up_path, changed_hint):
    d = json.load(open(up_path, encoding="utf-8"))
    d["source_version"] = "1.4.0"
    d["codex_version"] = "1.4.0"
    d["revision_date"] = changed_hint

    src_prefix = "plugins/three-kingdoms-focus-studio"
    codex_prefix = "codex/marketplace/plugins/three-kingdoms-focus-studio"

    entries = d["files"]
    listed = set()
    for e in entries:
        rel = e.get("codex_path")
        if not rel:
            continue
        listed.add(rel)
        full = os.path.join(codex_root, rel)
        if not os.path.isfile(full):
            print(f"  ⚠️  找不到 {rel}")
            continue
        now = sha256_file(full)
        e["codex_sha256"] = now
        head = git_show(repo, "HEAD", f"{codex_prefix}/{rel}")
        up_head = git_show(repo, "HEAD", f"{src_prefix}/{e['source_path']}") if e.get("source_path") else None
        e["change"] = classify(now,
                               sha256_bytes(head) if head is not None else None,
                               sha256_bytes(up_head) if up_head is not None else None)

    # 本次真正新增（HEAD 上游沒有、現在有）／Codex 原生檔（HEAD 已有但 manifest 未登錄）
    now_files = walk_files(codex_root)
    added = 0
    for rel in sorted(now_files - listed):
        upstream_bytes = git_show(repo, "HEAD", f"{src_prefix}/{rel}")
        codex_head_bytes = git_show(repo, "HEAD", f"{codex_prefix}/{rel}")
        if upstream_bytes is not None:
            e = {
                "source_path": rel,
                "source_sha256": sha256_bytes(upstream_bytes),
                "codex_path": rel,
                "codex_sha256": sha256_file(os.path.join(codex_root, rel)),
                "change": "unchanged",
            }
        elif codex_head_bytes is not None:
            # Codex 原生檔（agents/、CODEX.md、plugin.json…）：本來就存在於 Codex 套件，
            # 只是當初沒登錄進 manifest。不是本次新增。
            e = {
                "source_path": None,
                "source_sha256": None,
                "codex_path": rel,
                "codex_sha256": sha256_file(os.path.join(codex_root, rel)),
                "change": "codex_native_not_in_source",
            }
        else:
            e = {
                "source_path": None,
                "source_sha256": None,
                "codex_path": rel,
                "codex_sha256": sha256_file(os.path.join(codex_root, rel)),
                "change": ADDED,
            }
            added += 1
        entries.append(e)

    json.dump(d, open(up_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(up_path, "a", encoding="utf-8").write("\n")
    print(f"Codex 根 UPSTREAM.json：{len(entries)} 筆（新增登錄 {added} 筆）")


def refresh_skill_upstream(repo, variant_root, skill, hash_key, path_key, date,
                           new_files, path_base, entries_at, scope_dir=None):
    """更新單一 skill 的 UPSTREAM.json。

    `path_base` 決定路徑的解析起點：
    - MiniMax 版用 skill 目錄（路徑形如 `SKILL.md`、`references/local-setup.md`）
    - Codex 版用 plugin 根目錄（路徑形如 `skills/<skill>/SKILL.md`）
    `scope_dir` 限定只登錄該 skill 底下的檔案。
    """
    skill_root = os.path.join(variant_root, "skills", skill)
    up_path = os.path.join(skill_root, "UPSTREAM.json")
    if not os.path.isfile(up_path):
        return
    d = json.load(open(up_path, encoding="utf-8"))

    target = d
    for key in entries_at:
        target = target[key]

    listed = set()
    for e in target:
        rel = e.get(path_key)
        if not rel:
            continue
        listed.add(rel)
        full = os.path.join(path_base, rel)
        if not os.path.isfile(full):
            print(f"  ⚠️  找不到 {rel}")
            continue
        e[hash_key] = sha256_file(full)
        if os.path.basename(rel) in new_files or rel in new_files:
            e["change"] = ADAPTED

    scope_dir = scope_dir or skill_root
    scoped = {os.path.relpath(p, path_base) for p in
              [os.path.join(dp, fn)
               for dp, dn, fns in os.walk(scope_dir)
               for fn in fns
               if not fn.startswith("._") and fn != "UPSTREAM.json"]
              if "__pycache__" not in p}
    added = 0
    for rel in sorted(scoped - listed):
        e = {
            path_key: rel,
            hash_key: sha256_file(os.path.join(path_base, rel)),
            "source_sha256": None,
            "change": ADDED,
        }
        target.append(e)
        added += 1

    d["revision_date"] = date
    json.dump(d, open(up_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(up_path, "a", encoding="utf-8").write("\n")
    print(f"{os.path.basename(variant_root)}/{skill} UPSTREAM.json：{len(target)} 筆（新增登錄 {added} 筆）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--codex", required=True)
    ap.add_argument("--repo", required=True, help="minimax-plugins repo 根目錄（git 基準）")
    ap.add_argument("--date", default="2026-10-22")
    args = ap.parse_args()

    arw_new = {"SKILL.md", "references/output-variants.md", "scripts/make_variants.py"}

    refresh_root_codex(args.repo, args.codex,
                       os.path.join(args.codex, "UPSTREAM.json"), args.date)
    # MiniMax 版：路徑相對於 skill 目錄
    refresh_skill_upstream(args.repo, args.src, "audio-reactive-waveform",
                           "minimax_sha256", "path", args.date, arw_new,
                           path_base=os.path.join(args.src, "skills", "audio-reactive-waveform"),
                           entries_at=["files"])
    # Codex 版：路徑相對於 plugin 根目錄
    refresh_skill_upstream(args.repo, args.codex, "audio-reactive-waveform",
                           "codex_sha256", "codex_path", args.date, arw_new,
                           path_base=args.codex,
                           entries_at=["files"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

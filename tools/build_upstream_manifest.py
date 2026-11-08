#!/usr/bin/env python3
"""從 MiniMax 版 plugin 目錄產生 Codex 版的 UPSTREAM.json。

為什麼需要這支：UPSTREAM.json 要回答「這個 Codex 套件的每個檔案，是從
MiniMax 版的哪個檔案來的、內容有沒有被改過」。手寫這份清單會漏，
而且檔案一多就對不起來；這支腳本把清單機械重建出來。

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
        --source-version 1.0.0 --codex-version 1.0.0
"""

import argparse
import hashlib
import json
import os
import sys


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
    ap.add_argument("--src", required=True, help="MiniMax 版 plugin 目錄")
    ap.add_argument("--codex", required=True, help="Codex 版 plugin 目錄")
    ap.add_argument("--name", required=True)
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--ported-date", required=True)
    ap.add_argument("--source-version", required=True)
    ap.add_argument("--codex-version", required=True)
    ap.add_argument("--source-repository",
                    default="https://github.com/travisebill/minimax-plugins")
    ap.add_argument("--out", default=None,
                    help="輸出路徑；預設寫到 Codex 目錄下的 UPSTREAM.json")
    args = ap.parse_args()

    src_root = os.path.abspath(args.src)
    codex_root = os.path.abspath(args.codex)
    out_path = args.out or os.path.join(codex_root, "UPSTREAM.json")

    src_files = set(walk(src_root))
    codex_files = [f for f in walk(codex_root) if f != "UPSTREAM.json"]

    manifest_path = os.path.join(codex_root, ".codex-plugin", "plugin.json")
    entries = []
    for rel in codex_files:
        codex_full = os.path.join(codex_root, rel)
        codex_hash = sha256_file(codex_full)

        # 規則 3：兩份 manifest 取代 MiniMax 版的那一份
        if rel in ("plugin.json", ".codex-plugin/plugin.json"):
            source_rel = ".minimax-plugin/plugin.json"
            source_full = os.path.join(src_root, source_rel)
            entries.append({
                "source_path": source_rel if os.path.isfile(source_full) else None,
                "source_sha256": sha256_file(source_full) if os.path.isfile(source_full) else None,
                "codex_path": rel,
                "codex_sha256": codex_hash,
                "change": "replaced_by_codex_manifests",
            })
            continue

        # 規則 1：同路徑
        source_rel = rel
        source_full = os.path.join(src_root, source_rel)
        # 規則 2：圖示改名搬到 assets/
        if not os.path.isfile(source_full) and rel.startswith("assets/"):
            candidate = rel.split("/", 1)[1]
            if candidate in src_files:
                source_rel = candidate
                source_full = os.path.join(src_root, candidate)

        if os.path.isfile(source_full):
            source_hash = sha256_file(source_full)
            change = "unchanged" if source_hash == codex_hash else "adapted"
        else:
            source_rel = None
            source_hash = None
            change = "codex_native_not_in_source"

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

    counts = {}
    for e in entries:
        counts[e["change"]] = counts.get(e["change"], 0) + 1
    print(f"{out_path}：{len(entries)} 筆 {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

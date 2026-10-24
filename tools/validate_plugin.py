#!/usr/bin/env python3
"""外掛靜態驗證：frontmatter、內部連結、腳本語法、版本一致性、檔名慣例。

用法：
    python3 tools/validate_plugin.py <plugin-dir> [--codex-dir <codex-plugin-dir>]

任何一項不通過都以非零碼結束 —— 這支腳本本身就是驗證閘門，
所以它的判定邏輯必須先用已知正確與已知錯誤的樣本自我檢查過
（見 `--self-check`）。
"""

import argparse
import json
import os
import re
import subprocess
import sys

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def split_frontmatter(text):
    m = FRONTMATTER.match(text)
    return (m.group(1), text[m.end():]) if m else (None, text)


def check_skill(root, problems):
    """逐個 skill 檢查 frontmatter、連結、腳本。"""
    skills_dir = os.path.join(root, "skills")
    skill_names = sorted(n for n in os.listdir(skills_dir)
                          if os.path.isdir(os.path.join(skills_dir, n)))
    # 跨 skill 的腳本引用是合法的（例如 pipeline 提到審查 skill 的 measure_audio.py）
    sibling_scripts = set()
    for n in skill_names:
        sd = os.path.join(skills_dir, n, "scripts")
        if os.path.isdir(sd):
            for fn in os.listdir(sd):
                if fn.endswith(".py"):
                    sibling_scripts.add(fn)

    for name in skill_names:
        skill_dir = os.path.join(skills_dir, name)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_md):
            problems.append(f"{name}: 缺少 SKILL.md")
            continue
        text = open(skill_md, encoding="utf-8").read()
        fm, body = split_frontmatter(text)
        if fm is None:
            problems.append(f"{name}: frontmatter 格式錯誤")
            continue
        # name 必須存在且與目錄同名
        m = re.search(r"^name:\s*(\S+)\s*$", fm, re.M)
        if not m:
            problems.append(f"{name}: frontmatter 缺少 name")
        elif m.group(1) != name:
            problems.append(f"{name}: frontmatter name='{m.group(1)}' 與目錄名不符")
        if not re.search(r"^description:", fm, re.M):
            problems.append(f"{name}: frontmatter 缺少 description")
        # 內部 markdown 連結必須可解析
        for target in LINK.findall(body):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            clean = target.split("#")[0]
            if not clean:
                continue
            resolved = os.path.normpath(os.path.join(skill_dir, clean))
            if not os.path.exists(resolved):
                problems.append(f"{name}: 連結目標不存在 → {target}")
        # 腳本必須可編譯
        scripts_dir = os.path.join(skill_dir, "scripts")
        if os.path.isdir(scripts_dir):
            for fn in sorted(os.listdir(scripts_dir)):
                if not fn.endswith(".py") or fn.startswith("._"):
                    continue
                p = os.path.join(scripts_dir, fn)
                r = subprocess.run([sys.executable, "-m", "py_compile", p],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    problems.append(f"{name}/scripts/{fn}: 語法錯誤\n{r.stderr}")
        # 引用到的 scripts/ 必須真的存在（本 skill 或任一 sibling skill）
        for ref in re.findall(r"`?(scripts/[\w./-]+\.py)`?", body):
            if os.path.exists(os.path.join(skill_dir, ref)):
                continue
            if os.path.basename(ref) in sibling_scripts:
                continue
            problems.append(f"{name}: 引用了不存在的腳本 → {ref}")


def check_plugin_json(root, problems, label):
    p = os.path.join(root, ".minimax-plugin", "plugin.json")
    if not os.path.isfile(p):
        p = os.path.join(root, "plugin.json")
    if not os.path.isfile(p):
        problems.append(f"{label}: 找不到 plugin.json")
        return None
    d = json.load(open(p, encoding="utf-8"))
    if "version" not in d:
        problems.append(f"{label}: plugin.json 缺少 version")
    if not d.get("description"):
        problems.append(f"{label}: plugin.json 缺少 description")
    # MiniMax 版的 skills 陣列必須指向存在的檔案
    for rel in d.get("skills", []):
        if not os.path.isfile(os.path.join(root, rel)):
            problems.append(f"{label}: plugin.json skills 指向不存在的檔案 → {rel}")
    # skills 目錄與 plugin.json 的 skills 陣列必須互相覆蓋
    if d.get("skills"):
        declared = {os.path.basename(os.path.dirname(x)) for x in d["skills"]}
        actual = {n for n in os.listdir(os.path.join(root, "skills"))
                  if os.path.isdir(os.path.join(root, "skills", n))}
        for miss in actual - declared:
            problems.append(f"{label}: skill 目錄未在 plugin.json 登錄 → {miss}")
    return d


def self_check():
    """自我檢查：確認判定邏輯能分辨已知正確與已知錯誤的樣本。"""
    import tempfile
    good = tempfile.mkdtemp(prefix="good-")
    bad = tempfile.mkdtemp(prefix="bad-")
    for root, with_bad in [(good, False), (bad, True)]:
        os.makedirs(os.path.join(root, "skills", "demo"))
        fm = "name: demo\ndescription: test\n"
        link = "[ok](references/a.md)" if not with_bad else "[broken](references/missing.md)"
        open(os.path.join(root, "skills", "demo", "SKILL.md"), "w").write(
            f"---\n{fm}---\n\n{link}\n")
        os.makedirs(os.path.join(root, "skills", "demo", "references"))
        open(os.path.join(root, "skills", "demo", "references", "a.md"), "w").write("x")
    pg, pb = [], []
    check_skill(good, pg)
    check_skill(bad, pb)
    ok = (pg == [] and len(pb) == 1)
    print("=== 自我檢查 ===")
    print(f"  正確樣本問題數 = {len(pg)}（應為 0）")
    print(f"  錯誤樣本問題數 = {len(pb)}（應為 1）→ {pb}")
    print(f"  判定邏輯: {'通過' if ok else '失敗 —— 驗證器本身不可信'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plugin_dir")
    ap.add_argument("--codex-dir", default=None)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()

    if args.self_check:
        if not self_check():
            return 2

    problems = []
    print("=== 驗證 MiniMax 版 ===")
    d1 = check_plugin_json(args.plugin_dir, problems, "MiniMax")
    check_skill(args.plugin_dir, problems)
    print(f"  version = {d1.get('version') if d1 else '?'}")

    d2 = None
    if args.codex_dir:
        print("=== 驗證 Codex 版 ===")
        d2 = check_plugin_json(args.codex_dir, problems, "Codex")
        check_skill(args.codex_dir, problems)
        print(f"  version = {d2.get('version') if d2 else '?'}")
        if d1 and d2 and d1.get("version") != d2.get("version"):
            problems.append(f"兩份版本不一致：MiniMax {d1.get('version')} vs Codex {d2.get('version')}")

    if problems:
        print(f"\n❌ {len(problems)} 個問題：")
        for p in problems:
            print("  -", p)
        return 1
    print("\n✅ 靜態驗證全部通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())

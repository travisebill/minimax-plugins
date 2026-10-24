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
        # 腳本必須可編譯。
        # 用記憶體內 compile() 而不是 py_compile —— py_compile 會在旁邊產生
        # __pycache__，而那正是本檔案下面要檢查的項目：驗證器不該自己製造問題。
        scripts_dir = os.path.join(skill_dir, "scripts")
        if os.path.isdir(scripts_dir):
            for fn in sorted(os.listdir(scripts_dir)):
                if not fn.endswith(".py") or fn.startswith("._"):
                    continue
                p = os.path.join(scripts_dir, fn)
                try:
                    with open(p, encoding="utf-8") as fh:
                        compile(fh.read(), p, "exec")
                except SyntaxError as e:
                    problems.append(f"{name}/scripts/{fn}: 語法錯誤 → {e}")
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


def check_hooks(root, manifest, problems, label):
    """驗證 manifest 宣告的 Hook：檔案存在、欄位合規、腳本語法正確、引用路徑存在。

    為什麼要查：`node --check` 只解析語法，抓不到 `import { os } from "node:os"`
    這種錯誤（要等到執行時才炸）。而 Hook 腳本是在**使用者每個回合**都會跑的，
    一個壞掉的 import 會讓整條事件預算被燒掉。
    """
    declared = manifest.get("hooks") or []
    if not declared:
        return 0
    hook_docs = 0
    handlers = 0
    for rel in declared:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            problems.append(f"{label}: hooks 指向不存在的檔案 → {rel}")
            continue
        hook_docs += 1
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            problems.append(f"{label}: {rel} 不是合法 JSON → {e}")
            continue
        groups = doc.get("hooks")
        if not isinstance(groups, dict) or not groups:
            problems.append(f"{label}: {rel} 缺少 hooks 物件")
            continue
        for event, items in groups.items():
            if not isinstance(items, list) or not items:
                problems.append(f"{label}: {rel} 事件 {event} 必須是非空陣列")
                continue
            for group in items:
                matcher = group.get("matcher")
                if matcher is not None:
                    if not isinstance(matcher, str) or not matcher:
                        problems.append(f"{label}: {rel} 事件 {event} 的 matcher 必須是非空字串")
                    elif len(matcher) > 256:
                        problems.append(f"{label}: {rel} 事件 {event} 的 matcher 超過 256 字元")
                for h in group.get("hooks", []):
                    handlers += 1
                    if h.get("type") != "command":
                        problems.append(f"{label}: {rel} 事件 {event} 的 handler type 必須是 command")
                    cmd = h.get("command")
                    if not isinstance(cmd, str) or not cmd.strip():
                        problems.append(f"{label}: {rel} 事件 {event} 的 handler 缺少 command")
                        continue
                    name = h.get("name")
                    if name is not None and (not isinstance(name, str) or len(name) > 64):
                        problems.append(f"{label}: {rel} 事件 {event} 的 handler name 必須 ≤64 字元")
                    timeout = h.get("timeout", 5)
                    if not isinstance(timeout, int) or isinstance(timeout, bool) or not (1 <= timeout <= 10):
                        problems.append(f"{label}: {rel} 事件 {event} 的 handler timeout 必須是 1–10 的整數")
                    # ${PLUGIN_ROOT}/path 必須真的存在，而且語法要對
                    for ref in re.findall(r"\$\{PLUGIN_ROOT\}[/\\]+([\w./\\-]+)", cmd):
                        target = os.path.join(root, ref.replace("\\", "/"))
                        if not os.path.isfile(target):
                            problems.append(f"{label}: {rel} 引用的腳本不存在 → {ref}")
                            continue
                        if target.endswith((".mjs", ".js")):
                            r = subprocess.run(["node", "--check", target],
                                               capture_output=True, text=True)
                            if r.returncode != 0:
                                problems.append(
                                    f"{label}: {rel} 引用的 {ref} 語法錯誤\n{r.stderr.strip()}")
    # 外掛套件裡不該有快取與側車檔（整包檢查會擋，但靜態驗證是更早的閘門）
    for dp, dn, fns in os.walk(root):
        for n in list(dn):
            if n == "__pycache__":
                problems.append(f"{label}: 外掛內含 __pycache__ → {os.path.relpath(os.path.join(dp, n), root)}")
        for n in fns:
            if n.startswith("._") or n == ".DS_Store":
                problems.append(f"{label}: 外掛內含側車檔 → {os.path.relpath(os.path.join(dp, n), root)}")
    print(f"  {label} Hook：{hook_docs} 份文件、{handlers} 個 handler")
    return handlers


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


def self_check_hooks():
    """自我檢查：Hook 驗證能分辨正確與錯誤的外掛。"""
    import tempfile
    def build(with_bad):
        root = tempfile.mkdtemp(prefix="hook-")
        os.makedirs(os.path.join(root, "hooks", "lib"))
        script = "const a = 1;\n"
        if with_bad == "syntax":
            script = "import { os } from \"node:os\";\nconst x = ;\n"
        elif with_bad == "missing":
            script = "const a = 1;\n"
        open(os.path.join(root, "hooks", "lib", "hook-utils.mjs"), "w").write(script)
        cmd = 'node "${PLUGIN_ROOT}/hooks/lib/hook-utils.mjs"'
        if with_bad == "missing":
            cmd = 'node "${PLUGIN_ROOT}/hooks/lib/nope.mjs"'
        doc = {"hooks": {"PreToolUse": [{"matcher": "bash", "hooks": [
            {"type": "command", "name": "t", "command": cmd, "timeout": 5}]}]}}
        open(os.path.join(root, "hooks", "hooks.json"), "w").write(json.dumps(doc))
        return root, {"hooks": ["hooks/hooks.json"]}

    results = {}
    for case in (None, "syntax", "missing"):
        root, manifest = build(case)
        p = []
        check_hooks(root, manifest, p, "測試")
        results[case or "good"] = p
    ok = (results["good"] == [] and len(results["syntax"]) >= 1 and len(results["missing"]) >= 1)
    print("=== Hook 自我檢查 ===")
    print(f"  正確樣本問題數 = {len(results['good'])}（應為 0）")
    print(f"  語法錯樣本 = {len(results['syntax'])} 項（應 ≥1）")
    print(f"  引用缺檔樣本 = {len(results['missing'])} 項（應 ≥1）")
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
        if not self_check_hooks():
            return 2

    problems = []
    print("=== 驗證 MiniMax 版 ===")
    d1 = check_plugin_json(args.plugin_dir, problems, "MiniMax")
    check_skill(args.plugin_dir, problems)
    check_hooks(args.plugin_dir, d1 or {}, problems, "MiniMax")
    print(f"  version = {d1.get('version') if d1 else '?'}")

    d2 = None
    if args.codex_dir:
        print("=== 驗證 Codex 版 ===")
        d2 = check_plugin_json(args.codex_dir, problems, "Codex")
        check_skill(args.codex_dir, problems)
        check_hooks(args.codex_dir, d2 or {}, problems, "Codex")
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

#!/usr/bin/env python3
"""把 MiniMax 版 plugin 的 SKILL.md 內容同步到 Codex 版，保留 Codex 專屬差異。

兩份套件的差異規則（實測確認）：
  1. Codex 版在 frontmatter 之後多一行 runtime 引導 + 兩個空行。
  2. `yt-focus-music-pipeline` 在 Codex 版是「六個 skill」（不含
     audio-reactive-waveform），且沒有「音樂視覺化」那一節。
  3. `yt-publish-strategy` 在 Codex 版有一條不同的資料時效揭露句。

第 2、3 條是**依 skill 名稱**套用的特例，所以 skill 清單改成從來源目錄
自動發現後，這支工具對任何外掛都成立，而不只是 three-kingdoms。
發現規則：來源 `skills/` 下含有 SKILL.md 的子目錄。

用法：
    python3 tools/sync_codex_variant.py --src <minimax-plugin-dir> --codex <codex-plugin-dir> [--dry-run]
"""
import argparse
import os
import re
import sys

GUIDANCE = ("Read [Codex runtime guidance](../../CODEX.md) before using this skill. "
            "Resolve bundled skills and resources relative to this installed package.")


def discover_skills(src):
    """回傳來源 plugin 內所有含 SKILL.md 的 skill 目錄名（已排序）。"""
    skills_dir = os.path.join(src, "skills")
    if not os.path.isdir(skills_dir):
        return []
    return sorted(
        name for name in os.listdir(skills_dir)
        if os.path.isfile(os.path.join(skills_dir, name, "SKILL.md"))
    )


def split_frontmatter(text):
    """回傳 (frontmatter, body)。frontmatter 含起始與結尾的 ---。"""
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, flags=re.S)
    if not m:
        raise ValueError("找不到 frontmatter")
    return m.group(1), m.group(2)


GUIDANCE_INSERT_INDEX = 3   # body 第 4 行（H1 標題與其後空行之後）


def build_body(src_body, guidance_index):
    """在 body 前插入 Codex runtime 引導。

    只有原本就有引導行的檔案才保留它 —— `audio-reactive-waveform` 在 Codex
    版是後來直接加入的，從來沒有引導行，不要憑空補上。

    插入位置取自 Codex 版既有版式中引導行所在的位置（實測固定在 body 第 4 行，
    即 H1 標題與其後空行之後），不寫死。
    """
    if guidance_index is None:
        return src_body
    lines = src_body.split("\n")
    lines[guidance_index:guidance_index] = [GUIDANCE, "", ""]
    return "\n".join(lines)


def find_guidance_index(codex_body):
    """回傳 Codex 版 body 中引導行所在的索引；沒有則回傳 None。"""
    for i, line in enumerate(codex_body.split("\n")):
        if line.startswith("Read [Codex runtime guidance]"):
            return i
    return None


def codex_pipeline_body(body):
    """Codex 版的 pipeline 特有差異。"""
    out = []
    skip_waveform_section = False
    for line in body.split("\n"):
        # 1) 六個 skill
        line = line.replace("底下七個 skill 的工作", "底下六個 skill 的工作")
        # 2) 委派說法
        line = line.replace(
            "所有實際工作一律委派給下列 skill，不要在此複製它們的流程細節：",
            "依需求讀取並遵循下列套件內 skill，不在此複製它們的流程細節：")
        # 3) 移除 audio-reactive-waveform 表格列
        if line.startswith("| `audio-reactive-waveform` |"):
            continue
        out.append(line)
    text = "\n".join(out)
    # 4) 移除整個「音樂視覺化 — waveform / 頻譜條」章節
    text = re.sub(
        r"\n## 音樂視覺化 — waveform / 頻譜條\n.*?(?=\n## )",
        "\n",
        text,
        flags=re.S,
    )
    return text


def codex_publish_body(body):
    """Codex 版的 publish-strategy 資料時效揭露句。"""
    return body.replace(
        "**所有數據與政策條文皆為 2026-09-30 實測**，來源見 `references/`。",
        "**上游資料記錄於 2026-09-30，來源見 `references/`；本次移植未重新執行該研究。** "
        "頻道與競品數據僅代表歷史快照。提供現行政策、變現資格或搜尋排名建議前，"
        "查核官方來源與當前可取得的結果，記錄日期；未能驗證的項目標示「未確認」。",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--codex", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skills", default=None,
                    help="逗號分隔的 skill 名單；未指定時自動發現來源目錄下的全部 skill")
    args = ap.parse_args()

    if args.skills:
        skills = [s.strip() for s in args.skills.split(",") if s.strip()]
    else:
        skills = discover_skills(args.src)
    if not skills:
        print(f"[sync] 在 {args.src} 找不到任何含 SKILL.md 的 skill")
        return 1

    changed = []
    for skill in skills:
        src_path = os.path.join(args.src, "skills", skill, "SKILL.md")
        codex_path = os.path.join(args.codex, "skills", skill, "SKILL.md")
        src_text = open(src_path, encoding="utf-8").read()
        codex_text = open(codex_path, encoding="utf-8").read()

        fm, src_body = split_frontmatter(src_text)
        codex_fm, codex_body_old = split_frontmatter(codex_text)

        body = build_body(src_body, find_guidance_index(codex_body_old))
        if skill == "yt-focus-music-pipeline":
            body = codex_pipeline_body(body)
        elif skill == "yt-publish-strategy":
            body = codex_publish_body(body)

        new_text = codex_fm + body

        if new_text == codex_text:
            continue
        changed.append(skill)
        if args.dry_run:
            print(f"[dry-run] 會更新 {skill}")
        else:
            with open(codex_path, "w", encoding="utf-8") as f:
                f.write(new_text)
            print(f"已更新 {skill}")

    print(f"\n共 {len(changed)} 個檔案{'會' if args.dry_run else ''}變更：{', '.join(changed) or '（無）'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

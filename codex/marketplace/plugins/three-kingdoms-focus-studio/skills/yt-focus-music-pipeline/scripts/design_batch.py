#!/usr/bin/env python3
"""批次執行 MiniMax Design `execute`，並等待全部任務到終態。

每個任務用**自己的 MCP session**（避免共用 session 的序列化問題），
以執行緒平行送出；供應商端會自行排隊（約每 30 秒一支）。

用法：
    python3 design_batch.py .mcp/exec-chapter-c01.json .mcp/exec-chapter-c02.json ...
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "design_mcp_call", Path(__file__).with_name("design_mcp_call.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

TERMINAL = ("completed", "failed", "cancelled")


def submit(arg_file: str) -> tuple[str, str, dict]:
    rpc = d.Rpc()
    rpc.initialize()
    args = json.loads(Path(arg_file).read_text(encoding="utf-8"))
    res = d.unwrap(rpc.call("execute", args, bind=True))
    task = (res or {}).get("task", {}) if isinstance(res, dict) else {}
    return Path(arg_file).stem.replace("exec-", ""), task.get("id", ""), task


def main() -> int:
    files = sys.argv[1:]
    if not files:
        print(__doc__)
        return 2

    results = []
    with ThreadPoolExecutor(max_workers=len(files)) as pool:
        for name, tid, task in pool.map(submit, files):
            results.append((name, tid, task))
            print(f"[submit] {name:<16} task={tid} status={task.get('status')} "
                  f"credits={task.get('billing', {}).get('estimatedCredits')}", flush=True)

    pending = {tid: name for name, tid, _ in results if tid}
    final: dict[str, dict] = {}
    rpc = d.Rpc()
    rpc.initialize()
    while pending:
        for tid in list(pending):
            w = d.unwrap(rpc.call("task_wait", {"taskId": tid}, bind=True))
            t = (w or {}).get("task", {}) if isinstance(w, dict) else {}
            st = t.get("status")
            if st in TERMINAL:
                final[tid] = w
                del pending[tid]
                print(f"[done]   {pending.get(tid, tid):<16} {tid} status={st}", flush=True)
        if pending:
            time.sleep(10)
            for tid, name in pending.items():
                print(f"[wait]   {name:<16} {tid} 仍在跑…", flush=True)

    out = []
    for name, tid, _ in results:
        w = final.get(tid, {})
        t = (w or {}).get("task", {})
        out.append({
            "key": name, "task_id": tid, "status": t.get("status"),
            "outputs": t.get("outputs"), "billing": t.get("billing"),
            "problem": t.get("problem"),
        })
    Path(".mcp/batch-result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if all(o["status"] == "completed" for o in out) else 1


if __name__ == "__main__":
    raise SystemExit(main())

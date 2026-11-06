#!/usr/bin/env python3
"""等待多個 Design 任務到終態（用於批次生成後的等待）。

用法：
    python3 design_wait_many.py tsk_a tsk_b ...
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "design_mcp_call", Path(__file__).with_name("design_mcp_call.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

TERMINAL = ("completed", "failed", "cancelled")


def main() -> int:
    ids = sys.argv[1:]
    if not ids:
        print(__doc__)
        return 2
    rpc = d.Rpc()
    rpc.initialize()
    pending = set(ids)
    final: dict[str, dict] = {}
    while pending:
        for tid in list(pending):
            w = d.unwrap(rpc.call("task_wait", {"taskId": tid}, bind=True))
            t = (w or {}).get("task", {}) if isinstance(w, dict) else {}
            st = t.get("status")
            if st in TERMINAL:
                final[tid] = w
                pending.discard(tid)
                outs = t.get("outputs") or []
                print(f"[done] {tid} {st} "
                      f"{[o.get('versionId') for o in outs]} "
                      f"credits={(t.get('billing') or {}).get('estimatedCredits')} "
                      f"problem={json.dumps(t.get('problem'), ensure_ascii=False)[:200]}",
                      flush=True)
        if pending:
            time.sleep(15)
            print(f"[wait] 仍在跑: {sorted(pending)}", flush=True)

    out = []
    for tid in ids:
        t = (final.get(tid, {}) or {}).get("task", {})
        out.append({"task_id": tid, "status": t.get("status"),
                    "outputs": t.get("outputs"), "billing": t.get("billing"),
                    "problem": t.get("problem")})
    Path(".mcp/loops-result.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if all(o["status"] == "completed" for o in out) else 1


if __name__ == "__main__":
    raise SystemExit(main())

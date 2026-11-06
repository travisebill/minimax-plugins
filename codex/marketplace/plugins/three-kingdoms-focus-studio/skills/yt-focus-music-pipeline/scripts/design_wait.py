#!/usr/bin/env python3
"""等 MiniMax Design 任務跑到終態（並在等待期間自動重綁專案）。

用法：
    python3 design_wait.py <taskId> [--interval 8]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "design_mcp_call", Path(__file__).with_name("design_mcp_call.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task_id")
    ap.add_argument("--interval", type=int, default=8)
    args = ap.parse_args()

    rpc = d.Rpc()
    rpc.initialize()
    while True:
        w = d.unwrap(rpc.call("task_wait", {"taskId": args.task_id}, bind=True))
        t = (w or {}).get("task", {}) if isinstance(w, dict) else {}
        st = t.get("status")
        billing = t.get("billing") or {}
        print(f"[wait] {args.task_id} status={st} "
              f"credits={billing.get('chargedCredits', billing.get('estimatedCredits'))}",
              file=sys.stderr)
        if st in ("completed", "failed", "cancelled"):
            print(json.dumps(w, ensure_ascii=False, indent=1))
            return 0 if st == "completed" else 1
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())

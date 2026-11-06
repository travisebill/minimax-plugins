#!/usr/bin/env python3
"""直接對 MiniMax Design MCP 講 JSON-RPC（Streamable HTTP）。

**為什麼需要這支**：MCode 的 `mcp_invoke` 轉呼叫 deferred MCP 工具時，
會把 `execute` 的陣列／整數參數（`references`、`count`、`output.resources`、
`output.composition.placements`）**字串化**，schema 驗證必然失敗
（`/references: must be array`）。**重試沒有用** —— 同一份 payload 重送仍失敗。
這支用 stdlib 直接走 Streamable HTTP，參數原樣送出。

**注意**：`capability_get` 的 `ids: ["…"]`（字串陣列）反而會過 ——
不要把兩者混為一談。

用法：
    # 列出工具
    python3 design_mcp_call.py --list

    # 呼叫工具（參數從 JSON 檔讀）
    python3 design_mcp_call.py execute args.json

    # 呼叫工具（參數從 stdin 讀）
    cat args.json | python3 design_mcp_call.py execute -

環境變數：
    `DESIGN_MCP_ENDPOINT`  覆寫 endpoint（預設從 ~/.minimax/mcp.json 自動發現）
    `DESIGN_MCP_PROJECT`   要綁定的 Design projectId（呼叫前會先 open_project）

輸出：MCP 結果的 JSON（去掉 MCP 的 content 包裝，印出純 payload）。
`execute` 會阻塞到任務 settle，中途把 task 印到 stderr。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROTOCOL_VERSION = "2025-06-18"
DEFAULT_ENDPOINT = "http://127.0.0.1:18810/mcp"
DEFAULT_PROJECT = "p_e1d4830db5541b461ca864bf"  # S02-P04 的 Design 專案；換片時用 DESIGN_MCP_PROJECT 覆寫


def discover_endpoint() -> str:
    """從 ~/.minimax/mcp.json 讀出 minimax-design 的 url；讀不到就用預設。"""
    env = os.environ.get("DESIGN_MCP_ENDPOINT")
    if env:
        return env
    cfg = Path.home() / ".minimax" / "mcp.json"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        url = (data.get("mcpServers") or {}).get("minimax-design", {}).get("url")
        if url:
            return url
    except Exception:
        pass
    return DEFAULT_ENDPOINT


def discover_project() -> str:
    return os.environ.get("DESIGN_MCP_PROJECT", DEFAULT_PROJECT)


class Rpc:
    def __init__(self, endpoint: str | None = None, project_id: str | None = None) -> None:
        self.endpoint = endpoint or discover_endpoint()
        self.project_id = project_id or discover_project()
        self.session_id: str | None = None
        self._id = 0
        self._next_id()

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    def _post(self, payload: dict) -> tuple[dict, dict]:
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.endpoint, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                raw = resp.read().decode("utf-8")
                sid = resp.headers.get("Mcp-Session-Id")
                if sid:
                    self.session_id = sid
                return self._parse(raw), dict(resp.headers)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            return {"__http_error__": e.code, "body": raw}, dict(e.headers)

    @staticmethod
    def _parse(raw: str) -> dict:
        raw = raw.strip()
        if not raw:
            return {}
        # Streamable HTTP 會回 SSE；keepalive 行（": keepalive"）要略過，
        # 取**最後一個** data: 行。
        chunks: list[str] = []
        for line in raw.splitlines():
            if line.startswith("data:"):
                chunk = line[5:].strip()
                if chunk:
                    chunks.append(chunk)
        if chunks:
            raw = chunks[-1]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"__unparsed__": raw[:4000]}

    def initialize(self) -> dict:
        res, _ = self._post({
            "jsonrpc": "2.0", "id": self._next_id(), "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "mavis-design-mcp", "version": "1.0"},
            },
        })
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return res

    def call(self, tool: str, arguments: dict, bind: bool = True) -> dict:
        if self.session_id is None:
            self.initialize()
        # **每次 HTTP 連線都是新的 MCP session** → 專案綁定要重新建立
        if bind and tool != "open_project":
            self._post({
                "jsonrpc": "2.0", "id": self._next_id(), "method": "tools/call",
                "params": {"name": "open_project",
                           "arguments": {"projectId": self.project_id}},
            })
        res, _ = self._post({
            "jsonrpc": "2.0", "id": self._next_id(), "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        })
        return res

    def rpc(self, method: str, params: dict | None = None) -> dict:
        if self.session_id is None:
            self.initialize()
        res, _ = self._post({
            "jsonrpc": "2.0", "id": self._next_id(), "method": method,
            "params": params or {},
        })
        return res


def unwrap(res: dict) -> dict:
    """把 MCP tools/call 的 {content:[{type:text,text:json}]} 解成純 payload。"""
    if "result" not in res:
        return res
    result = res["result"]
    if isinstance(result, dict) and "content" in result:
        texts = [c.get("text", "") for c in result["content"] if c.get("type") == "text"]
        for t in texts:
            try:
                return json.loads(t)
            except json.JSONDecodeError:
                continue
        return {"__text__": texts, "__isError__": result.get("isError")}
    return result


def load_args(arg: str | None) -> dict:
    if not arg:
        return {}
    if arg == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(arg).read_text(encoding="utf-8")
    return json.loads(raw)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    tool = sys.argv[1]
    rpc = Rpc()
    if tool == "--list":
        out = rpc.rpc("tools/list")
        print(json.dumps(unwrap(out), ensure_ascii=False, indent=1)[:6000])
        return 0
    if tool == "--endpoint":
        print(json.dumps({"endpoint": rpc.endpoint, "project_id": rpc.project_id},
                         ensure_ascii=False, indent=1))
        return 0
    args = load_args(sys.argv[2] if len(sys.argv) > 2 else None)
    res = rpc.call(tool, args)
    payload = unwrap(res)
    print(json.dumps(payload, ensure_ascii=False, indent=1))

    # execute 會回 running → 追到終態
    task = (payload or {}).get("task") if isinstance(payload, dict) else None
    if task and task.get("status") in ("accepted", "running", "waiting_user", "unknown"):
        task_id = task["id"]
        print(f"\n[task_wait] {task_id} …", file=sys.stderr)
        while True:
            time.sleep(8)
            w = unwrap(rpc.call("task_wait", {"taskId": task_id}, bind=False))
            t = (w or {}).get("task", {}) if isinstance(w, dict) else {}
            st = t.get("status")
            print(f"[task_wait] {task_id} status={st}", file=sys.stderr)
            if st in ("completed", "failed", "cancelled"):
                print(json.dumps(w, ensure_ascii=False, indent=1))
                return 0 if st == "completed" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

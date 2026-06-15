"""极简 MCP over Streamable-HTTP 客户端。

只实现发布所需的最小子集：initialize 握手 + tools/call。
xiaohongshu-mcp 默认在 http://localhost:18060/mcp 暴露 MCP 端点。

真实网络调用集中在 HttpMcpTransport.call_tool 一处；其余逻辑通过
McpTransport 抽象进行单测（FakeTransport）。
"""
from __future__ import annotations

import json
from typing import Any, Optional

import httpx


class McpError(RuntimeError):
    pass


class McpTransport:
    """工具调用抽象。call_tool 返回 result 的结构化内容（dict）。"""

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict:  # pragma: no cover
        raise NotImplementedError


def _parse_response(resp: httpx.Response) -> dict:
    ctype = resp.headers.get("content-type", "")
    if "text/event-stream" in ctype:
        # 取最后一个 data: 行作为 JSON-RPC 响应
        payload: Optional[dict] = None
        for line in resp.text.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                try:
                    payload = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
        if payload is None:
            raise McpError("SSE 响应未包含可解析的 data 行")
        return payload
    return resp.json()


class HttpMcpTransport(McpTransport):
    """对接 streamable-HTTP MCP 服务（如 xiaohongshu-mcp）。"""

    def __init__(self, url: str, *, timeout: float = 120.0) -> None:
        self.url = url
        self.timeout = timeout
        self._session_id: Optional[str] = None
        self._next_id = 0

    def _rpc(self, client: httpx.Client, method: str, params: dict | None = None) -> httpx.Response:
        self._next_id += 1
        body = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            body["params"] = params
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        resp = client.post(self.url, json=body, headers=headers)
        if "mcp-session-id" in resp.headers:
            self._session_id = resp.headers["mcp-session-id"]
        resp.raise_for_status()
        return resp

    def _initialize(self, client: httpx.Client) -> None:
        self._rpc(
            client,
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "wewrite-web", "version": "0.1.0"},
            },
        )
        # initialized 通知（无 id）
        headers = {"Content-Type": "application/json"}
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        client.post(
            self.url,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers=headers,
        )

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            self._initialize(client)
            resp = self._rpc(client, "tools/call", {"name": name, "arguments": arguments})
            data = _parse_response(resp)
        if "error" in data:
            raise McpError(str(data["error"]))
        result = data.get("result", {})
        return _normalize_tool_result(result)


def _normalize_tool_result(result: dict) -> dict:
    """把 MCP tools/call 结果归一化为 dict。

    MCP 约定 result.content 是块列表；优先解析其中的文本/JSON。
    同时保留 isError、structuredContent 等字段。
    """
    out: dict[str, Any] = {"is_error": bool(result.get("isError", False))}
    if "structuredContent" in result:
        out["data"] = result["structuredContent"]
    texts: list[str] = []
    for block in result.get("content", []) or []:
        if isinstance(block, dict) and block.get("type") == "text":
            texts.append(str(block.get("text", "")))
    out["text"] = "\n".join(texts)
    # 文本本身可能是 JSON
    if texts:
        try:
            out.setdefault("data", json.loads(texts[0]))
        except (json.JSONDecodeError, ValueError):
            pass
    return out

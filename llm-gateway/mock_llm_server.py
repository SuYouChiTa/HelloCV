#!/usr/bin/env python3
"""本地假上游：一个 OpenAI 兼容的 ``/chat/completions``，用来离线联调。

它的价值在于**故意返回各种坏数据**：markdown 围栏、前后夹带废话、尾随逗号、单引号、
非法 option、缺字段、纯文本摆烂、空回复……你的网关必须全部接住。

用法::

    python mock_llm_server.py --port 8801          # 前台运行
    python mock_llm_server.py --list               # 看看预设了哪些坏回复

作为库使用（测试里就是这么做）::

    with MockLlmServer() as server:
        server.base_url  # http://127.0.0.1:<port>
"""

from __future__ import annotations

import argparse
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional

TIME_RE = re.compile(r'"time"\s*:\s*"([^"]{0,64})"')

#: 预设的「坏回复」序列，按请求顺序依次使用（用完后循环最后一个）。
#: 占位符 {time} 会被替换成请求里的 time，方便你观察网关有没有把 time 对齐。
DEFAULT_SCENARIOS: List[str] = [
    '```json\n{"time": "{time}", "option": "rock",}\n```',          # 1 围栏 + 尾随逗号
    '好的，我出剪刀：{"time": "{time}", "option": "scissor"}',        # 2 前后夹带自然语言
    '{"time": "{time}", "option": "SPOCK"}',                          # 3 option 非法
    '抱歉，我无法完成这个请求。',                                       # 4 完全不是 JSON
    '{"option": "paper"}',                                            # 5 缺 time
    '{"time": "{time}", "option": "ROCK", "extra": 123}',             # 6 大写 + 多余字段
    "{'time': '{time}', 'option': 'paper'}",                          # 7 单引号
    '{"time": "{time}", "option": "石头"}',                            # 8 中文取值
    '{"time": "1999-01-01T00:00:00+00:00", "option": "scissor"}',     # 9 time 与请求不一致
    '',                                                               # 10 空回复
    '{"time": "{time}", "option": "paper"',                           # 11 少一个右括号
    '{"time": "{time}", "option": "scissor"}',                        # 12 正常回复
]


class MockLlmServer:
    """后台线程里的假上游。"""

    def __init__(
        self,
        scenarios: Optional[List[str]] = None,
        host: str = "127.0.0.1",
        port: int = 0,
        reasoning_text: str = '{"time": "1970-01-01T00:00:00+00:00", "option": "rock"}',
    ) -> None:
        self.scenarios = list(scenarios if scenarios is not None else DEFAULT_SCENARIOS)
        self.host = host
        self.port = port
        #: 每条回复都附带一段 reasoning_content，模拟思考模型：它**不是**答案，网关必须忽略
        self.reasoning_text = reasoning_text
        self.requests: List[Dict[str, Any]] = []
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    def start(self) -> int:
        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args: Any) -> None:  # 静音
                pass

            def _send(self, status: int, payload: Dict[str, Any]) -> None:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler 的接口
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length).decode("utf-8", "replace")
                try:
                    body = json.loads(raw)
                except ValueError:
                    self._send(400, {"error": {"message": "bad json"}})
                    return

                messages = body.get("messages") or []
                user_text = str(messages[1].get("content") or "") if len(messages) >= 2 else ""
                match = TIME_RE.search(user_text)
                request_time = match.group(1) if match else ""
                with server._lock:
                    index = len(server.requests)
                    template = server.scenarios[index] if index < len(server.scenarios) else server.scenarios[-1]
                server.requests.append(
                    {
                        "path": self.path,
                        "model": body.get("model"),
                        "response_format": body.get("response_format"),
                        "thinking": body.get("thinking"),
                        "temperature": body.get("temperature"),
                        "max_tokens": body.get("max_tokens"),
                        "system_prompt": str(messages[0].get("content") or "") if messages else "",
                        "user_text": user_text,
                        "request_time": request_time,
                        "auth": self.headers.get("Authorization"),
                    }
                )
                content = template.replace("{time}", request_time)
                self._send(
                    200,
                    {
                        "id": "chatcmpl-mock-%d" % index,
                        "object": "chat.completion",
                        "model": body.get("model"),
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "reasoning_content": server.reasoning_text,
                                    "content": content,
                                },
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                    },
                )

        self._httpd = ThreadingHTTPServer((self.host, self.port), Handler)
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, name="mock-llm", daemon=True)
        self._thread.start()
        return self.port

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    @property
    def base_url(self) -> str:
        return "http://%s:%d" % (self.host, self.port)

    def __enter__(self) -> "MockLlmServer":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="本地假 LLM 上游（OpenAI 兼容）")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8801)
    parser.add_argument("--list", action="store_true", help="只打印预设的坏回复，不启动服务")
    args = parser.parse_args()

    if args.list:
        for index, scenario in enumerate(DEFAULT_SCENARIOS, start=1):
            print("%2d. %s" % (index, scenario if scenario else "<空回复>"))
        return

    server = MockLlmServer(host=args.host, port=args.port)
    server.start()
    print("假上游已启动：%s/chat/completions" % server.base_url)
    print("按顺序返回 %d 条预设坏回复，之后循环最后一条。Ctrl-C 退出。" % len(server.scenarios))
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()

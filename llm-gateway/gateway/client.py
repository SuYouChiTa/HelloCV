"""上游 API 转发层：构造请求、发送、重试、取出答案。

这一层要解决的真实问题：

* **鉴权**：``Authorization: Bearer <key>``，key 只从配置/环境变量来，绝不写死；
* **请求格式**：OpenAI 兼容的 ``/chat/completions``，开 ``response_format={"type":"json_object"}``
  让上游保证返回合法 JSON，同时默认关掉思考模式（``thinking={"type":"disabled"}``）省时间；
* **重试**：网络错误、429、5xx、**空回复**都值得退避重试；而 401/403/400（key 错、模型名错、
  参数非法）重试没有意义，要立刻失败；
* **只取 content**：思考模型还会返回 ``reasoning_content``（思维链），它**不是**答案，必须丢掉。

你需要实现（共 3 个）::

    build_body(request)         -> dict                    # 组装 Chat Completions 请求体
    extract_content(response)   -> (content, 有无思维链, finish_reason)
    decide(request)             -> (content, 元信息)        # 带重试的发送主流程

对应测试：``tests/test_client.py``。
"""

from __future__ import annotations

import json  # noqa: F401 - 实现 build_body 时要用到
import random
import threading
import time
from typing import Any, Callable, Dict, Optional, Tuple

import requests

from .config import GatewayConfig
from .prompts import SYSTEM_PROMPT, USER_PREFIX  # noqa: F401 - 实现 build_body 时要用到

__all__ = ["LlmError", "LlmAuthError", "LlmFatalError", "LlmClient"]

#: 这些 HTTP 状态码值得重试（服务端临时不可用 / 限流）
RETRY_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504, 522, 524})


class LlmError(RuntimeError):
    """调用上游失败（重试耗尽或响应结构异常）。"""


class LlmAuthError(LlmError):
    """API Key 缺失/无效（401/403）。"""


class LlmFatalError(LlmError):
    """重试也不会变好的错误（HTTP 400：模型名或参数不合法）。"""


class LlmClient:
    """OpenAI 兼容 Chat Completions 的最小客户端（线程安全）。"""

    def __init__(
        self,
        config: GatewayConfig,
        session: Optional[requests.Session] = None,
        sleep: Callable[[float], None] = time.sleep,
        log: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.config = config
        self.api_key = config.resolved_api_key()
        self._session = session or requests.Session()
        self._sleep = sleep
        self._log = log or (lambda _message: None)
        self._lock = threading.Lock()
        self._closed = False

    # ------------------------------------------------------------------ #
    # 已经写好的部分（不用改）
    # ------------------------------------------------------------------ #
    @property
    def endpoint(self) -> str:
        """拼出完整 URL：``<base>/chat/completions``（base 已经带了就不重复拼）。"""
        base = (self.config.api_base_url or "").rstrip("/")
        if base.endswith("/chat/completions"):
            return base
        return base + "/chat/completions"

    def build_headers(self) -> Dict[str, str]:
        """鉴权与内容类型。"""
        return {
            "Authorization": "Bearer %s" % self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def retry_delay(self, attempt: int, retry_after: Optional[str]) -> float:
        """指数退避 + 抖动；服务端给了 ``Retry-After`` 就听它的（不超过 backoff_max）。"""
        if retry_after:
            try:
                return max(0.0, min(float(retry_after), self.config.backoff_max))
            except (TypeError, ValueError):
                pass
        delay = min(self.config.backoff_base * (2 ** (attempt - 1)), self.config.backoff_max)
        return delay + random.uniform(0.0, self.config.backoff_base)

    def close(self) -> None:
        self._closed = True
        try:
            self._session.close()
        except Exception:  # noqa: BLE001
            pass

    def _error_snippet(self, response: Any) -> str:
        """尽量把上游错误正文里的原因抠出来，方便直接看出"为什么失败"。"""
        try:
            data = response.json()
        except Exception:  # noqa: BLE001
            return ""
        if not isinstance(data, dict):
            return ""
        error = data.get("error")
        if isinstance(error, dict):
            message = error.get("message") or error.get("code")
            return str(message) if message else ""
        if error:
            return str(error)
        message = data.get("message")
        return str(message) if message else ""

    # ------------------------------------------------------------------ #
    # TODO 7：组装请求体
    # ------------------------------------------------------------------ #
    def build_body(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """构造 Chat Completions 请求体。

    提示：

    * ``messages`` 两条：``{"role": "system", "content": SYSTEM_PROMPT}`` 和
      ``{"role": "user", "content": USER_PREFIX + json.dumps(request, ensure_ascii=False, separators=(",", ":"))}``；
    * 还需要 ``model`` / ``stream=False`` / ``temperature`` / ``max_tokens``（都从 ``self.config`` 取）；
    * ``self.config.enable_json_format`` 为真时加
      ``"response_format": {"type": "json_object"}``；
    * 思考开关：``"thinking": {"type": "enabled" if self.config.enable_thinking else "disabled"}``。

    目标：``tests/test_client.py`` 的 ``test_body_*`` 与 ``test_prompt_contains_json_word_for_json_mode`` 通过。
        """
        payload = json.dumps(request, ensure_ascii=False, separators=(",", ":"))
        # 请求实体：把本地 JSON 交给模型，并明确它在跟谁玩（system prompt 里含 JSON 字样）
        body: Dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PREFIX + payload},
            ],
            "stream": False,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if self.config.enable_json_format:
            body["response_format"] = {"type": "json_object"}
        # 思考模式默认关闭：思维链不是答案，还拖慢速度
        body["thinking"] = {"type": "enabled" if self.config.enable_thinking else "disabled"}
        return body

    # ------------------------------------------------------------------ #
    # TODO 8：发送（带重试）
    # ------------------------------------------------------------------ #
    def decide(self, request: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """请求一次出拳，返回 ``(content 文本, 元信息)``；重试耗尽抛 :class:`LlmError`。

    提示（骨架逻辑）：

    * 没有 key（``self.api_key`` 为空）直接抛 :class:`LlmAuthError`；
    * ``attempts = max(1, self.config.max_retries + 1)``，循环 ``attempt = 1..attempts``；
    * 每次 ``self._session.post(self.endpoint, data=payload, headers=..., timeout=(connect, read))``，
      其中 ``payload = json.dumps(body, ensure_ascii=False).encode("utf-8")``；
    * 状态码分支：
      - ``200`` -> ``content, has_reasoning, finish_reason = self.extract_content(response)``，
        返回 ``(content, {"attempt": ..., "http_status": 200, "latency_s": ..., "has_reasoning": ..., "finish_reason": ...})``；
      - ``401`` / ``403`` -> 抛 :class:`LlmAuthError`（不要重试）；
      - ``400`` -> 抛 :class:`LlmFatalError`（不要重试）；
      - 其它：状态码在 ``RETRY_STATUS`` 且还有重试机会 -> ``self._sleep(self.retry_delay(attempt, Retry-After))``
        后 ``continue``；否则抛 :class:`LlmError`；
    * ``LlmError``（比如空回复）和 ``requests.exceptions.RequestException``（网络错误）
      都当作可重试：还有机会就 sleep + 重试，否则把它抛出去 / 循环结束后抛 :class:`LlmError`；
    * 别忘了 ``except (LlmAuthError, LlmFatalError): raise`` 放在前面，避免它们被重试。

    目标：``tests/test_client.py`` 的 ``test_decide_*`` 通过。
        """
        # 没有 key 就没必要发请求：这不是"临时故障"，重试也不会好
        if not self.api_key:
            raise LlmAuthError("缺少 API Key（参数或环境变量 %s）" % self.config.api_key_env)

        attempts = max(1, self.config.max_retries + 1)
        last_error: Optional[Exception] = None

        for attempt in range(1, attempts + 1):
            try:
                body = self.build_body(request)
                payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
                started = time.time()
                response = self._session.post(
                    self.endpoint,
                    data=payload,
                    headers=self.build_headers(),
                    timeout=(self.config.connect_timeout, self.config.request_timeout),
                )
                latency = time.time() - started
                status = getattr(response, "status_code", 0)

                if status == 200:
                    content, has_reasoning, finish_reason = self.extract_content(response)
                    meta = {
                        "attempt": attempt,
                        "http_status": 200,
                        "latency_s": latency,
                        "has_reasoning": has_reasoning,
                        "finish_reason": finish_reason,
                    }
                    return content, meta

                if status in (401, 403):
                    detail = self._error_snippet(response)
                    raise LlmAuthError("上游拒绝鉴权：HTTP %s%s" % (status, "（%s）" % detail if detail else ""))
                if status == 400:
                    detail = self._error_snippet(response)
                    raise LlmFatalError(
                        "上游认为请求非法（模型名/参数）：HTTP 400%s" % ("（%s）" % detail if detail else "")
                    )

                retry_after = None
                headers = getattr(response, "headers", None)
                if isinstance(headers, dict):
                    retry_after = headers.get("Retry-After")
                message = "上游返回 HTTP %s" % status
                if status in RETRY_STATUS and attempt < attempts:
                    self._log("%s，第 %d 次重试" % (message, attempt))
                    self._sleep(self.retry_delay(attempt, retry_after))
                    continue
                detail = self._error_snippet(response)
                raise LlmError("%s%s" % (message, "（%s）" % detail if detail else ""))

            except (LlmAuthError, LlmFatalError):
                # 这两类重试没有意义，直接向上抛
                raise
            except requests.exceptions.RequestException as exc:
                # 网络层错误（超时、连接被重置…）值得退避重试
                last_error = exc
                if attempt < attempts:
                    self._log("网络错误 %s，第 %d 次重试" % (exc, attempt))
                    self._sleep(self.retry_delay(attempt, None))
                    continue
                raise LlmError("调用上游失败（网络错误）：%s" % exc) from exc
            except LlmError as exc:
                # 可重试的业务错误，例如上游返回了空 content
                last_error = exc
                if attempt < attempts:
                    self._log("%s，第 %d 次重试" % (exc, attempt))
                    self._sleep(self.retry_delay(attempt, None))
                    continue
                raise

        raise LlmError("调用上游失败：重试 %d 次后仍未成功（%s）" % (attempts, last_error))

    # ------------------------------------------------------------------ #
    # TODO 9：取出答案
    # ------------------------------------------------------------------ #
    @staticmethod
    def extract_content(response: Any) -> Tuple[str, bool, str]:
        """从 200 响应里取出 ``content``，返回 ``(content, 是否带思维链, finish_reason)``。

    提示：

    * ``response.json()`` 失败（不是 JSON）-> 抛 :class:`LlmError`；
    * ``data.get("choices")`` 为空 -> 抛 :class:`LlmError`；
    * 取 ``choices[0]["message"]`` 的 ``content`` 与 ``reasoning_content``；
    * ``content`` 不是非空字符串时都要抛 :class:`LlmError`（让上层重试），并且错误信息要能区分原因：
      - 有 ``reasoning_content``（思维链不是答案！）-> 提示"只返回了 reasoning_content"；
      - ``finish_reason == "length"`` -> 提示 max_tokens 不够用；
      - 其它 -> 提示 content 为空；
    * ``has_reasoning`` = ``reasoning_content`` 是非空字符串。

    目标：``tests/test_client.py`` 的 ``test_extract_content_*`` 通过。
        """
        try:
            data = response.json()
        except Exception as exc:  # noqa: BLE001 - 上游返回了非 JSON
            raise LlmError("上游响应不是合法 JSON: %s" % exc) from exc

        if not isinstance(data, dict):
            raise LlmError("上游响应顶层不是对象")

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LlmError("上游响应缺少 choices")

        choice = choices[0] if isinstance(choices[0], dict) else {}
        message = choice.get("message")
        if not isinstance(message, dict):
            raise LlmError("上游响应缺少 message")

        content = message.get("content")
        reasoning = message.get("reasoning_content")
        finish_reason = choice.get("finish_reason")

        # 思维链不是答案，但要记下来，方便上层判断"为什么会空"
        has_reasoning = isinstance(reasoning, str) and bool(reasoning)
        if not isinstance(content, str) or not content.strip():
            if has_reasoning:
                raise LlmError("上游只返回了 reasoning_content（思维链不是答案），没有 content")
            if finish_reason == "length":
                raise LlmError("上游回答被 max_tokens 截断（finish_reason=length），content 为空")
            raise LlmError("上游返回的 content 为空")

        return content, has_reasoning, str(finish_reason or "")

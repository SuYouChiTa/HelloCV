"""网关配置（本文件是脚手架，不需要修改）。"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from typing import Any, Dict

__all__ = ["GatewayConfig"]


@dataclass
class GatewayConfig:
    """一次运行所需的全部配置。

    所有字段都有默认值，方便在测试里 ``GatewayConfig(offline=True)`` 一把构造。
    """

    # ---- 上游 API ----
    api_base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-flash"
    api_key: str = ""
    api_key_env: str = "DEEPSEEK_API_KEY"

    # ---- 请求参数 ----
    enable_json_format: bool = True
    enable_thinking: bool = False
    temperature: float = 0.2
    max_tokens: int = 256

    # ---- 超时与重试 ----
    request_timeout: float = 15.0
    connect_timeout: float = 5.0
    max_retries: int = 2
    backoff_base: float = 0.5
    backoff_max: float = 4.0

    # ---- 其它 ----
    offline: bool = False  # True = 完全不调用 API，只用本地兜底出拳

    def resolved_api_key(self) -> str:
        """参数里的 key 优先，其次读环境变量（不要把 key 写进代码）。"""
        if self.api_key and self.api_key.strip():
            return self.api_key.strip()
        return (os.environ.get(self.api_key_env) or "").strip()

    def with_overrides(self, **overrides: Any) -> "GatewayConfig":
        """返回一个覆盖了部分字段的新配置（``None`` 表示不改）。"""
        clean: Dict[str, Any] = {
            key: value for key, value in overrides.items() if value is not None and hasattr(self, key)
        }
        return replace(self, **clean) if clean else replace(self)

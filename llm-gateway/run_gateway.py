#!/usr/bin/env python3
"""网关命令行入口：一行 JSON 请求进，一行 JSON 决策出。

用法::

    # 1) 离线模式（不调用任何 API，用本地规则出拳，先把流水线跑通）
    echo '{"time": "2026-01-01T00:00:00+00:00"}' | python run_gateway.py --offline

    # 2) 对着本地假上游联调（推荐，不花钱、结果可复现）
    python mock_llm_server.py --port 8801 &
    python run_gateway.py --api-base-url http://127.0.0.1:8801 < samples/requests.jsonl

    # 3) 真实 DeepSeek
    export DEEPSEEK_API_KEY=sk-xxx
    python run_gateway.py < samples/requests.jsonl

    # 4) 文件进文件出
    python run_gateway.py --input samples/requests.jsonl --output decisions.jsonl
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from gateway.app import JsonGateway
from gateway.config import GatewayConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="石头剪刀布决策网关（JSON 进 / JSON 出）")
    parser.add_argument("--input", default="-", help="输入文件（每行一个 JSON 请求），默认 stdin")
    parser.add_argument("--output", default="-", help="输出文件（每行一个 JSON 决策），默认 stdout")
    parser.add_argument("--api-base-url", default=None, help="上游 API 地址，默认 https://api.deepseek.com")
    parser.add_argument("--api-key", default=None, help="API Key（默认读环境变量 DEEPSEEK_API_KEY）")
    parser.add_argument("--model", default=None, help="模型名，默认 deepseek-flash")
    parser.add_argument("--offline", action="store_true", help="完全不调用 API，只用本地兜底出拳")
    parser.add_argument("--max-retries", type=int, default=None, help="失败重试次数，默认 2")
    parser.add_argument("--request-timeout", type=float, default=None, help="读超时秒数，默认 15")
    parser.add_argument("--max-tokens", type=int, default=None, help="max_tokens，默认 256")
    parser.add_argument("--enable-thinking", action="store_true", help="打开思考模式（更慢，默认关闭）")
    parser.add_argument("--quiet", action="store_true", help="不打印日志到 stderr")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    config = GatewayConfig().with_overrides(
        api_base_url=args.api_base_url,
        api_key=args.api_key,
        model=args.model,
        max_retries=args.max_retries,
        request_timeout=args.request_timeout,
        max_tokens=args.max_tokens,
    )
    if args.offline:
        config = config.with_overrides(offline=True)
    if args.enable_thinking:
        config = config.with_overrides(enable_thinking=True)

    log = (lambda _message: None) if args.quiet else None
    gateway = JsonGateway(config, log=log)

    reader = sys.stdin if args.input == "-" else open(args.input, "r", encoding="utf-8")
    writer = sys.stdout if args.output == "-" else open(args.output, "w", encoding="utf-8")
    try:
        stats = gateway.run(reader, writer)
    finally:
        if args.input != "-":
            reader.close()
        if args.output != "-":
            writer.close()
        client = getattr(gateway, "client", None)
        if client is not None and hasattr(client, "close"):
            client.close()

    print(
        "处理 %d 行：直接可用 %d / 已修正 %d / 本地兜底 %d / 输入非法 %d"
        % (stats.lines, stats.ok, stats.repaired, stats.fallback, stats.bad_input),
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

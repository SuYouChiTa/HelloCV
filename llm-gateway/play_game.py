#!/usr/bin/env python3
"""和 DeepSeek 玩几轮石头剪刀布（对局演示）。

用法::

    # 离线：不花钱，先看流水线是否跑通（本地兜底策略是「反制对手上一手」）
    python play_game.py --rounds 10 --offline

    # 对着本地假上游玩（会看到网关怎么接住各种坏回复）
    python mock_llm_server.py --port 8801 &
    python play_game.py --rounds 6 --api-base-url http://127.0.0.1:8801

    # 真实 DeepSeek
    export DEEPSEEK_API_KEY=sk-xxx
    python play_game.py --rounds 10 --strategy counter
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from gateway.app import JsonGateway
from gateway.config import GatewayConfig
from gateway.game import STRATEGIES, play_rounds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="和 DeepSeek 玩石头剪刀布")
    parser.add_argument("--rounds", type=int, default=10, help="对局轮数，默认 10")
    parser.add_argument("--strategy", default="random", choices=STRATEGIES, help="本地对手策略")
    parser.add_argument("--seed", type=int, default=None, help="随机种子（让对局可复现）")
    parser.add_argument("--offline", action="store_true", help="不调用 API，只用本地兜底出拳")
    parser.add_argument("--api-base-url", default=None, help="上游 API 地址")
    parser.add_argument("--api-key", default=None, help="API Key（默认读环境变量）")
    parser.add_argument("--model", default=None, help="模型名")
    parser.add_argument("--quiet", action="store_true", help="只打印每轮结果，不打印网关日志")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    config = GatewayConfig().with_overrides(
        api_base_url=args.api_base_url, api_key=args.api_key, model=args.model
    )
    if args.offline:
        config = config.with_overrides(offline=True)

    gateway = JsonGateway(config, log=(lambda _message: None) if args.quiet else None)
    print(
        "对局开始：%d 轮，对手策略=%s，模式=%s\n"
        % (args.rounds, args.strategy, "离线兜底" if config.offline else config.model)
    )
    result = play_rounds(
        gateway,
        rounds=args.rounds,
        strategy=args.strategy,
        seed=args.seed,
        log=None if args.quiet else print,
    )
    print("\n" + result.summary())
    client = getattr(gateway, "client", None)
    if client is not None and hasattr(client, "close"):
        client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

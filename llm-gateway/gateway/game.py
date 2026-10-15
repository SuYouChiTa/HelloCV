"""石头剪刀布的对局逻辑：本地对手 + 裁判 + 记分（本文件是脚手架，不需要修改）。

网关本身只负责「给一行请求，回一行决策」；这里负责把它跑成一场真正的比赛：

* :class:`Opponent` 提供几种本地策略（随机 / 循环 / 反制 / 模仿）；
* :func:`play_rounds` 每轮构造一行请求 JSON（含对手历史 ``history``），
  交给网关决策，再用 :func:`gateway.rules.judge` 判定胜负并记分。
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from .rules import OPTIONS, counter_to, judge, now_iso

__all__ = ["Opponent", "Round", "MatchResult", "play_rounds", "STRATEGIES"]

#: 本地对手策略：随机 / 固定循环 / 专打模型上一手 / 照抄模型上一手
STRATEGIES = ("random", "cycle", "counter", "copy")


class Opponent:
    """不调用任何 API 的本地对手。"""

    def __init__(self, strategy: str = "random", rng: Optional[random.Random] = None) -> None:
        if strategy not in STRATEGIES:
            raise ValueError("未知策略 %r，可选：%s" % (strategy, "/".join(STRATEGIES)))
        self.strategy = strategy
        self.rng = rng or random.Random()

    def choose(self, model_history: List[str], own_history: List[str]) -> str:
        """根据两边历史出拳（实现为纯函数，方便测试）。"""
        if self.strategy == "cycle":
            return OPTIONS[len(own_history) % len(OPTIONS)]
        if self.strategy == "counter" and model_history:
            return counter_to(model_history[-1])
        if self.strategy == "copy" and model_history:
            return model_history[-1]
        return self.rng.choice(OPTIONS)


@dataclass
class Round:
    index: int
    time: str
    model_option: str
    opponent_option: str
    result: int  # 1 模型赢 / 0 平 / -1 模型输
    notes: List[str] = field(default_factory=list)

    @property
    def result_text(self) -> str:
        return {1: "模型赢", 0: "平局", -1: "模型输"}[self.result]


@dataclass
class MatchResult:
    rounds: List[Round] = field(default_factory=list)
    fallback_rounds: int = 0  # 其中有多少轮是网关本地兜底出拳

    @property
    def wins(self) -> int:
        return sum(1 for item in self.rounds if item.result == 1)

    @property
    def losses(self) -> int:
        return sum(1 for item in self.rounds if item.result == -1)

    @property
    def draws(self) -> int:
        return sum(1 for item in self.rounds if item.result == 0)

    def summary(self) -> str:
        return "共 %d 轮：模型赢 %d / 平 %d / 输 %d（其中本地兜底 %d 轮）" % (
            len(self.rounds),
            self.wins,
            self.draws,
            self.losses,
            self.fallback_rounds,
        )


def play_rounds(
    gateway: Any,
    rounds: int = 10,
    strategy: str = "random",
    seed: Optional[int] = None,
    log: Optional[Callable[[str], None]] = None,
) -> MatchResult:
    """让网关和本地对手打 ``rounds`` 轮，返回对局结果。

    每轮发给网关的请求就是协议里的一行：

    ``{"time": "<ISO8601>", "history": ["rock", "paper", ...]}``
    """
    logger = log or (lambda _message: None)
    opponent = Opponent(strategy, random.Random(seed))
    result = MatchResult()
    model_history: List[str] = []
    opponent_history: List[str] = []

    for index in range(1, rounds + 1):
        request = {"time": now_iso(), "history": list(opponent_history[-10:])}
        decision, notes = gateway.handle_line(json.dumps(request, ensure_ascii=False))
        model_option = decision["option"]
        opponent_option = opponent.choose(model_history, opponent_history)
        outcome = judge(model_option, opponent_option)

        model_history.append(model_option)
        opponent_history.append(opponent_option)
        if any("兜底" in note for note in notes):
            result.fallback_rounds += 1
        result.rounds.append(Round(index, request["time"], model_option, opponent_option, outcome, list(notes)))
        logger(
            "第 %2d 轮  模型=%s  对手=%s(%s)  %s  %s"
            % (
                index,
                model_option,
                opponent_option,
                strategy,
                {1: "模型赢", 0: "平局", -1: "模型输"}[outcome],
                ("| " + "; ".join(notes)) if notes else "",
            )
        )

    return result

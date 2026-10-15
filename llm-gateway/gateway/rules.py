"""决策字段的解析、规范化与兜底。

约定的协议（一行进、一行出）::

    输入：{"time": "<本轮时间>", "history": ["rock", "paper", ...]}   # history 可选
    输出：{"time": "<与输入一致>", "option": "rock|scissor|paper"}    # 只允许这两个键

分层原则：

* :func:`parse_request` / :func:`normalize_time` —— 「读」：把外部输入变成可信的 Python 对象；
* :func:`normalize_option` —— 「整理」：把模型可能写歪的取值（大写、复数、中文）拉回枚举；
* :func:`validate_decision` / :func:`fallback_decision` —— 「兜底」：任何情况下都能给出合法决策；
* :func:`build_decision` / :func:`is_valid_decision` —— 「出口闸门」：只放行 {time, option}。

**网关是可信边界**：``time`` 一律以网关收到/生成的时间为准，不采信模型自己写的 time。

你需要实现（共 3 个）::

    normalize_option(value)                      -> str | None
    validate_decision(candidate, request)        -> (决策, 说明列表)
    fallback_decision(request)                   -> (决策, 说明列表)

对应测试：``tests/test_rules.py`` 的「整理」「校验与兜底」两节。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "OPTIONS",
    "BEATS",
    "ALIASES",
    "now_iso",
    "normalize_time",
    "parse_request",
    "get_time",
    "history_of",
    "normalize_option",
    "build_decision",
    "is_valid_decision",
    "validate_decision",
    "fallback_decision",
    "judge",
    "counter_to",
]

#: 合法出拳（必须是这三个小写英文，顺序固定，方便测试）
OPTIONS: Tuple[str, ...] = ("rock", "scissor", "paper")

#: 谁赢谁：key 打败 value
BEATS: Dict[str, str] = {"rock": "scissor", "scissor": "paper", "paper": "rock"}

#: 模型可能写出来的同义写法 -> 标准值（已经给你了，直接用）
ALIASES: Dict[str, str] = {
    "rock": "rock",
    "rocks": "rock",
    "石头": "rock",
    "拳头": "rock",
    "锤子": "rock",
    "scissor": "scissor",
    "scissors": "scissor",
    "剪刀": "scissor",
    "paper": "paper",
    "papers": "paper",
    "布": "paper",
}

_MAX_HISTORY = 10


# --------------------------------------------------------------------------- #
# 读：输入解析（已写好，不用改）
# --------------------------------------------------------------------------- #
def now_iso() -> str:
    """当前时间（带时区的 ISO8601），输入缺 time 时由网关自己补。"""
    return datetime.now(timezone.utc).isoformat()


def normalize_time(value: Any) -> Optional[str]:
    """把 time 字段拉成非空字符串；无法识别返回 ``None``。"""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned or len(cleaned) > 64:
            return None
        return cleaned
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    return None


def parse_request(raw: Any) -> Dict[str, Any]:
    """解析一行请求：``str`` 走 ``json.loads``，``dict`` 直接透传，其余抛 ``ValueError``。"""
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("请求为空")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("请求顶层必须是 JSON 对象")
    return parsed


def get_time(request: Dict[str, Any]) -> Optional[str]:
    """取请求里的 time（缺失或非法返回 ``None``）。"""
    if not isinstance(request, dict):
        return None
    return normalize_time(request.get("time"))


def history_of(request: Dict[str, Any]) -> List[str]:
    """取对手历史出拳：只保留能识别的元素，最多保留最近 10 个。"""
    if not isinstance(request, dict):
        return []
    raw = request.get("history")
    if not isinstance(raw, list):
        return []
    history: List[str] = []
    for item in raw:
        option = normalize_option(item)
        if option is not None:
            history.append(option)
    return history[-_MAX_HISTORY:]


# --------------------------------------------------------------------------- #
# TODO 4：枚举归一化
# --------------------------------------------------------------------------- #
def normalize_option(value: Any) -> Optional[str]:
    """把模型给的取值拉回 ``OPTIONS``；无法识别返回 ``None``。

    提示：

    * 非字符串直接返回 ``None``（``42`` / ``None`` / ``["rock"]`` 都不算有效出拳）；
    * ``value.strip().lower()`` 之后查 :data:`ALIASES`：
      这样 ``"  ROCK "`` -> ``rock``、``"Scissors"`` -> ``scissor``、``"石头"`` -> ``rock``。

    目标：``tests/test_rules.py`` 的 ``test_normalize_option_*`` 与 ``test_aliases_*`` 通过。
    """
    # 只认字符串：数字 / None / 列表都不是合法出拳，直接判无效。
    if not isinstance(value, str):
        return None
    return ALIASES.get(value.strip().lower())


# --------------------------------------------------------------------------- #
# 出口闸门（已写好，不用改）
# --------------------------------------------------------------------------- #
def build_decision(time_value: Any, option: Any) -> Dict[str, Any]:
    """按协议构造决策对象：**只有** time 与 option 两个键，多余字段一律不带出网关。"""
    return {"time": str(time_value), "option": str(option)}


def is_valid_decision(payload: Any) -> bool:
    """出口自检：必须是恰好含 time / option 两个键的 JSON 对象，且 option 合法。"""
    if not isinstance(payload, dict):
        return False
    if set(payload.keys()) != {"time", "option"}:
        return False
    if not isinstance(payload["time"], str) or not payload["time"]:
        return False
    return payload["option"] in OPTIONS


# --------------------------------------------------------------------------- #
# TODO 5：校验与修正
# --------------------------------------------------------------------------- #
def validate_decision(candidate: Any, request: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """把模型输出修正成合法决策，返回 ``(决策, 修正说明列表)``，**永不抛异常**。

    提示：

    1. ``candidate`` 不是 dict -> 直接 ``return fallback_decision(request)``，
       并在说明里加上 ``"非对象->兜底"``；
    2. ``normalize_option(candidate.get("option"))`` 得到 ``None`` -> 同样走兜底，
       说明里加上 ``"option 非法->兜底"``；
    3. time 以请求为准（网关是可信边界）：
       * 请求里有 time -> 用它；若模型也写了不同的 time，说明里加一句 "丢弃模型的 time"；
       * 请求里没有 -> 用模型给的 time（说明 "请求无 time->用模型的 time"）；
       * 都没有 -> ``now_iso()``（说明 "请求无 time->用当前时间"）；
    4. 最后 ``build_decision(time_value, option)`` 返回，保证只有两个键。

    注意 ``fallback_decision`` 返回的是 ``(决策, 说明)`` 元组，别把元组当决策返回。

    目标：``tests/test_rules.py`` 的 ``test_validate_decision_*`` 通过。
    """
    # 1) 根本不是对象：直接兜底（fallback_decision 返回的是元组）
    if not isinstance(candidate, dict):
        decision, notes = fallback_decision(request)
        return decision, ["非对象->兜底"] + notes

    # 2) option 拉不回枚举：同样兜底
    option = normalize_option(candidate.get("option"))
    if option is None:
        decision, notes = fallback_decision(request)
        return decision, ["option 非法->兜底"] + notes

    notes: List[str] = []

    # 3) time 以请求为准（网关是可信边界，不采信模型自己写的时间）
    request_time = get_time(request)
    model_time = normalize_time(candidate.get("time"))
    if request_time:
        time_value = request_time
        if model_time and model_time != request_time:
            notes.append("丢弃模型的 time")
    elif model_time:
        time_value = model_time
        notes.append("请求无 time->用模型的 time")
    else:
        time_value = now_iso()
        notes.append("请求无 time->用当前时间")

    # 4) 出口只放行 {time, option}
    return build_decision(time_value, option), notes


# --------------------------------------------------------------------------- #
# TODO 6：本地兜底
# --------------------------------------------------------------------------- #
def counter_to(option: str) -> str:
    """能赢过 ``option`` 的出拳（已写好，直接用）。"""
    for candidate, beaten in BEATS.items():
        if beaten == option:
            return candidate
    raise ValueError("未知出拳：%r" % (option,))


def fallback_decision(request: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """不依赖模型的本地兜底决策：任何输入都要给出合法决策。

    提示：

    * ``history = history_of(request)``；有历史就出 ``counter_to(history[-1])``
      （对手上一手是 X，就出能赢 X 的拳），说明里写 ``"兜底:counter(X)"``；
    * 没有历史就出 ``"rock"``，说明里写 ``"兜底:rock"``；
    * time 用 ``get_time(request) or now_iso()``；
    * 返回 ``(build_decision(time_value, option), [说明])``。

    目标：``tests/test_rules.py`` 的 ``test_fallback_decision_*`` 通过。
    """
    history = history_of(request)
    if history:
        # 对手上一手是 X，就出能赢 X 的那一手
        option = counter_to(history[-1])
        note = "兜底:counter(%s)" % history[-1]
    else:
        option = "rock"
        note = "兜底:rock"

    time_value = get_time(request) or now_iso()
    return build_decision(time_value, option), [note]


# --------------------------------------------------------------------------- #
# 裁判（已写好，不用改）
# --------------------------------------------------------------------------- #
def judge(mine: str, theirs: str) -> int:
    """比较两手：``1`` 我赢，``-1`` 我输，``0`` 平局。"""
    if mine == theirs:
        return 0
    return 1 if BEATS.get(mine) == theirs else -1

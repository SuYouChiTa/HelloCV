"""把「读输入 -> 转发 -> JSON 容错 -> 校验 -> 兜底 -> 写输出」串成一条流水线。

对外只有一条硬性约定：**读进来一行，就写出去一行合法 JSON 决策**。
不管上游挂了、模型胡说、还是输入本身不是 JSON，都不允许把异常抛给调用方，
也不允许输出半截/非法 JSON —— 否则下游（真实系统里的消息总线）会直接报错。

你需要实现（共 1 个，但它是把前面所有零件接起来的那一步）::

    handle_request(request) -> (决策, 说明列表)

``handle_line`` / ``run`` / ``Stats`` 已经写好，不用改。
对应测试：``tests/test_app.py``。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, TextIO, Tuple

from .client import LlmClient
from .config import GatewayConfig
from .json_guard import JsonGuardError, dumps_json, loads_object  # noqa: F401 - 实现 handle_request 时要用到
from .rules import (  # noqa: F401 - 实现 handle_request 时要用到
    build_decision,
    fallback_decision,
    get_time,
    is_valid_decision,
    now_iso,
    parse_request,
    validate_decision,
)

__all__ = ["Stats", "JsonGateway"]


@dataclass
class Stats:
    """跑完一轮之后的统计，方便观察容错到底起了多少作用。"""

    lines: int = 0
    ok: int = 0        # 模型的答案直接可用
    repaired: int = 0  # 可用但被网关修正过（例如丢弃模型自报的 time）
    fallback: int = 0  # 走了本地兜底出拳
    bad_input: int = 0  # 输入行不是合法 JSON

    def as_dict(self) -> Dict[str, int]:
        return {
            "lines": self.lines,
            "ok": self.ok,
            "repaired": self.repaired,
            "fallback": self.fallback,
            "bad_input": self.bad_input,
        }


class JsonGateway:
    """一进一出的决策网关。"""

    def __init__(
        self,
        config: GatewayConfig,
        client: Optional[Any] = None,
        log: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.config = config
        self.log = log or (lambda message: print("[gateway] %s" % message, file=sys.stderr, flush=True))
        if client is not None:
            self.client = client
        elif config.offline:
            self.client = None  # 离线模式：只用本地规则出拳
        else:
            self.client = LlmClient(config, log=lambda message: self.log("上游: %s" % message))

    # ------------------------------------------------------------------ #
    # TODO 10：核心编排
    # ------------------------------------------------------------------ #
    def handle_request(self, request: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """核心编排：调用上游 -> JSON 容错 -> 合法性校验 -> 兜底。

    返回 ``(合法决策, 说明列表)``，**永不抛异常**。提示：

    1. ``notes: List[str] = []``、``decision: Optional[Dict[str, Any]] = None``；
    2. 只有在 ``self.client is not None``（在线模式）时才调用上游：
       * ``content, meta = self.client.decide(request)`` 拿回原始文本；
       * ``candidate = loads_object(content)`` 把任意文本整理成 dict；
       * ``decision, notes = validate_decision(candidate, request)`` 校验/修正；
       * 可以顺手把 ``meta["latency_s"]`` 之类写进日志（可选）；
    3. ``JsonGuardError``（模型输出整理不出来）和**其它任何异常**（上游超时、500……）
       都要被接住：往 ``notes`` 里记一句原因，然后 ``decision`` 保持为 ``None``；
    4. ``decision is None`` 时用 ``fallback_decision(request)`` 本地出拳，
       ``notes`` 里加上 ``"本地兜底"`` 和兜底自己的说明；
    5. 出口用 ``is_valid_decision(decision)`` 再自检一次，
       万一不合法就退化成 ``build_decision(get_time(request) or now_iso(), "rock")``，
       ``notes`` 里加上 ``"出口自检失败->rock"``；
    6. 返回 ``(decision, notes)``。

    目标：``tests/test_app.py`` 的 ``test_handle_request_*`` 与 ``test_run_*`` 通过。
        """
        notes: List[str] = []
        decision: Optional[Dict[str, Any]] = None

        # 1) 在线模式才调用上游；离线模式（或没有 client）直接用本地规则
        if self.client is not None:
            try:
                content, meta = self.client.decide(request)
                self.log("上游返回 HTTP %s，耗时 %.2fs" % (meta.get("http_status"), meta.get("latency_s") or 0.0))
                candidate = loads_object(content)
                decision, notes = validate_decision(candidate, request)
            except JsonGuardError as exc:
                # 模型说的不是 JSON：记下来，走兜底
                notes.append("上游异常: 模型输出无法整理成 JSON（%s）" % exc)
            except Exception as exc:  # noqa: BLE001 - 上游超时/500/鉴权失败…一律兜底
                notes.append("上游异常: %s" % exc)

        # 2) 没拿到决策就本地兜底（任何输入都必须给出一行合法 JSON）
        if decision is None:
            fallback, extra = fallback_decision(request)
            decision = fallback
            notes.append("本地兜底")
            notes.extend(extra)

        # 3) 出口自检：万一还不合法，退化成最保守的 rock
        if not is_valid_decision(decision):
            decision = build_decision(get_time(request) or now_iso(), "rock")
            notes.append("出口自检失败->rock")

        return decision, notes

    # ------------------------------------------------------------------ #
    # 已写好：输入解析与主循环（不用改）
    # ------------------------------------------------------------------ #
    def handle_line(self, line: str) -> Tuple[Dict[str, Any], List[str]]:
        """一行文本 -> ``(决策, 说明)``。

        输入不是 JSON 时**不转发给上游**（坏数据不值得花钱），直接用「当前时间 + 兜底出拳」回一行。
        """
        notes: List[str] = []
        text = line.strip()
        try:
            request = parse_request(text)
        except Exception as exc:  # noqa: BLE001 - 坏输入也要有输出
            notes.append("输入不是合法 JSON: %s" % exc)
            decision, extra = fallback_decision({})
            return decision, notes + extra
        decision, extra = self.handle_request(request)
        return decision, notes + extra

    def run(self, reader: Iterable[str], writer: TextIO) -> Stats:
        """逐行处理，写出 ``{"time": ..., "option": ...}``，返回统计。"""
        stats = Stats()
        for line in reader:
            if not line.strip():
                continue
            stats.lines += 1
            try:
                decision, notes = self.handle_line(line)
            except Exception as exc:  # noqa: BLE001 - 最后一道保险
                decision, notes = build_decision(now_iso(), "rock"), ["内部异常: %s" % exc]
            writer.write(dumps_json(decision) + "\n")
            writer.flush()
            if any("输入不是合法 JSON" in note for note in notes):
                stats.bad_input += 1
            if any("兜底" in note for note in notes):
                stats.fallback += 1
            elif notes:
                stats.repaired += 1
            else:
                stats.ok += 1
            self.log(
                "第 %d 行 -> %s %s"
                % (stats.lines, dumps_json(decision), ("| " + "; ".join(notes)) if notes else "")
            )
        return stats

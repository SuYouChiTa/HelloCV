"""预设提示词（本文件是脚手架，不需要修改）。

注意两个细节，它们直接决定 json_object 模式能不能稳定工作：

1. 提示词里必须出现 **json** 字样（官方 JSON Output 文档的硬性要求）；
2. 必须给出目标字段的**示例**，并明确「只能是小写英文、不许有多余字段、不许 markdown」。
"""

from __future__ import annotations

__all__ = ["SYSTEM_PROMPT", "USER_PREFIX", "OPTION_HINT"]

OPTION_HINT = 'rock（石头）、scissor（剪刀）、paper（布）'

SYSTEM_PROMPT = (
    "你在玩石头剪刀布（rock-paper-scissors），负责为当前这一轮出拳。\n"
    "输入是一个 JSON 对象，里面有一个字符串字段 time（本轮时间），可能还有可选数组 history"
    "（对手的历史出拳，按时间从旧到新，元素为 rock/scissor/paper）。\n"
    "胜负规则：rock 赢 scissor，scissor 赢 paper，paper 赢 rock。\n"
    "你必须只输出一个 JSON 对象，恰好包含两个键：\n"
    '  "time"：字符串，与输入里的 time 完全一致；\n'
    '  "option"：字符串，只能取 ' + OPTION_HINT + " 之一，必须是小写英文。\n"
    "可以结合 history 推测对手习惯，拿不准时随机选一个即可。\n"
    "禁止输出 markdown 代码块、解释文字或任何多余字段；除这个 JSON 对象外不要输出别的内容。\n"
    '例如：{"time": "2026-01-01T00:00:00+00:00", "option": "rock"}'
)

USER_PREFIX = (
    "这是本轮的请求 JSON，请按系统提示的格式只输出一个决策 JSON 对象"
    "（只包含 time 与 option 两个键）：\n"
)

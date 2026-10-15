"""JSON 容错层：把模型返回的**任意文本**整理成 Python 字典。

这是本练习最核心的模块，也是你主要要写的地方。

模型（即使开了 JSON 模式）经常返回这些东西：

* ````` ```json {...} ``` ```` —— 外面套了 markdown 代码块
* ``好的，我出剪刀：{"option": "scissor"}`` —— 前后夹带自然语言
* ``{"option": "rock",}`` —— 尾随逗号
* ``{'option': 'rock'}`` —— 单引号
* ``{"option": None}`` —— Python 的 None / True / False
* ``{"option": "rock"`` —— 少了一个右括号
* 直接摆烂：``抱歉，我无法回答。``

``loads_object`` 的容错阶梯（已经给你写好了，它调用下面三个 TODO）：

1. 直接 ``json.loads``
2. :func:`strip_code_fence` 剥掉 markdown 围栏
3. :func:`find_first_json_object` 从自由文本里抠出配平的 ``{...}``
4. :func:`repair_json_text` 修复文本，再解析一次
5. 顶层是数组就取第一个对象
6. 全部失败 —— 抛 :class:`JsonGuardError`，由上层走兜底逻辑

**重要原则：容错不等于瞎猜。** 这里只负责「把明显是 JSON 的文本救回来」，
不做语义修补；字段缺失、取值非法是 :mod:`gateway.rules` 的事。

你需要实现（共 3 个）::

    strip_code_fence(text)          -> str          # 剥 markdown 围栏
    find_first_json_object(text)    -> str | None   # 字符串感知的括号配对
    repair_json_text(text)          -> str          # 文本级修复

对应测试：``tests/test_json_guard.py``。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

__all__ = [
    "JsonGuardError",
    "strip_code_fence",
    "find_first_json_object",
    "repair_json_text",
    "loads_object",
    "loads_object_or_none",
    "dumps_json",
]


class JsonGuardError(ValueError):
    """无法从给定文本里整理出 JSON 对象。"""


# --------------------------------------------------------------------------- #
# TODO 1：剥掉 markdown 围栏
# --------------------------------------------------------------------------- #
def strip_code_fence(text: str) -> str:
    """如果文本里有 ```` ``` ```` 围栏，返回围栏**内部**的内容；否则原样返回。

    提示：

    * ``text.split("```")`` 之后，下标 1、3、5… 的片段就是围栏内部；
    * 语言标记行（``json`` / ``JSON`` / ``js``…）要丢掉：判断第一行很短且不含 ``{``；
    * 没写结束围栏（模型被截断）时，取到文本结尾即可（``split`` 天然就是这个效果）；
    * 围栏可能出现在自然语言中间（``好的：```json {...}``` ``），别只看开头；
    * 有多个围栏时，优先返回「第一个以 ``{`` 开头的」，没有就返回第一个非空片段。

    目标：``tests/test_json_guard.py`` 里的 5 个 ``test_strip_code_fence_*`` 通过。
    """
    if "```" not in text:
        return text

    # split 之后下标 1、3、5… 的片段就是围栏内部（模型截断时最后一段没有收尾围栏）。
    pieces = [piece for piece in text.split("```")[1::2] if piece.strip()]
    if not pieces:
        return text

    cleaned = []
    for piece in pieces:
        lines = piece.split("\n", 1)
        # 语言标记行（json / JSON / js…）的特征：很短、且不含花括号。
        if len(lines) == 2 and len(lines[0].strip()) <= 10 and "{" not in lines[0]:
            piece = lines[1]
        cleaned.append(piece)

    # 优先第一个以 { 开头的片段（多半就是 JSON 本体）。
    for piece in cleaned:
        if piece.lstrip().startswith("{"):
            return piece.strip()
    return cleaned[0].strip()


# --------------------------------------------------------------------------- #
# TODO 2：字符串感知的括号配对
# --------------------------------------------------------------------------- #
def find_first_json_object(text: str) -> Optional[str]:
    """从自由文本中找出第一个**括号配平**的 ``{...}``，找不到返回 ``None``。

    提示：

    * 逐字符扫描，维护 ``depth``（花括号深度）、``in_string``、``escaped`` 三个状态；
    * 字符串内部的 ``{`` ``}`` 不参与计数；``\\"`` 不算字符串结束；
    * 从每个 ``{`` 开始尝试，``depth`` 回到 0 就返回 ``text[start:index + 1]``；
    * 某个 ``{`` 一直没配平，就换下一个 ``{`` 继续找；
    * 找不到任何配平对象时返回 ``None``（上层会去走修复或兜底）。

    目标：``tests/test_json_guard.py`` 里的 6 个 ``test_find_first_json_object_*`` 通过。
    """
    length = len(text)
    for start in range(length):
        if text[start] != "{":
            continue
        # 从每个 { 开始尝试配对；没配平就换下一个 { 继续。
        depth = 1
        in_string = False
        escaped = False
        index = start + 1
        while index < length:
            char = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start:index + 1]
            index += 1
    return None


# --------------------------------------------------------------------------- #
# 已经写好的小工具（修复时用得上，不用改）
# --------------------------------------------------------------------------- #
_PY_LITERAL_RE = re.compile(r"(?<![\w\"'])(None|True|False)(?![\w\"'])")
_PY_LITERALS = {"None": "null", "True": "true", "False": "false"}
_OPEN_TO_CLOSE = {"\u201c": "\u201d", "\u2018": "\u2019"}  # “ -> ” ，‘ -> ’
_ANY_QUOTE = ('"', "'", "\u201c", "\u201d", "\u2018", "\u2019")


def _strip_comments(text: str) -> str:
    """去掉 ``//`` 与 ``/* */`` 注释（字符串内部的斜杠要保留，例如 https://）。"""
    out: List[str] = []
    in_string = False
    escaped = False
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            out.append(char)
            index += 1
        elif char == "/" and index + 1 < length and text[index + 1] == "/":
            while index < length and text[index] != "\n":
                index += 1
        elif char == "/" and index + 1 < length and text[index + 1] == "*":
            index += 2
            while index + 1 < length and not (text[index] == "*" and text[index + 1] == "/"):
                index += 1
            index += 2
        else:
            out.append(char)
            index += 1
    return "".join(out)


def _normalize_strings(text: str) -> str:
    """把「像字符串」的引号统一成 ``"``，并把字符串里的裸换行转义掉。

    * 不在字符串里遇到 ``'`` / ``“`` / ``”`` 时，都当成字符串开头，输出 ``"``；
    * 字符串内部的中文引号按普通字符保留（否则会把 ``"他说“好”"`` 改坏）；
    * 字符串内部的裸换行 / 制表符转义成 ``\\n`` / ``\\t``。
    """
    out: List[str] = []
    closers: List[str] = []
    escaped = False
    for char in text:
        if closers:  # 在字符串内部
            if escaped:
                out.append(char)
                escaped = False
            elif char == "\\":
                out.append(char)
                escaped = True
            elif char == "\n":
                out.append("\\n")
            elif char == "\r":
                out.append("\\r")
            elif char == "\t":
                out.append("\\t")
            elif char == closers[-1]:
                out.append('"')
                closers.pop()
            else:
                out.append(char)
        else:
            if char in _ANY_QUOTE:
                closers.append(_OPEN_TO_CLOSE.get(char, char))
                out.append('"')
            else:
                out.append(char)
    return "".join(out)


def _close_unfinished(text: str) -> str:
    """补齐缺失的右引号与右括号，并丢掉结尾多余的逗号。"""
    stripped = text.rstrip()
    if stripped.endswith(","):
        stripped = stripped[:-1]
    stack: List[str] = []
    in_string = False
    escaped = False
    for char in stripped:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "{[":
            stack.append(char)
        elif char in "}]":
            if stack and ((char == "}" and stack[-1] == "{") or (char == "]" and stack[-1] == "[")):
                stack.pop()
    suffix = '"' if in_string else ""
    while stack:
        suffix += "}" if stack.pop() == "{" else "]"
    return stripped + suffix


# --------------------------------------------------------------------------- #
# TODO 3：文本级修复
# --------------------------------------------------------------------------- #
def repair_json_text(text: str) -> str:
    """对「明显是 JSON、但有点小毛病」的文本做修复（不保证一定成功）。

    提示（按顺序做，上面三个工具函数直接用）：

    1. ``_strip_comments(text).strip()`` 去注释；
    2. 用 ``_PY_LITERAL_RE`` 把 ``None/True/False`` 换成 ``null/true/false``
       （``re.sub`` 的回调用 lambda 查 ``_PY_LITERALS``）；
    3. 正则去掉尾随逗号：把 ``,`` 后面只跟 ``}`` / ``]`` 的情况删掉；
    4. 去掉结尾多余的逗号与空白；
    5. ``_normalize_strings`` 统一引号 + 转义裸换行；
    6. ``_close_unfinished`` 补齐缺失的右引号 / 右括号。

    目标：``tests/test_json_guard.py`` 里的 9 个 ``test_repair_*`` 通过。
    """
    # 1) 去掉 // 与 /* */ 注释
    cleaned = _strip_comments(text).strip()
    # 2) Python 字面量 -> JSON 字面量（只替换独立单词，别碰字符串里的同名子串）
    cleaned = _PY_LITERAL_RE.sub(lambda m: _PY_LITERALS[m.group(0)], cleaned)
    # 3) 尾随逗号：, 后面只剩 } 或 ] 的情况
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    # 4) 结尾多余的逗号
    cleaned = cleaned.rstrip().rstrip(",").rstrip()
    # 5) 统一引号 + 把字符串里的裸换行转义
    cleaned = _normalize_strings(cleaned)
    # 6) 补齐缺失的右引号 / 右括号
    return _close_unfinished(cleaned)


# --------------------------------------------------------------------------- #
# 编排：容错阶梯（已写好，不用改）
# --------------------------------------------------------------------------- #
def _candidate_texts(text: str) -> List[str]:
    """按「原文 -> 围栏内 -> 自由文本里抠出来的对象」收集候选片段。"""
    candidates: List[str] = [text.strip()]
    fenced = strip_code_fence(text).strip()
    if fenced and fenced not in candidates:
        candidates.append(fenced)
    found = find_first_json_object(fenced or text)
    if found and found not in candidates:
        candidates.append(found)
    found_raw = find_first_json_object(text)
    if found_raw and found_raw not in candidates:
        candidates.append(found_raw)
    return candidates


def _pick_object(parsed: Any) -> Optional[Dict[str, Any]]:
    """顶层是对象就返回；是数组就取第一个对象；其它返回 ``None``。"""
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, list):
        for item in parsed:
            if isinstance(item, dict):
                return item
    return None


def loads_object(text: Any) -> Dict[str, Any]:
    """把任意模型输出整理成 dict，失败抛 :class:`JsonGuardError`。"""
    if isinstance(text, dict):
        return text
    if text is None:
        raise JsonGuardError("模型返回内容为 None")
    if not isinstance(text, str):
        raise JsonGuardError("模型返回内容类型是 %s，期望 str" % type(text).__name__)
    if not text.strip():
        raise JsonGuardError("模型返回内容为空")

    seen: set = set()
    errors: List[str] = []
    for candidate in _candidate_texts(text):
        if not candidate:
            continue
        for variant in (candidate, repair_json_text(candidate)):
            if not variant or variant in seen:
                continue
            seen.add(variant)
            try:
                parsed = json.loads(variant)
            except Exception as exc:  # noqa: BLE001 - 逐级降级，失败就试下一个
                errors.append("%s: %s" % (type(exc).__name__, exc))
                continue
            picked = _pick_object(parsed)
            if picked is not None:
                return picked
            errors.append("顶层 JSON 不是对象")
    detail = errors[-1] if errors else "没找到 JSON 对象"
    raise JsonGuardError("无法从模型输出中整理出 JSON 对象（%s）" % detail)


def loads_object_or_none(text: Any) -> Optional[Dict[str, Any]]:
    """容错版 :func:`loads_object`：失败返回 ``None`` 而不是抛异常。"""
    try:
        return loads_object(text)
    except JsonGuardError:
        return None


def dumps_json(obj: Any) -> str:
    """网关统一出口：紧凑 JSON、保留中文、拒绝 NaN。"""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
